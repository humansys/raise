# Implementation Plan: F9.5 Error Emitters

## Overview
- **Feature:** F9.5
- **Epic:** E9 Local Learning
- **Story Points:** 1 SP
- **Feature Size:** XS
- **Created:** 2026-02-03
- **Dependencies:** F9.2 Signal Writer (✓ complete)

## Context

**Existing infrastructure:**
- Python telemetry module with `emit_error_event()` convenience function
- Shell scripts for hook-based events

**Target:**
- Emit error_event when tools fail
- Capture tool, error_type, context, recoverable flag
- Enable pattern detection: "pytest not found 5x this week"

## Story

**As** Rai (the AI partner)
**I want** tool errors to emit telemetry signals
**So that** I can detect recurring errors and suggest fixes

## Acceptance Criteria

- [ ] Error events emitted on tool failures
- [ ] Captures tool name, error type, context, recoverable flag
- [ ] Signals written to `.rai/telemetry/signals.jsonl`
- [ ] Schema matches ADR-018 ErrorEvent format

## Tasks

### Task 1: Create error event shell script
- **Description:** Create `log-error-event.sh` for hook-based error capture
- **Files:**
  - `.claude/skills/scripts/log-error-event.sh` (new)
- **Verification:** Script emits valid ErrorEvent JSON
- **Size:** XS
- **Dependencies:** None

## Execution Order

1. Task 1 — Create script

## Risks

- **Error detection:** Shell scripts may not capture all errors — Mitigation: Start with explicit invocations
- **Context sensitivity:** Avoid capturing sensitive info in context field — Mitigation: Keep context minimal (tool name only)

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1 | XS | 15m | -- | |
| **Total** | **XS** | **15m** | -- | |

---

*Plan created: 2026-02-03*
*Next: `/story-implement`*
