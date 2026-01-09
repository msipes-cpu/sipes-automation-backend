# Directive: Generate Proposal Workflow

This workflow allows you (the Agent) to generate a professional PDF proposal for the user based on a Fireflies.ai meeting transcript.

## 1. Goal
Produce a `Proposal.pdf` that is ready for signature and payment collection, using data extracted from a meeting.

## 2. Inputs
-   **Meeting ID** (Optional): The Fireflies Meeting ID. If not provided, fetch the *latest* meeting.
-   **Proposal Details** (Optional Overrides): Logic to override specific fields if the AI analysis is off.

## 3. Workflow Steps

### Step 1: Fetch Transcript
Run the `execution/fireflies_client.py` script.
*   **Command**: `python execution/fireflies_client.py --limit 1` (or `--id <MEETING_ID>`)
*   **Output**: Returns the full transcript text (and basic metadata like Title, Date).
*   **Action**: Store this transcript in `.tmp/transcript.txt`.

### Step 1b: Verify Meeting (CRITICAL)
**Before analyzing**, confirm with the USER that this is the correct meeting.
*   **Notify User**: "I fetched the latest meeting: **[Meeting Title]** from **[Date]**. Is this the one you want a proposal for?"
*   **Wait**: Do not proceed until confirmed. This prevents wasting time on the wrong call.

### Step 2: Analyze & Extract (Agentic)
**YOU** (The Agent) read `.tmp/transcript.txt` and extract the following JSON structure.
*   **Prompt**: "Read this transcript. Extract the Client Name, Company, Executive Summary (Outcome focused), Scope of Work (List of titles + descriptions), Pricing (Line items + Total), Timeline (Target delivery date only), and a 'Deposit Amount' (usually 50%).
    
    **CRITICAL STYLING INSTRUCTIONS**:
    1.  **Executive Summary ("The Problem")**: This needs to be DETAILED. Don't just say 'manual process'. Describe the specific pain points, lost time, errors, and emotional frustration expressed in the call. Write 3-4 distinct sentences.
    2.  **Proposed Solution ("The Solution")**: Be expansive. Describe not just 'automation' but the 'Business Transformation'. Use professional, high-agency language (e.g., 'Fully automated, zero-touch pipeline...').
    3.  **Scope of Work & Exclusions**: Extract the specific deliverables. ALSO identify and list specific **Exclusions** (e.g. data migration, design work) to protect scope.
    3.  **Related Systems**: Identify systems mentioned that are either part of the integration or explicitly OUT of scope (e.g., 'Existing ERP', 'Inventory System', 'Payroll').
    4.  **Access Requirements**: List the specific systems/accounts the client needs to provide permission for (typically includes: N8N, OpenAI, CRM, Communication channels).
    5.  **Diagram/Phasing**: If a diagram is included, clarify what subset is covered by *this* proposal vs. the full vision. DO NOT include a full system estimate unless explicitly asked.
    6.  **Future Phases**: If discussed, extract any pricing or scope notes for future phases (e.g. 'Phase 2 would be an additional $500')."

### Step 2b: Find Proof of Work (Proof)
Run the project matching script using the extracted Project Title and Summary as the query to find relevant past work.
```bash
npx tsx scripts/match-projects.ts "[extracted project title] [summary keywords]"
```
**Action**: Copy the top 2-3 matched projects into the `relevant_projects` field in the JSON.

