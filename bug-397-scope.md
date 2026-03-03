# Bug RAISE-397 — Scope

WHAT:      `ruff check src/ tests/` exits non-zero with 37 violations
WHEN:      Any CI run after RAISE-396 fix (pytest now passes, ruff gate reached)
WHERE:     tests/adapters/, tests/graph/, tests/rai_server/, tests/session/,
           src/rai_cli/adapters/sync.py
EXPECTED:  ruff check exits 0, all violations resolved
Done when: `uv run ruff check src/ tests/` exits 0 with 0 errors

## Analysis (XS — evident cause)

Pre-existing violations accumulated across multiple stories, masked by
pytest collection failures (RAISE-396). Now surface since pytest passes.

Categories:
- UP017: timezone.utc → datetime.UTC (20 auto-fixable)
- I001: unsorted import blocks (auto-fixable)
- F401: unused imports (auto-fixable)
- F841: unused local variable `original_search` (manual)
- UP047: generic function should use type parameters `_run_sync` (manual)

Countermeasure: ruff --fix for auto-fixable, manual edits for remainder.
