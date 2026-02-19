---
id: RAISE-197
title: "Multi-agent skill distribution with plugin architecture"
size: L
complexity: moderate-high
modules: [mod-onboarding, mod-config, mod-cli]
depends_on: [RAISE-128]
---

# RAISE-197: Multi-Agent Skill Distribution

## Problem

RAISE-128 introduced IDE abstraction with `IdeConfig` for Claude and Antigravity, but:
1. Module naming is Claude-specific (`claudemd.py`, `ClaudeMdGenerator`)
2. The generator produces a generic stub, not the real projection from `.raise/` canonical source (ADR-012)
3. Only 2 of 9+ market-relevant tools are supported (5 IDEs + 4 CLIs support SKILL.md)
4. `--ide` accepts only one value — teams use multiple tools
5. No auto-detection of installed agents
6. No extensibility — adding a new target requires modifying source code

## Value

1. **For the team:** `rai init --detect` configures ANY developer's IDE/CLI automatically
2. **For Kurigage:** Same canonical process → N tool projections. Every dev gets their preferred tool configured
3. **For the ecosystem:** Third parties (F&F user wanting Azure connector) can build agent connectors without PRing our repo

## Research Base

| Document | Key Finding |
|----------|-------------|
| `work/research/raise-197-ide-skills-cursor.md` | Cursor 2.4 (Jan 2026) added native SKILL.md via AgentSkills spec |
| `work/research/raise-197-ide-skills-windsurf.md` | Identical SKILL.md format, closest to RaiSE architecture |
| `work/research/raise-197-ide-skills-copilot.md` | Richest model: agents + prompts + per-dir instructions. Different frontmatter |
| `work/research/raise-197-ide-skills-antigravity.md` | Identical SKILL.md format, `.agent/` convention |
| `work/research/raise-197-cursor-skills-workarounds.md` | Cursor 2.4 skills confirmed, Custom Modes NOT file-configurable |
| `work/research/raise-197-cli-agents-landscape.md` | SKILL.md is de facto standard across 6+ tools. AGENTS.md at 60K+ repos |

**Key insight:** SKILL.md (AgentSkills standard) has converged across Claude Code, Cursor, Windsurf, Antigravity, Codex CLI, Gemini CLI, Cline, and OpenCode. Only Copilot uses a different frontmatter format. The abstraction should be "agent targets", not "IDEs".

## Approach

### 1. Rename `claudemd.py` → `instructions.py`

- `ClaudeMdGenerator` → `InstructionsGenerator`
- `generate_claude_md()` → `generate_instructions()`
- Update all imports across codebase

### 2. Rename `IdeConfig` → `AgentConfig` with plugin support

The core abstraction becomes tool-agnostic. An `AgentConfig` can represent an IDE, CLI, or any agent that consumes instructions + skills.

```python
from typing import Literal, Protocol

# Built-in targets (Tier 1 — this story)
BuiltinAgentType = Literal["claude", "cursor", "windsurf", "copilot", "antigravity"]

class AgentConfig(BaseModel):
    """Configuration for a target agent/IDE/CLI."""
    model_config = ConfigDict(frozen=True)

    name: str                                  # Display name
    agent_type: str                            # Registry key (e.g. "claude", "codex-cli", "azure-devops")
    instructions_file: str                     # Where to write instructions
    skills_dir: str | None = None              # Where to copy skills (None = no skills support)
    workflows_dir: str | None = None           # Where to copy workflows
    detection_markers: list[str] = []          # Paths to check for presence
    plugin: str | None = None                  # Python module/path for custom logic
```

### 3. AgentPlugin protocol — extensibility via Python plugins

```python
class AgentPlugin(Protocol):
    """Protocol for custom agent connectors."""

    def transform_instructions(self, content: str, config: AgentConfig) -> str:
        """Transform generated instructions for this target. Default: pass-through."""
        ...

    def transform_skill(self, frontmatter: dict, body: str, config: AgentConfig) -> tuple[dict, str]:
        """Transform a SKILL.md for this target. Default: pass-through."""
        ...

    def post_init(self, project_root: Path, config: AgentConfig) -> list[str]:
        """Run after all files are generated. Returns list of created files. Default: no-op."""
        ...
```

