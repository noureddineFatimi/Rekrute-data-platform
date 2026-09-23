from api.models.schemas import SearchCreate, SearchCreateResponse
from api.models.database import SearchJob, Offer
from datetime import datetime
from config import PENDING
import threading
import logging 
from config import FAILED, DONE, RUNNING
from fastapi import HTTPException
from sqlmodel import select
from api.models.schemas import SearchResponse, OfferResponse
from scraper.rekrute import get_jobs
from db.database import get_session

def start_scraping(search_id: int):
    """
    Lance le scraping dans un thread séparé.
    """

    thread = threading.Thread(
        target=run_scraping,
        args=(search_id,),
        daemon=True
    )

    thread.start()

def create_search(searchCreate: SearchCreate):
    with get_session() as session:
        search = SearchJob(url=searchCreate.url, max_items=searchCreate.maxItems, status=PENDING,created_at=datetime.now())
        session.add(search)
        session.commit()
        session.refresh(search)
        search_id = search.id
    start_scraping(search_id)
    searchCreateResponse = SearchCreateResponse(search_id=search_id, status=PENDING)
    return searchCreateResponse

def run_scraping(search_id: int):
    """
    Fonction exécutée dans le thread.
    Elle récupère le SearchJob, lance le scraper,
    sauvegarde les offres et met à jour le statut.
    """

    with get_session() as session:

        search = session.get(SearchJob, search_id)

        if search is None:
            logging.error(
                "SearchJob %s introuvable",
                search_id
            )
            return

        try:
            search.status = RUNNING
            session.commit()
            count = 0
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

def get_jobs_by_search_id(search_id):
    with get_session() as session:
        search = session.get(SearchJob, search_id)
        if search is None:
            raise HTTPException(
                status_code=404,
                detail="Search not found"
            )
        
        statement = select(Offer).where(
            Offer.search_id == search_id
        )

        offers = session.exec(statement).all()

        count = len(offers)

        offersResponseList: list[OfferResponse] = [OfferResponse(**offer.__dict__) for offer in offers]

        searchResponse = SearchResponse(search_id=search.id, status=search.status, count=count, offers=offersResponseList, error=search.error)
        return searchResponse
        