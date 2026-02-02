# Epic E7: Distribution & Onboarding - Scope

> **Status:** DRAFT (blocked by E8)
> **Branch:** `feature/e7/distribution`
> **Created:** 2026-02-02
> **Target:** Feb 9, 2026 (Friends & Family pre-launch)
> **Research:** `work/research/openclaw-onboarding/` (RES-ONBOARD-001)
> **Depends on:** E8 Work Tracking Graph (for `raise status` to query graph)

---

## Objective

Make raise-cli installable, discoverable, and usable for F&F users. The goal is a smooth journey from `pip install` to first productive session in Claude Code.

**Value proposition:** Without this, F&F users can't easily adopt RaiSE. With it, they can install the package, run one command, and start using the skills immediately.

**Key Insight (from OpenClaw research):** Wizard-based onboarding removes friction. Users shouldn't edit config files manually. One command should set up everything needed.

---

## User Journey (Target)

```
pip install raise-cli          # Install the package
cd my-project                   # Enter their project
raise onboard                   # Interactive wizard
# → Creates CLAUDE.md + .claude/skills/

# Open Claude Code
/session-start                  # Begin working with RaiSE
```

**Time to first value:** < 5 minutes

---

## Features

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F7.1 | **Onboard Command** | S | Pending | `raise onboard` wizard with templates |
| F7.2 | **Package Metadata** | XS | ✅ Complete | pyproject.toml for PyPI |
| F7.3 | **Status Command** | XS | Pending | `raise status` health check |
| F7.4 | **README & Docs** | S | ✅ Complete | Updated 2026-02-02 |
| F7.5 | **Doctor Command** | S | Deferred | `raise doctor` diagnostics (P1) |

**F&F Scope:** F7.1, F7.3 (onboard + status)

---

## Architecture

### Onboard Templates

Learned from OpenClaw: templates scale complexity to user needs.

| Template | Audience | Creates |
|----------|----------|---------|
| **minimal** | F&F, quick start | CLAUDE.md + .claude/skills/ |
| standard | Teams | + governance/ + .raise/katas/ |
| full | Enterprise/Rai | + .rai/ (identity + memory) |

**F&F Default:** `minimal` — fastest path to value

### `raise onboard` Flow

```
Step 1: Detect Project State
  ├── Is this a git repo?
  ├── Existing governance/?
  └── Existing .claude/?

Step 2: Choose Template (if not --template flag)
  ? Select template:
    > minimal (recommended for getting started)
      standard
      full

Step 3: Copy Skills
  → .claude/skills/ (11 skills from package)

Step 4: Generate CLAUDE.md
  → Minimal template or from governance/ if exists

Step 5: Verify & Show Next Steps
  ✓ RaiSE initialized!

  Next:
    1. Open Claude Code here
    2. Run /session-start
```

### `raise status` Output

```
$ raise status

RaiSE Project Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CLAUDE.md          ✓ Present (2.1 KB)
  Skills             ✓ 11 installed
  Governance         ✗ Not found (optional)
  Rai Identity       ✗ Not found (optional)

  Template: minimal
  Version:  raise-cli 2.0.0

Ready to use. Run /session-start in Claude Code.
```

### Package Structure

Skills must be bundled with the package for `onboard` to copy them:

```
raise-cli/
├── src/raise_cli/
│   ├── cli/commands/
│   │   ├── onboard.py      # NEW
│   │   └── status.py       # NEW (or extend existing)
│   └── data/               # NEW - bundled assets
│       └── skills/         # Skills to copy on onboard
│           ├── session-start/
│           ├── session-close/
│           └── ...
└── pyproject.toml          # Include data/ in package
```

---

## In Scope (F&F - Feb 9)

**MUST:**
- [ ] `raise onboard` command with minimal template
- [ ] Copy skills from package to `.claude/skills/`
- [ ] Generate minimal CLAUDE.md
- [ ] `raise status` health check
- [ ] Skills bundled in package (`src/raise_cli/data/skills/`)
- [ ] Update pyproject.toml to include package data

