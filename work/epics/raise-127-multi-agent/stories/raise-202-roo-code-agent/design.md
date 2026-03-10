---
id: RAISE-202
title: "Roo Code agent support (LiteLLM-compatible)"
epic: RAISE-127
created: 2026-02-19
status: design
---

# RAISE-202: Roo Code agent support

## What & Why

**Problem:** Clients using Roo Code + LiteLLM can't use `rai init` to scaffold RaiSE — Roo Code is not a recognized agent type.

**Value:** Unblocks a client-driven use case with ~1 day of work. The multi-agent plugin architecture (ADR-032) already handles all the complexity — this is a data addition, not a structural change.

## Architectural Context

- **Module:** `mod-agents` (extends) + `mod-config` (AgentConfig Literal update)
- **Layer:** lyr-leaf — no new dependencies
- **Pattern (ADR-032):** Each new agent = 1 YAML file + optional plugin. No plugin needed for Roo — it uses the Agent Skills standard with identical SKILL.md format (name + description YAML frontmatter).
- **Constraint:** `BuiltinAgentType` is a `Literal["claude", "cursor", ...]` — must add `"roo"` here and in `AgentChoice` enum.

## Approach

1. Add `src/rai_cli/agents/roo.yaml` with Roo Code paths and detection markers
2. Extend `BuiltinAgentType`, `AgentChoice`, and `BUILTIN_AGENTS` in `agents.py` with the `roo` entry
3. **No plugin needed** — Roo reads `SKILL.md` with standard frontmatter (`name`, `description`) identical to Claude Code. No transformation required.

## Examples

### CLI usage

```bash
# Initialize a project for Roo Code
rai init --agent roo

# Multi-agent (Roo + Claude)
rai init --agent roo --agent claude

# Auto-detect if .roo/ directory exists
rai init --detect
```

### Expected scaffolding output

```
Initializing RaiSE for Roo Code...
✓ .roo/rules/raise.md  (instructions)
✓ .roo/skills/rai-session-start/SKILL.md
✓ .roo/skills/rai-story-start/SKILL.md
... (26 public skills total)
✓ .raise/ (governance scaffold)
```

### roo.yaml (new file)

```yaml
name: Roo Code
agent_type: roo
instructions_file: .roo/rules/raise.md
skills_dir: .roo/skills
detection_markers:
  - .roo/rules
  - .roo
  - .rooignore
```

### agents.py additions

```python
# BuiltinAgentType Literal — add "roo"
BuiltinAgentType = Literal["claude", "cursor", "windsurf", "copilot", "antigravity", "roo"]

# AgentChoice enum — add roo = "roo"

# BUILTIN_AGENTS dict — add entry
"roo": AgentConfig(
    name="Roo Code",
    agent_type="roo",
    skills_dir=".roo/skills",
    instructions_file=".roo/rules/raise.md",
    detection_markers=[".roo/rules", ".roo", ".rooignore"],
),
```

## Acceptance Criteria

**MUST:**
- [ ] `rai init --agent roo` creates `.roo/skills/` with all 26 public skills (SKILL.md intact, no transformation)
- [ ] `rai init --agent roo` creates `.roo/rules/raise.md` with instructions content
- [ ] `rai init --detect` recognizes a project with `.roo/` directory as Roo Code
- [ ] `rai skill list` resolves skills from `.roo/skills/` when agent is `roo`
- [ ] All tests pass, pyright clean, coverage ≥ 90%

**SHOULD:**
- [ ] `rai init --agent roo --agent claude` scaffolds both in a single pass

**MUST NOT:**
- Transform SKILL.md frontmatter (Roo uses identical format — no CopilotPlugin-style override needed)
- Add new Python dependencies
