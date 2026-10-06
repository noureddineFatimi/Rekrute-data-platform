import os
import logging
from dotenv import load_dotenv

load_dotenv()

def requireEnv(envName: str):
    value: str | None = os.getenv(envName)
    if value is None:
        logging.error(f"{envName} is missing")
        raise RuntimeError(f"{envName} is missing")
    else:
        return value  

POSTGRES_USER = requireEnv("POSTGRES_USER")
POSTGRES_PASSWORD = requireEnv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rekrute_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

PENDING = "pending" 
DONE = "done"
FAILED = "failed"
RUNNING = "running"  