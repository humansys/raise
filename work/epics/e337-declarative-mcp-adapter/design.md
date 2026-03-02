# Epic Design: E337 — Declarative MCP Adapter Framework

> Architecture: ADR-041 | Research: `dev/research/declarative-mcp-adapter-design.md`

## Gemba: Current State

### Adapter Architecture (post-E301)

```
protocols.py          → AsyncProjectManagementAdapter (11 methods)
                      → AsyncDocumentationTarget (5 methods)
models.py             → IssueRef, IssueDetail, IssueSummary, etc. (shared boundary models)
mcp_bridge.py         → McpBridge (generic async MCP client, lazy connect, telemetry)
mcp_jira.py           → McpJiraAdapter (~410 LOC, maps protocol → jira_* tools)
mcp_confluence.py     → McpConfluenceTarget (~similar pattern)
filesystem.py         → FilesystemPMAdapter (local JSON files)
sync.py               → SyncPMAdapter / SyncDocsAdapter wrappers
registry.py           → Entry point discovery (rai.adapters.pm, rai.docs.targets)
```

**Pain point:** Each new MCP adapter duplicates the same pattern: create bridge → build args → call tool → parse response → return model. `McpJiraAdapter` is 410 LOC of this plumbing.

### What Changes

```
NEW: src/rai_cli/adapters/declarative/
  __init__.py              → Public API
  expressions.py           → ExpressionEvaluator (~100 LOC)
  schema.py                → Pydantic config models (~80 LOC)
  adapter.py               → DeclarativeMcpAdapter (~200 LOC)

MODIFIED: src/rai_cli/adapters/registry.py
  + _discover_yaml_adapters() → scans .raise/adapters/*.yaml
  + merge into get_pm_adapters() / get_doc_targets() (entry points take priority)

UNCHANGED: mcp_bridge.py, protocols.py, models.py, sync.py, mcp_jira.py, mcp_confluence.py, filesystem.py
```

## Target Components

### 1. ExpressionEvaluator (`expressions.py`)

Minimal template engine. No external dependencies.

**Supported syntax:**
- `{{ param }}` — parameter substitution
- `{{ obj.field }}` — dot-access into dicts/objects
- `{{ value | str }}` — type coercion to string
- `{{ value | default('fallback') }}` — fallback for None/missing
- `{{ items | pluck('name') }}` — extract field from list of dicts
- `{{ value | json }}` — JSON serialize
- Literals (no `{{ }}`) — passthrough

**Contract:**
```python
class ExpressionEvaluator:
    def evaluate(self, template: str, context: dict[str, Any]) -> Any: ...
    def evaluate_args(self, args: dict[str, str], context: dict[str, Any]) -> dict[str, Any]: ...
```

### 2. DeclarativeAdapterConfig (`schema.py`)

Pydantic models validating YAML structure.

```python
class ServerConfig(BaseModel):
    command: str                          # e.g. "uvx"
    args: list[str]                       # e.g. ["mcp-github"]
    env: list[EnvMapping] | None = None   # env var → CLI flag mapping

class MethodMapping(BaseModel):
    tool: str                             # MCP tool name
    args: dict[str, str]                  # template expressions for args
    response: ResponseMapping | None      # how to parse response

class ResponseMapping(BaseModel):
    model: str                            # target Pydantic model name
    fields: dict[str, str]                # field → expression mapping
    items_path: str | None = None         # dot-path to list in response

class DeclarativeAdapterConfig(BaseModel):
    adapter: AdapterMeta                  # name, protocol, description
    server: ServerConfig
    methods: dict[str, MethodMapping | None]  # None = unsupported
```

### 3. DeclarativeMcpAdapter (`adapter.py`)

Generic class instantiated from YAML config. Implements `AsyncProjectManagementAdapter` and/or `AsyncDocumentationTarget` based on `adapter.protocol`.

**Key design:**
- One class handles both PM and Docs protocols
- `adapter.protocol` field determines which methods are expected
- `@runtime_checkable` isinstance() validates protocol compliance
- Methods declared as `null` in YAML → `NotImplementedError`
- `batch_transition` auto-loops over `transition_issue` if not explicitly declared

**Contract:**
```python
class DeclarativeMcpAdapter:
    def __init__(self, config: DeclarativeAdapterConfig, project_root: Path | None = None): ...
    # All 11 PM methods + 5 Docs methods, dispatched via config.methods
```

### 4. Registry Extension (`registry.py`)

```python
def _discover_yaml_adapters(protocol: str) -> dict[str, type]:
    """Scan .raise/adapters/*.yaml, return factory functions keyed by adapter name."""

def get_pm_adapters() -> dict[str, type]:
    result = _discover(EP_PM_ADAPTERS)       # entry points first (priority)
    yaml_adapters = _discover_yaml_adapters("pm")
    for name, cls in yaml_adapters.items():
        if name not in result:               # entry points override
            result[name] = cls
    return result
```

## Key Contracts

| Interface | Consumer | Provider |
|-----------|----------|----------|
| `AsyncProjectManagementAdapter` | `SyncPMAdapter` → CLI commands | `DeclarativeMcpAdapter` (new) |
| `AsyncDocumentationTarget` | `SyncDocsAdapter` → CLI commands | `DeclarativeMcpAdapter` (new) |
| `McpBridge.call()` | `DeclarativeMcpAdapter` | `McpBridge` (unchanged) |
| `registry.get_pm_adapters()` | `backlog` CLI group | `registry.py` (extended) |

## YAML Config Example (GitHub)

```yaml
adapter:
  name: github
  protocol: pm
  description: "GitHub Issues via mcp-github"

server:
  command: uvx
  args: [mcp-github]
  env:
    - env: GITHUB_TOKEN
      flag: --token

methods:
  create_issue:
    tool: github_create_issue
    args:
      title: "{{ issue.summary }}"
      body: "{{ issue.description }}"
      repo: "{{ project_key }}"
    response:
      model: IssueRef
      fields:
        key: "{{ data.number | str }}"
        url: "{{ data.html_url }}"

  search:
    tool: github_search_issues
    args:
      query: "{{ query }}"
      per_page: "{{ limit }}"
    response:
      model: list[IssueSummary]
      items_path: data.items
      fields:
        key: "{{ item.number | str }}"
        summary: "{{ item.title }}"
        status: "{{ item.state }}"

  # Unsupported methods
  link_to_parent: null
  link_issues: null
```

## Dependency Graph

```
S337.1 (Expression evaluator)
  └── S337.2 (YAML schema models)
        └── S337.3 (DeclarativeMcpAdapter PM)
              ├── S337.4 (YAML discovery in registry)
              │     └── S337.7 (Reference config + docs)
              ├── S337.5 (Docs protocol support)
              └── S337.6 (CLI validation command)
```
