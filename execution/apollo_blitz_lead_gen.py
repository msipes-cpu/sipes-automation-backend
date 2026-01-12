import os
import requests
import json
import time
import csv
import argparse
import sys
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import helper modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from verify_leads import verify_email_tiered
    from gdrive_manager import get_drive_service, find_or_create_folder, upload_file
except ImportError:
    pass

load_dotenv()

# --- Configuration ---
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APOLLO_API_URL = "https://api.apollo.io/v1/mixed_people/search"
BLITZ_API_KEY = os.getenv("BLITZ_API_KEY")
BLITZ_API_URL = "https://api.blitz-api.ai/api/enrichment/email"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def fetch_apollo_page(page: int, per_page: int = 100) -> List[Dict[str, Any]]:
    if not APOLLO_API_KEY:
        raise ValueError("APOLLO_API_KEY not set")

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY
    }

    # Parameters derived from User URL (Fixed)
    payload = {
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

    try:
        resp = requests.post(APOLLO_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("people", [])
    except Exception as e:
        log(f"Apollo API Error on page {page}: {e}")
        return []

def enrich_with_blitz(linkedin_url: str) -> str:
    if not BLITZ_API_KEY or not linkedin_url:
        return None
        
    headers = {
        "Content-Type": "application/json",
        "x-api-key": BLITZ_API_KEY
    }
    
    try:
        resp = requests.post(BLITZ_API_URL, headers=headers, json={"linkedin_profile_url": linkedin_url})
        if resp.status_code == 200:
            data = resp.json()
            email = data.get('email') or data.get('work_email') or data.get('personal_email')
            if not email and 'data' in data and isinstance(data['data'], dict):
                email = data['data'].get('email')
            return email
        elif resp.status_code == 429:
            time.sleep(2) # Backoff
            return None
    except Exception as e:
        # log(f"Blitz API Error: {e}")
        pass
        
    return None

def process_lead(lead_data):
    # Worker function for verification
    index, lead = lead_data
    linkedin_url = lead.get("linkedin_url")
    
    out_lead = {
        "First Name": lead.get("first_name"),
        "Last Name": lead.get("last_name"),
        "Title": lead.get("title"),
        "Company": lead.get("organization", {}).get("name"),
        "Location": lead.get("headline") or f"{lead.get('city')}, {lead.get('state')}",
        "LinkedIn": linkedin_url,
        "Industry": lead.get("organization", {}).get("industry"),
        "Website": lead.get("organization", {}).get("website_url"),
        "Apollo ID": lead.get("id"),
        "Email": None,
        "Verification Status": "Not Verified"
    }

    if not linkedin_url:
        return None

    # Blitz Enrichment
    time.sleep(0.5) # Throttle per worker
    email = enrich_with_blitz(linkedin_url)

    if email:
        out_lead["Email"] = email
        try:
            verify_res = verify_email_tiered(email)
            status = verify_res.get("final_status")
            out_lead["Verification Status"] = status
            
            if status == "safe":
                # log(f"Success: {email}") # Reduce noise
                return out_lead
            else:
                return None # Reject unsafe
        except Exception:
            return None
    else:
        return None

def main():
    parser = argparse.ArgumentParser(description="Apollo -> Blitz -> Verify Orchestrator (Target-based)")
    parser.add_argument("--target", type=int, default=10000, help="Target number of VERIFIED leads")
    parser.add_argument("--start-page", type=int, default=1, help="Page to start from")
    args = parser.parse_args()

    target_verified = args.target
    current_verified_count = 0
    page = args.start_page
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"apollo_blitz_10k_{timestamp}.csv"
    filepath = os.path.join(os.getcwd(), filename)
    
    log(f"Starting execution. Target: {target_verified} verified leads.")
    log(f"Saving to: {filename}")

    # Prepare threading
    max_workers = 5
    headers_written = False
    
    fieldnames = ["First Name", "Last Name", "Title", "Company", "Location", "LinkedIn", "Industry", "Website", "Apollo ID", "Email", "Verification Status"]

    # Open file in append mode (although we rewrite header if new, handle essentially for stream)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        headers_written = True
        
        while current_verified_count < target_verified:
            log(f"Fetching Apollo Page {page}... (Verified: {current_verified_count}/{target_verified})")
            
            leads = fetch_apollo_page(page)
            if not leads:
                log("No more leads returned from Apollo. Stopping.")
                break
                
            # Process batch
            batch_inputs = [(i, l) for i, l in enumerate(leads)]
            batch_verified_count = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_lead = {executor.submit(process_lead, item): item for item in batch_inputs}
                
                for future in concurrent.futures.as_completed(future_to_lead):
                    try:
                        result = future.result()
                        if result:
                            writer.writerow(result)
                            batch_verified_count += 1
                    except Exception as exc:
                        log(f"Worker Exception: {exc}")
            
            f.flush() # Ensure data is safe
            current_verified_count += batch_verified_count
            log(f"Page {page} complete. +{batch_verified_count} verified leads. Total: {current_verified_count}")
            
            page += 1
            
            # Apollo Deep Pagination Limit check
            if page > 100:
                log("Warning: Reached Apollo 100-page (10k raw) limit for this search criteria.")
                log("To get more leads, we would need to split the search criteria (e.g. by location states).")
                log("Continuing for now just in case.")
                # We break if empty return, so we can just let it run until 400/error
            
            time.sleep(1) # Polite pause between pages

    log(f"Execution finished. Total Verified Leads: {current_verified_count}")
    
    # Upload
    if current_verified_count > 0:
        try:
             # Ensure impersonation if env var set
            from gdrive_manager import get_drive_service, find_or_create_folder, upload_file
            
            service = get_drive_service()
            folder_id, folder_link = find_or_create_folder(service, "Leads from Apollo API")
            file_id, file_link = upload_file(service, filepath, folder_id)
            
            log("------------------------------------------------")
            log(f"UPLOAD COMPLETE: {file_link}")
            log("------------------------------------------------")
            print(f"\nFinal Google Sheet Link: {file_link}\n")
            
        except Exception as e:
            log(f"Drive Upload Failed: {e}")

if __name__ == "__main__":
    main()
