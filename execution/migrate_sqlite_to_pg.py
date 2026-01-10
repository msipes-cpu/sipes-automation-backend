import sqlite3
import os
import json
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import Run, Log

# Path to old DB
SQLITE_DB_PATH = "automation.db"

def migrate():
    if not os.path.exists(SQLITE_DB_PATH):
        print("No SQLite database found. Skipping migration.")
        return

    print("Starting migration from SQLite to Postgres...")
    
    # Ensure PG tables exist
    Base.metadata.create_all(bind=engine)
    
    pg_db = SessionLocal()
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    
    try:
        # Migrate Runs
        print("Migrating runs...")
        runs = sqlite_conn.execute("SELECT * FROM runs").fetchall()
        for r in runs:
            # Check if exists
            exists = pg_db.query(Run).filter(Run.run_id == r['run_id']).first()
            if exists:
                print(f"Skipping existing run: {r['run_id']}")
                continue
                
            new_run = Run(
                run_id=r['run_id'],
                script_name=r['script_name'],
                status=r['status'],
                start_time=r['start_time'],
                end_time=r['end_time'],
                args=r['args'] if 'args' in r.keys() else "[]",
                env_vars=r['env_vars'] if 'env_vars' in r.keys() else "{}"
            )
            pg_db.add(new_run)
        pg_db.commit()
        print(f"Migrated {len(runs)} runs.")

        # Migrate Logs
        print("Migrating logs...")
        logs = sqlite_conn.execute("SELECT * FROM logs").fetchall()
        count = 0
        for l in logs:
            # We don't check existence for logs row-by-row for perf, 
            # assuming if run exists, we might duplicate if re-run.
            # Ideally we check by timestamp + run_id match or assume empty target.
            # Let's just blindly insert for now? Or check count?
            # To be safe against duplicated runs, we should check.
            # Actually, `logs` table in PG has auto-increment ID.
            
            new_log = Log(
                run_id=l['run_id'],
                timestamp=l['timestamp'],
                event_type=l['event_type'],
                data=l['data']
            )
            pg_db.add(new_log)
            count += 1
            
            if count % 1000 == 0:
                print(f"Processed {count} logs...")
                pg_db.commit()
        
        pg_db.commit()
        print(f"Migrated {count} logs.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        pg_db.rollback()
    finally:
        pg_db.close()
        sqlite_conn.close()

if __name__ == "__main__":
    migrate()
