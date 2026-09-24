from fastapi import FastAPI
from api.routers import offers

app = FastAPI(title="Offers Management API")
app.include_router(offers.router)