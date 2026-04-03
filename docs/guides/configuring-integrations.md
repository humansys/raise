---
title: Configuring Jira & Confluence
description: Set up Atlassian integrations for your RaiSE project — automated discovery, validated config, daily workflows with Rai.
---

Configure Jira and Confluence so RaiSE can manage your backlog and publish documentation. Since v2.4, most of the setup is automated — you provide credentials, Rai discovers everything else.

**Design principle:** Config files (`.raise/*.yaml`) are shared in the repo — they describe *what* to connect to. Credentials (API tokens, emails) live in environment variables — they identify *who* is connecting. You never need to look up project keys, workflow IDs, or space keys manually.

---

## Quick Start (2 minutes)

If you just want to get going:

```bash
# 1. Install adapter dependencies
pip install "raise-cli[jira,confluence]"

# 2. Set credentials (add to .bashrc/.zshrc for persistence)
export JIRA_API_TOKEN="your-token"
export JIRA_EMAIL="you@company.com"
export CONFLUENCE_API_TOKEN="your-token"
export CONFLUENCE_USERNAME="you@company.com"

# 3. Run the setup skill
/rai-adapter-setup

# 4. Verify
rai doctor
```

That's it. Rai discovers your projects, spaces, workflows, and issue types, generates validated YAML, and writes it. The rest of this guide explains what's happening under the hood and how to customize.

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| `raise-cli` | 2.4.0+ | Core CLI |
| `raise-cli[jira]` | optional | Jira adapter (`atlassian-python-api`) |
| `raise-cli[confluence]` | optional | Confluence adapter (`atlassian-python-api`) |

```bash
# Install both adapters
pip install "raise-cli[jira,confluence]"
```

No external CLI tools are needed — both adapters are pure Python.

---

## 1. Authentication

Both adapters use Atlassian API tokens (same token works for Jira and Confluence on the same site).

### Create an API token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. **Create API token** — copy it immediately (shown only once)
3. The token works for all Atlassian Cloud products on your site

### Set environment variables

Add these to your shell profile (`.bashrc`, `.zshrc`, or `.env`):

```bash
# Jira
export JIRA_EMAIL="you@company.com"
export JIRA_API_TOKEN="ATATT3x..."

# Confluence
export CONFLUENCE_USERNAME="you@company.com"
export CONFLUENCE_API_TOKEN="ATATT3x..."
```

**Multi-instance** — if your org has multiple Atlassian sites, use instance-specific vars:

```bash
export JIRA_API_TOKEN_HUMANSYS="token-for-humansys"
export JIRA_API_TOKEN_CLIENTSITE="token-for-client"
```

Resolution order: `{VAR}_{INSTANCE}` → `{VAR}` (generic fallback).

---

## 2. Automated Setup — `/rai-adapter-setup`

The setup skill automates configuration through conversation. Run it and answer 3-4 questions:

```
/rai-adapter-setup
```

**What happens:**

1. **Detect** — Rai checks which credentials are available and which configs already exist
2. **Discover** — Rai queries your Atlassian instance to find:
   - **Jira:** all projects, workflow states, issue types
   - **Confluence:** all spaces and their structure
3. **Select** — You choose which projects/spaces to include
4. **Generate** — Rai produces YAML config that passes schema validation
5. **Write** — After your approval, config is saved to `.raise/`

**Example flow:**

```
> /rai-adapter-setup

Jira credentials detected (JIRA_API_TOKEN is set)
Confluence credentials detected (CONFLUENCE_API_TOKEN is set)

Which adapters to configure? [jira/confluence/both]
> both

Discovering Jira... Found 39 projects.
Which project(s) to include? [comma-separated keys or 'all']
> RAISE, RTEST

Discovering Confluence... Found 115 spaces.
Which space to use?
> RaiSE1

[Shows generated YAML preview]

Write config to .raise/jira.yaml? [y/n]
> y

Write config to .raise/confluence.yaml? [y/n]
> y

Running rai doctor to verify... All adapter checks pass.
```

