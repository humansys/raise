# Bug Plan: RAISE-552

## Tasks

### T1 — Regression test (RED)
Write tests for `_to_jql()`:
- issue key → `issue = KEY`
- explicit JQL → pass-through
- plain text → `text ~ "text"`

File: packages/raise-pro/tests/adapters/test_mcp_jira_search.py
Commit: test(RAISE-552): regression tests for _to_jql query normalization [RED]

### T2 — Implement `_to_jql()` (GREEN)
Add static method `_to_jql(query: str) -> str` to `McpJiraAdapter`.
Wire it into `search()`: `clean_query = self._to_jql(query.replace("\\!", "!"))`.

File: packages/raise-pro/src/rai_pro/adapters/mcp_jira.py
Commit: fix(RAISE-552): normalize plain-text query to JQL in McpJiraAdapter.search [GREEN]

### T3 — Gates
uv run pytest packages/raise-pro/tests/ --tb=short
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/
uv run pyright
