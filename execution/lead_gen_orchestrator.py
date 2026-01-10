
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

def fetch_and_enrich_leads(apollo_url, limit=100):
    print(f"Starting Fetch for URL: {apollo_url}")
    print(f"Limit: {limit}")

    # 1. Parse URL
    print("Parsing URL...")
    payload = parse_apollo_url(apollo_url)
    if not payload:
        print("Error: Could not parse URL or URL is invalid.")
        return []

    # Add API KEY for Apollo
    if not APOLLO_API_KEY:
        print("Error: APOLLO_API_KEY not set.")
        return []
    
    # 2. Search Apollo
    print("Searching Apollo...")
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY
    }
    
    # Smart per_page
    payload["per_page"] = min(100, limit)
    
    all_leads = []
    page = 1
    target_count = limit

    # Minimal Loop
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
            # Avoid rapid paging if scraping many
            time.sleep(1)
        except Exception as e:
            print(f"Apollo Search Error: {e}")
            break
            
    print(f"Total Leads Found: {len(all_leads)}")
    if not all_leads:
        return []

    # 3. Enrich with Blitz
    if not BLITZ_API_KEY:
        print("Error: BLITZ_API_KEY not set.")
        return []
        
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
        
        # 4. Filter & Normalize
        if email and email.strip() and email != "unable to get email":
            lead['blitz_email'] = email
            enriched_leads.append(lead)
        
        # Progress Update
        # We base progress on 'processed' vs 'total found'
        # Emitting [PROGRESS]: X/Y
        if (i+1) % 5 == 0 or (i+1) == len(all_leads):
            print(f"[PROGRESS]: {i+1}/{len(all_leads)}")
            sys.stdout.flush() # Ensure it sends immediately

        if (i+1) % 10 == 0:
            print(f"Enriched {i+1}/{len(all_leads)}...")

    print(f"Leads with Email: {len(enriched_leads)}")
    return enriched_leads

def get_preview_leads(apollo_url):
    """
    Fetches 10 leads, enriches them, and masks emails for preview.
    """
    leads = fetch_and_enrich_leads(apollo_url, limit=10)
    
    # Mask emails
    for lead in leads:
        email = lead.get('blitz_email', '')
        if email and '@' in email:
            try:
                user, domain = email.split('@')
                if len(user) > 2:
                    masked_user = user[:2] + '*' * (len(user) - 2)
                else:
                    masked_user = user + '*'
                lead['blitz_email'] = f"{masked_user}@{domain}"
            except: pass
            
    # Apply Column Logic for Preview too (Clean up output)
    clean_leads = []
    unwanted = {'account', 'account_id', 'awards', 'email', 'organization_id', 'breadcrumbs'}
    
    for lead in leads:
        new_lead = {}
        # Priority columns
        new_lead['first_name'] = lead.get('first_name', '')
        new_lead['last_name'] = lead.get('last_name', '')
        new_lead['blitz_email'] = lead.get('blitz_email', '')
        new_lead['title'] = lead.get('title', '')
        new_lead['company'] = lead.get('organization', {}).get('name') or lead.get('company', '') # Apollo structure varies
        
        # Add others if needed, but preview should be simple
        clean_leads.append(new_lead)
        
    return clean_leads

def run_orchestrator(apollo_url, target_email, limit=100):
    enriched_leads = fetch_and_enrich_leads(apollo_url, limit)
    
    if not enriched_leads:
        print("No enriched leads to export.")
        return

    # 5. Export to Google Sheets
    # Retrieve fieldnames
    keys = set()
    for l in enriched_leads:
        keys.update(l.keys())
    
    # Custom Column Logic
    unwanted = {'account', 'account_id', 'awards', 'email', 'organization_id', 'breadcrumbs'} 
    
    filtered_keys = [k for k in keys if k not in unwanted and k.lower() not in ['account', 'account id', 'awards']]

    priority = ['first_name', 'last_name', 'blitz_email']
    
    remaining = [k for k in filtered_keys if k not in priority]
    remaining.sort()
    
    fieldnames = priority + remaining
    
    # ... Export Logic (Gspread)
    # Using existing logic flow but cleaned up
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        IMPERSONATE_EMAIL = os.getenv("GOOGLE_IMPERSONATE_EMAIL")
        
        creds = None
        google_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        
        if google_json:
            creds = Credentials.from_service_account_info(json.loads(google_json), scopes=SCOPES)
        else:
            SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "credentials.json"
            if os.path.exists(SERVICE_ACCOUNT_FILE):
                creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            else:
                print("Error: Google Credentials not found. Set GOOGLE_CREDENTIALS_JSON or provide credentials.json")
                sys.exit(1)

        if IMPERSONATE_EMAIL:
            creds = creds.with_subject(IMPERSONATE_EMAIL)
            
        client = gspread.authorize(creds)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sheet_title = f"Apollo Leads - {timestamp}"
        sh = client.create(sheet_title)
        
        if target_email:
            print(f"Sharing with {target_email}...")
            sh.share(target_email, perm_type='user', role='writer')
            
        worksheet = sh.get_worksheet(0)
        rows = [fieldnames]
        for lead in enriched_leads:
            rows.append([str(lead.get(k, "")) for k in fieldnames])
        worksheet.update(rows)
        
        print(f"SUCCESS: Sheet created and shared.")
        print(f"Sheet URL: {sh.url}")
        
    except Exception as e:
        print(f"Export Error: {e}")
        sys.exit(1)
        
    # Cleanup
    if os.path.exists(temp_csv):
        os.remove(temp_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    
    run_orchestrator(args.url, args.email, args.limit)
