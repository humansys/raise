# E494: ACLI Jira Adapter — Design

## Gemba (current state)

### What exists

`McpJiraAdapter` (437 lines) in `packages/raise-pro/src/rai_pro/adapters/mcp_jira.py`:
- Delegates all 11 protocol methods to `McpBridge` (mcp-atlassian subprocess)
- Auth via env vars: `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`
- Config from `.raise/jira.yaml` (flat schema: `workflow.status_mapping` required)
- Response parsing handles two formats: flat (sooperset) and nested (raw Jira API)
- Single Jira instance per process

### What ACLI provides

- `acli jira workitem {create,view,edit,transition,search,comment,link}` — full CRUD
- `--json` flag on all commands → raw Jira API format (nested)
- Multi-site auth via `acli jira auth login --site X` + `acli jira auth switch --site X`
- Bulk operations: `--key K1,K2,K3` or `--jql` for batch edits/transitions
- Currently authenticated: `rai-agent.atlassian.net` only

### Key finding: JSON format compatibility

ACLI `--json` output uses the **nested Jira API format** (`fields.summary`,
`fields.status.name`, `fields.issuetype.name`). This is the same format our
existing parsers already handle (`is_flat=False` branch). We can reuse:
- `_extract_issue_fields(data, is_flat=False)`
- `_parse_issue_detail()` (nested branch)
- `_parse_comments()` (nested branch)
- `_parse_search_results()` (nested branch)

## Target Components

```
packages/raise-pro/src/rai_pro/adapters/
├── mcp_jira.py          # existing — kept as jira-mcp entry point
├── acli_jira.py          # NEW — AcliJiraAdapter
└── acli_bridge.py        # NEW — _run_acli() subprocess wrapper

.raise/jira.yaml          # EXTENDED — instances section added
```

## Key Contracts

### AcliJiraBridge (acli_bridge.py)

Core subprocess wrapper. ~50 lines.

```python
class AcliJiraBridge:
    """Thin wrapper around `acli jira` subprocess calls."""

    def __init__(self, binary: str = "acli") -> None: ...

    async def call(
        self,
        subcommand: list[str],     # e.g. ["workitem", "search"]
        flags: dict[str, str],     # e.g. {"--jql": "...", "--limit": "5"}
        *,
        site: str | None = None,   # multi-instance: --site flag
    ) -> dict[str, Any]:
        """Execute acli jira <subcommand> <flags> --json, return parsed dict."""
        ...

    async def health(self, site: str | None = None) -> AdapterHealth: ...
```

Internals:
- `asyncio.create_subprocess_exec("acli", "jira", *subcommand, *flat_flags, "--json")`
- Parse stdout as JSON, stderr as error
- Logfire span: `acli.call` with command, site, latency_ms, success
- Raise `AcliBridgeError` on non-zero exit or JSON parse failure

### AcliJiraAdapter (acli_jira.py)

Implements `AsyncProjectManagementAdapter`. ~250 lines (vs 437 current).

```python
class AcliJiraAdapter:
    def __init__(self, project_root: Path | None = None) -> None:
        # Load jira.yaml → status_mapping + instances
        # Create AcliJiraBridge
        ...

    def _site_for_project(self, project_key: str) -> str | None:
        """Resolve project → instance → site URL from jira.yaml."""
        ...
```

Method mapping:

| Protocol method | ACLI command | Key flags |
|-----------------|-------------|-----------|
| `create_issue` | `workitem create` | `--project`, `--summary`, `--type`, `--label`, `--json` |
| `get_issue` | `workitem view` | `KEY`, `--fields *all`, `--json` |
| `update_issue` | `workitem edit` | `--key`, `--summary`/`--labels`/etc, `--json` |
| `transition_issue` | `workitem transition` | `--key`, `--status NAME`, `--json` |
| `batch_transition` | `workitem transition` | `--key K1,K2,K3`, `--status`, `--yes` |
| `link_to_parent` | `workitem edit` | `--key`, `--from-json` (parent field) |
| `link_issues` | `workitem link create` | `--out`, `--in`, `--type` |
| `add_comment` | `workitem comment create` | `--key`, `--body`, `--json` |
| `get_comments` | `workitem comment list` | `--key`, `--json`, `--limit` |
| `search` | `workitem search` | `--jql`, `--limit`, `--json` |
| `health` | `auth status` | (check exit code) |

### jira.yaml schema extension

```yaml
# NEW: instances section (optional — backward compatible)
instances:
  rai-agent:
    site: rai-agent.atlassian.net
  humansys:
    site: humansys.atlassian.net

# EXTENDED: projects gain instance field
projects:
  RAI:
    instance: rai-agent      # → resolves to site
    name: Rai Dev
    ...
  RAISE:
    instance: humansys       # → resolves to site
    name: RAISE
    ...

# UNCHANGED
workflow:
  status_mapping: ...
  lifecycle_mapping: ...
```

If no `instances` section → single-site mode (current behavior, backward compatible).

## Decisions

### D1: Sync subprocess, not async

ACLI is a short-lived subprocess (~200-500ms per call). Using
`asyncio.create_subprocess_exec` keeps the adapter async-compatible but the
calls are effectively sequential. No benefit from async streaming here.

### D2: Reuse existing response parsers

ACLI returns nested Jira API format. Reuse `_extract_issue_fields`,
`_parse_issue_detail`, `_parse_search_results`, `_parse_comments` from
`mcp_jira.py` — extract to shared module or inherit.

### D3: Coexist, don't replace

Register as `jira-acli` entry point alongside `jira` (MCP). Resolution
preference: if `acli` binary found in PATH → use `jira-acli`, else → `jira`.
User can force with `-a jira-acli` or `-a jira`.

### D4: Site switching via `auth switch` before calls

ACLI does NOT support `--site` per workitem command. Site switching requires
`acli jira auth switch --site X` which mutates global state (~/.config/acli/).
Strategy: track current site in adapter state, only call `auth switch` when
the target site differs from current. Risk: concurrent processes could conflict.
Mitigation: document single-process assumption, consider file lock if needed.

### D5: transition_issue uses status NAME, not transition ID

ACLI `workitem transition --status "In Progress"` resolves the transition
internally. We can simplify: pass the human-readable name, skip transition ID
lookup. The `status_mapping` in jira.yaml becomes optional for ACLI adapter.
