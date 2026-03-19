# E494: ACLI Jira Adapter — Scope

## Objective

Replace the MCP bridge-based Jira adapter with a thin ACLI subprocess wrapper that
supports multi-instance Jira, simplifies the codebase, and preserves governance and
observability.

## Value

- Users already have ACLI installed and authenticated — align adapter with their tool
- Multi-instance unlocks working across rai-agent + humansys sites from one `rai backlog`
- Eliminates MCP subprocess + async bridge complexity for basic Jira CRUD
- ACLI returns raw Jira API JSON — the nested format our parsers already handle

## In Scope (MUST)

- `AcliJiraAdapter` implementing `AsyncProjectManagementAdapter` (11 methods)
- Core `_run_acli()` — subprocess, `--json` parsing, error handling, telemetry
- Multi-instance: `jira.yaml` with `instances:` section, site switching per call
- Entry point registration as `jira-acli` (coexist with MCP adapter)
- Adapter resolution: prefer `jira-acli` when ACLI is available, fall back to MCP

## In Scope (SHOULD)

- `rai doctor` check for ACLI availability and auth status
- JQL quoting for reserved words (RAISE → 'RAISE')

## Out of Scope

- Protocol changes (`AsyncProjectManagementAdapter` stays as-is)
- Data model changes (`IssueSpec`, `IssueDetail`, etc. stay as-is)
- CLI command changes (`rai backlog` interface unchanged)
- Confluence adapter (separate epic if needed)
- ACLI installation/auth setup (prerequisite, user responsibility)
- Removing MCP adapter (kept as fallback)

## Stories

### S494.1: Spike — ACLI JSON mapping validation (XS)

Validate that ACLI `--json` output maps cleanly to existing adapter models.
No code — just a test script and documented findings.

**Dependencies:** None (foundation)

### S494.2: Core subprocess wrapper with telemetry (S)

`_run_acli(args) -> dict` — subprocess call, JSON parse, logfire span,
error handling. Single function that all protocol methods delegate to.

**Dependencies:** S494.1 findings

### S494.3: Full protocol implementation (M)

All 11 `AsyncProjectManagementAdapter` methods via ACLI commands.
Reuse existing `_to_jql()`, `_resolve_transition_id()`, response parsers
where the JSON format matches (it does — ACLI returns nested Jira API format).

**Dependencies:** S494.2

### S494.4: Multi-instance config and site switching (S)

Extend `jira.yaml` schema with `instances:` section. Adapter resolves
project → instance → site. ACLI `--site` flag or `auth switch` per call.

**Dependencies:** S494.3

### S494.5: Entry point, resolution, and migration (S)

Register `jira-acli` entry point. Update `resolve_adapter()` to prefer ACLI
when available. Docs for migration. Keep MCP adapter as `jira-mcp` fallback.

**Dependencies:** S494.4

## Done Criteria

- [ ] `rai backlog search/get/create/transition/comment` work via ACLI adapter
- [ ] Multi-instance tested: query RAISE (humansys) and RAI (rai-agent) in one session
- [ ] Logfire telemetry spans emitted per ACLI call (command, latency, success)
- [ ] Existing tests pass or migrated to ACLI adapter
- [ ] MCP adapter preserved as `jira-mcp` entry point
- [ ] `rai doctor` reports ACLI availability (SHOULD)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ACLI `--site` switching is slow (re-auth per call) | Medium | Medium | Cache auth state, batch calls per site |
| ACLI JSON output changes between versions | Low | High | Pin minimum ACLI version, test in CI |
| ACLI not installed on user machine | Medium | Low | Fallback to MCP adapter, clear error message |
