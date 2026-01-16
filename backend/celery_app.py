import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Default to local Redis if not set, check common service names
REDIS_URL = os.getenv("REDIS_URL") or os.getenv("REDIS_PRIVATE_URL") or os.getenv("REDIS_TLS_URL")

if not REDIS_URL:
    print("WARNING: No REDIS_URL found. Defaulting to localhost (will fail in production).")
    REDIS_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "sipes_automation_worker",
    broker=REDIS_URL,
    include=['backend.tasks']
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
