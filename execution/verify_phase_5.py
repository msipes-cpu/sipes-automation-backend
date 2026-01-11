
import os
import sys
import uuid
import redis
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load .env from current directory (root) explicitly
load_dotenv(os.path.join(os.getcwd(), '.env'))

# Add backend to path - NOT NEEDED if running from root
# sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.models import Run, Lead
from backend.database import Base, SessionLocal

# Setup DB
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("⚠️ DATABASE_URL not found, falling back to local SQLite.")
    DATABASE_URL = "sqlite:///./automation.db"
    
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure DB exists for verification
Base.metadata.create_all(bind=engine)

# Setup Redis
REDIS_URL = os.getenv("REDIS_URL")

def verify_persistence():
    print("--- Verifying Persistence ---")
    session = SessionLocal()
    try:
        # Create a Test Run
        run_id = str(uuid.uuid4())
        print(f"Creating Test Run: {run_id}")
        new_run = Run(
            run_id=run_id,
            status="test",
            start_time=datetime.utcnow().isoformat() # key change: string format
        )
        session.add(new_run)
        
        # Create a Test Lead
        print("Creating Test Lead linked to Run")
        test_lead = Lead(
            run_id=run_id,
            raw_data={"test_key": "test_value", "name": "Verification Lead"},
            # created_at=datetime.utcnow() # Lead model doesn't have created_at in observed version, rely on models.py
        )
        session.add(test_lead)
        session.commit()
        
        # Verify
        saved_lead = session.query(Lead).filter_by(run_id=run_id).first()
        if saved_lead and saved_lead.raw_data and saved_lead.raw_data.get('name') == "Verification Lead":
             print("✅ Persistence Verified: Lead saved and retrieved.")
        else:
             print("❌ Persistence Failed: Could not retrieve lead.")
             
    except Exception as e:
        print(f"❌ Persistence Error: {e}")
    finally:
        session.close()

def verify_caching():
    print("\n--- Verifying Redis Caching ---")
    try:
        r = redis.from_url(REDIS_URL)
        test_key = "test_verification_key"
        test_val = "cached_value"
        
        print(f"Setting Redis Key: {test_key}")
        r.set(test_key, test_val, ex=60)
        
        retrieved = r.get(test_key)
        if retrieved and retrieved.decode('utf-8') == test_val:
            print("✅ Caching Verified: Redis key set and retrieved.")
        else:
            print("❌ Caching Failed: Redis key mismatch or missing.")
            
    except Exception as e:
        print(f"❌ Caching Error: {e}")

if __name__ == "__main__":
    verify_persistence()
    verify_caching()
