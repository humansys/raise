# Implementation Plan: S-DEMO.2 OAuth Authentication

## Overview
- **Story:** S-DEMO.2
- **Epic:** E-DEMO (JIRA Sync Enabler)
- **Story Points:** 3 SP
- **Feature Size:** M
- **Timeline:** Sat 17:00 → Sat 23:00 (6 hours target)
- **Critical Path:** Blocks S-DEMO.3 (JIRA client needs auth)
- **Created:** 2026-02-14

## Objective

Implement OAuth 2.0 Authorization Code + PKCE flow for JIRA Cloud authentication, enabling secure token acquisition, storage, and refresh for RaiSE backlog sync.

**Foundation:** ADR-026 (OAuth Provider Choice) — Authorization Code + PKCE selected over Device Flow

---

## Tasks

### Task 1: Set up OAuth dependencies
- **Description:** Add required OAuth libraries to project dependencies
- **Files:**
  - `pyproject.toml` (add `atlassian-python-api`, `authlib`, `cryptography`)
- **TDD Cycle:** N/A (infrastructure setup)
- **Verification:**
  ```bash
  uv pip list | grep -E "atlassian|authlib|cryptography"
  ```
- **Size:** XS
- **Dependencies:** None
- **Duration:** ~10 min

---

### Task 2: Create credentials storage module
- **Description:** Implement secure token encryption and storage using Fernet (symmetric encryption)
- **Files:**
  - `rai_providers/auth/credentials.py` (NEW)
  - `tests/providers/auth/test_credentials.py` (NEW)
- **TDD Cycle:**
  - **RED:** Write test for `store_token()` and `load_token()` with encryption
  - **GREEN:** Implement Fernet-based encryption, XDG-compliant path (`~/.rai/credentials.json`)
  - **REFACTOR:** Extract key derivation, handle missing credentials file gracefully
- **Verification:**
  ```bash
  pytest tests/providers/auth/test_credentials.py -v
  ruff check rai_providers/auth/credentials.py
  pyright rai_providers/auth/credentials.py
  ```
- **Size:** S
- **Dependencies:** Task 1
- **Security constraints:**
  - MUST: guardrail-must-sec-001 (no secrets in code)
  - MUST: guardrail-must-sec-002 (input validation)
- **Duration:** ~45 min

---

### Task 3: Implement OAuth Authorization Code + PKCE flow
- **Description:** Core OAuth flow: redirect URI, state parameter, PKCE code verifier/challenge, token exchange
- **Files:**
  - `rai_providers/jira/oauth.py` (NEW)
  - `tests/providers/jira/test_oauth.py` (NEW)
- **TDD Cycle:**
  - **RED:** Write test for OAuth flow stages (authorization URL generation, callback handling, token exchange)
  - **GREEN:** Implement:
    - PKCE code verifier generation (random 43-128 char string)
    - Code challenge (SHA256 hash of verifier, base64url encoded)
    - Authorization URL construction with state + PKCE
    - Local HTTP server for callback (e.g., `http://localhost:8080/callback`)
    - Token exchange with authorization code
  - **REFACTOR:** Extract URL construction, callback parsing, error handling
- **Verification:**
  ```bash
  pytest tests/providers/jira/test_oauth.py -v --cov=rai_providers/jira/oauth
  pyright rai_providers/jira/oauth.py
  ```
- **Size:** M (highest complexity)
- **Dependencies:** Task 2
- **Risk:** OAuth complexity, browser interaction
- **Mitigation:** Use `authlib` for PKCE helpers, reference `atlassian-python-api` patterns
- **Duration:** ~2 hours

---

### Task 4: Implement token refresh logic
- **Description:** Automatic background token refresh when expired (using refresh token)
- **Files:**
  - `rai_providers/jira/oauth.py` (extend)
  - `tests/providers/jira/test_oauth.py` (extend)
- **TDD Cycle:**
  - **RED:** Write test for expired token detection and refresh flow
  - **GREEN:** Implement:
    - Token expiry check (compare `expires_at` with current time)
    - Refresh token exchange (POST to token endpoint)
    - Update stored credentials with new access token
  - **REFACTOR:** Handle edge cases (no refresh token, network failures, invalid refresh token)
- **Verification:**
  ```bash
  pytest tests/providers/jira/test_oauth.py::test_token_refresh -v
  ```
- **Size:** S
- **Dependencies:** Task 3
- **Duration:** ~45 min

---

### Task 5: Add CLI command `rai backlog auth`
- **Description:** Wire OAuth flow to CLI command with provider support
- **Files:**
  - `rai_cli/commands/backlog.py` (extend)
  - `tests/cli/test_backlog_auth.py` (NEW)
- **TDD Cycle:**
  - **RED:** Write integration test for `rai backlog auth --provider jira`
  - **GREEN:** Implement:
    - Typer command: `@backlog_app.command("auth")`
    - Provider validation (only "jira" for now)
    - Call OAuth flow, store credentials
    - Success feedback: "✓ Authenticated as {email}"
  - **REFACTOR:** Error handling (OAuth failures, network issues), user-friendly messages
- **Verification:**
  ```bash
  pytest tests/cli/test_backlog_auth.py -v
  rai backlog auth --help  # Verify command exists
  ```
- **Size:** S
- **Dependencies:** Task 4
- **Architecture:** mod-cli (orchestration) → mod-providers (domain logic)
- **Duration:** ~45 min

---

