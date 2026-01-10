
import os
import argparse
import sys
import json
import csv
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Import our modules
# Assuming execution directory is in path or we are running from root
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from url_parser import parse_apollo_url
# We need to import the logic from other scripts, or better yet, run them as modules
# But since they are designed as scripts, I will subprocess them or import if possible.
# apollo_search.py uses argparse in main, but has a search_apollo function. 
# enrich_with_blitz.py uses argparse. I'll modify enrich_with_blitz to have an importable function or replicate logic.
# I'll replicate the core logic here or subprocess for isolation. 
# Subprocess is safer given the existing script structure, but importing is cleaner.
# I'll check if I can import `search_apollo` from apollo_search.py
try:
    from apollo_search import search_apollo
except ImportError:
    # If standard import fails, try relative
    pass

load_dotenv()

APOLLO_API_URL = "https://api.apollo.io/v1/mixed_people/search"
BLITZ_API_URL = "https://api.blitz-api.ai/api/enrichment/email"
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
BLITZ_API_KEY = os.getenv("BLITZ_API_KEY")

def run_orchestrator(apollo_url, target_email):
    print(f"Starting Lead Gen for URL: {apollo_url}")
    print(f"Target Email: {target_email}")

    # 1. Parse URL
    print("Parsing URL...")
    payload = parse_apollo_url(apollo_url)
    if not payload:
        print("Error: Could not parse URL or URL is invalid.")
        return

    # Add API KEY for Apollo
    if not APOLLO_API_KEY:
        print("Error: APOLLO_API_KEY not set.")
        return
    
    # 2. Search Apollo
    print("Searching Apollo...")
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY
    }
    
    # Force 100 leads per request
    payload["per_page"] = 100
    
    all_leads = []
    page = 1
    target_count = 100 # Fixed to 100 per prompt "pull 100 leads"

    # Minimal Loop for 100 leads
    while len(all_leads) < target_count:
        payload["page"] = page
        try:
            resp = requests.post(APOLLO_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            people = data.get("people", [])
            print(f"Page {page}: Found {len(people)}")
            
            if not people:
                break
                
            all_leads.extend(people)
            if len(all_leads) >= target_count:
                all_leads = all_leads[:target_count]
                break
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"Apollo Search Error: {e}")
            break
            
    print(f"Total Leads Found: {len(all_leads)}")
    if not all_leads:
        print("No leads found.")
        return

    # 3. Enrich with Blitz
    if not BLITZ_API_KEY:
        print("Error: BLITZ_API_KEY not set.")
        return
        
    print("Enriching with Blitz...")
    enriched_leads = []
    blitz_headers = {
        "Content-Type": "application/json",
        "x-api-key": BLITZ_API_KEY
    }
    
    for i, lead in enumerate(all_leads):
        linkedin_url = lead.get("linkedin_url")
        email = None
        
        if linkedin_url:
            try:
                # Rate limit 5/sec -> 0.25s sleep
                time.sleep(0.25) 
                
                b_resp = requests.post(BLITZ_API_URL, headers=blitz_headers, json={"linkedin_profile_url": linkedin_url})
                if b_resp.status_code == 200:
                    b_data = b_resp.json()
                    # Check various email fields
                    email = b_data.get('email') or b_data.get('work_email') or b_data.get('personal_email')
                    
                    if not email and 'data' in b_data and isinstance(b_data['data'], dict):
                        email = b_data['data'].get('email')
                elif b_resp.status_code == 429:
                    print("Rate limit hit, waiting...")
                    time.sleep(2)
            except Exception as e:
                print(f"Blitz Error for {linkedin_url}: {e}")
        
        # 4. Filter: Only keep if email found
        if email and email.strip() and email != "unable to get email":
            lead['blitz_email'] = email
            # We also update the main email field for export convenience?
            # Or keep separate? User said "put 'unable to get email' - that's fine" in previous prompt
            # But in THIS prompt: "removes all the ones they weren't able to get the emails for"
            # So we filter!
            enriched_leads.append(lead)
        
        if (i+1) % 10 == 0:
            print(f"Enriched {i+1}/{len(all_leads)}...")

    print(f"Leads with Email: {len(enriched_leads)}")
    
    if not enriched_leads:
        print("No leads with emails found.")
        return

    # 5. Export to Google Sheets
    # Retrieve fieldnames
    keys = set()
    for l in enriched_leads:
        keys.update(l.keys())
    fieldnames = sorted(list(keys))
    
    # Prepare data list of lists for gspread (handled by export_leads logic usually, but export_leads.py works on CSV/JSON)
    # Let's use export_leads.py via subprocess to ensure we use the logic we just fixed (DWD, etc)
    # First save to temp csv
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_csv = f"leads_{timestamp}.csv"
    
    with open(temp_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_leads)
        
    print(f"Saved temp CSV: {temp_csv}")
    
    # Call export_leads.py
    # We need to explicitly pass impersonating email (which is the target email usually, or we use the one in ENV if configured)
    # The user said "input an email address... The sheet would be shared with that email address."
    # AND "I can update the scripts to impersonate you".
    # Usually you impersonate the admin (msipes@sipesautomation.com) to CREATE the sheet, then SHARE it with the input email.
    # OR if the input email IS the admin, just impersonate them.
    # Let's assume we impersonate the env var GOOGLE_IMPERSONATE_EMAIL (admin) to own the file, 
    # and SHARE it with `target_email`.
    
    # Modifying export_leads.py to accept --share_email might be needed if it doesn't already?
    # Checked export_leads.py: it reads TARGET_EMAIL_FOR_SHARES from env. 
    # I should pass it via env var when calling subprocess.
    
    from export_leads import export_to_sheets, read_csv
    # Actually, importing is better if we can instantiate params dynamically.
    # But export_leads.py logic for sharing is inside `create_new_sheet` which reads env.
    
    print("Exporting to Google Sheets...")
    # Update env for sharing just for this call
    os.environ["TARGET_EMAIL_FOR_SHARES"] = target_email
    
    # We call the main block logic or re-implement export call here.
    # Re-implementing is safer to control the flow.
    
    try:
        # Import dynamic
        import gspread
        from google.oauth2.service_account import Credentials
        
        SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "credentials.json"
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        IMPERSONATE_EMAIL = os.getenv("GOOGLE_IMPERSONATE_EMAIL")
        
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        if IMPERSONATE_EMAIL:
            creds = creds.with_subject(IMPERSONATE_EMAIL)
            
        client = gspread.authorize(creds)
        
        sheet_title = f"Apollo Leads - {timestamp}"
        sh = client.create(sheet_title)
        
        # Share
        if target_email:
            print(f"Sharing with {target_email}...")
            sh.share(target_email, perm_type='user', role='writer')
            
        # Write data
        # gspread expects list of lists
        worksheet = sh.get_worksheet(0)
        
        rows = [fieldnames]
        for lead in enriched_leads:
            rows.append([str(lead.get(k, "")) for k in fieldnames])
            
        worksheet.update(rows)
        
        print(f"SUCCESS: Sheet created and shared.")
        print(f"Sheet URL: {sh.url}")
        
    except Exception as e:
        print(f"Export Error: {e}")
        
    # Cleanup
    if os.path.exists(temp_csv):
        os.remove(temp_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    
    run_orchestrator(args.url, args.email)
