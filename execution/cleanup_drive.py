
import os
import argparse
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise ValueError(f"Service account file not found at {SERVICE_ACCOUNT_FILE}")
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def list_files(service, limit=50):
    """List files sorted by size (descending)."""
    print("Listing files (sorted by size)...")
    try:
        # Note: 'quotaBytesUsed' is the field for size, but sorting by it in the query 
        # is only supported for 'recents' or requires specific query parameters. 
        # Actually 'orderBy' supports 'quotaBytesUsed desc'.
        results = service.files().list(
            q="trashed=false",
            pageSize=limit,
            fields="nextPageToken, files(id, name, mimeType, quotaBytesUsed)",
            orderBy="quotaBytesUsed desc"
        ).execute()
        
        items = results.get('files', [])

        if not items:
            print("No files found.")
        else:
            print(f"{'ID':<35} | {'Size (MB)':<10} | {'Name'}")
            print("-" * 80)
            for item in items:
                size_bytes = int(item.get('quotaBytesUsed', 0))
                size_mb = size_bytes / (1024 * 1024)
                print(f"{item['id']:<35} | {size_mb:>9.2f}  | {item['name']}")
                
    except Exception as e:
        print(f"Error listing files: {e}")

def delete_file(service, file_id):
    """Permanently delete a file."""
    try:
        service.files().delete(fileId=file_id).execute()
        print(f"Successfully deleted file: {file_id}")
    except Exception as e:
        print(f"Error deleting file {file_id}: {e}")

def empty_trash(service):
    """Empty the trash to free up space."""
    print("Emptying trash...")
    try:
        service.files().emptyTrash().execute()
        print("Trash emptied successfully.")
    except Exception as e:
        print(f"Error emptying trash: {e}")

def check_quota(service):
    """Check storage quota."""
    try:
        about = service.about().get(fields="storageQuota").execute()
        quota = about.get('storageQuota', {})
        
        limit = int(quota.get('limit', 0))
        usage = int(quota.get('usage', 0))
        usage_in_drive = int(quota.get('usageInDrive', 0))
        
        limit_gb = limit / (1024**3)
        usage_gb = usage / (1024**3)
        
        print(f"Storage Quota: {usage_gb:.2f} GB used / {limit_gb:.2f} GB limit")
        print(f"Drive Usage: {usage_in_drive / (1024**3):.2f} GB")
        
    except Exception as e:
        print(f"Error checking quota: {e}")

def list_shared_drives(service):
    """List available Shared Drives."""
    print("Listing Shared Drives...")
    try:
        results = service.drives().list(pageSize=10).execute()
        drives = results.get('drives', [])
        
        if not drives:
            print("No Shared Drives found.")
        else:
            print(f"{'ID':<35} | {'Name'}")
            print("-" * 50)
            for drive in drives:
                print(f"{drive['id']:<35} | {drive['name']}")
    except Exception as e:
        print(f"Error listing shared drives: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup Google Drive Storage")
    parser.add_argument("--list", action="store_true", help="List largest files")
    parser.add_argument("--delete", help="File ID to delete")
    parser.add_argument("--empty-trash", action="store_true", help="Empty the trash")
    parser.add_argument("--quota", action="store_true", help="Check current quota usage")
    
    args = parser.parse_args()
    
    try:
        service = get_drive_service()
        
        if args.quota:
            check_quota(service)
            list_shared_drives(service)
            
        if args.list:
            list_files(service)
            
        if args.delete:
            delete_file(service, args.delete)
            
        if args.empty_trash:
            empty_trash(service)
            
        if not (args.list or args.delete or args.empty_trash or args.quota):
            print("No action specified. Use --quota, --list, --delete <ID>, or --empty-trash")
            
    except Exception as e:
        print(f"Initialization Error: {e}")
