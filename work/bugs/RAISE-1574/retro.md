## Retrospective: RAISE-1574

### Summary
- Root cause: `create_issue()` in jira_adapter.py ignores `issue.metadata` — parent key from CLI never reaches Jira fields dict
- Fix approach: read `metadata["parent"]` and add `{"parent": {"key": value}}` to fields dict (2 lines)
- Classification: Interface/S2-Medium/Code/Missing

### Process Improvement
**Prevention:** Integration tests that verify data flows end-to-end across layers (CLI flag → adapter fields dict → API payload). RAISE-866 added the model and CLI flag but no test verified the adapter consumed the new field.
**Pattern:** Interface + Missing + Code → feature delivered across layers without vertical integration test. The CLI silently accepts input that never reaches the backend.

### Heutagogical Checkpoint
1. Learned: `metadata` in IssueSpec is the generic bag for fields without first-class adapter support. Parent was the first consumer, custom fields will follow (tasks 2.2/2.3).
2. Process change: When a story touches multiple layers (CLI + adapter + client), require at least one test that spans the full path.
3. Framework improvement: None — bugfix flow worked well for XS scope.
4. Capability gained: Confirmed Jira parent payload format (`{"parent": {"key": ...}}`), verified with real Jira API including hierarchy validation errors.

### Patterns
- Added: PAT-F-057 (silent acceptance at layer boundaries)
- Reinforced: none (BASE-048 not in patterns.jsonl, only in graph)
