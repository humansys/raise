# Implementation Plan: F14.14 Skill CLI Commands

## Overview

- **Feature:** F14.14
- **Story Points:** 5 SP
- **Feature Size:** S/M
- **Created:** 2026-02-05

## Tasks

### Task 1: Create Skill Schema (Pydantic Models)

- **Description:** Create Pydantic models to parse SKILL.md frontmatter. Schema should capture name, description, metadata, hooks structure.
- **Files:**
  - `src/raise_cli/skills/__init__.py` (new module)
  - `src/raise_cli/skills/schema.py` (new)
  - `tests/skills/test_schema.py` (new)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/skills/test_schema.py -v`
- **Size:** M
- **Dependencies:** None

### Task 2: Create Skill Parser

- **Description:** Parse SKILL.md files extracting YAML frontmatter and markdown body. Handle edge cases (missing frontmatter, invalid YAML).
- **Files:**
  - `src/raise_cli/skills/parser.py` (new)
  - `tests/skills/test_parser.py` (new)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/skills/test_parser.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Create Skill Locator

- **Description:** Find skill directories in `.claude/skills/`. List all skills with metadata. No platform detection complexity — just Claude Code for now.
- **Files:**
  - `src/raise_cli/skills/locator.py` (new)
  - `tests/skills/test_locator.py` (new)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/skills/test_locator.py -v`
- **Size:** S
- **Dependencies:** Task 2

### Task 4: Implement `raise skill list` Command

- **Description:** CLI command to list all skills with human/json output. Group by lifecycle, show version and description.
- **Files:**
  - `src/raise_cli/cli/commands/skill.py` (new)
  - `src/raise_cli/cli/commands/__init__.py` (update exports)
  - `src/raise_cli/cli/main.py` (register command)
  - `src/raise_cli/output/formatters/skill.py` (new)
  - `tests/cli/commands/test_skill.py` (new)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_skill.py::test_skill_list -v`
- **Size:** M
- **Dependencies:** Task 3

### Task 5: Implement `raise skill validate` Command

- **Description:** Validate skill structure against schema. Check frontmatter, required fields, hook paths, required sections.
- **Files:**
  - `src/raise_cli/skills/validator.py` (new)
  - `src/raise_cli/cli/commands/skill.py` (add validate command)
  - `tests/skills/test_validator.py` (new)
  - `tests/cli/commands/test_skill.py` (add validate tests)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/skills/test_validator.py -v && pytest tests/cli/commands/test_skill.py::test_skill_validate -v`
- **Size:** M
- **Dependencies:** Task 4

### Task 6: Implement `raise skill check-name` Command

- **Description:** Check proposed skill name against ontology patterns (PAT-130-136). Verify {domain}-{action} pattern, no conflicts with existing skills or CLI commands.
- **Files:**
  - `src/raise_cli/skills/naming.py` (new)
  - `src/raise_cli/cli/commands/skill.py` (add check-name command)
  - `tests/skills/test_naming.py` (new)
  - `tests/cli/commands/test_skill.py` (add check-name tests)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/skills/test_naming.py -v && pytest tests/cli/commands/test_skill.py::test_skill_check_name -v`
- **Size:** S
- **Dependencies:** Task 4

### Task 7: Implement `raise skill scaffold` Command

- **Description:** Generate new SKILL.md from template file (`.raise/templates/skill.md`). Template uses `{{placeholder}}` syntax for substitution. Scaffold validates name before generating.
- **Files:**
  - `src/raise_cli/skills/scaffold.py` (new)
  - `src/raise_cli/cli/commands/skill.py` (add scaffold command)
  - `tests/skills/test_scaffold.py` (new)
  - `tests/cli/commands/test_skill.py` (add scaffold tests)
- **Template:** `.raise/templates/skill.md` (already created)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/skills/test_scaffold.py -v && pytest tests/cli/commands/test_skill.py::test_skill_scaffold -v`
- **Size:** M
- **Dependencies:** Task 6 (uses check-name for validation)

### Task 8: Update `/skill-create` Skill

- **Description:** Update the `/skill-create` skill to use new CLI commands instead of manual file operations.
- **Files:**
  - `.claude/skills/skill-create/SKILL.md` (update)
- **TDD Cycle:** N/A (documentation update)
- **Verification:** Manual — invoke `/skill-create` and verify it uses CLI commands
- **Size:** XS
- **Dependencies:** Task 7

### Task 9 (Final): Manual Integration Test

- **Description:** Validate all four commands work end-to-end with actual skills directory.
- **Verification:**
  - `uv run raise skill list` shows all 20 skills grouped by lifecycle
  - `uv run raise skill validate` validates all skills
  - `uv run raise skill check-name test-skill` gives correct feedback
  - `uv run raise skill scaffold test-skill --lifecycle utility` creates valid SKILL.md
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order

1. Task 1 — Schema (foundation)
2. Task 2 — Parser (depends on 1)
3. Task 3 — Locator (depends on 2)
4. Task 4 — `list` command (depends on 3)
5. Task 5, Task 6 — `validate` and `check-name` (parallel, depend on 4)
6. Task 7 — `scaffold` (depends on 6)
7. Task 8 — Update `/skill-create` (depends on 7)
8. Task 9 — Integration test (final)

## Risks

- **YAML parsing edge cases:** Mitigation — use pyyaml/ruamel.yaml, test with real SKILL.md files
- **Ontology pattern evolution:** Mitigation — patterns stored in code, easy to update

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | Schema models |
| 2 | S | -- | Parser |
| 3 | S | -- | Locator |
| 4 | M | -- | list command |
| 5 | M | -- | validate command |
| 6 | S | -- | check-name command |
| 7 | M | -- | scaffold command |
| 8 | XS | -- | skill-create update |
| 9 | XS | -- | Integration test |

**Estimated total:** ~15-20 tests, 4-6 new files
