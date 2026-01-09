import os
import requests
import argparse
from dotenv import load_dotenv

load_dotenv()

GHL_ACCESS_TOKEN = os.getenv("GHL_ACCESS_TOKEN")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID")
BASE_URL = "https://services.leadconnectorhq.com"

def update_ghl_contact(email, proposal_link, proposal_number):
    if not GHL_ACCESS_TOKEN or not GHL_LOCATION_ID:
        print("Error: GHL Credentials not set.")
        return False

    headers = {
        "Authorization": f"Bearer {GHL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    # 1. Find Contact
    print(f"Searching for contact: {email}")
    search_url = f"{BASE_URL}/contacts/?locationId={GHL_LOCATION_ID}&query={email}"
    try:
        resp = requests.get(search_url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        contacts = data.get('contacts', [])
        
        if not contacts:
            print(f"Contact not found for {email}. Skipping GHL update.")
            return False
            
        contact_id = contacts[0]['id']
        contact_name = contacts[0].get('name', email)
        print(f"Found Contact: {contact_name} ({contact_id})")
        
        # 2. Add Note
        note_url = f"{BASE_URL}/contacts/{contact_id}/notes"
        note_body = {
            "body": f"Proposal {proposal_number} Sent.\nLink: {proposal_link}"
        }
        resp = requests.post(note_url, headers=headers, json=note_body)
        resp.raise_for_status()
        print("Note added successfully.")
        return True

    except Exception as e:
        print(f"GHL Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--link", required=True)
    parser.add_argument("--number", required=True)
    args = parser.parse_args()
    
    update_ghl_contact(args.email, args.link, args.number)
