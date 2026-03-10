# Implementation Plan: S-RESEARCH-GATE

## Overview
- **Story:** S-RESEARCH-GATE
- **Size:** XS
- **Created:** 2026-02-11

## Tasks

### Task 1: Add research gate step to SKILL.md
- **Description:** Add Step 1.7 (Research Gate) between Step 1.5 (Risk Assessment) and Step 2 (Frame What & Why). Conditional: recommended when story touches human interaction. Include criteria for "UX-facing" and reference PAT-E-263.
- **Files:** `.claude/skills/rai-story-design/SKILL.md`, `src/rai_cli/skills_base/rai-story-design/SKILL.md`
- **Verification:** Both files identical after edit, step coherent with surrounding steps
- **Size:** XS
- **Dependencies:** None

### Task 2: Mark parking lot item done
- **Description:** Check the parking lot item (line 165) as complete
- **Files:** `dev/parking-lot.md`
- **Size:** XS
- **Dependencies:** Task 1

### Task 3: Manual integration test
- **Description:** Read the skill end-to-end to verify new step flows naturally
- **Verification:** Step numbering consistent, no broken references
- **Size:** XS
- **Dependencies:** Task 1

## Execution Order
1. Task 1
2. Task 2 + Task 3 (parallel)

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | XS | -- | |
| 2 | XS | -- | |
| 3 | XS | -- | |
