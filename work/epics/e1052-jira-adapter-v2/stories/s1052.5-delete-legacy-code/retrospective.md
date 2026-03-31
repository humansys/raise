# S1052.5 Retrospective — Delete Legacy Code

## Summary

Deleted all legacy Jira adapter code superseded by PythonApiJiraAdapter (S1052.3).
Absorbs planned S1052.4.

## Metrics

- **Files deleted:** 33 (source + tests + docs)
- **LOC removed:** 8,486
- **Source LOC:** 2,603 (adapters, hooks, providers)
- **Test LOC:** 5,383
- **Doc LOC:** ~500

## What Was Deleted

### raise-pro source (2,603 LOC)
- `adapters/acli_jira.py` (417 LOC) — AcliJiraAdapter
- `adapters/acli_bridge.py` (210 LOC) — sync-to-async bridge
- `hooks/jira_sync.py` (127 LOC) — JiraSyncHook
- `providers/jira/` (8 files, 1,633 LOC) — client, models, oauth, sync, properties, exceptions

### raise-cli source (216 LOC)
- `hooks/builtin/backlog.py` — BacklogHook

### Tests (5,383 LOC across 15 files)
- raise-pro: providers/jira/ tests, test_jira_sync, test_base (trimmed)
- raise-cli: test_backlog_hook, test_backlog_integration, test_acli_bridge, test_acli_jira, integration/jira/

### Docs (2 files)
- `docs/guides/jira-adapter-architecture.md`
- `docs/guides/jira-adapter.md`

## Entry Point Changes

- raise-pro: removed `jira` adapter and `jira-sync` hook entry points
- raise-cli: removed `backlog` hook entry point
- raise-cli: added `[atlassian]` optional dep, kept `[confluence]` and `[jira]` as aliases

## Broken Imports Found and Fixed

1. `test_base.py` — removed test that imported deleted `JiraClient`
2. `conftest.py` — removed `jira_yaml_setup` fixture (orphaned after BacklogHook test deletion)
3. `events.py` — updated docstring referencing BacklogHook

## Test Results

- 4,506 passed, 25 skipped (zero regressions)
- 3 pre-existing failures unrelated to this story
- Pyright: 0 errors
- Ruff: 15 errors (all pre-existing, reduced from 17 by file deletion)
