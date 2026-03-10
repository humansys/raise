---
title: rai backlog
description: Manage backlog items via project management adapters (Jira, etc.).
---

Manage backlog items via `ProjectManagementAdapter`. The query format is adapter-specific (e.g., JQL for Jira). Use `-a` to select an adapter when multiple are registered.

## `rai backlog create`

Create a new backlog item.

| Argument | Description |
|----------|-------------|
| `SUMMARY` | Issue title (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--project` | `-p` | Project key, e.g. `RAISE` (**required**) |
| `--type` | `-t` | Issue type. Default: `Task` |
| `--labels` | `-l` | Comma-separated labels |
| `--parent` | | Parent issue key |
| `--description` | `-d` | Issue description (markdown) |
| `--adapter` | `-a` | Adapter name override |
| `--format` | `-f` | Output format: `human`, `agent`. Default: `human` |

```bash
# Create a task
rai backlog create "Add CLI docs" -p RAISE

# Create with labels and parent
rai backlog create "Fix login bug" -p RAISE -t Bug -l "priority,frontend" --parent RAISE-100
```

---

## `rai backlog get`

Retrieve details for a single backlog item.

| Argument | Description |
|----------|-------------|
| `KEY` | Issue key, e.g. `RAISE-123` (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--adapter` | `-a` | Adapter name override |

```bash
rai backlog get RAISE-123
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
rai backlog get-comments RAISE-123
rai backlog get-comments RAISE-123 --limit 5
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
rai backlog search "project = RAISE AND status = 'In Progress'"

# Limit results
rai backlog search "project = RAISE" -n 10
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
rai backlog transition RAISE-123 in-progress
rai backlog transition RAISE-123 done
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
rai backlog batch-transition RAISE-1,RAISE-2,RAISE-3 done
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
rai backlog update RAISE-123 -s "Updated title" -l "urgent"
rai backlog update RAISE-123 --priority High --assignee alice
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
rai backlog link RAISE-100 RAISE-101 blocks
rai backlog link RAISE-200 RAISE-201 relates
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
rai backlog comment RAISE-123 "Implementation complete, ready for review."
```

---

## `rai backlog sync`

Regenerate `governance/backlog.md` from a remote adapter.

| Flag | Short | Description |
|------|-------|-------------|
| `--project` | `-p` | Project key filter (e.g., `RAISE`) |
| `--adapter` | `-a` | Adapter name override |

```bash
rai backlog sync -p RAISE
```

**See also:** [`rai adapter`](cli/adapter.md)
