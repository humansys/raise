# Implementation Plan: RAISE-146 — Wire --session through telemetry CLI

## Overview
- **Story:** RAISE-146
- **Story Points:** 1 SP
- **Size:** XS
- **Created:** 2026-02-16

## Tasks

### Task 1: Add --session to emit-work, emit-session, emit-calibration
- **Description:** Add `--session` option to all three emit commands in `memory.py`. Resolve via `resolve_session_id()` (flag > env var). Pass resolved `session_id` to `emit()`.
- **Files:** `src/rai_cli/cli/commands/memory.py`
- **TDD Cycle:** RED (test that --session flag routes signals to per-session dir) → GREEN (add option + wiring) → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_memory.py -k emit`
- **Size:** S
- **Dependencies:** None

### Task 2: Manual Integration Test
- **Description:** Run `rai memory emit-work story TEST-1 -e start -p design --session <active-session>` and verify signal lands in per-session directory.
- **Verification:** Check `.raise/rai/personal/sessions/SES-NNN/signals.jsonl` contains the event.
- **Size:** XS
- **Dependencies:** Task 1

## Execution Order
1. Task 1 (implementation + tests)
2. Task 2 (integration validation)

## Risks
- None significant. Pattern already established in `session.py`, `emit()` already supports `session_id`.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | XS | -- | |
