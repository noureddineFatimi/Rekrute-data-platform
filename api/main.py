from fastapi import FastAPI
from api.routers import searches
import uvicorn
from db.database import create_db_and_tables

create_db_and_tables()

app = FastAPI(title="Scraping Management API")

app.include_router(searches.router)

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)