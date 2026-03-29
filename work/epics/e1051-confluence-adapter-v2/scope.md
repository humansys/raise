# E1051: Confluence Adapter v2

## Objective

Port Confluence adapter from mcp-atlassian (MCP stdio, Node dependency) to
atlassian-python-api (pure Python). Include backend discovery, config schema
with artifact-type routing, and adapter doctor — making Confluence integration
reliable from setup to daily use.

## Design Decisions

1. **Open-core** — adapter lives in `raise-cli`, same level as filesystem adapter
2. **API token auth** — url + username in config, token from env var (`CONFLUENCE_API_TOKEN`)
3. **Multi-instance** — same pattern as jira.yaml (default_instance + instances map)
4. **Config schema** — instances + routing per-instance (artifact-type → parent_title + labels)
5. **No local cache** — API is source of truth for page existence (no confluence-pages.yaml)
6. **Sync adapter** — implements `DocumentationTarget` directly (no async wrapper)
7. **Optional dependency** — `raise-cli[confluence]` for atlassian-python-api; filesystem is default
8. **Protocol minimal** — only 2 new Protocol methods (set_labels, get_labels); discovery/admin
   methods stay on ConfluenceClient (concrete class, not Protocol)

## Stories

### S1051.1: Confluence client wrapper (M)
Wrapper over `atlassian.Confluence` with API token auth, multi-instance support,
error normalization. 10 methods (concrete class, not Protocol). In `raise-cli/adapters/`.
Optional dependency (`raise-cli[confluence]`). Tests with mocks.

### S1051.2: PythonApiConfluenceAdapter (M)
Implements `DocumentationTarget` (sync, not async) using client from S1051.1.
Publish with routing from config. Entry point in raise-cli. Filesystem remains default.

### S1051.3: Config schema + Pydantic models (S)
`.raise/confluence.yaml` with instances, routing, labels. Pydantic models.
Validation. Backwards compat with v1 schema (just `space_key`).

### S1051.4: Confluence discovery service (S)
Query spaces, page trees, labels. Produce structured space map.
Foundation for doctor and setup skill.

### S1051.5: Adapter doctor — Confluence (S)
Validate config vs live backend. Integrate into existing `rai doctor`.
Report mismatches with actionable suggestions.

### S1051.6: Config generator — `/rai-adapter-setup` Confluence (M)
Interactive skill: discovery → present → human selects → generate valid YAML.

## Dependencies

```
S1051.1 Client wrapper ──┐
                         ├──→ S1051.2 Adapter
S1051.3 Config schema ───┘        │
                                  ↓
                           S1051.4 Discovery
                                  │
                         ┌────────┴────────┐
                         ↓                 ↓
                  S1051.5 Doctor    S1051.6 Generator
```

S1051.1 and S1051.3 can run in parallel.

## In Scope

1. Confluence client wrapper (11 methods over atlassian-python-api)
2. PythonApiConfluenceAdapter implementing full AsyncDocumentationTarget
3. Config schema with multi-instance + artifact-type routing
4. Backend discovery service
5. Adapter doctor (Confluence checks)
6. Config generator skill

## Out of Scope

- McpConfluenceAdapter removal (preserved as legacy)
- Jira adapter (RAISE-1052)
- Content properties / attachments (RAISE-834)
- Multi-space routing (one space per instance)
- Server/DC support (Cloud only for now)
- Templates (deferred — low usage, high complexity)
- Index auto-generation (skill concern, not adapter)
- Archive hook (hook concern, not adapter)

## Done Criteria

1. `rai docs publish adr` works with PythonApiConfluenceAdapter + routing from config
2. `rai docs get` and `rai docs search` work via new adapter
3. `rai adapter check` reports healthy for Confluence via new adapter
4. `rai doctor` includes Confluence config-vs-backend validation
5. `/rai-adapter-setup` generates valid `.raise/confluence.yaml` from discovery
6. McpConfluenceAdapter still works (not removed)
7. All existing Confluence adapter tests pass on new adapter
8. Zero Node/MCP dependencies for Confluence

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| atlassian-python-api Cloud behavior differs from expected | Medium | High | S1051.1 validates all 11 methods against live backend first |
| Config migration breaks existing setups | Low | High | S1051.3 includes backwards compat — v1 schema still works |
| Registry wiring breaks raise-pro | Medium | Medium | New adapter registered as alternative, toggle via config |

## Function Map (validated against ADR-014)

| # | Method | New | Backed by (atlassian-python-api) |
|---|--------|:---:|----------------------------------|
| 1 | `publish(doc_type, content, metadata)` | No | `create_page` / `update_page` + routing |
| 2 | `get_page(identifier)` | No | `get_page_by_id` |
| 3 | `search(query, limit)` | No | `cql` |
| 4 | `health()` | No | `get_all_spaces(limit=1)` |
| 5 | `can_publish(doc_type, metadata)` | No | Config check |
| 6 | `set_labels(page_id, labels)` | Yes | `set_page_label` |
| 7 | `get_labels(page_id)` | Yes | `get_page_labels` |
| 8 | `get_page_children(page_id)` | Yes | `get_child_pages` |
| 9 | `get_spaces()` | Yes | `get_all_spaces` |
| 10 | `get_page_by_title(space, title)` | Yes | `get_page_by_title` |
| 11 | `create_page(space, title, body, parent_id)` | Yes | `create_page` |

## Design References

- ADR-014: `governance/adrs/v2/adr-014-atlassian-transport-backend.md`
- Adapter Vision: `governance/product/adapter-vision.md` §3
- RAISE-830 (Done): functional spec for ported features
- Current MCP adapter: `packages/raise-pro/src/rai_pro/adapters/mcp_confluence.py`
- Protocol: `packages/raise-cli/src/raise_cli/adapters/protocols.py`