### What the generator discovers automatically

| Section | Source | Manual equivalent |
|---------|--------|-------------------|
| Projects | `list_projects()` API | Looking up keys in Jira UI |
| Workflow states | `get_status_for_project()` API | Checking board settings |
| Status mapping | Slugified from state names | Mapping names to IDs by hand |
| Issue types | `issue_createmeta_issuetypes()` API | Checking project settings |
| Spaces | `get_all_spaces()` API (paginated) | Browsing Confluence admin |

### What you still configure manually

The generator cannot discover everything. These sections need human input:

| Section | Why | How |
|---------|-----|-----|
| `workflow.lifecycle_mapping` | Maps RaiSE lifecycle events to Jira transitions | Add after setup — see [Lifecycle Mapping](#lifecycle-mapping) |
| `team` | Team members, roles, focus areas | Add manually to `jira.yaml` |
| `routing` (Confluence) | Where to publish each artifact type | Defaults provided; customize per project |

---

## 3. Manual Configuration

If you prefer full control or need to customize beyond what the generator provides.

### 3.1 Jira — `.raise/jira.yaml`

Shared in the repo. Describes the instance, projects, workflows, and team.

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
    description: RaiSE framework development
    board_type: scrum
  RTEST:
    instance: humansys
    name: RaiSE Test Sandbox
    category: Testing
    board_type: scrum

# Workflow — generated automatically by /rai-adapter-setup
workflow:
  states:
    - name: Backlog
      category: new
    - name: Selected for Development
      category: new
    - name: In Progress
      category: indeterminate
    - name: Done
      category: done

  status_mapping:
    backlog: Backlog
    selected-for-development: Selected for Development
    in-progress: In Progress
    done: Done

  # Manual — maps RaiSE lifecycle events to your Jira transitions
  lifecycle_mapping:
    story_start: 31      # transition ID for "In Progress"
    story_close: 41      # transition ID for "Done"
    epic_start: 31
    epic_close: 41
    selected: 21
    backlog: 11

# Issue types — generated automatically
issue_types:
  - name: Epic
  - name: Story
  - name: Bug
  - name: Task
  - name: Sub-task

# Manual — team section
team:
  - name: Your Name
    identifier: you@company.com
    role: lead-dev
    focus: product, architecture
```

#### Lifecycle Mapping

The `lifecycle_mapping` connects RaiSE story/epic lifecycle events to Jira transitions. To find your transition IDs:

```bash
rai backlog get RAISE-123    # any existing issue
# Look at available transitions
```

Or ask Rai:

```
What are the available transitions for issue RAISE-123?
```

### 3.2 Confluence — `.raise/confluence.yaml`

**Minimal (single instance):**

```yaml
url: "https://yoursite.atlassian.net/wiki"
space_key: "MYSPACE"
```

**Full (with routing):**

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
      developer:
        parent_title: "Developer Docs"
        labels: ["developer-docs"]
```

**Routing** controls where `rai docs publish <type>` places pages and what labels they get. Without routing, pages are created at the space root with no labels.

---

## 4. Verification — `rai doctor`

After setup, run the doctor to verify everything works:

```bash
rai doctor
```

The adapter check validates three levels:

| Level | What it checks | Failure |
|-------|---------------|---------|
| **Config** | `.raise/jira.yaml` and `.raise/confluence.yaml` exist | WARN — run `/rai-adapter-setup` |
| **Credentials** | API tokens and usernames are set | ERROR — set env vars |
| **Connectivity** | Backend is reachable (online mode) | ERROR — check token/network |

For live connectivity checks:

```bash
rai doctor --online
```

---

## 5. Daily Workflows with Rai

Once configured, the adapters power your daily work through Rai. Here's what becomes possible:

### Backlog Management (Jira)

```bash
# Search issues
rai backlog search "project = RAISE AND status = 'In Progress'" -n 10

# Get issue details
rai backlog get RAISE-1187

# Create issues
rai backlog create "Fix pagination bug" -p RAISE -t Bug

# Transition issues
rai backlog transition RAISE-1187 done

# Link issues
rai backlog link RAISE-1187 RAISE-1130 "is caused by"

# Add comments
rai backlog comment RAISE-1187 "Fixed in commit abc123"
```

### Documentation Publishing (Confluence)

```bash
# Publish an ADR
rai docs publish adr --title "ADR-045: Doctor Protocol"

# Search docs
rai docs search "adapter setup" -n 5

# Get a page
rai docs get 12345678
```

### How Skills Use Adapters

The adapters aren't just CLI tools — they're consumed by RaiSE skills throughout the lifecycle:

| Skill | Jira usage | Confluence usage |
|-------|------------|------------------|
| `/rai-story-start` | Transitions issue to In Progress | — |
| `/rai-story-close` | Transitions issue to Done | — |
| `/rai-epic-start` | Creates Epic issue if needed | — |
| `/rai-epic-close` | Transitions Epic to Done | — |
| `/rai-epic-docs` | — | Publishes epic documentation |
| `/rai-session-start` | Loads sprint context | — |
| `/rai-doctor` | Validates adapter health | Validates adapter health |
| `/rai-adapter-setup` | Discovers projects + workflows | Discovers spaces |

### Conversational Usage

You can also work through Rai conversationally:

```
> What's in my current sprint?
> Show me all bugs in RAISE
> Create a story for adding OAuth support
> Move RAISE-1200 to Done
> Publish the E1130 design doc to Confluence
```

Rai translates your intent into the right CLI commands and API calls.

### Discovery for Decision-Making

The discovery services are available beyond setup — use them anytime to understand your Jira or Confluence landscape:

```python
# In a skill or script
from raise_cli.adapters.jira_discovery import JiraDiscovery
from raise_cli.adapters.confluence_discovery import ConfluenceDiscovery

# What workflows does this project use?
jira_map = jira_discovery.discover(project_key="RAISE")
for state in jira_map.workflows["RAISE"]:
    print(f"  {state.name} ({state.status_category})")

# What spaces are available?
conf_map = confluence_discovery.discover()
for space in conf_map.spaces:
    print(f"  {space.key} — {space.name}")
```

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `No Jira API token found` | Missing env var | `export JIRA_API_TOKEN="..."` |
| `No Confluence API token found` | Missing env var | `export CONFLUENCE_API_TOKEN="..."` |
| `ImportError: atlassian-python-api` | Missing optional dep | `pip install "raise-cli[jira,confluence]"` |
| `401 Unauthorized` | Wrong token or email | Regenerate token at id.atlassian.com |
| `default_instance 'X' not found` | Instance name mismatch | Check `default_instance` matches `instances:` key |
| `Space 'X' not found` | Wrong space key | Run `/rai-adapter-setup` to discover available spaces |
| Doctor shows WARN for config | Config file missing | Run `/rai-adapter-setup` |
| Doctor shows ERROR for token | Env var not set | Check shell profile, restart terminal |
| Discovery returns empty issue types | API version mismatch | Fixed in v2.4.0 — update raise-cli |
| Discovery returns fewer spaces than expected | Pagination bug | Fixed in v2.4.0 (RAISE-1187) |

---

## Quick Checklist for New Devs

- [ ] Install adapter dependencies: `pip install "raise-cli[jira,confluence]"`
- [ ] Create API token at https://id.atlassian.com/manage-profile/security/api-tokens
- [ ] Set env vars in shell profile (`JIRA_API_TOKEN`, `JIRA_EMAIL`, `CONFLUENCE_API_TOKEN`, `CONFLUENCE_USERNAME`)
- [ ] Run `/rai-adapter-setup` — answer 3-4 questions
- [ ] Verify with `rai doctor`
- [ ] Try it: `rai backlog search "project = YOURPROJECT" -n 3`
