---
title: rai backlog
description: Manage backlog items via project management adapters (Jira, etc.).
---

Manage backlog items via `ProjectManagementAdapter`. The adapter (Jira, filesystem, etc.) is selected automatically or via `-a`.

## Setup

### Machine Requirements

The Jira adapter requires [Atlassian CLI (ACLI)](https://developer.atlassian.com/cli) installed and authenticated.

```bash
# Verify ACLI is installed
acli --version

# Authenticate (opens browser for OAuth)
acli jira auth login --site your-org.atlassian.net
```

For detailed setup, multi-instance configuration, and troubleshooting, see **[Configuring Integrations](../guides/configuring-integrations.md)**.

### Project Configuration

**`.raise/jira.yaml`** — Required. Defines Jira instances and project routing.

```yaml
# .raise/jira.yaml (minimal)
default_instance: myorg

instances:
  myorg:
    site: myorg.atlassian.net
    email: you@myorg.com
    projects: [PROJ]

projects:
  PROJ:
    instance: myorg
    name: My Project
```

**`.raise/manifest.yaml`** — Set the default adapter so you don't need `-a jira` on every command:

```yaml
# .raise/manifest.yaml
backlog:
  adapter_default: jira
```

Without `adapter_default`, `rai backlog` errors with "Multiple PM adapters found" because both `filesystem` and `jira` are always registered.

### Adapter Selection

Resolution order (first match wins):

1. `-a <name>` flag on the command
2. `backlog.adapter_default` in `.raise/manifest.yaml`
3. Auto-detect — only works if exactly one adapter is registered

Since `raise-cli` registers both `filesystem` and `jira` as entry points, auto-detect always fails. **You must use one of the first two options.**

---

## Jira Notes

### Search requires JQL

`rai backlog search` passes the query string directly to Jira's search API. Plain text does not work — you must use [JQL](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/).

```bash
# wrong — returns no results
rai backlog search "PROJ-302"

# correct — JQL
rai backlog search "issue = PROJ-302"
rai backlog search "project = PROJ AND status = 'In Progress'"
```

If your project key is a reserved JQL keyword, quote it: `project = "MYPROJECT"`.

### Status names for `transition`

Status names are converted by convention: `in-progress` → `In Progress`, `done` → `Done`. Use lowercase with hyphens:

| Status name | Jira state |
|-------------|-----------|
| `backlog` | Backlog |
| `selected` | Selected For Development |
| `in-progress` | In Progress |
| `done` | Done |

```bash
rai backlog transition PROJ-123 in-progress
rai backlog transition PROJ-123 done
```

---

## `rai backlog create`

Create a new backlog item.

| Argument | Description |
|----------|-------------|
| `SUMMARY` | Issue title (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--project` | `-p` | Project key, e.g. `PROJ` (**required**) |
| `--type` | `-t` | Issue type. Default: `Task` |
| `--labels` | `-l` | Comma-separated labels |
| `--parent` | | Parent issue key |
| `--description` | `-d` | Issue description (markdown) |
| `--adapter` | `-a` | Adapter name override |
| `--format` | `-f` | Output format: `human`, `agent`. Default: `human` |

```bash
# Create a task
rai backlog create "Add CLI docs" -p PROJ

# Create with labels and parent
rai backlog create "Fix login bug" -p PROJ -t Bug -l "priority,frontend" --parent PROJ-100
```

---

## `rai backlog get`

Retrieve details for a single backlog item.

| Argument | Description |
|----------|-------------|
| `KEY` | Issue key, e.g. `PROJ-123` (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--adapter` | `-a` | Adapter name override |

```bash
rai backlog get PROJ-123
```

---

## `rai backlog get-comments`

Retrieve comments for a backlog item.

| Argument | Description |
|----------|-------------|
| `KEY` | Issue key (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--limit` | `-n` | Max comments. Default: `10` |
| `--adapter` | `-a` | Adapter name override |

```bash
rai backlog get-comments PROJ-123
rai backlog get-comments PROJ-123 --limit 5
```

---

## `rai backlog search`

Search backlog items. Query format is adapter-specific (JQL for Jira).

| Argument | Description |
|----------|-------------|
| `QUERY` | Search query (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--limit` | `-n` | Max results. Default: `50` |
| `--adapter` | `-a` | Adapter name override |
| `--format` | `-f` | Output format: `human`, `agent`. Default: `human` |

```bash
# JQL search
rai backlog search "project = PROJ AND status = 'In Progress'"

# Limit results
rai backlog search "project = PROJ" -n 10
```

---

## `rai backlog transition`

Transition a backlog item to a new status.

| Argument | Description |
|----------|-------------|
| `KEY` | Issue key (**required**) |
| `STATUS` | Target status (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--adapter` | `-a` | Adapter name override |

```bash
rai backlog transition PROJ-123 in-progress
rai backlog transition PROJ-123 done
```

---

## `rai backlog batch-transition`

Transition multiple backlog items at once.

| Argument | Description |
|----------|-------------|
| `KEYS` | Comma-separated issue keys (**required**) |
| `STATUS` | Target status (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--adapter` | `-a` | Adapter name override |

```bash
rai backlog batch-transition PROJ-1,PROJ-2,PROJ-3 done
```

---

## `rai backlog update`

Update fields on a backlog item.

| Argument | Description |
|----------|-------------|
| `KEY` | Issue key (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--summary` | `-s` | New summary |
| `--labels` | `-l` | Comma-separated labels |
| `--priority` | | Priority name |
| `--assignee` | | Assignee identifier |
| `--adapter` | `-a` | Adapter name override |

```bash
rai backlog update PROJ-123 -s "Updated title" -l "urgent"
rai backlog update PROJ-123 --priority High --assignee alice
```

---

## `rai backlog link`

Link two backlog items.

| Argument | Description |
|----------|-------------|
| `SOURCE` | Source issue key (**required**) |
| `TARGET` | Target issue key (**required**) |
| `LINK_TYPE` | Link type, e.g. `blocks`, `relates` (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--adapter` | `-a` | Adapter name override |

```bash
rai backlog link PROJ-100 PROJ-101 blocks
rai backlog link PROJ-200 PROJ-201 relates
```

---

## `rai backlog comment`

Add a comment to a backlog item.

| Argument | Description |
|----------|-------------|
| `KEY` | Issue key (**required**) |
| `BODY` | Comment text in markdown (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--adapter` | `-a` | Adapter name override |

```bash
rai backlog comment PROJ-123 "Implementation complete, ready for review."
```

---

## `rai backlog sync`

Regenerate `governance/backlog.md` from a remote adapter.

| Flag | Short | Description |
|------|-------|-------------|
| `--project` | `-p` | Project key filter (e.g., `PROJ`) |
| `--adapter` | `-a` | Adapter name override |

```bash
rai backlog sync -p PROJ
```

**See also:** [`rai adapter`](adapter.md/
