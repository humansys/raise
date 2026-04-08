# RAISE-1574: --parent ignored in rai backlog create

WHAT:      `rai backlog create "Title" -p RAISE --parent RAISE-764` accepts the flag but the parent never reaches Jira. The issue is created without a parent link.
WHEN:      Every time `--parent` is passed to `rai backlog create`.
WHERE:     `packages/raise-cli/src/raise_cli/adapters/jira_adapter.py:203-218` — `create_issue()` builds fields dict from IssueSpec but ignores `metadata` entirely.
EXPECTED:  The created Jira issue should have `{"parent": {"key": "RAISE-764"}}` in its fields, making it a child of the specified parent.
Done when: `create_issue()` reads `metadata["parent"]` and includes it in the fields dict sent to Jira. Test covers the path.
