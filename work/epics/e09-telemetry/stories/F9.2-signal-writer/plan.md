# Implementation Plan: F9.2 Signal Writer

## Overview
- **Feature:** F9.2
- **Epic:** E9 Local Learning
- **Story Points:** 2 SP
- **Feature Size:** S
- **Created:** 2026-02-03
- **Dependencies:** F9.1 Signal Schema (✓ complete)

## Story

**As** Rai (the AI partner)
**I want** to write signals to a JSONL file
**So that** telemetry events are persisted for later analysis

## Acceptance Criteria

- [ ] `emit()` function appends signal to `.rai/telemetry/signals.jsonl`
- [ ] Creates `.rai/telemetry/` directory if missing
- [ ] Handles all 5 signal types (via Signal union)
- [ ] Thread-safe writes (file locking or atomic append)
- [ ] Returns result with success/failure status
- [ ] Tests pass with >90% coverage

## Tasks

### Task 1: Create writer module with emit function
- **Description:** Create `writer.py` with `emit()` function that appends signals to JSONL
- **Files:**
  - `src/raise_cli/telemetry/writer.py` (new)
  - `src/raise_cli/telemetry/__init__.py` (update exports)
- **Verification:** `uv run python -c "from raise_cli.telemetry import emit"`
- **Size:** S
- **Dependencies:** None

### Task 2: Add tests for writer
- **Description:** Unit tests for emit function — success, directory creation, error handling
- **Files:**
  - `tests/telemetry/test_writer.py` (new)
- **Verification:** `uv run pytest tests/telemetry/test_writer.py -v --cov=src/raise_cli/telemetry`
- **Size:** S
- **Dependencies:** Task 1

## Execution Order

1. Task 1 (foundation) — Create writer module
2. Task 2 (validation) — Add tests

## Risks

- **File locking complexity:** Mitigation — Start with simple append, add locking if needed
- **Directory permissions:** Mitigation — Graceful error handling with clear message

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1 | S | 20m | -- | |
| 2 | S | 25m | -- | |
| **Total** | **S** | **45m** | -- | |

---

*Plan created: 2026-02-03*
*Next: `/story-implement`*
