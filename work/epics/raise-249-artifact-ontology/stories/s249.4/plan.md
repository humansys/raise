# Implementation Plan: epic-design v1.2 — Scope/Design Split

## Overview
- **Story:** S249.4
- **Size:** S
- **Tasks:** 3
- **Derived from:** design.md § Approach + Contract 2 from epic design.md
- **Created:** 2026-02-22

## Tasks

### Task 1: Split Step 10 and add design.md step + templates

**Objective:** Modify SKILL.md so Step 10 produces scope.md (WHAT/WHY only) and a new Step 10.5 produces design.md (HOW/interfaces). Update both templates.

**Changes:**
- **File:** `.claude/skills/rai-epic-design/SKILL.md`
- Step 10: Trim to scope-only content (Objective, Stories, In/Out Scope, Done Criteria, Dependencies)
- New Step 10.5: Create Epic Design Document with Gemba, Target Components, Key Contracts, Migration Path
- Epic Scope Template: Remove Gemba/architecture detail, keep PM content
- Add Epic Design Template: Contract 2b format (Gemba, components, contracts)
- Context § Outputs: Add `design.md` as primary output
- Output section: Add `design.md`

**Size:** S
**Dependencies:** None

### Task 2: Version bump + metadata

**Objective:** Bump version to 1.2.0, update description to reflect dual-artifact output.

**File:** `.claude/skills/rai-epic-design/SKILL.md`
- `raise.version: "1.2.0"`
- Description: mention scope.md + design.md separation

**Size:** XS
**Dependencies:** Task 1

### Task 3: Self-test — verify Contract 2 consumability

**Objective:** Verify that the scope.md template is consumable by epic-plan and the design.md template is consumable by story-design.

**Verification:**
- Read epic-plan SKILL.md — confirm it can find stories table, dependencies in scope.md format
- Read story-design SKILL.md — confirm it references epic design.md for component interfaces
- Walk through Contract 2 format and verify no missing fields

**Size:** XS
**Dependencies:** Task 1, Task 2

## Execution Order
1. Task 1 (core change)
2. Task 2 (metadata)
3. Task 3 (self-test)

## Risks
- Template too verbose → Keep Contract 2 format from epic design.md as-is, already validated

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | XS | -- | |
| 3 | XS | -- | |
