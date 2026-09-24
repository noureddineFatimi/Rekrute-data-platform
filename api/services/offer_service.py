from sqlmodel import select
import api.models.schemas as schemas
import api.models.database as database
from api.db.database import get_session

def get_offers(sector=None, region=None, contrat=None, keyword=None, limit=50, offset=0):
    with get_session() as session:
        statement = select(database.Offer)
        if sector: statement = statement.where(database.Offer.sector.ilike(f"%{sector}%"))
        if region: statement = statement.where(database.Offer.region.ilike(f"%{region}%"))
        if contrat: statement = statement.where(database.Offer.contrat == contrat)
        if keyword: statement = statement.where(database.Offer.titre.ilike(f"%{keyword}%"))

        offers = session.exec(statement.offset(offset=offset).limit(limit=limit)).all()

        offers_response_list: list[schemas.Offer] = [schemas.Offer(**offer.__dict__) for offer in offers]
        offers_response: schemas.OffersResponse = schemas.OffersResponse(count=len(offers_response_list), offers=offers_response_list)
        return offers_response
        