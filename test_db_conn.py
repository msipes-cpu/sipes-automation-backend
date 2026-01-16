import socket
import os

def test_connection():
    host = "shortline.proxy.rlwy.net"
    port = 27546
    
    print(f"Testing connection to {host}:{port}...")
    try:
        s = socket.create_connection((host, port), timeout=5)
        print("SUCCESS: Connection established.")
        s.close()
        return True
    except Exception as e:
        print(f"FAILURE: Could not connect. Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
