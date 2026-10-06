import logging
from datetime import datetime
from config import FAILED, RUNNING
from db.models import SearchJob, StagingOffer
from db.session import get_session
from sources.rekrute import get_jobs

def scrape_offers(dag_run_id: str, url: str, max_items: int = 10) -> int:
    """Task 1 du DAG : scrape et dépose en staging. Ne touche jamais à `offer`."""
    with get_session() as session:
        search = SearchJob(url=url, max_items=max_items, status=RUNNING, created_at=datetime.now())
        session.add(search); session.commit(); session.refresh(search)
        search_id = search.id
        try:
            count = 0
            for offer_data in get_jobs(dag_run_id, url, max_items):
                session.add(StagingOffer(
                    search_id=search_id, titre=offer_data.get("titre"), link=offer_data.get("link"),
                    sector=offer_data.get("sector"), experience=offer_data.get("experience"),
                    region=offer_data.get("region"), formation=offer_data.get("formation"),
                    competences_personnelles=offer_data.get("competencesPersonnelles"),
                    contrat=offer_data.get("contrat"), teletravail=offer_data.get("teletravail"),
                    description=offer_data.get("description"), date_limite=offer_data.get("dateLimite"), date_publication=offer_data.get("datePublication")
                ))
                count += 1
            session.commit()
            logging.info("scrape_offers: %s offres déposées en staging pour search_id=%s", count, search_id)
        except Exception as e:
            session.rollback()
            search.status = FAILED; search.error = str(e); session.commit()
            raise
    return search_id 