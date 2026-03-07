# RAISE-482: Fix Plan

## Task 1: Regression test (RED)

Write test for a `check_legacy_packages()` function that detects co-installed
legacy packages and returns a warning message. Mock `importlib.metadata` to
simulate old packages being present.

**Verify:** `uv run pytest tests/cli/test_legacy_check.py -x`
**Commit:** `test(RAISE-482): RED — regression test for legacy package detection`

## Task 2: Implement legacy package check (GREEN)

Create `raise_cli/compat.py` with `check_legacy_packages()` that:
- Checks if `rai-cli` or `rai-core` are installed via `importlib.metadata`
- Returns warning string with uninstall command, or None if clean

Wire it into CLI startup (`main.py`) to emit warning via `logging.warning`.

**Verify:** `uv run pytest tests/cli/test_legacy_check.py -x && uv run pytest -x && uv run ruff check src/ && uv run pyright`
**Commit:** `fix(RAISE-482): detect and warn about co-installed legacy packages`
