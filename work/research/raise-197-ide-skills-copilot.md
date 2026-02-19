# GitHub Copilot — Skills & Agent Research (RAISE-197)

> Source: SES-212, 2026-02-18. Agent research.

## Summary

Copilot has the RICHEST extensibility model. Agents + prompts + per-directory instructions.

## Capabilities

### Instructions (`.github/copilot-instructions.md`)
- Always-on, project-wide
- Plain markdown, no frontmatter
- Applied to ALL Copilot Chat requests
- ~2 pages recommended limit

### Per-Directory Instructions (`.instructions.md`)
- Location: `.github/instructions/` or custom via settings
- YAML frontmatter with `applyTo` glob pattern
- Combines with project-level instructions (both applied)
- VS Code also recognizes `CLAUDE.md` (opt-in) and `AGENTS.md` (opt-in)

### Custom Agents (`.github/agents/*.md`)
- YAML frontmatter + markdown body
- Key fields: `description` (required), `name`, `tools`, `infer`, `mcp-servers`, `target`
- `infer: true` — agent auto-selected based on task (like Windsurf/Antigravity semantic match)
- Tool aliases: `execute`/`shell`/`bash`, `read`, `edit`/`write`, `search`/`grep`/`glob`, `agent`/`task`, `web`
- MCP integration via `mcp-servers` field (org/enterprise level)
- 30,000 char limit per agent file
- Priority: repo > org > enterprise

### Prompt Files (`.github/prompts/*.prompt.md`)
- Reusable slash commands
- YAML frontmatter: `description`, `agent`, `model`, `tools`
- Variables: `${file}`, `${selection}`, `${workspaceFolder}`, `${input:varName}`
- Tool references: `#tool:<tool-name>` in body
- Invoked via `/prompt-name` in chat

### Built-in Participants
- `@workspace`, `@terminal`, `@vscode` — NOT customizable via files
- Custom participants require VS Code extension (Chat Participant API)

## Architecture Comparison

| RaiSE Concept | Copilot Equivalent |
|---------------|-------------------|
| `CLAUDE.md` | `.github/copilot-instructions.md` |
| `.claude/skills/*/SKILL.md` | `.github/agents/*.md` (with tool restrictions) |
| Skills as slash commands | `.github/prompts/*.prompt.md` |
| Per-module context | `.instructions.md` with `applyTo` globs |

## RaiSE Integration Path
1. `.github/copilot-instructions.md` — always-on instructions
2. `.github/agents/` — map skills to agents (different frontmatter: `tools`, `infer`)
3. `.github/prompts/` — map skills to slash commands (`.prompt.md` format)
4. `AGENTS.md` — cross-tool compatible

## Frontmatter Differences

```yaml
# RaiSE SKILL.md
---
name: rai-story-start
description: Initialize story with branch and scope commit
---

# Copilot agent equivalent
---
name: rai-story-start
description: Initialize story with branch and scope commit
tools: ['execute', 'read', 'edit', 'search']
infer: true
---

# Copilot prompt equivalent
---
description: Initialize story with branch and scope commit
agent: agent
tools: ['execute', 'read', 'edit', 'search']
---
```

## Sources
- [GitHub Docs - Repository Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [VS Code - Custom Instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [VS Code - Prompt Files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [GitHub Docs - Custom Agents](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
