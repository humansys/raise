# RAISE-1574: Analysis

## Method: Document directly (cause evident from reproduction)

## Root Cause

`jira_adapter.py:create_issue()` builds the Jira fields dict from `IssueSpec` but only reads `summary`, `issue_type`, `description`, and `labels`. It never reads `metadata`, where the CLI deposits the parent key (`backlog.py:93`: `metadata={"parent": parent}`).

The wiring was omitted when RAISE-866 added `parent_key` to the IssueSpec model and `--parent` to the CLI — the adapter method was not updated to consume it.

## Evidence

- `jira_adapter.py:206-214`: fields dict construction — no reference to `metadata`
- `backlog.py:93`: `metadata={"parent": parent} if parent else {}`
- `jira_client.py:178-180`: `set_parent()` already uses `{"parent": {"key": parent}}` format — confirming the expected Jira payload

## Fix Approach

In `create_issue()`, after building the fields dict, add parent handling:

```python
if issue.metadata.get("parent"):
    fields["parent"] = {"key": issue.metadata["parent"]}
```

This is the minimal fix for RAISE-1574. The broader question of passing all metadata keys as custom fields is a separate feature (tasks 2.2/2.3 in the proposal).
