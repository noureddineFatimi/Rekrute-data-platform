import os
import logging
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rekrute_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

if POSTGRES_USER is None or POSTGRES_PASSWORD is None:
    logging.error(
        "Missing environment variables"
    )
    raise RuntimeError("Error: Missing environment variables")