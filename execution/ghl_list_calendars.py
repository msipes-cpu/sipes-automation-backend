import os
import requests
from dotenv import load_dotenv

load_dotenv()

GHL_ACCESS_TOKEN = os.getenv("GHL_ACCESS_TOKEN")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID")

def list_calendars():
    headers = {
        "Authorization": f"Bearer {GHL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    url = f"https://services.leadconnectorhq.com/calendars/?locationId={GHL_LOCATION_ID}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        calendars = data.get("calendars", [])
        print(f"Found {len(calendars)} calendars:")
        for c in calendars:
            print(f"- {c['name']} (ID: {c['id']})")
                
    except requests.exceptions.RequestException as e:
        print(f"Error listing calendars: {e}")
        if hasattr(e, 'response') and e.response:
             print(f"Response: {e.response.text}")

if __name__ == "__main__":
    list_calendars()
