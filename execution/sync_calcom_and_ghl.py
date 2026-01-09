import sys
import os
import requests
import dateutil.parser
import dateutil.tz
from datetime import timezone

# Adjust path for execution module imports
sys.path.append(os.path.join(os.getcwd(), 'execution'))

from ghl_upsert_contact import upsert_contact
from ghl_create_opportunity import create_opportunity
from ghl_send_sms import send_sms
from state_utils import load_state, mark_booking_processed, is_booking_processed

# Config
WELCOME_MSG_TEMPLATE = "Hey, thank you so much for booking a meeting with us. Looking forward to speaking with you, Michael."

def process_single_booking(booking, state):
    """
    Process a single booking object from Cal.com.
    Returns True if processed successfully, False otherwise.
    """
    uid = booking.get("uid")
    if not uid:
        print("Error: Booking missing UID.")
        return False
        
    title = booking.get("title", "")
    
    # FILTER: Only "Kick Off" meetings
    if "Kick Off" not in title:
        print(f"Skipping non-Kick Off meeting: {uid} - {title}")
        return False

    # Check state
    is_new = not is_booking_processed(state, uid)
    if not is_new:
        print(f"Booking {uid} already processed. Skipping.")
        # If you needed to update existing bookings, you'd do it here.
        # But per user request we only touch new ones.
        return True

    print(f"Processing New Kick Off: {uid} - {title}")

    # Extract details
    responses = booking.get("responses", {})
    email = responses.get("email")
    name = responses.get("name")
    start_time = booking.get("startTime")
    metadata = booking.get("metadata", {})
    video_call_url = metadata.get("videoCallUrl", "")
    
    # Phone extraction
    phone = responses.get("phone")
    if not phone and booking.get("attendees"):
        # Fallback logic if needed
        pass
        
    # Name Parsing
    if isinstance(name, dict):
         clean_name = f"{name.get('firstName', '')} {name.get('lastName', '')}"
         first_name = name.get("firstName", "Unknown")
         last_name = name.get("lastName", "")
    elif isinstance(name, str):
         clean_name = name
         parts = name.split(maxsplit=1)
         first_name = parts[0]
         last_name = parts[1] if len(parts) > 1 else ""
    else:
         clean_name = "Unknown"
         first_name = "Unknown"
         last_name = ""

    # Business Name Extraction
    business_name = responses.get("company") or responses.get("business_name")
    if not business_name and email and "@" in email:
        domain = email.split("@")[1]
        if "gmail" not in domain and "yahoo" not in domain:
            business_name = domain.split(".")[0].capitalize()
    
    if not business_name:
        business_name = "Lead"

    # Time Formatting (ET)
    try:
        start_dt = dateutil.parser.isoparse(start_time)
        et_tz = dateutil.tz.gettz('America/New_York')
        start_dt_et = start_dt.astimezone(et_tz)
        time_str = start_dt_et.strftime("%a, %b %d %I:%M %p ET")
    except Exception as e:
        print(f"Time parsing failed: {e}")
        time_str = start_time

    # Construct Opportunity Name
    opp_name = f"{business_name} {clean_name} - {time_str}"
    print(f"Generated Opp Name: {opp_name}")

    # 1. Upsert Contact
    contact_id = upsert_contact(email, first_name, last_name, phone=phone)
    if not contact_id:
        print("Failed to get/create contact.")
        return False

    # 2. Create Opportunity
    opp_id = create_opportunity(contact_id, opp_name)
    
    # 3. Update Source & Name (Only on Initial Setup)
    if opp_id:
         # Need headers for manual update
         headers = {
            "Authorization": f"Bearer {os.getenv('GHL_ACCESS_TOKEN')}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
         }
         update_url = f"https://services.leadconnectorhq.com/opportunities/{opp_id}"
         
         payload = {
             "pipelineId": os.getenv("GHL_PIPELINE_ID"),
             "source": video_call_url,
             "name": opp_name
         }
         try:
             requests.put(update_url, headers=headers, json=payload)
             print(f"Initial Setup: Updated source to {video_call_url} and name to {opp_name}")
         except Exception as e: 
             print(f"Update failed: {e}")

    # 4. SMS Actions
    if phone:
        print("Sending welcome SMS...")
        send_sms(contact_id, WELCOME_MSG_TEMPLATE)
    else:
        print("Skipping SMS: No phone number provided in booking.")
    
    # Mark as processed
    mark_booking_processed(state, uid, data={"title": opp_name, "email": email, "start_time": start_time, "contact_id": contact_id})
    
    return True

# Main block for manual polling reuse
def main():
    from fetch_calcom_bookings import fetch_bookings
    print("Starting sync job...")
    state = load_state()
    bookings = fetch_bookings()
    print(f"Fetched {len(bookings)} bookings.")
    
    count = 0
    for b in bookings:
        if process_single_booking(b, state):
             count += 1
    print(f"Job finished. processed {count}.")

if __name__ == "__main__":
    main()
