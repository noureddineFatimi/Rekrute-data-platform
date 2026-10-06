import logging
from urllib.request import urlopen
from urllib.parse import urlsplit
from db.models import Proxy
from db.session import get_session

PROXY_API_URL = (
    "https://api.proxyscrape.com/v4/free-proxy-list/get"
    "?request=display_proxies&proxy_format=protocolipport&format=text&protocol=http&limit=20"
)
REQUEST_TIMEOUT_SECONDS = 30
logger = logging.getLogger(__name__)

def fetch_and_store_proxies(dag_run_id: str) -> str:
    """Fetch HTTP proxies, persist them for this DAG run, and return its ID."""
    if dag_run_id is None:
        raise ValueError("Dag run id manquant")

    with urlopen(PROXY_API_URL, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        body = response.read().decode("utf-8")

    proxies: list[str] = []
    for line in body.splitlines():
        proxy = line.strip()
        if not proxy:
            continue

        try:
            parsed = urlsplit(proxy)
            valid_proxy = (
                parsed.scheme == "http"
                and parsed.hostname is not None
                and parsed.port is not None
            )
        except ValueError:
            valid_proxy = False

        if valid_proxy:
            proxies.append(proxy)
        else:
            logger.warning("Ignoring invalid proxy returned by the API: %r", proxy)

    proxies = list(dict.fromkeys(proxies))
    if not proxies:
        raise RuntimeError("The proxy API returned no valid HTTP proxies")

    with get_session() as session:
        try:
            for proxy in proxies:
                session.add(Proxy(dag_run_id=dag_run_id, proxy=proxy))
            session.commit()
        except:
            session.rollback()
            logger.error("Error during adding proxies to database")
            raise RuntimeError("Error during adding proxies to database")
    
    logger.info(
        "Stored %d proxies for dag_run_id=%s",
        len(proxies),
        dag_run_id,
    )
    return dag_run_id
