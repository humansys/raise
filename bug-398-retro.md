# RAISE-398 Retro

## Fix summary

Two independent root causes, two atomic fixes:

1. **queries.py**: removed unused `text` import — leftover from prior refactor,
   never caught because ruff was blocked by the 37-violation backlog (RAISE-397).

2. **mcp_jira.py**: added `cast(dict[str, Any], data["issue"])` to restore type
   information lost when pyright narrows `Any` through isinstance to
   `dict[Unknown, Unknown]`. The cast is safe — the isinstance guard runs first.

## Fix addresses root cause?

Yes. Both fixes address structural causes, not symptoms:
- A: the import genuinely was unused
- B: the type chain was genuinely broken at the isinstance reassignment

## Regressions?

None. 3345 tests pass, ruff clean, pyright 0 errors.

## Pattern worth recording?

Yes — the cast pattern is a reusable technique.
