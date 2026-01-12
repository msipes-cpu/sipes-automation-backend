import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def check_runs():
    db_url = os.getenv("DATABASE_URL")
    print(f"Checking DB: {db_url}")
    
    if not db_url:
        print("ERROR: DATABASE_URL not found.")
        return

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Count runs
            result = conn.execute(text("SELECT COUNT(*) FROM runs"))
            count = result.scalar()
            print(f"Total Runs in DB: {count}")
            
            # Show last 5
            if count > 0:
                print("Last 5 Runs:")
                result = conn.execute(text("SELECT run_id, status, start_time FROM runs ORDER BY start_time DESC LIMIT 5"))
                for row in result:
                    print(row)
            else:
                print("No runs found in table 'runs'.")
                
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    check_runs()
