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
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from verify_leads import verify_email_tiered
    from gdrive_manager import get_drive_service, find_or_create_folder, upload_file
except ImportError:
    pass

load_dotenv()

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APOLLO_API_URL = "https://api.apollo.io/v1/mixed_people/search"
BLITZ_API_KEY = os.getenv("BLITZ_API_KEY")
BLITZ_API_URL = "https://api.blitz-api.ai/api/enrichment/email"
MILLION_VERIFIER_API_KEY = os.getenv("MILLION_VERIFIER_API_KEY")

log_lock = threading.Lock()

def log(msg):
    with log_lock:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_apollo_headers():
    return {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY
    }

def get_apollo_payload(page: int, per_page: int = 100):
   return {
        "page": page,
        "per_page": per_page,
        "person_titles": [
            "ceo", "cmo", "cofounder", "owner", "president", "managing director", "coo", "cto",
            "vp operations", "vp manufacturing", "plant director", "director of engineering",
            "operations manager", "production manager", "manufacturing manager", "vp sales",
            "director of sales", "sales operations manager"
        ],
        "person_locations": ["United States", "Canada", "Mexico"],
        "organization_num_employees_ranges": [
            "201,500", "101,200", "51,100", "21,50", "11,20", "501,1000", "1001,2000"
        ],
        "organization_industry_tag_ids": [
            "5567ce987369643b789e0000", "5567e1337369641ad2970000", "5567e1b97369641ea9690200",
            "5567e0eb73696410e4bd1200", "5567cd4c73696439c9030000", "5567cd4973696439d53c0000",
            "5567cdf27369644cfd800000", "5567e0dd73696416d3c20100", "5567cdda7369644cf95d0000",
            "5567e21e73696426a1030000", "5567e1a17369641ea9d30100", "5567e1b3736964208b280000",
            "5567e0d47369641233eb0600", "5567e0d87369640e5aa30c00", "5567e36973696431a4480000",
            "5567e97f7369641e57730100", "5567cdd97369645624020000", "5567cd49736964540d020000",
            "5567e1097369641b5f810500", "5567cd4d7369644d513e0000", "5567cede73696440d0040000"
        ],
        "q_organization_keyword_tags": [
            "manufacturing", "robotics", "lean manufacturing", "process improvement"
        ],
        "q_not_organization_keyword_tags": [
             "distributor", "retailer", "wholesaler", "non-profit", "startups", "bank", "lawyers",
             "accounting", "insurance agencies & brokerages", "consulting", "real estate", "recruiting",
             "marketing agency", "advertising", "CPA", "banking", "credit union", "financial advisor",
             "wealth management", "investment", "law firm", "attorney", "legal", "consultant",
             "insurance", "brokerage", "staffing"
        ],
        "revenue_range": {"min": 700000},
        "contact_email_status": ["verified"]
    }

def fetch_page_helper(page):
    try:
        resp = requests.post(APOLLO_API_URL, headers=get_apollo_headers(), json=get_apollo_payload(page), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("people", []), data.get("pagination", {})
    except Exception as e:
        log(f"Fetch Error Page {page}: {e}")
        return [], {}

def enrich_and_verify(lead):
    linkedin_url = lead.get("linkedin_url")
    if not linkedin_url: return None

    # Blitz Enrichment
    try:
        # Retry logic for Blitz 429
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            resp = requests.post(BLITZ_API_URL, headers={"x-api-key": BLITZ_API_KEY}, json={"linkedin_profile_url": linkedin_url}, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                email = data.get('email') or data.get('work_email') or data.get('personal_email')
                if not email and 'data' in data and isinstance(data['data'], dict):
                    email = data['data'].get('email')
                
                if email:
                    # Verification
                    try:
                        verify_res = verify_email_tiered(email)
                        status = verify_res.get("final_status")
                        
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
                            "Verification Status": status
                        }
                    except Exception as e:
                       log(f"Verification fail {email}: {e}")
                       pass
                break # Email found (or not), but API call success
                
            elif resp.status_code == 429:
                log(f"Blitz 429 Rate Limit - Attempt {attempt}")
                time.sleep(2 ** attempt) # Backoff
            else:
                log(f"Blitz Error {resp.status_code}: {resp.text}")
                break
    except Exception as e:
        log(f"Blitz Exception: {e}")
        pass
    
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=10000)
    args = parser.parse_args()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"apollo_blitz_TURBO_{timestamp}.csv"
    filepath = os.path.join(os.getcwd(), filename)
    
    # Check total pages first
    p1_people, p1_pag = fetch_page_helper(1)
    total_pages = 100 # Apollo Default Limit
    if p1_pag:
        total_pages = min(p1_pag.get("total_pages", 100), 100) # Cap at 100 for safety unless we want deep pagination
    
    log(f"TURBO MODE STARTED. Fetching {total_pages} pages in parallel. Target: {args.target}")

    lead_queue = Queue()
    
    # 1. Producer: Fetch all pages
    def producer():
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as fetcher:
            future_to_page = {fetcher.submit(fetch_page_helper, p): p for p in range(1, total_pages + 1)}
            for future in concurrent.futures.as_completed(future_to_page):
                try:
                    people, _ = future.result()
                    for p in people:
                        lead_queue.put(p)
                except Exception as e:
                    pass
        # Signal done
        for _ in range(50): # Signal for each consumer
            lead_queue.put(None)

    prod_thread = threading.Thread(target=producer)
    prod_thread.start()

    # 2. Consumer: Process Leads
    fieldnames = ["First Name", "Last Name", "Title", "Company", "Location", "LinkedIn", "Industry", "Website", "Apollo ID", "Email", "Verification Status"]
    verified_count = 0
    concurrency = 10 
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            # We pull from queue and submit to executor? 
            # Or make workers pull from queue. Better to make workers pull.
            
            def consumer_worker():
                nonlocal verified_count
                while True:
                    lead = lead_queue.get()
                    if lead is None:
                        break
                    
                    try:
                        res = enrich_and_verify(lead)
                        if res and res["Verification Status"] == "safe":
                            with log_lock:
                                writer.writerow(res)
                                f.flush()
                                verified_count += 1
                                if verified_count % 50 == 0:
                                    print(f"Verified Leads: {verified_count}/{args.target}")
                    except Exception:
                        pass
                    finally:
                         lead_queue.task_done()

            # Start consumers
            futures = [executor.submit(consumer_worker) for _ in range(concurrency)]
            concurrent.futures.wait(futures)

    prod_thread.join()
    log(f"Done. Total Verified: {verified_count}")
    
    # Upload...
    # (Same upload code)

if __name__ == "__main__":
    main()
