# Implementation Plan: S16.4 — Lifecycle Integration

## Overview
- **Feature:** S16.4
- **Story Points:** 2 SP
- **Feature Size:** S
- **Created:** 2026-02-09

## Tasks

### Task 1: Add Step 1.75 to story-close SKILL.md
- **Description:** Insert "Step 1.75: Coherence Check" between Step 1.5 (structural drift) and Step 2 (identify parent branch) in `.claude/skills/story-close/SKILL.md`. The step instructs Rai to invoke `/docs-update` when the story touched code files. Includes skip condition for non-code stories and a commit sub-step for doc changes.
- **Files:** `.claude/skills/story-close/SKILL.md`
- **TDD Cycle:** N/A — this is a Markdown skill definition, not code. Verification is structural review.
- **Verification:** Read the modified SKILL.md and confirm: (1) Step 1.75 exists between 1.5 and 2, (2) skip condition present, (3) `/docs-update` invocation instruction present, (4) commit instruction for doc changes present
- **Size:** S
- **Dependencies:** None

### Task 2: Manual Integration Test
- **Description:** Walk through the story-close skill mentally with a scenario: a story that changed `src/rai_cli/memory/...` files. Verify the step ordering makes sense and the skip condition triggers correctly for a docs-only story.
- **Verification:** Confirm the step flow is coherent end-to-end
- **Size:** XS
- **Dependencies:** Task 1

## Execution Order
1. Task 1 (the edit)
2. Task 2 (validation)

## Risks
- **Step numbering drift:** story-close uses 0.1, 1, 1.5, 2, 3... Adding 1.75 fits the pattern. Low risk.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | XS | -- | |
