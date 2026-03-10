---
id: ADR-032
title: Multi-Agent Skill Distribution with Plugin Architecture
status: accepted
date: 2026-02-18
decision_makers: [emilio]
story: RAISE-197
---

# ADR-032: Multi-Agent Skill Distribution with Plugin Architecture

## Context

RAISE-128 introduced `IdeConfig` supporting Claude and Antigravity. By February 2026,
the agent ecosystem had expanded: Cursor 2.4 added native SKILL.md support, Windsurf,
GitHub Copilot, and 6+ CLI tools all converge on the AgentSkills standard. The old
model had four problems: (1) Claude-specific naming, (2) hardcoded 2-target registry,
(3) single `--ide` flag, and (4) no extensibility without modifying source code.

## Decision

Replace `IdeConfig` with `AgentConfig` + a 3-tier YAML registry + `AgentPlugin` protocol.

### AgentConfig model

```python
class AgentConfig(BaseModel):
    name: str
    agent_type: str
    instructions_file: str
    skills_dir: str | None = None
    workflows_dir: str | None = None
    detection_markers: list[str] = []
    plugin: str | None = None
```

`skills_dir: str | None` — supports agents without skills directories (future Tier 2/3).

### 3-tier YAML registry (last-wins)

1. Built-in YAML files bundled in `rai_cli.agents` package (5 Tier-1 agents)
2. Project `.raise/agents/*.yaml` — team-level overrides
3. User `~/.rai/agents/*.yaml` — personal overrides + third-party agents

### AgentPlugin protocol (not ABC)

```python
class AgentPlugin(Protocol):
    def transform_instructions(self, content: str, config: AgentConfig) -> str: ...
    def transform_skill(self, frontmatter: dict, body: str, config: AgentConfig) -> tuple[dict, str]: ...
    def post_init(self, project_root: Path, config: AgentConfig) -> list[str]: ...
```

Protocol (not ABC): duck typing allows third parties to implement only the hooks they need,
without forced inheritance. `DefaultAgentPlugin` provides pass-through for all methods.

### Tier model

| Tier | Targets | Distribution |
|------|---------|--------------|
| 1 | Claude, Cursor, Windsurf, Copilot, Antigravity | Built-in YAML |
| 2 | Codex CLI, Gemini CLI, OpenCode, Cline | Community YAML PR |
| 3 | Azure DevOps, enterprise custom | User YAML + pip plugin |

### CLI changes

- `--agent` (repeatable, new) replaces `--ide` (deprecated alias preserved)
- `--detect` auto-detects agents from `detection_markers` + generates `AGENTS.md`
- Default: `["claude"]` (backward compat)

### Manifest schema

`ide.type` (str, singular) → `agents.types` (list[str], plural).
`model_validator(mode='before')` migrates old format on load. Both written for transition.

## Consequences

### Positive
- Zero code changes to add a new Tier-2 agent (YAML only)
- Third-party Tier-3 agents via pip install (F&F customer Azure connector use case)
- SKILL.md frontmatter transformation per-agent (CopilotPlugin validated protocol)
- `rai init --detect` configures any developer's environment automatically
- AGENTS.md generated as bonus — compatible with 60K+ repos ecosystem standard

### Negative
- `skills_dir: str | None` requires null guards at all call sites (found in locator.py, builder.py)
- Plugin loading via `importlib.import_module` adds dynamic import complexity
- Forward dependency: registry tests needed a CopilotPlugin stub before T6 full impl

### Neutral
- Old `IdeConfig`, `get_ide_config`, `generate_claude_md` preserved as backward-compat shims
- `ide.type` still written to manifest during transition period
