# Implementation Plan: S15.6 Skills Integration

## Overview
- **Feature:** S15.6
- **Story Points:** 3 SP
- **Feature Size:** S
- **Created:** 2026-02-08

## Tasks

### Task 1: Add Architectural Context Step to /story-design
- **Description:** Insert Step 0.2 "Load Architectural Context" after Step 0.1 (prerequisites) and before Step 1 (complexity assessment). The step instructs Rai to identify the primary module(s) the story affects, run `raise memory context <module>`, and use the returned bounded context, layer, constraints, and dependencies to inform design decisions. Include guidance on how to present an "Architectural Context" section in design output.
- **Files:** `.claude/skills/story-design/SKILL.md`
- **Verification:** Read the modified file, confirm step is present with correct numbering and content
- **Size:** S
- **Dependencies:** None

### Task 2: Add Architectural Context Step to /epic-design
- **Description:** Insert Step 0.6 "Load Architectural Context" after Step 0.5 (query context) and before Step 1 (frame objective). For epics, add guidance to query multiple modules since epics span features. Include "for each candidate module the epic might touch, load its context" instruction.
- **Files:** `.claude/skills/epic-design/SKILL.md`
- **Verification:** Read the modified file, confirm step is present with multi-module guidance
- **Size:** S
- **Dependencies:** None (parallel with Task 1)

### Task 3: Add Architectural Context Step to /story-plan
- **Description:** Insert Step 0.6 "Load Architectural Context" after Step 0.5 (query context) and before Step 1 (select story). Add guidance that architectural context informs task decomposition — tasks that cross bounded contexts should be separate tasks.
- **Files:** `.claude/skills/story-plan/SKILL.md`
- **Verification:** Read the modified file, confirm step is present with task decomposition guidance
- **Size:** S
- **Dependencies:** None (parallel with Tasks 1-2)

### Task 4 (Final): Manual Integration Test
- **Description:** Dogfood the new step by running `raise memory context` for a real module and verifying the output would be useful in a design context. Verify all 3 skills have consistent step structure.
- **Verification:** Run `raise memory context memory` and confirm it returns useful architectural context. Verify all 3 SKILL.md files have the new step in the correct position.
- **Size:** XS
- **Dependencies:** Tasks 1, 2, 3

## Execution Order
1. Tasks 1, 2, 3 (parallel — independent skill files)
2. Task 4 — Manual Integration Test (final validation)

## Risks
- Step numbering conflicts: Mitigate by verifying surrounding step numbers after insertion

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | story-design |
| 2 | S | -- | epic-design |
| 3 | S | -- | story-plan |
| 4 | XS | -- | Integration test |
