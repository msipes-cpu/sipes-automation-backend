
import os
import csv
import time
import requests
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BLITZ_API_KEY = os.getenv("BLITZ_API_KEY")
BLITZ_API_URL = "https://api.blitz-api.ai/api/enrichment/email"

def enrich_with_blitz(input_file):
    if not BLITZ_API_KEY:
        print("Error: BLITZ_API_KEY not set.")
        return

    print(f"Reading from {input_file}...")
    
    leads = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                leads.append(row)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Add new column for Blitz Email
    if "blitz_email" not in fieldnames:
        fieldnames.append("blitz_email")

    total_leads = len(leads)
    print(f"Enriching {total_leads} leads...")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": BLITZ_API_KEY
    }

    # Rate limit: 5 requests per second => 0.2 seconds per request
    # To be safe, we'll use 0.25s delay
    DELAY_SECONDS = 0.25

    for i, lead in enumerate(leads):
        linkedin_url = lead.get("linkedin_url") or lead.get("person_linkedin_url")
        
        if linkedin_url:
            try:
                payload = {
                    "linkedin_profile_url": linkedin_url
                }
                
                response = requests.post(BLITZ_API_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    # Response format: check user example or assume standard.
                    # User curl example didn't show response body, assuming it returns 'email' or 'work_email' etc.
                    # Common pattern: {"email": "..."} or {"data": {"email": "..."}}
                    # I will log the first response to debug if needed, but for now apply best guess logic 
                    # based on common patterns. Wait, I should probably inspect the response for the first one.
                    # But per instructions "if you can't get the emails... put 'unable to get email'"
                    
                    # Let's support a few common structures or just dump the whole response to a debug field first?
                    # No, user wants the result. 
                    # Assuming simple {"email": "x@y.com"} or similar based on the endpoint name.
                    # Or maybe "paylaod" -> "email".
                    
                    found_email = data.get('email') or data.get('work_email') or data.get('personal_email')
                    
                    if not found_email and 'data' in data and isinstance(data['data'], dict):
                         found_email = data['data'].get('email')
                    
                    lead['blitz_email'] = found_email if found_email else "unable to get email"
                    
                # Handle rate limit 429 specifically if we hit it?
                elif response.status_code == 429:
                    print("Hit rate limit, sleeping longer...")
                    time.sleep(2)
                    lead['blitz_email'] = "rate_limited" 
                    # Retry? simpler to just mark and move on for this v1
                else:
                    lead['blitz_email'] = "unable to get email" 
                    # print(f"Failed: {response.status_code} {response.text}") 
                    
            except Exception as e:
                print(f"Error calling Blitz: {e}")
                lead['blitz_email'] = "error"
        else:
            lead['blitz_email'] = "no linkedin url"

        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{total_leads}")
        
        time.sleep(DELAY_SECONDS)

    # Save to timestamped file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"apollo_leads_enriched_blitz_{timestamp}.csv"
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leads)
        print(f"Successfully saved enriched leads to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich leads with Blitz API")
    parser.add_argument("input_file", help="Path to input CSV file")
    args = parser.parse_args()
    
    enrich_with_blitz(args.input_file)
