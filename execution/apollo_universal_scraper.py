import os
import requests
import json
import time
import csv
import argparse
import sys
import concurrent.futures
import threading
from datetime import datetime
from typing import List, Dict, Any
from queue import Queue
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from googleapiclient.http import MediaFileUpload
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from verify_leads import verify_email_tiered
    from gdrive_manager import get_drive_service, find_or_create_folder
except ImportError:
    pass

load_dotenv()

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APOLLO_API_URL = "https://api.apollo.io/v1/mixed_people/search"
BLITZ_API_KEY = os.getenv("BLITZ_API_KEY")
BLITZ_API_URL = "https://api.blitz-api.ai/api/enrichment/email"
MILLION_VERIFIER_API_KEY = os.getenv("MILLION_VERIFIER_API_KEY")

ANYMAILFINDER_API_KEY = os.getenv("ANYMAILFINDER_API_KEY")

log_lock = threading.Lock()

def log(msg):
    with log_lock:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_session(pool_size=100):
    """Creates a requests Session with connection pooling and retries."""
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size, max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_apollo_headers():
    return {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY
    }

def parse_apollo_url_to_payload(url: str, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
    parsed_url = urlparse(url)
    if parsed_url.fragment:
        query_string = parsed_url.fragment.split('?', 1)[1] if '?' in parsed_url.fragment else ""
    else:
        query_string = parsed_url.query

    params = parse_qs(query_string)
    
    payload = {
        "page": page,
        "per_page": per_page
    }

    def add_list_param(url_key, api_key):
        if url_key in params:
            payload[api_key] = params[url_key]

    add_list_param('personTitles[]', 'person_titles')
    add_list_param('personLocations[]', 'person_locations')
    add_list_param('organizationNumEmployeesRanges[]', 'organization_num_employees_ranges')
    add_list_param('organizationIndustryTagIds[]', 'organization_industry_tag_ids')
    add_list_param('qOrganizationKeywordTags[]', 'q_organization_keyword_tags')
    add_list_param('contactEmailStatusV2[]', 'contact_email_status')
    add_list_param('qNotOrganizationKeywordTags[]', 'q_not_organization_keyword_tags')
    add_list_param('includedOrganizationKeywordFields[]', 'included_organization_keyword_fields')
    add_list_param('excludedOrganizationKeywordFields[]', 'excluded_organization_keyword_fields')
    add_list_param('organizationLatestFundingStageV2[]', 'organization_latest_funding_stage_v2')
    add_list_param('organizationTechnologies[]', 'organization_technologies')
    
    # Handle single value params
    if 'organizationHasJobOpeningsV2' in params:
        val = params['organizationHasJobOpeningsV2'][0]
        # Apollo expects boolean true/false, not string "true" in some contexts, but usually string "true" in JSON payload works or needs conversion.
        # Based on typical Apollo API, it might expect boolean.
        if val.lower() == 'true':
            payload['organization_has_job_openings_v2'] = True
        elif val.lower() == 'false':
             payload['organization_has_job_openings_v2'] = False

    revenue_min = params.get('revenueRange[min]')
    revenue_max = params.get('revenueRange[max]')
    if revenue_min or revenue_max:
        payload["revenue_range"] = {}
        if revenue_min:
            payload["revenue_range"]["min"] = int(revenue_min[0])
        if revenue_max:
            payload["revenue_range"]["max"] = int(revenue_max[0])

    if "contact_email_status" not in payload:
         payload["contact_email_status"] = ["verified"]

    return payload

def fetch_page_helper(url, page, session):
    try:
        payload = parse_apollo_url_to_payload(url, page)
        # Use session for connection pooling
        resp = session.post(APOLLO_API_URL, headers=get_apollo_headers(), json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("people", []), data.get("pagination", {})
    except Exception as e:
        log(f"Fetch Error Page {page}: {e}")
        return [], {}

def find_email_anymailfinder(first_name, last_name, company_name, domain, session):
    """Fallback to AnyMail Finder if Blitz fails."""
    if not ANYMAILFINDER_API_KEY:
        return None
        
    url = "https://api.anymailfinder.com/v5.1/find-email/person"
    headers = {
        "Authorization": ANYMAILFINDER_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {}
    if domain:
        payload["domain"] = domain
    elif company_name:
        payload["company_name"] = company_name
    else:
        return None # Need at least one

    if first_name and last_name:
        payload["first_name"] = first_name
        payload["last_name"] = last_name
    else:
         # Could try Full Name if available in future, but distinct is safer
         return None

    try:
        resp = session.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("email") # or 'email_class' logic
    except Exception:
        pass
    
    return None

def enrich_and_verify(lead, session):
    linkedin_url = lead.get("linkedin_url")
    email = None
    verification_source = "blitz" # default
    verification_status = None

    # 1. Blitz Enrichment (Primary)
    if linkedin_url:
        try:
            # Retry logic for Blitz 429
            MAX_RETRIES = 10
            for attempt in range(MAX_RETRIES):
                resp = session.post(BLITZ_API_URL, headers={"x-api-key": BLITZ_API_KEY}, json={"linkedin_profile_url": linkedin_url}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    email = data.get('email') or data.get('work_email') or data.get('personal_email')
                    if not email and 'data' in data and isinstance(data['data'], dict):
                        email = data['data'].get('email')
                    break
                    
                elif resp.status_code == 429:
                    log(f"Blitz 429 - Sleep {2**attempt}s")
                    time.sleep(2 ** attempt) 
                else:
                    break
        except Exception:
            pass

    # 1.5 Verify Blitz Result Immediately
    if email:
        try:
            verify_res = verify_email_tiered(email, session=session)
            verification_status = verify_res.get("final_status")
            
            # If Blitz gave us a bad email, treat it as "not found" so we try AnyMail Finder
            if verification_status == "invalid":
                log(f"Blitz email {email} is INVALID. Falling back to AnyMail Finder.")
                email = None # Trigger fallback
                verification_source = "anymail_finder" # If found later
            # Optional: Catch-all logic? For now, we keep catch-all from Blitz unless user says otherwise.
            # Only discarding "invalid".
        except Exception:
            pass 

    # 2. AnyMail Finder Fallback (Secondary)
    # Runs if:
    #   a) Blitz found nothing
    #   b) Blitz found an 'invalid' email (set to None above)
    if not email:
        # Try to extract domain from website_url or organization info
        domain = None
        website = lead.get("organization", {}).get("website_url")
        if website:
             parsed = urlparse(website)
             domain = parsed.netloc.replace("www.", "")
        
        company_name = lead.get("organization", {}).get("name")
        first_name = lead.get("first_name")
        last_name = lead.get("last_name")

        # Fallback only if we have minimum info
        if (domain or company_name) and first_name and last_name:
            email = find_email_anymailfinder(first_name, last_name, company_name, domain, session)
            if email:
                verification_source = "anymail_finder"
                # Need to verify this new email
                try:
                    verify_res = verify_email_tiered(email, session=session)
                    verification_status = verify_res.get("final_status")
                except Exception:
                    pass

    # 3. Final Result Construction
    if email:
        return {
            "First Name": lead.get("first_name"),
            "Last Name": lead.get("last_name"),
            "Title": lead.get("title"),
            "Company": lead.get("organization", {}).get("name"),
            "Location": lead.get("headline") or f"{lead.get('city')}, {lead.get('state')}",
            "LinkedIn": linkedin_url,
            "Industry": lead.get("organization", {}).get("industry"),
            "Website": lead.get("organization", {}).get("website_url"),
            "Apollo ID": lead.get("id"),
            "Email": email,
            "Verification Status": verification_status,
            "Source": verification_source
        }
    
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=True, help="Apollo Search URL")
    parser.add_argument("--target", type=int, default=1000, help="Target number of verified leads")
    parser.add_argument("--niche", type=str, default="Leads", help="Niche name for the file")
    parser.add_argument("--threads", type=int, default=100, help="Number of consumer threads (default: 100)")
    parser.add_argument("--fetch-workers", type=int, default=30, help="Number of fetch threads (default: 30)")
    parser.add_argument("--exclude-file", type=str, help="Path to CSV file to exclude existing leads")
    args = parser.parse_args()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{args.niche}_{timestamp}.csv"
    filepath = os.path.join(os.getcwd(), filename)
    
    # Initialize Session
    global_session = get_session(pool_size=args.threads + args.fetch_workers + 10)

    # Check total pages
    try:
        _, p1_pag = fetch_page_helper(args.url, 1, global_session)
        total_pages = min(p1_pag.get("total_pages", 100), 100) # Cap at 100
        log(f"TURBO MODE. Niche: {args.niche}. Pages: {total_pages}. Target: {args.target}. Threads: {args.threads}")
    except Exception as e:
        log(f"Failed to fetch initial page: {e}")
        return

    lead_queue = Queue()
    
    # 1. Producer
    def producer():
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.fetch_workers) as fetcher:
            future_to_page = {fetcher.submit(fetch_page_helper, args.url, p, global_session): p for p in range(1, total_pages + 1)}
            for future in concurrent.futures.as_completed(future_to_page):
                try:
                    people, _ = future.result()
                    for p in people:
                        lead_queue.put(p)
                except Exception:
                    pass
        # Signal done
        for _ in range(args.threads + 10): 
            lead_queue.put(None)

    prod_thread = threading.Thread(target=producer)
    prod_thread.start()

    # 2. Consumer
    fieldnames = ["First Name", "Last Name", "Title", "Company", "Location", "LinkedIn", "Industry", "Website", "Apollo ID", "Email", "Verification Status", "Source"]
    verified_count = 0
    
    # Load exclusions
    processed_ids = set()
    processed_linkedin = set()
    processed_emails = set()
    excluded_check_keys = set()
    if args.exclude_file and os.path.exists(args.exclude_file):
        log(f"Loading exclusions from {args.exclude_file}...")
        try:
            with open(args.exclude_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("LinkedIn"):
                         excluded_check_keys.add(row.get("LinkedIn"))
                    if row.get("Email"):
                         excluded_check_keys.add(row.get("Email"))
            log(f"Loaded {len(excluded_check_keys)} exclusions.")
        except Exception as e:
            log(f"Error loading exclude file: {e}")

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            def consumer_worker():
                nonlocal verified_count
                while True:
                    lead = lead_queue.get()
                    if lead is None:
                        break
                    
                    if verified_count >= args.target:
                        lead_queue.task_done()
                        continue
                        
                        # Deduplication Check (In-Memory)
                        is_duplicate = False
                        with log_lock:
                            if lead.get("id") in processed_ids:
                                is_duplicate = True
                            elif lead.get("linkedin_url") and lead.get("linkedin_url") in processed_linkedin:
                                is_duplicate = True
                            else:
                                if lead.get("id"):
                                    processed_ids.add(lead.get("id"))
                                if lead.get("linkedin_url"):
                                    processed_linkedin.add(lead.get("linkedin_url"))
                        
                        if is_duplicate:
                            lead_queue.task_done()
                            continue

                        try:
                            # Exclusion check (File-based)
                            if lead.get("linkedin_url") in excluded_check_keys:
                                lead_queue.task_done()
                                continue

                            res = enrich_and_verify(lead, global_session)
                            if res and res["Verification Status"] == "safe":
                                with log_lock:
                                    # Double check duplication on email just in case (though unlikely if ID/LinkedIn unique)
                                    if res["Email"] in processed_emails:
                                        lead_queue.task_done()
                                        continue
                                    processed_emails.add(res["Email"])

                                    if verified_count < args.target:
                                        writer.writerow(res)
                                        f.flush()
                                        verified_count += 1
                                        if verified_count % 10 == 0:
                                            print(f"Verified Leads: {verified_count}/{args.target}")
                    except Exception:
                        pass
                    finally:
                         lead_queue.task_done()

            futures = [executor.submit(consumer_worker) for _ in range(args.threads)]
            concurrent.futures.wait(futures)

    prod_thread.join()
    log(f"Done. Total Verified: {verified_count}")
    
    # Upload to Google Drive
    try:
        drive_service = get_drive_service()
        folder_id, _ = find_or_create_folder(drive_service, "Apollo Universal Leads")
        
        file_metadata = {
            'name': filename.replace('.csv', ''),
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(filepath, mimetype='text/csv', resumable=True)
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        log(f"Uploaded to Google Drive as Sheet. File ID: {file.get('id')}")
        print(f"File Link: {file.get('webViewLink')}")
        
    except Exception as e:
        log(f"GDrive Upload Error: {e}")

if __name__ == "__main__":
    main()
