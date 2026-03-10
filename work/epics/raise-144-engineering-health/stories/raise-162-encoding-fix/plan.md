# Implementation Plan: RAISE-162

## Overview
- **Story:** RAISE-162 — Add encoding="utf-8" to read_text() calls in test suite
- **Size:** XS
- **Created:** 2026-02-17

## Tasks

### Task 1: Mechanical replacement of read_text() calls
- **Description:** Use `sed` to replace all `.read_text()` with `.read_text(encoding="utf-8")` across test files
- **Files:** 26 files in `tests/`
- **Verification:**
  - `grep -rn '\.read_text()' tests/ --include='*.py'` returns zero hits
  - `grep -rn 'read_text(encoding="utf-8")' tests/ --include='*.py'` returns ~123 hits
  - `uv run pytest` passes
- **Size:** XS
- **Dependencies:** None

### Task 2: Add pre-commit regression hook
- **Description:** Add a `local` pre-commit hook that fails if bare `.read_text()` appears in `tests/`
- **Files:** `.pre-commit-config.yaml`
- **Verification:**
  - `pre-commit run check-read-text-encoding --all-files` passes
- **Size:** XS
- **Dependencies:** Task 1

### Task 3 (Final): Manual Integration Test
- **Description:** Verify the hook catches a regression — temporarily add a bare `read_text()` to a test file, confirm hook fails, then revert
- **Verification:** Hook rejects the bad pattern, then passes after revert
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order
1. Task 1 — sed replacement + test suite green
2. Task 2 — pre-commit hook
3. Task 3 — integration validation

## Risks
- **sed edge cases:** `.read_text()` could appear in string literals or comments. Mitigated by reviewing diff before commit.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | XS | -- | |
| 2 | XS | -- | |
| 3 | XS | -- | |
