# Windsurf IDE — Skills & Agent Research (RAISE-197)

> Source: SES-212, 2026-02-18. Agent research.

## Summary

Windsurf has the CLOSEST architecture to RaiSE. Skills, workflows, rules — same taxonomy.

## Capabilities

### Skills (`.windsurf/skills/<name>/SKILL.md`)
- Introduced Jan 12, 2026
- YAML frontmatter (`name`, `description`) + markdown body
- Supporting files: scripts, templates, checklists in skill folder
- Triggering: automatic (semantic match on description) OR manual (`@skill-name`)
- Scopes: workspace (`.windsurf/skills/`) and global (`~/.codeium/windsurf/skills/`)

### Workflows (`.windsurf/workflows/*.md`)
- Plain markdown files, one per workflow
- Triggered via `/slash-command` (filename = command name)
- Sequential step processing
- Composable (workflows can call other workflows)
- 12,000 char limit per file
- Scopes: workspace and enterprise system-level

### Rules (`.windsurf/rules/*.md`)
- Markdown with optional frontmatter for activation mode
- Four modes: Always-on, Glob, Model Decision, Manual (`@rule-name`)
- 12,000 char limit
- Scopes: workspace, global, system/enterprise

### AGENTS.md
- Supported (auto-scoping by directory placement)
- Case-insensitive, walks up to git root

### Memories
- Auto-generated context persisted across sessions
- `~/.codeium/windsurf/memories/`
- User can prompt "create a memory of..."

## Architecture Comparison

| RaiSE Concept | Windsurf Equivalent |
|---------------|-------------------|
| `.claude/skills/*/SKILL.md` | `.windsurf/skills/*/SKILL.md` (identical format!) |
| Skills as slash commands | `.windsurf/workflows/*.md` as `/commands` |
| `CLAUDE.md` | `.windsurf/rules/raise.md` (always-on) + `AGENTS.md` |
| `rai memory` | Memories (simpler, flat) |

## RaiSE Integration Path
1. `.windsurf/rules/raise.md` — always-on instructions
2. `.windsurf/skills/` — scaffold skills (same SKILL.md format!)
3. `.windsurf/workflows/` — generate workflow shims per skill
4. `AGENTS.md` — cross-tool compatible

## Sources
- [Cascade Skills Docs](https://docs.windsurf.com/windsurf/cascade/skills)
- [Workflows Docs](https://docs.windsurf.com/windsurf/cascade/workflows)
- [AGENTS.md Docs](https://docs.windsurf.com/windsurf/cascade/agents-md)
- [Rules & Workflows Best Practices](https://www.paulmduvall.com/using-windsurf-rules-workflows-and-memories/)
