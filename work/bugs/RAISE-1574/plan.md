# RAISE-1574: Plan

## Tasks

### T1: Write regression test (RED)
- Write test that creates an issue with `metadata={"parent": "PARENT-1"}` and asserts the fields dict sent to Jira includes `{"parent": {"key": "PARENT-1"}}`
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_jira_adapter.py -x` — test FAILS
- Commit: `test(RAISE-1574): add regression test for parent in create_issue`

### T2: Fix create_issue to pass parent from metadata (GREEN)
- In `jira_adapter.py:create_issue()`, after building fields dict, add: `if issue.metadata.get("parent"): fields["parent"] = {"key": issue.metadata["parent"]}`
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_jira_adapter.py -x` — test PASSES
- Commit: `fix(RAISE-1574): pass parent from metadata in create_issue`
