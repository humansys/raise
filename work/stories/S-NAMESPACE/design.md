---
story_id: S-NAMESPACE
title: Add rai- prefix namespace to all distributed skills
size: M
phase: design
modules: [mod-skills_base, mod-onboarding, mod-skills, mod-rai_base]
research: RES-NAMESPACE-001
---

# S-NAMESPACE: Skill Namespace Prefix

## What & Why

**Problem:** RaiSE distributes 20 skills to `.claude/skills/` with generic names (`research`, `debug`, `session-start`). Jumpstart clients and experienced Claude Code users will create or install skills that collide.

**Value:** Pre-publish namespacing (PAT-253) prevents collision at zero migration cost. Post-publish would require migration for every installed user.

## Approach

Mechanical rename: add `rai-` prefix to all skill directory names and update all sync points. Convention follows Agent Skills spec (`[a-z0-9-]` only) and Spec Kit ecosystem precedent (`speckit-specify`, `speckit-plan`).

### Rename Map

**20 distributed skills** (in both `src/rai_cli/skills_base/` and `.claude/skills/`):

| Current | Namespaced |
|---------|-----------|
| `session-start` | `rai-session-start` |
| `session-close` | `rai-session-close` |
| `story-start` | `rai-story-start` |
| `story-design` | `rai-story-design` |
| `story-plan` | `rai-story-plan` |
| `story-implement` | `rai-story-implement` |
| `story-review` | `rai-story-review` |
| `story-close` | `rai-story-close` |
| `epic-start` | `rai-epic-start` |
| `epic-design` | `rai-epic-design` |
| `epic-plan` | `rai-epic-plan` |
| `epic-close` | `rai-epic-close` |
| `discover-start` | `rai-discover-start` |
| `discover-scan` | `rai-discover-scan` |
| `discover-validate` | `rai-discover-validate` |
| `discover-document` | `rai-discover-document` |
| `project-create` | `rai-project-create` |
| `project-onboard` | `rai-project-onboard` |
| `research` | `rai-research` |
| `debug` | `rai-debug` |

**3 non-distributed project-local skills** (`.claude/skills/` only):

| Current | Namespaced |
|---------|-----------|
| `docs-update` | `rai-docs-update` |
| `framework-sync` | `rai-framework-sync` |
| `skill-create` | `rai-skill-create` |

### Components Affected

| Component | Location | Change Type | Count |
|-----------|----------|-------------|-------|
| Skill directories | `src/rai_cli/skills_base/` | Rename | 20 dirs |
| Skill directories | `.claude/skills/` | Rename | 23 dirs |
| SKILL.md frontmatter | Both locations | Edit `name:` field | ~43 files |
| DISTRIBUTABLE_SKILLS | `src/rai_cli/skills_base/__init__.py` | Edit list | 1 file |
| methodology.yaml | `src/rai_cli/rai_base/framework/` | Edit refs | 1 file |
| methodology.yaml | `.raise/rai/framework/` | Edit refs | 1 file |
| Cross-references | SKILL.md bodies + references/ | Edit `/skill-name` refs | ~26 files, ~188 occurrences |
| CLAUDE.md | Root | Edit `/session-start` ref | 1 file |
| CLAUDE.local.md | Root | Edit `/session-start` ref | 1 file |
| Tests | `tests/` | Edit assertions | ~5 files |
| MEMORY.md | `.claude/projects/` | Regenerate | Auto |
| Graph | `.raise/rai/memory/` | Rebuild | Auto |

### Sync Constraints (Poka-Yoke)

1. **Directory ↔ frontmatter `name:`** — MUST match (Agent Skills spec requirement)
2. **DISTRIBUTABLE_SKILLS ↔ directory names** — Scaffolder reads this list to copy skills
3. **methodology.yaml ↔ MEMORY.md** — MEMORY.md auto-generated from methodology.yaml
4. **skills_base/ ↔ .claude/skills/** — Must stay in sync (distributed copies)

## Examples

**Before:**
```
.claude/skills/session-start/SKILL.md
---
name: session-start
description: Begin a session by loading context...
---
```

**After:**
```
.claude/skills/rai-session-start/SKILL.md
---
name: rai-session-start
description: Begin a session by loading context...
---
```

**Invocation change:**
```
# Before
/session-start

# After
/rai-session-start
```

**DISTRIBUTABLE_SKILLS change:**
```python
# Before
DISTRIBUTABLE_SKILLS: list[str] = [
    "session-start",
    "session-close",
    ...
]

# After
DISTRIBUTABLE_SKILLS: list[str] = [
    "rai-session-start",
    "rai-session-close",
    ...
]
```

**Cross-reference change in SKILL.md:**
```markdown
# Before
- Complement: /session-close
- Next skill: /story-design

# After
- Complement: /rai-session-close
- Next skill: /rai-story-design
```

## Acceptance Criteria

### MUST
- All 23 skill directories renamed with `rai-` prefix in their respective locations
- All SKILL.md frontmatter `name:` fields match their directory names
- DISTRIBUTABLE_SKILLS list matches new directory names
- Both methodology.yaml files updated with new skill names
- All cross-references between skills updated (~188 occurrences)
- All tests pass
- Type checks pass
- Linting passes

### SHOULD
- Graph builds successfully after rename
- MEMORY.md regenerated
- No stale references found by final grep sweep (PAT-181)

### MUST NOT
- Leave any un-prefixed skill name in code or config
- Break the scaffolder (skill distribution to new projects)
- Change skill behavior or body content beyond references

## Verification Gate

**Final sweep** (PAT-151, PAT-181): After all renames, grep for old names to catch long tail:
```bash
grep -rn "session-start\|session-close\|story-start\|story-design\|story-plan\|story-implement\|story-review\|story-close\|epic-start\|epic-design\|epic-plan\|epic-close\|discover-start\|discover-scan\|discover-validate\|discover-document\|project-create\|project-onboard" \
  --include="*.py" --include="*.yaml" --include="*.md" \
  src/ .claude/skills/ | grep -v "rai-" | grep -v "work/" | grep -v "__pycache__"
```

Any hits without `rai-` prefix are missed renames.
