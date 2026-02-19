---
type: module
name: agents
purpose: "Bundled YAML agent configurations and CopilotPlugin for multi-agent skill distribution"
status: current
depends_on: [config]
depended_by: [onboarding, cli]
entry_points: []
public_api:
  - "copilot_plugin.CopilotPlugin"
components: 7
constraints:
  - "YAML files are package data — not Python. Read via importlib.resources."
  - "Plugin classes must satisfy AgentPlugin Protocol from config.agent_plugin"
  - "Built-in configs are Tier-1 only — community Tier-2 and third-party Tier-3 live outside the package"
---

## Purpose

The agents module ships the 5 built-in Tier-1 agent configurations as YAML files and provides the `CopilotPlugin` — the only built-in agent that requires code-level customization (Copilot uses different SKILL.md frontmatter).

This module is **data-heavy, code-light**: 5 YAML files + 1 plugin class. The actual loading logic lives in `config.agent_registry`.

## Key Files

- **`claude.yaml`** — Claude Code (CLAUDE.md, .claude/skills/)
- **`cursor.yaml`** — Cursor 2.4+ (AgentSkills spec, .cursor/skills/)
- **`windsurf.yaml`** — Windsurf (.windsurf/skills/, .windsurf/workflows/)
- **`copilot.yaml`** — GitHub Copilot (.github/agents/, .github/prompts/) → references `copilot_plugin`
- **`antigravity.yaml`** — Antigravity (.agent/skills/, .agent/workflows/)
- **`copilot_plugin.py`** — `CopilotPlugin` implementing `AgentPlugin` Protocol. Transforms SKILL.md frontmatter (adds `tools`, `infer`; removes `license`, `compatibility`) and generates `.github/prompts/*.prompt.md` via `post_init`.

## Data Flow

```
rai init --agent copilot
  → config.agent_registry.load_registry()
      → importlib.resources.files("rai_cli.agents") / "copilot.yaml"
      → AgentConfig(plugin="rai_cli.agents.copilot_plugin")
  → AgentRegistry.get_plugin("copilot")
      → importlib.import_module("rai_cli.agents.copilot_plugin")
      → CopilotPlugin()
  → scaffold_skills(plugin=CopilotPlugin)
      → CopilotPlugin.transform_skill(frontmatter, body, config)
  → CopilotPlugin.post_init(project_root, config)
      → writes .github/prompts/*.prompt.md
```

## Extension Points

Third-party agents use the same YAML format but live in:
- Project: `.raise/agents/your-agent.yaml`
- User: `~/.rai/agents/your-agent.yaml`

Third-party plugins are pip-installable packages; referenced by module path in YAML `plugin:` field.
