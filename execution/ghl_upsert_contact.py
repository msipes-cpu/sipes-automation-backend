import os
import requests
import json

from dotenv import load_dotenv
load_dotenv()

GHL_ACCESS_TOKEN = os.getenv("GHL_ACCESS_TOKEN")
# If using V1/Location API Key, you often just use `Authorization: Bearer <API_KEY>`
# If using V2/OAuth, it's also `Authorization: Bearer <ACCESS_TOKEN>`

def upsert_contact(email, first_name, last_name, phone=None):
    """
    Search for a contact by email. 
    If found, update it. 
    If not, create it.
    Returns the Contact ID.
    """
    headers = {
        "Authorization": f"Bearer {GHL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-07-28" # Required for V2 API
    }
    
    # 1. Search for contact
    # Add locationId to lookup to ensure scoping is correct
    lookup_url = f"https://services.leadconnectorhq.com/contacts/lookup?email={email}&locationId={os.getenv('GHL_LOCATION_ID')}"
    
    contact_id = None
    
    try:
        # Try to find existing contact
        response = requests.get(lookup_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data and "contacts" in data and len(data["contacts"]) > 0:
                contact_id = data["contacts"][0]["id"]
                print(f"Found existing contact: {contact_id}")
        
        # Prepare payload
        payload = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "name": f"{first_name} {last_name}",
            "source": "Cal.com Sync"
        }
        if phone:
            payload["phone"] = phone

        if contact_id:
            # Update existing - Do NOT include locationId usually for updates
            update_url = f"https://services.leadconnectorhq.com/contacts/{contact_id}"
            resp = requests.put(update_url, headers=headers, json=payload)
            resp.raise_for_status()
            print(f"Updated contact {contact_id}")
            return contact_id
        else:
            # Create new - Include locationId
            payload["locationId"] = os.getenv("GHL_LOCATION_ID")
            create_url = "https://services.leadconnectorhq.com/contacts/"
            resp = requests.post(create_url, headers=headers, json=payload)
            
            if not resp.ok:
                print(f"Error creating contact: {resp.status_code} - {resp.text}")
                
                # Check if it's a duplicate error and extract ID
                try:
                    err_data = resp.json()
                    if err_data.get("message") == "This location does not allow duplicated contacts." and "meta" in err_data:
                         dup_id = err_data["meta"].get("contactId")
                         if dup_id:
                             print(f"Recovered contact ID from duplicate error: {dup_id}")
                             return dup_id
                except:
                    pass
                    
                resp.raise_for_status()
                
            new_data = resp.json()
            # Response usually contains { "contact": { "id": "..." } }
            new_id = new_data.get("contact", {}).get("id")
            print(f"Created new contact {new_id}")
            return new_id

    except requests.exceptions.RequestException as e:
        print(f"Error upserting contact: {e}")
        # Print response text for debugging
        if hasattr(e, 'response') and e.response:
             print(f"Response: {e.response.text}")
        return None
