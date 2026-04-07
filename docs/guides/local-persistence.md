---
title: Local Persistence
description: Use RaiSE without external services — filesystem-backed backlog and documentation targets for offline and open-source use.
---

RaiSE ships with filesystem-backed adapters for both backlog management and documentation publishing. These are the **default** when no external services (Jira, Confluence) are configured — no setup required.

## When to Use Filesystem Adapters

| Scenario | Backlog | Docs |
|----------|---------|------|
| **Getting started** — exploring RaiSE before connecting Jira/Confluence | filesystem | filesystem |
| **Offline work** — no network access | filesystem | filesystem |
| **Open-source projects** — no Atlassian license | filesystem | filesystem |
| **Team with Atlassian** — connected to Jira and Confluence | jira | confluence or composite |
| **Belt and suspenders** — local backup + remote publish | jira | composite (both) |

## Filesystem Backlog (FilesystemPMAdapter)

### Storage

Each issue is a YAML file at `.raise/backlog/items/{KEY}.yaml`:

```
.raise/backlog/items/
├── E1.yaml          # Epic
├── S1.1.yaml        # Story under E1
├── S1.2.yaml        # Story under E1
├── E2.yaml          # Another epic
└── S2.1.yaml        # Story under E2
```

### Issue Schema

```yaml
key: E1
summary: "Implement user authentication"
issue_type: Epic
status: in-progress
description: "OAuth2 + PKCE flow for web and CLI clients"
labels:
  - security
  - v1.0
priority: high
assignee: alice@company.com
parent: null
created: "2026-04-01T09:00:00+00:00"
updated: "2026-04-03T14:30:00+00:00"
comments:
  - id: E1-1
    body: "Decided on PKCE over implicit flow"
    author: rai
    created: "2026-04-02T10:00:00+00:00"
links:
  - target: E2
    link_type: blocks
```

### Key Generation

Keys are auto-generated based on issue type:

- **Epics:** `E1`, `E2`, `E3`, ...
- **Stories:** `S{epic_num}.1`, `S{epic_num}.2`, ... (requires `parent_key` in metadata)
- **Tasks:** Same as epics (`E{N}`)

### CLI Usage

All `rai backlog` commands work transparently with the filesystem adapter:

```bash
# Create an epic
rai backlog create "Implement auth" -p LOCAL -t Epic

# Create a story under it
rai backlog create "OAuth2 flow" -p LOCAL -t Story --parent E1

# Search
rai backlog search "auth"
rai backlog search "status = in-progress"

# Transition
rai backlog transition E1 done

# Comment
rai backlog comment E1 "Completed OAuth2 implementation"

# Get details
rai backlog get E1
```

### Adapter Selection

When only one adapter is registered, it's selected automatically. When multiple adapters are available (filesystem + jira), specify which one:

```bash
rai backlog search "auth" -a filesystem    # Force filesystem
rai backlog search "auth" -a jira          # Force Jira
```

---

## Filesystem Documentation Target (FilesystemDocsTarget)

### What It Does

Writes documentation to local markdown files. This is the **write-only** counterpart to Confluence — it saves files locally but doesn't support search or retrieval (use your editor or `grep` for that).

### Usage

```bash
# Publish from governance convention (governance/roadmap.md)
rai docs publish roadmap --title "Q2 Roadmap"

# Publish from any file
rai docs publish adr --title "ADR-045" --file dev/decisions/adr-045.md

# Publish from stdin
echo "# My Doc" | rai docs publish notes --title "Session Notes" --path docs/notes.md --stdin
```

### Where Files Go

The `--path` flag (or `metadata["path"]`) determines the output location. When publishing from an existing file, the path defaults to that file's location.

### Frontmatter Validation

The filesystem target validates YAML frontmatter before writing:

- **Required fields:** `title`, `status`
- **Epic-level docs:** also require `epic_id`
- **Story-level docs:** also require `story_id` and `epic_id`

---

## Composite Target (Dual-Write)

The `CompositeDocTarget` publishes to **both** filesystem and Confluence in a single call:

1. Filesystem first (durability guarantee — your file is always saved)
2. Confluence second (returns the remote URL)
3. If Confluence fails but filesystem succeeds: returns success with "sync pending" warning

This is the default behavior when both targets are registered. No configuration needed.

```bash
# This writes locally AND publishes to Confluence
rai docs publish adr --title "ADR-045"

# Output:
# Published: adr → https://yoursite.atlassian.net/wiki/spaces/SPACE/pages/12345
```

If Confluence is down:

```
# Published: adr → docs/governance/adr-045.md
# Warning: Remote publish failed (sync pending) — retry with rai docs publish
```

---

## Migrating to Jira/Confluence Later

The filesystem adapter is a starting point, not a dead end. When you're ready to connect external services:

1. Follow the [Configuring Jira & Confluence](configuring-integrations.md) guide
2. Your filesystem backlog stays as-is — it doesn't conflict with Jira
3. Use `-a` flag to choose which adapter to use per command

There is no automatic migration from filesystem YAML to Jira issues. The recommended approach is to create new issues in Jira and reference the filesystem keys in descriptions or comments for traceability.
