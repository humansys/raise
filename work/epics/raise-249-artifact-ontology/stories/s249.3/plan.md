# Implementation Plan: epic-start v1.1 — Epic Brief Artifact

## Overview
- **Story:** S249.3
- **Size:** S
- **Tasks:** 2
- **Derived from:** design.md § Gemba + epic design.md § Contract 1
- **Created:** 2026-02-22

## Tasks

### Task 1: Add Step 3.5 and update SKILL.md

**Objective:** Add Epic Brief artifact step (Contract 1) to epic-start skill, update Output and Summary, bump version.

**Changes to `.claude/skills/rai-epic-start/SKILL.md`:**

1. **Frontmatter:** version `1.0.0` → `1.1.0`
2. **Context § Output:** Add `brief.md` bullet
3. **+Step 3.5: Create Epic Brief Artifact** — insert between Step 3 (Define Scope) and Step 4 (Scope Commit):
   - Purpose: produce structured Epic Brief for epic-design to consume
   - Contract 1 template: YAML frontmatter + Hypothesis (SAFe) + Success Metrics + Appetite (Shape Up) + Scope Boundaries (In MUST/SHOULD, No-Gos, Rabbit Holes)
   - "How epic-design consumes it" section
   - Artifact location: `work/epics/{epic-id}/brief.md`
4. **Step 4 (Scope Commit):** Mention `brief.md` included in commit
5. **Output section:** Add `brief.md`
6. **Summary Template:** Add brief mention

**Verification:** Read modified SKILL.md, confirm Step 3.5 between Step 3 and Step 4, Contract 1 matches epic design.md.

**Size:** S
**Dependencies:** None

---

### Task 2 (Final): Self-Test — Write Mini Epic Brief Artifact

**Objective:** Validate Contract 1 by producing a sample `brief.md` and verifying epic-design could consume it.

**What to do:**
- Write sample brief.md for a hypothetical epic
- Verify: YAML frontmatter with epic_id, title, status, created
- Verify: Hypothesis in SAFe format, Success Metrics, Appetite, Scope Boundaries
- Cross-reference with epic design.md § Contract 1 consumption points

**Output:** Self-test at `work/epics/raise-249-artifact-ontology/stories/s249.3/self-test-contract1.md`

**Size:** XS
**Dependencies:** Task 1

## Execution Order
1. Task 1 (SKILL.md modifications)
2. Task 2 (self-test validation)

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | XS | -- | Self-test |
