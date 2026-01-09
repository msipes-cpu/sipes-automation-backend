import argparse
import csv
import os
import json
from datetime import datetime
from apollo_search import search_apollo 

# Target Avatar: Marketing Agencies, $50k-$500k rev
JOB_TITLES = ["Founder", "CEO", "Owner", "Co-Founder", "Managing Partner", "Chief Operating Officer", "COO", "President", "Director of Marketing"]
LOCATIONS = ["United States", "United Kingdom", "Canada", "Australia"]
EMPLOYEES = ["11,20", "21,50", "51,100"] 
KEYWORDS = ["Marketing Agency", "Digital Marketing", "Lead Generation Agency", "Performance Marketing", "Social Media Marketing"]

OUTPUT_FILE = "first_five_tracking.csv"

def source_leads(target_count=100):
    """
    Sources leads from Apollo and appends to the tracking CSV.
    Fetches pages until target_count NEW leads are found.
    """
    print(f"🔎 Sourcing leads via Apollo until we add {target_count} new ones...")
    
    existing_emails = set()
    if os.path.isfile(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Email"):
                    existing_emails.add(row["Email"])
    
    new_leads_added = 0
    page = 1
    max_pages = 20 # Safety limit
    
    while new_leads_added < target_count and page <= max_pages:
        print(f"  -> Fetching page {page}...")
        
        results = search_apollo(
            job_titles=JOB_TITLES,
            locations=LOCATIONS,
            organization_num_employees_ranges=EMPLOYEES,
            keywords=KEYWORDS,
            limit=50,
            page=page
        )
        
        if not results:
            print("  -> No more results found.")
            break
            
        print(f"  -> Retrieved {len(results)} raw leads.")
        
        batch_new_leads = []
        
        for person in results:
            email = person.get("email", "")
            linkedin = person.get("linkedin_url", "")
            
            if not email and not linkedin:
                continue
                
            if email and email in existing_emails:
                continue
                
            fname = person.get("first_name", "")
            lname = person.get("last_name", "")
            name = f"{fname} {lname}".strip()
            if not name: continue
            
            title = person.get("title", "Founder")
            org = person.get("organization", {}) or {}
            company = org.get("name", "Unknown Agency")
            
            context = "looks like you're driving a lot of inbound traffic"
            
            lead_dict = {
                "Name": name,
                "Company": company,
                "Role": title,
                "Email": email,
                "LinkedIn": linkedin,
                "Personalized_Line_Context": context,
                "Status": "To Contact"
            }
            batch_new_leads.append(lead_dict)
            existing_emails.add(email) 
            
        if batch_new_leads:
            file_exists = os.path.isfile(OUTPUT_FILE)
            with open(OUTPUT_FILE, 'a', newline='') as f:
                fieldnames = ["Name", "Company", "Role", "Email", "LinkedIn", "Personalized_Line_Context", "Status"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(batch_new_leads)
            
            count = len(batch_new_leads)
            new_leads_added += count
            print(f"  -> Added {count} new leads. Total new: {new_leads_added}/{target_count}")
        else:
            print("  -> All leads on this page were duplicates.")
            
        page += 1
        
    print(f"🎉 Done. Added {new_leads_added} total new leads.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Lead Sourcing")
    parser.add_argument("--count", type=int, default=100, help="Number of leads to fetch")
    args = parser.parse_args()
    
    source_leads(args.count)
