# Fathom Transcript to Cold Email Strategy Automation

## Goal
Automate the creation of a "D100" Cold Email Strategy document from a Fathom sales call transcript. 
1. Validate the lead in GHL.
2. Extract key info using OpenAI.
3. Generate strategy content (Target Audience, Email Sequence, ROI).
4. Create a Google Doc with the strategy.
5. Update GHL with the asset link and next steps.
6. Notify the sales team via Slack.

## Triggers
- **Manual/Webhook**: Triggered when a new transcript is available from Fathom.
- **Input**: `transcript_text` (or path to file), `prospect_email`, `meeting_date`.

## Workflow Steps

### 1. Qualification Check (GHL)
- **Tool**: `execution/ghl_client.py`
- **Action**: Search contact by email.
- **Logic**: 
    - Verify contact exists.
    - Check Pipeline Stage.
    - **Stop** if Pipeline Stage != [Target Stage] (e.g., "Demo Completed" or input arg).

### 2. AI Extraction & Generation (OpenAI)
- **Tool**: `execution/process_fathom_transcript.py` (Main Logic)
- **Models**: GPT-4o
- **Steps**:
    1.  **Extract Info**: Parse transcript for Prospect Name, Company, Pain Points, etc.
    2.  **Generate Target Audience**: Based on industry/pain points.
    3.  **Write Emails**: 5-email sequence.
    4.  **Calculate ROI**: Projection based on inputs.

### 3. Document Creation (Google Docs)
- **Tool**: `execution/gdrive_manager.py`
- **Action**: 
    - Compile all generated sections into a Markdown formatted text.
    - Upload to Google Drive with MIME type conversion to Google Doc.
    - Save to folder: "Client Assets" (or similar).

### 4. CRM Update (GoHighLevel)
- **Tool**: `execution/ghl_client.py`
- **Actions**:
    - Add Tag: "D100 Ready"
    - Add Note: Link to D100 doc, Opportunity Score, Next Steps.
    - Create Task: "Review D100 for [Prospect]"

### 5. Notification (Slack)
- **Tool**: `execution/slack_client.py`
- **Action**: Send message to `#sales`.
- **Content**: Prospect Name, Score, Link to Doc.

## Inputs & Configuration
- `OPENAI_API_KEY`: Required.
- `GHL_ACCESS_TOKEN`: Required.
- `SLACK_BOT_TOKEN`: Required.
- `GOOGLE_SERVICE_ACCOUNT_FILE`: Required.

## Edge Cases
- **Contact Not Found**: Create contact or Error (Configurable). Default: Error.
- **Low Opportunity Score**: Flag in Slack? (Currently just logs).
- **Drive Failure**: Retry or save local backup.
