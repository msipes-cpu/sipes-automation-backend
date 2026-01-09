import requests
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from providers.base import EmailProvider

class PlusvibeProvider(EmailProvider):
    BASE_URL = "https://api.plusvibe.ai/api/v1"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.session = requests.Session()
        # Header best guess based on docs "API key included in request headers"
        self.headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        
        # Resolve Workspace ID
        self.workspace_id = self._get_first_workspace()

    def _get_first_workspace(self) -> Optional[str]:
        try:
            resp = self.session.get(f"{self.BASE_URL}/workspaces", headers=self.headers)
            if resp.ok:
                data = resp.json()
                # data might be list or { data: [] }
                if isinstance(data, list) and len(data) > 0:
                    return data[0]['id']
                if isinstance(data, dict) and 'data' in data and len(data['data']) > 0:
                     return data['data'][0]['id']
        except Exception as e:
            print(f"PlusVibe Workspace Init Failed: {e}")
        return None

    def get_accounts(self) -> List[Dict]:
        if not self.workspace_id:
            print("PlusVibe Error: No Workspace ID resolved")
            return []

        # 1. Get All Accounts
        url = f"{self.BASE_URL}/workspaces/{self.workspace_id}/email-accounts"
        accounts_map = {}
        try:
            resp = self.session.get(url, headers=self.headers)
            if not resp.ok:
                print(f"PlusVibe API Error: {resp.text}")
                return []
            
            data = resp.json()
            raw_accounts = data if isinstance(data, list) else data.get('data', [])
            for raw in raw_accounts:
                accounts_map[str(raw.get('id'))] = raw
        except Exception as e:
            print(f"PlusVibe get_accounts failed: {e}")
            return []

        # 2. Get Workspace Warmup Stats (for Reputation)
        # /workspaces/{id}/warmup-stats
        stats_map = {}
        try:
            # Stats endpoint often takes date range, defaulting to recent if omitted?
            # Docs: Get Warmup Stats (Workspace-Level)
            # Assuming it returns a list of stats per account or aggregate?
            # Let's try fetching individual status if bulk fails or use data from account list if present.
            # Many APIs include 'warmup_status' in the account object.
            pass 
        except: pass

        normalized = []
        for aid, raw in accounts_map.items():
            # Extract Reputation
            # Often inside "warmup_status" -> "reputation" or "health_score"
            rep = 0
            if 'warmup_status' in raw and isinstance(raw['warmup_status'], dict):
                 # Pipl/PlusVibe often explicitly has 'reputation_score' or 'spam_score'
                 w = raw['warmup_status']
                 # Invert spam score if needed? Or use health score.
                 # Let's assume 'reputation' key exists or 'score'.
                 rep = w.get('reputation', 99) 
            
            normalized.append({
                "id": str(raw.get('id')),
                "email": raw.get('email'),
                "reputation": float(rep),
                "active_campaigns": 0, 
                "tags": [t.get('name', '').lower() for t in raw.get('tags', [])],
                "raw": raw
            })
        return normalized

    def tag_account(self, account_id: str, tag_text: str):
        if not self.workspace_id: return
        # POST /workspaces/{id}/email-accounts/bulk-tag-ops
        # { "email_account_ids": [id], "tags": [ "tagName" ], "operation": "add" }
        url = f"{self.BASE_URL}/workspaces/{self.workspace_id}/email-accounts/bulk-tag-ops"
        payload = {
            "email_account_ids": [account_id],
            "tags": [tag_text],
            "operation": "add"
        }
        try:
            self.session.post(url, headers=self.headers, json=payload)
        except Exception as e:
            print(f"PlusVibe tag_account failed: {e}")

    def get_campaigns_for_account(self, account_id: str) -> List[str]:
        return []

    def add_account_to_campaign(self, campaign_id: str, account_id: str):
        pass

    def remove_account_from_campaign(self, campaign_id: str, account_id: str):
        pass
