---
title: Jira Adapter Architecture
description: Technical architecture of the ACLI Jira adapter — component diagram, class structure, sequence flows, and design decisions.
---

This document explains the internal architecture of the ACLI Jira adapter for developers who need to understand, modify, or extend it.

## Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        rai backlog CLI                       │
│                   (src/raise_cli/cli/commands/backlog.py)     │
└──────────────────────────┬──────────────────────────────────┘
                           │ resolve_adapter("jira")
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      SyncPMAdapter                           │
│              (src/raise_cli/adapters/sync.py)                │
│         Wraps async adapter for sync CLI consumption         │
└──────────────────────────┬──────────────────────────────────┘
                           │ delegates via asyncio.run()
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    AcliJiraAdapter                            │
│       (packages/raise-pro/src/rai_pro/adapters/acli_jira.py) │
│                                                              │
│  Responsibilities:                                           │
│  - Implement AsyncProjectManagementAdapter (11 methods)      │
│  - Load jira.yaml config (instances, projects, workflow)     │
│  - Resolve project → instance → site                         │
│  - Parse ACLI JSON responses into adapter models             │
│  - Normalize status names by convention                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ self._bridge.call(subcommand, flags, site=...)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    AcliJiraBridge                             │
│     (packages/raise-pro/src/rai_pro/adapters/acli_bridge.py) │
│                                                              │
│  Responsibilities:                                           │
│  - Subprocess execution: acli jira <cmd> <flags> [--json]    │
│  - Auth switching: acli jira auth switch --site <site>       │
│  - Site caching: only switch when site differs               │
│  - JSON parsing of stdout                                    │
│  - Telemetry spans (logfire) per call                        │
│  - Health check via acli jira auth status                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ asyncio.create_subprocess_exec()
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    acli (Atlassian CLI)                       │
│                    External binary in PATH                    │
│                                                              │
│  acli jira workitem search --jql "..." --limit 50 --json     │
│  acli jira workitem view PROJ-123 --fields *all --json       │
│  acli jira workitem create --project PROJ --summary ... --json│
│  acli jira auth switch --site other.atlassian.net             │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
                           ▼
                    ┌──────────────┐
                    │  Jira Cloud  │
                    │   REST API   │
                    └──────────────┘
```

## Class Diagram (UML)

```
┌─────────────────────────────────────────┐
│    «protocol»                            │
│    AsyncProjectManagementAdapter         │
├─────────────────────────────────────────┤
│ + create_issue(project, spec) → IssueRef │
│ + get_issue(key) → IssueDetail           │
│ + update_issue(key, fields) → IssueRef   │
│ + transition_issue(key, status) → IssueRef│
│ + search(query, limit) → [IssueSummary]  │
│ + batch_transition(keys, status) → Batch │
│ + link_to_parent(child, parent) → None   │
│ + link_issues(source, target, type) → None│
│ + add_comment(key, body) → CommentRef    │
│ + get_comments(key, limit) → [Comment]   │
│ + health() → AdapterHealth               │
└────────────────────┬────────────────────┘
                     │ implements
                     ▼
┌─────────────────────────────────────────┐
│           AcliJiraAdapter                │
├─────────────────────────────────────────┤
│ - _instances: dict[str, dict]            │
│ - _projects: dict[str, dict]             │
│ - _default_site: str                     │
│ - _bridge: AcliJiraBridge                │
├─────────────────────────────────────────┤
│ + __init__(project_root?)                │
│ + build_url(key) → str                   │
│ - _resolve_site(project_key) → str       │
│ - _resolve_site_from_key(issue_key) → str│
│ - _resolve_site_from_jql(jql) → str      │
│ - _extract_issue_fields(data) → dict     │
│ - _parse_issue_detail(data) → IssueDetail│
│ - _parse_result_envelope(data) → IssueRef│
│ + [all 11 protocol methods]              │
└────────────────────┬────────────────────┘
                     │ uses
                     ▼
