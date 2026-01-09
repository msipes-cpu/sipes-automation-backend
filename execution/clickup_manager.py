import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.clickup.com/api/v2"

def get_headers():
    token = os.getenv("CLICKUP_API_TOKEN")
    if not token:
        raise ValueError("CLICKUP_API_TOKEN not found in .env")
    return {
        "Authorization": token,
        "Content-Type": "application/json"
    }

def get_teams():
    """Get authorized teams (workspaces). Returns the first team found."""
    url = f"{BASE_URL}/team"
    resp = requests.get(url, headers=get_headers())
    resp.raise_for_status()
    teams = resp.json().get("teams", [])
    if not teams:
        raise ValueError("No teams found in ClickUp.")
    return teams[0] # Return first team

def get_spaces(team_id):
    """Get all spaces in a team."""
    url = f"{BASE_URL}/team/{team_id}/space"
    resp = requests.get(url, headers=get_headers())
    resp.raise_for_status()
    return resp.json().get("spaces", [])

def find_or_create_space(team_id, space_name="Clients"):
    """Finds a space by name or creates it."""
    spaces = get_spaces(team_id)
    for space in spaces:
        if space["name"].lower() == space_name.lower():
            print(f"Found existing space: {space['name']}")
            return space["id"]
    
    # Create
    print(f"Creating new space: {space_name}...")
    url = f"{BASE_URL}/team/{team_id}/space"
    payload = {
        "name": space_name,
        "multiple_assignees": True,
        "features": {"due_dates": {"enabled": True, "start_date": True, "remap_due_dates": True}}
    }
    resp = requests.post(url, headers=get_headers(), json=payload)
    resp.raise_for_status()
    return resp.json().get("id")

def create_folder(space_id, folder_name):
    """Creates a folder in a space."""
    # Check if exists (ClickUp doesn't enforce unique names easily, but we can check)
    url = f"{BASE_URL}/space/{space_id}/folder"
    resp = requests.get(url, headers=get_headers())
    folders = resp.json().get("folders", [])
    for f in folders:
        if f["name"].lower() == folder_name.lower():
            print(f"Found existing folder: {folder_name}")
            return f["id"]

    print(f"Creating folder: {folder_name}...")
    payload = {"name": folder_name}
    resp = requests.post(url, headers=get_headers(), json=payload)
    resp.raise_for_status()
    return resp.json().get("id")

def create_list(folder_id, list_name):
    """Creates a list in a folder."""
    # Check existing
    url = f"{BASE_URL}/folder/{folder_id}/list"
    resp = requests.get(url, headers=get_headers())
    lists = resp.json().get("lists", [])
    for l in lists:
        if l["name"].lower() == list_name.lower():
            return l["id"]

    print(f"Creating list: {list_name}...")
    payload = {"name": list_name}
    resp = requests.post(url, headers=get_headers(), json=payload)
    resp.raise_for_status()
    return resp.json().get("id")

def create_task(list_id, name, description=None, due_date=None):
    """Creates a task in a list."""
    url = f"{BASE_URL}/list/{list_id}/task"
    payload = {
        "name": name,
        "description": description or ""
    }
    if due_date:
        payload["due_date"] = due_date
        
    resp = requests.post(url, headers=get_headers(), json=payload)
    if not resp.ok:
        print(f"Failed to create task {name}: {resp.text}")
    return resp.json().get("id")
