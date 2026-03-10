# JIRA OAuth Setup Guide

**Purpose:** Document the OAuth app configuration for RaiSE ↔ JIRA integration.

**Created:** 2026-02-15 (during S-DEMO.6 Rehearsal 1 debugging)

---

## OAuth App: "rai cli"

**Location:** [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/)

### Configuration

| Setting | Value |
|---------|-------|
| **App Name** | rai cli |
| **Callback URL** | `http://localhost:8080/callback` (EXACT match required) |
| **Scopes** | `read:jira-work`, `write:jira-work`, `read:jira-user`, `read:me`, `offline_access` |
| **Permissions** | User Identity API (MUST be enabled) |

### Credentials (Secret — NOT in repo)

Stored in `.env` file (gitignored):

```bash
JIRA_CLIENT_ID=<from-developer-console>
JIRA_CLIENT_SECRET=<from-developer-console>
JIRA_CLOUD_ID=<from-accessible-resources-api>
```

---

## Setup Instructions

### First-Time Setup

1. **Get OAuth credentials:**
   - Go to: https://developer.atlassian.com/console/myapps/
   - Open "rai cli" app
   - Copy Client ID and Client Secret

2. **Configure environment:**
   ```bash
   # Edit .env file
   vim .env

   # Add credentials:
   JIRA_CLIENT_ID=<paste-client-id>
   JIRA_CLIENT_SECRET=<paste-client-secret>
   JIRA_CLOUD_ID=<leave-empty-for-now>
   ```

3. **Load environment variables:**
   ```bash
   source .envrc
   ```

4. **Authenticate:**
   ```bash
   rai backlog auth --provider jira
   ```

   This will:
   - Open browser for OAuth flow
   - Store encrypted token in `~/.rai/credentials.json`
   - Display authenticated user email

5. **Get Cloud ID:**
   ```bash
   # After successful auth, retrieve cloud ID:
   curl -H "Authorization: Bearer $(python3 -c "from rai_providers.auth.credentials import load_token; from rai_cli.config.paths import get_credentials_path; print(load_token('jira', get_credentials_path())['access_token'])")" \
     https://api.atlassian.com/oauth/token/accessible-resources | jq -r '.[0].id'
   ```

   Update `.env` with the cloud ID:
   ```bash
   JIRA_CLOUD_ID=<paste-cloud-id>
   ```

6. **Reload environment:**
   ```bash
   source .envrc
   ```

### Per-Session Setup

**Every time you start a new terminal session:**

```bash
cd /home/emilio/Code/raise-commons
source .envrc
```

**Or use direnv for automatic loading:**

```bash
# Install direnv (one-time)
sudo apt install direnv  # or: brew install direnv

# Configure shell (one-time, add to ~/.bashrc or ~/.zshrc)
eval "$(direnv hook bash)"  # or: eval "$(direnv hook zsh)"

# Allow .envrc in this directory (one-time per project)
direnv allow

# Now .env loads automatically when you cd into the directory
```

---

## Files

| File | Purpose | Tracked in Git? |
|------|---------|-----------------|
| `.env` | OAuth credentials (secrets) | ❌ NO (in .gitignore) |
| `.envrc` | Loader script | ✅ YES (safe, no secrets) |
| `~/.rai/credentials.json` | Encrypted OAuth tokens | ❌ NO (local user data) |

---

## Troubleshooting

### "Couldn't identify the app" error

**Cause:** `JIRA_CLIENT_ID` or `JIRA_CLIENT_SECRET` not set or incorrect.

**Fix:**
1. Check `.env` has correct values
2. Run `source .envrc`
3. Verify: `echo $JIRA_CLIENT_ID` (should show your client ID)

### "JIRA_CLOUD_ID environment variable not set" error

**Cause:** Cloud ID not configured.

**Fix:**
1. Follow Step 5 in "First-Time Setup" to retrieve cloud ID
2. Add to `.env`
3. Run `source .envrc`

### 401 Unauthorized errors

**Cause:** Token expired or invalid.

**Fix:**
1. Re-authenticate: `rai backlog auth --provider jira`
2. If that fails, check OAuth app is still active in Developer Console

### Callback URL mismatch

**Cause:** OAuth app callback URL doesn't match `http://localhost:8080/callback`

**Fix:**
1. Go to Developer Console
2. Edit "rai cli" app
3. Set callback URL EXACTLY: `http://localhost:8080/callback` (no trailing slash)

---

## Security Notes

- **Never commit `.env`** — contains OAuth secrets
- Tokens are encrypted in `~/.rai/credentials.json` (Fernet encryption)
- File permissions: `credentials.json` is 0600 (owner read/write only)
- Tokens include refresh tokens for automatic renewal

---

## Pattern for Memory

**PAT-205: OAuth credentials require env var persistence**

**Problem:** CLI OAuth flow works during session but fails on next session because `JIRA_CLIENT_ID`, `JIRA_CLIENT_SECRET`, and `JIRA_CLOUD_ID` are not persisted.

**Solution:**
1. Store secrets in `.env` (gitignored)
2. Create `.envrc` loader script (tracked in git)
3. Document "source .envrc" as session setup requirement
4. Recommend direnv for automatic loading

**Why this pattern:**
- Separates secrets (`.env`) from safe config (`.envrc`)
- Explicit load step prevents accidental secret exposure
- Direnv integration provides DX convenience
- Works across team members (each has own `.env`)

**Related files:**
- `.env` (template created, secrets filled by developer)
- `.envrc` (loader script, safe to commit)
- `.gitignore` (ensures `.env` never tracked)

**Session discipline:** Add "source .envrc" to session startup checklist for JIRA-dependent work.

---

**Last Updated:** 2026-02-15
**Story:** S-DEMO.6 (Rehearsal 1 debugging)
