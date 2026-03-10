# Implementation Plan: Per-Session State Isolation

## Overview
- **Story:** RAISE-138
- **Story Points:** 3 SP
- **Feature Size:** M
- **Created:** 2026-02-15

## Tasks

### Task 1: Add `get_session_dir()` path helper
- **Description:** Add `get_session_dir(session_id, project_root)` to `config/paths.py`. Returns `.raise/rai/personal/sessions/{session_id}/`. This is the foundation all other tasks build on.
- **Files:** `src/rai_cli/config/paths.py`, `tests/config/test_paths.py`
- **TDD Cycle:** RED (test `get_session_dir("SES-177")` returns correct path) → GREEN (implement) → REFACTOR
- **Verification:** `pytest tests/config/test_paths.py -v`
- **Size:** XS
- **Dependencies:** None

### Task 2: Per-session state read/write
- **Description:** Update `session/state.py` to accept `session_id` parameter. When provided, read/write `state.yaml` from per-session directory (`sessions/{session_id}/state.yaml`). When not provided, fall back to flat file (`personal/session-state.yaml`) for backward compat. Update existing tests.
- **Files:** `src/rai_cli/session/state.py`, `tests/session/test_state.py`
- **TDD Cycle:** RED (test load/save with session_id writes to per-session dir) → GREEN → REFACTOR
- **Verification:** `pytest tests/session/test_state.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Per-session telemetry writes
- **Description:** Update `telemetry/writer.py` `emit()` to accept optional `session_id`. When provided, write to `sessions/{session_id}/signals.jsonl` instead of `personal/telemetry/signals.jsonl`. Convenience functions (`emit_skill_event`, etc.) pass through `session_id`. Update tests.
- **Files:** `src/rai_cli/telemetry/writer.py`, `tests/telemetry/test_writer.py`
- **TDD Cycle:** RED (test emit with session_id writes to per-session dir) → GREEN → REFACTOR
- **Verification:** `pytest tests/telemetry/test_writer.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 4: Session directory lifecycle (create on start, cleanup on close)
- **Description:** Wire session directory creation into CLI `session start` command — create `sessions/{SES-NNN}/` dir when generating session ID. Wire cleanup into `session close` — remove session directory after `process_session_close` completes. Update `close.py` to write state to per-session dir (pass session_id through). Add migration logic: if flat `session-state.yaml` and `telemetry/signals.jsonl` exist and no per-session dirs yet, move them into a session dir on first start.
- **Files:** `src/rai_cli/cli/commands/session.py`, `src/rai_cli/session/close.py`, `tests/cli/commands/test_session.py`
- **TDD Cycle:** RED (test session start creates dir, test close removes dir, test migration moves files) → GREEN → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_session.py tests/session/ -v`
- **Size:** M
- **Dependencies:** Tasks 1, 2, 3

### Task 5: Update bundle loader for per-session state
- **Description:** Update `session/bundle.py` `assemble_context_bundle()` to load session state from per-session directory when session_id is available. The session start command already passes session_id to the bundle — ensure it loads from the correct path.
- **Files:** `src/rai_cli/session/bundle.py`, `tests/session/test_bundle.py` (if exists)
- **TDD Cycle:** RED (test bundle loads state from per-session dir) → GREEN → REFACTOR
- **Verification:** `pytest tests/session/ -v`
- **Size:** S
- **Dependencies:** Task 2

### Task 6: Full validation pass
- **Description:** Run full test suite, pyright, ruff, bandit. Fix any issues. Verify two independent session directories can coexist without interference.
- **Verification:** `pytest && pyright && ruff check src/ tests/ && bandit -r src/ -c pyproject.toml`
- **Size:** S
- **Dependencies:** Tasks 1-5

### Task 7 (Final): Manual Integration Test
- **Description:** Validate story works end-to-end with running `rai` CLI:
  1. `rai session start --project . --agent claude-code` → creates `sessions/SES-NNN/`
  2. `rai memory emit-work story TEST -e start -p design` → signals go to per-session dir
  3. `rai session close --session SES-NNN --project . --summary "test"` → session dir cleaned up
  4. Verify flat files are migrated if they existed
- **Verification:** Demo the story working interactively against real `.raise/` dir
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order

1. Task 1 — path helper (foundation, XS)
2. Task 2, Task 3 — per-session state + telemetry (parallel, both depend only on Task 1)
3. Task 4 — CLI wiring + migration (depends on 1, 2, 3)
4. Task 5 — bundle loader update (depends on 2)
5. Task 6 — full validation pass
6. Task 7 — manual integration test

Note: Tasks 2 and 3 can run in parallel. Task 5 can also overlap with Task 4 since they share no files.

## Risks

- **Migration edge cases**: Flat files exist but are empty/corrupt → handle gracefully (skip migration, log warning)
- **Close cleanup timing**: Removing session dir before all writes complete → ensure cleanup is last step in close
- **Telemetry CLI commands use `--session` flag**: The `emit-work` and other telemetry CLI commands need to pass session_id through to `emit()` — verify this path exists or wire it in Task 4

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | XS | -- | |
| 2 | S | -- | |
| 3 | S | -- | |
| 4 | M | -- | |
| 5 | S | -- | |
| 6 | S | -- | |
| 7 | XS | -- | Integration test |
