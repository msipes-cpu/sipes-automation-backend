import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Default to SQLite for local development compatibility if PG is not set
# But in production (Railway), this MUST be set to the Postgres URL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./automation.db")

check_same_thread = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL, connect_args=check_same_thread
)

# Debug: Print DB Connection
safe_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "sqlite/local"
print(f"[Database] Connecting to: ...{safe_url}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_migrations():
    """
    Simple auto-migration to ensure schema is up to date without full Alembic setup.
    """
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            # Check/Add 'args' column to 'runs'
            try:
                conn.execute(text("SELECT args FROM runs LIMIT 1"))
            except Exception:
                print("⚠️ Column 'args' missing in 'runs'. Adding...")
                conn.execute(text("ALTER TABLE runs ADD COLUMN args TEXT"))
                conn.commit()
                print("✅ Added column 'args'.")

            # Check/Add 'env_vars' column to 'runs'
            try:
                conn.execute(text("SELECT env_vars FROM runs LIMIT 1"))
            except Exception:
                print("⚠️ Column 'env_vars' missing in 'runs'. Adding...")
                conn.execute(text("ALTER TABLE runs ADD COLUMN env_vars TEXT"))
                conn.commit()
                print("✅ Added column 'env_vars'.")
                
            print("✅ Database Schema Checked.")
    except Exception as e:
        print(f"❌ Migration check failed (Expected if tables don't exist yet): {e}")
