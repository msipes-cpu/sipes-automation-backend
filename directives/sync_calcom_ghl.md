# Sync Cal.com Bookings to GoHighLevel

## Goal
Automate the process of adding new Cal.com bookings to GoHighLevel (GHL) as contacts and adding them to a specific Opportunity pipeline.

## Inputs
- **Cal.com API Key**: To fetch bookings.
- **GoHighLevel Access Token**: To interact with the GHL API (contacts & opportunities).
- **GHL Location ID**: The specific sub-account in GHL.
- **Pipeline ID**: The ID of the pipeline to add the lead to.
- **Stage ID**: The specific stage (e.g., "Meeting Booked") to place the lead in.

## Modes of Operation

### 1. Polling Mode (Local Script)
Run `python3 execution/sync_calcom_and_ghl.py` manually or via cron. It fetches recent bookings and processes new ones.

### 2. Webhook Mode (Make.com / Cloud)
This logic can be triggered by a webhook.
- **Trigger**: Make.com receives Cal.com webhook -> Sends JSON payload to this system.
- **Receiver**: You need a running server (like `webhook_server.py`) to accept the POST request.
- **Constraint**: If you cannot run a local server/ngrok, **you cannot "send it to me" (the AI agent) directly** as I am not a persistent server. I am an ephemeral process.

**Alternative Workflow using Make.com ONLY:**
If you want to avoid running local Python scripts entirely, you can migrate this logic *into* Make.com:
1.  **Make Trigger**: Cal.com "Watch Bookings".
2.  **Make Action**: HTTP Request to GHL API (Contacts Upsert).
3.  **Make Action**: HTTP Request to GHL API (Opportunity Create).
4.  **Make Action**: Twilio/GHL SMS.

**If you want to keep the Python Logic but trigger via Make:**
You still need a place to *host* the Python script (Render, Heroku, AWS Lambda). Make.com would then send a request to your hosted Python script.

## Setup Requirements
- `.env` file must contain:
    - `CALCOM_API_KEY`
    - `GHL_ACCESS_TOKEN`
    - `GHL_LOCATION_ID`
    - `GHL_PIPELINE_ID`
    - `GHL_STAGE_ID`
