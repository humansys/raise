---
title: Jira Adapter (ACLI)
description: Install, configure, and use the ACLI-based Jira adapter for rai backlog commands. Supports multi-instance Jira with project routing.
---

The Jira adapter connects `rai backlog` to Jira Cloud via [Atlassian CLI (ACLI)](https://developer.atlassian.com/cli). It replaces the previous MCP-based adapter with a simpler subprocess model that supports multi-instance Jira sites.

## Prerequisites

### 1. Install Atlassian CLI

Download and install ACLI from [developer.atlassian.com/cli](https://developer.atlassian.com/cli).

```bash
# Verify installation
acli --version
```

### 2. Authenticate

ACLI manages its own credentials. Authenticate to each Jira site you'll use:

```bash
# Interactive login — opens browser for OAuth
acli jira auth login --site your-org.atlassian.net

# Verify authentication
acli jira auth status
```

You can authenticate to multiple sites. The adapter switches between them automatically based on project routing.

### 3. Install raise-pro

The Jira adapter lives in the `raise-pro` package:

```bash
uv pip install -e packages/raise-pro
```

Verify the entry point is registered:

```bash
rai adapter list
# Should show: jira (rai_pro.adapters.acli_jira:AcliJiraAdapter)
```

## Configuration

### `.raise/jira.yaml` — Required

This file defines your Jira instances, project routing, and workflow mapping.

#### Minimal (single instance)

```yaml
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

#### Multi-instance

```yaml
default_instance: primary

instances:
  primary:
    site: primary.atlassian.net
    email: you@primary.com
    projects: [PROJ, INFRA]

  partner:
    site: partner.atlassian.net
    email: you@partner.com
    projects: [EXT]

projects:
  PROJ:
    instance: primary
    name: Main Product
  INFRA:
    instance: primary
    name: Infrastructure
  EXT:
    instance: partner
    name: External Integrations
```

When you run `rai backlog search "project = EXT"`, the adapter:
1. Extracts `EXT` from the JQL
2. Looks up `projects.EXT.instance` → `partner`
3. Looks up `instances.partner.site` → `partner.atlassian.net`
4. Switches ACLI auth to that site before executing

Unknown projects fall back to `default_instance`.

#### Configuration Reference

| Field | Required | Description |
|-------|----------|-------------|
| `default_instance` | Yes | Instance name to use when project is unknown |
| `instances` | Yes | Named Jira site configurations |
| `instances.<name>.site` | Yes | Jira Cloud hostname (e.g. `myorg.atlassian.net`) |
| `instances.<name>.email` | No | Account email (documentation only) |
| `instances.<name>.projects` | Yes | Project keys hosted on this instance |
| `projects` | No | Project-to-instance routing overrides |
| `projects.<KEY>.instance` | Yes | Instance name for this project |
| `projects.<KEY>.name` | No | Human-readable project name |
| `workflow.status_mapping` | No | Status name → transition ID mapping (legacy) |
| `workflow.lifecycle_mapping` | No | Lifecycle event → transition ID for auto-sync hooks |

### `.raise/manifest.yaml` — Recommended

Set the default adapter so you don't need `-a jira` on every command:

```yaml
backlog:
  adapter_default: jira
```

Without this, `rai backlog` will error when both `filesystem` and `jira` adapters are registered.

## Usage

### Search

```bash
# JQL search
rai backlog search "project = PROJ AND status = 'In Progress'" -a jira

# Limit results
rai backlog search "project = PROJ" -n 10 -a jira

# Issue key lookup (auto-converted to JQL)
rai backlog search "PROJ-123" -a jira

# Text search (auto-converted to text ~ "query")
rai backlog search "onboarding flow" -a jira
```

**Note:** If your project key is a JQL reserved word (e.g. `RAISE`, `ORDER`), quote it: `project = 'RAISE'`.

### Get issue details

```bash
rai backlog get PROJ-123 -a jira
```

### Create issues

```bash
# Simple task
rai backlog create "Fix login bug" -p PROJ -t Bug -a jira

# With labels and parent
rai backlog create "Add docs" -p PROJ -t Story -l "docs,v2.3" --parent PROJ-100 -a jira
```

### Transition status

Status names are converted by convention: `in-progress` → `In Progress`, `done` → `Done`.

```bash
rai backlog transition PROJ-123 in-progress -a jira
rai backlog transition PROJ-123 done -a jira
```

### Batch transition

```bash
rai backlog batch-transition PROJ-1,PROJ-2,PROJ-3 done -a jira
```

### Comments

```bash
# Add comment
rai backlog comment PROJ-123 "Implementation complete." -a jira

# Get comments
rai backlog get-comments PROJ-123 -a jira
```

### Link issues

```bash
rai backlog link PROJ-100 PROJ-101 Blocks -a jira
```

### Health check

```bash
rai adapter check
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ACLI binary 'acli' not found in PATH` | ACLI not installed | Install from [developer.atlassian.com/cli](https://developer.atlassian.com/cli) |
| `AcliJiraAdapter init failed` | Missing or malformed `jira.yaml` | Check `.raise/jira.yaml` has `instances` and `default_instance` |
| `auth switch to X failed` | Not authenticated to that site | Run `acli jira auth login --site X` |
| `'RAISE' is a reserved JQL word` | Project key is a JQL keyword | Quote in queries: `project = 'RAISE'` |
| `PM adapter 'jira' not found` | `raise-pro` not installed | Run `uv pip install -e packages/raise-pro` |
| `Multiple PM adapters found` | No default set | Add `backlog.adapter_default: jira` to `.raise/manifest.yaml` |
