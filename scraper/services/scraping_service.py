from scraper.db.models import SearchJob, Offer
import logging 
from scraper.config import FAILED, DONE, RUNNING, PENDING
from sqlmodel import select
from scraper.sources.rekrute import get_jobs
from scraper.db.session import get_session
from datetime import datetime

def run_scraping_jobs(url: str, max_items: int = 10) -> dict:
    with get_session() as session:
        search = SearchJob(url=url, max_items=max_items, status=PENDING, created_at=datetime.now())
        session.add(search)
        session.commit()
        session.refresh(search)
        search_id = search.id
        search.status = RUNNING 
        session.commit()
        count = 0
        try:
            logging.info(
                "Début du scraping pour search_id=%s",
                search_id
            )

            for offer_data in get_jobs(search.url, search.max_items):

                existing_offer = session.exec(select(Offer).where(Offer.link == offer_data.get("link"))).first()

                if existing_offer:
                    existing_offer.titre = offer_data.get("titre")
                    existing_offer.sector = offer_data.get("sector")
                    existing_offer.experience = offer_data.get("experience")
                    existing_offer.region = offer_data.get("region")
                    existing_offer.formation = offer_data.get("formation")
                    existing_offer.competences_personnelles = offer_data.get("competencesPersonnelles")
                    existing_offer.contrat = offer_data.get("contrat")
                    existing_offer.teletravail = offer_data.get("teletravail")
                    existing_offer.description = offer_data.get("description")
                    existing_offer.date_limite = offer_data.get("dateLimite")
                    existing_offer.search_id = search_id
                else:
                    offer = Offer(
                        search_id=search_id,
                        titre=offer_data.get("titre"),
                        link=offer_data.get("link"),
                        sector=offer_data.get("sector"),
                        experience=offer_data.get("experience"),
                        region=offer_data.get("region"),
                        formation=offer_data.get("formation"),
                        competences_personnelles=offer_data.get(
                            "competencesPersonnelles"
                        ),
                        contrat=offer_data.get("contrat"),
                        teletravail=offer_data.get("teletravail"),
                        description=offer_data.get("description"),
                        date_limite=offer_data.get("dateLimite"),
                    )

                    session.add(offer)
                session.commit()
                count += 1

            search.status = DONE
            search.error = None

            session.commit()
            status = DONE

            logging.info(
                "Scraping terminé pour search_id=%s",
                search_id
            )

        except Exception as e:
            session.rollback()

            logging.exception(
                "Erreur pendant le scraping search_id=%s",
                search_id
            )

            search.status = FAILED
            search.error = str(e)
            session.commit()

            raise

    return {"search_id": search_id, "status": status, "count": count}