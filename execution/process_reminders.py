import sys
import os
import json
from datetime import datetime, timedelta
import dateutil.parser

# Ensure imports work
sys.path.append(os.path.join(os.getcwd(), 'execution'))

from ghl_send_sms import send_sms
from state_utils import load_state, mark_reminder_sent, is_reminder_sent

def process_reminders():
    print("Checking for reminders...")
    state = load_state()
    bookings = state.get("processed_bookings", {})
    
    now = datetime.now() # Warning: Timezone naive. Cal.com often returns UTC.
    # We should handle timezones properly. Assuming System is UTC or local matching Cal.com?
    # Cal.com "startTime": "2025-12-18T12:20:00.000Z" (UTC)
    
    from datetime import timezone
    now_utc = datetime.now(timezone.utc)
    
    for uid, data in bookings.items():
        contact_id = data.get("contact_id")
        start_str = data.get("start_time")
        
        if not contact_id or not start_str:
            continue
            
        try:
            start_dt = dateutil.parser.isoparse(start_str)
        except:
            print(f"Failed to parse time for {uid}: {start_str}")
            continue
            
        # Calculate time until meeting
        diff = start_dt - now_utc
        minutes_remaining = diff.total_seconds() / 60
        
        # Define Windows (in minutes) w/ tolerance
        windows = {
            "12h": {"target": 720, "tolerance": 30},
            "1h": {"target": 60, "tolerance": 15},
            "30m": {"target": 30, "tolerance": 10},
            "1m": {"target": 1, "tolerance": 5} 
        }
        
        for name, spec in windows.items():
            target = spec["target"]
            tol = spec["tolerance"]
            
            # Logic: If remaining time is between target-tol and target+tol
            # AND not sent
            if (target - tol) <= minutes_remaining <= (target + tol):
                if not is_reminder_sent(state, uid, name):
                    print(f"Sending {name} reminder for {uid} (Starts in {minutes_remaining:.1f} mins)")
                    
                    # Construct Message
                    # "Hey, looking forward to meeting, which is in a specific amount of time. Let me know if you have any questions or need to move it."
                    time_desc = f"{int(target/60)} hours" if target >= 60 else f"{int(target)} minutes"
                    if target == 1: time_desc = "1 minute"
                    
                    msg = f"Hey, looking forward to meeting, which is in {time_desc}. Let me know if you have any questions or need to move it."
                    
                    # Send
                    success = send_sms(contact_id, msg)
                    if success:
                        mark_reminder_sent(state, uid, name)
                # else: already sent
            # else: not inside window
            
    print("Reminder check complete.")

if __name__ == "__main__":
    process_reminders()
