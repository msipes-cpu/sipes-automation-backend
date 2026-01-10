import os
import requests
import json
import time
import csv
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APOLLO_API_URL = "https://api.apollo.io/v1/mixed_people/search"

def run_custom_search():
    if not APOLLO_API_KEY:
        print("Error: APOLLO_API_KEY not set.")
        return

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY
    }

    # Derived from user URL
    # https://app.apollo.io/#/people?page=1...
    
    person_titles = [
        "ceo", "cmo", "cofounder", "owner", "president", "managing director", "coo", "cto", 
        "vp operations", "vp manufacturing", "Plant Director", "Director of Engineering", 
        "Operations Manager", "Production Manager", "Manufacturing Manager", "VP Sales", 
        "Director of Sales", "Sales Operations Manager"
    ]
    
    person_locations = ["United States", "Canada", "Mexico"]
    
    # Organization Employee Ranges
    org_num_employees_ranges = [
        "201,500", "101,200", "51,100", "21,50", "11,20", "501,1000", "1001,2000"
    ]
    
    # Industry Tag IDs
    org_industry_tag_ids = [
        "5567ce987369643b789e0000", "5567e1337369641ad2970000", "5567e1b97369641ea9690200", 
        "5567e0eb73696410e4bd1200", "5567cd4c73696439c9030000", "5567cd4973696439d53c0000", 
        "5567cdf27369644cfd800000", "5567e0dd73696416d3c20100", "5567cdda7369644cf95d0000", 
        "5567e21e73696426a1030000", "5567e1a17369641ea9d30100", "5567e1b3736964208b280000", 
        "5567e0d47369641233eb0600", "5567e0d87369640e5aa30c00", "5567e36973696431a4480000", 
        "5567e97f7369641e57730100", "5567cdd97369645624020000", "5567cd49736964540d020000", 
        "5567e1097369641b5f810500", "5567cd4d7369644d513e0000", "5567cede73696440d0040000"
    ]

    # Keywords (Concepts matches)
    q_organization_keyword_tags = [
        "manufacturing", "robotics", "lean manufacturing", "process improvement"
    ]
    
    # Excluded Keywords
    q_not_organization_keyword_tags = [
        "distributor", "retailer", "wholesaler", "non-profit", "startups", "bank", "lawyers", 
        "accounting", "insurance agencies & brokerages", "consulting", "real estate", "recruiting", 
        "marketing agency", "advertising", "CPA", "banking", "credit union", "financial advisor", 
        "wealth management", "investment", "law firm", "attorney", "legal", "consultant", 
        "insurance", "brokerage", "staffing"
    ]

    all_leads = []
    page = 1
    per_page = 100 # Fetch 100 in one go if possible
    target_count = 100

    while len(all_leads) < target_count:
        print(f"Fetching page {page}...")
        
        payload = {
            "page": page,
            "per_page": per_page,
            "person_titles": person_titles,
            "person_locations": person_locations,
            "organization_num_employees_ranges": org_num_employees_ranges,
            "organization_industry_tag_ids": org_industry_tag_ids,
            "q_organization_keyword_tags": q_organization_keyword_tags,
            # Note: Apollo API typically uses specific fields for exclusions. 
            # If 'q_not_organization_keyword_tags' isn't standard, we try passing it as is 
            # or we might need to use 'organization_keywords_exclude' if listed in their docs.
            # Based on URL structure, usually these map directly to body keys or nested params.
            # We will try passing them as keys first.
            "q_not_organization_keyword_tags": q_not_organization_keyword_tags,
            "revenue_range": {"min": 700000},
            "contact_email_status": ["verified"], # User asked for this in URL, effectively filters for expandable emails
            # IMPORTANT: We do NOT set reveal_personal_emails or set any email reveal flags.
            # This ensures we just get the people records (search), not enriched details (unless already in cached view).
        }

        try:
            response = requests.post(APOLLO_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            people = data.get("people", [])
            print(f"Page {page}: Found {len(people)} leads")
            
            if not people:
                print("No more results.")
                break
                
            all_leads.extend(people)
            
            # Simple deduplication just in case
            # (Apollo pagination should handle uniqueness usually)
            
            if len(all_leads) >= target_count:
                all_leads = all_leads[:target_count]
                break
            
            page += 1
            time.sleep(1) # Be nice to API

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if e.response is not None:
                print(e.response.text)
            break

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"apollo_leads_custom_{timestamp}.csv"
    
    if all_leads:
        # Determine headers from the first lead, but ensure specific order if desired
        # For now, just take all keys present in the first few items to be safe? 
        # Or just dump keys from the first item. 
        # Apollo objects can be nested. We might want to flatten them slightly or just dump as strings for complex objects.
        
        # Taking a superset of keys or just the keys from the first one
        # Let's iterate all to find all possible keys to be safe
        keys = set()
        for lead in all_leads:
            keys.update(lead.keys())
        fieldnames = sorted(list(keys))
        
        with open(output_file, "w", newline="", encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_leads)
            
        print(f"Successfully saved {len(all_leads)} leads to {output_file}")
    else:
        print("No leads found, nothing saved.")

if __name__ == "__main__":
    run_custom_search()
