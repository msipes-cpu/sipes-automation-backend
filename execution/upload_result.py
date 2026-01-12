import os
import sys
from gdrive_manager import get_drive_service, find_or_create_folder, upload_file
from dotenv import load_dotenv

load_dotenv()

FILENAME = "apollo_blitz_TURBO_20260111_2211.csv"
FILEPATH = os.path.join(os.getcwd(), FILENAME)

def main():
    print(f"Uploading {FILENAME}...")
    try:
        service = get_drive_service()
        folder_id, folder_link = find_or_create_folder(service, "Leads from Apollo API")
        file_id, file_link = upload_file(service, FILEPATH, folder_id)
        print(f"UPLOAD_LINK: {file_link}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
