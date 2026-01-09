import requests
import sys

API_KEY = "88f2c063-2b67-4cf6-936f-90ccd3b73494_ggw7d77"
BASE_URL = "https://server.smartlead.ai/api/v1/campaigns"

def main():
    print(f"Verifying API Key: {API_KEY}...")
    try:
        response = requests.get(BASE_URL, params={"api_key": API_KEY}, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # It might be a list or a dict containing campaigns
            count = len(data) if isinstance(data, list) else len(data.get('campaigns', []))
            print(f"Success! Found {count} campaigns.")
            # Print first campaign name if available
            if isinstance(data, list) and count > 0:
                print(f"Sample Campaign: {data[0].get('name', 'Unknown')}")
        else:
            print(f"Failed. Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