**Key design decisions:**
- **Protocol, not ABC** — duck typing, no forced inheritance. A plugin only implements what it needs.
- **Default no-op** — if no plugin is specified, the engine uses pass-through (copy-as-is). 4/5 built-in targets need no plugin.
- **Single real plugin in v1** — `CopilotPlugin` validates the protocol with a real use case (frontmatter transformation for `.github/agents/` and `.github/prompts/`).

### 4. YAML-based agent registry

Built-in targets ship as YAML in the package. Users extend via `~/.rai/agents/` (global) or `.raise/agents/` (project).

```yaml
# Built-in: bundled with rai-cli package
# src/rai_cli/agents/claude.yaml
name: Claude Code
agent_type: claude
instructions_file: CLAUDE.md
skills_dir: .claude/skills
detection_markers:
  - CLAUDE.md
  - .claude
```

```yaml
# Built-in with plugin: Copilot needs frontmatter transformation
# src/rai_cli/agents/copilot.yaml
name: GitHub Copilot
agent_type: copilot
instructions_file: .github/copilot-instructions.md
skills_dir: .github/agents
workflows_dir: .github/prompts
detection_markers:
  - .github/copilot-instructions.md
plugin: rai_cli.agents.copilot_plugin
```

```yaml
# User-defined: F&F user creates this, no PR needed
# ~/.rai/agents/azure-devops.yaml
name: Azure DevOps
agent_type: azure-devops
instructions_file: .azure/instructions.md
skills_dir: .azure/skills
detection_markers:
  - .azure
plugin: rai_azure_connector  # pip install rai-azure-connector
```

**Registry loading order** (last wins):
1. Built-in YAML (bundled in package)
2. Project-level `.raise/agents/*.yaml`
3. User-level `~/.rai/agents/*.yaml`

### 5. Built-in agent configs (Tier 1)

| Agent | instructions_file | skills_dir | workflows_dir | Plugin | Notes |
|-------|-------------------|------------|---------------|--------|-------|
| claude | `CLAUDE.md` | `.claude/skills` | — | — | Native SKILL.md |
| cursor | `.cursor/rules/raise.mdc` | `.cursor/skills` | — | — | SKILL.md via AgentSkills spec (2.4+) |
| windsurf | `.windsurf/rules/raise.md` | `.windsurf/skills` | `.windsurf/workflows` | — | Identical SKILL.md format |
| copilot | `.github/copilot-instructions.md` | `.github/agents` | `.github/prompts` | `CopilotPlugin` | Different frontmatter: adds `tools`, `infer` |
| antigravity | `.agent/rules/raise.md` | `.agent/skills` | `.agent/workflows` | — | Identical SKILL.md format |

**Change from v1 design:** Cursor now has `skills_dir` (Cursor 2.4 added native SKILL.md support, Jan 2026).

### 6. Instructions generator reads from `.raise/` canonical source

The generator produces a **projection** from canonical files, not a stub. Same content for all agents, different output path.

**Sections to generate (from canonical sources):**

| Section | Source | Content |
|---------|--------|---------|
| Header | `manifest.yaml` | Project name, `/rai-session-start` prompt |
| Rai Identity | `.raise/rai/identity/core.md` | Values, boundaries, principles |
| Process Rules | `.raise/rai/framework/methodology.yaml` | Lifecycle, gates, critical rules |
| Branch Model | `.raise/manifest.yaml` or convention | Branch naming, merge flow |
| CLI Quick Reference | Template or introspection | Common commands, mistakes |
| External Integrations | `.raise/jira.yaml` etc. | Integration configs |

**MUST:** Generator returns `str`. Caller handles path (PAT-E-156).

