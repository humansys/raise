# Epic Design: E337 — Declarative MCP Adapter Framework

> Architecture: ADR-041 | Research: `dev/research/declarative-mcp-adapter-design.md`
> Architecture Review: PASS WITH QUESTIONS (all resolved — see scope.md AR-* table)

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
_resolve.py           → Generic resolver: discover → select → instantiate → wrap
```

**Pain point:** Each new MCP adapter duplicates the same pattern: create bridge → build args → call tool → parse response → return model. `McpJiraAdapter` is 410 LOC of this plumbing.

### What Changes

```
NEW: src/rai_cli/adapters/declarative/
  __init__.py              → Public API
  expressions.py           → ExpressionEvaluator (~100 LOC)
  schema.py                → Pydantic config models (~80 LOC)
  adapter.py               → DeclarativeMcpAdapter (~200 LOC)

MODIFIED: src/rai_cli/cli/commands/_resolve.py
  + discover_yaml_adapters() → scans .raise/adapters/*.yaml
  + merge YAML results into entry point results (entry points take priority)
  (AR-Q2: here, NOT in registry.py — keeps stable core untouched)

UNCHANGED: registry.py, mcp_bridge.py, protocols.py, models.py, sync.py,
           mcp_jira.py, mcp_confluence.py, filesystem.py
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
    env: list[str] | None = None          # env var names to pass to subprocess
                                          # (AR-R2: simple list, not env→flag mapping)

class MethodMapping(BaseModel):
    tool: str                             # MCP tool name
    args: dict[str, str]                  # template expressions for args
    response: ResponseMapping | None      # how to parse response

class ResponseMapping(BaseModel):
    # (AR-R1: no `model` field — adapter infers return type from method name)
    fields: dict[str, str]                # field → expression mapping
    items_path: str | None = None         # dot-path to list in response

class DeclarativeAdapterConfig(BaseModel):
    adapter: AdapterMeta                  # name, protocol, description
    server: ServerConfig
    methods: dict[str, MethodMapping | None]  # None = unsupported
```

### 3. DeclarativeMcpAdapter (`adapter.py`)

Generic class instantiated from YAML config. Implements both `AsyncProjectManagementAdapter` and `AsyncDocumentationTarget` based on `adapter.protocol` (AR-Q1: one class, dispatch table).

**Key design:**
- One class handles both PM and Docs protocols (AR-Q1)
- `adapter.protocol` field determines which methods are expected
- `@runtime_checkable` isinstance() validates protocol compliance
- Methods declared as `null` in YAML → `NotImplementedError`
- `batch_transition` auto-loops over `transition_issue` if not explicitly declared
- Single shared `McpBridge` per adapter lifetime (AR-C2)

**Contract:**
```python
class DeclarativeMcpAdapter:
    def __init__(self, config: DeclarativeAdapterConfig, project_root: Path | None = None): ...
    # All 11 PM methods + 5 Docs methods, dispatched via config.methods
    async def aclose(self) -> None: ...  # delegates to bridge.aclose()
```

### 4. Discovery in Resolver (`_resolve.py`)

Discovery goes in `_resolve.py`, NOT in `registry.py` (AR-Q2: keeps stable core untouched).

```python
def discover_yaml_adapters(protocol: str) -> dict[str, Callable[[], Any]]:
    """Scan .raise/adapters/*.yaml, return factory closures keyed by adapter name.

    Each closure captures the parsed config and returns a new DeclarativeMcpAdapter
    when called with no arguments (AR-C1: compatible with resolve_entrypoint).
    """
    ...

def resolve_adapter(adapter_name: str | None) -> ProjectManagementAdapter:
    return resolve_entrypoint(
        discover=lambda: {**get_pm_adapters(), **discover_yaml_adapters("pm")},
        ...
    )
```

**Note:** `resolve_entrypoint` currently types `discover` as `Callable[[], dict[str, type]]`. The YAML factories are closures, not types. Either relax the type to `Callable[[], dict[str, Callable[[], Any]]]` or keep `type` and use `type(...)` trick. Resolve during S337.3 implementation.

## Key Contracts

| Interface | Consumer | Provider |
|-----------|----------|----------|
| `AsyncProjectManagementAdapter` | `SyncPMAdapter` → CLI commands | `DeclarativeMcpAdapter` (new) |
| `AsyncDocumentationTarget` | `SyncDocsAdapter` → CLI commands | `DeclarativeMcpAdapter` (new) |
| `McpBridge.call()` | `DeclarativeMcpAdapter` | `McpBridge` (unchanged) |
| `_resolve.py` discover functions | `resolve_adapter()`, `resolve_docs_target()` | Entry points + YAML discovery |

## YAML Config Example (GitHub, post-AR)

```yaml
adapter:
  name: github
  protocol: pm
  description: "GitHub Issues via mcp-github"

server:
  command: uvx
  args: [mcp-github]
  env: [GITHUB_TOKEN]            # AR-R2: simple list

methods:
  create_issue:
    tool: github_create_issue
    args:
      title: "{{ issue.summary }}"
      body: "{{ issue.description }}"
      repo: "{{ project_key }}"
    response:                      # AR-R1: no `model` field
      fields:
        key: "{{ data.number | str }}"
        url: "{{ data.html_url }}"

  search:
    tool: github_search_issues
    args:
      query: "{{ query }}"
      per_page: "{{ limit }}"
    response:
      items_path: data.items
      fields:
        key: "{{ item.number | str }}"
        summary: "{{ item.title }}"
        status: "{{ item.state }}"

  # Unsupported methods
  link_to_parent: null
  link_issues: null
```

## Dependency Graph (post-AR, 5 stories)

```
S337.1 (Expression evaluator + YAML schema)    [S]
  └── S337.2 (DeclarativeMcpAdapter PM)         [M]
        ├── S337.3 (YAML discovery in resolver)  [S]
        │     └── S337.5 (Reference config + validation CLI)  [S]
        └── S337.4 (Docs protocol support)       [S]
```
