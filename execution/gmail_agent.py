import os
import argparse
import base64
import json
from email.mime.text import MIMEText
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Constants
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json")
# The user to impersonate
IMPERSONATED_USER = "msipes@sipesautomation.com"
SCOPES = ['https://mail.google.com/']

def get_gmail_service():
    """Authenticate acting as the user."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Error: {SERVICE_ACCOUNT_FILE} not found.")
        return None

    try:
        # Load credentials from the service account file manually to fix key format
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            info = json.load(f)
            
        # Ensure private key is formatted correctly
        if 'private_key' in info:
            raw_key = info['private_key']
            # Try handling multiple newline variants
            key = raw_key.replace('\\n', '\n')
            info['private_key'] = key

        creds = Credentials.from_service_account_info(
            info, 
            scopes=SCOPES
        )
        
        # Impersonate the user
        delegated_creds = creds.with_subject(IMPERSONATED_USER)
        
        # Build the Gmail service
        service = build('gmail', 'v1', credentials=delegated_creds)
        return service
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

def get_body_from_parts(payload):
    """Recursively extract body from payload."""
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                # Keep looking for plain text, but store this just in case
                data = part['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            elif 'parts' in part:
                 # Recursive check for nested parts
                 nested_body = get_body_from_parts(part)
                 if nested_body:
                     return nested_body
    elif 'body' in payload:
         # Single part message
         data = payload['body'].get('data')
         if data:
             return base64.urlsafe_b64decode(data).decode('utf-8')
             
    return body

def get_message_details(service, msg_id):
    """Get subject and snippet of a message."""
    try:
        msg = service.users().messages().get(userId='me', id=msg_id).execute()
        payload = msg['payload']
        headers = payload.get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        snippet = msg.get('snippet', '')
        
        # Get Body
        body = get_body_from_parts(payload)

        print(f"\n--- Message ID: {msg_id} ---")
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Snippet: {snippet}")
        print(f"Body:\n{body}")
        
    except Exception as e:
        print(f"Error fetching message {msg_id}: {e}")

def list_messages(service, query=""):
    """List messages matching the query."""
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No messages found.")
        else:
            print(f"Found {len(messages)} messages:")
            for msg in messages:
                get_message_details(service, msg['id'])
                
    except Exception as e:
        print(f"An error occurred: {e}")

def create_message(sender, to, subject, message_text):
    """Create a message for an email."""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def create_draft(service, user_id, message_body):
    """Create and insert a draft email. message_body is a dict from create_message."""
    try:
        draft = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=draft).execute()
        print(f"Draft id: {draft['id']}")
        return draft
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gmail Agent")
    parser.add_argument("--search", help="Search query (e.g., 'from:andy')", default="")
    parser.add_argument("--id", help="Get specific message by ID")
    parser.add_argument("--draft", action="store_true", help="Create a draft")
    parser.add_argument("--to", help="Recipient email")
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--body-file", help="Path to file containing body text")
    args = parser.parse_args()
    
    print(f"Connecting to Gmail as {IMPERSONATED_USER}...")
    service = get_gmail_service()
    if service:
        print("Connected!")
        
        if args.draft:
            if not (args.to and args.subject and args.body_file):
                print("Error: --to, --subject, and --body-file are required for drafts.")
            else:
                with open(args.body_file, 'r') as f:
                    body_text = f.read()
                
                message = create_message(IMPERSONATED_USER, args.to, args.subject, body_text)
                create_draft(service, 'me', message)
                print("Draft created successfully.")
                
        elif args.id:
            get_message_details(service, args.id)
        elif args.search:
            print(f"Searching for: '{args.search}'")
            list_messages(service, args.search)
        else:
            print("Please provide --search, --id, or --draft")