```json
{
  "client_name": "Andy Hipkin",
  "client_company": "Sea Cow Group",
  "project_title": "Order Processing Automation",
  "executive_summary": "Automate the manual WhatsApp-to-Xero order process...",
  "relevant_projects": [
      {
          "title": "Airtable Manufacturing Job Tracker",
          "industry": "Manufacturing",
          "description": "Digitizing CNC manufacturing workflows...",
          "technologies": ["Airtable", "Automations"]
      } 
  ],
  "scope_of_work": [
    { "title": "WhatsApp Integration", "description": "Auto-ingest orders..." },
    { "title": "Xero Integration", "description": "Auto-create invoices..." }
  ],
  "timeline": "Monday delivery",
  "access_requirements": [ "Stripe", "Gmail", "Hosting" ],
  "related_systems": [ 
      { "title": "CRM", "description": "Full setup..." },
      { "title": "Cold Outreach", "description": "ROI focused..." }
  ],
  "exclusions": ["Data Migration", "Logo Design"],
  "pricing": [
    { "item": "Development Fee", "cost": 800 }
  ],
  "payment_link": "https://buy.stripe.com/...",
  "diagram_image": ".tmp/diagram.png",
  "project_phasing": {
      "note": "Diagram shows full vision. This is Phase 1.",
      "included_steps": ["Step 1", "Step 2"]
  },
  "billing_terms": "A $250 initial payment...",
  "future_phases": "Phase 2 will cost $500...",
  "client_email": "andy@seacow.com",
  "email_context": {
      "phase_info": "This covers Phase 1...",
      "urgency": "Aiming for Monday delivery..."
  }
}
```

### Optional: related_systems
You can now include a list of `related_systems` in the JSON to create a dedicated section for clarifying out-of-scope or related items.

### 3. Generate Proposal
Run the generator locally. This will create a PDF named `[J-Number]_[ClientName]_Proposal_Rev[Rev].pdf` in `.tmp/` and a `pdf_metadata.json` file for signature placement.

```bash
python3 execution/generate_proposal.py --data .tmp/proposal_data.json
```

### 4. DocuSeal, Email & CRM
**CRITICAL SAFETY RULE**: You are **FORBIDDEN** from sending emails via `gmail_agent.py` immediately. You must **ALWAYS** create a **DRAFT** first. Only the user can hit "Send".

1.  **Upload to DocuSeal** (Multi-Party):
    *   Script supports both "Client" and "Sipes Automation" signers automatically.
    ```bash
    python3 execution/docuseal_client.py --pdf .tmp/[FILENAME].pdf --emails "[CLIENT_EMAIL],msipes@sipesautomation.com" --no-email
    ```
2.  **Draft Email via Gmail API**:
    *   **Guideline 1 (Content)**: "Short and to the point". State the proposal exists and next steps.
    *   **Guideline 2 (Formatting)**: Use **HTML tags** `<b>...</b>` for bolding. Do **NOT** use markdown `**`.
    *   **Guideline 3 (Threading)**: Assume this is a reply. Find the original `Message-ID` using `gmail_agent.py --search`.
    *   **Action**: Create a **DRAFT**.
    ```bash
    # 1. Write body to file (NO SUBJECT LINE INSIDE)
    echo "Hi [Name],\n\n..." > .tmp/email_body.txt
    
    # 2. Create Draft
    python3 execution/gmail_agent.py --draft --to "[CLIENT_EMAIL]" --subject "RE: [Original Subject]" --body-file .tmp/email_body.txt
    ```
3.  **Update GHL Opportunity**:
    *   Add a note to the contact with the proposal link.
    ```bash
    python3 execution/ghl_client.py --email "[CLIENT_EMAIL]" --link "[DOCUSEAL_LINK]" --number "[J-NUMBER]"
    ```
4.  **Notify User**:
    *   "Draft created in Gmail (ID: [DraftID]). GHL Updated. Please review and click Send."

### Step 5: Final Report

### Step 6: Final Report
*   Notify the user: "Proposal for **<Client>** ($<Total>) has been generated and sent to **<Email>** via DocuSeal. Don't forget to track the deposit!"

## 4. Tools & Assets
-   `execution/fireflies_client.py`: Python script to hit Fireflies GraphQL API.
-   `execution/generate_proposal.py`: Python script using `fpdf2` to render the PDF.
-   `execution/docuseal_client.py`: Python script to send to DocuSeal.
-   Logo: `assets/logo.png` (If available, otherwise text only).
