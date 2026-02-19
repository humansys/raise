# Cursor IDE — Skills & Agent Research (RAISE-197)

> Source: SES-212, 2026-02-18. Agent research.

## Summary

Cursor has NO native skills or workflows. Most limited of the 5 IDEs.

## Capabilities

### Rules (`.cursor/rules/*.mdc`)
- YAML frontmatter + markdown body
- Fields: `description`, `globs`, `alwaysApply`
- Four types: Always, Auto-Attach (glob), Agent (AI decides), Manual (`@rule-name`)
- Static text only — no tool invocation, no gates
- `.mdc` extension is legacy; new format is folders with `RULE.md`

### AGENTS.md
- Supported (Linux Foundation standard, shared with Windsurf/Copilot)
- Plain markdown, no frontmatter required
- Nested: nearest `AGENTS.md` to edited file takes precedence (monorepo)
- 60,000+ open-source projects now include it

### Custom Modes (agents)
- Role + model + tool permissions + system prompt
- GUI-configured only (not yet file-based)
- `.cursor/modes.json` announced but not stable
- NOT version-controlled

### Notepads
- Rich-text markdown stored in local SQLite
- NOT version-controlled, NOT shareable
- Referenced via `@NotepadName` in chat

## What Cursor DOESN'T Have
- No skills directory
- No workflows / slash commands from files
- No tool invocation from rules
- No parameterized templates
- No enforcement/gates

## RaiSE Integration Path
1. `.cursor/rules/raise.mdc` — instructions (alwaysApply: true)
2. `AGENTS.md` — cross-tool compatible instructions
3. Wait for `.cursor/modes.json` for agent definitions

## Sources
- [Cursor Rules Docs](https://cursor.com/docs/context/rules)
- [AGENTS.md Official](https://agents.md/)
- [Awesome Cursor Rules MDC](https://github.com/sanjeed5/awesome-cursor-rules-mdc)
