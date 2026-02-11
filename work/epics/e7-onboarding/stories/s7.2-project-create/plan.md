# Implementation Plan: S7.2 — `/project-create` skill

## Overview
- **Feature:** S7.2
- **Story Points:** 8 SP
- **Feature Size:** M
- **Created:** 2026-02-08
- **Design:** `work/epics/e7-onboarding/stories/s7.2-project-create/design.md`

## Tasks

### Task 1: Create SKILL.md with frontmatter and structure
- **Description:** Create `src/rai_cli/skills_base/project-create/SKILL.md` with correct YAML frontmatter (metadata, hooks) and all section headers. This is the skeleton — steps will be filled in Task 2. Follow the standard skill structure from session-start, story-start, etc.
- **Files:**
  - Create: `src/rai_cli/skills_base/project-create/SKILL.md`
- **TDD Cycle:** N/A (skill file, not code) — validate with `uv run rai skill validate .claude/skills/project-create/` after copying
- **Verification:** Frontmatter parses as valid YAML; required fields present (name, description, metadata, hooks); section headers match skill convention
- **Size:** S
- **Dependencies:** None

### Task 2: Write skill steps (conversation flow + doc generation)
- **Description:** Fill the Steps section of SKILL.md with the complete conversation flow from the design:
  - Step 1: Verify prerequisites (governance/ exists, templates have placeholders)
  - Step 2: Collect project identity (name, description)
  - Step 3: Collect goals and requirements (→ RF-XX entries)
  - Step 4: Collect quality constraints (→ guardrails table)
  - Step 5: Collect architecture context (→ system-context, system-design)
  - Step 6: Generate and write governance docs (with parser-compatible format guidance and concrete examples)
  - Step 7: Build graph and verify (`rai memory build`, 30+ nodes gate)
  - Step 8: Summary and next steps
  Each step must include: description, CLI commands where applicable, **Verification** block, and **If you can't continue** recovery guidance. Include concrete output examples showing exact parser-compatible format (RF-XX headings, bold-pipe tables, guardrail ID tables).
- **Files:**
  - Modify: `src/rai_cli/skills_base/project-create/SKILL.md`
- **TDD Cycle:** N/A (skill file) — review against parser regex patterns from design.md
- **Verification:** Each step has verification block; parser contract examples match actual regex in `src/rai_cli/governance/parsers/*.py`; flow is coherent end-to-end
- **Size:** L
- **Dependencies:** Task 1

### Task 3: Register in DISTRIBUTABLE_SKILLS and scaffold locally
- **Description:** Add `"project-create"` to `DISTRIBUTABLE_SKILLS` list in `src/rai_cli/skills_base/__init__.py`. Then run `rai init` on raise-commons to scaffold it to `.claude/skills/project-create/`. Verify the skill file copies correctly.
- **Files:**
  - Modify: `src/rai_cli/skills_base/__init__.py`
  - Created by CLI: `.claude/skills/project-create/SKILL.md`
- **TDD Cycle:** RED: verify skill not yet in distribution list → GREEN: add to list, run scaffold → REFACTOR: N/A
- **Verification:** `grep "project-create" src/rai_cli/skills_base/__init__.py` finds entry; `.claude/skills/project-create/SKILL.md` exists after scaffold; `uv run rai skill validate .claude/skills/project-create/` passes
- **Size:** S
- **Dependencies:** Task 2

### Task 4: Manual Integration Test — dry run on temp project
- **Description:** Validate the skill works end-to-end by simulating the flow:
  1. Create a temp directory
  2. Run `uv run raise init` to scaffold governance templates
  3. Verify templates exist with placeholder content
  4. Read the skill and mentally walk through each step
  5. Manually fill one governance doc (prd.md) following the skill's output examples
  6. Run `uv run rai memory build` and verify governance nodes are extracted
  7. Confirm the parser contract holds — generated content produces graph nodes
- **Verification:** Parser extracts nodes from skill-format content; flow is coherent; no dead-end steps
- **Size:** S
- **Dependencies:** Task 3

## Execution Order
1. Task 1 — skeleton (foundation)
2. Task 2 — steps content (core work, depends on 1)
3. Task 3 — distribution registration (depends on 2)
4. Task 4 — integration test (final validation, depends on 3)

## Risks
- **Parser contract drift:** Generated content format might not match parser regex. **Mitigation:** Task 2 includes concrete examples verified against actual parser source; Task 4 validates with real `rai memory build`.
- **Conversation flow too rigid:** Skill steps might not match how users actually describe projects. **Mitigation:** Steps use open-ended questions, not rigid templates. Shu/Ha/Ri adaptation covers different experience levels.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | Skeleton with frontmatter |
| 2 | L | -- | Core work — conversation flow + examples |
| 3 | S | -- | Registration + scaffold |
| 4 | S | -- | Integration test |
