
import os
import requests
import json
import logging
from dotenv import load_dotenv

# Setup Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class UniversalCampaignManager:
    def __init__(self, campaign_ids, supabase_url, supabase_key, smartlead_api_key):
        self.campaign_ids = [str(cid).strip() for cid in campaign_ids.split(',') if cid.strip()]
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.smartlead_api_key = smartlead_api_key
        
        # Headers
        self.sl_headers = {} # API Key passed as param usually, but let's check docs. V1 uses ?api_key=...
        self.sb_headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }

    def fetch_accounts_from_db(self):
        """Fetches all accounts and their statuses from Supabase."""
        try:
            # Fetch all to know who to remove too
            url = f"{self.supabase_url}/rest/v1/email_accounts?select=id,email,status,daily_limit"
            resp = requests.get(url, headers=self.sb_headers)
            if resp.status_code != 200:
                logging.error(f"Failed to fetch from DB: {resp.text}")
                return [], []
            
            data = resp.json()
            sending = [acc for acc in data if acc['status'] == 'SENDING']
            paused = [acc for acc in data if acc['status'] != 'SENDING'] # Everyone else
            
            logging.info(f"DB State: {len(sending)} Sending, {len(paused)} Paused/Other")
            return sending, paused
        except Exception as e:
            logging.error(f"DB Fetch Error: {e}")
            return [], []

    def get_campaign_accounts(self, campaign_id):
        """Fetches current accounts in a campaign."""
        url = f"https://server.smartlead.ai/api/v1/campaigns/{campaign_id}/email-accounts?api_key={self.smartlead_api_key}&limit=1000"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                return resp.json() # List of dicts {id, email...}
            return []
        except:
            return []

    def update_campaign(self, campaign_id, db_sending, db_paused):
        """Syncs campaign membership with DB state. Returns (added_count, removed_count)."""
        logging.info(f"--- Processing Campaign {campaign_id} ---")
        
        # 1. Get Current State
        current_accounts = self.get_campaign_accounts(campaign_id)
        current_ids = set(str(acc['id']) for acc in current_accounts)
        
        # 2. Determine Actions
        target_sending_ids = set(str(acc['id']) for acc in db_sending)
        
        # To Add: In DB Sending Set but NOT in Campaign
        to_add = [int(uid) for uid in target_sending_ids if uid not in current_ids]
        
        # To Remove: In Campaign but NOT in DB Sending Set (i.e. is Paused/Sick/Warming)
        to_remove = [int(uid) for uid in current_ids if uid not in target_sending_ids]

        added_count = 0
        removed_count = 0

        # 3. Execute Additions
        if to_add:
            logging.info(f"Adding {len(to_add)} accounts to Campaign {campaign_id}...")
            url = f"https://server.smartlead.ai/api/v1/campaigns/{campaign_id}/email-accounts?api_key={self.smartlead_api_key}"
            try:
                # API expects {"email_account_ids": [...]}
                resp = requests.post(url, json={"email_account_ids": to_add})
                if resp.status_code == 200:
                    logging.info(f"✅ Successfully added {len(to_add)} accounts.")
                    added_count = len(to_add)
                else:
                    logging.error(f"❌ Failed to add accounts: {resp.text}")
            except Exception as e:
                logging.error(f"❌ Add Exception: {e}")
        else:
            logging.info("No accounts to add.")

        # 4. Execute Removals
        if to_remove:
            logging.info(f"Removing {len(to_remove)} accounts from Campaign {campaign_id}...")
            for acc_id in to_remove:
                url = f"https://server.smartlead.ai/api/v1/campaigns/{campaign_id}/email-accounts/{acc_id}?api_key={self.smartlead_api_key}"
                try:
                    resp = requests.delete(url)
                    if resp.status_code == 200:
                        logging.info(f"✅ Removed {acc_id}")
                        removed_count += 1
                    else:
                        logging.error(f"❌ Failed to remove {acc_id}: {resp.text}")
                except Exception as e:
                    logging.error(f"❌ Remove Exception: {e}")
        else:
            logging.info("No accounts to remove.")
            
        return added_count, removed_count

    def run(self):
        sending, paused = self.fetch_accounts_from_db()
        stats = {'added': 0, 'removed': 0, 'volume': 0}
        
        # Calculate Volume (Sum of daily limits of sending accounts)
        total_volume = sum([int(acc.get('daily_limit', 0)) for acc in sending])
        stats['volume'] = total_volume
        
        if not sending and not paused:
            logging.warning("No data found in DB. Aborting to prevent mass removal.")
            return stats

        for cid in self.campaign_ids:
            a, r = self.update_campaign(cid, sending, paused)
            stats['added'] += a
            stats['removed'] += r
            
        return stats

if __name__ == "__main__":
    # Env Check
    start_ids = os.getenv("TARGET_CAMPAIGN_IDS")
    sb_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    sb_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    sl_key = os.getenv("SMARTLEAD_API_KEY") 
    
    # Or SA_SM1_API_KEY override
    alt_key = os.getenv("SA_SM1_API_KEY")
    if alt_key: sl_key = alt_key

    if not start_ids or not sb_url or not sb_key or not sl_key:
        logging.error("Missing Environment Variables. Need TARGET_CAMPAIGN_IDS, SUPABASE_*, SMARTLEAD_API_KEY.")
        exit(1)

    manager = UniversalCampaignManager(start_ids, sb_url, sb_key, sl_key)
    manager.run()
