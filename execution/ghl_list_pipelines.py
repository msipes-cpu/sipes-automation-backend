import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GHL_ACCESS_TOKEN = os.getenv("GHL_ACCESS_TOKEN")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID")

def list_pipelines():
    headers = {
        "Authorization": f"Bearer {GHL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    # If Location ID is not in token (e.g. OAuth), it might be needed in query param
    url = f"https://services.leadconnectorhq.com/opportunities/pipelines?locationId={GHL_LOCATION_ID}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        pipelines = data.get("pipelines", [])
        print(f"Found {len(pipelines)} pipelines:")
        for p in pipelines:
            print(f"\nID: {p['id']}")
            print(f"Name: {p['name']}")
            print("Stages:")
            for s in p.get("stages", []):
                print(f"  - {s['name']} (ID: {s['id']})")
                
    except requests.exceptions.RequestException as e:
        print(f"Error listing pipelines: {e}")
        if hasattr(e, 'response') and e.response:
             print(f"Response: {e.response.text}")

if __name__ == "__main__":
    if not GHL_ACCESS_TOKEN or not GHL_LOCATION_ID:
        print("Please set GHL_ACCESS_TOKEN and GHL_LOCATION_ID in .env first.")
    else:
        list_pipelines()
