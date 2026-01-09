import sys
import os

def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# ... inside functions replace print with log ...

import requests
import json
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APOLLO_MATCH_URL = "https://api.apollo.io/v1/people/match"

def enrich_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enriches a list of leads using Apollo's /people/match endpoint.
    This helps 'reveal' missing emails if the initial search didn't provide them,
    or if we want to find personal emails.
    """
    if not APOLLO_API_KEY:
        raise ValueError("APOLLO_API_KEY environment variable is not set.")

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY
    }

    enriched_leads = []
    
    log(f"Enriching {len(leads)} leads via Apollo Match...")

    # process in batches if necessary, but for now simple iteration or small batch 
    # Apollo's match endpoint usually takes one record at a time or a small batch? 
    # The doc says /people/match takes a single person's details. 
    # For bulk, there is /mixed_people/search but 'match' is best for specific enrichment.
    # Actually, let's check if there is a bulk match. 
    # If not, we iterate. Rate limits apply.
    
    for lead in leads:
        # We need at least some info to match. 
        # Usually from a search we have an ID, or Name + Company.
        
        payload = {}
        
        if lead.get('id'):
             payload['id'] = lead.get('id')
        elif lead.get('email'):
            payload['email'] = lead.get('email')
        else:
            if lead.get('first_name') and lead.get('last_name'):
                 payload['first_name'] = lead.get('first_name')
                 payload['last_name'] = lead.get('last_name')
            
            if lead.get('organization_name'):
                 payload['organization_name'] = lead.get('organization_name')
            
            if lead.get('domain'):
                 payload['domain'] = lead.get('domain')

        # If payload is empty, we can't enrich
        if not payload:
            log(f"Skipping lead: Not enough info to match. {lead}")
            enriched_leads.append(lead)
            continue
        
        # Add reveal_personal_emails=true if usually desired, or make it an option?
        # For B2B, we usually want work emails.
        # But 'reveal_email' is often implied if we want to spend a credit.
        payload['reveal_personal_emails'] = True 
        payload['reveal_phone_number'] = False # Optional, save credits? assuming False for now

        try:
            response = requests.post(APOLLO_MATCH_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                person = data.get('person')
                if person:
                    # Update lead with new data. 
                    # We merge, preferring the new enriched data? 
                    # Usually 'person' object has the full details.
                    # Let's update the original dictionary with the new one 
                    # but keep any custom fields we might have added.
                    lead.update(person)
                    lead['enrichment_status'] = 'success'
                    log(f"Enriched: {lead.get('name') or lead.get('email')}")
                else:
                    lead['enrichment_status'] = 'no_match'
                    log(f"No match found for: {lead.get('name')}")
            else:
                 log(f"Failed to enrich {lead.get('name')}: {response.status_code} - {response.text}")
                 lead['enrichment_status'] = 'error'
                 lead['enrichment_error'] = response.text

        except Exception as e:
            log(f"Error calling Apollo Match: {e}")
            lead['enrichment_status'] = 'error'
            lead['enrichment_error'] = str(e)
            
        enriched_leads.append(lead)
        
    return enriched_leads

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich leads using Apollo Match")
    parser.add_argument("--input_file", help="Path to JSON input file")
    parser.add_argument("--input_json", help="JSON string input")
    
    args = parser.parse_args()
    
    leads = []
    if args.input_file:
        try:
            with open(args.input_file, 'r') as f:
                leads = json.load(f)
        except Exception as e:
            log(f"Error reading file: {e}")
            exit(1)
    elif args.input_json:
        try:
            leads = json.loads(args.input_json)
        except Exception as e:
            log(f"Error parsing JSON: {e}")
            exit(1)
            
    if not leads:
        log("No leads provided.")
        exit(1)
        
    try:
        results = enrich_leads(leads)
        print(json.dumps(results, indent=2))
    except Exception as e:
        log(f"Unexpected error: {e}")
        exit(1)
