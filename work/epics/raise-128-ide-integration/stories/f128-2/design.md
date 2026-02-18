---
story_id: "F128.2"
title: "Decouple Init from Claude Paths"
epic_ref: "RAISE-128 IDE Integration"
story_points: 5
complexity: "moderate"
status: "draft"
version: "1.0"
created: "2026-02-18"
updated: "2026-02-18"
template: "lean-feature-spec-v2"
---

# Feature: Decouple Init from Claude Paths

> **Epic**: RAISE-128 - IDE Integration
> **Complexity**: moderate | **SP**: 5

---

## 1. What & Why

**Problem**: Four modules hardcode `.claude/skills` and `CLAUDE.md` paths, making it impossible for `rai init` to scaffold for any IDE other than Claude Code.

**Value**: After this refactor, all init-chain functions accept `IdeConfig` and resolve paths from it. `rai init` output is identical (backward compat), but the door is open for F128.3 (Antigravity scaffolding).

---

## 2. Approach

Thread `IdeConfig` through the four coupling points so each resolves paths from config instead of string literals. Default remains `"claude"` everywhere — zero behavior change for existing users.

**Components affected**:
- **`skills/locator.py`** (modify): `get_default_skill_dir()` accepts optional `IdeConfig`
- **`onboarding/skills.py`** (modify): `scaffold_skills()` accepts optional `IdeConfig`
- **`context/builder.py`** (modify): `UnifiedGraphBuilder` accepts optional `IdeConfig`
- **`onboarding/claudemd.py`** (modify): `generate_claude_md()` returns content for any IDE instructions file (content is already IDE-agnostic; no structural change needed here — path resolution happens in `init.py`)

**Architectural context**:
- `mod-skills` (lyr-domain) and `mod-config` (lyr-leaf) are lower layers — changes here propagate upward
- `mod-onboarding` (lyr-integration) and `mod-context` (lyr-integration) consume the lower layers
- Dependency flow respects layer rules: integration → domain → leaf

**Scope correction from gemba**: `config/paths.py:get_claude_memory_path()` is for IDE **user-state** directories (`~/.claude/projects/...`), not project structure. Excluded from F128.2 — it correctly remains Claude-specific.

---

## 3. Interface / Examples

### API Usage — get_default_skill_dir

```python
from rai_cli.skills.locator import get_default_skill_dir
from rai_cli.config.ide import get_ide_config

# Default (backward compat) — identical to current behavior
skill_dir = get_default_skill_dir(project_root=Path("/home/user/project"))
# => Path("/home/user/project/.claude/skills")

# With explicit IDE config
config = get_ide_config("antigravity")
skill_dir = get_default_skill_dir(project_root=Path("/home/user/project"), ide_config=config)
# => Path("/home/user/project/.agent/skills")
```

### API Usage — scaffold_skills

```python
from rai_cli.onboarding.skills import scaffold_skills
from rai_cli.config.ide import get_ide_config

# Default (backward compat)
result = scaffold_skills(project_root=Path("/home/user/project"))
# Scaffolds to .claude/skills/ as before

# With Antigravity
config = get_ide_config("antigravity")
result = scaffold_skills(project_root=Path("/home/user/project"), ide_config=config)
# Scaffolds to .agent/skills/
```

### API Usage — UnifiedGraphBuilder

```python
from rai_cli.context.builder import UnifiedGraphBuilder
from rai_cli.config.ide import get_ide_config

# Default (backward compat)
builder = UnifiedGraphBuilder(project_root=Path("/home/user/project"))
# load_skills() reads from .claude/skills/

# With explicit config
config = get_ide_config("antigravity")
builder = UnifiedGraphBuilder(project_root=Path("/home/user/project"), ide_config=config)
# load_skills() reads from .agent/skills/
```

### Data Structures

```python
# Already exists from F128.1 — no changes needed
class IdeConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    ide_type: IdeType
    skills_dir: str             # ".claude/skills" or ".agent/skills"
    instructions_file: str      # "CLAUDE.md" or ".agent/rules/raise.md"
    workflows_dir: str | None   # None or ".agent/workflows"
```

---

## 4. Acceptance Criteria

### Must Have

- [ ] `get_default_skill_dir()` accepts optional `ide_config: IdeConfig` parameter; defaults to Claude
- [ ] `scaffold_skills()` accepts optional `ide_config: IdeConfig` parameter; defaults to Claude
- [ ] `UnifiedGraphBuilder.__init__()` accepts optional `ide_config: IdeConfig` parameter; defaults to Claude
- [ ] `load_skills()` uses `self.ide_config.skills_dir` instead of hardcoded `.claude/skills`
- [ ] `rai init` (no `--ide` flag) produces **identical output** to pre-refactor
- [ ] All existing tests pass without modification (backward compat proof)
- [ ] New unit tests for each refactored function with non-default `IdeConfig`

### Should Have

- [ ] Docstrings updated to reflect IDE-agnostic behavior
- [ ] Log messages use dynamic paths from config (not hardcoded `.claude/skills`)

### Must NOT

- [ ] **MUST NOT** change `get_claude_memory_path()` — it's IDE user-state, not project structure
- [ ] **MUST NOT** add `--ide` flag to CLI yet — that's F128.4
- [ ] **MUST NOT** generate Antigravity-specific files — that's F128.3
- [ ] **MUST NOT** break any existing caller that doesn't pass `ide_config`

---

## References

**Related ADRs**:
- ADR-031: IdeConfig pattern (IDE abstraction via frozen Pydantic model + registry)

**Related Features**:
- F128.1: IDE Configuration Model (Done — provides `IdeConfig`, `get_ide_config()`)
- F128.3: Antigravity Scaffolding (next — consumes the decoupled code)
- F128.4: Init --ide Flag + E2E Tests (wires CLI)

**Dependencies**:
- F128.1 complete (provides `IdeConfig` model and factory)

---

**Template Version**: 2.0 (Lean Feature Spec)
**Created**: 2026-02-18
