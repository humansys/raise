# Implementation Plan: F9.3 Skill Emitters

## Overview
- **Feature:** F9.3
- **Epic:** E9 Local Learning
- **Story Points:** 2 SP
- **Feature Size:** S
- **Created:** 2026-02-03
- **Dependencies:** F9.2 Signal Writer (✓ complete)

## Context

**Existing infrastructure:**
- Skills have hooks in SKILL.md frontmatter (PostToolUse, Stop)
- Shell scripts in `.claude/skills/scripts/` handle events
- Currently writes to `.raise/telemetry/events.jsonl` (legacy path)

**Target:**
- Update scripts to write to `.rai/telemetry/signals.jsonl`
- Use SkillEvent schema format from ADR-018
- Track start/complete/abandon with duration

## Story

**As** Rai (the AI partner)
**I want** skill invocations to emit telemetry signals
**So that** I can learn which skills are used and where friction occurs

## Acceptance Criteria

- [ ] `log-skill-start.sh` emits SkillEvent with event="start"
- [ ] `log-skill-complete.sh` emits SkillEvent with event="complete" and duration
- [ ] Signals written to `.rai/telemetry/signals.jsonl`
- [ ] Schema matches ADR-018 SkillEvent format
- [ ] Existing hooks continue to work (no breaking changes)

## Tasks

### Task 1: Update skill scripts to use new telemetry path and schema
- **Description:** Modify shell scripts to write SkillEvent-formatted JSON to `.rai/telemetry/signals.jsonl`
- **Files:**
  - `.claude/skills/scripts/log-skill-start.sh` (modify)
  - `.claude/skills/scripts/log-skill-complete.sh` (modify)
- **Verification:** Run a skill, check `.rai/telemetry/signals.jsonl` has valid SkillEvent
- **Size:** S
- **Dependencies:** None

### Task 2: Add duration tracking between start and complete
- **Description:** Store start timestamp, calculate duration on complete
- **Files:**
  - `.claude/skills/scripts/log-skill-start.sh` (modify)
  - `.claude/skills/scripts/log-skill-complete.sh` (modify)
- **Verification:** Complete event has accurate duration_sec
- **Size:** XS
- **Dependencies:** Task 1

## Execution Order

1. Task 1 (foundation) — Update path and schema
2. Task 2 (enhancement) — Add duration tracking

## Risks

- **Hook environment variables:** May not have all needed context — Mitigation: Use available vars, graceful fallback
- **Duration accuracy:** Depends on start timestamp persistence — Mitigation: Store in temp file per skill invocation

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1 | S | 20m | -- | |
| 2 | XS | 10m | -- | |
| **Total** | **S** | **30m** | -- | |

---

*Plan created: 2026-02-03*
*Next: `/story-implement`*
