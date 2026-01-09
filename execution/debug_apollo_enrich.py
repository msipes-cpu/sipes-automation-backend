
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")

def main():
    print("Testing Apollo Enrichment...")
    if not APOLLO_API_KEY:
        print("No API Key")
        return

    # A sample lead from the failed batch (Ahmet Dogan)
    # We'll try to find him or retrieve him.
    # We can try name + company search/match.
    
    url = "https://api.apollo.io/v1/people/match"
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY
    }
    
    payload = {
        "first_name": "Ahmet",
        "last_name": "Dogan",
        "organization_name": "DeepMind", # Just kidding, let's use his real one or empty?
        # CSV said: Founder & CEO at (Company Name was empty in snippet?) 
        # Wait, CSV snippet:
        # Ahmet Dogan,Ahmet,Dogan,Founder & CEO,,email_not_unlocked@domain.com
        # Company field was EMPTY in CSV! that's why match failed!
        # If company is empty, we can't match easily.
        
        "domain": "google.com" # Dummy test
    }
    
    # Wait, why was company empty in CSV?
    # Because `apollo_search.py` didn't get it?
    # `lead.get('organization_name')` or `company_name`?
    # `convert_leads_to_csv.py` uses `lead.get("company_name") or lead.get("organization_name", "")`.
    
    # Let's try to fetch a known person or search generic.
    pass

    # Actually, let's look at the JSON `powerhouse_verified_...` to see why company is missing.
    # If company is missing, that's the root cause.
    
if __name__ == "__main__":
    main()
