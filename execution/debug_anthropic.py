import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("ANTHROPIC_API_KEY")
print(f"Key loaded: {key[:15]}...{key[-5:] if key else 'None'}")

if not key:
    print("No key found!")
    exit(1)

client = anthropic.Anthropic(api_key=key)

try:
    print("Testing claude-3-haiku-20240307...")
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("Success!")
    print(message.content[0].text)
except Exception as e:
    print(f"Error: {e}")
