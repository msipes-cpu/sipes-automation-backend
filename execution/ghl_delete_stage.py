import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GHL_ACCESS_TOKEN = os.getenv("GHL_ACCESS_TOKEN")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID")
GHL_PIPELINE_ID = os.getenv("GHL_PIPELINE_ID")

def delete_stage(stage_id_to_remove):
    headers = {
        "Authorization": f"Bearer {GHL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    # 1. Get current pipeline
    get_url = f"https://services.leadconnectorhq.com/opportunities/pipelines/{GHL_PIPELINE_ID}?locationId={GHL_LOCATION_ID}"
    
    try:
        response = requests.get(get_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        pipeline = data.get("pipeline") # Single pipeline object
        if not pipeline:
            print("Pipeline not found.")
            return

        current_stages = pipeline.get("stages", [])
        new_stages = [s for s in current_stages if s["id"] != stage_id_to_remove]
        
        if len(new_stages) == len(current_stages):
            print("Stage ID not found in pipeline. Nothing to delete.")
            return

        print(f"Removing stage. Count went from {len(current_stages)} to {len(new_stages)}.")

        # 2. Update pipeline
        update_url = f"https://services.leadconnectorhq.com/opportunities/pipelines/{GHL_PIPELINE_ID}"
        
        payload = {
            "name": pipeline["name"],
            "stages": new_stages,
            "locationId": GHL_LOCATION_ID
        }

        resp = requests.put(update_url, headers=headers, json=payload)
        resp.raise_for_status()
        print("Pipeline updated successfully. Stage removed.")

    except requests.exceptions.RequestException as e:
        print(f"Error updating pipeline: {e}")
        if hasattr(e, 'response') and e.response:
             print(f"Response: {e.response.text}")

if __name__ == "__main__":
    # Stage ID for "Demo Booked" provided by user context or previous step
    # We'll hardcode it here or pass it in. Check context: e2ec572a-69cc-4208-a9e7-9a55617d89ad
    TARGET_STAGE_ID = "e2ec572a-69cc-4208-a9e7-9a55617d89ad" 
    delete_stage(TARGET_STAGE_ID)
