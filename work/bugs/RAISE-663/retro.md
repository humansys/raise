# Retrospective: RAISE-663

## Summary
- Root cause: `str()` on ADF dict in `_parse_issue_detail` produces Python repr
- Fix approach: `_adf_to_text()` recursive walker + remove hard-cap workaround

## Heutagogical Checkpoint
1. **Learned:** ADF is a tree structure — any assumption of "description is a string" breaks on real Jira content. The hard-cap in backlog.py was a silent symptom of an upstream parser defect, not a display policy.
2. **Process change:** When a display command truncates output aggressively (500 chars), that's a code smell pointing at a bad upstream conversion, not a display choice. Investigate upward.
3. **Framework improvement:** None — the bugfix lifecycle worked cleanly. RCA session yesterday meant Step 2 was near-zero cost today.
4. **Capability gained:** Pattern for ADF→text in Python: walk node tree, accumulate text nodes, add newlines after block-level nodes. Handles all common ADF node types.

## Patterns
- Added: none (ADF pattern already captured in session-close context from yesterday's research)
- Reinforced: none evaluated
