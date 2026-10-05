from sqlmodel import SQLModel, Field

class Offer(SQLModel, table=True):
    __tablename__ = "offer"

    id: int | None = Field(default=None, primary_key=True)
    search_id: int = Field(foreign_key="search_job.id")

    titre: str | None = None
    link: str = Field(unique=True, index=True)
    sector: str | None = None
    experience: str | None = None
    region: str | None = None
    formation: str | None = None
    competences_personnelles: str | None = None
    contrat: str | None = None
    teletravail: str | None = None
    description: str | None = None
    date_limite: str | None = None
    date_publication: str | None = None