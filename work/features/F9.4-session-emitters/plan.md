# Implementation Plan: F9.4 Session Emitters

## Overview
- **Feature:** F9.4
- **Epic:** E9 Local Learning
- **Story Points:** 2 SP
- **Feature Size:** S
- **Created:** 2026-02-03
- **Updated:** 2026-02-03 (expanded scope after discovery)
- **Dependencies:** F9.2 Signal Writer (✓ complete)

## Context

**Existing infrastructure:**
- `/session-close` skill has hooks (PostToolUse, Stop)
- Python telemetry module: `src/raise_cli/telemetry/` (F9.1, F9.2)
- Memory CLI commands: `raise memory add-session`

**Discovery:**
Shell script hooks can't receive session metadata (type, outcome, features) because Claude can't set environment variables for hooks. We need a CLI command that Claude calls explicitly.

**Solution:**
CLI command `raise telemetry emit-session` that Claude calls at end of /session-close with session context.

## Story

**As** Rai (the AI partner)
**I want** session completions to emit telemetry signals
**So that** I can learn which session types succeed and where patterns emerge

## Acceptance Criteria

- [x] Shell script exists for future hook use
- [ ] CLI command `raise telemetry emit-session` works
- [ ] Captures session_type, outcome, duration_min, features
- [ ] Signals written to `.rai/telemetry/signals.jsonl`
- [ ] Schema matches ADR-018 SessionEvent format
- [ ] /session-close skill instructs Claude to call CLI

## Tasks

### Task 1: Create session telemetry shell script ✓ DONE
- **Description:** Create `log-session-event.sh` for future hook use
- **Files:**
  - `.claude/skills/scripts/log-session-event.sh` (new)
- **Verification:** Script emits valid SessionEvent JSON
- **Status:** Complete
- **Notes:** Works but requires env vars that hooks can't provide

### Task 2: Add hook to session-close ✓ DONE
- **Description:** Wire shell script into Stop hook
- **Files:**
  - `.claude/skills/session-close/SKILL.md` (modify)
- **Status:** Complete
- **Notes:** Hook added, but emits "unknown" without env vars

### Task 3: Create CLI telemetry command
- **Description:** Add `raise telemetry emit-session` command that Claude can call
- **Files:**
  - `src/raise_cli/cli/commands/telemetry.py` (new)
  - `src/raise_cli/cli/main.py` (modify - register command)
- **Verification:** `raise telemetry emit-session --type feature --outcome success` works
- **Size:** S
- **Dependencies:** F9.2 Signal Writer

### Task 4: Update session-close skill
- **Description:** Add instruction for Claude to call CLI at session end
- **Files:**
  - `.claude/skills/session-close/SKILL.md` (modify)
- **Verification:** /session-close workflow includes CLI call
- **Size:** XS
- **Dependencies:** Task 3

## Execution Order

1. ~~Task 1 (foundation)~~ ✓
2. ~~Task 2 (hook)~~ ✓
3. Task 3 (CLI command) ← **NEXT**
4. Task 4 (skill integration)

## Risks

- **Session metadata availability:** Claude needs to know session context — Mitigation: Skill instructions guide Claude to gather this
- **CLI discoverability:** User/Claude needs to know command exists — Mitigation: Document in skill

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1 | S | 20m | 3m | Shell script |
| 2 | XS | 10m | 2m | Hook wiring |
| 3 | S | 20m | -- | CLI command |
| 4 | XS | 10m | -- | Skill update |
| **Total** | **S** | **60m** | -- | |

---

*Plan created: 2026-02-03*
*Plan updated: 2026-02-03 (CLI approach after hook limitation discovered)*
