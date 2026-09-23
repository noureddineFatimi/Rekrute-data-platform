import os
import logging
from dotenv import load_dotenv

load_dotenv()

PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PASSWORD = os.getenv("PASSWORD")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rekrute_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
PENDING = "pending" 
DONE = "done"
FAILED = "failed"
RUNNING = "running"

if PROXY_USERNAME is None or PASSWORD is None:
    logging.error(
        "Proxy username or password is missing in the .env file "
        "or in the environment variables."
    )
    raise RuntimeError("Proxy username or password is missing")