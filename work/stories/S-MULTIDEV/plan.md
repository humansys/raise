# Implementation Plan: S-MULTIDEV — Multi-Developer Safety

## Overview
- **Story:** S-MULTIDEV
- **Size:** M
- **Created:** 2026-02-11
- **Modules:** mod-session, mod-memory, mod-context, mod-config

## Tasks

### Task 1: Gitignore index.json + remove from tracking (D1)
- **Description:** Add `.raise/rai/memory/index.json` to `.gitignore` and remove from git tracking with `git rm --cached`. Trivial, no code changes.
- **Files:** `.gitignore`
- **TDD Cycle:** N/A (git-only change)
- **Verification:** `git ls-files .raise/rai/memory/index.json` returns empty
- **Size:** XS
- **Dependencies:** None

### Task 2: Delete empty sessions/index.jsonl from tracking (D5)
- **Description:** Remove `.raise/rai/memory/sessions/index.jsonl` (0 bytes, tracked) and its parent dir from git. Sessions already write to `personal/sessions/index.jsonl`.
- **Files:** git rm only
- **TDD Cycle:** N/A (git-only change)
- **Verification:** `git ls-files .raise/rai/memory/sessions/` returns empty
- **Size:** XS
- **Dependencies:** None

### Task 3: Move session-state.yaml to personal/ (D2)
- **Description:** Update `SESSION_STATE_REL_PATH` in `session/state.py` to point to `.raise/rai/personal/session-state.yaml`. Add migration logic: if old path exists and new doesn't, move it. Remove old file from git tracking.
- **Files:** `src/rai_cli/session/state.py`, `tests/session/test_state.py`
- **TDD Cycle:**
  - RED: Test that `get_session_state_path()` returns personal/ path; test migration from old to new path
  - GREEN: Update path constant + add migration in `load_session_state()`
  - REFACTOR: Clean up docstrings
- **Verification:** `pytest tests/session/test_state.py -v`
- **Size:** S
- **Dependencies:** None

### Task 4: Developer-prefixed pattern IDs (D3)
- **Description:** Modify `_get_next_id()` in `memory/writer.py` to accept an optional `developer_prefix` parameter. When provided, generates `PAT-{X}-{NNN}` instead of `PAT-{NNN}`. Update `append_pattern()` to accept and pass through the prefix. The prefix comes from `~/.rai/developer.yaml` (`pattern_prefix` field). `_get_next_id()` must handle both old format (`PAT-NNN`) and new format (`PAT-X-NNN`) when scanning for max ID.
- **Files:** `src/rai_cli/memory/writer.py`, `tests/memory/test_writer.py`
- **TDD Cycle:**
  - RED: Test `_get_next_id()` with prefix generates `PAT-E-001`; test it handles mixed old/new IDs; test `append_pattern()` with prefix
  - GREEN: Add `developer_prefix` param to `_get_next_id()` and `append_pattern()`
  - REFACTOR: Ensure backward compat (no prefix = old behavior)
- **Verification:** `pytest tests/memory/test_writer.py -v`
- **Size:** M
- **Dependencies:** None

### Task 5: Move calibration.jsonl to personal/ (D4)
- **Description:** The graph builder already loads from 3 tiers (global, project, personal). Calibration is currently tracked in project `memory/`. Move it to `personal/` and remove from git tracking. Update `session/close.py` if it writes calibration to the project scope — it should write to personal scope instead.
- **Files:** `src/rai_cli/session/close.py` (if needed), `src/rai_cli/context/builder.py` (verify), tests
- **TDD Cycle:**
  - RED: Test calibration append writes to personal/ dir
  - GREEN: Update scope parameter in close.py calibration write
  - REFACTOR: Clean up
- **Verification:** `pytest tests/ -k calibration -v`
- **Size:** S
- **Dependencies:** None

### Task 6: Migrate existing patterns PAT-001..259 → PAT-E-001..259
- **Description:** Write a one-time migration of `.raise/rai/memory/patterns.jsonl` to rename all `PAT-NNN` entries to `PAT-E-NNN`. This is a data-only change. Can be a script or done in-place.
- **Files:** `.raise/rai/memory/patterns.jsonl`
- **TDD Cycle:** N/A (data migration, verify with grep)
- **Verification:** `grep -c '"PAT-[0-9]' .raise/rai/memory/patterns.jsonl` returns 0; `grep -c '"PAT-E-' .raise/rai/memory/patterns.jsonl` returns 259
- **Size:** S
- **Dependencies:** Task 4 (ID format must be decided first)

### Task 7: Wire prefix through session close
- **Description:** `session/close.py` calls `append_pattern()` during close. It needs to load the developer prefix from the profile and pass it through. Verify the full flow: session close → append_pattern → correct prefixed ID.
- **Files:** `src/rai_cli/session/close.py`, tests
- **TDD Cycle:**
  - RED: Test that session close produces prefixed pattern IDs
  - GREEN: Load prefix from developer profile, pass to append_pattern()
  - REFACTOR: Clean up
- **Verification:** `pytest tests/session/ -v`
- **Size:** S
- **Dependencies:** Task 4

### Task 8: Full validation gate
- **Description:** Run full test suite, type checks, linting. Fix any breakage.
- **Files:** Any files needing fixes
- **TDD Cycle:** N/A
- **Verification:** `pytest && pyright && ruff check .`
- **Size:** S
- **Dependencies:** Tasks 1-7

### Task 9 (Final): Manual Integration Test
- **Description:** Run `rai session start`, verify context loads. Run `rai session close` with a test pattern, verify PAT-E-NNN ID. Verify index.json is not tracked. Verify session-state.yaml writes to personal/.
- **Verification:** Demo the full flow interactively
- **Size:** XS
- **Dependencies:** Task 8

## Execution Order

1. Task 1 + Task 2 (parallel, git-only, trivial)
2. Task 3 + Task 4 + Task 5 (parallel, independent code changes)
3. Task 6 (data migration, depends on Task 4)
4. Task 7 (wiring, depends on Task 4)
5. Task 8 (validation gate, depends on all)
6. Task 9 (manual integration test)

## Risks

- **Pattern migration correctness:** Old PAT-NNN references in MEMORY.md and skill files. MEMORY.md is auto-generated so it rebuilds. Skill files reference patterns by number — need to check and update.
- **Session close flow:** Most complex integration point. Multiple writes in one operation.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | XS | -- | |
| 2 | XS | -- | |
| 3 | S | -- | |
| 4 | M | -- | |
| 5 | S | -- | |
| 6 | S | -- | |
| 7 | S | -- | |
| 8 | S | -- | |
| 9 | XS | -- | |
