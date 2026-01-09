import os
import csv
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1PSA6Rl5cxWf99XEzL-6hwE9RbrIef0QoRNoqhGelSwU/edit?gid=592369058#gid=592369058"
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "credentials.json"
TRACKING_CSV = "first_five_tracking.csv"

def get_sheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    return gspread.authorize(creds)

def process_leads():
    print("Connecting to Google Sheets...")
    gc = get_sheet_client()
    sh = gc.open_by_url(GOOGLE_SHEET_URL)
    
    all_leads = []
    
    for ws in sh.worksheets():
        # FILTER: Only target Marketing Agencies per new strategy
        if "marketing" not in ws.title.lower():
            continue

        print(f"Processing sheet: {ws.title}")
        records = ws.get_all_records()
        
        for row in records:
            email = row.get("email", "").strip()
            if not email:
                continue
                
            fname = row.get("first_name", "")
            lname = row.get("last_name", "")
            name = f"{fname} {lname}".strip()
            company = row.get("company_name", "")
            role = row.get("title", "")
            linkedin = row.get("linkedin_url", "")
            
            # New Context for Speed-to-Lead Script
            # "Saw you run [Agency] – looks like you’re driving a lot of inbound traffic."
            # The script builder uses {context}, so we can make this the second half of that sentence.
            # Actually, looking at outreach_manager.py, it inserts context on its own line.
            # Let's make the context specific to the opening observation.
            
            context = "looks like you're driving a lot of inbound traffic"
            
            all_leads.append({
                "Name": name,
                "Company": company,
                "Role": role,
                "Email": email,
                "LinkedIn": linkedin,
                "Personalized_Line_Context": context,
                "Status": "To Contact"
            })
            
    print(f"Found {len(all_leads)} leads across all sheets.")
    
    # Write to CSV
    # We will overwrite the template since the user wants to use this list
    with open(TRACKING_CSV, 'w', newline='') as f:
        fieldnames = ["Name", "Company", "Role", "Email", "LinkedIn", "Personalized_Line_Context", "Status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_leads)
        
    print(f"Successfully saved {len(all_leads)} leads to {TRACKING_CSV}")

if __name__ == "__main__":
    process_leads()
