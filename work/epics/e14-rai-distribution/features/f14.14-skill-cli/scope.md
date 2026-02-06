# F14.14: Skill CLI Commands

> Platform-agnostic skill management for inference economy.

## Context

The `/skill-create` meta-skill currently requires AI inference to:
- List existing skills (scan directories)
- Check naming conflicts (query memory + scan)
- Generate templates (copy from doc)
- Validate structure (parse and check)

Per inference economy principle: **gather with tools, think with inference.**

These operations should be deterministic CLI commands.

## Problem Statement

1. **Inference waste:** AI spends tokens discovering what CLI could report instantly
2. **Platform coupling:** Current skills assume `.claude/skills/` (Claude Code specific)
3. **No validation:** Skill structure errors caught late (when AI tries to use them)
4. **Manual naming checks:** Ontology compliance (PAT-132) not enforced

## Research Needed

### Platform Skill Formats

| Platform | Skill Location | Format | Research Status |
|----------|---------------|--------|-----------------|
| Claude Code | `.claude/skills/` | SKILL.md (YAML+Markdown) | Known |
| Cursor | `.cursor/` ? | Unknown | Needs research |
| Windsurf | ? | Unknown | Needs research |
| Continue.dev | `.continue/` ? | Unknown | Needs research |
| Generic | `.raise/skills/` ? | RaiSE native | To define |

**Key question:** Should RaiSE skills be platform-specific (`.claude/skills/`) or have a canonical location (`.raise/skills/`) with platform adapters?

### Research Tasks

1. How do Cursor, Windsurf, Continue.dev handle custom skills/prompts?
2. Is there an emerging standard for AI tool skills?
3. What's the minimal common format across platforms?

---

## Proposed Solution

### CLI Command Group

```
raise skill
├── list                    # List skills with metadata
├── scaffold <name>         # Generate SKILL.md template
├── validate [path]         # Validate skill structure
└── check-name <name>       # Check naming against conventions
```

### Platform Abstraction

```python
# Detect platform and resolve skill paths
class SkillLocator:
    def detect_platform(self) -> Platform
    def get_skill_dirs(self) -> list[Path]
    def get_canonical_dir(self) -> Path  # .raise/skills/ fallback
```

**Priority order:**
1. Platform-specific (`.claude/skills/`, `.cursor/`, etc.)
2. RaiSE canonical (`.raise/skills/`)
3. Legacy (if any)

---

## Features

### `raise skill list`

List all discovered skills across platform directories.

**Output (human):**
```
Skills (20 found)

Lifecycle: session
  session-start    v3.0.0  Load memory, propose focus
  session-close    v2.0.0  Capture learnings, update memory

Lifecycle: feature
  feature-start    v1.2.0  Initialize feature with branch
  ...

Platform: .claude/skills/ (Claude Code)
```

**Output (json):**
```json
{
  "skills": [
    {
      "name": "session-start",
      "version": "3.0.0",
      "lifecycle": "session",
      "path": ".claude/skills/session-start/SKILL.md"
    }
  ],
  "platform": "claude-code",
  "skill_dir": ".claude/skills/"
}
```

### `raise skill scaffold <name>`

Generate a new skill with proper structure.

```bash
raise skill scaffold feature-validate
```

Creates:
```
.claude/skills/feature-validate/
└── SKILL.md  # Template with correct frontmatter, hooks, sections
```

**Options:**
- `--lifecycle <session|epic|feature|discovery|utility|meta>`
- `--after <skill-name>` — Set prerequisites
- `--before <skill-name>` — Set next

### `raise skill validate [path]`

Validate skill structure against RaiSE schema.

```bash
# Validate specific skill
raise skill validate .claude/skills/my-skill/SKILL.md

# Validate all skills
raise skill validate
```

**Checks:**
- [ ] YAML frontmatter present and valid
- [ ] Required fields (name, description, metadata)
- [ ] Hook paths exist (`.raise/scripts/log-skill-complete.sh`)
- [ ] Required sections (Purpose, Context, Steps, Output)
- [ ] Naming convention (`{domain}-{action}`)

**Output:**
```
Validating: .claude/skills/my-skill/SKILL.md

✓ Frontmatter valid
✓ Required fields present
✗ Hook path not found: .raise/scripts/log-skill-complete.sh
✓ Required sections present
⚠ Name 'do-thing' doesn't follow {domain}-{action} pattern

1 error, 1 warning
```

### `raise skill check-name <name>`

Check proposed skill name against ontology patterns.

```bash
raise skill check-name session-validate
```

**Checks:**
- [ ] Follows `{domain}-{action}` pattern
- [ ] No conflict with existing skills
- [ ] No conflict with CLI commands (PAT-132)
- [ ] Domain exists in known lifecycles

**Output:**
```
Checking name: session-validate

✓ Follows {domain}-{action} pattern
✓ No conflict with existing skills
✓ No CLI command conflict
✓ Domain 'session' is a known lifecycle

Name 'session-validate' is valid.

Suggestion: Position after 'session-start', before 'session-close'
```

---

## In Scope

**MUST:**
- [ ] `raise skill list` with human/json output
- [ ] `raise skill scaffold <name>` with template generation
- [ ] `raise skill validate` for structure checking
- [ ] `raise skill check-name` for ontology compliance
- [ ] Platform detection (Claude Code at minimum)
- [ ] Tests for all commands

**SHOULD:**
- [ ] Support `.raise/skills/` as fallback location
- [ ] Skill schema validation (Pydantic model)

**COULD:**
- [ ] Multi-platform detection (Cursor, Windsurf)
- [ ] Skill migration between platforms

## Out of Scope

- Skill execution (that's the AI's job)
- Skill marketplace/sharing
- Remote skill repositories
- Skill versioning/updates

## Done Criteria

- [ ] All four commands implemented
- [ ] Platform detection works for Claude Code
- [ ] `/skill-create` updated to use new CLI commands
- [ ] Tests pass (target: 15-20 new tests)
- [ ] Coverage maintained (>90%)
- [ ] Ontology patterns (PAT-130-136) enforced in check-name

---

## Size

**M** — New command group, platform abstraction, ~5-8 files

## Dependencies

- F14.13 (ontology cleanup) — For ontology patterns to enforce
- `/skill-create` skill — Will be updated to use these commands

## References

- `/skill-create` skill: `.claude/skills/skill-create/SKILL.md`
- Ontology patterns: PAT-130 through PAT-136
- Inference economy: CLAUDE.md, Emilio's personal memory
