## Analysis: RAISE-1152

### Root Cause (5 Whys)

1. **Why does --assignee not work?** Jira API rejects the update — "one of 'fields' or 'update' required"
2. **Why rejected?** Adapter sends `{"assignee": "email-string"}` but Jira Cloud requires `{"assignee": {"accountId": "..."}}`
3. **Why wrong format?** `jira_adapter.update_issue` is a raw pass-through — no field normalization
4. **Why no normalization?** Adapter was built for simple fields (summary, labels, priority) — assignee was added to CLI but adapter mapping was never implemented
5. **Why never caught?** No test validates assignee round-trip. Jira's error is cryptic ("one of 'fields' or 'update' required") hiding the actual format mismatch

### Evidence

```
$ uv run rai backlog update RAISE-1152 --assignee "fernando@rhumanys.ai" -a jira
Error: update_issue(RAISE-1152): unexpected error: one of 'fields' or 'update' required
```

### Fix Approach

Two-part fix in `jira_adapter.py`:

1. **Add `_normalize_fields` method** — intercept assignee (and future Jira-specific fields) before passing to client:
   - If `fields["assignee"]` is a string → resolve to accountId via Jira user search, then format as `{"accountId": "..."}`
   - Add `_resolve_account_id(query)` using atlassian-python-api's user search

2. **Add assignee to `IssueSpec`** — optional field so `create_issue` can also set it

Keep changes in the adapter layer only — CLI and Protocol stay unchanged.
