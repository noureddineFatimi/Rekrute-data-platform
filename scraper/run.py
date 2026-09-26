from scraper.services.scraping_service import run_scraping_jobs

try:
    run_scraping_jobs(url="https://www.rekrute.com/fr/offres-emploi-pharmacie-sante-29.html", max_items=1)
except Exception as e:
    print(f"Erreur: {str(e)}")