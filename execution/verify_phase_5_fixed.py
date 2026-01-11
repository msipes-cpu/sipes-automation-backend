
import os
import sys
import json
import uuid
import datetime
from dotenv import load_dotenv

# Ensure we can import from backend
sys.path.append(os.getcwd())

from backend.database import SessionLocal, engine, Base
from backend.models import Run, Lead
import redis

# Load env vars
load_dotenv()

def verify_persistence():
    print("--- Verifying DB Persistence ---")
    session = SessionLocal()
    
    # 1. Create a Run
    run_id = f"test_verify_{uuid.uuid4().hex[:8]}"
    print(f"Creating Run: {run_id}")
    new_run = Run(
        run_id=run_id,
        script_name="verification_script",
        status="COMPLETED",
        start_time=datetime.datetime.utcnow().isoformat(),
        end_time=datetime.datetime.utcnow().isoformat(),
        args=json.dumps(["arg1", "arg2"]),
        env_vars=json.dumps({"TEST_VAR": "true"})
    )
    session.add(new_run)
    try:
        session.commit()
        print("SUCCESS: Run committed to DB.")
    except Exception as e:
        print(f"FAILURE: Could not commit Run. {e}")
        session.rollback()
        return

    # 2. Create a Lead
    print("Creating Lead linked to Run...")
    lead_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com", 
        "manual_entry": True
    }
    new_lead = Lead(
        run_id=run_id,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        raw_data=lead_data 
    )
    session.add(new_lead)
    try:
        session.commit()
        print("SUCCESS: Lead committed to DB.")
    except Exception as e:
        print(f"FAILURE: Could not commit Lead. {e}")
        session.rollback()

    # 3. Verify Retrieval
    retrieved_run = session.query(Run).filter(Run.run_id == run_id).first()
    if retrieved_run:
        print(f"SUCCESS: Retrieved Run {retrieved_run.run_id}")
        if retrieved_run.leads:
            print(f"SUCCESS: Run has {len(retrieved_run.leads)} linked leads.")
            print(f"Lead Raw Data: {retrieved_run.leads[0].raw_data}")
        else:
            print("FAILURE: No leads linked to run.")
    else:
        print("FAILURE: Could not retrieve Run.")

    session.close()

def verify_redis():
    print("\n--- Verifying Redis Caching ---")
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("WARNING: REDIS_URL not found in env. Skipping Redis check.")
        return

    try:
        r = redis.from_url(redis_url)
        test_key = "verify_phase_5_test"
        r.set(test_key, "working", ex=60)
        val = r.get(test_key)
        if val and val.decode('utf-8') == "working":
            print("SUCCESS: Redis set/get confirmed.")
        else:
            print(f"FAILURE: Redis get returned {val}")
    except Exception as e:
        print(f"FAILURE: Redis connection error. {e}")

if __name__ == "__main__":
    try:
        verify_persistence()
    except Exception as e:
        print(f"CRITICAL FAILURE during DB check: {e}")
        import traceback
        traceback.print_exc()
        
    try:
        verify_redis()
    except Exception as e:
        print(f"CRITICAL FAILURE during Redis check: {e}")
