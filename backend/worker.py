from backend.celery_app import celery_app
# Helper to ensure tasks are registered
import backend.tasks

if __name__ == "__main__":
    # Start the worker
    # Usage: python backend/worker.py worker --loglevel=info
    celery_app.start()
