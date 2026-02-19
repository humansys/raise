---
id: RAISE-197
title: "Standardize IDE abstraction — multi-IDE instructions generator"
size: L
complexity: moderate
modules: [mod-onboarding, mod-config, mod-cli]
depends_on: [RAISE-128]
---

# RAISE-197: Standardize IDE Abstraction Layer

## Problem

RAISE-128 introduced IDE abstraction with `IdeConfig` for Claude and Antigravity, but:
1. Module naming is Claude-specific (`claudemd.py`, `ClaudeMdGenerator`)
2. The generator produces a generic stub, not the real projection from `.raise/` canonical source (ADR-012)
3. Only 2 of 5 market-relevant IDEs are supported
4. `--ide` accepts only one value — teams use multiple IDEs
5. No auto-detection of installed IDEs

## Value

Every developer on the team (and Kurigage clients) gets a correctly configured IDE from a single `rai init --detect`, regardless of which IDE they use. The team can validate all 5 IDEs this week.

## Approach

### 1. Rename `claudemd.py` → `instructions.py`

- `ClaudeMdGenerator` → `InstructionsGenerator`
- `generate_claude_md()` → `generate_instructions()`
- Update all imports across codebase

### 2. Expand IdeType registry to 5 IDEs

```python
IdeType = Literal["claude", "cursor", "windsurf", "copilot", "antigravity"]

IDE_CONFIGS: dict[IdeType, IdeConfig] = {
    "claude": IdeConfig(
        ide_type="claude",
        skills_dir=".claude/skills",
        instructions_file="CLAUDE.md",
        detection_markers=["CLAUDE.md", ".claude"],
    ),
    "cursor": IdeConfig(
        ide_type="cursor",
        skills_dir=None,
        instructions_file=".cursor/rules/raise.mdc",
        detection_markers=[".cursor"],
    ),
    "windsurf": IdeConfig(
        ide_type="windsurf",
        skills_dir=None,
        instructions_file=".windsurf/rules/raise.md",
        detection_markers=[".windsurf"],
    ),
    "copilot": IdeConfig(
        ide_type="copilot",
        skills_dir=None,
        instructions_file=".github/copilot-instructions.md",
        detection_markers=[".github/copilot-instructions.md"],
    ),
    "antigravity": IdeConfig(
        ide_type="antigravity",
        skills_dir=".agent/skills",
        instructions_file=".agent/rules/raise.md",
        workflows_dir=".agent/workflows",
        detection_markers=[".agent"],
    ),
}
```

**IdeConfig changes:**
- Add `detection_markers: list[str]` — paths to check for IDE presence
- `skills_dir` becomes `str | None` — most IDEs don't have native skills

### 3. Instructions generator reads from `.raise/` canonical source

The generator produces a **projection** from canonical files, not a stub. Same content for all IDEs, different output path.

**Sections to generate (from canonical sources):**

| Section | Source | Content |
|---------|--------|---------|
| Header | `manifest.yaml` | Project name, `/rai-session-start` prompt |
| Rai Identity | `.raise/rai/identity/core.md` | Values, boundaries, principles |
| Process Rules | `.raise/rai/framework/methodology.yaml` | Lifecycle, gates, critical rules |
| Branch Model | `.raise/manifest.yaml` or convention | Branch naming, merge flow |
| CLI Quick Reference | Template or introspection | Common commands, mistakes |
| Critical Rules | Framework | TDD, commit policy, HITL, types |

**MUST:** Generator returns `str`. Caller handles path (PAT-E-156).

**MUST NOT:** Hardcode any IDE-specific content in the generated string.

### 4. Auto-detection in `rai init --detect`

```bash
# Auto-detects and generates for all found IDEs
$ rai init --detect
  Detected IDEs: claude, cursor
  Generating instructions for: claude, cursor
  → CLAUDE.md (updated)
  → .cursor/rules/raise.mdc (created)

# Explicit multi-IDE
$ rai init --ide claude --ide cursor --ide copilot

# Single IDE (backward compat)
$ rai init --ide antigravity
```

