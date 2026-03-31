# E1052: Jira Adapter v2 — Pure Python Transport

## Objective

Replace the ACLI subprocess-based Jira adapter with a pure Python implementation
using `atlassian-python-api`. Eliminate Java/ACLI dependency, delete legacy code
(ACLI adapter + providers/jira/ sync engine + Jira-specific hook), generalize
the lifecycle hook for any PM adapter.

## Value

- **-1200 LOC net**: less code doing the same work
- **Zero external binary**: no ACLI/Java install, no subprocess overhead
- **Consistent pattern**: same architecture as Confluence adapter (E1051)
- **Open-core**: adapter moves from raise-pro to raise-cli
- **Generalized hook**: BacklogSyncHook works with any PM adapter, not just Jira

## Design Decisions (from interactive review, 2026-03-31)

| # | Decision | Rationale | AR Heuristic |
|---|----------|-----------|:------------:|
| D1 | Adapter lives in raise-cli, not raise-pro | Consistent with Confluence; raise-pro differentiates via sync engine, not CRUD | H10 Pattern Duplication |
| D2 | New JiraClient from scratch, delete providers/jira/ | Sync engine has no consumer; two Jira clients is confusion | H4 Unused Consumers |
| D3 | Pydantic for jira.yaml (JiraConfig) | Consistent with ConfluenceConfig; validation at load time | H10, project rule |
| D4 | BacklogSyncHook by convention, not config | `story_start → "in-progress"`, `story_close → "done"` is universal | H8 Config Over Convention |
| D5 | `raise-cli[atlassian]` unified optional dep | Same library for Jira + Confluence; `[jira]`+`[confluence]` = semantic dup | H9 Semantic Duplication |
| D6 | Don't touch providers/jira/client.py OAuth | Different purpose (bidirectional sync); delete entirely, not merge | H7 Abstraction-to-LOC |

## Stories

| # | Story | Size | Description | Depends on |
|---|-------|:----:|-------------|------------|
| S1052.1 | JiraClient wrapper | M | Wrapper over `atlassian.Jira`: auth from env, error normalization, multi-instance routing | — |
| S1052.2 | JiraConfig Pydantic | S | Pydantic model for `jira.yaml`. Backwards compat with current schema. Validation at load. | — |
| S1052.3 | PythonApiJiraAdapter | M | 11 PM protocol methods via JiraClient. Entry point in raise-cli. Replaces AcliJiraAdapter. | S1052.1, S1052.2 |
| S1052.4 | BacklogSyncHook generalized | S | Move from raise-pro → raise-cli. Convention-based (~40 LOC). Delete JiraSyncHook. | — |
| S1052.5 | Delete ACLI + providers/jira/ | S | Remove AcliJiraAdapter, AcliJiraBridge, providers/jira/ (6 files). Unify `[jira]`+`[confluence]` → `[atlassian]`. Migrate entry points. | S1052.3, S1052.4 |
| S1052.6 | Integration tests + docs | S | E2E with real Jira (skip when unavailable). Architecture module doc. | S1052.3 |

## Dependencies

```
S1052.1 (Client) ──┐
                    ├──→ S1052.3 (Adapter) ──→ S1052.5 (Delete old)
S1052.2 (Config) ──┘                      └──→ S1052.6 (Tests + docs)

S1052.4 (Hook) — independent, parallel with any story
```

S1052.1 and S1052.2 can run in parallel.
S1052.5 and S1052.6 can run in parallel after S1052.3.
S1052.4 has no dependencies — runs anytime.

**External:** None. `atlassian-python-api` already a dependency (via Confluence).

## In Scope (MUST)

- JiraClient with auth, errors, multi-instance (same pattern as ConfluenceClient)
- JiraConfig Pydantic model for `.raise/jira.yaml`
- PythonApiJiraAdapter implementing full AsyncProjectManagementAdapter
- BacklogSyncHook generalized (convention-based, adapter-agnostic)
- Delete AcliJiraAdapter, AcliJiraBridge, providers/jira/ (all 6 files)
- Unify optional dependency: `[jira]` + `[confluence]` → `[atlassian]`
- Entry point migration: `rai.adapters.pm: jira` → new adapter in raise-cli

## In Scope (SHOULD)

- JiraExceptions typed hierarchy (same pattern as confluence_exceptions.py)
- Logfire telemetry on JiraClient operations (carry forward from ACLI bridge)

## Out of Scope

| Item | Rationale | Deferred to |
|------|-----------|-------------|
| Backend discovery (query workflows, transitions) | Self-service capability | RAISE-1130 |
| Adapter doctor (validate config vs live backend) | Self-service capability | RAISE-1130 |
| Config generator (`/rai-adapter-setup`) | Self-service capability | RAISE-1130 |
| Graceful degradation (Jira fail → filesystem) | Reliability capability | RAISE-1131 |
| Human error messages referencing doctor | Reliability capability | RAISE-1131 |
| Bidirectional sync engine rebuild | No consumer; speculative | Parking lot |
| OAuth authentication flow | API token sufficient | Parking lot |

## Done Criteria

1. `rai backlog create/get/search/transition/comment/link/update` work via new adapter
2. Multi-instance tested: query RAISE (humansys) in one session
3. All existing `rai backlog` tests pass with new adapter
4. AcliJiraAdapter, AcliJiraBridge, providers/jira/ deleted
5. JiraSyncHook replaced by BacklogSyncHook (convention-based, in raise-cli)
6. `pip install raise-cli[atlassian]` installs both Jira + Confluence support
7. Zero Java/ACLI dependency for Jira operations
8. Entry point `rai.adapters.pm: jira` points to new adapter in raise-cli

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| `atlassian-python-api` Jira API differs from ACLI output format | Medium | Medium | S1052.1 validates all methods against live backend first (same as E1051) |
| BacklogSyncHook convention doesn't cover all workflow variants | Low | Low | Convention covers 95%; override via config in RAISE-1130 if needed |
| Deleting providers/jira/ breaks something unexpected | Low | Medium | Grep all imports before deletion; tests catch consumers |

## Progress Tracking

| Story | Status | Commit | Date |
|-------|--------|--------|------|
| S1052.1 | DONE | 672b7b9b | 2026-03-31 |
| S1052.2 | TODO | — | — |
| S1052.3 | TODO | — | — |
| S1052.4 | TODO | — | — |
| S1052.5 | TODO | — | — |
| S1052.6 | TODO | — | — |

## Metrics (targets)

| Metric | Target |
|--------|--------|
| LOC added | ~500 |
| LOC deleted | ~1700 |
| LOC net | ~-1200 |
| New tests | ~60 |
| Stories | 6 |
| Sessions | 1 |
