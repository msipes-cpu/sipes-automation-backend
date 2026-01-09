import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GHL_ACCESS_TOKEN = os.getenv("GHL_ACCESS_TOKEN")

def send_sms(contact_id, message_body):
    """
    Sends an SMS to the specified contact via GoHighLevel.
    """
    headers = {
        "Authorization": f"Bearer {GHL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    url = "https://services.leadconnectorhq.com/conversations/messages"
    
    # Payload for sending generic message
    # To initiate, we usually need the contactId.
    payload = {
        "type": "SMS",
        "contactId": contact_id,
        "message": message_body
        # "mobileId": ... might be needed if multiple numbers? usually defaults.
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # If 400+, print details
        if not response.ok:
            print(f"Failed to send SMS: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        data = response.json()
        print(f"SMS sent successfully! Message ID: {data.get('conversationId') or data.get('id')}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS: {e}")
        return False
