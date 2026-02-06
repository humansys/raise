# Progress: F14.14 Skill CLI Commands

## Status
- **Started:** 2026-02-05 21:30
- **Current Task:** 5 of 9
- **Status:** In Progress (paused)

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

## Remaining Tasks

- Task 5: `raise skill validate` command
- Task 6: `raise skill check-name` command
- Task 7: `raise skill scaffold` command
- Task 8: Update `/skill-create` skill
- Task 9: Manual integration test

## Blockers
- None

## Discoveries
- Rich console.print() corrupts JSON output — use plain print() for JSON
- Pydantic default_factory needs lambda for pyright strict mode
