
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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

def fetch_and_enrich_leads(apollo_url, limit=100, skip_enrichment=False, mock_mode=False):
    if mock_mode:
        print(f"[MOCK] Starting Fake Fetch for URL: {apollo_url}")
        print(f"[MOCK] Generating {limit} dummy leads...")
        
        dummy_leads = []
        for i in range(min(limit, 10)): # Cap mock at 10 to be fast
            time.sleep(1) # Simulate work
            print(f"[PROGRESS]: {i+1}/{min(limit, 10)}")
            sys.stdout.flush()
            
            dummy_leads.append({
                "first_name": f"TestUser{i}",
                "last_name": "Doe",
                "email": f"test.user.{i}@example.com",
                "linkedin_url": f"https://linkedin.com/in/testuser{i}",
                "company": "Test Corp Inc.",
                "title": "Director of Testing",
                "location": "New York, USA",
                "keywords": "testing, qa, automation"
            })
            
        print("[MOCK] Fetch complete.")
        return dummy_leads

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
    
    # Calculate pages needed
    # Apollo returns 100 per page max if we set per_page=100
    import math
    payload["per_page"] = 100 
    
    # We fetch 2x the required count initially to account for leads without valid emails
    # But for specialized enrichment, maybe 1.5x is enough. 
    # Let's fetch enough pages to cover 'limit' assuming 50% hit rate safe bet? 
    # Or just fetch exact pages first, then fetch more if needed?
    # "Turbo mode" prefers fetching more upfront to avoid sequential round trips.
    safety_multiplier = 2.0
    target_fetch_count = int(limit * safety_multiplier)
    total_pages_needed = math.ceil(target_fetch_count / 100)
    # Cap at reasonable max (e.g. 100 pages = 10k leads)
    if total_pages_needed > 100: total_pages_needed = 100
    
    print(f"Turbo Mode: Launching parallel fetch for {total_pages_needed} pages to find {limit} verified leads...")

    # --- Helper: Fetch Single Page ---
    def fetch_page(page_num):
        local_payload = payload.copy()
        local_payload["page"] = page_num
        
        # Redis Cache Check
        redis_client = None
        redis_url = os.getenv("REDIS_URL")
        cache_key = None
        
        if redis_url:
            try:
                redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
                payload_str = json.dumps(local_payload, sort_keys=True)
                payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
                cache_key = f"apollo_search:{payload_hash}"
                
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data).get("people", [])
            except: pass

        # API Request
        try:
            # Retry Check
            for attempt in range(3):
                resp = requests.post(APOLLO_API_URL, headers=headers, json=local_payload, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    # Cache Set
                    if redis_client and cache_key:
                        try: redis_client.setex(cache_key, 86400, json.dumps(data))
                        except: pass
                    return data.get("people", [])
                elif resp.status_code == 429:
                    print(f"Page {page_num} Rate Limited (Apollo). Retrying in {5 * (attempt + 1)}s...")
                    time.sleep(5 * (attempt + 1))
                else:
                    return []
        except Exception as e:
            print(f"Error fetching page {page_num}: {e}")
            return []
        return []

    # --- Step 2: Parallel Fetch ---
    raw_leads = []
    seen_ids = set()
    
    # User Concern: Apollo Rate Limits.
    # Reduced workers from 10 -> 5 to be safe. Still 5x faster than sequential.
    with ThreadPoolExecutor(max_workers=5) as executor: 
        future_to_page = {executor.submit(fetch_page, p): p for p in range(1, total_pages_needed + 1)}
        for future in as_completed(future_to_page):
            people = future.result()
            if people:
                for p in people:
                    pid = p.get('id')
                    if pid not in seen_ids:
                        seen_ids.add(pid)
                        raw_leads.append(p)
    
    print(f"Fetched {len(raw_leads)} unique raw leads. Starting Parallel Enrichment...")

    # --- Step 3: Parallel Enrichment ---
    verified_leads = []
    
    def enrich_lead(lead_data):
        l_new = lead_data.copy()
        l_linkedin = l_new.get("linkedin_url")
        l_email = None
        
        if skip_enrichment:
             l_email = l_new.get("email") or "preview@hidden.com"
        elif l_linkedin:
            # Backoff for Blitz
            for attempt in range(3):
                try:
                    b_resp = requests.post(BLITZ_API_URL, headers=blitz_headers, json={"linkedin_profile_url": l_linkedin}, timeout=10)
                    if b_resp.status_code == 200:
                        b_data = b_resp.json()
                        l_email = b_data.get('work_email') or b_data.get('email')
                        
                        # Fallback to data object
                        if not l_email and 'data' in b_data and isinstance(b_data['data'], dict):
                            l_email = b_data['data'].get('work_email') or b_data['data'].get('email')
                        break # Success
                    elif b_resp.status_code == 429:
                        time.sleep(1 * (attempt + 1)) # Lightweight backoff
                    else:
                        break # Fatal error for this lead
                except:
                    break
        
        if l_email and l_email.strip() and "unable" not in l_email.lower():
            l_new['blitz_email'] = l_email
            return l_new
        return None

    # High Concurrency for Enrichment
    # User Request: Throttling to avoid 429s. Blitz Limit ~5 req/sec.
    # We use 5 workers. Assuming each req takes >200ms, this is safe. 
    # If reqs are faster, we might hit limits, but our backoff handles it.
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        # Submit all raw leads? Or chunks? submitting all is fine for <5000
        # Initial Progress Log
        print(f"[PROGRESS]: 0/{limit}")
        sys.stdout.flush()

        for lead in raw_leads:
            if len(verified_leads) >= limit: break # Pre-check, though futures launch fast
            futures.append(executor.submit(enrich_lead, lead))
            
        completed_count = 0
        for future in as_completed(futures):
            result = future.result()
            completed_count += 1
            
            if result:
                verified_leads.append(result)
                
                # Report Progress
                # More frequent updates for small batches
                if limit < 50 or len(verified_leads) % 5 == 0 or len(verified_leads) >= limit:
                    print(f"[PROGRESS]: {len(verified_leads)}/{limit}")
                    sys.stdout.flush()
            
            # Interactive Break found?
            if len(verified_leads) >= limit:
                print("Hit target limit! Finishing pending tasks...")
                # We stop processing new results we care about, effectively stopping.
                break

    print(f"Final Count: Found {len(verified_leads)} verified leads.")
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
def run_orchestrator(apollo_url, target_email, limit=100, mock_mode=False):
    # 1. Setup & Early Sheet Creation
    print(f"Starting Job for: {target_email} (Limit: {limit})")
    
    sheet_url = None
    worksheet = None
    
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
                print("Google Credentials not found. Starting in CSV Download Mode.")
                sheet_url = None
                creds = None 

        if IMPERSONATE_EMAIL and creds:
             creds = creds.with_subject(IMPERSONATE_EMAIL)
            
        if creds:
            client = gspread.authorize(creds)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = "TEST RUN" if mock_mode else "Apollo Leads"
            sheet_title = f"{prefix} - {timestamp}"
            sh = client.create(sheet_title)
            sheet_url = sh.url
            
            if target_email:
                print(f"Sharing with {target_email}...")
                sh.share(target_email, perm_type='user', role='writer')
                
            worksheet = sh.get_worksheet(0)
            
            # Determine Headers Early (Standard Set)
            fieldnames = ['first_name', 'last_name', 'title', 'company', 'blitz_email', 'linkedin_url', 'location']
            worksheet.update([fieldnames])
            
            print(f"Sheet Created: {sheet_url}")
        
    except Exception as e:
        print(f"Sheet Creation Error: {e}")
    
    # 2. Notify User: Job Started
    if target_email:
        eta_minutes = int(limit / 200) + 2 # Rough estimate
        send_email_notification(target_email, sheet_url, limit, status="STARTED", eta=eta_minutes)

    # 3. Run Enrichment
    enriched_leads = fetch_and_enrich_leads(apollo_url, limit, mock_mode=mock_mode)
    
    if not enriched_leads:
        print("No enriched leads found.")
        return

    # 4. Save to DB
    save_leads_to_db(enriched_leads)

    # 5. Populate Sheet
    if worksheet:
        try:
            # Dynamic Column Logic (to catch any extra fields)
            keys = set()
            for l in enriched_leads:
                keys.update(l.keys())
            
            unwanted = {'account', 'account_id', 'awards', 'email', 'organization_id', 'breadcrumbs'} 
            filtered_keys = [k for k in keys if k not in unwanted and k.lower() not in ['account', 'account id', 'awards']]
            priority = ['first_name', 'last_name', 'blitz_email', 'title', 'company', 'linkedin_url']
            remaining = [k for k in filtered_keys if k not in priority]
            remaining.sort()
            
            final_fieldnames = priority + remaining
            
            rows = [final_fieldnames]
            for lead in enriched_leads:
                rows.append([str(lead.get(k, "")) for k in final_fieldnames])
            
            # Clear and Update
            worksheet.clear()
            worksheet.update(rows)
            print("Sheet populated successfully.")
             
        except Exception as e:
            print(f"Sheet Populating Error: {e}")
    
    # 6. Notify User: Job Complete
    if target_email:
        send_email_notification(target_email, sheet_url, len(enriched_leads), status="COMPLETED")

def send_email_notification(to_email, sheet_url, count, status="COMPLETED", eta=None):
    sender = os.getenv('SENDER_EMAIL')
    password = os.getenv('SENDER_PASSWORD')
    server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    port = int(os.getenv('SMTP_PORT', 587))
    
    if not sender or not password:
        print("Skipping Email: SENDER_EMAIL or SENDER_PASSWORD not set.")
        return

    dashboard_url = "https://sa.sipesautomation.com/c/sipes/tools/apollo" # Default
    # If sheet_url is missing, point to dashboard
    action_url = sheet_url if sheet_url else dashboard_url
    action_text = "Open Google Sheet" if sheet_url else "Download CSV from Dashboard"
    action_color = "#2563eb" if sheet_url else "#0f172a" 

    try:
        msg = MIMEMultipart()
        msg['From'] = f"Sipes Automation <{sender}>"
        msg['To'] = to_email
        
        # Common Marketing Footer
        marketing_footer = """
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center;">
            <h3 style="color: #1e3a8a; margin-bottom: 10px;">Want to Automate Your Business?</h3>
            <p style="color: #555; font-size: 14px; line-height: 1.5; margin-bottom: 20px;">
                This tool saved you hours of manual work. Imagine what else we could automate for you.<br>
                We build custom AI systems that scale your operations without scaling headcount.
            </p>
            <a href="https://calendly.com/sipes-automation/30min" style="display: inline-block; background-color: #111827; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                Book a Strategy Call
            </a>
            <p style="font-size: 12px; color: #999; margin-top: 20px;">
                &copy; 2024 Sipes Automation. All rights reserved.
            </p>
        </div>
        """

        if status == "STARTED":
            msg['Subject'] = f"Lead Generation Started 🚀 (ETA: {eta} mins)"
            html = f"""
            <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; max-width: 600px; margin: 0 auto; color: #333;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h2 style="color: #1e40af; font-size: 24px;">Your Job Has Started</h2>
                </div>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 30px;">
                    <p style="font-size: 16px; margin: 10px 0;"><strong>Target:</strong> {count} Verified Leads</p>
                    <p style="font-size: 16px; margin: 10px 0;"><strong>Est. Time:</strong> ~{eta} minutes</p>
                    <p style="font-size: 14px; color: #64748b; margin-top: 15px;">
                        {'We are creating your Google Sheet.' if sheet_url else 'We are enriching your leads. You can download the CSV from the dashboard when complete.'}
                    </p>
                </div>

                <div style="text-align: center; margin-bottom: 40px;">
                    <a href="{action_url}" style="background-color: {action_color}; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        {action_text}
                    </a>
                </div>

                {marketing_footer}
            </body>
            </html>
            """
        else:
            # COMPLETED
            msg['Subject'] = f"Success! {count} Leads Ready 🎯"
            html = f"""
            <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; max-width: 600px; margin: 0 auto; color: #333;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h2 style="color: #059669; font-size: 24px;">Lead Generation Complete!</h2>
                </div>
                
                <div style="background-color: #f0fdf4; padding: 25px; border-radius: 12px; border: 1px solid #bbf7d0; margin-bottom: 30px; text-align: center;">
                    <p style="font-size: 18px; margin-bottom: 10px;">We successfully enriched</p>
                    <h1 style="font-size: 48px; color: #059669; margin: 0 0 20px 0; font-weight: 800;">{count}</h1>
                    <p style="font-size: 16px; color: #166534;">Verified Leads</p>
                </div>

                <div style="text-align: center; margin-bottom: 40px;">
                    <a href="{action_url}" style="background-color: #059669; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        {action_text}
                    </a>
                </div>

                {marketing_footer}
            </body>
            </html>
            """
        
        msg.attach(MIMEText(html, 'html'))
        
        msg.attach(MIMEText(html, 'html'))
        
        if port == 465:
            # SSL Connection
            with smtplib.SMTP_SSL(server, port) as s:
                s.login(sender, password)
                s.send_message(msg)
        else:
            # TLS Connection (587)
            with smtplib.SMTP(server, port) as s:
                s.starttls()
                s.login(sender, password)
                s.send_message(msg)
                
        print(f"Email notification ({status}) sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--mock", action="store_true", help="Enable test mode (mock data)")
    args = parser.parse_args()
    
    # Handle mock URL
    target_url = args.url
    if args.mock:
        target_url = "https://app.apollo.io/mock-test"
    
    run_orchestrator(target_url, args.email, args.limit, mock_mode=args.mock)
