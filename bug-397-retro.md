# Bug RAISE-397 — Retro

## Fix Summary

- 37 ruff violations resolved: 33 auto-fixed, 4 manual
- 71 files reformatted (ruff format)
- Root cause: violations accumulated across stories, masked by pytest failure (RAISE-396)

## Manual fixes

| Rule | Location | Change |
|------|----------|--------|
| UP042 | schemas/journal.py | JournalEntryType(str, Enum) → StrEnum |
| UP047 | adapters/sync.py | TypeVar("T") → PEP 695 type param `[T]` |
| F841 | tests/adapters/test_sync.py | Remove unused `original_search` |
| E741 | tests/cli/commands/test_graph_agent_format.py | Rename `l` → `ln` (14 sites) |

## Systemic Insight

Lint gates should be enforced per-story to prevent accumulation.
When pytest fails, ruff/format/pyright are never reached — masking debt.