### Task 6 (Final): Manual integration test
- **Description:** Validate OAuth flow works end-to-end with real JIRA Cloud
- **Verification:**
  1. Run `rai backlog auth --provider jira`
  2. Verify browser opens with JIRA authorization page
  3. Approve access in JIRA
  4. Verify redirect to localhost callback
  5. Verify success message: "✓ Authenticated as {your_email}"
  6. Check `~/.rai/credentials.json` exists and contains encrypted token
  7. Make test JIRA API call (e.g., get current user)
  8. Wait for token to "expire" (or manually set expiry in past) and verify refresh works
- **Size:** XS
- **Dependencies:** Task 5 (all tasks must pass)
- **Gate:** M1 (Authentication Working) — blocks S-DEMO.3
- **Duration:** ~15 min

---

## Execution Order

**Sequential (critical path, no parallelism):**

1. **Task 1** (Dependencies setup) → Foundation
2. **Task 2** (Credentials storage) → Security layer
3. **Task 3** (OAuth flow) → Core implementation
4. **Task 4** (Token refresh) → Extends Task 3
5. **Task 5** (CLI command) → Integration layer
6. **Task 6** (Manual test) → Validation gate

**Why sequential:**
- Task 3 needs Task 2 (can't exchange tokens without storage)
- Task 4 extends Task 3 (refresh logic builds on OAuth flow)
- Task 5 needs Task 4 (CLI can't wire incomplete flow)
- Task 6 validates entire chain

**Parallel opportunities:** None (tight dependencies)

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation | Fallback |
|------|:----------:|:------:|------------|----------|
| **OAuth PKCE complexity** | Medium | High | Use `authlib` library (proven PKCE helpers). Reference ADR-026 research (32 sources). | If blocked >3h, pivot to simpler Device Flow |
| **Browser interaction in CLI** | Medium | Medium | Use `webbrowser.open()` + local HTTP server (`http.server`). Test with headless fallback (manual URL copy). | Provide manual URL copy if browser fails |
| **Token storage security** | Low | High | Use Fernet (symmetric encryption), derive key from user-specific seed. Never log tokens. | If Fernet fails, use basic file permissions (chmod 600) |
| **JIRA API changes** | Low | Medium | Pin `atlassian-python-api` version. Monitor Atlassian changelog. | Use direct REST calls if library breaks |
| **Network failures during OAuth** | Medium | Low | Implement retry with exponential backoff (3 attempts). Clear error messages. | User can retry command |

---

## Success Criteria (M1 Gate)

**Milestone M1: Authentication Working (Saturday 23:00)**

- [x] Task 1: Dependencies installed
- [ ] Task 2: Credentials storage working (encrypted, XDG-compliant)
- [ ] Task 3: OAuth flow completes (browser → redirect → token)
- [ ] Task 4: Token refresh works (automatic background)
- [ ] Task 5: CLI command works (`rai backlog auth --provider jira`)
- [ ] Task 6: Manual integration test passes (JIRA API call succeeds)

**Demo capability:** `rai backlog auth --provider jira` → "✓ Authenticated as user@example.com"

**Blocker fallback:** If M1 not reached by 23:00 Saturday → Escalate to user, consider pivot to hardcoded API tokens (less secure but faster)

---

## Duration Tracking

| Task | Size | Planned | Actual | Variance | Notes |
|------|:----:|:-------:|:------:|:--------:|-------|
| 1 | XS | 10 min | — | — | Dependencies |
| 2 | S | 45 min | — | — | Credentials storage |
| 3 | M | 2h | — | — | OAuth flow (highest risk) |
| 4 | S | 45 min | — | — | Token refresh |
| 5 | S | 45 min | — | — | CLI command |
| 6 | XS | 15 min | — | — | Manual integration test |
| **Total** | **M (3 SP)** | **~5h** | — | — | 1h buffer for unknowns |

**Velocity target:** 3 SP / 6h = 0.5 SP/hour (on track for 10-12 SP/day)

**Tracking:** Update "Actual" column after each task completion. Commit after each task with duration in commit message.

---

## Quality Gates (Per-Task)

- [ ] Unit tests pass (`pytest`)
- [ ] Type checks pass (`pyright --strict`)
- [ ] Linting passes (`ruff check`)
- [ ] Security scan passes (`bandit -r rai_providers/`)
- [ ] Test coverage >90% for new code
- [ ] No secrets in code (credentials.json never committed)
- [ ] Docstrings on all public APIs (Google-style)

---

## Architecture Notes

**New module:** `rai_providers/` (integration layer)

```
rai_providers/
├── __init__.py
├── auth/
│   ├── __init__.py
│   └── credentials.py      # Task 2: Token encryption/storage
└── jira/
    ├── __init__.py
    └── oauth.py             # Task 3-4: OAuth flow + refresh
```

**CLI integration:** `rai_cli/commands/backlog.py` (Task 5)

**Bounded context:** bc-external-integration (NEW) — JIRA/GitLab/Odoo adapters

**Layer:** lyr-integration (NEW) — Depends on leaf (config), depended by orchestration (CLI)

**Dependencies:**
- mod-providers → mod-config (credentials path resolution)
- mod-cli → mod-providers (orchestrates OAuth flow)

---

## Next Steps

After S-DEMO.2 complete:
1. **Commit & Push:** Merge story branch to `demo/atlassian-webinar`
2. **Update Plan:** Mark M1 milestone complete in `work/epics/e-demo-jira-sync/plan.md`
3. **Next Story:** `/rai-story-start S-DEMO.3` (JIRA client — needs auth from this story)

---

*Plan created: 2026-02-14*
*TDD-first approach: RED → GREEN → REFACTOR for all tasks*
*Ready for `/rai-story-implement`*
