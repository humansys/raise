---
story_id: RAISE-203
title: Remove raise-commons-specific hardcoding from distributable assets
type: bugfix
size: M
modules: [mod-memory, mod-onboarding]
---

# RAISE-203: Remove raise-commons-specific hardcoding from distributable assets

## Problem

Bundled assets distributed via `rai-cli` (PyPI) contain values specific to the raise-commons project. Users who scaffold new projects get a methodology that references "v2" as their development branch, a skill example that mentions "Emilio" as if he were the current user, and a migration function named after a specific developer. This creates confusion and erodes trust in the framework's generality.

## Value

Users adopting RaiSE get clean, project-agnostic templates from day one. No "who is Emilio?" moments. No "why does it say v2 when my branch is develop?" confusion.

## Approach

Replace hardcoded values with dynamic substitution (branch name) or generic placeholders (examples). Rename developer-specific code to generic equivalents.

### Components affected

| File | Change | What |
|------|--------|------|
| `src/rai_cli/rai_base/framework/methodology.yaml` | **modify** | Replace "v2" with `{development_branch}` placeholder |
| `src/rai_cli/onboarding/memory_md.py` | **modify** | `_add_branches_section()` substitutes placeholder from manifest |
| `src/rai_cli/cli/commands/init.py` | **modify** | Pass `development_branch` to `generate_memory_md()` |
| `src/rai_cli/skills_base/rai-session-close/SKILL.md` | **modify** | Replace "Emilio" with generic "{developer}" in example |
| `src/rai_cli/onboarding/migration.py` | **modify** | Rename `migrate_emilio_profile()` → `migrate_developer_profile()` |
| `src/rai_cli/onboarding/__init__.py` | **modify** | Update import/export |
| `tests/onboarding/test_migration.py` | **modify** | Update function name references |

## Examples

### methodology.yaml — Before

```yaml
branches:
  structure: |
    main (stable)
      └── v2 (development)
            └── epic/e{N}/{name}
                  └── story/s{N}.{M}/{name}
  flow:
    - Stories merge to epic branch
    - Epics merge to development branch (v2)
    - Development merges to main at release
```

### methodology.yaml — After

```yaml
branches:
  structure: |
    main (stable)
      └── {development_branch} (development)
            └── epic/e{N}/{name}
                  └── story/s{N}.{M}/{name}
  flow:
    - Stories merge to epic branch
    - Epics merge to development branch ({development_branch})
    - Development merges to main at release
```

### memory_md.py — _add_branches_section() change

```python
def _add_branches_section(
    self, lines: list[str], methodology: dict[str, Any],
    development_branch: str = "main",
) -> None:
    # ... existing code ...
    structure = branches.get("structure", "")
    if structure:
        structure = structure.replace("{development_branch}", development_branch)
        # ... render as before ...
```

### rai-session-close/SKILL.md — Before

```yaml
next_session_prompt: |
  Emilio mentioned interest in [topic] — if he brings it up, [context].
```

### rai-session-close/SKILL.md — After

```yaml
next_session_prompt: |
  The developer mentioned interest in [topic] — if they bring it up, [context].
```

### migration.py — Rename

```python
# Before
def migrate_emilio_profile(project_path, *, name="Emilio", ...):
    """Create Emilio's profile from existing memory data."""

# After
def migrate_developer_profile(project_path, *, name="Developer", ...):
    """Create developer profile from existing memory data."""
```

## Acceptance Criteria

**MUST:**
- [ ] Generated MEMORY.md uses branch name from `manifest.yaml → branches.development`
- [ ] `methodology.yaml` contains no literal "v2" as branch name
- [ ] No "Emilio" appears as example user in `skills_base/` templates
- [ ] `migrate_emilio_profile` renamed to `migrate_developer_profile` across codebase
- [ ] All existing tests pass

**SHOULD:**
- [ ] Default development branch is "main" when manifest has no `branches.development`

**MUST NOT:**
- [ ] Must not change author credits ("Rai + Emilio", `rai@humansys.ai`) — those are legitimate attributions
- [ ] Must not alter `patterns-base.jsonl` or identity files (already clean)
