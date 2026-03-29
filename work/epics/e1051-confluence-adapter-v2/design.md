# E1051: Confluence Adapter v2 — Design

## Gemba: Current Architecture

### Adapter flow (today)
```
rai docs publish adr
  → resolve_docs_target() → SyncDocsAdapter(McpConfluenceAdapter)
    → McpConfluenceAdapter.publish()          # async
      → McpBridge.call("confluence_create_page")  # MCP stdio
        → uvx mcp-atlassian (Node subprocess)
          → Confluence REST API
```

### Adapter flow (target)
```
rai docs publish adr
  → resolve_docs_target() → PythonApiConfluenceAdapter
    → .publish()                              # sync, no wrapper needed
      → resolve routing from config
      → ConfluenceClient.get_page_by_title()  # exists?
      → ConfluenceClient.create_page() or update_page()
      → ConfluenceClient.set_labels()
      → PublishResult
```

## Architecture Review Resolutions (pre-implementation)

### C1: Protocol scope — RESOLVED
Split into two interfaces:
- **`DocumentationTarget` Protocol** (7 methods) — consumer-facing:
  publish, get_page, search, health, can_publish + `set_labels`, `get_labels`
- **`ConfluenceClient`** (concrete class, not Protocol) — implementation detail:
  get_spaces, get_page_children, get_page_by_title, create_page, update_page,
  set_labels, get_labels, search, health
  Used by discovery, doctor, setup — NOT by skills or CLI commands.

### Q1: Sync, not async — RESOLVED
`atlassian-python-api` is sync (requests). Adapter implements `DocumentationTarget`
directly (sync Protocol). No async wrapper, no SyncDocsAdapter double-wrap.
This is a departure from McpConfluenceAdapter (which was async) but proportional:
the library is sync, the CLI is sync, adding async is pure ceremony.

### Q2+Q3: Optional dependency in raise-cli — RESOLVED
- `atlassian-python-api` is an optional dependency: `raise-cli[confluence]`
- Entry point registered in `raise-cli/pyproject.toml`
- Filesystem adapter remains the default (no Confluence dep required)
- Import guarded: adapter module imports `atlassian` at class level, not module level.
  If not installed, entry point load logs warning and skips.

## Key Files

| File | Role | Change |
|------|------|--------|
| `raise-cli/adapters/protocols.py` | Protocol definitions | Add `set_labels`, `get_labels` to DocumentationTarget |
| `raise-cli/adapters/confluence_client.py` | **NEW** — client | Wraps `atlassian.Confluence`, auth resolution, error normalization |
| `raise-cli/adapters/confluence.py` | **NEW** — adapter | Implements `DocumentationTarget` (sync) using client + config routing |
| `raise-cli/adapters/confluence_config.py` | **NEW** — config models | Pydantic models for `.raise/confluence.yaml` |
| `raise-cli/adapters/confluence_discovery.py` | **NEW** — discovery | Uses client directly (not Protocol) to build space map |
| `raise-cli/doctor/checks/adapter.py` | **NEW** — doctor check | Uses client directly to validate config vs backend |
| `raise-cli/pyproject.toml` | Dependencies + entry point | Optional dep, entry point registration |
| `raise-pro/adapters/mcp_confluence.py` | Legacy adapter | No changes — preserved |

## Config Schema

```yaml
# .raise/confluence.yaml v2
default_instance: humansys

instances:
  humansys:
    url: https://humansys.atlassian.net/wiki
    username: emilio@humansys.ai
    space_key: RaiSE1
    # token from CONFLUENCE_API_TOKEN_HUMANSYS or CONFLUENCE_API_TOKEN
    routing:
      adr:
        parent_title: Architecture
        labels: [adr]
      research:
        parent_title: Research
        labels: [research]
      epic-scope:
        parent_title: Epics
        labels: [epic, scope]
```

Routing is per-instance (R2 resolution — each instance/space has its own page tree).

Backwards compat: if only `space_key` present (v1), treat as single
default instance with no routing.

## Protocol Extension (minimal)

```python
# Added to DocumentationTarget (sync) and AsyncDocumentationTarget:
def set_labels(self, page_id: str, labels: list[str]) -> None: ...
def get_labels(self, page_id: str) -> list[str]: ...
```