┌─────────────────────────────────────────┐
│           AcliJiraBridge                 │
├─────────────────────────────────────────┤
│ - _binary: str                           │
│ - _current_site: str | None              │
├─────────────────────────────────────────┤
│ + __init__(binary="acli")                │
│ + call(subcommand, flags, *, site?,      │
│        json_output?) → Any               │
│ + health(site?) → AdapterHealth          │
│ - _switch_site(site) → None              │
└─────────────────────────────────────────┘

┌───────────────────┐  ┌───────────────┐  ┌──────────────┐
│    AcliBridgeError │  │  IssueSpec    │  │  IssueRef    │
│    (Exception)     │  │  IssueDetail  │  │  IssueSummary│
└───────────────────┘  │  Comment      │  │  CommentRef  │
                       │  BatchResult  │  │  AdapterHealth│
                       │  FailureDetail│  └──────────────┘
                       └───────────────┘
                       raise_cli.adapters.models
```

## Sequence Diagrams

### Search Flow

```
User          CLI             SyncPMAdapter    AcliJiraAdapter    AcliJiraBridge     acli          Jira
 │              │                   │                │                  │              │             │
 │ rai backlog  │                   │                │                  │              │             │
 │  search      │                   │                │                  │              │             │
 │  "project=X" │                   │                │                  │              │             │
 │─────────────>│                   │                │                  │              │             │
 │              │ resolve_adapter() │                │                  │              │             │
 │              │──────────────────>│                │                  │              │             │
 │              │   search(query)   │                │                  │              │             │
 │              │──────────────────>│  search(query) │                  │              │             │
 │              │                   │───────────────>│                  │              │             │
 │              │                   │                │ to_jql(query)    │              │             │
 │              │                   │                │ resolve_site(X)  │              │             │
 │              │                   │                │    call(["workitem","search"],  │             │
 │              │                   │                │         {--jql, --limit},       │             │
 │              │                   │                │         site=X.atlassian.net)   │             │
 │              │                   │                │────────────────>│              │             │
 │              │                   │                │                  │ _switch_site │             │
 │              │                   │                │                  │─────────────>│ auth switch │
 │              │                   │                │                  │              │────────────>│
 │              │                   │                │                  │              │<────────────│
 │              │                   │                │                  │  subprocess  │             │
 │              │                   │                │                  │─────────────>│ workitem    │
 │              │                   │                │                  │              │  search     │
 │              │                   │                │                  │              │  --json     │
 │              │                   │                │                  │              │────────────>│
 │              │                   │                │                  │              │<────────────│
 │              │                   │                │                  │  JSON array  │             │
 │              │                   │                │<────────────────│              │             │
 │              │                   │                │ parse → [IssueSummary]         │             │
 │              │                   │<───────────────│                  │              │             │
 │              │<──────────────────│                │                  │              │             │
 │  results     │                   │                │                  │              │             │
 │<─────────────│                   │                │                  │              │             │
```

### Multi-Instance Site Resolution

```
AcliJiraAdapter                              AcliJiraBridge              acli
      │                                            │                      │
      │  search("project = EXT")                   │                      │
      │  _resolve_site_from_jql("project = EXT")   │                      │
      │  → extract "EXT" from JQL                  │                      │
      │  → projects["EXT"].instance → "partner"    │                      │
      │  → instances["partner"].site               │                      │
      │      → "partner.atlassian.net"             │                      │
      │                                            │                      │
      │  call(cmd, flags, site="partner.atl...")    │                      │
      │───────────────────────────────────────────>│                      │
      │                                            │ site ≠ _current_site │
      │                                            │ _switch_site()       │
      │                                            │─────────────────────>│
      │                                            │  acli jira auth      │
      │                                            │   switch --site      │
      │                                            │   partner.atl...     │
      │                                            │<─────────────────────│
      │                                            │ _current_site =      │
      │                                            │  "partner.atl..."    │
      │                                            │                      │
      │                                            │ execute command       │
      │                                            │─────────────────────>│
      │                                            │<─────────────────────│
      │<───────────────────────────────────────────│                      │