**Detection logic:**
```python
def detect_ides(project_root: Path) -> list[IdeType]:
    """Detect IDEs with presence in the project."""
    detected = []
    for ide_type, config in IDE_CONFIGS.items():
        for marker in config.detection_markers:
            if (project_root / marker).exists():
                detected.append(ide_type)
                break
    return detected
```

### 5. Manifest schema change

```yaml
# Before (Fernando's)
ide:
  type: claude

# After
ide:
  types: [claude, cursor]
```

Backward compat: read old `ide.type` (singular), write new `ide.types` (plural).

### 6. CLI flag change

`--ide` becomes repeatable:
```python
ide: Annotated[
    list[IdeChoice] | None,
    typer.Option("--ide", help="Target IDE(s). Repeatable. Auto-detected if omitted with --detect."),
] = None
```

**Logic:**
- `--ide` provided → use those
- `--detect` without `--ide` → auto-detect + prompt if interactive
- Neither → default to `["claude"]` (backward compat)

## Examples

### CLI usage
```bash
# Existing behavior (unchanged)
rai init
# → Generates CLAUDE.md only (default)

# Multi-IDE explicit
rai init --ide claude --ide cursor
# → Generates CLAUDE.md + .cursor/rules/raise.mdc

# Auto-detect with --detect
rai init --detect
# → Scans for IDE markers, generates for all found

# Antigravity with workflows
rai init --ide antigravity
# → .agent/rules/raise.md + .agent/skills/ + .agent/workflows/
```

### Generated instructions output (same for all IDEs)
```markdown
<!-- Generated from .raise/ canonical source. Do not edit manually. Regenerate with: rai init -->

# {project_name}

Run `/rai-session-start` at the beginning of each session to load full context.

## Rai Identity

### Values
1. Honesty over Agreement — ...
...

## Process Rules
### Work Lifecycle
EPIC: /rai-epic-start → ...
...

### Gates
- Epic branch exists before epic design
...

### Critical Rules
- TDD always
...

## Branch Model
main → v2 → epic/... → story/...

## CLI Quick Reference
| cmd | sig | notes |
...
```

## Acceptance Criteria

**MUST:**
- [ ] `claudemd.py` renamed to `instructions.py`, all imports updated
- [ ] 5 IdeTypes registered with correct paths and detection markers
- [ ] Generator reads from `.raise/` canonical source, produces real projection
- [ ] `rai init --ide X` works for all 5 IDEs
- [ ] `rai init --detect` auto-detects and generates for found IDEs
- [ ] `rai init` (no flags) still defaults to claude (backward compat)
- [ ] All existing tests pass + new tests for 5 IDEs
- [ ] Quality gates pass (ruff, pyright)

**SHOULD:**
- [ ] Testing guide for team to validate each IDE
- [ ] Binary artifacts (PDF) removed from repo
- [ ] Manifest backward compat (read singular, write plural)

**MUST NOT:**
- [ ] Break existing `rai init` default behavior
- [ ] Hardcode IDE-specific content in generated instructions
- [ ] Couple generator to specific IDE paths

## Architectural Context

- **Module:** mod-onboarding (integration layer, bc-experience domain)
- **Pattern:** PAT-E-156 (separate generation from placement)
- **Pattern:** PAT-E-347 (canonical source / projected prompt — ADR-012)
- **ADR:** ADR-031 (IdeConfig pattern — extending, not replacing)

## Research Sources

- [Cursor Rules Docs](https://cursor.com/docs/context/rules) — `.cursor/rules/*.mdc`, `.cursorrules` deprecated
- [Windsurf Rules Guide](https://design.dev/guides/windsurf-rules/) — `.windsurf/rules/*.md`
- [GitHub Copilot Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) — `.github/copilot-instructions.md`
- [AI IDE Comparison 2026](https://www.digitalapplied.com/blog/cursor-vs-windsurf-vs-google-antigravity-ai-ide-comparison-2026)
