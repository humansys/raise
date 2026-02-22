# Implementation Plan: story-start v1.1 — User Story Artifact

## Overview
- **Story:** S249.5
- **Size:** S
- **Tasks:** 2
- **Derived from:** design.md § New Content: Step 5.5
- **Created:** 2026-02-21

## Tasks

### Task 1: Add Step 5.5 and update SKILL.md

**Objective:** Add User Story artifact step (Contract 3) to story-start skill, update Output and Summary sections, bump version.

**Changes to `.claude/skills/rai-story-start/SKILL.md`:**

1. **Frontmatter:** version `1.2.0` → `1.3.0`
2. **Context § Output:** Add `story.md` bullet: `User Story artifact (Connextra + Gherkin + SbE)`
3. **+Step 5.5: Create User Story Artifact** — insert between Step 5 (Define Scope) and Step 6 (Create Scope Commit):
   - Purpose: produce structured User Story for story-design to consume
   - Depth heuristic table: XS=skip, S=light, M=full, L+=full+notes
   - Contract 3 template: YAML frontmatter + Connextra + Gherkin + SbE + Notes
   - "How story-design consumes it" section
   - Skip condition for XS stories
   - Verification line
4. **Step 6 (Scope Commit):** Update to mention `story.md` is included in the commit (if created)
5. **Output section:** Add `story.md` to output list
6. **Feature Start Summary Template:** Add `story.md` mention

**Verification:**
- Read the modified SKILL.md end-to-end
- Confirm Step 5.5 appears between Step 5 and Step 6
- Confirm Contract 3 template matches epic design.md § Contract 3
- Confirm no language-specific examples (PAT-E-400)
- Confirm version is 1.3.0

**Size:** S
**Dependencies:** None
**AC Reference:** All MUST criteria from design.md § AC

---

### Task 2 (Final): Self-Test — Write Mini User Story Artifact

**Objective:** Validate Contract 3 by producing a sample `story.md` artifact and verifying story-design could consume it.

**What to do:**
- Write a sample `story.md` for a hypothetical story using the new template
- Verify: has YAML frontmatter with required fields (story_id, title, epic_ref, size, status, created)
- Verify: has Connextra format (As a / I want / so that)
- Verify: has at least 1 Gherkin scenario with Given/When/Then
- Verify: has SbE table with concrete values
- Cross-reference with story-design v1.2 Step 5: confirms it can reference `story.md § Acceptance Criteria`

**Output:** Self-test artifact at `work/epics/raise-249-artifact-ontology/stories/s249.5/self-test-contract3.md`

**Size:** XS
**Dependencies:** Task 1

## Execution Order
1. Task 1 (SKILL.md modifications)
2. Task 2 (self-test validation)

## Risks
- Contract 3 template diverges from epic design.md § Contract 3 → Mitigation: cross-reference during Task 1

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | XS | -- | Self-test |
