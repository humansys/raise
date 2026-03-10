---
story_id: F128.4
title: Init --ide Flag + E2E Tests
size: S
complexity: moderate
phase: design
epic: RAISE-128
module: mod-cli, mod-onboarding
domain: bc-application-layer
layer: lyr-orchestration
---

# F128.4: Init --ide Flag + E2E Tests

## What & Why

**Problem:** `rai init` always scaffolds Claude Code conventions (`.claude/skills/`, `CLAUDE.md`). After F128.1–F128.3 decoupled all scaffolding functions to accept `IdeConfig`, the CLI entry point still hardcodes the Claude path. There's no way to initialize a project for Antigravity.

**Value:** Completing the wiring makes `rai init --ide antigravity` produce a working `.agent/` structure. This is the final integration point — all pieces exist, this connects them.

## Architectural Context

- **Module:** `mod-cli` (orchestration layer — depends on everything, nothing depends on it)
- **Touched file:** `src/rai_cli/cli/commands/init.py` (coupling point #6 from epic scope)
- **Constraints:** All MUST guardrails apply (type hints, ruff, pyright, bandit, tests >90%)

## Approach

Add `--ide` option to `init_command()`. Create `IdeConfig` from the flag via `get_ide_config()`. Pass it to:
1. `scaffold_skills(project_path, ide_config=ide_config)`
2. `scaffold_workflows(project_path, ide_config=ide_config)`
3. `generate_claude_md(..., ide_config=ide_config)` — writes to `ide_config.instructions_file`
4. MEMORY.md: write Claude Code copy **only when ide_type == "claude"** (Antigravity has no equivalent)

**Components affected:**

| Component | Change |
|-----------|--------|
| `cli/commands/init.py` | Modify — add `--ide` param, pass `IdeConfig` to functions |
| `tests/cli/commands/test_init.py` | Modify — add E2E tests for both IDE paths |

## Examples

### CLI Usage

```bash
# Default (backward compat — identical to today)
rai init

# Explicit Claude (same as default)
rai init --ide claude

# Antigravity
rai init --ide antigravity

# Combined with existing flags
rai init --ide antigravity --name my-project --detect
```

### Expected Output (Antigravity)

```
.agent/
  skills/
    rai-session-start/SKILL.md
    rai-session-close/SKILL.md
    ...
  rules/
    raise.md              # instructions file (equivalent of CLAUDE.md)
  workflows/
    rai-session-start.md
    rai-session-close.md
    ...
.raise/
  manifest.yaml
  rai/
    identity/
    memory/
      MEMORY.md           # canonical copy only (no Claude Code copy)
    framework/
governance/
  ...
```

### Key Integration Point

```python
# In init_command():
from rai_cli.config.ide import IdeConfig, IdeType, get_ide_config

def init_command(
    ...,
    ide: Annotated[
        IdeType,
        typer.Option("--ide", help="Target IDE (claude, antigravity)"),
    ] = "claude",
) -> None:
    ide_config = get_ide_config(ide)
    # ... existing code ...
    skills_result = scaffold_skills(project_path, ide_config=ide_config)
    scaffold_workflows(project_path, ide_config=ide_config)
    # ... instructions file uses ide_config.instructions_file path ...
    # ... MEMORY.md Claude copy only when ide == "claude" ...
```

## Acceptance Criteria

**MUST:**
- `rai init --ide antigravity` produces `.agent/skills/`, `.agent/rules/raise.md`, `.agent/workflows/`
- `rai init` (no flag) produces identical output to current behavior (backward compat)
- `rai init --ide claude` produces identical output to `rai init` (explicit default)
- MEMORY.md Claude Code copy only written for `--ide claude`
- `--ide` appears in CLI help with valid choices
- All quality gates pass (ruff, pyright, bandit, pytest >90%)

**MUST NOT:**
- Break existing `rai init` behavior
- Write Claude-specific paths when `--ide antigravity`
- Require `--ide` flag (must default to "claude")
