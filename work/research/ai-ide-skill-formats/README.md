# AI IDE Skill/Prompt Formats Research

> Research ID: RES-SKILL-FMT-001
> Date: 2026-02-05
> Status: Complete
> Decision: F14.14 architecture

## Executive Summary

**Finding:** An emerging standard exists — **AGENTS.md** — backed by Linux Foundation and supported by 20+ tools. However, most IDEs also maintain their own proprietary formats for advanced features.

**Recommendation:** Support AGENTS.md as canonical + Claude Code native format. Platform detection is lower priority than standards alignment.

---

## Research Question

How do AI coding tools handle custom skills/prompts? What are the file locations, formats, and is there an emerging standard?

---

## Key Findings

### 1. AGENTS.md is the Emerging Standard

**Confidence: HIGH** (5 sources, Linux Foundation backing)

[AGENTS.md](https://agents.md/) is a Linux Foundation-stewarded open format:
- Plain Markdown, no required structure
- Supported by 20+ tools including Cursor, GitHub Copilot, Zed, Claude, Google Jules, Aider
- Hierarchical: closest file to edited file wins
- No YAML frontmatter required

**Supported tools:** OpenAI Codex, Google Jules, Cursor, VS Code, GitHub Copilot, Anthropic Claude, Aider, Zed, Warp, Factory, and more.

### 2. Each IDE Also Has Proprietary Formats

Despite AGENTS.md convergence, each tool maintains its own format for advanced features:

| Tool | Proprietary Location | Format | Notes |
|------|---------------------|--------|-------|
| **Claude Code** | `.claude/skills/*/SKILL.md` | YAML frontmatter + Markdown | Hooks, lifecycle |
| **Cursor** | `.cursor/rules/*.mdc` | YAML frontmatter + Markdown | Globs, apply modes |
| **Windsurf** | `.windsurf/rules/*.md` | Markdown | GUI wrapper |
| **GitHub Copilot** | `.github/instructions/*.instructions.md` | YAML frontmatter + Markdown | applyTo globs |
| **Continue.dev** | `.continue/prompts/*.prompt.md` | YAML frontmatter + Markdown | Slash commands |
| **Zed** | `.rules` or Rules Library | Plain Markdown | Priority order fallback |
| **Gemini Code Assist** | `.idea/project.prompts.xml` | XML | JetBrains ecosystem |
| **Aider** | `CONVENTIONS.md` (explicit load) | Plain Markdown | No auto-discovery |

### 3. Common Patterns Across Formats

**Confidence: HIGH** (observed in 6+ tools)

| Pattern | Adoption |
|---------|----------|
| Markdown as base format | Universal |
| YAML frontmatter for metadata | 5/8 tools |
| Glob patterns for file matching | 4/8 tools |
| Hierarchical resolution (nearest wins) | 4/8 tools |
| Slash command invocation | 3/8 tools |

### 4. Zed's Compatibility Approach is Instructive

Zed checks for rules files in this priority order:
1. `.rules`
2. `.cursorrules`
3. `.windsurfrules`
4. `.clinerules`
5. `.github/copilot-instructions.md`
6. `AGENT.md`
7. `AGENTS.md`
8. `CLAUDE.md`
9. `GEMINI.md`

**First match wins.** This allows one file to work across multiple tools.

---

## Evidence Catalog

| Source | Type | Evidence Level | Key Finding |
|--------|------|----------------|-------------|
| [agents.md](https://agents.md/) | Primary | Very High | Linux Foundation standard, 20+ tools |
| [Cursor Docs](https://cursor.com/docs/context/rules) | Primary | Very High | `.cursor/rules/*.mdc` with YAML frontmatter |
| [Zed Docs](https://zed.dev/docs/ai/rules) | Primary | Very High | Multi-format compatibility list |
| [GitHub Copilot Docs](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) | Primary | Very High | `.github/instructions/*.instructions.md` |
| [Continue.dev Docs](https://docs.continue.dev/customize/deep-dives/prompts) | Primary | High | `.prompt.md` with YAML frontmatter |
| [Windsurf Docs](https://docs.windsurf.com/) | Primary | High | `.windsurf/rules/` directory |
| [Gemini Docs](https://developer.android.com/studio/gemini/rules) | Primary | High | XML format in `.idea/` |
| [Aider Docs](https://aider.chat/docs/usage/conventions.html) | Primary | High | Explicit `CONVENTIONS.md` loading |

---

## Implications for F14.14

### Architecture Decision

**Option A: Platform-specific detection (original scope)**
- Detect Cursor, Windsurf, etc.
- Parse each format natively
- Complexity: HIGH, maintenance burden

**Option B: Standards-first (recommended)**
- Support AGENTS.md as primary
- Support Claude Code native (`.claude/skills/`)
- Support `.raise/skills/` as RaiSE canonical
- Ignore proprietary formats (users can use AGENTS.md)
- Complexity: LOW, standards-aligned

### Recommended Approach

```
Priority order for skill discovery:
1. .claude/skills/        # Claude Code native (current)
2. .raise/skills/         # RaiSE canonical (future)
3. AGENTS.md / CLAUDE.md  # Standards compatibility
```

**Rationale:**
- Claude Code is our primary target (F&F deadline)
- AGENTS.md provides cross-platform portability
- `.raise/skills/` prepares for platform independence
- Avoid proprietary format fragmentation

### What This Means for F14.14 Scope

**Keep:**
- `raise skill list` — List `.claude/skills/`
- `raise skill scaffold` — Generate in `.claude/skills/`
- `raise skill validate` — Validate SKILL.md structure
- `raise skill check-name` — Ontology compliance

**Simplify:**
- Platform detection → Just check for `.claude/skills/` existence
- Multi-platform support → Defer to post-F&F
- AGENTS.md support → Nice-to-have, simple to add later

---

## References

- [AGENTS.md Specification](https://agents.md/)
- [Cursor Rules Documentation](https://cursor.com/docs/context/rules)
- [Zed AI Rules](https://zed.dev/docs/ai/rules)
- [GitHub Copilot Custom Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [Continue.dev Prompts](https://docs.continue.dev/customize/deep-dives/prompts)
- [Gemini Code Assist Rules](https://developer.android.com/studio/gemini/rules)
- [Aider Conventions](https://aider.chat/docs/usage/conventions.html)

---

*Research completed: 2026-02-05*
*Researcher: Rai*
