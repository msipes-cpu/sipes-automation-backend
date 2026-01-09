import sys
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_drive(creds_path):
    print(f"Testing Drive API with {creds_path}")
    try:
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        service = build('drive', 'v3', credentials=creds)
        
        # Try listing files
        results = service.files().list(pageSize=1).execute()
        files = results.get('files', [])
        print("Drive API Success! Files found:", len(files))
        return True
    except Exception as e:
        print(f"Drive API Failed: {e}")
        return False

if __name__ == "__main__":
    test_drive("../credentials.json")
