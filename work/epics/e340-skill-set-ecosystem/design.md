# Epic Design: Skill Set Ecosystem

| Field | Value |
|-------|-------|
| Scope | `scope.md` |
| Research | `work/research/skill-set-patterns/` |
| AR | PASS WITH QUESTIONS → overlay-only (Q2 resolved) |

## Gemba: Current State

### Files to Modify

| File | Role | Changes |
|------|------|---------|
| `src/rai_cli/onboarding/skills.py` | Main scaffolding logic | Add overlay step after builtin deploy |
| `src/rai_cli/onboarding/skill_manifest.py` | Manifest model | Add `skill_set` field |
| `src/rai_cli/cli/commands/init.py` | CLI entry point | Add `--skill-set` option |
| `.claude/skills/rai-skill-create/SKILL.md` | Skill creation | Target `.raise/skills/{set}/` |
| `src/rai_cli/cli/commands/skill.py` | Scaffold CLI | Add `--set` option |

### Key Contracts

**`scaffold_skills()` new signature:**
```python
def scaffold_skills(
    project_root: Path,
    *,
    agent_config: AgentConfig | None = None,
    plugin: AgentPlugin | None = None,
    force: bool = False,
    skip_updates: bool = False,
    dry_run: bool = False,
    skill_set: str | None = None,     # NEW — None = builtins only
) -> SkillScaffoldResult:
```

**Unified `_copy_skill_tree` (AR R1):**
```python
def _copy_skill_tree(
    source_dir: Path | Traversable,    # CHANGED — accept both
    dest_dir: Path,
    result: SkillScaffoldResult,
    *,
    plugin: AgentPlugin | None = None,
    agent_config: AgentConfig | None = None,
    overwrite: bool = False,
) -> int:
```

**Manifest extension:**
```python
class SkillManifest(BaseModel):
    skill_set: str | None = None   # NEW: which set was last deployed
    # ... existing fields unchanged
```

### Data Flow (Overlay-Only)

```
scaffold_skills(skill_set="my-company")
  │
  ├── Step 1: Deploy builtins → .claude/skills/
  │   (existing three-hash flow, UNCHANGED)
  │
  └── Step 2: Apply overlay (only if skill_set is not None)
      overlay_dir = .raise/skills/{skill_set}/
      for each skill_dir in overlay_dir:
        _copy_skill_tree(skill_dir, .claude/skills/{name}/, overwrite=True)
        manifest.skills[name] = SkillEntry(origin="project", ...)
      manifest.skill_set = skill_set
```

Step 1 is exactly today's code. Step 2 is ~20 lines of new code after the
existing loop. No refactoring of the existing function needed.