**SHOULD:**
- [ ] `--template` flag for future templates
- [ ] `--yes` flag for non-interactive mode
- [ ] Detect existing files and prompt before overwrite

---

## Out of Scope (Post-F&F)

**Deferred:**
- Standard/full templates
- `raise doctor` diagnostics
- `raise sync` (regenerate CLAUDE.md)
- `raise upgrade` (update skills)
- Shell completions (F7.3 from original backlog)

---

## Done Criteria

### Per Feature
- [ ] Code implemented with type annotations
- [ ] Unit tests (>90% coverage)
- [ ] CLI help text complete
- [ ] Works on fresh project (greenfield)
- [ ] Works on existing project (brownfield)

### Epic Complete
- [ ] `pip install raise-cli` works
- [ ] `raise onboard` creates working setup
- [ ] `raise status` shows project health
- [ ] F&F user can go from install to /session-start in <5 minutes
- [ ] Tested in fresh repo (dogfooding invertido)

---

## Dependencies

```
F7.2 (Package Metadata) ← DONE
  ↓
F7.4 (README) ← DONE
  ↓
F7.1 (Onboard) ← NEXT
  ↓
F7.3 (Status)
```

**Blockers:** None — F7.2 and F7.4 complete

---

## Learnings from Research (RES-ONBOARD-001)

### What OpenClaw Does Well

| Pattern | Application to RaiSE |
|---------|---------------------|
| Single `onboard` command | `raise onboard` wizard |
| Interactive wizard | Guide through template choice |
| `doctor` command | `raise doctor` for diagnostics (P1) |
| Workspace isolation | Per-project `.claude/skills/` |
| Daemon mode | NOT needed — Claude Code is the runtime |

### Key Differences

| OpenClaw | RaiSE |
|----------|-------|
| Multi-channel messaging | Claude Code only |
| Global config (`~/.openclaw/`) | Per-project config |
| Node.js (`npm install`) | Python (`pip install`) |
| Agent-first (autonomous) | Human-first (collaborative) |
| Gateway daemon | No daemon needed |

### Design Decision

**Per-project skills** instead of global:
- Enables customization per project
- Works offline (no network dependency)
- Aligns with "governance as code" (skills versioned with project)
- Trade-off: ~200KB duplication per project (acceptable)

---

## Implementation Notes

### Skills Bundling

To include skills in the Python package:

```toml
# pyproject.toml
[tool.hatch.build.targets.wheel]
packages = ["src/raise_cli"]

[tool.hatch.build.targets.wheel.force-include]
".claude/skills" = "raise_cli/data/skills"
```

Or use `importlib.resources` pattern:

```python
from importlib.resources import files

def get_skills_path() -> Path:
    return files("raise_cli.data.skills")
```

### Onboard Command Structure

```python
@app.command()
def onboard(
    template: str = typer.Option("minimal", help="Template: minimal, standard, full"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Non-interactive mode"),
) -> None:
    """Initialize RaiSE in current project."""
    ...
```

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Install to first skill | < 5 minutes | Manual test |
| Onboard success rate | > 95% | No errors on clean project |
| Files created correctly | 100% | Unit tests |
| Works on brownfield | Yes | Test on existing repo |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Skills too large for package | Low | Medium | Measure size, consider --no-skills flag |
| Overwrite existing files | Medium | Medium | Prompt before overwrite, --force flag |
| Template choice confusion | Low | Low | Good defaults, clear descriptions |

---

## Timeline

| Day | Date | Features | Cumulative |
|:---:|------|----------|:----------:|
| 1 | Feb 3 | F7.1 Onboard (minimal) | 60% |
| 1 | Feb 3 | F7.3 Status | 80% |
| 2 | Feb 4 | Testing + polish | 100% |
| 3-7 | Feb 5-9 | Buffer, dogfooding | **F&F Ready** |

**Estimated effort:** 3-4 hours with kata cycle

---

*Epic tracking - update per feature completion*
*Created: 2026-02-02*
*Research input: RES-ONBOARD-001 (OpenClaw onboarding)*
