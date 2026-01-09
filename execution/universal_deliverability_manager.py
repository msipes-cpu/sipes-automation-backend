#!/usr/bin/env python3
"""
Universal Deliverability Manager
--------------------------------
A platform-agnostic system for managing cold email reputation.
Separates "Doctor" (Logic) from "Translator" (API Provider).

Features:
-   Multi-platform (Smartlead, Instantly)
-   Pre-flight Check (Confirm before acting)
-   Configurable Thresholds
-   Reporting (Email & Slack)
-   Account Age Handling (< 14 days mandatory warmup)

Usage:
    python3 execution/universal_deliverability_manager.py --platform smartlead --api-key KEY
"""

import os
import sys
import json
import time
import requests
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
import concurrent.futures # For parallel execution
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# --- CONFIGURATION DEFAULTS ---
DEFAULT_SICK_THRESHOLD = 98
WARMUP_PERIOD_DAYS = 14
DEFAULT_WARMUP_SETTINGS = {
    'total_warmup_per_day': 35,
    'daily_rampup': 5,
    'reply_rate_percentage': 38,
    'warmup_enabled': True
}
TARGET_TAGS = ['Sick', 'Bench'] 

# --- 1. ABSTRACT PROVIDER ---

class DeliverabilityProvider(ABC):
    def __init__(self, api_key: str, dry_run: bool = False):
        self.api_key = api_key
        self.dry_run = dry_run
        self.tags_map = {} 

    @abstractmethod
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Returns list with 'id', 'email', 'reputation', 'created_at', 'tags'."""
        pass

    @abstractmethod
    def update_tags(self, account_id: Union[str, int], add_tags: List[str], remove_tags: List[str]) -> bool:
        pass

    @abstractmethod
    def enable_warmup(self, account_id: Union[str, int], settings: Dict[str, Any]) -> bool:
        pass

    def log(self, message: str, level: str = "INFO"):
        prefix = "[DRY RUN] " if self.dry_run else ""
        print(f"{prefix}[{level}] {message}")


# --- 2. SMARTLEAD PROVIDER ---

class SmartleadProvider(DeliverabilityProvider):
    BASE_URL = "https://server.smartlead.ai/api/v1"

    def __init__(self, api_key: str, dry_run: bool = False):
        super().__init__(api_key, dry_run)
        self.session = requests.Session()

    def _req(self, method: str, endpoint: str, json_data: dict = None, params: dict = None):
        url = f"{self.BASE_URL}/{endpoint}"
        if not params: params = {}
        params['api_key'] = self.api_key
        
        if self.dry_run and method != 'GET':
            self.log(f"Would call {method} {url}", "DRY")
            return None
            
        # Robust Retry with Backoff
        for attempt in range(5):
            try:
                resp = self.session.request(method, url, json=json_data, params=params, timeout=30)
                if resp.status_code == 429:
                    wait_time = (attempt + 1) * 2 # 2, 4, 6, 8, 10s
                    self.log(f"Rate limited on {endpoint}. Retrying in {wait_time}s...", "WARN")
                    time.sleep(wait_time)
                    continue
                return resp
            except Exception as e:
                self.log(f"Request failed (Attempt {attempt+1}/5): {e}", "ERROR")
                time.sleep(1)
        return None

    # _sync_tags removed

    def get_all_accounts(self) -> List[Dict[str, Any]]:
        self.log("Fetching Smartlead accounts...")

        all_accounts = []
        offset = 0
        limit = 50
        
        while True:
            resp = self._req('GET', 'email-accounts', params={'limit': limit, 'offset': offset})
            if not resp or resp.status_code != 200: 
                self.log(f"Failed to fetch batch at offset {offset}", "ERROR")
                break
            
            batch = resp.json()
            if not batch: 
                break
                
            all_accounts.extend(batch)
            if len(batch) < limit: 
                break
            
            offset += limit
            self.log(f"Fetched {len(all_accounts)} accounts so far...")

        standardized = []
        if all_accounts:
            # ACTIVE SCAN: Iterate accounts, fetching details until tags are found
            tags_found = 0
            self.log("Active Scan: Searching for Manual Seed Account to learn Tag IDs...")
            
            # Use a generator or just loop. We need to stop as soon as we have the IDs.
            # Limit to 100 to avoid extreme delays vs timeouts
            scan_limit = 100
            for i, acc in enumerate(all_accounts[:scan_limit]):
                 if tags_found >= 4:
                     self.log(f"Found all tags after scanning {i} accounts. Stopping scan.")
                     break
                 
                 # Optimization: Skip checking if account clearly has no tags? 
                 # No, list view doesn't tell us. Must fetch.
                 try:
                    r = self._req('GET', f"email-accounts/{acc['id']}", params={'fetch_tags': 'true'})
                    if r and r.status_code == 200:
                        data = r.json()
                        if data.get('tags'):
                            for tag in data['tags']:
                                t_name = tag['name'].lower()
                                if t_name not in self.tags_map:
                                    self.tags_map[t_name] = tag['id']
                                    self.log(f"Found Tag ID: {t_name} -> {tag['id']}")
                                    tags_found += 1
                 except Exception as e:
                     pass

            if tags_found < 4:
                self.log(f"WARNING: Only found {tags_found}/4 tags after scanning {scan_limit} accounts.", "WARN")
                self.log(f"Ensure 'Warming', 'Sick', 'Bench', 'Sending' are assigned to an account in the first {scan_limit}.", "WARN")

        for acc in all_accounts:
            rep = 0
            if 'warmup_details' in acc and isinstance(acc['warmup_details'], dict):
                r_str = str(acc['warmup_details'].get('warmup_reputation', '0')).replace('%', '')
                rep = int(r_str) if r_str.isdigit() else 0
            
            created_at = datetime.now()
            if 'created_at' in acc:
                try: created_at = datetime.fromisoformat(acc['created_at'].split('.')[0].replace('Z', ''))
                except: pass

            standardized.append({
                'id': acc['id'],
                'email': acc.get('email', acc.get('from_email')),
                'reputation': rep,
                'daily_limit': acc.get('message_per_day', 0), # Corrected Field Name
                'created_at': created_at,
                'tags': acc.get('tags', []) # Store raw tags list for name access
            })
        return standardized

    # _scan_for_tag_ids removed


    def update_tags(self, account_id, add_tags, remove_tags) -> bool:
        # Resolve names to IDs
        add_ids = [int(self.tags_map.get(t.lower())) for t in add_tags if t.lower() in self.tags_map]
        rem_ids = [int(self.tags_map.get(t.lower())) for t in remove_tags if t.lower() in self.tags_map]
        
        # Ensure account_id is int (Spec requires integer)
        try:
            acc_id_int = int(account_id)
        except:
            self.log(f"Invalid account ID: {account_id}", "ERROR")
            return False
            
        # API requires lists of integers
        if add_ids: 
            self._req('POST', 'email-accounts/tag-mapping', json_data={'email_account_ids': [acc_id_int], 'tag_ids': add_ids})
        if rem_ids: 
            self._req('DELETE', 'email-accounts/tag-mapping', json_data={'email_account_ids': [acc_id_int], 'tag_ids': rem_ids})
        return True

    def enable_warmup(self, account_id, settings) -> bool:
        self.log(f"Enabling warmup for {account_id}")
        return self._req('POST', f"email-accounts/{account_id}/warmup", json_data=settings) is not None


# --- 3. INSTANTLY PROVIDER ---

class InstantlyProvider(DeliverabilityProvider):
    BASE_URL = "https://api.instantly.ai/api/v2"

    def _req(self, method: str, endpoint: str, json_data: dict = None, params: dict = None):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        time.sleep(0.5) 
        if self.dry_run and method != 'GET': return None
        try:
            return requests.request(method, f"{self.BASE_URL}/{endpoint}", headers=headers, json=json_data, params=params, timeout=30)
        except Exception as e:
            self.log(f"Request failed: {e}", "ERROR")
            return None

    def get_all_accounts(self) -> List[Dict[str, Any]]:
        self.log("Fetching Instantly accounts...")
        
        all_items = []
        skip = 0
        limit = 100 # API Max seems < 1000. 100 is safe.
        
        while True:
            resp = self._req('GET', 'accounts', params={'limit': limit, 'skip': skip})
            if not resp or resp.status_code != 200: 
                self.log(f"Failed to fetch batch at skip {skip} (Status: {resp.status_code if resp else 'None'})", "ERROR")
                break
                
            items = resp.json().get('items', [])
            if not items: 
                break
                
            all_items.extend(items)
            
            if len(items) < limit:
                break
            
            skip += limit
            self.log(f"Fetched {len(all_items)} accounts so far...")
            
        self._scan_tags()
        standardized = []
        for acc in all_items:
            created_at = datetime.now()
            if 'timestamp_created' in acc:
                try: created_at = datetime.fromisoformat(acc['timestamp_created'].split('.')[0].replace('Z', ''))
                except: pass

            standardized.append({
                'id': acc['email'], 'email': acc.get('email'), 'reputation': 0, 
                'created_at': created_at, 'tags': [t.get('label', t.get('name', '')) for t in acc.get('tags', [])]
            })
        return standardized

    def _scan_tags(self):
        resp = self._req('GET', 'custom-tags')
        if resp and resp.status_code == 200:
            for t in resp.json().get('items', []): 
                # Instantly V2 uses 'label', Smartlead uses 'name'. Be robust.
                tag_name = t.get('label', t.get('name', ''))
                self.tags_map[tag_name.lower()] = t['id']

    def update_tags(self, account_id, add_tags, remove_tags) -> bool:
        add = [self.tags_map.get(t.lower()) for t in add_tags if t.lower() in self.tags_map]
        rem = [self.tags_map.get(t.lower()) for t in remove_tags if t.lower() in self.tags_map]
        if add: self._req('POST', 'custom-tags/toggle-resource', json_data={"tag_ids": add, "resource_type": 1, "resource_ids": [account_id], "assign": True})
        if rem: self._req('POST', 'custom-tags/toggle-resource', json_data={"tag_ids": rem, "resource_type": 1, "resource_ids": [account_id], "assign": False})
        return True

    def enable_warmup(self, account_id, settings) -> bool:
        return self._req('POST', 'accounts/warmup/enable', json_data={"emails": [account_id]}) is not None


# --- 4. LOGIC ENGINE ---

class Action:
    def __init__(self, account_id, email, action_type, reason, details=""):
        self.account_id = account_id
        self.email = email
        self.type = action_type # 'WARMUP_NEW', 'FIX_SICK', 'RESTORE_HEALTHY'
        self.reason = reason
        self.details = details

class UniversalDeliverabilityManager:
    def __init__(self, provider: DeliverabilityProvider, sick_threshold: int, healthy_tag: str = 'Running', instance_name: str = "Email Manager", dashboard_url: str = ""):
        self.provider = provider
        self.sick_threshold = sick_threshold
        self.healthy_tag = healthy_tag
        self.instance_name = instance_name
        self.dashboard_url = dashboard_url
        self.proposed_actions: List[Action] = []
        self.all_accounts = [] # Store accounts for later sync
        # UPDATED STATS: separate warming vs sick
        # UPDATED STATS: separate buckets
        self.stats = {'total': 0, 'sick_found': 0, 'warming_found': 0, 'bench_found': 0, 'sending_found': 0}

    def analyze(self):
        """Phase 1: Read-Only Analysis"""
        print("🚀 Starting Analysis...")
        self.all_accounts = self.provider.get_all_accounts()
        self.stats['total'] = len(self.all_accounts)
        
        # Buckets
        warming_candidates = []
        sick_candidates = []
        healthy_candidates = []

        # 1. Classify
        for acc in self.all_accounts:
            age_days = (datetime.now() - acc['created_at']).days
            rep = acc['reputation']
            
            if age_days < WARMUP_PERIOD_DAYS:
                warming_candidates.append(acc)
            elif rep < self.sick_threshold:  # Now 98%
                sick_candidates.append(acc)
            else:
                healthy_candidates.append(acc)

        # 2. Process Warming & Sick (Absolute Rules)
        for acc in warming_candidates:
            self._propose_tag_update(acc, 'Warming', ['Sick', 'Bench', 'Sending'])
            self.stats['warming_found'] += 1

        for acc in sick_candidates:
            self._propose_tag_update(acc, 'Sick', ['Warming', 'Bench', 'Sending'])
            self.stats['sick_found'] += 1

        # 3. Process Healthy (20/80 Bench Split) - Stable Balancing
        total_healthy = len(healthy_candidates)
        if total_healthy > 0:
            target_bench_count = int(total_healthy * 0.20)
            
            # Sort to minimize disruption: 
            # 1. Existing Bench (Keep them)
            # 2. Neutral (Recovering/New)
            # 3. Existing Sending (Move last)
            def sort_key(a):
                tags = [t.lower() for t in a.get('tags', [])]
                if 'bench' in tags: return 0
                if 'sending' in tags: return 2
                return 1
            
            healthy_sorted = sorted(healthy_candidates, key=sort_key)
            
            bench_group = healthy_sorted[:target_bench_count]
            sending_group = healthy_sorted[target_bench_count:]
            
            for acc in bench_group:
                self._propose_tag_update(acc, 'Bench', ['Warming', 'Sick', 'Sending'])
                self.stats['bench_found'] += 1
                
            for acc in sending_group:
                self._propose_tag_update(acc, 'Sending', ['Warming', 'Sick', 'Bench'], enable_warmup=False) 
                self.stats['sending_found'] += 1

    def _propose_tag_update(self, acc, target_tag, remove_tags, enable_warmup=True):
        current_tags = [t.lower() for t in acc.get('tags', [])]
        
        # Check if update needed
        needs_tag = target_tag.lower() not in current_tags
        has_forbidden = any(t.lower() in current_tags for t in remove_tags)
        
        if needs_tag or has_forbidden:
            reason = f"Classified as {target_tag}"
            if target_tag == 'Warming':
                reason = f"New Account ({(datetime.now() - acc['created_at']).days}d)"
            elif target_tag == 'Sick':
                reason = f"Low Reputation ({acc['reputation']}%)"
            elif target_tag == 'Bench':
                reason = "Healthy Reserve (Top 20%)"
            elif target_tag == 'Sending':
                reason = "Active Sender (Healthy)"

            action_type = f"SET_{target_tag.upper()}"
            self.proposed_actions.append(Action(acc['id'], acc['email'], action_type, reason))


    def print_plan(self):
        print("\n📋 PLAN SUMMARY")
        print("------------------------------------------------")
        print(f"Sick Threshold: {self.sick_threshold}%")
        print(f"Accounts Scanned: {self.stats['total']}")
        print("------------------------------------------------")
        
        if not self.proposed_actions:
            print("✅ No actions needed. All accounts compliant.")
            return

        print(f"⚠️  PROPOSED ACTIONS ({len(self.proposed_actions)}):")
        for act in self.proposed_actions:
            icon = "👶" if act.type == 'WARMUP_NEW' else "🚑" if act.type == 'FIX_SICK' else "🎉"
            print(f"  {icon} [{act.type}] {act.email} -> {act.reason}")
        print("------------------------------------------------")

    def sync_to_supabase(self):
        """Syncs all_accounts status to Supabase"""
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            print("Skipping Supabase Sync (Missing credentials)")
            return

        # Clean key just in case
        if key.startswith('"') and key.endswith('"'): key = key[1:-1]

        print(f"Syncing {len(self.all_accounts)} accounts to Supabase...")
        
        # Prepare Batch
        records = []
        for acc in self.all_accounts:
            # Re-read tags from memory (assumes they were updated in-place or simply read)
            # Since we didn't update the dict objects in memory during _execute_action, 
            # we rely on the initial fetch state + known actions.
            # Ideally, we should update self.all_accounts during execution, but for now
            # we sync the LATEST known state. 
            
            # Determine Status from Tags
            tags = [t['name'].lower() for t in acc.get('tags', [])]
            status = 'UNKNOWN'
            if 'sick' in tags: status = 'SICK'
            if 'warming' in tags: status = 'WARMING'
            if 'bench' in tags: status = 'BENCH'
            if 'sending' in tags: status = 'SENDING' 

            records.append({
                "id": acc['id'],
                "email": acc['email'],
                "status": status,
                "tags": tags,
                "warmup_score": int(acc.get('reputation', 0)),
                "daily_limit": int(acc.get('daily_limit', 0)),
                "last_updated_at": "now()"
            })

        # Upsert Batch (Supabase supports upsert)
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        
        # Batch size 100 to be safe
        batch_size = 100
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                r = requests.post(f"{url}/rest/v1/email_accounts", headers=headers, json=batch)
                if r.status_code not in [200, 201]:
                     print(f"Supabase Sync Failed: {r.status_code} - {r.text}")
            except Exception as e:
                print(f"Supabase Sync Error: {e}")

        print("✅ Supabase Sync Complete")

    def get_sending_volume(self):
        """Calculates total daily limit for all currently 'Sending' accounts."""
        total_limit = 0
        for acc in self.all_accounts:
            tags = [t.get('name', '').lower() for t in acc.get('tags', [])]
            if 'sending' in tags:
                total_limit += int(acc.get('daily_limit', 0))
        return total_limit

    def fetch_previous_volume(self, sb_url, sb_key):
        """Fetches total daily limit of 'Sending' accounts from Supabase (Before Sync)."""
        try:
            headers = {
                "apikey": sb_key,
                "Authorization": f"Bearer {sb_key}",
                "Content-Type": "application/json"
            }
            # Fetch statuses and limits
            url = f"{sb_url}/rest/v1/email_accounts?select=daily_limit,status"
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                total = sum([d.get('daily_limit', 0) for d in data if d.get('status') == 'SENDING'])
                return total
            return 0
        except:
            return 0

    def execute(self):
        """Phase 2: Execution (Parallelized)"""
        if not self.proposed_actions: return
        print(f"\n⚡ EXECUTING PLAN ({len(self.proposed_actions)} actions)...")
        print(f"   Using ThreadPool (Simulated Batching) for speed...")

        # Execute in parallel threads (simultaneous requests)
        # Reduced workers to 3 to avoid Smartlead Rate Limits (10 req/2s)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Map action -> future
            futures = {executor.submit(self._execute_action, act): act for act in self.proposed_actions}
            
            for future in concurrent.futures.as_completed(futures):
                act = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Error processing {act.email}: {e}")

        print(f"✅ Job Complete.")
        
        # 6. Sync State to DB
        self.sync_to_supabase()

    def _execute_action(self, act: Action):
        """Helper for single action execution"""
        
        # Tags to remove are implicit in logic, but let's re-derive or pass them?
        # Simpler: The Action Type is "SET_X". We know the set of 4 mutually exclusive tags.
        ALL_TAGS = ['Warming', 'Sick', 'Bench', 'Sending']
        target_tag = act.type.replace("SET_", "").capitalize()  # e.g. "Warming" from SET_WARMING
        
        # Determine removal list
        remove_tags = [t for t in ALL_TAGS if t != target_tag]
        
        # Execute Tag Swap
        self.provider.update_tags(act.account_id, [target_tag], remove_tags)
        
        # Throttle to prevent rate limits
        time.sleep(0.5)
        
        # Enable Warmup Specifics if needed
        if target_tag in ['Warming', 'Sick']:
             self.provider.enable_warmup(act.account_id, DEFAULT_WARMUP_SETTINGS)

        # UPDATE INTERNAL STATE FOR SUPABASE SYNC
        for acc in self.all_accounts:
            if str(acc['id']) == str(act.account_id):
                # Update tags list in memory
                # Remove mutually exclusive tags (tags are dicts)
                new_tags = [t for t in acc.get('tags', []) if t.get('name', '').lower() not in [x.lower() for x in ALL_TAGS]]
                # Add new tag (as dict)
                new_tags.append({'name': target_tag})
                acc['tags'] = new_tags
                break

        print(f"[INFO] {act.email} -> {target_tag}")

    def generate_html(self, web_link=None):
        """Generates the Clean HTML Report (User Preferred)."""
        # Stats
        total = self.stats['total']
        warming = self.stats['warming_found']
        sick = self.stats['sick_found']
        bench = self.stats['bench_found']
        sending = self.stats['sending_found']
        
        # Build Logs
        logs_html = ""
        for act in self.proposed_actions:
            # Icon Map
            icon = "⚪️"
            color = "#333"
            if 'WARMING' in act.type: icon, color = "👶", "#f0ad4e"
            elif 'SICK' in act.type: icon, color = "🚑", "#d9534f"
            elif 'BENCH' in act.type: icon, color = "🛋️", "#5bc0de"
            elif 'SENDING' in act.type: icon, color = "🚀", "#5cb85c"
            
            line = f"{icon} [{act.type}] {act.email} -> {act.reason}"
            logs_html += f"<div style='color: {color}; margin-bottom: 4px;'>{line}</div>"

        if not logs_html:
            logs_html = "<div>No actions needed. All accounts aligned.</div>"

        # HTML Template
        report_link_html = f"<p><a href='{web_link}'>View Full Web Report</a></p>" if web_link else ""
        
        dashboard_link_html = ""
        if self.dashboard_url:
            dashboard_link_html = f"<p style='margin-top: 5px;'><a href='{self.dashboard_url}'>Open {self.instance_name} Dashboard</a></p>"

        return f"""
        <html>
        <body style="font-family: Helvetica, Arial, sans-serif; color: #333;">
            <div style="border-bottom: 2px solid #333; padding_bottom: 10px; margin-bottom: 20px;">
                <h2 style="margin: 0;">Inbox Bench Report: {self.instance_name}</h2>
                {dashboard_link_html}
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; border: 1px solid #ddd;">
                <tr style="background-color: #f9f9f9; text-align: center;">
                    <th style="padding: 10px; border: 1px solid #ddd;">Total</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Warming (<14d)</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Sick (<98%)</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Bench (20%)</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Sending (80%)</th>
                </tr>
                <tr style="text-align: center; font-size: 18px; font-weight: bold;">
                    <td style="padding: 15px; border: 1px solid #ddd;">{total}</td>
                    <td style="padding: 15px; border: 1px solid #ddd; color: #f0ad4e;">{warming}</td>
                    <td style="padding: 15px; border: 1px solid #ddd; color: #d9534f;">{sick}</td>
                    <td style="padding: 15px; border: 1px solid #ddd; color: #5bc0de;">{bench}</td>
                    <td style="padding: 15px; border: 1px solid #ddd; color: #5cb85c;">{sending}</td>
                </tr>
            </table>

            <p><strong>Status:</strong> COMPLETED</p>
            <p><strong>Summary:</strong> Processed {total} accounts. Optimized {sending} senders.</p>
            
            {report_link_html}

            <h3 style="border-bottom: 1px solid #ccc; margin-top: 30px;">Logs:</h3>
            <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 12px; max-height: 400px; overflow-y: auto;">
                {logs_html}
            </div>
        </body>
        </html>
        """

    def send_report(self, email_to=None, slack_url=None, web_link=None, campaign_stats=None, volume_stats=None):
        """Sends a beautiful report (HTML Email) or concise Stats (Slack)."""
        if not self.proposed_actions and not email_to and not slack_url: return

        # --- GENERATE CONTENT ---
        html_body = self.generate_html(web_link)
        
        # Build Text Logs for Slack/Plaintext
        logs_text = ""
        for act in self.proposed_actions:
            icon = "👶" if act.type == 'WARMUP_NEW' else "🚑" if act.type == 'FIX_SICK' else "🎉"
            logs_text += f"{icon} [{act.type}] {act.email} -> {act.reason}\n"
        if not logs_text: logs_text = "No status changes."

        # Slack (Concise Overview)
        if slack_url:
            # Campaign Stats
            camp_text = "• Campaign: No changes"
            if campaign_stats:
                added = campaign_stats.get('added', 0)
                removed = campaign_stats.get('removed', 0)
                camp_text = f"• Campaign: +{added} Added | -{removed} Removed"

            # Volume Stats
            vol_text = "• Sending Volume: N/A"
            if volume_stats:
                curr = volume_stats.get('current', 0)
                prev = volume_stats.get('previous', 0)
                diff = curr - prev
                sign = "+" if diff >= 0 else ""
                vol_text = f"• Sending Volume: {curr} ({sign}{diff})"

            slack_msg = (
                f"*Inbox Bench Daily Update*\n"
                f"• Total Accounts: {self.stats['total']}\n"
                f"• Sick: {self.stats['sick_found']}\n"
                f"• Warming: {self.stats['warming_found']}\n"
                f"• Bench: {self.stats['bench_found']}\n"
                f"{camp_text}\n"
                f"{vol_text}\n"
            )
            
            try:
                requests.post(slack_url, json={'text': slack_msg})
                print("✅ Slack Report Sent.")
            except: print("❌ Failed to send Slack report.")

        # Email (HTML)
        if email_to:
            sender = os.getenv('SENDER_EMAIL')
            password = os.getenv('SENDER_PASSWORD')
            server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            port = int(os.getenv('SMTP_PORT', 587))
            
            if sender and password:
                try:
                    msg = MIMEMultipart('alternative')
                    msg['From'] = f"Inbox Bench <{sender}>"
                    msg['To'] = email_to
                    msg['Subject'] = f"Inbox Bench [{self.instance_name}]: {self.stats['sick_found']} Sick, {self.stats['warming_found']} Warming"
                    
                    # Attach parts
                    msg.attach(MIMEText(logs_text, 'plain')) # Fallback
                    msg.attach(MIMEText(html_body, 'html'))
                    
                    with smtplib.SMTP(server, port) as s:
                        s.starttls()
                        s.login(sender, password)
                        s.send_message(msg)
                    print("✅ Email Report Sent.")
                except Exception as e:
                    print(f"❌ Failed to send Email report: {e}")
            else:
                print("⚠️  Skipping Email Report: SENDER_EMAIL or SENDER_PASSWORD env vars missing.")


# --- 5. MAIN ---

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv() # Load .env file

    parser = argparse.ArgumentParser(description='Universal Deliverability Manager')
    parser.add_argument('--platform', required=True, choices=['smartlead', 'instantly'])
    parser.add_argument('--api-key', required=True)
    parser.add_argument('--sick-threshold', type=int, default=DEFAULT_SICK_THRESHOLD, help='Reputation % below which account is Sick')
    parser.add_argument('--report-email', type=str, help='Email to send report to')
    parser.add_argument('--slack-webhook', type=str, help='Slack Webhook URL')
    parser.add_argument('--auto-approve', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--dry-run', action='store_true', help='Simulate actions')
    parser.add_argument('--test-email', action='store_true', help='Send a test email report immediately and exit')
    parser.add_argument('--healthy-tag', type=str, default='Running', help='Tag name for healthy accounts (def: Running)')
    args = parser.parse_args()

    # Init Provider
    provider = None
    if args.platform == 'smartlead':
        provider = SmartleadProvider(args.api_key, dry_run=args.dry_run)
    elif args.platform == 'instantly':
        provider = InstantlyProvider(args.api_key, dry_run=args.dry_run)
    
    # Init Manager
    manager = UniversalDeliverabilityManager(provider, args.sick_threshold)

    # Test Email Path
    if args.test_email:
        print("🧪 Sending TEST report...")
        manager.proposed_actions.append(Action("TEST_ID", "test@example.com", "TEST_ACTION", "Verifying email delivery"))
        manager.send_report(args.report_email, args.slack_webhook)
        sys.exit(0)

    # Normal Analysis
    manager.analyze()
    manager.print_plan()

    # Pre-flight Check
    if manager.proposed_actions:
        if args.dry_run:
            print("\n[DRY RUN] Skipping execution.")
        elif args.auto_approve:
            manager.execute()
            manager.send_report(args.report_email, args.slack_webhook)
        else:
            confirm = input("\nProceed with these changes? [y/N]: ").lower()
            if confirm == 'y':
                manager.execute()
                manager.send_report(args.report_email, args.slack_webhook)
            else:
                print("❌ Operation Cancelled by user.")
