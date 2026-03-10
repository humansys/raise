# Implementation Plan: RAISE-139 CWD Poka-yoke

## Overview
- **Story:** RAISE-139 (fixes RAISE-134)
- **Story Points:** 3 SP
- **Size:** S
- **Created:** 2026-02-15

## Design Summary

Guard on `session close`: compare resolved project path from `ActiveSession.project`
against the `--project` flag (or CWD). Reject writes on mismatch with clear error.

Guard lives in CLI command layer (`commands/session.py`), not the orchestrator.

## Tasks

### Task 1: CWD mismatch guard in session close command
- **Description:** Add guard after session ID resolution in `close()` command. Look up the `ActiveSession` for the resolved session ID, compare `Path(active.project).resolve()` vs `Path(project).resolve()`. On mismatch, call `cli_error()` with both paths. Guard only fires when we have both a resolved session ID AND an active session with a project path.
- **Files:** `src/rai_cli/cli/commands/session.py`
- **TDD Cycle:** RED (test mismatch rejected) → GREEN (add guard) → REFACTOR
- **Test file:** `tests/test_session_close_cwd_guard.py`
- **Verification:** `pytest tests/test_session_close_cwd_guard.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Manual integration test
- **Description:** Run `rai session start --project /home/emilio/Code/raise-commons --context` then attempt `rai session close --summary "test" --project /tmp` and verify rejection. Then close from correct project and verify success.
- **Verification:** Mismatch rejected with clear message; correct project succeeds.
- **Size:** XS
- **Dependencies:** Task 1

## Execution Order
1. Task 1 — guard + tests
2. Task 2 — manual validation

## Risks
- Path comparison edge cases (symlinks, trailing slashes): mitigated by `Path.resolve()` which canonicalizes both
- ActiveSession might not exist (legacy sessions without project): guard only fires when active session has project field

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | XS | -- | |
