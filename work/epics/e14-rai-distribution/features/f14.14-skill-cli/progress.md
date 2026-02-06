# Progress: F14.14 Skill CLI Commands

## Status
- **Started:** 2026-02-05 21:30
- **Completed:** 2026-02-05
- **Status:** Complete

## Completed Tasks

### Task 1: Skill Schema (Pydantic Models)
- **Completed:** 2026-02-05
- **Files:** `src/raise_cli/skills/schema.py`
- **Tests:** 12 passing
- **Notes:** SkillMetadata, SkillFrontmatter, Skill models with from_raw()

### Task 2: Skill Parser
- **Completed:** 2026-02-05
- **Files:** `src/raise_cli/skills/parser.py`
- **Tests:** 12 passing
- **Notes:** parse_frontmatter(), parse_skill(), ParseError

### Task 3: Skill Locator
- **Completed:** 2026-02-05
- **Files:** `src/raise_cli/skills/locator.py`
- **Tests:** 13 passing
- **Notes:** SkillLocator class, find_skill_dirs(), group_by_lifecycle()

### Task 4: `raise skill list` Command
- **Completed:** 2026-02-05
- **Files:** `src/raise_cli/cli/commands/skill.py`, `src/raise_cli/output/formatters/skill.py`
- **Tests:** 6 passing
- **Notes:** Human and JSON output, grouped by lifecycle

### Task 5: `raise skill validate` Command
- **Completed:** 2026-02-05
- **Files:** `src/raise_cli/skills/validator.py`
- **Tests:** 20 passing (13 validator + 7 CLI)
- **Notes:** Validates frontmatter, fields, sections, naming, hooks

### Task 6: `raise skill check-name` Command
- **Completed:** 2026-02-05
- **Files:** `src/raise_cli/skills/name_checker.py`
- **Tests:** 18 passing (12 checker + 6 CLI)
- **Notes:** Pattern, skill conflict, CLI conflict, lifecycle checks

### Task 7: `raise skill scaffold` Command
- **Completed:** 2026-02-05
- **Files:** `src/raise_cli/skills/scaffold.py`
- **Tests:** 16 passing (10 scaffold + 6 CLI)
- **Notes:** Creates SKILL.md from template, infers lifecycle

### Task 8: Update `/skill-create` Skill
- **Completed:** 2026-02-05
- **Files:** `.claude/skills/skill-create/SKILL.md`
- **Notes:** Integrated CLI commands into steps, version 2.0.0

### Task 9: Manual Integration Test
- **Completed:** 2026-02-05
- **Notes:** End-to-end verification of all commands

## Test Summary
- **Total new tests:** 79
- **Full suite:** 1028 passing
- **Coverage:** Maintained >90%

## Discoveries
- Rich console.print() corrupts JSON output — use plain print() for JSON
- Pydantic default_factory needs lambda for pyright strict mode
- `epic-start` skill missing Context section (pre-existing issue)
- `debug` and `research` naming warnings expected (utility skills)
