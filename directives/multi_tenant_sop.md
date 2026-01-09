# Multi-Tenant Automation SOP

**Goal:** Manage multiple clients from a single workspace using a centralized configuration.

## Core Rules

1.  **One Workspace:** Do not create new workspaces for new clients. All clients live in `config/clients.json`.
2.  **Selective Automations:** **Clients do NOT get all automations by default.** You must explicitly enable specific automations for each client in their configuration.
3.  **Stateless Execution:** Execution scripts (flows) must remain generic and accept client configurations as arguments.

## Configuration Schema (`config/clients.json`)

Each client object must include:

```json
{
  "client_name": "String",
  "client_id": "String (Unique)",
  "enabled_automations": [ "lead_sourcing", "email_reporting", "etc..." ],
  "settings": {
      "api_keys": { ... },
      "parameters": { ... }
  }
}
```

## Onboarding Process

1.  Add client to `config/clients.json`.
2.  **Ask the user** which automations to enable for this specific client.
3.  Add only those automation IDs to the `enabled_automations` list.
