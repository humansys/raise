# Implementation Plan: story-design v1.2

## Overview
- **Story:** S249.1
- **Size:** M
- **Type:** Skill content (markdown only, zero code)
- **File:** `.claude/skills/rai-story-design/SKILL.md`
- **Created:** 2026-02-21
- **Derived from:** design.md § 3 (Gemba) + § 4 (New Content Specification)

## Tasks

### Task 1: Add Step 2.5 Gemba Walk

- **Description:** Insert new Step 2.5 between Step 2 (What & Why) and Step 3 (Approach). Contains: purpose, depth heuristic table (XS/S/M/L+), output table template (File/Interface/Changes/Stays), key instruction reinforcing PAT-E-187.
- **File:** `.claude/skills/rai-story-design/SKILL.md`
- **Insert after:** Step 2 (Frame What & Why), before Step 3 (Describe Approach)
- **Verification:** Step 2.5 heading exists; depth heuristic table has 4 rows (XS/S/M/L+); output table template present
- **Size:** S

### Task 2: Adjust Step 3 language

- **Description:** Soften "trust AI for HOW" in Step 3 since HOW is now partially designed via Target Interfaces. Keep the step's core purpose (high-level approach, components affected) but acknowledge that function-level detail comes in Step 3.5.
- **File:** `.claude/skills/rai-story-design/SKILL.md`
- **Verification:** Step 3 no longer says "trust AI to determine implementation details" verbatim; still focuses on WHAT at component level
- **Size:** XS
- **Dependencies:** None (but logically follows Task 1)

### Task 3: Add Step 3.5 Target Interfaces

- **Description:** Insert new Step 3.5 between Step 3 (Approach) and Step 4 (Examples). Three sub-sections: New/Modified Functions (actual Python signatures), New/Modified Models (Pydantic), Integration Points (calls/consumption). Same depth heuristic as Gemba. Key instruction: "actual signatures, not pseudocode."
- **File:** `.claude/skills/rai-story-design/SKILL.md`
- **Insert after:** Step 3 (Describe Approach), before Step 4 (Create Examples)
- **Verification:** Step 3.5 heading exists; 3 sub-sections present; depth heuristic referenced
- **Size:** S
- **Dependencies:** Task 2

### Task 4: Adjust Step 5 (AC from story.md)

- **Description:** Change Step 5 from "Define Acceptance Criteria" to "Reference or Define Acceptance Criteria". Primary path: reference Gherkin from story.md. Fallback: define inline (backward compat when no story.md exists). Add template showing both paths.
- **File:** `.claude/skills/rai-story-design/SKILL.md`
- **Verification:** Step 5 mentions story.md reference; fallback path documented; MUST NOT break when story.md absent
- **Size:** XS
- **Dependencies:** None

### Task 5: Update Inputs, Output, Step 8 checklist + version bump

- **Description:** Four small updates: (1) Add "User Story (story.md) with Gherkin AC" as optional input in Context section. (2) Add Contract 4 output format to Output section. (3) Add Gemba + Target Interfaces items to Step 8 review checklist. (4) Bump version to 1.2.0 in frontmatter.
- **File:** `.claude/skills/rai-story-design/SKILL.md`
- **Verification:** Inputs mention story.md; Output describes Contract 4 structure; Step 8 has Gemba + interfaces checks; frontmatter version = 1.2.0
- **Size:** S
- **Dependencies:** Tasks 1-4

### Task 6: Self-test artifact

- **Description:** Write a mini-example design.md in Contract 4 format for a fictional story, verifying story-plan could consume it. Place in `stories/s249.1/self-test-contract4.md`. This validates the contract is coherent before S2 (story-plan v1.1) starts.
- **File:** `work/epics/raise-249-artifact-ontology/stories/s249.1/self-test-contract4.md`
- **Verification:** Artifact has all 6 Contract 4 sections; Gemba table populated; Target Interfaces have actual signatures; story-plan could derive tasks from it
- **Size:** S
- **Dependencies:** Task 5

### Task 7: Commit + scope tracking update

- **Description:** Stage changes, commit, update scope.md progress tracking in epic.
- **Verification:** Clean git status; commit message references S249.1
- **Size:** XS
- **Dependencies:** Task 6

## Execution Order

1. Task 1 — Gemba Walk step (foundation)
2. Task 2 — Step 3 language adjustment
3. Task 3 — Target Interfaces step
4. Task 4 — Step 5 AC adjustment (parallel with 1-3, but logically after)
5. Task 5 — Inputs/Output/Checklist/Version (needs 1-4 done)
6. Task 6 — Self-test artifact (validates the whole)
7. Task 7 — Commit + tracking

## Risks

- **Over-specifying the Gemba step makes skill too verbose:** Mitigation — depth heuristic keeps XS/S stories light; focus on table format, not prose.
- **Step numbering confusion with .5 insertions:** Mitigation — keep existing step numbers untouched; .5 is a well-understood interpolation pattern in RaiSE skills.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1: Gemba Walk | S | — | |
| 2: Step 3 language | XS | — | |
| 3: Target Interfaces | S | — | |
| 4: Step 5 AC | XS | — | |
| 5: Inputs/Output/Checklist/Version | S | — | |
| 6: Self-test artifact | S | — | |
| 7: Commit + tracking | XS | — | |
