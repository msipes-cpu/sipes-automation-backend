import os
import json
import csv
import argparse
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

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

def create_new_sheet(client, title):
    """Create a new spreadsheet and return its ID and URL."""
    sh = client.create(title)
    # Share with the service account's client_email (usually automatic)
    # But importantly, we need to share it with the user if we knew their email, 
    # or just make it public/link-viewable if that's the only option without user email.
    # For now, we'll return the URL. The user must have shared the folder with the service account 
    # or the service account owns it. 
    # To make it accessible to the user, we should probably share it with their email if provided,
    # or put it in a Shared Drive folder. 
    # Simplest for now: Make it link-viewable (anyone with link) or just print the URL (created by Service Account).
    # Note: Service Account created sheets are often not visible to the user unless shared.
    # Let's try to share with a default user email if in .env, else make it link shareable?
    # Actually, sharing to anyone with link is risky. 
    # Better: User presumably has access to the Service Account's drive or we share to a specific email.
    
    # We will try to read a TARGET_EMAIL from env
    target_email = os.getenv("TARGET_EMAIL_FOR_SHARES")
    if target_email:
        try:
            sh.share(target_email, perm_type='user', role='writer')
            print(f"Shared sheet with {target_email}")
        except Exception as e:
            print(f"Failed to share with {target_email}: {e}")
            
    return sh.id, sh.url

def export_to_sheets(data: List[List[Any]], spreadsheet_id: str = None, new_sheet_name: str = "Leads Export"):
    client = get_service()
    
    if not spreadsheet_id:
        print("No Spreadsheet ID provided. Creating a new Sheet...")
        sid, url = create_new_sheet(client, new_sheet_name)
        print(f"Created new Spreadsheet: {url}")
        spreadsheet_id = sid
        sheet = client.open_by_key(sid)
        worksheet = sheet.get_worksheet(0) # Default first sheet
    else:
        sheet = client.open_by_key(spreadsheet_id)
        try:
            worksheet = sheet.add_worksheet(title=new_sheet_name, rows=len(data)+10, cols=len(data[0])+5)
        except:
             # Fallback to appending to first sheet or specific name logic
             worksheet = sheet.get_worksheet(0)

    # Clear and write
    worksheet.clear()
    worksheet.update(data)
    return sheet.url

def read_csv(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export CSV/JSON to Google Sheets")
    parser.add_argument("--input_file", required=True, help="Path to input file (CSV or JSON)")
    parser.add_argument("--spreadsheet_id", help="ID of existing Google Sheet (Optional - creates new if empty)")
    parser.add_argument("--title", default="Exported Leads", help="Title for new sheet if creating one")
    
    args = parser.parse_args()
    
    data = []
    if args.input_file.endswith('.csv'):
        data = read_csv(args.input_file)
    elif args.input_file.endswith('.json'):
        with open(args.input_file, 'r') as f:
            raw = json.load(f)
            # Basic flatten logic or just dumping raw json not ideal. 
            # Assuming list of dicts.
            if isinstance(raw, list) and len(raw) > 0:
                headers = list(raw[0].keys())
                data = [headers]
                for item in raw:
                    data.append([str(item.get(k, "")) for k in headers])
    
    if data:
        url = export_to_sheets(data, args.spreadsheet_id, args.title)
        print(f"✅ Export Success! View at: {url}")
    else:
        print("❌ No data found to export.")
