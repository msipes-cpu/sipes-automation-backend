import os
import requests
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

CALCOM_API_KEY = os.getenv("CALCOM_API_KEY")

def fetch_bookings():
    """
    Fetches bookings from Cal.com.
    Returns a list of bookings that are 'ACCEPTED' or 'CONFIRMED'.
    """
    url = "https://api.cal.com/v1/bookings"
    params = {
        "apiKey": CALCOM_API_KEY,
        "status": "ACCEPTED" 
    }
    
    try:
        # Removing status param for now to test basic connectivity
        # params = {"apiKey": CALCOM_API_KEY, "status": "ACCEPTED"} 
        params = {"apiKey": CALCOM_API_KEY} 
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        bookings = data.get("bookings", [])
        return bookings

    except requests.exceptions.RequestException as e:
        print(f"Error fetching bookings: {e}")
        if hasattr(e, 'response') and e.response:
             print(f"Response Body: {e.response.text}")
        return []

if __name__ == "__main__":
    bookings = fetch_bookings()
    print(f"Found {len(bookings)} bookings.")
    if bookings:
        print("Sample Booking JSON (Full):")
        import json
        b = bookings[0]
        print(json.dumps(b, indent=2))
        
        print("\n--- Keys in 'responses' ---")
        print(b.get("responses", {}).keys())
        
    for b in bookings[:2]: # Print first 2 to verify structure
        print(f"- {b['title']}")
