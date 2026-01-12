import argparse
import json
import logging
import sys
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Setup logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='%(levelname)s: %(message)s')

# Constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
IMPERSONATED_USER = "msipes@sipesautomation.com"

# Locate credentials
def get_service():
    # Try multiple locations for credentials
    candidates = [
        "credentials.json",
        "../credentials.json",
        "/Users/michaelsipes/Coding/SA Workspace/credentials.json",
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    ]
    
    creds = None
    for c in candidates:
        if c and os.path.exists(c):
            try:
                creds = service_account.Credentials.from_service_account_file(c, scopes=SCOPES)
                # Impersonate user to own the file
                creds = creds.with_subject(IMPERSONATED_USER)
                break
            except Exception as e:
                logging.warning(f"Failed to load creds from {c}: {e}")
                continue
    
    if not creds:
        logging.error("Could not find valid credentials.json")
        return None

    return build('sheets', 'v4', credentials=creds)

def get_drive_service():
    # Helper to get drive service sharing credentials logic
    # Reusing the get_service logic but for drive
    #Ideally refactor get_service to take service name, but duplicating for safety/speed now
    candidates = [
        "credentials.json",
        "../credentials.json",
        "/Users/michaelsipes/Coding/SA Workspace/credentials.json",
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    ]
    
    creds = None
    for c in candidates:
        if c and os.path.exists(c):
            try:
                creds = service_account.Credentials.from_service_account_file(c, scopes=SCOPES)
                creds = creds.with_subject(IMPERSONATED_USER)
                break
            except Exception:
                continue
    
    if not creds: return None
    return build('drive', 'v3', credentials=creds)

def create_sheet(title, share_email=None):
    service = get_service()
    if not service:
        return {"success": False, "error": "Authentication failed"}

    try:
        logging.info(f"Creating sheet '{title}' as {IMPERSONATED_USER}...")
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
        
        sheet_id = spreadsheet.get('spreadsheetId')
        sheet_url = spreadsheet.get('spreadsheetUrl')
        
        logging.info(f"Created: {sheet_url}")

        # Share if email provided
        if share_email:
            try:
                drive_service = get_drive_service()
                if drive_service:
                    logging.info(f"Sharing with {share_email}...")
                    display_msg = "Here is your InboxBench Verification Report."
                    drive_service.permissions().create(
                        fileId=sheet_id,
                        body={'type': 'user', 'role': 'writer', 'emailAddress': share_email},
                        emailMessage=display_msg
                    ).execute()
                    logging.info("Shared successfully.")
                else:
                    logging.warning("Could not load Drive service for sharing.")
            except Exception as e:
                logging.error(f"Sharing failed: {e}")
                # Don't fail the whole request, just log it
        
        return {
            "success": True, 
            "sheet_id": sheet_id, 
            "sheet_url": sheet_url,
            "owner": IMPERSONATED_USER,
            "shared_with": share_email
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", default="InboxBench Verification Report")
    parser.add_argument("--share_email", required=False, help="Email to share the sheet with")
    args = parser.parse_args()
    
    result = create_sheet(args.title, args.share_email)
    print(json.dumps(result))
