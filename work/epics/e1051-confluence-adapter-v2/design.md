# E1051: Confluence Adapter v2 — Design

## Gemba: Current Architecture

### Adapter flow (today)
```
rai docs publish adr
  → resolve_docs_target() → SyncDocsAdapter(McpConfluenceAdapter)
    → McpConfluenceAdapter.publish()
      → McpBridge.call("confluence_create_page", {...})
        → uvx mcp-atlassian (Node subprocess, MCP stdio)
          → Confluence REST API
```

### Adapter flow (target)
```
rai docs publish adr
  → resolve_docs_target() → SyncDocsAdapter(PythonApiConfluenceAdapter)
    → PythonApiConfluenceAdapter.publish()
      → resolve routing from config (adr → parent "Architecture", labels [adr])
      → ConfluenceClient.get_page_by_title(space, title)  # exists?
      → ConfluenceClient.create_page() or update_page()
      → ConfluenceClient.set_labels()
      → PublishResult
```

### Key files

| File | Role | Change |
|------|------|--------|
| `raise-cli/adapters/protocols.py` | Protocol definitions | Extend AsyncDocumentationTarget with 6 new methods |
| `raise-cli/adapters/confluence_client.py` | **NEW** — client wrapper | 11 methods over atlassian-python-api |
| `raise-cli/adapters/confluence.py` | **NEW** — adapter | Implements AsyncDocumentationTarget |
| `raise-cli/adapters/confluence_config.py` | **NEW** — config models | Pydantic models for .raise/confluence.yaml |
| `raise-cli/adapters/confluence_discovery.py` | **NEW** — discovery | Space map builder |
| `raise-cli/doctor/checks/adapter.py` | **NEW** — doctor check | Confluence config validation |
| `raise-pro/adapters/mcp_confluence.py` | Legacy adapter | No changes — preserved |
| `raise-pro/adapters/__init__.py` | Entry point | Add new adapter registration |

### Config schema

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

Backwards compat: if only `space_key` present (v1), treat as single
default instance with no routing.

### Protocol extension

```python
# New methods added to AsyncDocumentationTarget
async def set_labels(self, page_id: str, labels: list[str]) -> None: ...
async def get_labels(self, page_id: str) -> list[str]: ...
async def get_page_children(self, page_id: str) -> list[PageSummary]: ...
async def get_spaces(self) -> list[SpaceInfo]: ...
async def get_page_by_title(self, space_key: str, title: str) -> PageContent | None: ...
async def create_page(self, space_key: str, title: str, body: str, parent_id: str | None = None) -> PageContent: ...
```

New methods have default `raise NotImplementedError` in Protocol —
existing adapters (McpConfluence, Filesystem) don't break.

### Auth resolution

```
1. Check instance config for username + url
2. Token: CONFLUENCE_API_TOKEN_{INSTANCE_NAME_UPPER}
3. Fallback: CONFLUENCE_API_TOKEN
4. If neither: error with actionable message → "run /rai-adapter-setup"
```

### Registry wiring

New adapter registered via entry point in `raise-cli/pyproject.toml`:
```toml
[project.entry-points."rai.docs"]
confluence = "raise_cli.adapters.confluence:PythonApiConfluenceAdapter"
```

McpConfluenceAdapter remains registered in raise-pro. Selection via
`--target` flag or config preference.
