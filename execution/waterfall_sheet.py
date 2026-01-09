import os
import time
import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1X54mv0pUKcdTI17450i7ktHicA6Cfi2Vp7p6jDpdDkM/edit#gid=0"
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "credentials.json"
MILLION_VERIFIER_API_KEY = os.getenv("MILLION_VERIFIER_API_KEY")
ANYMAILFINDER_API_KEY = os.getenv("ANYMAILFINDER_API_KEY")

# Column Headers (Expected)
COL_EMAIL = "Email"
COL_VERIFIED = "Verified"
COL_FIRST_NAME = "First Name"
COL_LAST_NAME = "Last Name"
COL_COMPANY_DOMAIN = "Company Domain" # or Website
COL_WEBSITE = "Website"

# API Endpoints
MV_URL = "https://api.millionverifier.com/api/v3/"
AMF_URL = "https://api.anymailfinder.com/v5.1/find-email/person"

def get_sheet_client():
    """Authenticate and return gspread client."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    return gspread.authorize(creds)

def verify_million_verifier(email):
    """
    Verify email using MillionVerifier.
    Returns: 'safe', 'risky', 'invalid', 'unknown', or 'error'
    """
    if not email: return "no_email"
    
    url = f"{MV_URL}?api_key={MILLION_VERIFIER_API_KEY}&email={email}&timeout=10000"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("result", "unknown")
    except Exception as e:
        print(f"Error verifying {email}: {e}")
    return "error"

def find_anymail_finder(first, last, domain):
    """
    Find email using Anymail Finder.
    Returns: email (str) or None
    """
    if not ANYMAILFINDER_API_KEY: 
        print("Missing Anymail Finder API Key")
        return None
        
    headers = {
        "Authorization": ANYMAILFINDER_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "domain": domain,
        "first_name": first,
        "last_name": last
    }
    
    try:
        resp = requests.post(AMF_URL, headers=headers, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            # Check if we got a valid result
            return data.get("email") # AMF returns the best email found
    except Exception as e:
        print(f"Error finding email for {first} {last} @ {domain}: {e}")
    return None

def normalize_status(status):
    """Normalize status for sheet output."""
    if status == "safe":
        return "verified"
    return "no email found"

def process_sheet():
    print("Connecting to Google Sheet...")
    gc = get_sheet_client()
    
    try:
        sh = gc.open_by_url(GOOGLE_SHEET_URL)
        worksheet = sh.get_worksheet(0) # Assume first sheet
    except Exception as e:
        print(f"Failed to open sheet: {e}")
        return

    # Get all records
    records = worksheet.get_all_records()
    print(f"Found {len(records)} rows to process.")
    
    # We need to write back to the sheet. 
    # To be efficient and safe, we'll iterate and update cell by cell or batch update.
    # Given the requirements ("append... put in verified column"), let's find the column indices.
    
    headers = worksheet.row_values(1)
    
    try:
        idx_email = headers.index(COL_EMAIL) + 1
        idx_verified = headers.index(COL_VERIFIED) + 1
    except ValueError as e:
        print(f"Error: Required columns not found. Headers: {headers}")
        print("Please ensure 'Email' and 'Verified' columns exist.")
        return

    # Optional columns for finding
    idx_first = headers.index(COL_FIRST_NAME) + 1 if COL_FIRST_NAME in headers else None
    idx_last = headers.index(COL_LAST_NAME) + 1 if COL_LAST_NAME in headers else None
    
    # Try multiple variants for domain
    idx_domain = None
    if COL_COMPANY_DOMAIN in headers: idx_domain = headers.index(COL_COMPANY_DOMAIN) + 1
    elif COL_WEBSITE in headers: idx_domain = headers.index(COL_WEBSITE) + 1
    
    updates = [] # List of (row_num, col_num, value)

    for i, row in enumerate(records):
        row_num = i + 2 # 1-based index + header
        
        email = row.get(COL_EMAIL, "").strip()
        verified_status = row.get(COL_VERIFIED, "").lower()
        
        # Skip if already processed? User didn't say to skip, but usually good practice. 
        # But user said "verify if the emails... are verified", implying we should check even if populated?
        # User: "if there are no emails use anymailfinder... append the sheet"
        # I will assume we process all rows where 'Verified' is empty or we want to re-verify?
        # Let's process everything to be safe as per "verify if the emails in this list are verified".
        
        final_status = "no email found"
        final_email = email
        
        # Step 1: Check existing email
        if email:
            print(f"Row {row_num}: Verifying {email}...")
            mv_result = verify_million_verifier(email)
            print(f"  -> Result: {mv_result}")
            
            if mv_result == "safe":
                final_status = "verified"
            else:
                # Email exists but is bad/unsafe/unknown -> Treat as no email found for now, try to find new one?
                # User: "If found but verified not safe to send put ... 'no email found'"
                # AND "if there are no emails use anymailfinder... based on information provided"
                # So if existing is bad, we essentially strip it and try to find a new one.
                final_status = "no email found" 
                # Don't delete the original email from the sheet unless user explicitly asked, 
                # but user said "append the sheet with the email if found".
                # If I find a NEW email, I should replace it?
                # User: "apend the sheet with the email if found... if it is a verified email address then put verfied"
                # I will try to find a BETTER email.
                
        # Step 2: Waterfall / Find if needed
        # We find if: 1) No email originally, OR 2) Original email was not 'safe'
        if final_status != "verified" and idx_first and idx_last and idx_domain:
            first = row.get(COL_FIRST_NAME, "")
            last = row.get(COL_LAST_NAME, "")
            # Handle domain variants
            domain = ""
            if COL_COMPANY_DOMAIN in headers: domain = row.get(COL_COMPANY_DOMAIN, "")
            elif COL_WEBSITE in headers: domain = row.get(COL_WEBSITE, "")
            
            if first and last and domain:
                print(f"Row {row_num}: Searching for {first} {last} @ {domain}...")
                found_email = find_anymail_finder(first, last, domain)
                
                if found_email:
                    print(f"  -> Found: {found_email}")
                    # Re-verify the found email? AMF usually verifies, but let's double check with MV to be consistent
                    # or trust AMF? AMF provides 'verified' emails often.
                    # User: "apend the sheet with the email if found... if not found put 'no email found'"
                    # Let's verify the FOUND email to be 100% sure it's 'verified' by our standard (MV).
                    
                    mv_check = verify_million_verifier(found_email)
                    if mv_check == "safe":
                        final_email = found_email
                        final_status = "verified"
                        updates.append((row_num, idx_email, final_email)) # Update email column
                    else:
                        print(f"  -> Found email {found_email} was {mv_check}, discarding.")
                        
        # Update Verified status
        current_verified = row.get(COL_VERIFIED)
        if current_verified != final_status:
            updates.append((row_num, idx_verified, final_status))
            
    # Perform Batch Updates
    print(f"Updating {len(updates)} cells...")
    for row, col, val in updates:
        worksheet.update_cell(row, col, val)
        time.sleep(0.5) # Avoid rate limits

    print("Done.")

if __name__ == "__main__":
    process_sheet()
