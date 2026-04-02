---
title: Configuring Jira & Confluence
description: Set up Atlassian integrations for your RaiSE project — shared config in repo, secrets in environment.
---

Configure Jira and Confluence so RaiSE can manage your backlog and publish documentation.

**Design principle:** Config files (`.raise/*.yaml`) are shared in the repo — they describe *what* to connect to. Credentials (API tokens, emails) live in environment variables — they identify *who* is connecting.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| `raise-cli` | 2.4.0+ | Core CLI |
| `raise-cli[jira]` | optional | Jira adapter (installs `atlassian-python-api`) |
| `raise-cli[confluence]` | optional | Confluence adapter (installs `atlassian-python-api`) |

```bash
# Install both adapters
pip install "raise-cli[jira,confluence]"

# Or individually
pip install "raise-cli[jira]"
pip install "raise-cli[confluence]"
```

> **Note (v2.4+):** Both Jira and Confluence adapters are pure Python using `atlassian-python-api`. No external CLI tools (like `acli`) are needed.

---

## 1. Jira

### 1.1 Create an API token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create token → copy it immediately (shown only once)

### 1.2 Environment variables

Set these in your shell profile (`.bashrc`, `.zshrc`) or `.env` file:

```bash
export JIRA_USERNAME="you@company.com"
export JIRA_API_TOKEN="your-api-token-here"
```

For multi-instance setups, use instance-specific vars:

```bash
export JIRA_USERNAME_HUMANSYS="you@company.com"
export JIRA_API_TOKEN_HUMANSYS="your-token"
```

Resolution order: `JIRA_API_TOKEN_{INSTANCE}` → `JIRA_API_TOKEN`. Same for username.

### 1.3 Config file — `.raise/jira.yaml`

This file is **shared in the repo**. It describes the Jira instance, projects, workflow states, and team. No secrets here.

```yaml
# .raise/jira.yaml
default_instance: humansys

instances:
  humansys:
    site: humansys.atlassian.net
    projects: [MYPROJECT]

projects:
  MYPROJECT:
    instance: humansys
    name: My Project
    category: Development
    description: Project description
    board_type: scrum          # or kanban

workflow:
  states:
    - name: Backlog
      id: 11
      category: To Do
    - name: Selected for Development
      id: 21
      category: To Do
    - name: In Progress
      id: 31
      category: In Progress
    - name: Done
      id: 41
      category: Done

  status_mapping:
    backlog: 11
    selected: 21
    in-progress: 31
    done: 41

  lifecycle_mapping:
    story_start: 31
    story_close: 41
    epic_start: 31
    epic_close: 41

team:
  - name: Your Name
    identifier: you@company.com
    role: lead-dev
    focus: product, architecture
```

**How to discover your workflow IDs:**

```bash
rai backlog get-transitions <ISSUE_KEY>
```

Use an existing issue in your project. The transition IDs vary by Jira workflow — don't assume the defaults match yours.

### 1.4 Verify

```bash
rai backlog search "project = MYPROJECT" -n 3
```

If auth fails, you'll see: `No Jira API token found. Set JIRA_API_TOKEN_HUMANSYS or JIRA_API_TOKEN environment variable.`

---

## 2. Confluence

### 2.1 Create an API token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create token → copy it immediately (shown only once)

### 2.2 Environment variables

Set these in your shell profile (`.bashrc`, `.zshrc`) or `.env` file:

```bash
export CONFLUENCE_USERNAME="you@company.com"
export CONFLUENCE_API_TOKEN="your-api-token-here"
```

For multi-instance setups, use instance-specific vars:

```bash
export CONFLUENCE_USERNAME_HUMANSYS="you@company.com"
export CONFLUENCE_API_TOKEN_HUMANSYS="your-token"
```

Resolution order: `CONFLUENCE_API_TOKEN_{INSTANCE}` → `CONFLUENCE_API_TOKEN`. Same for username.

### 2.3 Config file — `.raise/confluence.yaml`

Shared in the repo. Describes the instance URL, space, and artifact routing.

**Minimal (single instance):**

```yaml
url: "https://yoursite.atlassian.net/wiki"
space_key: "MYSPACE"
```

**Full (with routing and instance name):**

