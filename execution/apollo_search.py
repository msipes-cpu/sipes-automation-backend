import os
import requests
import json
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Placeholder for Apollo API Key from env
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APOLLO_API_URL = "https://api.apollo.io/v1/mixed_people/search"

def search_apollo(
    job_titles: List[str] = None,
    locations: List[str] = None,
    organization_num_employees_ranges: List[str] = None,
    keywords: List[str] = None,
    limit: int = 10,
    page: int = 1
) -> List[Dict[str, Any]]:
    """
    Searches Apollo for leads based on criteria.
    """
    if not APOLLO_API_KEY:
        raise ValueError("APOLLO_API_KEY environment variable is not set.")

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY
    }

    # Construct the payload
    payload = {
        "page": page,
        "per_page": limit,
    }
    
    if job_titles:
        payload["person_titles"] = job_titles
    if locations:
        payload["person_locations"] = locations
    if organization_num_employees_ranges:
        payload["organization_num_employees_ranges"] = organization_num_employees_ranges
    if keywords:
        # Use q_organization_keyword_tags to filter by company keywords/industry
        payload["q_organization_keyword_tags"] = keywords


    
    # Debug print
    print(f"Searching Apollo with payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(APOLLO_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        people = data.get("people", [])
        print(f"Found {len(people)} leads on page 1.")
        
        return people

    except requests.exceptions.RequestException as e:
        print(f"Error querying Apollo API: {e}")
        if e.response is not None:
             print(f"Response: {e.response.text}")
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search Apollo for leads")
    parser.add_argument("--job_titles", nargs="+", help="List of job titles", default=[])
    parser.add_argument("--locations", nargs="+", help="List of locations (e.g., 'New York, NY', 'US')", default=[])
    parser.add_argument("--employees", nargs="+", help="List of employee ranges (e.g., '1,10', '11,50')", default=[])
    parser.add_argument("--keywords", nargs="+", help="List of keywords/industry tags", default=[])
    parser.add_argument("--limit", type=int, help="Number of leads to fetch", default=5)
    
    args = parser.parse_args()
    
    try:
        results = search_apollo(
            job_titles=args.job_titles, 
            locations=args.locations,
            organization_num_employees_ranges=args.employees,
            keywords=args.keywords,
            limit=args.limit
        )
        # Output results as JSON
        print(json.dumps(results, indent=2))
            
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
