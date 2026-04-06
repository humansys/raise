# RAISE-605: Plan

## Tasks

### T1: Regression tests — adapter uses metadata["parent_id"] (RED)
- Test: metadata["parent_id"] set → used directly, routing parent skipped
- Test: metadata["parent_id"] not set → routing parent used (existing behavior)
- Test: neither parent_id nor routing → error with clear message
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_confluence_adapter.py -x -k "parent"` — FAILS
- Commit: `test(RAISE-605): regression tests for parent_id in publish`

### T2: Adapter — read metadata["parent_id"] with routing fallback (GREEN)
- In `publish()`: check metadata["parent_id"] first, then routing, then error
- When parent_id from metadata, still resolve routing for labels (if available)
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_confluence_adapter.py -x` — PASSES
- Commit: `fix(RAISE-605): adapter publish reads metadata parent_id`

### T3: CLI — add --parent flag to publish command
- Add `--parent PAGE_ID` option to `docs publish`
- Pass as `metadata["parent_id"]`
- Test CLI wiring via test_docs_commands.py
- Verify: `uv run pytest packages/raise-cli/tests/cli/test_docs_commands.py -x -k "parent"` — PASSES
- Commit: `fix(RAISE-605): add --parent flag to rai docs publish`
