# Epic Scope: E337 — Declarative MCP Adapter Framework

## Objective

Enable integration of any MCP server via declarative YAML config (~50-80 lines) instead of dedicated Python adapter code (~400 LOC), while keeping existing adapters unchanged.

## In Scope

- Mini expression evaluator (dot-access, type coercion, default, pluck, json filters)
- Pydantic models for YAML adapter config validation
- Generic `DeclarativeMcpAdapter` class implementing PM protocol via YAML mapping
- YAML discovery in adapter registry (`.raise/adapters/*.yaml`)
- Docs protocol support extension
- CLI validation command (`rai adapter validate`)
- Reference config (github.yaml or linear.yaml as example)

## Out of Scope

- Auto-discovery of MCP tools (Level 3 — future)
- Jinja2 or complex template engine
- Changes to existing adapters (Jira, Confluence, Filesystem)
- Changes to McpBridge
- MCP server installation/management
- UI for adapter creation

## Planned Stories

| # | Story | Size | Depends On |
|---|-------|------|------------|
| S337.1 | Expression evaluator | S | — |
| S337.2 | YAML schema models | S | S337.1 |
| S337.3 | DeclarativeMcpAdapter (PM) | M | S337.2 |
| S337.4 | YAML discovery in registry | S | S337.3 |
| S337.5 | Docs protocol support | S | S337.3 |
| S337.6 | CLI validation command | XS | S337.3 |
| S337.7 | Reference config + docs | XS | S337.3 |

## Done Criteria

- [ ] Any MCP server can be integrated via YAML config
- [ ] `rai backlog --adapter <name>` works with YAML-defined adapters
- [ ] Existing adapters (Jira, Confluence, Filesystem) unaffected
- [ ] All new code has unit + integration tests
- [ ] Reference config demonstrates real-world usage
