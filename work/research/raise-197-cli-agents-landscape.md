# AI CLI Coding Agent Configuration Landscape (RAISE-197)

> Source: SES-213, 2026-02-18. Agent research.

## Summary

SKILL.md has converged as a de facto cross-tool standard. AGENTS.md is gaining traction (60K+ repos) but adoption is fragmented. Each tool uses its own dot-directory for config.

## Comparison Table

| Tool | Instructions | Skills | AGENTS.md | Config Dir | Detection Markers |
|---|---|---|---|---|---|
| **Claude Code** | `CLAUDE.md` | `.claude/skills/` | No | `.claude/` | `CLAUDE.md`, `.claude/` |
| **Codex CLI** | `AGENTS.md` | `.agents/skills/` | Native | `.codex/` | `AGENTS.md`, `.agents/` |
| **Gemini CLI** | `GEMINI.md` | `.gemini/skills/` | Partial (`AGENT.md`) | `.gemini/` | `GEMINI.md`, `.gemini/` |
| **Aider** | `.aider.conf.yml` | No | Via `--read` | (root file) | `.aider.conf.yml` |
| **Kilo Code** | `.kilocode/rules/` | No (Memory Bank) | Supported | `.kilocode/` | `.kilocode/` |
| **Amazon Q** | `.amazonq/rules/` | JSON custom agents | No | `.amazonq/` | `.amazonq/` |
| **Cline** | `.clinerules` | `.cline/skills/` | Pending PR | `.cline/` | `.clinerules`, `.cline/` |
| **Goose** | `.goosehints` | No (MCP) | Listed supporter | `~/.config/goose/` | `.goosehints` |
| **OpenCode** | `AGENTS.md` | `.opencode/skills/` | Native | `.opencode/` | `.opencode/` |

## SKILL.md Convergence

The SKILL.md format (YAML frontmatter + markdown + optional subdirs) is identical across:

| Tool | Skills Path |
|---|---|
| Claude Code | `.claude/skills/<name>/SKILL.md` |
| Codex CLI | `.agents/skills/<name>/SKILL.md` |
| Gemini CLI | `.gemini/skills/<name>/SKILL.md` |
| Cursor 2.4+ | Project-level (agentskills.io spec) |
| Cline | `.cline/skills/` or `.claude/skills/` |
| OpenCode | `.opencode/skills/` |

Tools that do NOT support SKILL.md: Aider, Kilo Code, Amazon Q, Goose.

## Per-Tool Details

### Codex CLI (OpenAI)
**Evidence: Very High**
- `AGENTS.md` native — drove the standard. Hierarchical: `~/.codex/AGENTS.md` → project root. Also `AGENTS.override.md`.
- Skills: `.agents/skills/<name>/SKILL.md`. Global: `~/.codex/skills/`. Ships built-in skills in `~/.codex/skills/.system/`.
- Slash: `/init`, `/review`, `/diff`, `/skills`, `$skill-name` for invocation.
- Config: `~/.codex/config.toml` for model, permissions, skill toggles.

### Gemini CLI (Google)
**Evidence: Very High**
- `GEMINI.md` hierarchical (CWD upward to `.git` root). Also reads `AGENT.md`.
- Skills: `.gemini/skills/<name>/SKILL.md`. On-demand loading (name/description indexed at startup).
- Extensions system: 70+ extensions (prompts, MCP servers, commands, themes, hooks, sub-agents, skills).
- `.geminiignore` for exclusions.

### Aider
**Evidence: High**
- Simple by design. No skills, no config directory.
- `.aider.conf.yml` at root or `~/.aider.conf.yml`.
- `CONVENTIONS.md` loaded via `--read`. AGENTS.md via `--read` too.
- Git-native: auto-commits changes. 100+ models.

### Kilo Code
**Evidence: High**
- VS Code extension + CLI 1.0 (2026). 1.5M+ users.
- Memory Bank: `.kilocode/rules/memory-bank/` with structured markdown (brief.md, etc.).
- AGENTS.md supported. No SKILL.md.
- Cross-platform sync (VS Code, JetBrains, CLI, Slack).

### Amazon Q Developer CLI
**Evidence: High**
- `.amazonq/rules/*.md` — domain-specific rules, auto-loaded.
- Custom agents: JSON in `~/.aws/amazonq/cli-agents/` or `.aws/amazonq/agents/`.
- No AGENTS.md, no SKILL.md. Own ecosystem.

### Cline
**Evidence: High**
- VS Code extension. `.clinerules` (single file or directory).
- Skills (experimental, v3.48.0+): `.cline/skills/` or `.claude/skills/` (Claude Code compatible).
- AGENTS.md pending (issue #5033, discussion #6162).

### Goose (Block)
**Evidence: Medium**
- `.goosehints` at project root. Open-source by Block.
- Extensibility via MCP servers, not skills.
- Listed as AGENTS.md supporter.

### OpenCode
**Evidence: Medium**
- `AGENTS.md` supported. Rich config surface.
- `.opencode/` with subdirs: `agents/`, `commands/`, `modes/`, `plugins/`, `skills/`, `tools/`, `themes/`.
- Most granular open-source CLI config.

## AGENTS.md Adoption (Feb 2026)

60K+ repos. Maintained at agents.md.

| Status | Tools |
|---|---|
| **Native** | Codex CLI, OpenCode |
| **Supported** | Kilo Code, Cursor, Windsurf, Copilot |
| **Partial** | Gemini CLI (`AGENT.md`), Aider (via `--read`) |
| **No** | Claude Code (`CLAUDE.md`), Amazon Q (`.amazonq/rules/`) |
| **Pending** | Cline (PR in progress) |

## Key Findings for RaiSE

1. **SKILL.md is the winning format** — 6+ tools use identical format, only path differs per tool
2. **Instructions are fragmented** — each tool has its own file convention, no single standard
3. **AGENTS.md is the closest to universal instructions** — but Claude Code and Amazon Q don't use it
4. **Detection is per-tool** — each uses own dot-directory, making auto-detection straightforward
5. **Copilot remains the outlier** — `.github/agents/` uses different frontmatter (adds `tools`, `infer`)
6. **CLIs are valid distribution targets** — Codex CLI, Gemini CLI, OpenCode all support SKILL.md

## Sources
- [Codex CLI AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- [Codex Agent Skills](https://developers.openai.com/codex/skills/)
- [Gemini CLI Configuration](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html)
- [Gemini CLI Skills](https://geminicli.com/docs/cli/skills/)
- [Aider Configuration](https://aider.chat/docs/config.html)
- [Kilo Code Memory Bank](https://kilo.ai/docs/advanced-usage/memory-bank)
- [Amazon Q Project Rules](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-project-rules.html)
- [Cline Skills](https://docs.cline.bot/features/skills)
- [OpenCode Config](https://opencode.ai/docs/config/)
- [AGENTS.md Standard](https://agents.md/)
