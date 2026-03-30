---
epic_id: "RAISE-1051"
title: "Confluence Adapter v2"
status: "draft"
created: "2026-03-29"
---

# Epic Brief: Confluence Adapter v2

## Hypothesis
For RaiSE developers who need reliable documentation publishing,
the PythonApiConfluenceAdapter is a pure-Python adapter
that eliminates MCP/Node dependencies and adds discovery + config validation.
Unlike McpConfluenceAdapter (MCP stdio, 5/11 functions, no config schema),
our solution covers 11/11 functions with generated config and doctor validation.

## Success Metrics
- **Leading:** `rai docs publish adr` routes correctly from generated config on first try
- **Lagging:** Zero Confluence adapter failures caused by config or transport issues

## Appetite
M — 5-7 stories

## Scope Boundaries
### In (MUST)
- PythonApiConfluenceAdapter implementing full DocumentationTarget protocol
- All RAISE-830 features on new transport (labels, routing, index, templates, batch)
- Confluence backend discovery (spaces, page trees, templates, labels)
- `.raise/confluence.yaml` config schema (artifact-type routing, parent pages, labels)
- Adapter doctor for Confluence (validate config vs live backend)

### In (SHOULD)
- `/rai-adapter-setup` Confluence portion (interactive config generation)
- Telemetry events per operation

### No-Gos
- Removing McpConfluenceAdapter (preserved as legacy)
- Jira adapter work (that's RAISE-1052)
- Content properties / attachment support (RAISE-834)
- Multi-space routing (one space per repo is sufficient for v2.4)

### Rabbit Holes
- Building a full Confluence IA planner — discover and map, don't redesign
- Supporting Server/DC from day one — Cloud first, DC later
- Template creation — use existing templates, don't create the template engine
