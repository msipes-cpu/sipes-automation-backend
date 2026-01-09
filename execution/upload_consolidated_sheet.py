import os
import csv
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = "1PSA6Rl5cxWf99XEzL-6hwE9RbrIef0QoRNoqhGelSwU"

# Map of filename to Tab Name
FILES_TO_UPLOAD = {
    "leads_legal_services.csv": "Legal Services",
    "leads_accounting_services.csv": "Accounting",
    "leads_management_consulting.csv": "Consulting",
    "leads_it_services.csv": "IT Services",
    "leads_marketing_agencies.csv": "Marketing",
    "leads_commercial_insurance.csv": "Insurance",
    "leads_engineering_architecture.csv": "Engineering"
}

# Setup Google Sheets Auth
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "credentials.json"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_service():
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    else:
        raise ValueError(f"Service account file not found at {SERVICE_ACCOUNT_FILE}")

def read_csv(file_path):
    data = []
    if not os.path.exists(file_path):
        print(f"Warning: File not found {file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data

def main():
    print(f"Connecting to Spreadsheet ID: {SPREADSHEET_ID}")
    try:
        client = get_service()
        sheet = client.open_by_key(SPREADSHEET_ID)
        print(f"Access granted to sheet: {sheet.title}")
    except Exception as e:
        print(f"Error accessing sheet: {e}")
        print("Please ensure 'antigravity@antigravity-479502.iam.gserviceaccount.com' is an Editor.")
        return

    for filename, tab_name in FILES_TO_UPLOAD.items():
        print(f"\nProcessing {filename} -> Tab: {tab_name}")
        data = read_csv(filename)
        
        if not data:
            print("Skipping empty or missing file.")
            continue
            
        try:
            # Check if worksheet exists
            try:
                worksheet = sheet.worksheet(tab_name)
                print(f"Worksheet '{tab_name}' exists. Clearing content...")
                worksheet.clear()
            except gspread.exceptions.WorksheetNotFound:
                print(f"Creating new worksheet '{tab_name}'...")
                worksheet = sheet.add_worksheet(title=tab_name, rows=len(data)+20, cols=len(data[0])+5)
            
            # Write data
            worksheet.update(data)
            print("✓ Data uploaded successfully.")
            
        except Exception as e:
            print(f"Error uploading to tab '{tab_name}': {e}")

    print("\n-------------------------------------------")
    print("Consolidation Complete!")
    print(f"Link: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")

if __name__ == "__main__":
    main()
