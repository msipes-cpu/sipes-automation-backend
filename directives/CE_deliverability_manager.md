# CE Deliverability Manager (Inbox Bench)

## New Instance Setup Checklist (ASK USER FIRST)
Before creating a new instance of Inbox Bench (Deliverability Manager), you **MUST** obtain the following information:

### 1. Platform & Access
*   **Platform**: "Is this for **Smartlead** or **Instantly**?"
*   **Instance Name**: "What should we name this instance in reports (e.g., 'Client X', 'Main', 'Agency 2')?"
*   **Dashboard URL**: "Please provide the direct link to the Email Accounts page for this workspace."
*   **API Key**: "Please provide the API Key for this specific workspace."

### 2. Tagging (CRITICAL)
*   **Tags Created?**: "Have you manually created these 4 tags in the platform?"
    *   `Warming`
    *   `Sick`
    *   `Bench`
    *   `Sending`
*   **Seed Account (Smartlead Only)**: "For Smartlead, have you assigned ALL 4 tags to one of the **first 10** email accounts?" (Required for ID discovery).

### 3. Logic Configuration
*   **Inbox Health**: "What is the minimum warmup reputation? (Default: **97%** or **98%**)"
*   **Campaign Sync (Smartlead Only)**: "Do you want to automatically add/remove 'Sending' accounts from specific Campaigns? If yes, provide the **Campaign IDs**."

### 4. Reporting
*   **Recipient Email**: "Where should the daily report be sent?"
*   **Slack Webhook**: "Do you have a Slack Webhook URL for notifications?"
*   **SMTP Credentials**: "Do you have specific SMTP credentials (Sender Email/Pass) for this report, or should we use the default `smartguard-secrets`?"

### 5. Deployment
*   **Secrets**: will need to be added to `modal_*.py` or Modal Secrets.

## Logic Overview
Ideally runs daily to categorize email accounts into 4 buckets:
1.  **Warming**: < 14 days old (from created_at).
2.  **Sick**: < 97% Reputation (matches specific threshold).
3.  **Bench**: Healthy but resting (20% of healthy pool).
4.  **Sending**: Healthy and active (80% of healthy pool).

## Quick Start
```bash
python3 -m modal run execution/modal_deliverability_manager.py::run_job
```

## Prerequisites (CRITICAL)
Smartlead's API does **NOT** support creating tags. You must:
1.  **Manually Create Tags** in Smartlead UI: `Warming`, `Sick`, `Bench`, `Sending`.
2.  **Assign ALL 4 Tags** to a single "Seed" email account.
    *   **CRITICAL**: This Seed Account MUST be one of the **first 10 accounts** in your Smartlead list (e.g., `sipesautocore.com`). The script scans the top 100, but ensuring it's in the top 10 guarantees discovery.

## Configuration
- **Concurrency**: Set `max_workers=3` to avoid Rate Limits.
- **Throttle**: `0.5s` delay between actions is recommended.
- **Retries**: Use robust backoff (5 retries) for API calls.

## Deployment (Modal)
The job is deployed on Modal to run daily.
- **Entrypoint**: `execution/modal_deliverability_manager.py`
- **Logic**: `execution/universal_deliverability_manager.py` (Uploaded into container)
- **Secrets**:
    - `smartguard-secrets`: Default.
    - `sa-sm1-secret`: Specific override for `SA_SM1_API_KEY`.
