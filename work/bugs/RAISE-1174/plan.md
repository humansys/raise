# RAISE-1174: Plan

## Tasks

### T1: Regression tests for _ensure_cql plain-text wrapping
- Test plain text → `siteSearch ~ "..."` wrapping
- Test CQL passthrough for each operator (~, =, AND, OR, ORDER BY)
- Test quote escaping in plain text
- Test single word input
- Test search() integration passes plain text through _ensure_cql to backend
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_confluence_client.py -x -k "ensure_cql or plain_text"`
- Commit: `test(RAISE-1174): regression tests for plain-text CQL auto-wrapping`

### T2: Triage + close artifacts
- Set Jira classification fields
- Write retro
- Close via MR
