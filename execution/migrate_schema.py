
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Migration script to add missing columns to 'runs' table
# Columns to add: args (Text), env_vars (Text)

def migrate_db():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not set.")
        return

    print(f"Connecting to DB...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Checking 'runs' table schema...")
        # Simple check: try to select the column. If fail, add it.
        # Note: This is a hacky migration. Proper way is Alembic.
        # But this works for immediate fixes.
        
        try:
            conn.execute(text("SELECT args FROM runs LIMIT 1"))
            print("✅ Column 'args' already exists.")
        except Exception:
            print("⚠️ Column 'args' missing. Adding...")
            conn.execute(text("ALTER TABLE runs ADD COLUMN args TEXT"))
            conn.commit()
            print("✅ Added column 'args'.")

        try:
            conn.execute(text("SELECT env_vars FROM runs LIMIT 1"))
            print("✅ Column 'env_vars' already exists.")
        except Exception:
            print("⚠️ Column 'env_vars' missing. Adding...")
            conn.execute(text("ALTER TABLE runs ADD COLUMN env_vars TEXT"))
            conn.commit()
            print("✅ Added column 'env_vars'.")
            
        print("\n✅ Migration Complete.")

if __name__ == "__main__":
    migrate_db()
