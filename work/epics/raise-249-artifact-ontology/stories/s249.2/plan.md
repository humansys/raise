# Implementation Plan: story-plan v1.1 — SDLD Task Blueprints

## Overview
- **Story:** S249.2
- **Size:** M
- **Tasks:** 5
- **Derived from:** design.md § Target Interfaces
- **Created:** 2026-02-21

## Tasks

### Task 1: Restructure Step 2 — SDLD Blueprint task format

**Objective:** Replace the generic task structure in Step 2 with RED/GREEN paired sections that consume Contract 4.

**What to change in SKILL.md Step 2:**
- Replace the current task structure block (Description/Files/TDD Cycle/Verification/Size/Dependencies) with the SDLD Blueprint format
- RED section: test file, test function name, Given/When/Then from Gherkin, code sketch
- GREEN section: implementation file, function signature from Contract 4, integration point
- Each task gets **Objective**, **AC Reference** fields
- Keep: task granularity guidance table, t-shirt sizing guide, final Integration Test pattern
- Add explicit instruction: "Derive task deliverables from design.md § Target Interfaces"

**Files:** `.claude/skills/rai-story-plan/SKILL.md` (Step 2 section)

**Verification:** Step 2 contains RED/GREEN paired format; old generic format removed; Final Integration Test pattern preserved.

**Size:** M
**Dependencies:** None

---

### Task 2: Add depth heuristic table

**Objective:** Add a depth heuristic so blueprint detail scales with story size (XS=lightweight → M+=full SDLD).

**What to add after the new task format in Step 2:**
- Depth heuristic table (4 rows: XS/S/M/L)
- XS: test name + assertion only / function name + file only
- S: test sketch (Given/When/Then) / signature + file + integration
- M+: full test code sketch / full signature + imports + integration
- Instruction: "Apply depth heuristic BEFORE writing tasks"

**Files:** `.claude/skills/rai-story-plan/SKILL.md` (Step 2 section, after task format)

**Verification:** Depth heuristic table present with 4 size rows; each row specifies RED and GREEN depth.

**Size:** S
**Dependencies:** Task 1

---

### Task 3: Add Traceability Table to Step 6

**Objective:** Add traceability table format that maps every AC scenario to tasks and back to design sections.

**What to add in Step 6 (Document Plan):**
- Traceability table format: `| AC Scenario | Task(s) | Design § |`
- Instruction: "Every AC scenario MUST map to at least one task"
- Instruction: "Every task MUST reference an AC scenario"

**Files:** `.claude/skills/rai-story-plan/SKILL.md` (Step 6 section)

**Verification:** Traceability table format defined; bidirectional mapping instruction present.

**Size:** S
**Dependencies:** None (parallel with Task 1-2)

---

### Task 4: Update Plan Template + metadata + Context section

**Objective:** Sync the Plan Template section at the bottom of SKILL.md with the new SDLD format. Update frontmatter version and Context inputs.

**What to change:**
- Plan Template: replace generic task structure with SDLD Blueprint example (using platform-agnostic code — 5+ languages in comments)
- Plan Template: add Traceability table to template
- Frontmatter: version `1.0.0` → `1.1.0`
- Context § Inputs: add "Story Design (Contract 4) for function signatures and Gemba state"
- Context § Output description: mention "SDLD Task Blueprints" not just "implementation plan"

**Files:** `.claude/skills/rai-story-plan/SKILL.md` (Plan Template section, frontmatter, Context section)

**Verification:** Template matches new format; version is 1.1.0; Context references Contract 4; all code examples show multiple languages.

**Size:** S
**Dependencies:** Tasks 1, 2, 3 (template must reflect all changes)

---

### Task 5 (Final): Self-test — produce Contract 5 sample

**Objective:** Validate the new format works by producing a sample plan.md from S249.1's self-test-contract4.md. This proves story-plan v1.1 can consume Contract 4 and produce Contract 5.

**What to do:**
- Read `self-test-contract4.md` (the "export command" example design)
- Apply the new SKILL.md format to produce `self-test-contract5.md`
- The sample should have 3-4 tasks with RED/GREEN pairs derived from the Contract 4 Target Interfaces
- Include traceability table mapping the 4 AC items to tasks
- Use platform-agnostic language (TypeScript, matching the Contract 4 example)

**Files:** `work/epics/raise-249-artifact-ontology/stories/s249.2/self-test-contract5.md` (new)

**Verification:** Self-test artifact exists; tasks derive from Contract 4 signatures; traceability covers all 4 AC items; story-implement could execute these tasks mechanically.

**Size:** S
**Dependencies:** Tasks 1-4

## Execution Order

1. Task 1 — Step 2 restructure (foundation — all other tasks depend on this format)
2. Task 2 — Depth heuristic (extends Step 2)
3. Task 3 — Traceability table (can overlap with T1-T2 conceptually, but sequential for clean commits)
4. Task 4 — Template + metadata sync (must reflect T1-T3)
5. Task 5 — Self-test (validates everything works end-to-end)

## Traceability

| AC (from design.md) | Task(s) | Design § |
|---------------------|---------|----------|
| RED/GREEN paired sections | T1 | Target Interfaces → Target Task Format |
| RED includes test file, function, Given/When/Then, code sketch | T1 | Target Interfaces → RED section |
| GREEN includes file, signature from Contract 4, integration | T1 | Target Interfaces → GREEN section |
| Each task references AC scenario | T1 | Target Interfaces → AC Reference field |
| Traceability table maps AC → tasks | T3 | Target Interfaces → Traceability Table |
| Depth heuristic by story size | T2 | Target Interfaces → Depth Heuristic |
| Platform-agnostic examples (PAT-E-400) | T4 | Constraints |
| Plan Template updated | T4 | AC → SHOULD |
| Context references Contract 4 | T4 | AC → SHOULD |
| Self-test from Contract 4 input | T5 | Constraints |

## Risks

- **Over-specifying the template:** Keep examples minimal — show the structure, not a full real-world plan. Mitigation: one example per section, comments for language variants.
- **Template drift from Step 2:** Template and Step 2 define the same format in two places. Mitigation: Task 4 explicitly syncs them; add a note in SKILL.md that template must match Step 2.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | |
| 2 | S | -- | |
| 3 | S | -- | |
| 4 | S | -- | |
| 5 | S | -- | Self-test |

---

*Plan derived from: design.md § Target Interfaces + Gemba of SKILL.md v1.0.0*
*Next: `/rai-story-implement`*
