# Implementation Plan: S7.3 `/project-onboard` Skill

## Overview
- **Feature:** S7.3
- **Size:** M
- **Epic:** E7
- **Created:** 2026-02-08

## Tasks

### Task 1: Write the `/project-onboard` skill file
- **Description:** Create `.claude/skills/project-onboard/SKILL.md` with the full brownfield onboarding skill. Structure mirrors `/project-create` but adds discovery phases. Three-phase pipeline: discover → converse → generate. Same governance doc parser contracts. Same 30+ node gate.
- **Files:** `.claude/skills/project-onboard/SKILL.md` (create)
- **TDD Cycle:** N/A — skill file is a Markdown document, not code. Validated by integration test in Task 2.
- **Verification:** File exists, YAML frontmatter valid, all 3 phases documented, parser contracts referenced correctly
- **Size:** M
- **Dependencies:** None

### Task 2: Integration test — brownfield walkthrough on temp project
- **Description:** End-to-end validation: create a temp Python project with source files, run `rai init --detect`, then manually walk through the skill steps (discover scan + analyze, verify governance docs generated match parser contracts, run `rai memory build`, verify 30+ nodes). This validates the skill produces real, parseable governance output.
- **Files:** None (manual test in /tmp)
- **TDD Cycle:** N/A — integration test, not unit test
- **Verification:** `rai memory build` on temp project produces 30+ governance nodes after following skill steps
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Manual Integration Test
- **Description:** Demonstrate the full brownfield onboarding workflow working end-to-end. Walk through `/project-onboard` skill on a temp project, show discovery output, governance generation, graph build, and `/session-start` working after onboarding.
- **Verification:** Full walkthrough produces working `/session-start` result
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order
1. Task 1 — Write skill file (foundation)
2. Task 2 — Integration test on temp project (validates skill)
3. Task 3 — Manual integration test (final demo)

## Risks
- Discovery output format may vary across project types: Mitigated by testing with a real Python project structure
- Parser contract drift from S7.2: Mitigated by referencing same format, not duplicating

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | Skill file |
| 2 | S | -- | Integration test |
| 3 | XS | -- | Demo |
