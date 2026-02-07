---
story_id: skill-scaffolding
title: Skill Scaffolding in raise init
type: feature
story_points: 5
complexity: moderate
research: work/research/skill-distribution/
---

# Design: Skill Scaffolding in `raise init`

## What & Why

**Problem:** New users who install `raise-cli` and run `raise init` get base Rai assets (identity, patterns, methodology) but no Claude Code skills. The core DX — `/session-start`, `/discover-*` — is invisible to them.

**Value:** Users can immediately use `/session-start` and the discovery workflow after `raise init`. The onboarding path works end-to-end.

## Approach

### Architecture: Canonical Source with IDE Adapters (PAT-128)

Store distributable skills as canonical markdown in `raise_cli.skills_base` package (alongside `rai_base`). During `raise init`, copy skills to IDE-specific locations via adapter functions.

```
src/raise_cli/
├── rai_base/           # Existing: identity, patterns, methodology
│   ├── identity/
│   ├── memory/
│   └── framework/
│
└── skills_base/        # NEW: distributable skills
    ├── __init__.py     # Package metadata + skill manifest
    ├── session-start/
    │   └── SKILL.md
    ├── discover-start/
    │   └── SKILL.md
    ├── discover-scan/
    │   └── SKILL.md
    ├── discover-validate/
    │   └── SKILL.md
    └── discover-complete/
        └── SKILL.md
```

### Two-Layer Design

```
raise init
│
├── Layer 1: Skills (Claude Code — Phase 1)
│   └── Copy skills_base/* → .claude/skills/
│
└── Layer 2: Rules (Multi-IDE — Phase 2)
    ├── Claude Code  → CLAUDE.md (already exists)
    ├── Cursor       → .cursor/rules/raise.mdc
    ├── Windsurf     → .windsurf/rules/raise.md
    ├── Copilot      → .github/copilot-instructions.md
    └── Universal    → AGENTS.md
```

### Phase 1 (F&F): Claude Code Skills

**Components:**

| Component | Change | Purpose |
|-----------|--------|---------|
| `src/raise_cli/skills_base/` | CREATE | Package with distributable skills |
| `src/raise_cli/onboarding/skills.py` | CREATE | Skill scaffolding logic |
| `src/raise_cli/cli/commands/init.py` | MODIFY | Call skill scaffolding |
| `src/raise_cli/onboarding/bootstrap.py` | MODIFY | Add `skills_copied` to result |

**Flow:**

```python
# In init_command(), after bootstrap_rai_base():
from raise_cli.onboarding.skills import scaffold_skills
skills_result = scaffold_skills(project_path, ide="claude")
```

### Phase 2 (Post-F&F): Multi-IDE Rules

**New option:** `raise init --ide <name>` or auto-detect from project files.

```bash
raise init                     # Claude Code skills (default)
raise init --ide cursor        # + .cursor/rules/raise.mdc
raise init --ide copilot       # + .github/copilot-instructions.md
raise init --ide all           # All detected IDEs
```

**IDE Detection heuristic:**
- `.cursor/` exists → Cursor user
- `.github/` exists → Copilot user
- `.windsurf/` exists → Windsurf user

**Adapter interface:**

```python
class IDEAdapter(Protocol):
    """Generate IDE-specific configuration from canonical skills."""

    def scaffold(self, project_root: Path, skills: list[SkillManifest]) -> SkillResult:
        """Copy/generate skills in IDE-native format."""
        ...
```

**IMPORTANT:** Phase 2 adapter interface is designed but NOT implemented in Phase 1. We only build the Claude adapter now.

## Examples

### CLI Usage

```bash
# Phase 1: Default (Claude Code)
$ raise init
✓ Created .raise/manifest.yaml
✓ Created .raise/rai/ (base Rai)
✓ Created .claude/skills/ (5 skills)

# Phase 2: Multi-IDE
$ raise init --ide cursor
✓ Created .raise/manifest.yaml
✓ Created .raise/rai/ (base Rai)
✓ Created .claude/skills/ (5 skills)
✓ Created .cursor/rules/raise.mdc
```