Only 2 new methods. Default `raise NotImplementedError` — existing adapters don't break.

## ConfluenceClient (concrete, not Protocol)

```python
class ConfluenceClient:
    """Wraps atlassian.Confluence with auth resolution and error normalization.

    NOT a Protocol — consumed directly by adapter, discovery, doctor.
    """
    def __init__(self, config: ConfluenceInstanceConfig) -> None: ...

    # Publishing
    def create_page(self, space: str, title: str, body: str, parent_id: str | None) -> PageContent: ...
    def update_page(self, page_id: str, title: str, body: str) -> PageContent: ...
    def get_page_by_id(self, page_id: str) -> PageContent: ...
    def get_page_by_title(self, space: str, title: str) -> PageContent | None: ...

    # Labels
    def set_labels(self, page_id: str, labels: list[str]) -> None: ...
    def get_labels(self, page_id: str) -> list[str]: ...

    # Discovery
    def get_spaces(self) -> list[SpaceInfo]: ...
    def get_page_children(self, page_id: str) -> list[PageSummary]: ...

    # Search & Health
    def search(self, cql: str, limit: int = 10) -> list[PageSummary]: ...
    def health(self) -> AdapterHealth: ...
```

## Auth Resolution

```
1. Read instance config: url + username
2. Token: CONFLUENCE_API_TOKEN_{INSTANCE_NAME_UPPER}
3. Fallback: CONFLUENCE_API_TOKEN
4. If neither: ImportError-style message → "pip install raise-cli[confluence]"
   or "set CONFLUENCE_API_TOKEN" depending on what's missing
```

## Registry Wiring

```toml
# raise-cli/pyproject.toml
[project.optional-dependencies]
confluence = ["atlassian-python-api>=3.41"]

[project.entry-points."rai.docs.targets"]
confluence = "raise_cli.adapters.confluence:PythonApiConfluenceAdapter"
```

Entry point load is guarded — if `atlassian-python-api` not installed,
`ep.load()` raises ImportError, registry logs warning and skips.
Filesystem adapter remains default.

## Function Map (validated against ADR-014)

### Protocol methods (7 — consumer-facing)
| # | Method | New | Consumer |
|---|--------|:---:|----------|
| 1 | `publish(doc_type, content, metadata)` | No | `rai docs publish`, skills |
| 2 | `get_page(identifier)` | No | `rai docs get` |
| 3 | `search(query, limit)` | No | `rai docs search` |
| 4 | `health()` | No | `rai adapter check` |
| 5 | `can_publish(doc_type, metadata)` | No | Sync wrapper |
| 6 | `set_labels(page_id, labels)` | Yes | Skills, publish routing |
| 7 | `get_labels(page_id)` | Yes | Doctor, discovery |

### Client methods (10 — implementation detail)
| # | Method | Consumer |
|---|--------|----------|
| 1 | `create_page(space, title, body, parent_id)` | Adapter (publish), setup |
| 2 | `update_page(page_id, title, body)` | Adapter (publish) |
| 3 | `get_page_by_id(page_id)` | Adapter (get_page) |
| 4 | `get_page_by_title(space, title)` | Adapter (routing) |
| 5 | `set_labels(page_id, labels)` | Adapter, skills |
| 6 | `get_labels(page_id)` | Doctor, discovery |
| 7 | `get_spaces()` | Discovery, setup |
| 8 | `get_page_children(page_id)` | Discovery, doctor |
| 9 | `search(cql, limit)` | Adapter (search) |
| 10 | `health()` | Adapter (health) |

## Design References

- ADR-014: `governance/adrs/v2/adr-014-atlassian-transport-backend.md`
- Adapter Vision: `governance/product/adapter-vision.md` §3
- RAISE-830 (Done): functional spec for ported features
- Current MCP adapter: `packages/raise-pro/src/rai_pro/adapters/mcp_confluence.py`
- Protocol: `packages/raise-cli/src/raise_cli/adapters/protocols.py`
- Sync wrapper: `packages/raise-cli/src/raise_cli/adapters/sync.py`
