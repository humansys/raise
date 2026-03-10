# Implementation Plan: RAISE-201 — Session Close Race Condition

## Overview
- **Story:** RAISE-201
- **Size:** S (3 SP)
- **Created:** 2026-02-19

## Tasks

### Task 1: Add session_id to CloseInput + load_state_file
- **Description:** Add `session_id: str = ""` field to `CloseInput` dataclass.
  Update `load_state_file()` to read `session_id` from YAML. Backwards
  compatible — missing field defaults to empty string.
- **Files:** `src/rai_cli/session/close.py`, `tests/session/test_close.py`
- **TDD Cycle:**
  - RED: Test that `load_state_file` returns `CloseInput` with `session_id`
    when present in YAML, and empty string when absent.
  - GREEN: Add field + read logic.
  - REFACTOR: None expected.
- **Verification:** `uv run pytest tests/session/test_close.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Coherence validation in close command
- **Description:** In `session.py` `close()` command, after loading state file,
  validate that `close_input.session_id` matches `resolved_session_id` (if both
  are present). Hard reject with error message on mismatch. Skip validation if
  either is empty (backwards compat).
- **Files:** `src/rai_cli/cli/commands/session.py`, `tests/cli/test_session_close.py`
- **TDD Cycle:**
  - RED: Test that CLI exits with error when session_id mismatch detected.
    Test that CLI proceeds when session_id matches or is absent.
  - GREEN: Add validation after `load_state_file()` call.
  - REFACTOR: Extract validation to helper if needed.
- **Verification:** `uv run pytest tests/cli/test_session_close.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Update skill template + manual integration test
- **Description:** Update `rai-session-close` SKILL.md: change state file path
  from `/tmp/session-output.yaml` to `/tmp/session-output-{SES-ID}.yaml`, add
  `session_id` field to YAML example, add `--session {SES-ID}` to CLI call.
  Then manually test the full flow.
- **Files:** `.claude/skills/rai-session-close/SKILL.md`
- **Verification:** Read skill, verify path and YAML example are updated.
  Manual: write a test YAML with session_id, run `rai session close` with
  matching and mismatching `--session` flags.
- **Size:** XS
- **Dependencies:** Task 2

## Execution Order
1. Task 1 (model + loader)
2. Task 2 (validation, depends on T1)
3. Task 3 (skill template + manual test, depends on T2)

## Risks
- **Test file location unclear:** Need to find existing close tests to extend.
  Mitigation: grep for existing test patterns.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | XS | -- | |
