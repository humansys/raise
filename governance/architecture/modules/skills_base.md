---
type: module
name: skills_base
purpose: "Distributable skill collection — the 21 SKILL.md files that ship with raise-cli"
status: current
depends_on: []
depended_by: [onboarding]
entry_points: []
public_api:
  - "DISTRIBUTABLE_SKILLS"
  - "__version__"
components: 0
constraints:
  - "No internal dependencies — distribution package"
  - "Skills are copied to .claude/skills/ on raise init, not imported at runtime"
  - "Adding a skill here makes it available to all new projects"
---

## Purpose

The skills_base module packages the 21 RaiSE skills that ship with raise-cli. On `rai init`, the onboarding module copies these SKILL.md files into the project's `.claude/skills/` directory. After that, they're independent — the project's copies can be customized without affecting the base.

The `DISTRIBUTABLE_SKILLS` constant lists all included skills: session lifecycle (session-start, session-close), story lifecycle (story-start, story-design, story-plan, story-implement, story-review, story-close), epic lifecycle (epic-design, epic-plan, epic-start, epic-close), discovery (discover-start, discover-scan, discover-validate, discover-complete), and tools (research, debug).

## Key Files

- **`__init__.py`** — Exports `DISTRIBUTABLE_SKILLS` list and `__version__`
- **`skills/`** — Individual skill directories, each containing a `SKILL.md` file

## Dependencies

None — data-only package. Content is accessed via `importlib.resources`.

## Conventions

- Each skill lives in `skills/<name>/SKILL.md` with YAML frontmatter
- `DISTRIBUTABLE_SKILLS` must be updated when adding or removing skills
- Skills follow the RaiSE skill schema (validated by the `skills` module)
- Version tracked separately from `rai_base` since skill content evolves independently
