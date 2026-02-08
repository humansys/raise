---
type: module
name: skills
purpose: "Skill management — parsing, locating, validating, and scaffolding SKILL.md files"
status: current
depends_on: []
depended_by: [cli, output]
entry_points:
  - "raise skill list"
  - "raise skill show"
  - "raise skill validate"
  - "raise skill create"
public_api:
  - "Skill"
  - "SkillFrontmatter"
  - "SkillLocator"
  - "parse_skill"
  - "list_skills"
components: 25
constraints:
  - "Skills are markdown files, not Python code — this module manages them, doesn't execute them"
  - "Skill names must follow the ontology naming convention"
  - "No internal dependencies — leaf module"
---

## Purpose

The skills module provides the tooling side of the RaiSE Skills + Toolkit architecture (ADR-012). While **skills themselves** are markdown process guides executed by AI, this module handles the **management operations**: finding skills on disk, parsing their YAML frontmatter, validating their structure, checking naming compliance, and scaffolding new skills from templates.

Think of it as "skill infrastructure" — it doesn't run skills, it helps you create, find, and maintain them.

## Key Files

- **`schema.py`** — Pydantic models for skill structure: `Skill`, `SkillFrontmatter`, `SkillMetadata`, `SkillHook`. Defines the contract that SKILL.md files must follow.
- **`parser.py`** — `parse_skill()` and `parse_frontmatter()` functions. Extract YAML frontmatter and markdown body from SKILL.md files.
- **`locator.py`** — `SkillLocator` class and `list_skills()`. Finds skills in `.claude/skills/` directory, returns typed `Skill` objects.
- **`validator.py`** — Validates skill structure: required fields present, naming convention followed, hooks well-formed.
- **`name_checker.py`** — Enforces ontology-compliant naming (verb-noun pattern, no abbreviations).
- **`scaffold.py`** — Generates new SKILL.md files from templates with proper frontmatter structure.

## Dependencies

None — leaf module. Uses only Pydantic and Python stdlib.

## Conventions

- Skill files live in `.claude/skills/<name>/SKILL.md`
- Frontmatter uses YAML between `---` delimiters
- Skill names use kebab-case: `story-plan`, `discover-scan`, `session-close`
- The `raise.` prefix in frontmatter keys is reserved for RaiSE-specific metadata
