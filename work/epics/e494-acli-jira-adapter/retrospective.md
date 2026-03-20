# E494: ACLI Jira Adapter — Epic Retrospective

## Summary

| Metric | Value |
|--------|-------|
| Stories | 6 (S494.1–S494.6) |
| Commits | 27 |
| Lines | +2460 / -1167 (net +1293) |
| Sessions | 3 (SES-345, SES-346, SES-347) |
| Patterns captured | 6 (PAT-E-040 through PAT-E-043, plus 2 from earlier stories) |
| Bugs found by integration tests | 3 |

## Stories Delivered

| Story | What | Size | Est/Actual |
|-------|------|------|------------|
| S494.1 | Spike — ACLI JSON mapping validation | XS | — |
| S494.2 | Core subprocess wrapper + telemetry | S | — |
| S494.3 | Full protocol (11 methods, 31 tests) | M | — |
| S494.4 | Multi-instance config + site switching | S | 85m/80m (1.06x) |
| S494.5 | Delete MCP adapter, migrate entry point | S | 15m/20m (1.33x) |
| S494.6 | Integration test suite (15 E2E tests) | S | 45m/60m (1.33x) |

## Key Deliverables

- **AcliJiraAdapter** — 11 protocol methods via ACLI subprocess, replacing MCP bridge
- **AcliJiraBridge** — thin subprocess wrapper with telemetry spans and auth switching
- **Multi-instance config** — `jira.yaml` with named instances, project→instance routing
- **MCP Jira adapter deleted** — -1115 LOC, single integration path
- **15 integration tests** — real Jira E2E, reusable pattern for future adapters
- **RTEST sandbox project** — test isolation in humansys Jira

## What Went Well

- **Research-grounded design** — 7 tools analyzed for multi-instance patterns before coding (S494.4)
- **TDD caught regressions** — 61 unit tests + 15 integration tests, every commit gated
- **Integration tests proved their value** — 3 bugs invisible to unit mocks found in first run
- **Clean deletion** — S494.5 removed 1115 LOC with zero breakage, quality review caught dead ruff config
- **Scope discipline** — JQL reserved word bug (RAISE keyword) tracked but not scope-crept into the epic

## What to Improve

- **Spike depth** — S494.1 should have captured exact response format for ALL ACLI commands, not just the happy path. Would have prevented 2 of the 3 integration bugs.
- **Venv management** — `uv pip install --reinstall` vs `uv sync --all-extras` confusion cost ~10min across stories. Now documented as PAT-E-041.
- **Plan atomicity** — S494.5 split delete + rewire into 2 tasks but they were atomically dependent. Fixed in PAT-E-040.

## Patterns Captured

| ID | Summary | Type |
|----|---------|------|
| PAT-E-040 | Deletion + entry point rewire must be one atomic commit | process |
| PAT-E-041 | `uv sync --all-extras` for workspace package reinstall, not `uv pip install` | technical |
| PAT-E-042 | Integration tests find what unit mocks hide — mocks validate assumptions, not contracts | process |
| PAT-E-043 | ACLI response format map (create→full issue, edit→envelope, link→no --json) | technical |

## Open Items (carried forward)

- **JQL reserved word quoting** — RAISE is a reserved JQL word, queries with `project = RAISE` fail. Workaround: `project = 'RAISE'`. Needs fix in `to_jql()`.
- **`rai doctor` ACLI check** — SHOULD item from scope, not implemented. Low priority.
- **Branch cleanup** — `story/raise-502/session-counter-resilience` still exists (pre-E494).
