
import csv
import os
import requests
import json
import time

from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = "marketing/companies_temp.csv"
OUTPUT_FILE = "marketing/prospects_batch_0104.csv" # Overwriting the empty one
ANYMAIL_API_KEY = os.getenv("ANYMAILFINDER_API_KEY")

def find_email(domain, first, last):
    if not ANYMAIL_API_KEY:
        print("Error: ANYMAILFINDER_API_KEY not set.")
        return None

    url = "https://api.anymailfinder.com/v5.0/search/person.json"
    headers = {
        "X-Api-Key": ANYMAIL_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Try with full name or split
    payload = {
        "domain": domain,
        "first_name": first,
        "last_name": last
    }
    
    try:
        # Note: Anymail finder often uses GET or POST. v5.0 usually POST.
        # Docs say: POST /v5.0/search/person.json
        resp = requests.post(url, headers=headers, json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            # Look for email
            # Structure usually: {"results": {"email": "..."}}
            email = data.get("email")
            if not email and "results" in data:
                email = data["results"].get("email")
            
            if email:
                return email
            else:
                print(f"No email found for {first} {last} @ {domain}")
                # print(f"Full response: {json.dumps(data)}")
        else:
            print(f"Error {resp.status_code} for {domain}: {resp.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    return None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found.")
        return

    print(f"Reading from {INPUT_FILE}...")
    
    results = []
    
    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company = row['Company']
            domain = row['Domain']
            first = row['First Name']
            last = row['Last Name']
            
            print(f"Searching for {first} {last} at {company} ({domain})...")
            
            email = find_email(domain, first, last)
            
            if email:
                print(f"✅ Found: {email}")
                # Create result row
                res_row = {
                    "Name": f"{first} {last}",
                    "First Name": first,
                    "Last Name": last,
                    "Title": "CEO", # Assumed
                    "Company": company,
                    "Email": email,
                    "LinkedIn": "", # We don't have this, but that's okay for email outreach context
                    "Location": "",
                    "Website": domain,
                    "Status": "Not Contacted",
                    "Personalized_Line_Context": "",
                    "Warm/Cold": "Cold",
                    "Generated_Draft_Variant": "A", # Default
                    "Generated_Draft_Subject": "",
                    "Generated_Draft_Body": ""
                }
                results.append(res_row)
            else:
                print("❌ Not found or error.")
            
            time.sleep(1) # Rate limit nice

    print(f"Found {len(results)} valid emails.")
    
    if results:
        headers = ["Name", "First Name", "Last Name", "Title", "Company", "Email", "LinkedIn", "Location", "Website", "Status", "Personalized_Line_Context", "Warm/Cold", "Generated_Draft_Variant", "Generated_Draft_Subject", "Generated_Draft_Body"]
        
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
