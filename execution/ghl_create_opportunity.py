import os
import requests

from dotenv import load_dotenv
load_dotenv()

GHL_ACCESS_TOKEN = os.getenv("GHL_ACCESS_TOKEN")
GHL_PIPELINE_ID = os.getenv("GHL_PIPELINE_ID")
GHL_STAGE_ID = os.getenv("GHL_STAGE_ID")

def create_opportunity(contact_id, title, monetary_value=0):
    """
    Creates an opportunity for the given contact.
    """
    headers = {
        "Authorization": f"Bearer {GHL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    url = "https://services.leadconnectorhq.com/opportunities/"
    
    payload = {
        "pipelineId": GHL_PIPELINE_ID,
        "locationId": os.getenv("GHL_LOCATION_ID"), # Sometimes required depending on auth type
        "contactId": contact_id,
        "name": title,
        #"stageId": GHL_STAGE_ID,
        "status": "open"
    }

    if monetary_value:
        payload["monetaryValue"] = monetary_value

    try:
        response = requests.post(url, headers=headers, json=payload)
        if not response.ok:
            print(f"Failed to create opportunity. Status: {response.status_code}")
            print(f"Response: {response.text}")
            response.raise_for_status()
            
        data = response.json()
        opp_id = data.get("opportunity", {}).get("id")
        print(f"Created opportunity {opp_id}")
        
        # Now try to update stage if provided
        if GHL_STAGE_ID:
            update_url = f"https://services.leadconnectorhq.com/opportunities/{opp_id}"
            update_payload = {
                "pipelineId": GHL_PIPELINE_ID,
                "stageId": GHL_STAGE_ID,
                "locationId": os.getenv("GHL_LOCATION_ID"),
                "status": "open"
            }
            try:
                resp = requests.put(update_url, headers=headers, json=update_payload)
                if resp.ok:
                    print(f"Updated opportunity stage to {GHL_STAGE_ID}")
                else:
                    print(f"Failed to update stage: {resp.text}")
            except Exception as e:
                print(f"Exception updating stage: {e}")

        return opp_id
    except requests.exceptions.RequestException as e:
        # Handle duplicate opportunity case
        if "Can not create duplicate opportunity" in str(e) or (hasattr(e, 'response') and "duplicate opportunity" in e.response.text):
            print("Opportunity already exists. Fetching to update stage...")
            # Search for existing opportunity
            search_url = f"https://services.leadconnectorhq.com/opportunities/search?location_id={os.getenv('GHL_LOCATION_ID')}&contact_id={contact_id}"
            try:
                search_resp = requests.get(search_url, headers=headers)
                if search_resp.ok:
                    data = search_resp.json()
                    opps = data.get("opportunities", [])
                    if opps:
                        # Assuming the most recent one or matching one
                        existing_opp = opps[0]
                        existing_opp_id = existing_opp["id"]
                        print(f"Found existing opportunity {existing_opp_id}.")
                        print(f"Keys: {list(existing_opp.keys())}")
                        
                        # Apply the stage update logic (reused)
                        if GHL_STAGE_ID:
                            update_url = f"https://services.leadconnectorhq.com/opportunities/{existing_opp_id}"
                            
                            # Try pipelineStageId based on error feedback? Or use keys to guess?
                            # For now, remove locationId as it was flagged
                            update_payload = {
                                "pipelineId": GHL_PIPELINE_ID,
                                "pipelineStageId": GHL_STAGE_ID, # Trying new key
                                "name": existing_opp.get("name"),
                                "status": "open"
                            }
                            resp = requests.put(update_url, headers=headers, json=update_payload)
                            if resp.ok:
                                print(f"Updated opportunity stage to {GHL_STAGE_ID}")
                                return existing_opp_id
                            else:
                                print(f"Failed to update stage: {resp.text}")
                                
                                # Fallback test?
                                if "should not exist" in resp.text:
                                    print("Trying alternate key 'stageId' without locationId...")
                                    update_payload = {
                                        "pipelineId": GHL_PIPELINE_ID,
                                        "stageId": GHL_STAGE_ID,
                                        "status": "open"
                                    }
                                    resp = requests.put(update_url, headers=headers, json=update_payload)
                                    print(f"Retry status: {resp.status_code} - {resp.text}")
                    else:
                        print(f"No opportunities found for contact {contact_id}.")
                else:
                    print(f"Search failed: {search_resp.status_code} - {search_resp.text}")
            except Exception as search_e:
                print(f"Error searching opportunity: {search_e}")
                
        print(f"Error creating opportunity exception: {e}")
        return None
