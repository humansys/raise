# E1051: Confluence Adapter v2

## Objective

Port Confluence adapter from mcp-atlassian (MCP stdio, Node dependency) to
atlassian-python-api (pure Python). Include backend discovery, config schema
with artifact-type routing, and adapter doctor — making Confluence integration
reliable from setup to daily use.

## In Scope

1. **PythonApiConfluenceAdapter** — implement DocumentationTarget protocol using
   `atlassian.Confluence` class from atlassian-python-api
2. **Port RAISE-830 features** — labels, artifact-type routing, index auto-gen,
   archive hook, templates, batch page tree creation
3. **Confluence Backend Discovery** — query spaces, page trees, templates, labels.
   Produce structured space map.
4. **Config Schema (`.raise/confluence.yaml`)** — artifact-type routing, parent
   pages, templates, label conventions
5. **Adapter Doctor (Confluence)** — validate config against live backend, report
   mismatches, suggest fixes
6. **Config Generator** — `/rai-adapter-setup` Confluence portion

## Out of Scope

- McpConfluenceAdapter removal (stays as legacy)
- Jira adapter (RAISE-1052)
- Content properties / attachments (RAISE-834)
- Multi-space routing
- Server/DC support (Cloud only for now)

## Done Criteria

- PythonApiConfluenceAdapter passes all existing Confluence adapter tests
- `rai docs publish adr` routes to correct parent page with labels from config
- `rai adapter doctor` detects Confluence config-vs-backend mismatches
- `.raise/confluence.yaml` generated from discovery matches live space structure
- McpConfluenceAdapter still works (not broken by this work)

## Design References

- ADR-014: `governance/adrs/v2/adr-014-atlassian-transport-backend.md`
- Adapter Vision: `governance/product/adapter-vision.md` §3
- RAISE-830 (Done): functional spec for features to port
- Existing MCP adapter: `packages/raise-pro/src/rai_pro/adapters/mcp_confluence.py`
- atlassian-python-api Confluence: https://github.com/atlassian-api/atlassian-python-api
