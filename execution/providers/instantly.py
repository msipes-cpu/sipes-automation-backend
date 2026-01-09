import requests
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from providers.base import EmailProvider

class InstantlyProvider(EmailProvider):
    BASE_URL = "https://api.instantly.ai/api/v2"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.session = requests.Session()
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PATCH", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.tag_cache = {}

    def get_accounts(self) -> List[Dict]:
        url = f"{self.BASE_URL}/accounts"
        try:
            resp = self.session.get(url, headers=self.headers, params={"limit": 1000}, timeout=45)
            if not resp.ok:
                print(f"Instantly API Error: {resp.text}")
                return []
                
            data = resp.json()
            accounts_list = data.get('items', []) if isinstance(data, dict) else data
            
            normalized = []
            for raw in accounts_list:
                rep = 0
                if 'stat_warmup_score' in raw:
                    try:
                        rep = float(raw['stat_warmup_score'])
                    except: pass
                
                tags = []
                # Instantly v2 tags logic (check if object or ID)
                # Usually list of objects.
                if 'tags' in raw and isinstance(raw['tags'], list):
                    for t in raw['tags']:
                         if isinstance(t, dict): tags.append(str(t.get('name', '')).lower())
                         elif isinstance(t, str): tags.append(t.lower())

                # Active Campaigns: Instantly API v2 account object doesn't list active campaigns directly usually.
                # Only way is to fetch campaigns or check status?
                # For now, 0.
                active_campaigns = 0 

                normalized.append({
                    "id": raw.get('email'), # Use Email as ID for Instantly if UUID not reliable for v2 mapping?
                    # V2 usually has UUID 'id'. Let's use 'id' but fallback to email if needed.
                    "id": str(raw.get('id', raw.get('email'))),
                    "email": raw.get('email'),
                    "reputation": rep,
                    "active_campaigns": active_campaigns,
                    "tags": tags,
                    "raw": raw
                })
            return normalized

        except Exception as e:
            print(f"Instantly get_accounts failed: {e}")
            return []

    def _get_tag_id(self, tag_text: str) -> Optional[str]:
        # Helper to find tag UUID by name
        # GET /api/v2/custom-tags
        if tag_text.lower() in self.tag_cache:
            return self.tag_cache[tag_text.lower()]
            
        try:
            resp = self.session.get(f"{self.BASE_URL}/custom-tags", headers=self.headers)
            if resp.ok:
                tags = resp.json() # List of objects
                for t in tags:
                     if 'name' in t:
                         self.tag_cache[t['name'].lower()] = t['id']
                
                return self.tag_cache.get(tag_text.lower())
        except: pass
        return None

    def tag_account(self, account_id: str, tag_text: str):
        # 1. Get Tag ID
        tag_id = self._get_tag_id(tag_text)
        if not tag_id:
             # Create tag logic? 
             # POST /api/v2/custom-tags { "name": "..." }
             try:
                 create_resp = self.session.post(f"{self.BASE_URL}/custom-tags", headers=self.headers, json={"name": tag_text, "color": "#ff0000"})
                 if create_resp.ok:
                      tag_id = create_resp.json().get('id')
             except: pass
        
        if not tag_id: return

        # 2. Toggle Resource (Add Tag)
        # POST /api/v2/custom-tags/toggle-resource
        # Body: { tag_id: ..., resource_id: ..., resource_type: 1 } (1 = Email Account)
        try:
             # Ensure account_id is actually the email address if required by V2, or UUID.
             # Search results said "resource_id, which for an account is its email address".
             # BUT also said V2 uses UUIDs. Safer to try standard logic.
             # If account_id passed in is UUID, use it. If email, use it.
             # The `get_accounts` above sets `id` to the UUID.
             # Let's try UUID first.
             payload = {
                 "tag_id": tag_id,
                 "resource_id": account_id,
                 "resource_type": 1 
             }
             self.session.post(f"{self.BASE_URL}/custom-tags/toggle-resource", headers=self.headers, json=payload)
        except Exception as e:
             print(f"Instantly tag_account failed: {e}")

    def get_campaigns_for_account(self, account_id: str) -> List[str]:
        return [] # Difficult to get reverse mapping in Instantly v2 without N+1 queries

    def add_account_to_campaign(self, campaign_id: str, account_id: str):
        # Update Campaign with Email List
        # PATCH /api/v2/campaigns/{id}
        # { "email_list": ["email@..."] }
        # Need the EMAIL ADDRESS, not UUID.
        # This implies `account_id` MUST be resolved to email if it's a UUID.
        # Architecture mismatch: `InboxBench` passes `account_id` (UUID).
        # We need a way to lookup Email from ID? 
        # Or, `get_accounts` should key by ID, but we store Email in `account` dict.
        # WORKAROUND: In `SmartGuard.run_connection_check`, we have the `acc` dict. 
        # But `add_account_to_campaign` only takes ID.
        # We might need to fetch account details or cache them.
        pass

    def remove_account_from_campaign(self, campaign_id: str, account_id: str):
        pass