```

### Create Issue Flow

```
AcliJiraAdapter              AcliJiraBridge              acli              Jira
      │                            │                      │                 │
      │ create_issue("PROJ", spec) │                      │                 │
      │ _resolve_site("PROJ")      │                      │                 │
      │   → "myorg.atlassian.net"  │                      │                 │
      │                            │                      │                 │
      │ call(["workitem","create"],│                      │                 │
      │      {--project, --summary,│                      │                 │
      │       --type, --label},    │                      │                 │
      │      site=...)             │                      │                 │
      │───────────────────────────>│                      │                 │
      │                            │ subprocess_exec      │                 │
      │                            │─────────────────────>│ workitem create │
      │                            │                      │────────────────>│
      │                            │                      │ full issue JSON │
      │                            │                      │<────────────────│
      │                            │<─────────────────────│                 │
      │  {key:"PROJ-99", fields:{}}│                      │                 │
      │<───────────────────────────│                      │                 │
      │                            │                      │                 │
      │ result["key"] → "PROJ-99"  │                      │                 │
      │ build_url("PROJ-99")       │                      │                 │
      │ → IssueRef(key, url)       │                      │                 │
```

## Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D1 | ACLI subprocess over direct REST API | Users already have ACLI installed and authenticated. No additional credential management needed. |
| D2 | Async adapter with sync wrapper | `AsyncProjectManagementAdapter` protocol allows direct use in async contexts (rai-server). CLI wraps via `SyncPMAdapter`. |
| D3 | Auth switching with site caching | ACLI has no per-command `--site` flag. Auth switch is global state. Caching avoids redundant switches. |
| D4 | Status normalization by convention | `"in-progress"` → `"In Progress"` via `replace("-", " ").title()`. No config lookup needed. |
| D5 | Project → instance routing via config | `jira.yaml` maps project keys to named instances. Regex extracts project from JQL or issue key. |
| D6 | `json_output` parameter on bridge.call() | Some ACLI commands (e.g. `workitem link create`) don't support `--json`. Parameter allows opt-out. |
| D7 | Session-scoped integration tests | One ACLI auth setup per session. One test issue created/cleaned. Avoids Jira rate limits. |

## ACLI Response Format Map

Not all ACLI commands return the same JSON format:

| Command | `--json` | Response Format |
|---------|----------|-----------------|
| `workitem create` | Yes | Full issue: `{key, id, fields: {...}}` |
| `workitem view` | Yes | Full issue: `{key, id, fields: {...}}` |
| `workitem edit` | Yes | Envelope: `{results: [{status, message, id}]}` |
| `workitem transition` | Yes | Envelope: `{results: [{status, message, id}]}` |
| `workitem search` | Yes | Array: `[{key, fields: {...}}, ...]` |
| `comment create` | Yes | Envelope: `{results: [{status, message, id}]}` |
| `comment list` | Yes | Object: `{comments: [{id, body, author}]}` |
| `link create` | **No** | Not supported — use `json_output=False` |

## File Map

| File | Purpose |
|------|---------|
| `packages/raise-pro/src/rai_pro/adapters/acli_jira.py` | Adapter: protocol impl, config, parsing, routing |
| `packages/raise-pro/src/rai_pro/adapters/acli_bridge.py` | Bridge: subprocess, auth switch, telemetry |
| `packages/raise-pro/pyproject.toml` | Entry point: `jira = rai_pro.adapters.acli_jira:AcliJiraAdapter` |
| `.raise/jira.yaml` | Per-project Jira configuration |
| `src/raise_cli/adapters/protocols.py` | Protocol contracts |
| `src/raise_cli/adapters/sync.py` | Async→sync wrapper |
| `src/raise_cli/adapters/models.py` | Shared data models (IssueRef, IssueDetail, etc.) |
| `src/raise_cli/cli/commands/_resolve.py` | Adapter resolution from entry points |
| `tests/adapters/test_acli_jira.py` | Unit tests (61, mocked subprocess) |
| `tests/adapters/test_acli_bridge.py` | Bridge unit tests |
| `tests/integration/jira/` | Integration tests (15, real Jira) |
