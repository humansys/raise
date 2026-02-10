# Implementation Plan: BF-2 Architecture Graph Gap

## Overview
- **Story:** BF-2
- **Size:** L
- **Created:** 2026-02-10
- **Tasks:** 7 (5 implementation + 1 skill fix + 1 integration test)

## Tasks

### Task 1: Fix rai_base architecture templates (F1)
- **Description:** Add YAML frontmatter to system-context.md and system-design.md. Create new domain-model.md template. All must match `_parse_architecture_doc` dispatch types.
- **Files:**
  - Modify: `src/raise_cli/rai_base/governance/architecture/system-context.md`
  - Modify: `src/raise_cli/rai_base/governance/architecture/system-design.md`
  - Create: `src/raise_cli/rai_base/governance/architecture/domain-model.md`
- **TDD Cycle:**
  - RED: Template contract test — parse each template through `_parse_architecture_doc`, assert non-None return
  - GREEN: Add frontmatter to templates
  - REFACTOR: Verify `{project_name}` placeholder substitution still works with frontmatter
- **Verification:** `pytest tests/ -k "architecture" --no-header -q`
- **Size:** S
- **Dependencies:** None

### Task 2: Add completeness check to `raise memory validate` (F4)
- **Description:** Extend the existing validate command with a check that expected node types are present (architecture ≥1, module ≥1). Warning only, not hard failure.
- **Files:**
  - Modify: `src/raise_cli/cli/commands/memory.py` (validate function, ~line 554)
- **TDD Cycle:**
  - RED: Test that validate warns when graph has 0 architecture nodes; test it passes when ≥1 present
  - GREEN: Add completeness check after existing structural checks
  - REFACTOR: Clean up
- **Verification:** `pytest tests/cli/commands/test_memory.py -k "validate" --no-header -q`
- **Size:** M
- **Dependencies:** None

### Task 3: Fix /project-onboard skill — architecture templates (F2 partial)
- **Description:** Update Steps 6e/6f to include YAML frontmatter in template examples. Add Step 6g for domain-model.md generation. Correct the false statement at ~line 413 about architecture docs not producing nodes.
- **Files:**
  - Modify: `.claude/skills/project-onboard/SKILL.md`
- **TDD Cycle:** N/A (skill Markdown, no code test). Manual verification: read diff, confirm frontmatter matches parser contract.
- **Verification:** Manual review of diff
- **Size:** M
- **Dependencies:** Task 1 (need to know exact frontmatter format)

### Task 4: Fix /project-onboard skill — module doc generation (F2 + F5)
- **Description:** Add Step 6h: generate `governance/architecture/modules/*.md` for each discovered module. Add graph gate in Step 7: run `raise memory validate` after build, check for completeness warnings.
- **Files:**
  - Modify: `.claude/skills/project-onboard/SKILL.md`
- **TDD Cycle:** N/A (skill Markdown). Manual verification: template matches `_parse_module_doc` expected fields.
- **Verification:** Manual review of diff
- **Size:** M
- **Dependencies:** Task 1, Task 2 (validate must have completeness check for gate)

### Task 5: Fix /project-create skill (F3)
- **Description:** Apply same frontmatter fixes to Steps 6e/6f. Add Step 6g for domain-model.md. No module doc generation (greenfield has no discovery data).
- **Files:**
  - Modify: `.claude/skills/project-create/SKILL.md`
- **TDD Cycle:** N/A (skill Markdown).
- **Verification:** Manual review — confirm templates match project-onboard
- **Size:** S
- **Dependencies:** Task 3 (copy pattern from onboard)

### Task 6: Template contract test
- **Description:** Dedicated test that all `rai_base/governance/architecture/*.md` files have valid YAML frontmatter with `type:` field, and that `_parse_architecture_doc` produces non-None nodes from them.
- **Files:**
  - Create or extend: `tests/context/test_builder_templates.py` (or add to existing builder tests)
- **TDD Cycle:** This IS the test. Write it, run it, confirm green.
- **Verification:** `pytest tests/context/ -k "template" --no-header -q`
- **Size:** S
- **Dependencies:** Task 1 (templates must have frontmatter)

### Task 7 (Final): Manual Integration Test
- **Description:** Run the full pipeline on a temp project: scaffold templates → parse → build graph → validate. Assert architecture and module nodes appear. Verify completeness check passes.
- **Verification:**
  ```bash
  # In raise-commons:
  raise memory build && raise memory validate
  # Check: architecture nodes present, completeness check passes
  ```
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order

1. **Task 1** (templates) + **Task 2** (validate) — parallel, no dependencies
2. **Task 6** (template contract test) — depends on Task 1
3. **Task 3** (onboard skill: architecture) — depends on Task 1
4. **Task 4** (onboard skill: modules + gate) — depends on Tasks 1, 2
5. **Task 5** (create skill) — depends on Task 3
6. **Task 7** (integration test) — depends on all

## Risks

- **Placeholder substitution:** Adding frontmatter to templates may break `{project_name}` replacement in `raise init`. Mitigation: verify in Task 1.
- **Skill drift:** Skills are Markdown instructions for Rai, not executable code. We can't test them automatically. Mitigation: manual review, template contract test covers the data contract.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 - Templates | S | -- | |
| 2 - Validate | M | -- | |
| 3 - Onboard arch | M | -- | |
| 4 - Onboard modules | M | -- | |
| 5 - Create skill | S | -- | |
| 6 - Contract test | S | -- | |
| 7 - Integration | XS | -- | |
