import os
import sys
import csv
import requests
import argparse
from datetime import datetime

# Load Environment Variables
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

load_env()

PROSPEO_API_KEY = os.getenv("PROSPEO_API_KEY")
DATAGMA_API_KEY = os.getenv("DATAGMA_API_KEY")
FINDYMAIL_API_KEY = os.getenv("FINDYMAIL_API_KEY")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
MILLION_VERIFIER_API_KEY = os.getenv("MILLION_VERIFIER_API_KEY")

def verify_email(email):
    """Verify email with MillionVerifier."""
    if not MILLION_VERIFIER_API_KEY:
        return "Unknown (Missing Key)"
    
    url = f"https://api.millionverifier.com/api/v3/?api_key={MILLION_VERIFIER_API_KEY}&email={email}&timeout=10000"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("result", "Unknown") # safe, risky, invalid, unknown
    except Exception as e:
        print(f"Error validating {email}: {e}")
        return "Error"

def check_prospeo(first, last, domain):
    if not PROSPEO_API_KEY: return None
    return None 

def check_datagma(first, last, domain, linkedin_url=None):
    if not DATAGMA_API_KEY: return None
    url = "https://api.datagma.com/v1/enrich/profile?auth=" + DATAGMA_API_KEY
    params = {}
    if linkedin_url: params["lid"] = linkedin_url
    else: return None 
    
    try:
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("email")
    except:
        pass
    return None

def check_findymail(first, last, domain):
    if not FINDYMAIL_API_KEY: return None
    return None

def check_hunter(first, last, domain):
    if not HUNTER_API_KEY: return None
    url = f"https://api.hunter.io/v2/email-finder?domain={domain}&first_name={first}&last_name={last}&api_key={HUNTER_API_KEY}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("email")
    except:
        pass
    return None

def enrich_row(row):
    email = row.get("email") or row.get("Email")
    source = "Original"
    
    if email and isinstance(email, str) and "@" in email:
        status = verify_email(email)
        if status == "safe":
            return email, source, status
    
    first = row.get("firstName") or row.get("First Name")
    last = row.get("lastName") or row.get("Last Name")
    domain = row.get("companyDomain") or row.get("website") or row.get("Company Website")
    linkedin = row.get("linkedinUrl") or row.get("profileUrl") or row.get("LinkedIn Profile Url")

    if not domain:
         return email, source, "Skipped (No Domain)"

    if linkedin:
        new_email = check_datagma(first, last, domain, linkedin)
        if new_email: 
             status = verify_email(new_email)
             if status == "safe": return new_email, "Datagma", status

    new_email = check_hunter(first, last, domain)
    if new_email:
        status = verify_email(new_email)
        if status == "safe": return new_email, "Hunter", status

    return email, source, "Not Found/Safe"

def main():
    parser = argparse.ArgumentParser(description="Waterfall Enrichment Script")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    rows = []
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                rows.append(row)
    except Exception as e:
        print(f"Failed to read input CSV: {e}")
        sys.exit(1)
        
    print(f"Processing {len(rows)} rows...")
    
    if "final_email" not in fieldnames: fieldnames.append("final_email")
    if "enrichment_source" not in fieldnames: fieldnames.append("enrichment_source")
    if "verification_status" not in fieldnames: fieldnames.append("verification_status")

    results = []
    for row in rows:
        email, source, status = enrich_row(row)
        row["final_email"] = email
        row["enrichment_source"] = source
        row["verification_status"] = status
        results.append(row)
        
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Done! Saved to {args.output}")
    except Exception as e:
        print(f"Failed to write output CSV: {e}")

if __name__ == "__main__":
    main()
