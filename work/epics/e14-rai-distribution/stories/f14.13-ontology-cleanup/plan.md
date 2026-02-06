# Implementation Plan: F14.13 Phase 2 — CLI/Skill Ontology Restructure

## Overview
- **Feature:** F14.13 Phase 2
- **Story Points:** 5 SP
- **Feature Size:** M
- **Created:** 2026-02-05

## Summary

Restructure CLI commands to align with domain-centric ontology (Option A):
- Create `raise session` as first-class command group
- Unify `memory add-*` commands into single `memory add --type`
- Remove `raise status` (empty) and `raise telemetry` (merge into memory)
- Update 14 skills to use new CLI paths

## Tasks

### Task 1: Create Session Command Group
- **Description:** Create `cli/commands/session.py` with `start` and `close` subcommands. Reuse existing logic from `profile.py` session commands.
- **Files:**
  - `src/raise_cli/cli/commands/session.py` (new)
  - `src/raise_cli/cli/main.py` (register)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_session.py -v`
- **Size:** M
- **Dependencies:** None

### Task 2: Unify Memory Add Command
- **Description:** Create unified `raise memory add --type <pattern|calibration|session>` command. Merge telemetry emit-* signal writing into memory add with `--emit` flag for backward compat.
- **Files:**
  - `src/raise_cli/cli/commands/memory.py` (refactor add commands)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_memory.py -v`
- **Size:** M
- **Dependencies:** None

### Task 3: Update Session Skills
- **Description:** Update `session-start` and `session-close` skills to use new `raise session start/close` commands instead of `raise profile session-*`.
- **Files:**
  - `.claude/skills/session-start/SKILL.md`
  - `.claude/skills/session-close/SKILL.md`
- **TDD Cycle:** N/A (markdown only)
- **Verification:** Manual: skill syntax valid
- **Size:** S
- **Dependencies:** Task 1

### Task 4: Update Workflow Skills (Telemetry References)
- **Description:** Update all skills that reference `raise telemetry emit-*` to use new `raise memory add --type --emit` pattern. 12 skills affected.
- **Files:**
  - `.claude/skills/epic-start/SKILL.md`
  - `.claude/skills/epic-design/SKILL.md`
  - `.claude/skills/epic-plan/SKILL.md`
  - `.claude/skills/epic-close/SKILL.md`
  - `.claude/skills/story-start/SKILL.md`
  - `.claude/skills/story-design/SKILL.md`
  - `.claude/skills/story-plan/SKILL.md`
  - `.claude/skills/story-implement/SKILL.md`
  - `.claude/skills/story-review/SKILL.md`
  - `.claude/skills/story-close/SKILL.md`
- **TDD Cycle:** N/A (markdown only)
- **Verification:** `grep -r "raise telemetry" .claude/skills/` returns nothing
- **Size:** M
- **Dependencies:** Task 2

### Task 5: Move Scripts Out of Skills
- **Description:** Move `.claude/skills/scripts/` to `dev/scripts/`. Not a skill, misplaced.
- **Files:**
  - `.claude/skills/scripts/` → `dev/scripts/`
  - Update any references
- **TDD Cycle:** N/A (file move)
- **Verification:** `ls .claude/skills/scripts/` should not exist
- **Size:** XS
- **Dependencies:** None

### Task 6: Remove Status Command
- **Description:** Remove `raise status` command (empty, provides no value). Delete command and tests.
- **Files:**
  - `src/raise_cli/cli/commands/status.py` (delete)
  - `src/raise_cli/cli/main.py` (unregister)
  - `tests/cli/commands/test_status.py` (delete)
- **TDD Cycle:** N/A (deletion)
- **Verification:** `raise status` returns "unknown command" error
- **Size:** XS
- **Dependencies:** None

### Task 7: Remove Telemetry Command
- **Description:** Remove `raise telemetry` command group. Functionality merged into memory add.
- **Files:**
  - `src/raise_cli/cli/commands/telemetry.py` (delete)
  - `src/raise_cli/cli/main.py` (unregister)
  - Keep `src/raise_cli/telemetry/` module (schemas, writer)
- **TDD Cycle:** N/A (deletion)
- **Verification:** `raise telemetry` returns "unknown command" error
- **Size:** XS
- **Dependencies:** Task 4 (skills updated first)

### Task 8: Remove Profile Session Commands
- **Description:** Remove `session-start` and `session-end` from profile command group. Only `show` remains.
- **Files:**
  - `src/raise_cli/cli/commands/profile.py` (remove session commands)
  - `tests/cli/commands/test_profile.py` (remove session tests)
- **TDD Cycle:** N/A (deletion)
- **Verification:** `raise profile session-start` returns error
- **Size:** S
- **Dependencies:** Task 3 (skills updated first)

### Task 9: Update Documentation
- **Description:** Update CLAUDE.md, README, and any docs referencing old CLI structure.
- **Files:**
  - `CLAUDE.md` (update CLI tree in architecture section)
  - `README.md` (if CLI examples exist)
- **TDD Cycle:** N/A (docs)
- **Verification:** No references to `raise status`, `raise telemetry`, or `raise profile session`
- **Size:** S
- **Dependencies:** Tasks 6, 7, 8

### Task 10 (Final): Manual Integration Test
- **Description:** Validate complete ontology restructure works end-to-end:
  1. `raise session start` works
  2. `raise session close` works
  3. `raise memory add --type pattern` works
  4. `raise status` fails (removed)
  5. `raise telemetry` fails (removed)
  6. Run `/session-start` skill — uses new CLI
  7. All tests pass
- **Verification:** Demo the story working interactively
- **Size:** S
- **Dependencies:** All previous tasks

## Execution Order

1. **Parallel batch 1:** Tasks 1, 2, 5, 6 (independent)
2. **Sequential:** Task 3 (depends on 1)
3. **Sequential:** Task 4 (depends on 2)
4. **Sequential:** Task 7 (depends on 4)
5. **Sequential:** Task 8 (depends on 3)
6. **Sequential:** Task 9 (depends on 6, 7, 8)
7. **Final:** Task 10

## Risks

| Risk | Mitigation |
|------|------------|
| Breaking skills during transition | Update skills before removing old commands |
| Telemetry module confusion | Keep telemetry module (schemas, writer), only remove CLI |
| Missing test coverage | Add tests for new commands before removing old |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | Session command group |
| 2 | M | -- | Unified memory add |
| 3 | S | -- | Session skills |
| 4 | M | -- | 12 workflow skills |
| 5 | XS | -- | Move scripts |
| 6 | XS | -- | Remove status |
| 7 | XS | -- | Remove telemetry CLI |
| 8 | S | -- | Remove profile session |
| 9 | S | -- | Documentation |
| 10 | S | -- | Integration test |
