# Google API Standards

## Service Account Usage

### 1. Impersonation (Domain-Wide Delegation)
**Rule:** When creating Google Sheets or Drive files, **ALWAYS** use Service Account Impersonation (Domain-Wide Delegation) acting as `msipes@sipesautomation.com`.

**Reason:** 
Direct Service Account usage ("acting as itself") has a separate, restrictive storage quota (often 0 bytes for new projects or unbilled projects). Impersonating the admin user utilizes the Workspace storage, which bypasses `storageQuotaExceeded` errors and ensures files are owned by a human for easier management.

**Implementation Pattern:**
```python
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
IMPERSONATED_USER = 'msipes@sipesautomation.com'

def get_service():
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    
    # CRITICAL: Delegate authority
    delegated_creds = creds.with_subject(IMPERSONATED_USER)
    
    return build('sheets', 'v4', credentials=delegated_creds)
```

### 2. Permissions
- Do not rely on sharing files *after* creation if possible; creation via impersonation automatically makes `msipes@sipesautomation.com` the owner.
- If sharing is needed for clients, share from the impersonated account.

## Troubleshooting
- **403 PERMISSION_DENIED (storageQuotaExceeded)**: This means you forgot to impersonate. The Service Account is full/blocked. Implement `with_subject()`.
- **403 PERMISSION_DENIED (Caller does not have permission)**: Check if the API is enabled in Google Cloud Console.
