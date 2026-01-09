import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1PSA6Rl5cxWf99XEzL-6hwE9RbrIef0QoRNoqhGelSwU/edit?gid=592369058#gid=592369058"
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "credentials.json"

def get_sheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    return gspread.authorize(creds)

def inspect_headers():
    print("Connecting...")
    gc = get_sheet_client()
    try:
        sh = gc.open_by_url(GOOGLE_SHEET_URL)
        # Check all worksheets
        for ws in sh.worksheets():
            print(f"Sheet: {ws.title}")
            headers = ws.row_values(1)
            print(f"Headers: {headers}")
            print("-" * 20)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_headers()