**MUST NOT:** Hardcode any agent-specific content in the generated string. The `AgentPlugin.transform_instructions()` hook handles agent-specific adjustments.

### 7. Auto-detection in `rai init --detect`

```bash
# Auto-detects and generates for all found agents
$ rai init --detect
  Detected agents: claude, cursor, windsurf
  Generating for: claude, cursor, windsurf
  → CLAUDE.md (updated)
  → .cursor/rules/raise.mdc (created)
  → .cursor/skills/ (3 skills scaffolded)
  → .windsurf/rules/raise.md (created)
  → .windsurf/skills/ (3 skills scaffolded)
  → .windsurf/workflows/ (3 workflows scaffolded)

# Explicit multi-agent
$ rai init --agent claude --agent cursor --agent copilot

# Single agent (backward compat)
$ rai init --agent antigravity

# Backward compat: --ide still works as alias
$ rai init --ide claude
```

**Detection logic:**
```python
def detect_agents(project_root: Path) -> list[str]:
    """Detect agents with presence in the project."""
    detected = []
    for config in agent_registry.values():
        for marker in config.detection_markers:
            if (project_root / marker).exists():
                detected.append(config.agent_type)
                break
    return detected
```

### 8. Manifest schema change

```yaml
# Before (Fernando's)
ide:
  type: claude

# After
agents:
  types: [claude, cursor, windsurf]
```

Backward compat: read old `ide.type` (singular), migrate to `agents.types` on write.

### 9. CLI flag change

`--ide` becomes `--agent` (with `--ide` as deprecated alias):

```python
agent: Annotated[
    list[str] | None,
    typer.Option("--agent", help="Target agent(s). Repeatable. Auto-detected if omitted with --detect."),
] = None
```

**Logic:**
- `--agent` provided → use those (validate against registry)
- `--detect` without `--agent` → auto-detect + prompt if interactive
- Neither → default to `["claude"]` (backward compat)

### 10. AGENTS.md as bonus output

When `--detect` runs, also generate `AGENTS.md` at project root. Content equivalent to instructions but in the universal format. Supported by Cursor, Windsurf, Copilot, Codex CLI, Kilo Code, OpenCode (60K+ repos use it).

## Examples

### CLI usage
```bash
# Existing behavior (unchanged)
rai init
# → Generates CLAUDE.md only (default)

# Multi-agent explicit
rai init --agent claude --agent cursor
# → CLAUDE.md + .cursor/rules/raise.mdc + .cursor/skills/

# Auto-detect
rai init --detect
# → Scans for markers, generates for all found + AGENTS.md

# Third-party agent (after pip install rai-azure-connector)
rai init --agent azure-devops
# → .azure/instructions.md + .azure/skills/ (plugin handles specifics)
```

### CopilotPlugin (the one built-in plugin)
```python
# src/rai_cli/agents/copilot_plugin.py
from rai_cli.agents.protocol import AgentPlugin

class CopilotPlugin:
    """Transform RaiSE skills to Copilot agent format."""

    def transform_skill(self, frontmatter: dict, body: str, config: AgentConfig) -> tuple[dict, str]:
        """Add Copilot-specific frontmatter fields."""
        fm = {**frontmatter}
        fm["tools"] = ["execute", "read", "edit", "search"]
        fm["infer"] = True
        fm.pop("license", None)
        fm.pop("compatibility", None)
        return fm, body

    def post_init(self, project_root: Path, config: AgentConfig) -> list[str]:
        """Generate .prompt.md files from skills."""
        created = []
        prompts_dir = project_root / ".github" / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        for skill in self._discover_skills(project_root):
            prompt_file = prompts_dir / f"{skill.name}.prompt.md"
            prompt_file.write_text(self._skill_to_prompt(skill))
            created.append(str(prompt_file))
        return created
```

