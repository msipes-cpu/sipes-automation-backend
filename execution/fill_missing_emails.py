import os
import csv
import sys
import requests
from urllib.parse import urlparse
from time import sleep
from dotenv import load_dotenv

load_dotenv()

ANYMAILFINDER_API_KEY = os.getenv("ANYMAILFINDER_API_KEY")
AMF_URL = "https://api.anymailfinder.com/v5.1/find-email/person"

CSV_FILES = [
    "leads_legal_services.csv",
    "leads_accounting_services.csv",
    "leads_management_consulting.csv",
    "leads_it_services.csv",
    "leads_marketing_agencies.csv",
    "leads_commercial_insurance.csv",
    "leads_engineering_architecture.csv"
]

def get_domain_from_url(url):
    if not url:
        return None
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return None

def find_anymail_finder(first, last, domain):
    """
    Find email using Anymail Finder.
    Returns: email (str) or None
    """
    if not ANYMAILFINDER_API_KEY:
        print("Missing Anymail Finder API Key")
        return None

    if not first or not last or not domain:
        return None

    headers = {
        "Authorization": ANYMAILFINDER_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "first_name": first,
        "last_name": last,
        "domain": domain
    }
    
    try:
        # Rate limit pause
        sleep(0.5) 
        response = requests.post(AMF_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            email = data.get("email")
            # We accept if data['email_class'] is 'trustworthy' or others?
            # User just said "find them". Usually Anymail Finder only returns if it's somewhat confident.
            if email:
                print(f"  ✓ Found: {email}")
                return email
        else:
            # print(f"  X Not found ({response.status_code})")
            pass
            
    except Exception as e:
        print(f"  Error calling Anymail Finder: {e}")
        
    return None

def process_file(filename):
    print(f"\nProcessing {filename}...")
    if not os.path.exists(filename):
        print("  File not found.")
        return

    rows = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    valid_rows = []
    initial_count = len(rows)
    found_count = 0
    removed_count = 0

    for row in rows:
        email = row.get("email", "").strip()
        
        # Check if email is missing or placeholder
        if not email or "not_unlocked" in email or "email_not_unlocked" in email or email == "no_email":
            first = row.get("first_name", "").strip()
            last = row.get("last_name", "").strip()
            website = row.get("company_website", "").strip()
            domain = get_domain_from_url(website)
            
            print(f"  Missing email for {first} {last} ({domain or website})...", end="", flush=True)
            
            found_email = find_anymail_finder(first, last, domain)
            
            if found_email:
                row["email"] = found_email
                row["verification_status"] = "found_via_anymailfinder" # Update status to indicate source
                valid_rows.append(row)
                found_count += 1
            else:
                print(" Dropped.")
                removed_count += 1
        else:
            valid_rows.append(row)

    # Write back
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_rows)

    print(f"  Done. Initial: {initial_count}, Found: {found_count}, Removed: {removed_count}, Final: {len(valid_rows)}")

if __name__ == "__main__":
    if not ANYMAILFINDER_API_KEY:
        print("CRITICAL: ANYMAILFINDER_API_KEY is missing in environment variables.")
        sys.exit(1)
        
    for f in CSV_FILES:
        process_file(f)
