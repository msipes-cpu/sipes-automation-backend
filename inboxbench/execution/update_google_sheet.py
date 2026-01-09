import sys
import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import setup_logging

def update_google_sheet(sheet_id, full_report, creds_file=None):
    """
    Updates the Google Sheet with fresh data.
    """
    setup_logging()
    
    # Locate creds
    if not creds_file:
        possible_paths = [
            "credentials.json",
            "../credentials.json",
            "/Users/michaelsipes/Coding/SA Workspace/credentials.json"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                creds_file = p
                break
    
    if not creds_file or not os.path.exists(creds_file):
        logging.error("credentials.json not found. Cannot update Sheet.")
        return False

    try:
        creds = service_account.Credentials.from_service_account_file(
            creds_file, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=creds)
    except Exception as e:
        logging.error(f"Auth failed: {e}")
        return False
    
    logging.info(f"Updating Google Sheet ({sheet_id})...")
    
    rows = []
    # Header
    rows.append(["Client", "Tag", "Email", "SPF", "DKIM", "DMARC", "Inbox %", "Campaign Name", "Sent", "Replies"])
    
    for client in full_report.get("client_reports", []):
         client_name = client.get("client_name")
         tag = client.get("client_tag")
         
         # Merge Accounts and Campaigns? 
         # For simplicity, list Accounts, and leave Campaign columns blank, 
         # THEN list Campaigns with Account blank.
         # Or try to map if possible. 
         # Instantly doesn't strictly link them in this report data structure.
         
         # List Accounts
         for acc in client.get("accounts_data", []):
             rows.append([
                 client_name,
                 tag,
                 acc.get("email"),
                 acc.get("vitals", {}).get("spf"),
                 acc.get("vitals", {}).get("dkim"),
                 acc.get("vitals", {}).get("dmarc"),
                 acc.get("warmup", {}).get("inbox_rate"),
                 "", # Campaign Name
                 "", # Sent
                 ""  # Replies
             ])
             
         # List Campaigns
         for camp in client.get("campaigns_data", []):
             rows.append([
                 client_name,
                 tag,
                 "", # Email
                 "", # SPF
                 "", # DKIM
                 "", # DMARC
                 "", # Inbox %
                 camp.get("name"),
                 camp.get("sent"),
                 camp.get("replies")
             ])

    try:
         # Clear Sheet
         service.spreadsheets().values().clear(spreadsheetId=sheet_id, range="Sheet1").execute()
         # Write Data
         body = {'values': rows}
         service.spreadsheets().values().update(
             spreadsheetId=sheet_id, range="Sheet1!A1",
             valueInputOption="RAW", body=body
         ).execute()
         logging.info("Google Sheet updated successfully.")
         return True
    except Exception as e:
        logging.error(f"Sheets API Error: {e}")
        return False
