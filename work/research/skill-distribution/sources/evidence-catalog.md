# Evidence Catalog: Skill Distribution for AI IDEs

## Sources

### S1: Claude Code Skills Documentation
- **Type**: Primary
- **Evidence Level**: Very High
- **URL**: https://code.claude.com/docs/en/slash-commands
- **Key Finding**: Skills stored in `.claude/skills/{name}/SKILL.md` with optional frontmatter. User-invocable via `/name`. Also supports `~/.claude/skills/` for global skills.
- **Relevance**: Native format for Claude Code — our primary target.

### S2: Cursor Rules Documentation
- **Type**: Primary
- **Evidence Level**: Very High
- **URL**: https://cursor.com/docs/context/rules
- **Key Finding**: Rules in `.cursor/rules/*.mdc` (markdown with YAML frontmatter). Four types: Always, Auto (by description), Glob-matched, Manual (@-mention). Legacy `.cursorrules` still works.
- **Relevance**: Second most popular AI IDE. Must support.

### S3: Windsurf Rules
- **Type**: Primary
- **Evidence Level**: High
- **URL**: https://docs.windsurf.com/windsurf/cascade/memories
- **Key Finding**: `.windsurfrules` at project root (legacy) or `.windsurf/rules/rules.md` (modern). 6000 char limit per workspace.
- **Relevance**: Third major AI IDE. Simple format.

### S4: GitHub Copilot Instructions
- **Type**: Primary
- **Evidence Level**: Very High
- **URL**: https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
- **Key Finding**: `.github/copilot-instructions.md` for repo-wide, `.github/instructions/*.instructions.md` with `applyTo` glob frontmatter for path-specific. Also supports `AGENTS.md`.
- **Relevance**: Most widely used AI assistant. Must support.

### S5: ai-rulez — Multi-IDE Rule Generator
- **Type**: Secondary
- **Evidence Level**: High
- **URL**: https://github.com/Goldziher/ai-rulez
- **Key Finding**: Single source in `.ai-rulez/` (YAML+MD), generates native configs for 18+ IDEs. Pattern: canonical source → IDE-specific adapters. Supports rules, context, skills, agents.
- **Relevance**: Validates the "single source, multiple targets" architecture.

### S6: Ruler — Universal Rule Distribution
- **Type**: Secondary
- **Evidence Level**: Medium
- **URL**: https://github.com/intellectronica/ruler
- **Key Finding**: `.ruler/` directory with MD files, `ruler.toml` config, `apply` command generates for 25+ agents. Concatenates MD files in precedence order.
- **Relevance**: Simpler approach — just concatenate and distribute.

### S7: rulesync
- **Type**: Secondary
- **Evidence Level**: Medium
- **URL**: https://github.com/jpcaparas/rulesync
- **Key Finding**: Syncs instruction files across Claude, Cursor, Windsurf, Gemini, Copilot. Focus on keeping files in sync.
- **Relevance**: Shows demand for multi-IDE sync.

### S8: vibe-rules
- **Type**: Secondary
- **Evidence Level**: Medium
- **URL**: https://github.com/FutureExcited/vibe-rules
- **Key Finding**: Load/distribute rules for Cursor, Claude Code, Windsurf, Gemini, Codex, Cline, Roo, VSCode.
- **Relevance**: Community tool showing the same pattern.

### S9: Aider Conventions
- **Type**: Primary
- **Evidence Level**: High
- **URL**: https://aider.chat/docs/usage/conventions.html
- **Key Finding**: `CONVENTIONS.md` loaded via `.aider.conf.yml`. Read-only, cached. Simple markdown.
- **Relevance**: Shows the "just markdown" approach works for conventions.

### S10: AGENTS.md Convention
- **Type**: Secondary
- **Evidence Level**: High
- **URL**: https://kau.sh/blog/agents-md/
- **Key Finding**: Emerging cross-IDE standard. Copilot, Cursor, and others recognize `AGENTS.md`. Could become the universal format.
- **Relevance**: Potential convergence point for multi-IDE support.
