from fastapi import FastAPI
from api.routers import searches
import uvicorn

app = FastAPI(title="Scraping Management API")

app.include_router(searches.router)

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)