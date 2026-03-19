# E494: ACLI Jira Adapter — Scope

## Objective

Replace the MCP bridge-based Jira adapter with a light ACLI wrapper that supports
multi-instance Jira, simplifies the codebase, and preserves governance/observability.

## In Scope

- New `AcliJiraAdapter` implementing `AsyncProjectManagementAdapter`
- Core `_run_acli()` subprocess wrapper with JSON parsing and telemetry
- Multi-instance support via ACLI auth switching (`--site` flag)
- Updated `jira.yaml` schema supporting `instances:` section
- Migration path from current MCP adapter to ACLI adapter
- Entry point registration alongside (or replacing) MCP adapter

## Out of Scope

- Changes to `AsyncProjectManagementAdapter` protocol
- Changes to adapter data models (IssueSpec, IssueDetail, etc.)
- Changes to CLI commands (`rai backlog`)
- Confluence adapter (separate concern)
- ACLI installation/auth setup (user responsibility)

## Planned Stories (provisional — refined in epic-design)

1. Spike: validate ACLI JSON output maps to existing models
2. Core `_run_acli()` wrapper with telemetry
3. Implement full protocol (11 methods) via ACLI
4. Multi-instance config and site switching
5. Migration and entry point registration

## Done Criteria

- [ ] `rai backlog` commands work with ACLI adapter
- [ ] Multi-instance Jira tested (rai-agent + humansys)
- [ ] Telemetry spans emitted for each ACLI call
- [ ] Existing tests pass or are migrated
- [ ] MCP adapter preserved as fallback option
