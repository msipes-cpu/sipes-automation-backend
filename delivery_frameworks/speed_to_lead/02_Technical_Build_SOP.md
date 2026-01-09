# SOP: Speed-to-Lead Technical Build

**Role:** Automation Engineer
**Goal:** Configure sub-5-second lead routing and response.

---

## Phase 1: Ingestion Layer (The "Catch")
**Tool:** Make.com (formerly Integromat) or Zapier.

1.  **Create Scenario/Zap:** `[Client Name] - Speed-to-Lead Core`
2.  **Add Trigger: Webhook**
    *   Create a catch hook.
    *   Copy the URL.
3.  **Connect Sources:**
    *   **Facebook:** Connect FB Lead Ads app -> Subscribe to Page/Form -> Point to Webhook.
    *   **Website:** Configure form plugin (Elementor/Gravity Forms/Webflow) -> Webhook.
    *   **Google:** Connect Google Lead Form extension -> Webhook.
4.  **Standardize Data:**
    *   Add a "Set Variable" module to normalize fields:
        *   `lead_name`
        *   `lead_phone` (E.164 format)
        *   `lead_email`
        *   `lead_source` (e.g., "Facebook", "Website")

## Phase 2: CRM Layer (The "Store")
1.  **Search/Create Contact:**
    *   Check for existing contact by Email.
    *   If null, CREATE Contact.
        *   Map `lead_name`, `lead_email`, `lead_phone`.
        *   Add Tag: `speed-to-lead-active`
        *   Add Tag: `Source: [lead_source]`
2.  **Create Deal/Opportunity:**
    *   Pipeline: `Sales Pipeline`
    *   Stage: `New Lead`
    *   Owner: `[Assigned Rep ID]` (See Phase 4 for logic).

## Phase 3: Response Layer (The "Speed")
1.  **SMS:**
    *   **If GHL:** Add to "Auto-SMS" workflow.
    *   **If Twilio:** Send Message Module.
        *   To: `lead_phone`
        *   Body: *[Insert Template from Questionnaire]*
2.  **Email:**
    *   Send Email Module (Gmail/Outlook/SMTP).
        *   To: `lead_email`
        *   Subject/Body: *[Insert Template]*

## Phase 4: Notification Layer (The "Alert")
1.  **Determine Assignee:**
    *   *Simple:* Static assignment to one rep.
    *   *Advanced:* Data store in Make.com with `[Rep1, Rep2, Rep3]`. Rotate index.
2.  **Slack/Teams Notification:**
    *   HTTP Post to Client Webhook.
    *   **Payload:**
        ```json
        {
          "text": "🔥 NEW LEAD: [Name]\n📞 Phone: [Phone]\n📧 Email: [Email]\n🔗 Source: [Source]\n👤 Assigned to: [Rep Name]"
        }
        ```
3.  **Internal SMS:**
    *   Send SMS to the *Assigned Rep's* mobile number.
    *   Body: *"NEW LEAD: [Name]. Call now! [Phone]"*

## Phase 5: Backup Layer (The "Safety Net")
1.  **Wait Step (Make.com):**
    *   Sleep 15 Minutes.
2.  **Check Status:**
    *   Get CRM Contact/Deal.
    *   Filter: If `Status` is still `New Lead` (meaning status hasn't changed to "Contacted" or "Qualified").
3.  **Alert Manager:**
    *   Send SMS/Slack to `[Manager Name]`.
    *   Body: *"⚠️ ALERT: Lead [Name] has not been contacted for 15 minutes!"*
