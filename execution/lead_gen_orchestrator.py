
import os
import argparse
import sys
import json
import csv
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Table, MetaData, insert
from concurrent.futures import ThreadPoolExecutor, as_completed
import redis
import hashlib

# Import our modules
# Assuming execution directory is in path or we are running from root
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

# Robust Import Logic for URL Parser
try:
    # Try importing as if we are inside the execution package
    from .url_parser import parse_apollo_url
except ImportError:
    try:
        # Try absolute import (if running as script or execution in path)
        from url_parser import parse_apollo_url
    except ImportError:
        # Last resort: try full package path
        from execution.url_parser import parse_apollo_url

# Robust Import for Apollo Search (Optional/Sibling)
try:
    from .apollo_search import search_apollo
except ImportError:
    try:
        from apollo_search import search_apollo
    except ImportError:
        pass

load_dotenv()

APOLLO_API_URL = "https://api.apollo.io/v1/mixed_people/search"
BLITZ_API_URL = "https://api.blitz-api.ai/api/enrichment/email"
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
BLITZ_API_KEY = os.getenv("BLITZ_API_KEY")

def fetch_and_enrich_leads(apollo_url, limit=100, skip_enrichment=False):
    print(f"Starting Fetch for URL: {apollo_url}")
    print(f"Target Verified Leads: {limit}")

    # 1. Parse URL
    print("Parsing URL...")
    payload = parse_apollo_url(apollo_url)
    if not payload:
        print("Error: Could not parse URL or URL is invalid.")
        return []

    if not APOLLO_API_KEY:
        print("Error: APOLLO_API_KEY not set.")
        return []

    if not BLITZ_API_KEY:
        print("Error: BLITZ_API_KEY not set.")
        return []
    
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY
    }
    
    blitz_headers = {
        "Content-Type": "application/json",
        "x-api-key": BLITZ_API_KEY
    }
    
    verified_leads = []
    seen_ids = set()
    page = 1
    total_scanned = 0
    max_scan_limit = limit * 5 # Safety brake: scan at most 5x target to find leads
    
    # Smart per_page - fetch a bit more than needed to reduce calls since some will fail enrichment
    payload["per_page"] = 100 
    
    while len(verified_leads) < limit and total_scanned < max_scan_limit:
        
        # 2. Search Apollo Batch
        payload["page"] = page
        
        # Cache Check
        people = []
        cache_key = None
        redis_client = None
        redis_url = os.getenv("REDIS_URL")
        
        if redis_url:
            try:
                redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
                # Create a stable fingerprint of the payload
                payload_str = json.dumps(payload, sort_keys=True)
                payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
                cache_key = f"apollo_search:{payload_hash}"
                
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    print(f"[CACHE] Hit for page {page}")
                    data = json.loads(cached_data)
                    people = data.get("people", [])
            except Exception as e:
                print(f"Redis Error: {e}")
                redis_client = None

        if not people:
             try:
                print(f"Searching Apollo Page {page}...")
                resp = requests.post(APOLLO_API_URL, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                
                # Set Cache
                if redis_client and cache_key:
                    redis_client.setex(cache_key, 86400, json.dumps(data)) # 24h TTL
                    
                people = data.get("people", [])
             except Exception as e:
                print(f"Apollo Search Error: {e}")
                break
            
        if not people:
             print("No more leads found in Apollo.")
             break

        print(f"Page {page}: Fetched {len(people)} raw leads. Enriching via ThreadPool...")
            
            # 3. Enrich Batch with Blitz (Parallel)
            leads_to_process = []
            for lead in people:
                lid = lead.get('id')
                if lid in seen_ids:
                    continue
                seen_ids.add(lid)
                total_scanned += 1
                leads_to_process.append(lead)
                
                if total_scanned > max_scan_limit:
                    print("Hit Max Scan Limit (5x target). Stopping safety brake.")
                    break
            
            batch_verified = 0
            
            # Define helper for threading
            def process_single_lead(lead_data):
                l_new = lead_data.copy()
                l_linkedin = l_new.get("linkedin_url")
                l_email = None
                
                if skip_enrichment:
                    l_email = l_new.get("email") or "preview@hidden.com"
                elif l_linkedin:
                    try:
                        # minimal sleep for thread safety/rate matching
                        time.sleep(0.1) 
                        b_resp = requests.post(BLITZ_API_URL, headers=blitz_headers, json={"linkedin_profile_url": l_linkedin})
                        if b_resp.status_code == 200:
                            b_data = b_resp.json()
                            l_email = b_data.get('work_email') or b_data.get('email')
                            if not l_email and 'data' in b_data and isinstance(b_data['data'], dict):
                                l_email = b_data['data'].get('work_email') or b_data['data'].get('email')
                    except Exception as e:
                        print(f"Enrich Error: {e}")
                
                if l_email and l_email.strip() and "unable" not in l_email.lower():
                    l_new['blitz_email'] = l_email
                    return l_new
                return None

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(process_single_lead, l) for l in leads_to_process]
                
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        verified_leads.append(result)
                        batch_verified += 1
                        
                        # Real-time Update (Approximate due to threading)
                        if len(verified_leads) % 5 == 0 or len(verified_leads) >= limit:
                            print(f"[PROGRESS]: {len(verified_leads)}/{limit}")
                            sys.stdout.flush()

                    if len(verified_leads) >= limit:
                        # Cancel remaining? Hard with ThreadPool, just break loop
                        break
            
            print(f"Batch Result: {batch_verified} verified leads found in this batch.")
            
            if len(verified_leads) >= limit:
                break

            page += 1
            time.sleep(1) # Paging delay
            
        if len(verified_leads) >= limit:
            break

        page += 1
        time.sleep(1) # Paging delay
            
    print(f"Final Count: Found {len(verified_leads)} verified leads after scanning {total_scanned}.")
    return verified_leads[:limit]

def get_preview_leads(apollo_url):
    """
    Fetches 10 leads, enriches them, and masks emails for preview.
    """
    leads = fetch_and_enrich_leads(apollo_url, limit=10, skip_enrichment=True)
    
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
    return clean_leads

def save_leads_to_db(leads):
    run_id = os.getenv("RUN_ID")
    db_url = os.getenv("DATABASE_URL")
    
    if not run_id or not db_url:
        print("Skipping DB Save: No RUN_ID or DATABASE_URL.")
        return

    try:
        print("Saving leads to database...")
        engine = create_engine(db_url)
        metadata = MetaData()
        leads_table = Table('leads', metadata, autoload_with=engine)
        
        db_leads = []
        for lead in leads:
            db_leads.append({
                "run_id": run_id,
                "first_name": lead.get("first_name"),
                "last_name": lead.get("last_name"),
                "email": lead.get("blitz_email") or lead.get("email"),
                "company": lead.get("organization", {}).get("name") or lead.get("company"),
                "title": lead.get("title"),
                "linkedin_url": lead.get("linkedin_url"),
                "location": str(lead.get("country", "") or lead.get("state", "")),
                "raw_data": lead
            })
            
        with engine.connect() as conn:
            conn.execute(insert(leads_table), db_leads)
            conn.commit()
        print(f"Successfully saved {len(db_leads)} leads to DB.")
    except Exception as e:
        print(f"DB Save Error: {e}")
def run_orchestrator(apollo_url, target_email, limit=100):
    enriched_leads = fetch_and_enrich_leads(apollo_url, limit)
    
    if not enriched_leads:
        print("No enriched leads to export.")
        return

    # 4. Save to DB
    save_leads_to_db(enriched_leads)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    
    run_orchestrator(args.url, args.email, args.limit)
