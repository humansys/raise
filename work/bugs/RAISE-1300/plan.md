# RAISE-1300: Plan

## Tasks

### T1: Regression test — per-project workflow/issue_types in output (RED)
- Add test: single project → workflow_states and issue_types inside projects.{KEY}, not at root
- Add test: multi-project → each project has its own workflow_states and issue_types
- Add test: no global `workflow` or `issue_types` keys in output
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_jira_config_gen.py -x -k "per_project"` — FAILS
- Commit: `test(RAISE-1300): regression tests for per-project workflow/issue_types`

### T2: Refactor generate_jira_config to per-project structure (GREEN)
- Remove `_merge_workflows()` and `_merge_issue_types()` helpers
- In `generate_jira_config()`, put workflow_states and issue_types directly in each project's dict entry
- Remove global `workflow` and `issue_types` from result dict
- Update existing tests to expect new structure
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_jira_config_gen.py -x` — ALL PASS
- Commit: `fix(RAISE-1300): per-project workflow states and issue types in config gen`
