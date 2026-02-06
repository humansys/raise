# Evidence Catalog: Multi-Developer Configuration Patterns

## Sources

### S1: Aider Configuration
**URL:** https://aider.chat/docs/config/aider_conf.html
**Type:** Primary (official docs)
**Evidence Level:** Very High
**Key Finding:** Aider searches for `.aider.conf.yml` in home → git root → cwd (later wins). ALL `.aider*` files are gitignored by default.
**Relevance:** Direct precedent for personal vs shared config separation.

### S2: Continue Configuration
**URL:** https://docs.continue.dev/customize/deep-dives/configuration
**Type:** Primary (official docs)
**Evidence Level:** Very High
**Key Finding:** Personal in `~/.continue/config.yaml`, project override via `.continuerc.json` with `mergeBehavior` property.
**Relevance:** Shows two-level hierarchy with merge semantics.

### S3: Cursor Ignore Files
**URL:** https://docs.cursor.com/context/ignore-files
**Type:** Primary (official docs)
**Evidence Level:** Very High
**Key Finding:** Hierarchical ignore files, parent directories searched. Rules in `.cursor/rules/*.mdc` for team sharing.
**Relevance:** Shows project-level team configuration pattern.

### S4: Cursor Gitignore Template PR
**URL:** https://github.com/github/gitignore/pull/4639
**Type:** Secondary (community PR)
**Evidence Level:** High
**Key Finding:** Recommends `.cursorignore` and `.cursorindexingignore` in Global/Cursor.gitignore. These contain "user/team-specific paths."
**Relevance:** Shows what Cursor considers personal vs shared.

### S5: Claude Code Settings
**URL:** https://code.claude.com/docs/en/settings
**Type:** Primary (official docs)
**Evidence Level:** Very High
**Key Finding:** `.claude/settings.local.json` (gitignored automatically), `.claude/settings.json` (committed for team), `~/.claude/settings.json` (global defaults).
**Relevance:** Closest model to RaiSE architecture. Three-level hierarchy with explicit local gitignoring.

### S6: GitHub Copilot Instructions
**URL:** https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
**Type:** Primary (official docs)
**Evidence Level:** Very High
**Key Finding:** `.github/copilot-instructions.md` for repo-wide instructions. Personal settings are cloud-based (GitHub account).
**Relevance:** Shows cloud-personal + repo-shared pattern.

### S7: XDG Base Directory Specification
**URL:** https://specifications.freedesktop.org/basedir/latest/
**Type:** Primary (specification)
**Evidence Level:** Very High
**Key Finding:** `$XDG_DATA_HOME` (~/.local/share) for user data, `$XDG_CONFIG_HOME` (~/.config) for config, `$XDG_STATE_HOME` (~/.local/state) for state.
**Relevance:** Industry standard for personal data location on Linux.

### S8: Cody Context Management
**URL:** https://sourcegraph.com/docs/cody/capabilities/ignore-context
**Type:** Primary (official docs)
**Evidence Level:** High
**Key Finding:** "Cody Ignore" experimental feature for excluding files from LLM context. Respects .gitignore by default.
**Relevance:** Shows context-aware ignore pattern, enterprise-focused.

### S9: Aider Options Reference
**URL:** https://aider.chat/docs/config/options.html
**Type:** Primary (official docs)
**Evidence Level:** Very High
**Key Finding:** `--gitignore` option (default: True) adds `.aider*` to .gitignore automatically.
**Relevance:** Automatic gitignore of personal files is the pattern.
