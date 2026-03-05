# Implementation Plan: RAISE-243 rai-skill-create

## Overview
- **Story:** RAISE-243
- **Size:** M
- **Created:** 2026-02-20
- **Design:** `raise-243-design.md`

## Note on TDD

This story produces a SKILL.md file, not source code. There are no unit tests to write. Validation is via `rai skill validate` and manual integration test (create a skill using the creator).

## Tasks

### Task 1: Write SKILL.md frontmatter
- **Description:** Create `.claude/skills/rai-skill-create/SKILL.md` with complete YAML frontmatter: name, description, license, metadata (work_cycle: meta, frequency: on-demand, fase: 0), visibility: internal
- **Files:** `.claude/skills/rai-skill-create/SKILL.md`
- **Verification:** YAML parses correctly, metadata fields match schema
- **Size:** XS
- **Dependencies:** None

### Task 2: Write Purpose, Mastery, and Context sections
- **Description:** Define why the skill exists, ShuHaRi levels, when to use/skip, inputs, and outputs. Reference the design spec for flow and approach.
- **Files:** `.claude/skills/rai-skill-create/SKILL.md`
- **Verification:** Sections present and substantive (no TODOs)
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Write Steps section (core logic)
- **Description:** The main content — 8 steps as defined in design:
  1. Understand skill purpose (conversational)
  2. Derive and validate name (`rai skill check-name`)
  3. Determine lifecycle position (prerequisites, next, gate)
  4. Read reference skills for domain patterns (`rai skill list`, then read SKILL.md)
  5. Design skill content (Purpose, Context, Steps, Output) through conversation
  6. Write complete SKILL.md (frontmatter + body)
  7. Validate (`rai skill validate`)
  8. Present summary and next steps
  Each step needs: description, CLI commands (where applicable), verification gate, "If you can't continue" blocker.
- **Files:** `.claude/skills/rai-skill-create/SKILL.md`
- **Verification:** All 8 steps present with verification gates
- **Size:** L
- **Dependencies:** Task 2

### Task 4: Write Output, Notes, and References sections
- **Description:** Document deliverables table, design philosophy notes (orchestration not generation), reference skills list, and link to complement skills.
- **Files:** `.claude/skills/rai-skill-create/SKILL.md`
- **Verification:** All required sections present (Purpose, Context, Steps, Output)
- **Size:** XS
- **Dependencies:** Task 3

### Task 5: Validate and integration test
- **Description:** Run `rai skill validate` on the completed SKILL.md. Then manually test by invoking `/rai-skill-create` to create a throwaway test skill. Verify the creator guides through the full flow and produces a valid SKILL.md.
- **Files:** `.claude/skills/rai-skill-create/SKILL.md` (fixes from validation)
- **Verification:** `rai skill validate .claude/skills/rai-skill-create/SKILL.md` exits 0. Manual test produces a valid skill.
- **Size:** S
- **Dependencies:** Task 4

## Execution Order

```
Task 1 (frontmatter) → Task 2 (purpose/context) → Task 3 (steps) → Task 4 (output/notes) → Task 5 (validate + test)
```

Linear — each task extends the same file sequentially.

## Risks

| Risk | Mitigation |
|------|------------|
| Steps section too long/complex | Keep each step focused — CLI command OR conversation, not both |
| Skill reads awkwardly as instructions | Review from perspective of "Rai reading this to guide a human" |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1 - Frontmatter | XS | -- | |
| 2 - Purpose/Context | S | -- | |
| 3 - Steps | L | -- | Core logic |
| 4 - Output/Notes | XS | -- | |
| 5 - Validate + test | S | -- | |
