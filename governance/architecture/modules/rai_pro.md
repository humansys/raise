---
type: module
name: rai_pro
purpose: "Enterprise features package — contains provider integrations and premium functionality separated from core CLI"
status: current
depends_on: []
depended_by: [cli]
entry_points:
  - "rai backlog auth|pull|push|status"
public_api:
  - "providers.BacklogProvider (ABC)"
  - "providers.jira.JiraClient"
  - "providers.jira.oauth.authenticate"
  - "providers.jira.sync.pull_epic"
  - "providers.jira.sync.push_stories"
  - "providers.jira.sync.check_authorization"
components: 30
constraints:
  - "rai_pro never imports from raise_cli — it is an independent package"
  - "CLI wires rai_pro adapters; rai_pro knows nothing about CLI"
  - "Credentials are encrypted at rest with Fernet (0600 permissions)"
last_validated: "2026-02-15"
---

## Purpose

The `rai_pro` package contains **enterprise-only features** that extend the core RaiSE CLI. Currently this means external provider integrations (JIRA, with GitLab and Odoo planned). It is distributed as a separate top-level package (`src/rai_pro/`) to maintain clean separation from the open-core `rai_cli`.

The key design principle is that `rai_pro` is a **leaf package** — it depends on nothing inside `raise_cli`, and `raise_cli` only imports from it at the CLI wiring layer (`cli/commands/backlog.py`).

## Architecture

```
rai_pro/
├── providers/
│   ├── base.py          ← BacklogProvider ABC (provider-agnostic contract)
│   ├── auth/
│   │   └── credentials.py  ← Encrypted token storage (Fernet + 0600)
│   └── jira/
│       ├── client.py       ← JiraClient(BacklogProvider) + RateLimiter
│       ├── oauth.py        ← OAuth 2.0 + PKCE (RFC 7636)
│       ├── models.py       ← Pydantic models (JiraEpic, JiraStory, etc.)
│       ├── exceptions.py   ← Exception hierarchy (JiraError → subtypes)
│       ├── properties.py   ← Entity properties API (ADR-028)
│       ├── sync.py         ← Sync engine (pull/push/authorize)
│       └── sync_state.py   ← Persistent state (.raise/rai/sync/state.json)
```

## Key Design Decisions

- **BacklogProvider ABC**: Provider-agnostic interface with `read_epic`, `read_stories_for_epic`, `create_story`. New providers implement this contract.
- **Rate limiting**: Token bucket algorithm (10 req/sec sliding window) to respect JIRA Cloud limits.
- **Entity properties (ADR-028)**: Invisible metadata on JIRA issues (`com.humansys.raise.sync`) for tracking sync state without polluting issue fields.
- **Sync state separation**: State lives in `.raise/rai/sync/state.json`, NOT in the knowledge graph. This is intentional — sync state is ephemeral operational data.
- **Encrypted credentials**: OAuth tokens encrypted with Fernet using user-derived key, stored with 0600 permissions.

## Patterns

- All JIRA API responses are filtered to essential fields only (minimize data transfer)
- OAuth flow uses PKCE (RFC 7636) for security — no client secret exposure
- Error hierarchy: `JiraError` → `JiraApiError` (with status code), `JiraAuthError`, `JiraNotFoundError`, `JiraRateLimitError`
- Sync engine is stateless — all state flows through `SyncState` parameter
