from fastapi import APIRouter, HTTPException
import logging
from api.services.offer_service import get_offers
from api.models.schemas import OffersResponse

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(
    prefix="/offers",
    tags=["Offers"]
)

@router.get("", response_model=OffersResponse)
def list_offers(sector: str | None = None, region: str | None = None, contrat: str | None = None, keyword: str | None = None, limit: int = 50, offset: int = 0):
    try:
        offers_response = get_offers(sector, region, contrat, keyword, limit, offset)
        return offers_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) from e