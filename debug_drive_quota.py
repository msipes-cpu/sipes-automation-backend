import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Setup Google Drive Auth
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    else:
        print(f"File not found: {SERVICE_ACCOUNT_FILE}")
        return None

def check_quota(service):
    try:
        about = service.about().get(fields="storageQuota,user").execute()
        quota = about.get('storageQuota', {})
        user = about.get('user', {})
        print("\n--- Service Account Info ---")
        print(f"Email: {user.get('emailAddress')}")
        print(f"Display Name: {user.get('displayName')}")
        
        print("\n--- Storage Quota ---")
        limit = int(quota.get('limit', 0))
        usage = int(quota.get('usage', 0))
        usage_in_drive = int(quota.get('usageInDrive', 0))
        usage_in_trash = int(quota.get('usageInDriveTrash', 0))
        
        print(f"Limit: {limit / (1024**3):.2f} GB")
        print(f"Total Usage: {usage / (1024**3):.2f} GB")
        print(f"Usage In Drive: {usage_in_drive / (1024**3):.2f} GB")
        print(f"Usage In Trash: {usage_in_trash / (1024**3):.2f} GB")
        
        if limit > 0:
            print(f"Percent Used: {(usage/limit)*100:.2f}%")
            
    except Exception as e:
        print(f"Error checking quota: {e}")

def list_folders(service):
    print("\n--- Accessible Folders ---")
    try:
        # List folders (files with mimeType folder)
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false",
            pageSize=20,
            fields="nextPageToken, files(id, name, owners, capabilities)"
        ).execute()
        items = results.get('files', [])

        if not items:
            print("No folders found.")
        else:
            print(f"Found {len(items)} folders:")
            for item in items:
                owners = item.get('owners', [])
                owner_email = owners[0]['emailAddress'] if owners else "Unknown"
                print(f"Name: {item['name']} | ID: {item['id']} | Owner: {owner_email}")
                # print(f"  Can Add Children: {item.get('capabilities', {}).get('canAddChildren')}")

    except Exception as e:
        print(f"Error listing folders: {e}")
        
def list_root_files(service):
    print("\n--- Files in Root (Usage Hog check) ---")
    try:
        # List large files in root
        results = service.files().list(
            q="'root' in parents and trashed=false",
            pageSize=20,
            fields="files(id, name, size, mimeType)",
            orderBy="folder,quotaBytesUsed desc"
        ).execute()
        items = results.get('files', [])
        
        for item in items:
            size_mb = int(item.get('size', 0)) / (1024**2)
            print(f"File: {item['name']} | Size: {size_mb:.2f} MB")
            
    except Exception as e:
        print(f"Error listing files: {e}")

if __name__ == "__main__":
    service = get_drive_service()
    if service:
        check_quota(service)
        list_folders(service)
        list_root_files(service)
