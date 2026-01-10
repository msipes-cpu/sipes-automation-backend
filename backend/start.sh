#!/bin/bash

# Exit on error
set -e

# Run standard migration (if we have alembic later, for now just custom script)
# Try to migrate data if legacy DB exists (best effort)
if [ -f "automation.db" ]; then
    echo "Found legacy automation.db, attempting migration to Postgres..."
    python execution/migrate_sqlite_to_pg.py || echo "Migration failed or partial, continuing..."
fi

# Initialize DB Tables
# We do this in main.py startup event, but doing it explicitly here is fine too.
# For now, relying on main.py startup.

echo "Starting Celery Worker..."
# Start Celery in background
celery -A backend.celery_app worker --loglevel=info &

echo "Starting Uvicorn Server..."
# Start Uvicorn in foreground (so container keeps running)
# Use PORT env var provided by Railway
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
