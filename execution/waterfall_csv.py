
import os
import csv
import time
import requests
import argparse
from dotenv import load_dotenv

load_dotenv()

# API Keys
MILLION_VERIFIER_API_KEY = os.getenv("MILLION_VERIFIER_API_KEY")
ANYMAILFINDER_API_KEY = os.getenv("ANYMAILFINDER_API_KEY")

# API Endpoints
MV_URL = "https://api.millionverifier.com/api/v3/"
AMF_URL = "https://api.anymailfinder.com/v5.1/find-email/person"

def verify_million_verifier(email):
    """
    Verify email using MillionVerifier.
    Returns: 'safe', 'risky', 'invalid', 'unknown', or 'error'
    """
    if not email: return "no_email"
    
    # Correct param name is 'api'
    url = f"{MV_URL}?api={MILLION_VERIFIER_API_KEY}&email={email}&timeout=10000"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("result", "unknown")
        else:
            print(f"MV API Error: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Error verifying {email}: {e}")
    return "error"

def find_anymail_finder(first, last, domain):
    """
    Find email using Anymail Finder.
    Returns: email (str) or None
    """
    if not ANYMAILFINDER_API_KEY: 
        print("Missing Anymail Finder API Key")
        return None
        
    headers = {
        "Authorization": ANYMAILFINDER_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "domain": domain,
        "first_name": first,
        "last_name": last
    }
    
    try:
        resp = requests.post(AMF_URL, headers=headers, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("email") # AMF returns the best email found
    except Exception as e:
        print(f"Error finding email for {first} {last} @ {domain}: {e}")
    return None

def process_csv(input_path, output_path):
    print(f"Processing CSV: {input_path}")
    print(f"Writing to: {output_path}")
    
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            if "Verified" not in fieldnames:
                fieldnames.append("Verified")
            
            # Open output file immediately
            with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                outfile.flush()
                
                rows = list(reader) # Read all inputs first (safe for 12k rows)
                print(f"Found {len(rows)} rows.")
                
                for i, row in enumerate(rows):
                    print(f"Processing Row {i+1}...")
                    
                    email = row.get("Email", "").strip()
                    
                    first = row.get("First Name", "").strip()
                    last = row.get("Last Name", "").strip()
                    
                    # Check different domain possibilities
                    domain = row.get("Company Website", "").strip()
                    if not domain:
                        domain = row.get("Company Website Short", "").strip()
                    if not domain:
                         domain = row.get("Company Website Full", "").strip()
                         
                    if domain:
                        domain = domain.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]

                    
                    final_status = "no email found"
                    final_email = email
                    
                    # Step 1: Verify Existing
                    if email:
                        print(f"  Verifying existing: {email}")
                        mv_result = verify_million_verifier(email)
                        
                        # Accept "ok" (standard) or "safe" (generic terminology)
                        if mv_result == "ok" or mv_result == "safe":
                            final_status = "verified"
                        else:
                            print(f"  Existing email was {mv_result}. Will try to find new one.")
                            final_status = "no email found"
                    
                    # Step 2: Find if needed
                    if final_status != "verified" and first and last and domain:
                        print(f"  Searching for: {first} {last} @ {domain}")
                        found_email = find_anymail_finder(first, last, domain)
                        
                        if found_email:
                            print(f"  Found potential: {found_email}")
                            # Verify the found email
                            mv_check = verify_million_verifier(found_email)
                            
                            if mv_check == "ok" or mv_check == "safe":
                                final_email = found_email
                                final_status = "verified"
                                print(f"  Confirmed safe.")
                            else:
                                print(f"  Found email was {mv_check}.")
                    
                    # Update row
                    row["Email"] = final_email
                    row["Verified"] = final_status
                    
                    # Write ONLY if verified
                    if final_status == "verified":
                        writer.writerow(row)
                        outfile.flush()
                        print(f"  Verified. Row saved.")
                    else:
                        print(f"  Unverified/Not Found. Row deleted.")
                    
                    time.sleep(0.1) 
                    
    except Exception as e:
        print(f"Error processing: {e}")
        return

    print(f"Done. Output saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Input CSV file path")
    parser.add_argument("output_file", help="Output CSV file path")
    args = parser.parse_args()
    
    process_csv(args.input_file, args.output_file)
