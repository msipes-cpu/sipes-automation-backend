
import sys
import os

# Add root to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import backend.main...")
    from backend.main import app
    print("SUCCESS: backend.main imported successfully.")
except Exception as e:
    print("FAILURE: Could not import backend.main")
    print(e)
    import traceback
    traceback.print_exc()
