# RAISE-483: Fix Plan

## Task 1: Regression test (RED)

Write test that imports `McpBridge` when `mcp` is not installed (mock the import to simulate).
Verify it raises a clear error at instantiation, not at import time.

**Verify:** `uv run pytest tests/mcp/test_bridge_optional.py -x`
**Commit:** `test(RAISE-483): RED — regression test for mcp optional import guard`

## Task 2: Guard mcp import in bridge.py (GREEN)

In `raise_cli/mcp/bridge.py`, wrap `from mcp import ...` in try/except ImportError.
Store a sentinel. Raise clear `McpBridgeError` in `__init__` if `mcp` is not installed.

**Verify:** `uv run pytest tests/mcp/test_bridge_optional.py -x && uv run pytest -x && uv run ruff check src/ && uv run pyright`
**Commit:** `fix(RAISE-483): guard mcp optional import in McpBridge`

## Task 3: Verify full chain (REFACTOR)

Run full test suite. Verify `rai session start --context` works cleanly without `[mcp]`.
Clean up if needed.

**Verify:** `uv run pytest -x && uv run ruff check src/ && uv run pyright`
**Commit:** (only if refactoring needed)