### Expected File Output (Phase 1)

```
.claude/
└── skills/
    ├── session-start/
    │   └── SKILL.md
    ├── discover-start/
    │   └── SKILL.md
    ├── discover-scan/
    │   └── SKILL.md
    ├── discover-validate/
    │   └── SKILL.md
    └── discover-complete/
        └── SKILL.md
```

### Data Structures

```python
class SkillScaffoldResult(BaseModel):
    """Result of skill scaffolding operation."""
    skills_copied: list[str] = Field(default_factory=list)
    skills_skipped: list[str] = Field(default_factory=list)
    ide_target: str = "claude"  # Phase 2: which IDE adapter was used

# Skill manifest embedded in skills_base/__init__.py
DISTRIBUTABLE_SKILLS: list[str] = [
    "session-start",
    "discover-start",
    "discover-scan",
    "discover-validate",
    "discover-complete",
]
```

### Bootstrap Result Extension

```python
class BootstrapResult(BaseModel):
    # ... existing fields ...
    skills_copied: bool = False      # NEW
    skills_count: int = 0            # NEW
```

## Acceptance Criteria

### MUST

1. `raise init` copies 5 onboarding skills to `.claude/skills/`
2. Copied skills are identical to source (no transformation needed for Phase 1)
3. Existing files are never overwritten (same idempotency as bootstrap)
4. Skills work when invoked as `/session-start`, `/discover-start`, etc. in Claude Code
5. All existing tests pass; new tests cover skill scaffolding

### SHOULD

1. Output messages inform user about copied skills (Shu: detailed, Ri: concise)
2. Architecture supports future IDE adapters without refactoring scaffolding logic
3. `skills_base` package version tracked for future update checks

### MUST NOT

1. Copy lifecycle skills (story-*, epic-*, research) — those are for raise-commons developers
2. Break existing `raise init` behavior for users who don't use Claude Code
3. Hardcode paths — use `importlib.resources` for package assets (same pattern as `rai_base`)

## Design Decisions

### D1: Separate `skills_base` package vs adding to `rai_base`

**Decision:** Separate `skills_base` package.
**Rationale:** Skills and Rai base assets (identity, memory) are conceptually different. Skills are IDE-specific; Rai assets are universal. Separation keeps each package focused and allows independent versioning.

### D2: Copy vs symlink

**Decision:** Copy (not symlink).
**Rationale:** Symlinks break when the package is installed via pip/uv. Copying is what `rai_base` bootstrap does. Idempotent — skip existing files.

### D3: Skills stored in package vs fetched from remote

**Decision:** Stored in package (bundled).
**Rationale:** Offline-first, no network dependency during init. Versioned with the CLI. Same pattern as `rai_base`. Remote sync is Phase 3 (if ever).

### D4: `session-start` parking lot reference

**Decision:** Make optional with conditional check.
**Rationale:** The distributed version should check if `dev/parking-lot.md` exists before referencing it. Add `[if exists]` annotation or remove the hardcoded reference.

### D5: Phase 2 IDE detection — opt-in vs auto-detect

**Decision:** Opt-in via `--ide` flag (Phase 2).
**Rationale:** Auto-detection could generate unwanted files. Explicit is better than implicit for project config generation. Can add `--ide auto` later.

## Portability Notes

Per research (portability analysis):
- 4/5 skills fully portable
- `session-start`: References `dev/parking-lot.md` — must be made optional in distributed version
- Informational references to `work/stories/` in skills are safe (not executable)

## Testing Approach

- Unit tests for `scaffold_skills()` — verify files copied, idempotency, skip existing
- Integration test: `raise init` in temp dir → verify `.claude/skills/` created
- Verify `SKILL.md` content matches source (no corruption)
- Test with `RAI_HOME` override (isolated environment)
