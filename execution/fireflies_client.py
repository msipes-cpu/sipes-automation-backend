import os
import requests
import json
import argparse
from datetime import datetime

# Load env vars
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("FIREFLIES_API_KEY")
API_URL = "https://api.fireflies.ai/graphql"

def fetch_transcripts(limit=1, title_filter=None):
    if not API_KEY:
        print("Error: FIREFLIES_API_KEY not found in .env")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # GraphQL Query to get transcripts
    query = """
    query Transcripts($limit: Int) {
        transcripts(limit: $limit) {
            id
            title
            date
            sentences {
                index
                text
                speaker_name
            }
        }
    }
    """
    
    variables = {"limit": limit}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"query": query, "variables": variables})
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL Error: {data['errors']}")
            return None
            
        return data["data"]["transcripts"]
        
    except Exception as e:
        print(f"API Request Failed: {e}")
        return None

def fetch_transcript_by_id(transcript_id):
    if not API_KEY:
        print("Error: FIREFLIES_API_KEY not found in .env")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    query = """
    query Transcript($id: String!) {
        transcript(id: $id) {
            id
            title
            date
            sentences {
                index
                text
                speaker_name
            }
        }
    }
    """
    
    variables = {"id": transcript_id}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"query": query, "variables": variables})
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL Error: {data['errors']}")
            return None
            
        return data["data"]["transcript"]
        
    except Exception as e:
        print(f"API Request Failed: {e}")
        return None

def format_transcript_text(transcript):
    if not transcript:
        return ""
    
    output = f"Title: {transcript.get('title', 'Unknown')}\n"
    output += f"Date: {datetime.fromtimestamp(transcript.get('date', 0)/1000).strftime('%Y-%m-%d %H:%M:%S')}\n"
    output += f"ID: {transcript.get('id')}\n"
    output += "-" * 40 + "\n\n"
    
    sentences = transcript.get("sentences", [])
    if not sentences: # Handle case where sentences might be null or empty
        return output + "[No transcript text available]"

    for sent in sentences:
        speaker = sent.get("speaker_name") or "Unknown"
        text = sent.get("text", "")
        output += f"**{speaker}**: {text}\n"
        
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Fireflies.ai Transcripts")
    parser.add_argument("--id", help="Fetch a specific transcript by ID")
    parser.add_argument("--limit", type=int, default=1, help="Number of recent transcripts to fetch")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    
    args = parser.parse_args()
    
    result_text = ""
    
    if args.id:
        print(f"Fetching transcript {args.id}...")
        transcript = fetch_transcript_by_id(args.id)
        if transcript:
            result_text = format_transcript_text(transcript)
        else:
            result_text = "Transcript not found."
    else:
        print(f"Fetching last {args.limit} transcripts...")
        transcripts = fetch_transcripts(limit=args.limit)
        if transcripts:
            for t in transcripts:
                result_text += format_transcript_text(t) + "\n\n" + "="*50 + "\n\n"
        else:
            result_text = "No transcripts found."

    if args.output:
        # ensure dir exists
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result_text)
        print(f"Saved to {args.output}")
    else:
        print(result_text)
