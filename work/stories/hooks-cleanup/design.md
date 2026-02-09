---
story_id: hooks-cleanup
title: Remove duplicate bash hook telemetry
size: S
complexity: moderate
modules: [mod-telemetry, mod-skills]
---

# Design: Remove Duplicate Bash Hook Telemetry

## What & Why

**Problem:** Two parallel systems write to `signals.jsonl` — bash Stop hooks (`.raise/scripts/log-*.sh`) and CLI telemetry (`raise memory emit-work`). The CLI version is strictly better: Pydantic schemas, file locking, proper error handling. Bash hooks are a vestige from E9 Phase 1.

**Value:** Remove dead code that creates confusion and noise. One telemetry path = simpler mental model, fewer files to maintain, cleaner onboarding.

## Architectural Context

- **mod-telemetry** (bc-observability, lyr-domain): CLI-based telemetry via `raise memory emit-work` — this stays, it's the authoritative path
- **mod-skills** (skill parser/schema/validator/scaffold): Hooks are parsed from SKILL.md frontmatter — these models stay but become unused by distributable skills

## Approach

Remove bash hook infrastructure from three layers:

1. **Distributable skills** (20 SKILL.md files): Strip `hooks:` YAML section from frontmatter
2. **Source skills** (21 SKILL.md files in `.claude/skills/`): Strip `hooks:` YAML section — these are the templates that distributable skills copy from
3. **rai_base/scripts/**: Delete all 5 bash scripts
4. **bootstrap.py**: Remove `_copy_scripts()` function and its call
5. **scaffold.py**: Remove hooks from the skill template
6. **Tests**: Update bootstrap tests (remove `TestBootstrapScripts`), update skill tests that reference hooks

**IMPORTANT: Keep hook infrastructure in code** — `SkillHook`, `SkillHookCommand`, `_parse_hooks()`, `_validate_hook_paths()` remain. They're part of the parser/schema and could be used for future non-telemetry hooks. Removing them now would be over-scoping.

## Components Affected

| Component | Change | Files |
|-----------|--------|-------|
| Distributable skills | Delete `hooks:` block | 20 SKILL.md in `src/raise_cli/skills_base/` |
| Source skills | Delete `hooks:` block | 21 SKILL.md in `.claude/skills/` |
| Bash scripts | Delete | 5 files in `src/raise_cli/rai_base/scripts/` |
| Bootstrap | Delete `_copy_scripts()` + `scripts_copied` field | `onboarding/bootstrap.py` |
| Scaffold | Remove hooks from template | `skills/scaffold.py` |
| Bootstrap tests | Remove `TestBootstrapScripts` class | `tests/onboarding/test_bootstrap.py` |
| Schema tests | Tests still valid (schema stays) | No change needed |
| Parser tests | Tests still valid (parser stays) | No change needed |

## Examples

### Before (SKILL.md frontmatter)
```yaml
---
name: session-start
description: >
  Begin a session...
metadata:
  raise.work_cycle: session
  raise.version: "4.0.0"
hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=session-start \"$CLAUDE_PROJECT_DIR\"/.raise/scripts/log-skill-complete.sh"
---
```

### After (SKILL.md frontmatter)
```yaml
---
name: session-start
description: >
  Begin a session...
metadata:
  raise.work_cycle: session
  raise.version: "4.0.0"
---
```

### Scaffold template (after)
```python
content = dedent(f"""\
    ---
    name: {name}
    description: >
      [TODO: Add description of what this skill does]
    license: MIT
    metadata:
      raise.work_cycle: {lifecycle}
      ...
    ---
""")
# No hooks: section
```

## Acceptance Criteria

**MUST:**
- No `hooks:` sections in any of the 20 distributable SKILL.md files
- No `hooks:` sections in any of the 21 source SKILL.md files
- No bash scripts in `src/raise_cli/rai_base/scripts/`
- `_copy_scripts` removed from bootstrap
- Scaffold template generates skills without hooks
- All tests pass
- `BootstrapResult.scripts_copied` field removed

**SHOULD:**
- Single commit per logical group (skills, infra, tests)

**MUST NOT:**
- Remove `SkillHook`/`SkillHookCommand` models from schema
- Remove hook parsing from parser
- Remove hook validation from validator
- Break existing CLI telemetry (`raise memory emit-work`)
