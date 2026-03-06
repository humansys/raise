# RAISE-398 Analysis

## Root causes

### Cause A — queries.py: unused import
`text` was used for raw SQL in an earlier version, removed during a refactor,
but the import was never cleaned up. Trivial deuda.

Root cause: no ruff/pyright gate caught it at the time of the refactor
(ruff was blocked by the 37-violation backlog from RAISE-397).

### Cause B — mcp_jira.py: type narrowing lost on dict reassignment

`result.data: dict[str, Any]`

When accessing `data["issue"]` (value type: `Any`) and narrowing with
`isinstance(..., dict)`, pyright produces `dict[Unknown, Unknown]` — the
generic params are lost because `Any` does not carry them through narrowing.

After `data = data["issue"]`, all derived variables (`key`, `url`) inherit
the Unknown type, and passing them to `IssueRef(key=..., url=...)` triggers
`reportUnknownArgumentType`.

## Fix approach

A: Remove `text` from the sqlalchemy import in queries.py.

B: Cast the narrowed dict explicitly to `dict[str, Any]` so pyright can
   propagate the known value type through the rest of the function.
   `from typing import cast` + `data = cast(dict[str, Any], data["issue"])`
