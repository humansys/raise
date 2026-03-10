# RAISE-502: Plan

## Task 1: Regression test — get_next_id with sibling directories

**File:** `tests/memory/test_writer.py`
**What:** Add test that when index.jsonl is missing but sibling directories
`SES-001/`, `SES-024/` exist, `get_next_id` returns `SES-025` (not `SES-001`).
Also test: directories exist AND index.jsonl exists — index.jsonl max wins when
higher; directory max wins when higher (resilience).
**Verify:** `uv run pytest tests/memory/test_writer.py::TestGetNextId -x` — new tests RED
**Commit:** `test(RAISE-502): regression tests for directory fallback in get_next_id`

## Task 2: Fix get_next_id with directory scan fallback

**File:** `src/raise_cli/memory/writer.py`
**What:** After scanning index.jsonl entries, also scan the parent directory for
subdirectories matching `{PREFIX}-{NNN}` pattern. Take max of both sources.
Minimal change — add ~10 lines after the existing for-loop.
**Verify:** `uv run pytest tests/memory/test_writer.py::TestGetNextId -x` — all GREEN
**Commit:** `fix(RAISE-502): directory fallback in get_next_id prevents counter reset`

## Task 3: Gates pass

**Verify:**
- `uv run pytest --tb=short`
- `uv run ruff check`
- `uv run pyright`
**Commit:** only if fixes needed
