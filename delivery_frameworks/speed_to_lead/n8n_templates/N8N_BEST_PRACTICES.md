# n8n Best Practices: Speed-to-Lead Implementation

## 1. Data Normalization (The "Standard Lead")
Different sources send data in wild formats. Do not pass raw webhooks deeper into your flow.
**Rule:** The very first logic node after ingestion MUST return this exact object:
```json
{
  "lead_id": "unique-id-generated",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone_e164": "+15551234567",
  "source_platform": "facebook_ads",
  "campaign_id": "cp_12345",
  "ingested_at": "2023-10-27T10:00:00Z"
}
```
*Why?* If you change CRMs later, you only change the mapping in *one* place (the normalization node), not in 50 different nodes.

## 2. Execution Mode for "Wait" Nodes
The "Backup Watchdog" requires a 15-minute wait.
**Critical Config:**
- Ensure your n8n instance uses `EXECUTIONS_PROCESS=main` (if low volume) or `queue` (Redis) for reliability.
- **SQLite vs Postgres:** For production, use Postgres as the n8n database. SQLite locks up under load.
- **Execution Saving:** Set "Save Execution Progress" to **True** in workflow settings. This ensures that if the server crashes during the 15-minute wait, it resumes upon restart.

## 3. Error Handling (The "Dead Letter Queue")
Things break. APIs timeout.
**Pattern:**
1.  Create a separate workflow called `[SYS] Error Handler`.
2.  Trigger: `Error Trigger` node.
3.  Action: Slack notification to *your* private channel.
4.  In every production workflow, go to Settings -> `Error Workflow` -> Select `[SYS] Error Handler`.
*Outcome:* You know something broke before the client does.

## 4. Idempotency (Duplicate Prevention)
Webhooks sometimes fire twice (retries).
**Logic:**
- Use a `Deduplication` logic.
- Easiest: Use the Lead's Email as the key.
- Redis/Key-Value Store: `GET lead_email`. If exists -> Stop. If not -> `SET lead_email` (expire 1 day).

## 5. Security
- **Webhook Authentication:**
    - Basic: Add a header check if possible.
    - URL Secrecy: Treat the webhook URL like a password. Don't share it publicly.
- **Credentials:**
    - Use n8n "Credentials" store. NEVER hardcode API keys in the nodes (HTTP Request Header).
