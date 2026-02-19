# Google Antigravity — Skills & Agent Research (RAISE-197)

> Source: SES-212, 2026-02-18. Agent research.

## Summary

Antigravity = standalone IDE (NOT same as Gemini Code Assist or Gemini CLI).
Architecture is nearly identical to RaiSE's skill system.

## Identity Clarification

| Product | Type | Relation |
|---------|------|----------|
| **Antigravity** | Standalone agent-first IDE | Full IDE, `.agent/` convention |
| **Gemini Code Assist** | IDE extension (VS Code, IntelliJ) | Separate product, own agent mode |
| **Gemini CLI** | Terminal agent | Shares `.agent/` convention with Antigravity |

## Capabilities

### Rules (`.agent/rules/*.md`)
- Always-on guardrails, injected into system prompt
- Plain markdown files
- Global: `~/.gemini/GEMINI.md` (single file)

### Skills (`.agent/skills/<name>/SKILL.md`)
- YAML frontmatter (`name` optional, `description` MANDATORY) + markdown body
- Supporting dirs: `scripts/`, `resources/`, `assets/`
- Progressive disclosure: loaded only when semantic match
- Agent-triggered, NOT user-invoked (no slash commands for skills)
- Scopes: workspace (`.agent/skills/`) and global (`~/.gemini/antigravity/skills/`)

### Workflows (`.agent/workflows/*.md`)
- Plain markdown, filename = slash command
- User-triggered via `/command-name`
- Scopes: workspace and global (`~/.gemini/antigravity/global_workflows/`)

### Manager View
- Multi-agent orchestration console
- Agents work asynchronously (editor, terminal, browser)
- Artifacts: plans, task lists, screenshots, diffs
- Knowledge Base accumulates patterns
- 4 autonomy modes: agent-driven, agent-assisted, review-driven, custom

## Taxonomy (Google's own framing)

| Concept | Nature | Loading | Trigger |
|---------|--------|---------|---------|
| Rules | Passive guardrails | Always-on | Automatic |
| Skills | On-demand expertise | Agent-triggered (semantic) | Automatic |
| Workflows | Saved prompts | User-triggered | `/slash-command` |

## Complete Directory Structure

```
.agent/
├── rules/                        # Always-on (markdown)
│   └── raise.md
├── skills/                       # On-demand (SKILL.md + resources)
│   └── rai-story-start/
│       ├── SKILL.md
│       ├── scripts/
│       └── resources/
└── workflows/                    # Slash commands (markdown)
    └── rai-story-start.md

~/.gemini/
├── GEMINI.md                     # Global rules
└── antigravity/
    ├── skills/                   # Global skills
    └── global_workflows/         # Global workflows
```

## RaiSE Integration Path
1. `.agent/rules/raise.md` — always-on instructions
2. `.agent/skills/` — scaffold skills (same SKILL.md format!)
3. `.agent/workflows/` — generate workflow shims (Fernando already did this)

## Sources
- [Google Codelabs - Antigravity Skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills)
- [Customize Antigravity - Mete Atamel](https://atamel.dev/posts/2025/11-25_customize_antigravity_rules_workflows/)
- [Google Developers Blog - Antigravity](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/)
- [Antigravity vs Gemini Code Assist](https://www.augmentcode.com/tools/google-antigravity-vs-gemini-code-assist)
