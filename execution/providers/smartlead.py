import requests
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .base import EmailProvider

class SmartleadProvider(EmailProvider):
    BASE_URL = "https://server.smartlead.ai/api/v1"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.tag_cache = {}  # Cache: name.lower() -> id
        
        # Configure Robust Session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,  # Max retries
            backoff_factor=1,  # Wait 1s, 2s, 4s...
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_accounts(self) -> List[Dict]:
        resp = self.session.get(f"{self.BASE_URL}/email-accounts", params={'api_key': self.api_key}, timeout=45)
        resp.raise_for_status()
        # Normalize Data
        accounts = []
        for raw in resp.json():
            email = raw.get('email') or raw.get('from_email')
            # Extract Reputation
            rep = 0
            warmup = raw.get('warmup_details', {})
            if isinstance(warmup, dict):
                r_str = str(warmup.get('warmup_reputation', '0')).replace('%', '')
                rep = int(r_str) if r_str.isdigit() else 0
            
            # Extract Campaign Stats (Robust parsing)
            # Smartlead API structure varies; sometimes it's in stats, sometimes root
            # Checking 'stats' dict first
            stats = raw.get('stats', {})
            active_campaigns = 0
            if isinstance(stats, dict):
                 active_campaigns = stats.get('active_campaigns_count', 0)
            
            # Fallback to root or 0
            if not active_campaigns:
                 active_campaigns = raw.get('active_campaigns_count', 0)
            
            # Extract tags for diff-based syncing
            current_tags = []
            raw_tags = raw.get('tags', [])
            if isinstance(raw_tags, list):
                for t in raw_tags:
                    if isinstance(t, dict):
                        current_tags.append(str(t.get('name', '')).lower())
                    elif isinstance(t, str):
                        current_tags.append(t.lower())
                    # Ignore other types safely
            
            accounts.append({
                "id": str(raw.get('id')),
                "email": email,
                "reputation": rep,
                "active_campaigns": int(active_campaigns),
                "tags": current_tags, # List of lowercase tag names
                "raw": raw
            })
        return accounts

    def get_tag_id(self, tag_name: str) -> Optional[int]:
        """Find Tag ID by Name (Case-Insensitive) - With Caching"""
        tag_key = tag_name.lower()
        
        # 1. Check Cache
        if tag_key in self.tag_cache:
            return self.tag_cache[tag_key]
            
        try:
            resp = self.session.get(f"{self.BASE_URL}/tags", params={'api_key': self.api_key})
            if resp.ok:
                tags = resp.json()
                for t in tags:
                     # Some tags might not have 'name' or 'id' if malformed
                     if 'name' in t and 'id' in t:
                        self.tag_cache[t['name'].lower()] = t['id']
                
                # Check cache again
                if tag_key in self.tag_cache:
                    return self.tag_cache[tag_key]
            # No print here to avoid noise on successful retry-able failures, 
            # session handles it or raise_for_status would if we used it.
        except Exception as e:
             print(f"ERROR: get_tag_id failed: {e}")
        
        return None

    def create_tag(self, tag_name: str) -> Optional[int]:
        """Create a new tag"""
        try:
            url = f"{self.BASE_URL}/tags"
            # Random bright color
            import random
            color = random.choice(["#FF0000", "#00FF00", "#0000FF", "#FFA500"])
            resp = self.session.post(url, params={'api_key': self.api_key}, json={"name": tag_name, "color": color})
            if resp.ok and 'id' in resp.json():
                new_id = resp.json()['id']
                print(f"INFO: Created new tag '{tag_name}'")
                # Update Cache
                self.tag_cache[tag_name.lower()] = new_id
                return new_id
        except Exception as e:
            print(f"ERROR: create_tag failed: {e}")
        return None

    def add_tag(self, account_id: str, tag_id: int):
        """Add Tag to Account"""
        if not tag_id: return
        try:
            url = f"{self.BASE_URL}/email-accounts/{account_id}/tags"
            resp = self.session.post(url, params={'api_key': self.api_key}, json={"tag_id": tag_id})
        except Exception as e:
            print(f"ERROR: add_tag failed: {e}")

    def remove_tag(self, account_id: str, tag_id: int):
        """Remove Tag from Account"""
        if not tag_id: return
        try:
            url = f"{self.BASE_URL}/email-accounts/{account_id}/tags/{tag_id}"
            self.session.delete(url, params={'api_key': self.api_key})
        except: pass

    def tag_account(self, account_id: str, tag_text: str):
        # Wraps the lookup, create, and add logic
        tid = self.get_tag_id(tag_text)
        if not tid:
            tid = self.create_tag(tag_text)
            
        if tid: 
            self.add_tag(account_id, tid)
        else:
            print(f"ERROR: Could not resolve or create tag '{tag_text}'") 

    def get_campaigns_for_account(self, account_id: str) -> List[str]:
        # Smartlead: GET /email-accounts/{id}/campaigns
        url = f"{self.BASE_URL}/email-accounts/{account_id}/campaigns"
        try:
            resp = requests.get(url, params={'api_key': self.api_key})
            if resp.ok: return [str(c['id']) for c in resp.json()]
        except: pass
        return []

    def add_account_to_campaign(self, campaign_id: str, account_id: str):
        # POST /campaigns/{id}/email-accounts
        # body: { email_account_ids: [id] }
        url = f"{self.BASE_URL}/campaigns/{campaign_id}/email-accounts"
        requests.post(url, params={'api_key': self.api_key}, json={"email_account_ids": [int(account_id)]})

    def remove_account_from_campaign(self, campaign_id: str, account_id: str):
        # DELETE /campaigns/{id}/email-accounts/{acc_id}
        url = f"{self.BASE_URL}/campaigns/{campaign_id}/email-accounts/{account_id}"
        requests.delete(url, params={'api_key': self.api_key})