### User-created plugin (F&F Azure example)
```python
# rai_azure_connector/__init__.py (published as pip package)
class AzureDevOpsPlugin:
    def transform_instructions(self, content: str, config) -> str:
        # Add Azure-specific header
        return f"<!-- Azure DevOps Agent Instructions -->\n{content}"

    def post_init(self, project_root, config) -> list[str]:
        # Generate Azure pipeline integration
        pipeline_file = project_root / ".azure" / "agent-pipeline.yaml"
        pipeline_file.parent.mkdir(parents=True, exist_ok=True)
        pipeline_file.write_text(self._generate_pipeline())
        return [str(pipeline_file)]
```

## Acceptance Criteria

**MUST:**
- [ ] `claudemd.py` renamed to `instructions.py`, all imports updated
- [ ] `IdeConfig` renamed to `AgentConfig`, `IdeType` to `BuiltinAgentType`
- [ ] `AgentPlugin` protocol defined with 3 hooks (transform_instructions, transform_skill, post_init)
- [ ] 5 built-in agent configs as YAML files with correct paths and detection markers
- [ ] All 5 agents have `skills_dir` (Cursor confirmed SKILL.md support in 2.4)
- [ ] `CopilotPlugin` implements frontmatter transformation (validates protocol)
- [ ] Generator reads from `.raise/` canonical source, produces real projection
- [ ] `rai init --agent X` works for all 5 built-in agents
- [ ] `rai init --detect` auto-detects and generates for found agents
- [ ] `rai init` (no flags) still defaults to claude (backward compat)
- [ ] Agent registry loads from: built-in → `.raise/agents/` → `~/.rai/agents/`
- [ ] All existing tests pass + new tests for 5 agents + plugin protocol
- [ ] Quality gates pass (ruff, pyright)

**SHOULD:**
- [ ] `AGENTS.md` generated as bonus output on `--detect`
- [ ] `--ide` works as deprecated alias for `--agent`
- [ ] Testing guide for team to validate each agent
- [ ] Manifest backward compat (read `ide.type`, write `agents.types`)

**MUST NOT:**
- [ ] Break existing `rai init` default behavior
- [ ] Hardcode agent-specific content in generated instructions (use plugin hooks)
- [ ] Couple generator to specific agent paths
- [ ] Require code changes to add a new agent target (YAML + optional plugin is sufficient)

## Architectural Context

- **Module:** mod-onboarding (integration layer, bc-experience domain)
- **Pattern:** PAT-E-156 (separate generation from placement)
- **Pattern:** PAT-E-347 (canonical source / projected prompt — ADR-012)
- **ADR:** ADR-031 (IdeConfig pattern — extending to AgentConfig)
- **ADR:** ADR-032 (Multi-IDE skill distribution — draft, updated with plugin architecture)

## Tier Model

| Tier | Targets | RAISE-197 Scope | Extensibility |
|------|---------|-----------------|---------------|
| **1 (this story)** | Claude, Cursor, Windsurf, Copilot, Antigravity | Built-in YAML + CopilotPlugin | — |
| **2 (future)** | Codex CLI, Gemini CLI, OpenCode, Cline | Add YAML configs (no code) | Community PRs |
| **3 (ecosystem)** | Azure DevOps, custom enterprise tools | User YAML + pip-installable plugin | Third-party packages |

## Research Sources

- [AgentSkills Specification](https://agentskills.io/specification) — Cross-tool SKILL.md standard
- [AGENTS.md Standard](https://agents.md/) — 60K+ repos, Linux Foundation
- [Cursor 2.4 Skills](https://www.aimakers.co/blog/cursor-2-4-subagents/) — Native SKILL.md support
- [Windsurf Skills](https://docs.windsurf.com/windsurf/cascade/skills) — Identical format
- [Copilot Custom Agents](https://docs.github.com/en/copilot/reference/custom-agents-configuration) — Different frontmatter
- [Antigravity Skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills) — Identical format
- [OpenClaw Architecture](https://docs.openclaw.ai/tools/skills) — Skills + MCP two-layer model, ClawHub marketplace
- See `work/research/raise-197-*.md` for detailed per-tool analysis