```yaml
default_instance: humansys

instances:
  humansys:
    url: "https://humansys.atlassian.net/wiki"
    space_key: "RaiSE1"
    instance_name: "humansys"
    routing:
      adr:
        parent_title: "Architecture"
        labels: ["adr", "architecture"]
      story-scope:
        parent_title: "Epics"
        labels: ["story", "scope"]
      story-retrospective:
        parent_title: "Epics"
        labels: ["story", "retrospective"]
      epic-brief:
        parent_title: "Epics"
        labels: ["epic", "brief"]
```

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `url` | yes | Confluence base URL (include `/wiki` for Cloud) |
| `space_key` | yes | Target space key |
| `instance_name` | no | Used for env var resolution (default: `"default"`) |
| `username` | no | Falls back to `CONFLUENCE_USERNAME` env var |
| `routing` | no | Maps artifact types to parent pages and labels |

**Routing** controls where `rai docs publish <type>` places pages. Without routing, pages are created at the space root with no labels.

### 2.4 Page tracking — `.raise/confluence-pages.yaml`

Auto-generated on first publish. Maps artifact types to Confluence page IDs for upsert (create-or-update). **Do not commit this file** — it's gitignored because page IDs are instance-specific.

### 2.5 Verify

```bash
rai docs search "test" -n 1
```

If auth fails, you'll see: `No Confluence API token found. Set CONFLUENCE_API_TOKEN_HUMANSYS or CONFLUENCE_API_TOKEN environment variable.`

---

## Example: raise-commons configuration

The raise-commons project uses both integrations. Here's how it's set up:

**`.raise/jira.yaml`** — Two projects on the humansys instance:

```yaml
default_instance: humansys

instances:
  humansys:
    site: humansys.atlassian.net
    projects: [RAISE, RTEST]

projects:
  RAISE:
    instance: humansys
    name: RAISE
    category: Development
    board_type: scrum
  RTEST:
    instance: humansys
    name: RaiSE Test Sandbox
    category: Testing
    board_type: scrum
```

**`.raise/confluence.yaml`** — Full routing for all lifecycle artifacts:

```yaml
default_instance: humansys

instances:
  humansys:
    url: "https://humansys.atlassian.net/wiki"
    space_key: "RaiSE1"
    instance_name: "humansys"
    routing:
      adr:
        parent_title: "Architecture"
        labels: ["adr", "architecture"]
      story-scope:
        parent_title: "Epics"
        labels: ["story", "scope"]
      epic-brief:
        parent_title: "Epics"
        labels: ["epic", "brief"]
      # ... (20+ artifact types routed)
```

**Environment (each dev sets their own):**

```bash
export CONFLUENCE_USERNAME="emilio@humansys.ai"
export CONFLUENCE_API_TOKEN="ATATT3x..."
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `No Jira API token found` | Missing Jira env var | Set `JIRA_API_TOKEN` in shell profile |
| `No Jira username found` | Missing Jira username | Set `JIRA_USERNAME` in shell profile or `email` in config |
| `No Confluence API token found` | Missing Confluence env var | Set `CONFLUENCE_API_TOKEN` in shell profile |
| `ImportError: atlassian-python-api required` | Missing optional dep | `pip install "raise-cli[jira,confluence]"` |
| `Confluence config not found` | No `.raise/confluence.yaml` | Create config file (see 2.3) |
| `default_instance 'X' not found` | Instance name mismatch | Check `default_instance` matches a key in `instances:` |
| `401 Unauthorized` | Wrong token or email | Regenerate token at id.atlassian.com, verify email matches |
| `space_key` error | Wrong space key | Check space key in Confluence URL: `yoursite.atlassian.net/wiki/spaces/KEYHERE` |

---

## Quick checklist for new devs

- [ ] `pip install "raise-cli[jira,confluence]"` — install adapter dependencies
- [ ] Create API token at https://id.atlassian.com/manage-profile/security/api-tokens
- [ ] Set env vars in shell profile:
  - `JIRA_USERNAME` and `JIRA_API_TOKEN`
  - `CONFLUENCE_USERNAME` and `CONFLUENCE_API_TOKEN`
- [ ] Verify Jira: `rai backlog search "project = RAISE" -n 1`
- [ ] Verify Confluence: `rai docs search "test" -n 1`
