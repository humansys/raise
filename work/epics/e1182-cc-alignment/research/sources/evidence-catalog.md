# Evidence Catalog: CC Skill Metadata Best Practices

## Primary Sources

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| S1 | [Claude Code Skills Docs](https://code.claude.com/docs/en/skills) | Official docs | Very High | Complete frontmatter reference: `description`, `allowed-tools`, `disable-model-invocation`, `user-invocable`, `context`, `model`, `effort`, `paths`, `hooks`. Description truncated at 250 chars. Budget = 1% context window (~8K chars default). |
| S2 | [CC Agent SDK — Slash Commands](https://platform.claude.com/docs/en/agent-sdk/slash-commands) | Official docs | Very High | Frontmatter with `allowed-tools` shown in examples. Bash glob patterns (`Bash(git add:*)`). `disable-model-invocation` for manual-only. |
| S3 | [anthropics/claude-code repo](https://github.com/anthropics/claude-code) — `.claude/commands/*.md` | Primary (source code) | Very High | 100% of CC's own commands declare `allowed-tools`. Bash always filtered by subcommand. Descriptions 20-93 chars, verb-first. |
| S4 | [CC plugin-dev frontmatter-reference.md](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/command-development/references/frontmatter-reference.md) | Official reference | Very High | Description max ~60 chars recommended. `allowed-tools` supports string, comma-separated, or array. Bash(command:*) pattern documented. `disable-model-invocation` for destructive/interactive ops. |

## Secondary Sources

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| S5 | [fp8.co — Claude Code Skills Complete Developer Guide](https://fp8.co/articles/Claude-Code-Skills-Complete-Developer-Guide) | Community guide | High | Description max 1024 chars but front-load key use case. Include trigger phrases. `allowed-tools` with file-type globs (`Read(**/*.ts)`). Principle of least privilege. |
| S6 | [alexop.dev — Claude Code Customization Guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) | Community guide | High | "Claude decides whether to invoke a skill largely based on its description." Be task-specific, not feature-specific. Include multiple use-case categories. Keep concise — descriptions parsed every message. |
| S7 | [Geeky Gadgets — Claude Code Skills Best Practices](https://www.geeky-gadgets.com/claude-code-skills-best-practices/) | Community analysis | Medium | Limit to 20-30 skills. Quality over quantity. Clear descriptions improve activation rates. Progressive disclosure pattern. |
| S8 | [skillzwave.ai — Claude Code Skills Guide](https://skillzwave.ai/claude-code-skills-guide/) | Community guide | Medium | Single responsibility per skill. Action-oriented trigger phrases. Granular tool restrictions with wildcards. |

## Tertiary Sources

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| S9 | [CC plugin-dev skill-reviewer agent](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/agents/skill-reviewer.md) | Internal tooling | High | Notes `when_to_use` as "deprecated, use description only". Validates `allowed-tools` is array if present. |
| S10 | RaiSE codebase — 35 skills audited | Primary (our code) | Very High | 0/35 declare `allowed-tools`. 0/35 use `disable-model-invocation`. All descriptions >150 chars (exceed 250 truncation limit). |
