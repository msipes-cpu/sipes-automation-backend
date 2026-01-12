import os
import sys
from backend.database import SessionLocal
from backend.models import Run, Log
from sqlalchemy import desc

def check_recent_logs():
    db = SessionLocal()
    try:
        # Get last 10 runs
        runs = db.query(Run).order_by(desc(Run.start_time)).limit(10).all()
        if not runs:
            print("No runs found.")
            return

        print(f"Found {len(runs)} runs. Listing most recent:")
        for r in runs:
            print(f"- Run ID: {r.run_id} | Status: {r.status} | Time: {r.start_time}")
        
        last_run = runs[0]
        print(f"\nChecking Logs for LATEST Run ID: {last_run.run_id}")
        print(f"Status: {last_run.status}")
        print("-" * 30)

        logs = db.query(Log).filter(Log.run_id == last_run.run_id).order_by(Log.timestamp).all()
        
        for log in logs:
            print(f"[{log.event_type}] {log.data}")
        
        print("-" * 30)

    finally:
        db.close()

if __name__ == "__main__":
    check_recent_logs()
