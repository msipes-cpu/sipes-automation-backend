#!/usr/bin/env python3
"""
Magic Button Onboarding
-----------------------
Automates new client setup:
1. Creates Google Drive Folder Structure
2. Creates Private Slack Channel
3. Posts Welcome Message

Usage:
    python3 execution/onboard_client.py --client_name "Acme Corp" --website "acmecorp.com"
"""
import os
import sys
import argparse
import time
from dotenv import load_dotenv

# Import our existing GDrive tool
# Assuming execution/gdrive_manager.py exists and has importable functions.
# If not, we might need to subprocess it or ensure it's in pythonpath.
try:
    from execution.gdrive_manager import get_drive_service, find_or_create_folder, upload_file
except ImportError:
    # Fix import path for running from root
    sys.path.append(os.getcwd())
    from execution.gdrive_manager import get_drive_service, find_or_create_folder, upload_file

start_time = time.time()
load_dotenv()

def create_slack_channel(client_name):
    """Creates a private slack channel for the client."""
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
    except ImportError:
        print("Error: slack_sdk not installed. Skipping Slack setup.")
        return None

    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("Warning: SLACK_BOT_TOKEN not found. Skipping Slack setup.")
        return None

    client = WebClient(token=token)
    
    # Sanitize channel name (lowercase, no spaces, max 80 chars)
    # e.g. "Acme Corp" -> "client-acme-corp"
    sanitized = "".join([c if c.isalnum() else "-" for c in client_name.lower()]).strip("-")
    channel_name = f"client-{sanitized}"[:80]
    
    print(f"Creating Slack Channel: #{channel_name}...")
    
    try:
        # Create Channel
        response = client.conversations_create(name=channel_name, is_private=True)
        channel_id = response["channel"]["id"]
        print(f"✓ Created channel {channel_id}")
        
        # Post Welcome Message
        welcome_msg = (
            f"*:wave: Welcome to the private channel for {client_name}!* \n\n"
            f"Use this space for quick updates and team comms.\n"
            f"We are setting up your project folders now..."
        )
        client.chat_postMessage(channel=channel_id, text=welcome_msg)
        
        return channel_id
        
    except SlackApiError as e:
        if e.response['error'] == 'name_taken':
            print(f"Warning: Channel #{channel_name} already exists.")
            return "EXISTING"
        else:
            print(f"Slack API Error: {e.response['error']}")
            return None

def main():
    parser = argparse.ArgumentParser(description="Onboard New Client")
    parser.add_argument("--client_name", required=True, help="Full Client Name")
    parser.add_argument("--website", help="Client Website")
    parser.add_argument("--dry_run", action="store_true", help="Simulate actions")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Onboarding for: {args.client_name}")
    
    if args.dry_run:
        print("[DRY RUN] Would create Drive Folders and Slack Channel.")
        return

    # 1. Drive Setup
    try:
        print("\n--- Google Drive Setup ---")
        drive_service = get_drive_service()
        
        # Root: "Clients" (Ensure this exists)
        clients_root_id, _ = find_or_create_folder(drive_service, "Clients")
        
        # Client Folder
        client_folder_id, client_link = find_or_create_folder(drive_service, args.client_name, parent_id=clients_root_id)
        
        # Subfolders
        subfolders = ["01 Admin", "02 Reports", "03 Assets", "04 Legal"]
        created_links = []
        
        for sf in subfolders:
            sf_id, sf_link = find_or_create_folder(drive_service, sf, parent_id=client_folder_id)
            print(f"✓ Created '{sf}'")
            created_links.append(f"• {sf}: {sf_link}")
            
        print(f"✓ Drive Setup Complete: {client_link}")
        
    except Exception as e:
        print(f"❌ Drive Error: {e}")
        client_link = None
        created_links = []

    # 2. Slack Setup
    print("\n--- Slack Setup ---")
    channel_id = create_slack_channel(args.client_name)
    
    # 3. ClickUp Setup
    print("\n--- ClickUp Setup ---")
    clickup_list_url = None
    try:
        # Import here to avoid issues if file doesn't exist yet
        try:
            from execution.clickup_manager import get_teams, find_or_create_space, create_folder, create_list, create_task
        except ImportError:
            sys.path.append(os.getcwd())
            from execution.clickup_manager import get_teams, find_or_create_space, create_folder, create_list, create_task

        team = get_teams()
        team_id = team['id']
        print(f"✓ Found Workspace: {team['name']}")

        # Use "Main Space" as requested or fallback to finding "Project Management"
        space_id = find_or_create_space(team_id, "Main Space")
        
        # Create Folder for Client (e.g. "SeaCow Labs")
        # In Main Space, we might want a folder per client, OR just a list per client if it's a "Project Management" folder.
        # User said: "create this in main space project management"
        # Interpretation: Space="Main Space", Folder="Project Management" (or "Clients"), List="Client Name"
        # OR Space="Main Space", Folder="Client Name".
        # Let's go with Folder="Clients" (if not existing) inside Main Space? 
        # Actually, standard ClickUp hierarchy: Space -> Folder -> List.
        # If we put it in "Main Space", we probably want a Folder called "Clients" or "Projects", and then a List for this client.
        
        # Let's try to find/create a "Clients" folder in Main Space, then add a List for this client.
        folder_id = create_folder(space_id, "Active Projects") 
        
        # Create List with Client Name
        list_name = f"{args.client_name} - Implementation"
        list_id = create_list(folder_id, list_name)
        
        clickup_list_url = f"https://app.clickup.com/{team_id}/v/l/{list_id}"
        print(f"✓ Created List: {list_name} ({clickup_list_url})")
        
        # Create Standard Tasks
        tasks = [
            ("Kickoff Call", "Schedule kickoff with client"),
            ("Access & Credentials", "Get access to CRM, Ads, etc."),
            ("System Architecture", "Draft the Mermaid diagram"),
            ("Implementation", "Build the core workflows"),
            ("Testing & QA", "Verify all flows"),
            ("Go Live", "Launch and monitor")
        ]
        
        for t_name, t_desc in tasks:
            create_task(list_id, t_name, description=t_desc)
            
        print("✓ Populated standard tasks")

    except Exception as e:
        print(f"❌ ClickUp Error: {e}")

    # 4. Final Wrap-up (Post links to Slack if applicable)
    if channel_id and channel_id != "EXISTING" and client_link:
        try:
            from slack_sdk import WebClient
            client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
            
            links_text = "\n".join(created_links)
            msg = (
                f"*:file_folder: Project Folders Ready*\n"
                f"Access your Main Folder here: {client_link}\n\n"
                f"{links_text}\n\n"
                f"*:white_check_mark: Project Board:*\n{clickup_list_url if clickup_list_url else 'Pending'}"
            )
            client.chat_postMessage(channel=channel_id, text=msg)
            print("✓ Posted Drive & ClickUp links to Slack")
        except:
            pass

    print(f"\n✨ Onboarding Complete in {time.time() - start_time:.2f}s")
    
if __name__ == "__main__":
    main()
