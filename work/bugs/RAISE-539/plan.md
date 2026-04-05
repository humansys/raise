# RAISE-539: Plan

## Tasks

### T1: Write regression test (RED)
- Test that `_resolve_env` correctly parses `KEY=VALUE` entries in `ServerConnection.env`
- Test: env list `["TOKEN=abc123"]` → resolved dict has `TOKEN: "abc123"`
- Test: env list `["TOKEN"]` → resolved dict has `TOKEN: {from os.environ}`
- Test: mixed `["TOKEN=abc", "OTHER"]` → both resolved correctly
- Verify: `uv run pytest packages/raise-cli/tests/cli/test_mcp.py -x -k resolve_env` — tests FAIL
- Commit: `test(RAISE-539): regression test for KEY=VALUE env parsing in _resolve_env`

### T2: Fix _resolve_env to parse KEY=VALUE (GREEN)
- In `_resolve_env`: if entry contains `=`, split on first `=` and use value directly
- If no `=`, look up from `os.environ` as today
- Verify: `uv run pytest packages/raise-cli/tests/cli/test_mcp.py -x -k resolve_env` — tests PASS
- Commit: `fix(RAISE-539): parse KEY=VALUE in _resolve_env for MCP env resolution`
