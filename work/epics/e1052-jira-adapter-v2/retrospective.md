# E1052: Jira Adapter v2 — Epic Retrospective

## Summary

| Field | Value |
|-------|-------|
| **Epic** | E1052 |
| **Started** | 2026-03-31 |
| **Completed** | 2026-03-31 |
| **Stories planned** | 6 |
| **Stories delivered** | 5 (S1052.4 absorbed into S1052.5) |
| **Total tests** | 4,506 (120+ new) |
| **LOC net** | -7,729 |

## Delivered

1. **JiraClient** — 11 methods wrapping atlassian-python-api, auth from env, error normalization, multi-instance
2. **JiraConfig** — Pydantic model for jira.yaml, backwards compat, instance routing
3. **PythonApiJiraAdapter** — 11 AsyncProjectManagementAdapter methods, entry point in raise-cli
4. **Integration tests** — 9 E2E tests against live Jira Cloud (6 adapter + 3 client)
5. **Architecture module doc** — governance/architecture/modules/jira-adapter.md
6. **Massive cleanup** — deleted AcliJiraAdapter, AcliJiraBridge, providers/jira/ (7 files), JiraSyncHook, BacklogHook, legacy tests and docs

## Deleted (legacy)

- AcliJiraAdapter + AcliJiraBridge (raise-pro) — 627 LOC
- providers/jira/ sync engine (raise-pro) — 1,633 LOC
- JiraSyncHook (raise-pro) — 127 LOC
- BacklogHook (raise-cli) — 216 LOC
- Legacy tests — 5,383 LOC
- Legacy docs — 2 guide files

## What Went Well

- **E2E testing caught real bugs** — transition_issue and JQL quoting bugs invisible to mocks
- **Pattern replication saved ~40% time** — ConfluenceClient → JiraClient was mechanical
- **Interactive design process** — 6 decisions pre-approved at epic level, zero rework
- **ADR-015 validated** — epic fit in one session, worktree isolation worked
- **Aggressive cleanup** — -7,729 LOC net; less code, same functionality

## What Could Improve

- **Worktree base branch** — created from v2.3.0 instead of release/2.4.0, required mid-session rebase
- **E2E should run earlier** — integration tests were originally last; advancing them caught bugs sooner
- **Env var discovery** — .env file existed but wasn't loaded; direnv setup should be part of project init
- **atlassian-python-api bugs** — set_issue_status/issue_transition both broken for numeric IDs; had to POST directly

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| raise-cli not raise-pro | Consistent with Confluence; open-core | Clean, no cross-package deps |
| Delete providers/jira/ | No consumer, speculative sync engine | -1,633 LOC |
| Delete both hooks | Auto-transition unreliable without work_id→key mapping | Cleaner, explicit transitions in skills |
| Unified [atlassian] dep | Same library for both | DRY, with backwards-compat aliases |
| Direct POST for transitions | Library bug in set_issue_status | Works reliably against live Jira |

## Patterns

- **PAT: atlassian-python-api transition bug** — `set_issue_status()` and `issue_transition()` both call `get_transition_id_to_status_name()` which does `.lower()` on the status param, breaking with numeric IDs. POST directly to `/issue/{key}/transitions`.
- **PAT: JQL reserved words** — project names like "RAISE" are JQL reserved words. Always quote: `project = "RAISE"`.
- **PAT: E2E before cleanup** — run integration tests against real backends BEFORE deleting old code, not after.

## Metrics

| Story | Size | Tests | LOC src | LOC test |
|-------|:----:|:-----:|:-------:|:--------:|
| S1052.1 JiraClient | M | 49 | +281 | +781 |
| S1052.2 JiraConfig | S | 24 | +117 | +316 |
| S1052.3 Adapter | M | 46 | +359 | +677 |
| S1052.5 Cleanup | S | 0 | -2,603 | -5,383 |
| S1052.6 E2E + docs | S | 6 | +300 | +53 |
