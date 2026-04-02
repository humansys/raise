---
epic_id: "RAISE-1130"
title: "Adapter Self-Service — Design"
status: "accepted"
created: "2026-04-01"
---

# E1130 Design: Adapter Self-Service

## Gemba — Current State

### What Exists

| Component | Location | Discovery-relevant methods |
|-----------|----------|---------------------------|
| `ConfluenceClient` | `adapters/confluence_client.py` | `get_spaces()`, `get_page_children()`, `search()`, `health()` |
| `JiraClient` | `adapters/jira_client.py` | `get_transitions(key)`, `server_info()`, `jql()` |
| `ConfluenceConfig` | `adapters/confluence_config.py` | `from_dict()`, `ConfluenceInstanceConfig` Pydantic model |
| `JiraConfig` | `adapters/jira_config.py` | `from_dict()`, instance/project/workflow Pydantic models |
| `DoctorCheck` Protocol | `doctor/protocol.py` | `evaluate(context) → list[CheckResult]` |
| `AdapterHealth` model | `adapters/models/health.py` | `name`, `healthy`, `message`, `latency_ms` |
| `rai adapter check` CLI | existing | Validates Protocol contracts, not config vs backend |
| `rai doctor` CLI | existing | Extensible via `rai.doctor.checks` entry points |

### Gaps

1. **JiraClient** has no project listing, workflow discovery, or issue type discovery
2. **No config generation** — only config parsing exists
3. **No adapter doctor checks** — framework exists, no checks registered for Jira/Confluence
4. **No setup skill** — users write YAML manually

## Target Architecture

```
┌─────────────────────────────────────────────────────┐
│  /rai-adapter-setup  (S1130.6)                      │
│  Skill — orchestrates generators, writes files      │
└──────────┬─────────────────────┬────────────────────┘
           │                     │
    ┌──────▼──────┐       ┌──────▼──────┐
    │  Confluence  │       │  Jira       │
    │  Generator   │       │  Generator  │
    │  (S1130.4)   │       │  (S1130.5)  │
    └──────┬──────┘       └──────┬──────┘
           │                     │
    ┌──────▼──────┐       ┌──────▼──────┐
    │  Confluence  │       │  Jira       │
    │  Discovery   │       │  Discovery  │
    │  (S1130.1)   │       │  (S1130.2)  │
    └──────┬──────┘       └──────┬──────┘
           │                     │
    ┌──────▼──────┐       ┌──────▼──────┐
    │  Confluence  │       │  Jira       │
    │  Client      │       │  Client     │
    │  (existing)  │       │  (existing) │
    └─────────────┘       └─────────────┘

    ┌─────────────────────────────────────┐
    │  AdapterDoctorCheck  (S1130.3)      │
    │  DoctorCheck entry point            │
    │  Uses both discovery services       │
    └─────────────────────────────────────┘
```

## Design Decisions

### D1: Discovery as internal modules, not CLI commands

Discovery services (`confluence_discovery.py`, `jira_discovery.py`) live in `adapters/`.
Consumed by doctor and generator. Not exposed as CLI subcommands.

**Why:** Users never need to "discover" manually. The generator and doctor do it for them.
A CLI would be a second interface to maintain with no user value.

### D2: Doctor checks as entry points

`AdapterDoctorCheck` implements the existing `DoctorCheck` Protocol.
Registered in `rai.doctor.checks` entry point → appears automatically in `rai doctor`.

One check class, multiple validations:
- Config file exists and parses
- Env vars are set (token, username)
- Config matches live backend (space exists, project exists, transitions valid)

**Why:** Zero new CLI commands. Consistent with existing doctor framework (ADR-045).

### D3: Config generator returns dict, does not write files

Generator functions: `generate_confluence_config(discovered) → dict` and
`generate_jira_config(discovered) → dict`.

The `/rai-adapter-setup` skill serializes to YAML and writes files.

**Why:** Generators are pure functions, testeable without filesystem.
Skill handles UX (confirmation prompts, file paths).

### D4: New JiraClient methods for discovery

| Method | Returns | Purpose |
|--------|---------|---------|
| `list_projects()` | `list[dict]` | Accessible projects with key, name, type |
| `get_project_workflows(project_key)` | `list[dict]` | Workflow states + transition IDs |
| `get_issue_types(project_key)` | `list[dict]` | Available issue types |

Added to `JiraClient` directly — same pattern as `ConfluenceClient.get_spaces()`.

## Key Contracts

### Discovery Service — Confluence

```python
@dataclass(frozen=True)
class ConfluenceSpaceMap:
    spaces: list[SpaceInfo]
    top_level_pages: dict[str, list[PageSummary]]  # space_key → pages

class ConfluenceDiscovery:
    def __init__(self, client: ConfluenceClient) -> None: ...
    def discover(self, space_key: str | None = None) -> ConfluenceSpaceMap: ...
```

### Discovery Service — Jira

```python
@dataclass(frozen=True)
class JiraProjectMap:
    projects: list[ProjectInfo]
    workflows: dict[str, list[WorkflowState]]  # project_key → states
    issue_types: dict[str, list[IssueTypeInfo]]  # project_key → types

class JiraDiscovery:
    def __init__(self, client: JiraClient) -> None: ...
    def discover(self, project_key: str | None = None) -> JiraProjectMap: ...
```

### Config Generator

```python
def generate_confluence_config(
    space_map: ConfluenceSpaceMap,
    selected_space: str,
    instance_url: str,
    routing: dict[str, ArtifactRouting] | None = None,
) -> dict[str, Any]: ...

def generate_jira_config(
    project_map: JiraProjectMap,
    selected_projects: list[str],
    instance_site: str,
) -> dict[str, Any]: ...
```

### Doctor Check

```python
class AdapterDoctorCheck:
    check_id = "adapters"
    category = "integrations"
    description = "Validate Jira and Confluence adapter configuration"
    requires_online = True

    def evaluate(self, context: DoctorContext) -> list[CheckResult]: ...
```

## Stories (refined)

| # | Story | Size | Builds on |
|---|-------|------|-----------|
| S1130.1 | Confluence Discovery Service | S | Existing `ConfluenceClient.get_spaces()`, `get_page_children()` |
| S1130.2 | Jira Discovery Service | M | New `JiraClient` methods: `list_projects()`, `get_project_workflows()`, `get_issue_types()` |
| S1130.3 | Adapter Doctor Check | M | Both discovery services + `DoctorCheck` Protocol |
| S1130.4 | Config Generator — Confluence | S | `ConfluenceDiscovery` + `ConfluenceConfig` model |
| S1130.5 | Config Generator — Jira | M | `JiraDiscovery` + `JiraConfig` model |
| S1130.6 | `/rai-adapter-setup` skill | S | Both generators + skill framework |

## File Locations

```
packages/raise-cli/src/raise_cli/adapters/
├── confluence_discovery.py    # S1130.1 — new
├── jira_discovery.py          # S1130.2 — new
├── config_generator.py        # S1130.4 + S1130.5 — new
├── confluence_client.py       # existing (no changes)
├── jira_client.py             # S1130.2 adds 3 methods
└── ...

packages/raise-cli/src/raise_cli/doctor/checks/
└── adapters.py                # S1130.3 — new

.claude/skills/rai-adapter-setup/
└── SKILL.md                   # S1130.6 — new
```
