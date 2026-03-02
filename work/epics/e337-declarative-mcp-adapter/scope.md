# Epic Scope: E337 — Declarative MCP Adapter Framework

## Objective

Enable integration of any MCP server via declarative YAML config (~50-80 lines) instead of dedicated Python adapter code (~400 LOC), while keeping existing adapters unchanged.

**Value:** Unblocks GitHub, Linear, GitLab integrations without framework developer effort. Users write YAML, not Python.

## In Scope (MUST)

- Mini expression evaluator (dot-access, type coercion, default, pluck, json filters)
- Pydantic models for YAML adapter config validation
- Generic `DeclarativeMcpAdapter` class implementing PM protocol via YAML mapping
- YAML discovery in adapter registry (`.raise/adapters/*.yaml`)
- CLI validation command (`rai adapter validate`)

## In Scope (SHOULD)

- Docs protocol support extension (`AsyncDocumentationTarget`)
- Reference config (github.yaml as working example)

## Out of Scope

| Item | Rationale | Deferred To |
|------|-----------|-------------|
| Auto-discovery of MCP tools (Level 3) | Premature — Level 2 covers 80% | Future epic |
| Jinja2 or complex template engine | 4 filters suffice, zero deps | Extend evaluator if needed |
| Changes to existing adapters | Not needed — entry points have priority | N/A |
| Changes to McpBridge | Already stable (E301) | N/A |
| MCP server installation/management | Orthogonal concern | Toolchain epic |

## Stories

| # | Story | Size | Description | Depends On |
|---|-------|------|-------------|------------|
| S337.1 | Expression evaluator | S | `ExpressionEvaluator` class: `{{ var }}`, dot-access, 4 filters (`str`, `default`, `pluck`, `json`), ~100 LOC | — |
| S337.2 | YAML schema models | S | `DeclarativeAdapterConfig` Pydantic models: adapter/server/methods sections, validation | S337.1 |
| S337.3 | DeclarativeMcpAdapter (PM) | M | Generic adapter class implementing all 11 `AsyncProjectManagementAdapter` methods via YAML mapping + McpBridge | S337.2 |
| S337.4 | YAML discovery in registry | S | `_discover_yaml_adapters()` in registry.py, merge with entry point discovery, integration tests | S337.3 |
| S337.5 | Docs protocol support | S | Extend adapter for `AsyncDocumentationTarget` (5 methods: can_publish, publish, get_page, search, health) | S337.3 |
| S337.6 | CLI validation command | XS | `rai adapter validate <file>` — parse YAML, validate schema, report errors | S337.3 |
| S337.7 | Reference config + docs | XS | Working `github.yaml` with documentation, adapter authoring guide | S337.4 |

**Critical path:** S337.1 → S337.2 → S337.3 → S337.4 → S337.7
**Parallel after S337.3:** S337.5, S337.6

## Done Criteria

- [ ] Any MCP server can be integrated via YAML config (validated by reference config)
- [ ] `rai backlog --adapter <name>` works with YAML-defined adapter
- [ ] `rai adapter validate` catches invalid configs with clear errors
- [ ] Existing adapters (Jira, Confluence, Filesystem) unaffected (regression test)
- [ ] All new code has unit + integration tests
- [ ] ADR-041 accepted and referenced

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Expression evaluator insufficient for edge cases | Low | Medium | `| json` filter as escape hatch; extend evaluator incrementally |
| MCP server response format varies unpredictably | Medium | Medium | `items_path` + `fields` mapping handle nesting; fallback to raw bridge |
| Registry collision between YAML and entry point names | Low | Low | Entry points have priority (D4); warn on collision |
