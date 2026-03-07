# RAISE-483: Retrospective

## Fix Summary

Guarded `from mcp import ...` in `raise_cli/mcp/bridge.py` with try/except ModuleNotFoundError.
When `mcp` is not installed, the module loads cleanly and `McpBridge.__init__()` raises
`McpBridgeError` with actionable install guidance.

## Root Cause Confirmed

Unguarded module-level import of optional dependency (`mcp`) in `bridge.py`.
Entry point discovery (`registry._discover`) loaded `McpJiraAdapter` which triggered the import chain.

## What Went Well

- Existing `registry._discover()` already had error isolation (L46) — the fix complements it
- `from __future__ import annotations` + `TYPE_CHECKING` pattern keeps pyright happy
- logfire already used the same try/except pattern in the same file — consistency

## Pattern

PAT-E-597 (existing): `from __future__ import annotations` masks NameError for unimported names.
This bug is the complementary case: optional dependencies need explicit import guards even when
the module uses `from __future__ import annotations`.

Generalized: **all optional dependency imports must be guarded with try/except at module level,
with TYPE_CHECKING fallback for static analysis.**
