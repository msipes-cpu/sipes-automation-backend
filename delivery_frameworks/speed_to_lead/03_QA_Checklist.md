# QA Checklist: Speed-to-Lead

**Date:** [Date]
**Client:** [Client Name]
**Tester:** [Your Name]

---

## 1. Functional Tests (Does it work?)

### Lead Capture
- [ ] **Facebook Test:** Submitted test lead via FB Lead Ads Testing Tool? -> Captured?
- [ ] **Web Form Test:** Submitted test lead via Client Website? -> Captured?
- [ ] **Data Integrity:**
    - [ ] First Name matches?
    - [ ] Phone Number normalized (e.g. +1...)?
    - [ ] Source tag is correct?

### CRM Sync
- [ ] **Contact Created:** Does "Test Lead" exist in CRM?
- [ ] **Pipeline Stage:** Is Lead in "New Lead" stage?
- [ ] **Owner:** Was an owner assigned?

### Communication
- [ ] **SMS Received:** Did the test phone number receive the SMS?
- [ ] **Email Received:** Did the test email receive the auto-response?
- [ ] **Timing Check:** Did SMS arrive in <5 seconds from submission?

### Notifications
- [ ] **Slack/Teams:** Did the alert hit the channel?
- [ ] **Rep SMS:** Did the assigned Rep receive a functional "Call Now" SMS?
- [ ] **Click-to-Call:** Is the phone number in the notification clickable?

---

## 2. Logic Tests (Does it think?)

### Duplicate Handling
- [ ] Submit the *same* email address again.
    - [ ] **Pass:** System did NOT create a duplicate contact.
    - [ ] **Pass:** System DID update the existing contact's "Last Inquiry" date (or add note).

### Backup System
- [ ] Leave the test lead in "New Lead" status for 16 minutes.
    - [ ] **Pass:** Did the Manager receive the "Lead Ignored" alert?

---

## 3. Final Sign-Off
- [ ] **All Systems Green**
- [ ] **Test Data Cleared:** (Deleted test leads from CRM so client doesn't get confused).
