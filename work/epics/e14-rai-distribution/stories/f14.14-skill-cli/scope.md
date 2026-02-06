# F14.14: Skill CLI Commands

> Deterministic skill management for inference economy.

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
2. **No validation:** Skill structure errors caught late (when AI tries to use them)
3. **Manual naming checks:** Ontology compliance (PAT-132) not enforced

## Research Findings (RES-SKILL-FMT-001)

**Completed:** 2026-02-05 — See `work/research/ai-ide-skill-formats/`

### Key Findings

1. **AGENTS.md is the emerging standard** — Linux Foundation-backed, 20+ tools support it
2. **Common patterns:** Markdown + YAML frontmatter (5/8 tools), glob patterns (4/8)
3. **Zed's approach:** Priority fallback chain across multiple file conventions

### Platform Comparison

| Platform | Location | Format |
|----------|----------|--------|
| Claude Code | `.claude/skills/*/SKILL.md` | YAML + Markdown |
| Cursor | `.cursor/rules/*.mdc` | YAML + Markdown |
| GitHub Copilot | `.github/instructions/*.instructions.md` | YAML + Markdown |
| Zed | `.rules` (with fallback chain) | Plain Markdown |
| Windsurf | `.windsurf/rules/` | Markdown |

### Architecture Decision

**Standards-first approach** (not platform detection):
1. `.claude/skills/` — Claude Code native (F&F target)
2. `.raise/skills/` — RaiSE canonical (future, deferred)
3. AGENTS.md awareness — Deferred, simple to add later

**Rationale:** Claude Code is our target. AGENTS.md handles cross-platform portability when needed. Skip complex platform detection.

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
  story-start    v1.2.0  Initialize feature with branch
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
- [ ] Skill schema (Pydantic model for SKILL.md parsing)
- [ ] Tests for all commands

**SHOULD:**
- [ ] `/skill-create` updated to use new CLI commands

**COULD:**
- [ ] Support `.raise/skills/` as additional location

## Out of Scope

- Platform detection for Cursor/Windsurf/etc (use AGENTS.md for portability)
- Skill execution (that's the AI's job)
- Skill marketplace/sharing
- Remote skill repositories
- Skill versioning/updates

## Done Criteria

- [ ] All four commands implemented
- [ ] Works with `.claude/skills/` directory
- [ ] `/skill-create` updated to use new CLI commands
- [ ] Tests pass (target: 15-20 new tests)
- [ ] Coverage maintained (>90%)
- [ ] Ontology patterns (PAT-130-136) enforced in check-name

---

## Size

**S/M** — New command group, no platform abstraction needed, ~4-6 files

## Dependencies

- F14.13 (ontology cleanup) ✓ — Ontology patterns ready
- `/skill-create` skill — Will be updated to use these commands

## References

- `/skill-create` skill: `.claude/skills/skill-create/SKILL.md`
- Ontology patterns: PAT-130 through PAT-136
- Research: `work/research/ai-ide-skill-formats/README.md`
- Inference economy: CLAUDE.md, Emilio's personal memory
