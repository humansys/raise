## Plan: RAISE-1152

### T1: Regression test — assignee update fails (RED)

Add test in `test_jira_adapter.py` that verifies `update_issue` with assignee
resolves to `{"accountId": "..."}` format before calling client.

**Verify:** `uv run pytest packages/raise-cli/tests/adapters/test_jira_adapter.py -x --tb=short` → FAIL
**Commit:** `test(RAISE-1152): RED — regression test for assignee field normalization`

### T2: Add _resolve_account_id and _normalize_fields to adapter (GREEN)

In `jira_adapter.py`:
- Add `_resolve_account_id(query: str) -> str` — uses `self._client` user search
- Add `_normalize_fields(fields: dict) -> dict` — if `assignee` is string, resolve + format
- Call `_normalize_fields` in `update_issue` before passing to client

**Verify:** `uv run pytest packages/raise-cli/tests/adapters/test_jira_adapter.py -x --tb=short` → PASS
**Commit:** `fix(RAISE-1152): normalize assignee to accountId format in Jira adapter`

### T3: Add assignee to IssueSpec + create_issue

In `pm.py`: add optional `assignee: str | None = None` to `IssueSpec`.
In `jira_adapter.py:create_issue`: if `issue.assignee`, resolve and add to fields.
In `backlog.py:create`: add `--assignee` option, pass to IssueSpec.

Test: extend T1 test to cover create path.

**Verify:** All 4 gates pass
**Commit:** `feat(RAISE-1152): add assignee support to backlog create`

### T4: Add _resolve_account_id to JiraClient

The user search method belongs in `jira_client.py` (client owns all Jira API calls).
Move from adapter to client for proper layer separation.

**Verify:** All 4 gates pass
**Commit:** `refactor(RAISE-1152): move user search to JiraClient layer`
