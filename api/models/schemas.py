from pydantic import BaseModel

#get
class Offer(BaseModel):
    id: int 
    titre: str | None = None
    link: str | None = None
    sector: str | None = None
    experience: str | None = None
    region: str | None = None
    formation: str | None = None
    competences_personnelles: str | None = None
    contrat: str | None = None
    teletravail: str | None = None
    description: str | None = None
    date_limite: str | None = None

class OffersResponse(BaseModel):
    count :int = 0
    offers: list[Offer] = []