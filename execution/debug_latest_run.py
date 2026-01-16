import os
import sys
import json
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import Run, Log, Lead

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./automation.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_latest_run():
    db = SessionLocal()
    try:
        # Get latest run
        run = db.query(Run).order_by(desc(Run.start_time)).first()
        if not run:
            print("No runs found.")
            return

        print(f"Latest Run ID: {run.run_id}")
        print(f"Status: {run.status}")
        print(f"Start Time: {run.start_time}")
        
        # Check Leads
        lead_count = db.query(Lead).filter(Lead.run_id == run.run_id).count()
        print(f"Leads in DB: {lead_count}")
        
        # Get Logs
        print("\n--- JOB LOGS ---")
        logs = db.query(Log).filter(Log.run_id == run.run_id).order_by(Log.id.asc()).all()
        for log in logs:
            try:
                data = json.loads(log.data)
                stdout = data.get('stdout', '').strip()
                if stdout:
                    print(stdout)
            except:
                print(f"[Raw Data]: {log.data}")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_latest_run()
