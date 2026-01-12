import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the workspace root to the python path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
sys.path.append(os.getcwd())

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

from backend.models import Run

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_latest_run():
    db = SessionLocal()
    try:
        # Get the most recent run
        latest_run = db.query(Run).order_by(Run.created_at.desc()).first()
        
        if not latest_run:
            print("No runs found in the database.")
            return

        print(f"--- Latest Run Details ---")
        print(f"Run ID: {latest_run.run_id}")
        print(f"Status: {latest_run.status}")
        print(f"Created At: {latest_run.created_at}")
        
        if latest_run.logs:
            print("\n--- Recent Logs ---")
            # Show last 5 logs
            for log in latest_run.logs[-5:]:
                print(f"[{log.timestamp}] {log.level}: {log.message}")
        else:
            print("\nNo logs available yet.")

    except Exception as e:
        print(f"Error checking run status: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_latest_run()
