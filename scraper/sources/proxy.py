import os
import time
from scraper.config import PROXY_USERNAME, PASSWORD
import logging
from pathlib import Path

NAV_TIMEOUT = 20000  # proxies gratuits = souvent lents, 10s coupait trop court
DEBUG_DIR = "debug_dumps"  # screenshot + HTML sauvegardés ici quand wait_for_selector échoue
USERNAME = PROXY_USERNAME
PASSWORD = PASSWORD
BASE_DIR = Path(__file__).resolve().parent
PROXY_LIST_PATH = BASE_DIR.parent / "data" / "proxy-list.txt"

logger = logging.getLogger(__name__)

def initialize_proxy_list(path=PROXY_LIST_PATH):
    """Charge les proxies, un par ligne (format ip:port ou host:port)."""
    proxy_list = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                proxy = line.strip()  # sans strip(), chaque proxy contenait un "\n" -> invalide
                if not proxy:
                    continue
                if proxy == "DIRECT":
                    proxy_list.append(proxy)
                    continue
                if "://" not in proxy:
                    proxy = f"http://{proxy}"
                proxy_list.append(proxy)
    except FileNotFoundError:
        logger.error("Fichier introuvable : %s", path)
        return []
    return proxy_list

def get_link(post):
    """Extrait le lien complet de l'offre depuis un <li class='post-id'>."""
    tag = post.select_one(".titreJob")
    if tag and tag.get("href"):
        return f"https://www.rekrute.com{tag.get('href')}"
    return None

def _dump_debug(page, url):
    """Quand wait_for_selector échoue, sauvegarde une capture d'écran + le HTML brut pour voir
    EXACTEMENT ce que ce proxy a réellement chargé : bloqué ? CAPTCHA ? juste lent à finir
    de rendre ? page ok mais structure différente de celle attendue ?"""
    os.makedirs(DEBUG_DIR, exist_ok=True)
    stamp = int(time.time() * 1000)
    base = os.path.join(DEBUG_DIR, str(stamp))
    try:
        page.screenshot(path=f"{base}.png", full_page=True)
    except Exception:
        pass
    try:
        with open(f"{base}.html", "w", encoding="utf-8") as f:
            f.write(page.content())
    except Exception:
        pass
    logger.debug(
        "Debug sauvegardé : %s.png / %s.html (pour %s)",
        base,
        base,
        url,
    )

def fetch_html(browser, url, proxy, wait_selector, extract_selector=None, timeout=NAV_TIMEOUT):
    """
    Ouvre un context isolé (léger, pas un nouveau navigateur) avec `proxy`, charge `url`,
    attend `wait_selector` -- un sélecteur PRÉCIS qui ne peut exister que si le vrai
    contenu est arrivé, pas juste le conteneur vide -- puis retourne le HTML de
    `extract_selector`. Lève une exception explicite en cas d'échec (proxy mort, 403,
    timeout...) pour que l'appelant sache exactement pourquoi et puisse changer de proxy.
    """
    extract_selector = extract_selector or wait_selector
    context = browser.new_context() if proxy == "DIRECT" else browser.new_context(proxy={"server": proxy, "username": USERNAME, "password": PASSWORD})
    try:
        page = context.new_page()
        response = page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        if response is not None and not response.ok:
            logger.error("Bloacage de la part de ReKrute.")
            raise RuntimeError(f"HTTP {response.status} (probable blocage anti-bot)")

        try:
            page.wait_for_selector(wait_selector, timeout=timeout)
        except Exception:
            _dump_debug(page, url)
            logger.error("Sélecteur %s inexistant apres durré de %d", wait_selector, NAV_TIMEOUT)
            raise
        html = page.inner_html(extract_selector)
        if not html or not html.strip():
            logger.error("Sélecteur %s trouvé mais contenu vide", extract_selector)
            raise RuntimeError("sélecteur trouvé mais contenu vide")
        return html
    finally:
        context.close()


def fetch_with_retries(browser, url, proxy_list, wait_selector, extract_selector=None, start_index=0):
    """Essaie les proxies l'un après l'autre (en repartant de start_index) jusqu'à succès."""
    n = len(proxy_list)
    for attempt in range(n):
        idx = (start_index + attempt) % n  # ne peut jamais sortir des bornes de proxy_list
        proxy = proxy_list[idx]
        try:
            html = fetch_html(browser, url, proxy, wait_selector, extract_selector)
            return html, idx  # on repart de ce proxy au prochain appel, il vient de marcher
        except Exception as e:
            logger.warning("Proxy %s en échec sur %s : %r", proxy, url, e)  # erreur visible
    return None, start_index