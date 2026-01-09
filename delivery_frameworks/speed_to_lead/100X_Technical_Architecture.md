# 100X Technical Architecture

This document outlines the advanced logic flow for the upgraded Speed-to-Lead system.

## 1. The "Clean Water" Ingestion Layer (Lead_Ingest)
**Goal:** strict validation. Do not let bad data enter the CRM.
- **Trigger:** Webhook.
- **Validator Phone:** Regex check `^\+?[1-9]\d{1,14}$`. If fail -> Reject.
- **Validator Email:** Regex check.
- **Spam Trap:** If `name` = "test" or matches common bot patterns -> Reject.
- **Outcome:** Only "Clean" leads trigger the next step.

## 2. The Intelligence Routing Layer (Router_and_Sync)
**Goal:** value-based discrimination.
- **Step 1: Enrich.**
    - Query Apollo/Clearbit with Email.
    - Fetch: `Job Title`, `Company Size`, `Revenue`, `Industry`.
- **Step 2: Score.**
    - Logic:
        - If `Revenue` > $5M OR `Title` contains "Director/VP/Founder" -> **Score: High**.
        - Else -> **Score: Standard**.
- **Step 3: Route.**
    - **High Score:** -> Round Robin (Senior Closers Only) + Slack Channel `#whale-alert`.
    - **Standard Score:** -> Round Robin (Junior SDRs).

## 3. The Hyper-Personalized Comms Layer (Communications)
**Goal:** break through the noise.
- **Input:** Lead Name, Company Name, Industry, Job Title.
- **AI Agent (OpenAI):**
    - *Prompt:* "You are a helpful assistant. A lead named {Name} from {Company} (Industry: {Industry}) just inquired. Write a 1-sentence SMS opener engaging them about {Industry} challenges."
- **Output:**
    - SMS: "{AI_Generated_Message}"
    - Email: "Quick question about {Company}..."

## 4. The Data Loop (Ad_Platform_Feedback)
**Goal:** train the algorithm.
- **Trigger:** When Lead Score is determined (High/Standard).
- **Action:** Send Offline Event to Facebook CAPI.
    - Event Name: `Lead`
    - Parameter: `value` (High = $100, Standard = $10).
    - User Data: Hash(Email), Hash(Phone).
- **Result:** Facebook Ads starts finding more "High Score" people.
