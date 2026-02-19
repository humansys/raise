# Cursor IDE: Skills-Like Functionality Research (RAISE-197)

> Source: SES-213, 2026-02-18. Agent research.

## Critical Update: Cursor 2.4 Added Native Skills (Jan 2026)

**Evidence level: High** (multiple independent sources confirm)

Our earlier research (SES-212) that "Cursor has NO native skills" is **outdated**. Cursor 2.4 (released ~January 2026) introduced native `SKILL.md` support via the [Agent Skills open specification](https://agentskills.io/specification).

Key facts:
- Cursor now supports **Agent Skills** via `SKILL.md` files, both in editor and CLI
- Agents discover and apply skills when domain-specific knowledge is relevant
- Skills can include custom commands, scripts, and reference docs
- YAML frontmatter (`name`, `description`, `license`, `compatibility`, `metadata`) + Markdown body
- Optional bundled resources: `scripts/`, `references/`, `assets/`
- Recommended limit: keep SKILL.md body under 500 lines

**This means ALL 5 IDEs now support SKILL.md natively.**

## Cursor Rules (`.cursor/rules/*.mdc`)

**Evidence level: High**

Rules remain the primary configuration mechanism. `.mdc` format = YAML frontmatter + Markdown body.

| Type | Frontmatter | Behavior |
|------|------------|----------|
| **Always** | `alwaysApply: true` | Always injected into context |
| **Auto-Attach** | `globs: "*.py,*.ts"` | Injected when matching files referenced |
| **Agent-Requested** | `description: "..."` | Agent reads description, decides to include |
| **Manual** | No frontmatter | User must `@`-reference |

### Community Repositories
- **cursor.directory** — Community hub with pre-built rules + generator
- **PatrickJS/awesome-cursorrules** — Curated `.cursorrules` files
- **sanjeed5/awesome-cursor-rules-mdc** — Curated `.mdc` rule files
- **chrisboden/cursor-skills** — MCP-based skill orchestration (pre-2.4 workaround)

## AGENTS.md in Cursor

**Evidence level: Medium**

- Cursor reads `AGENTS.md` at repo root and nearest in nested folders (monorepo)
- Works as always-on context (like `alwaysApply: true` rule)
- Less granular than `.mdc` rules (no globs, no agent-requested filtering)

## Custom Modes

**Evidence level: Medium**

- GUI-configured, **NOT file-configurable** per-project
- Stored per-user, not version-controllable
- No `.cursor/modes.json` yet
- **Not a viable distribution target**

## Notepads

**Evidence level: High**

- Stored in local SQLite, **NOT version-controllable**
- Open feature request (issue #2208) for file-based notepads
- **Not a distribution target**

## Cursor CLI

**Evidence level: High**

- Beta CLI with terminal agent capability
- Modes: Interactive TUI, Headless (`-p`/`--print`), Plan, Ask
- Auth: `CURSOR_API_KEY` env var
- Output: `--output-format json` or `stream-json`
- Skills distributed as SKILL.md work in both editor and CLI

## RaiSE Integration Path

1. `.cursor/rules/raise.mdc` — always-on instructions (with `alwaysApply: true` frontmatter)
2. `.cursor/skills/` or project-level SKILL.md — native skills (Cursor 2.4+)
3. `AGENTS.md` — cross-tool compatible baseline

## Sources
- [Cursor 2.4: Subagents, Skills](https://www.aimakers.co/blog/cursor-2-4-subagents/)
- [SKILL.md Specification | DeepWiki](https://deepwiki.com/agentskills/agentskills/2.2-skill.md-specification)
- [skill.md: An open standard | Mintlify](https://www.mintlify.com/blog/skill-md)
- [Cursor Rules Deep Dive | Mervin Praison](https://mer.vin/2025/12/cursor-ide-rules-deep-dive/)
- [chrisboden/cursor-skills](https://github.com/chrisboden/cursor-skills)
- [Cursor CLI | Real Python](https://realpython.com/ref/ai-coding-tools/cursor-cli/)
