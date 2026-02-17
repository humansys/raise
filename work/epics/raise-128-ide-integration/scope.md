## Epic Scope: RAISE-128 IDE Integration

**JIRA:** [RAISE-128](https://humansys.atlassian.net/browse/RAISE-128)
**Objective:** Make rai-cli work with Antigravity (Google) via `rai init --ide antigravity`, mapping skills, instructions, and workflows to Antigravity's native conventions.

**In Scope:**
- `--ide` flag for `rai init` with `antigravity` support (claude remains default)
- Path mapping for Antigravity: `.agent/skills/`, `.agent/rules/raise.md`, `.agent/workflows/`
- Scaffold engine abstraction to decouple from Claude Code paths
- Tests for Antigravity paths

**Out of Scope:**
- Gemini CLI support → future story
- Other IDEs (Cursor, Windsurf, Continue, etc.) → future
- Runtime IDE detection → RAISE-127 Multi-Agent
- Slash command content changes (SKILL.md is universal) → not needed
- IDE-specific memory paths → defer

**Research Foundation:**
- SES-006: 9 IDEs mapped, 3 coupling points identified in `rai init`
- `dev/rai-architecture-discovery.md` sections 7-8
- Antigravity canonical dir is `.agent/`, not `.antigravity/` (legacy)
- Three Antigravity concepts: rules (always-on), skills (on-demand), workflows (user-triggered)

**Coupling Points (from research):**
1. `scaffold_skills()` → hardcoded `.claude/skills/`
2. `CLAUDE.md` generation → hardcoded filename
3. `get_claude_memory_path()` → `~/.claude/projects/` (Claude-specific, Antigravity skips)

**Antigravity Mapping:**
| Concept | Claude Code | Antigravity |
|---------|-----------|-------------|
| Skills dir | `.claude/skills/` | `.agent/skills/` |
| Instructions | `CLAUDE.md` | `.agent/rules/raise.md` |
| Slash commands | Skills = slash commands | `.agent/workflows/*.md` |
| Loading | All skills always loaded | Progressive disclosure (lazy by description) |

**Features (planned):**
- TBD via `/rai-epic-design`

**Done when:**
- [ ] `rai init --ide antigravity` scaffolds to correct Antigravity paths
- [ ] `rai init` (no flag) defaults to claude (backward compatible)
- [ ] All features complete
- [ ] Epic retrospective done
- [ ] Merged to `v2`
