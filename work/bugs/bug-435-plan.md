# RAISE-435 Plan

## T1: Regression test (RED)

Add test in `tests/adapters/test_mcp_jira.py` that passes JQL with `\!=` and
verifies the bridge receives clean `!=`.

- Verify: `uv run pytest tests/adapters/test_mcp_jira.py -k "backslash" -x` → FAIL
- Commit: `test(RAISE-435): RED — regression test for shell-escaped JQL`

## T2: Fix (GREEN)

In `McpJiraAdapter.search()`, sanitize `query.replace("\\!", "!")` before
passing to bridge.

- Verify: `uv run pytest tests/adapters/test_mcp_jira.py -k "backslash" -x` → PASS
- Verify: `uv run pytest tests/adapters/test_mcp_jira.py --no-header -q` → all pass
- Verify: `uv run pyright src/rai_cli/adapters/mcp_jira.py` → 0 errors
- Commit: `fix(RAISE-435): sanitize shell-escaped bang in JQL queries`
