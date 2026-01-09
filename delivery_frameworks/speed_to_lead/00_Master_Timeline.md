# Speed-to-Lead Install: Master Timeline & Process

**Objective:** Go from "Contract Signed" to "Live System" in 48-72 hours.

## High-Level Overview

| Phase | Description | Standard Duration | Owner |
| :--- | :--- | :--- | :--- |
| **Phase 0: Pre-Work** | Contract, Payment, & Initial Form | Day 0 | Sales |
| **Phase 1: Kickoff** | Technical Discovery Integration Access | Day 1 (AM) | Onboarding |
| **Phase 2: The Build** | Webhooks, CRM Setup, Automations | Day 1 (PM) - Day 2 | Engineering |
| **Phase 3: QA & Testing** | Latency tests, Source tracking check | Day 3 (AM) | Engineering |
| **Phase 4: Handoff** | Live Demo, Training, Handover | Day 3 (PM) | Onboarding |

---

## Detailed Schedule

### Day 0: The "Yes" (Sales Handoff)
- **Trigger:** Client signs agreement & pays invoice.
- **Action 1:** System automatically sends "Welcome Email" with link to **Discovery Questionnaire** (See `01a_Discovery_Questionnaire.md`).
- **Action 2:** System prompts user to book **Kickoff Call** (link to Calendly).
- **Goal:** Get the administrative work out of the way immediately.

### Day 1: Kickoff & Access (The "Info Gathering")
- **09:00 AM - Check Discovery Form:** verifying we have CRM logins, Ad Account IDs, and Slack/Teams Webhook URLs.
- **10:00 AM - Kickoff Call (30 mins):**
    - Validate business logic (Routing rules: "Who gets the leads?").
    - Confirm response copy (SMS/Email templates).
    - Test access to all platforms (Login check).
- **12:00 PM - "Go Dark":** Inform client we are starting the build and to expect an update in 48 hours.

### Day 2: The Build (The "Deep Work")
- **Step 1: Lead Capture Infrastructure**
    - Set up Webhook listeners (Make/Zapier).
    - Map fields (Name, Email, Phone, Source, Campaign, AdID).
- **Step 2: CRM Integration**
    - Configure CRM Pipeline/Status columns.
    - Set up "Duplicate Check" logic.
- **Step 3: Notification Layer**
    - Configure Slack/Teams alerts.
    - Setup "Round Robin" logic if multiple sales reps.
- **Step 4: Speed Response Layer**
    - Configure SMS Gateway (Twilio/CRM native).
    - Configure Email Gateway.
    - Implement "Office Hours" logic (if applicable - usually 24/7 for auto-response).

### Day 3: QA & Handoff (The "Reveal")
- **09:00 AM - Internal QA:**
    - Run "Test Lead" through all sources (FB, Google, Web).
    - Stopwatch test: Did SMS arrive <5s?
    - Data check: Did tags populate correctly?
- **11:00 AM - Schedule Handoff Call:** Confirm time with client for PM.
- **02:00 PM - Handoff Call (30 mins):**
    - **The "Magic Moment":** Have client submit a lead on their own form.
    - Watch their phone buzz in <5 seconds.
    - Walk through "How to manage" (pausing, updating scripts).
- **02:30 PM - Live:** System is officially "In Production".
