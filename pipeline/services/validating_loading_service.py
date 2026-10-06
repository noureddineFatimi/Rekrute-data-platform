import logging
from datetime import datetime
from sqlmodel import select
from config import FAILED, DONE
from db.models import SearchJob, Offer, StagingOffer
from db.session import get_session

def _is_valid(row: StagingOffer) -> tuple[bool, str | None]:
    if not row.titre:
        return False, "titre manquant"
    if not row.link:
        return False, "link manquant"
    if row.date_limite:
        try:
            datetime.strptime(row.date_limite, "%d/%m/%Y")
        except ValueError:
            logging.warning("date_limite non parseable pour link=%s : %r (offre acceptée quand même)",
                             row.link, row.date_limite)
    return True, None


def validate_and_load_offers(search_id: int) -> dict:
    """Task 2 du DAG : lit le staging de ce search_id, valide, upsert dans `offer`."""
    with get_session() as session:
        search = session.get(SearchJob, search_id)
        staged = session.exec(select(StagingOffer).where(StagingOffer.search_id == search_id)).all()
        accepted, rejected = 0, 0
        try:
            for row in staged:
                ok, reason = _is_valid(row)
                if not ok:
                    rejected += 1
                    logging.warning("Offre rejetée (search_id=%s, link=%s) : %s", search_id, row.link, reason)
                    continue
                existing = session.exec(select(Offer).where(Offer.link == row.link)).first()
                if existing:
                    existing.titre = row.titre; existing.sector = row.sector
                    existing.experience = row.experience; existing.region = row.region
                    existing.formation = row.formation; existing.competences_personnelles = row.competences_personnelles
                    existing.contrat = row.contrat; existing.teletravail = row.teletravail
                    existing.description = row.description; existing.date_limite = row.date_limite
                    existing.date_publication = row.date_publication
                    existing.search_id = search_id
                else:
                    session.add(Offer(
                        search_id=search_id, titre=row.titre, link=row.link, sector=row.sector,
                        experience=row.experience, region=row.region, formation=row.formation,
                        competences_personnelles=row.competences_personnelles, contrat=row.contrat,
                        teletravail=row.teletravail, description=row.description, date_limite=row.date_limite, date_publication=row.date_publication
                    ))
                accepted += 1
            search.status = DONE; search.error = None; session.commit()
        except Exception as e:
            session.rollback()
            search.status = FAILED; search.error = str(e); session.commit()
            raise
    return {"search_id": search_id, "status": DONE, "accepted": accepted, "rejected": rejected}