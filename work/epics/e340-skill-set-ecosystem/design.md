# Epic Design: Skill Set Ecosystem

| Field | Value |
|-------|-------|
| Scope | `scope.md` |
| Research | `work/research/skill-set-patterns/` |

## Gemba: Current State

### Files to Modify

| File | Role | Changes |
|------|------|---------|
| `src/rai_cli/onboarding/skills.py` | Main scaffolding logic | Add default/ population + overlay merge |
| `src/rai_cli/onboarding/skill_manifest.py` | Manifest model | Add `skill_set` field to manifest |
| `src/rai_cli/cli/commands/init.py` | CLI entry point | Add `--skill-set` option |
| `src/rai_cli/skills_base/__init__.py` | Builtin list | No changes needed |
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
    skill_set: str = "default",       # NEW
) -> SkillScaffoldResult:
```

**New internal function:**
```python
def _copy_skill_tree_path(
    source_dir: Path,           # filesystem Path (not Traversable)
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
    skill_set: str = "default"   # NEW: which set was deployed
    # ... existing fields
```

### Data Flow

```
scaffold_skills(skill_set="my-company")
  │
  ├── Step 1: Sync builtins → .raise/skills/default/
  │   (three-hash: DISTRIBUTABLE_SKILLS → default/{name}/SKILL.md)
  │   (stored RAW, no plugin transform)
  │
  ├── Step 2: Build merged skill list
  │   base = list dirs in .raise/skills/default/
  │   if skill_set != "default":
  │     overlay = list dirs in .raise/skills/{skill_set}/
  │     merged = {**base, **overlay}  # same-name wins
  │   else:
  │     merged = base
  │
  └── Step 3: Deploy merged → .claude/skills/
      (plugin transforms applied HERE)
      (manifest updated with origin per skill)
```

### Backward Compatibility

Existing projects have `.claude/skills/` populated directly (no `.raise/skills/default/`).

On first run with new code:
1. `scaffold_skills()` sees `.raise/skills/default/` doesn't exist
2. Creates it from builtins (same three-hash as today)
3. For each skill already in `.claude/skills/`: LEGACY classification
   - If matches builtin → record in manifest, origin: "framework"
   - If differs → record user's hash, origin: "framework" (user modified)
4. Deploys from `.raise/skills/default/` → `.claude/skills/` normally
5. Net effect: no visible change to user, just new intermediate directory
