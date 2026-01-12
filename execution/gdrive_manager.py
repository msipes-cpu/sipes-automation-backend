import os
import argparse
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

# Setup Google Drive Auth
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    """Initialize and return Google Drive service."""
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        impersonate_email = os.getenv("GOOGLE_IMPERSONATE_EMAIL")
        if impersonate_email:
            print(f"Impersonating: {impersonate_email}")
            creds = creds.with_subject(impersonate_email)
            
        service = build('drive', 'v3', credentials=creds)
        return service
    else:
        raise ValueError(f"Service account file not found at {SERVICE_ACCOUNT_FILE}")

def find_or_create_folder(service, folder_name, parent_id=None):
    """
    Find a folder by name or create it if it doesn't exist.
    Returns the folder ID.
    """
    # Search for existing folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, webViewLink)'
    ).execute()
    
    items = results.get('files', [])
    
    if items:
        print(f"Found existing folder: {items[0]['name']}")
        return items[0]['id'], items[0].get('webViewLink')
    
    # Create new folder
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_id:
        file_metadata['parents'] = [parent_id]
    
    folder = service.files().create(
        body=file_metadata,
        fields='id, webViewLink'
    ).execute()
    
    print(f"Created new folder: {folder_name}")
    return folder['id'], folder.get('webViewLink')

def upload_file(service, file_path, folder_id, file_name=None):
    """
    Upload a file to Google Drive folder.
    Returns the file ID and web view link.
    """
    if not file_name:
        file_name = os.path.basename(file_path)
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    # Determine MIME type based on extension
    if file_path.endswith('.csv'):
        mime_type = 'text/csv'
    elif file_path.endswith('.json'):
        mime_type = 'application/json'
    else:
        mime_type = 'application/octet-stream'
    
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    print(f"Uploaded {file_name} to Google Drive")
    return file['id'], file.get('webViewLink')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Google Drive folders and uploads")
    parser.add_argument("--folder_name", help="Name of the folder to create/find", default="Leads from Apollo API")
    parser.add_argument("--upload_file", help="Path to file to upload")
    parser.add_argument("--file_name", help="Optional custom name for uploaded file")
    
    args = parser.parse_args()
    
    try:
        service = get_drive_service()
        
        # Use parent folder ID from env if available
        parent_folder_id = os.getenv("GOOGLE_DRIVE_PARENT_ID")
        
        # Find or create the folder
        folder_id, folder_link = find_or_create_folder(service, args.folder_name, parent_id=parent_folder_id)
        print(f"Folder ID: {folder_id}")
        print(f"Folder Link: {folder_link}")
        
        # Upload file if specified
        if args.upload_file:
            if os.path.exists(args.upload_file):
                file_id, file_link = upload_file(service, args.upload_file, folder_id, args.file_name)
                print(f"File ID: {file_id}")
                print(f"File Link: {file_link}")
            else:
                print(f"Error: File not found at {args.upload_file}")
        
    except Exception as e:
        print(f"Error: {e}")
