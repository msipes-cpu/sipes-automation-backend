import json
import os

STATE_FILE = "execution/sync_state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"processed_bookings": {}, "reminders_sent": {}}
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"processed_bookings": {}, "reminders_sent": {}}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def is_booking_processed(state, uid):
    return uid in state.get("processed_bookings", {})

def mark_booking_processed(state, uid, data=None):
    if "processed_bookings" not in state:
        state["processed_bookings"] = {}
    state["processed_bookings"][uid] = data or {"timestamp": "now"}
    save_state(state)

def is_reminder_sent(state, uid, window):
    # window = "12h", "1h", "30m", "1m"
    reminders = state.get("reminders_sent", {})
    booking_reminders = reminders.get(uid, [])
    return window in booking_reminders

def mark_reminder_sent(state, uid, window):
    if "reminders_sent" not in state:
        state["reminders_sent"] = {}
    if uid not in state["reminders_sent"]:
        state["reminders_sent"][uid] = []
    
    if window not in state["reminders_sent"][uid]:
        state["reminders_sent"][uid].append(window)
        save_state(state)
