import json
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

SERVICE_ACCOUNT_FILE = "credentials.json"

def debug_key():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("File not found")
        return

    with open(SERVICE_ACCOUNT_FILE, 'r') as f:
        info = json.load(f)

    if 'private_key' not in info:
        print("No private_key in json")
        return

    raw_key = info['private_key']
    # Try the replace logic
    pem_data = raw_key.replace('\\n', '\n').encode('utf-8')

    print(f"PEM Data start: {pem_data[:40]}")
    try:
        private_key = serialization.load_pem_private_key(
            pem_data,
            password=None,
            backend=default_backend()
        )
        print("SUCCESS: Key loaded successfully with cryptography!")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    debug_key()
