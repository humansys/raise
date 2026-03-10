# Mentat: Identity & Onboarding Research

## Summary

Mentat is a terminal-based AI coding assistant (now also available as VS Code extension) that **has no distinct personality or named identity**. The tool focuses on practical functionality - context-aware code editing across multiple files - rather than persona. First-run experience is minimal: set API key, run from project directory, start chatting. The project has been **pivoted/archived** as of January 2025, with the current "Mentat" being a GitHub bot rather than the original CLI.

## Unknown 1: Identity Layering

### Findings

**No Built-in Personality:** Mentat is described purely as "the AI tool that assists you with any coding task" - functional, not personified. Unlike tools with named personas, Mentat is just "Mentat" or "the AI."

**Configuration System (Limited):**
- **Global config:** `~/.mentat/.mentat_config.json`
- **Project config:** `.mentat_config.json` in project root
- **Runtime commands:** `/config` to change settings mid-session

**Configurable Settings:**
- `model` - LLM selection (GPT-4-1106-preview recommended)
- `temperature` - Response randomness (default 0.2)
- `maximum_context` - Token limit for context window
- `auto_context_tokens` - RAG-retrieved context tokens
- `embedding_model` - Model for embeddings
- `parser` - Edit format: block, replacement, or unified-diff
- `theme` - UI appearance (dark/light)
- `file_exclude_glob_list` - Files to exclude

**What's Fixed:**
- Core AI behavior (no custom system prompts)
- The `no_parser_prompt` setting exists but is intended "only for fine-tuned models"
- No mechanism to inject custom personality or identity

**Key Insight:** Mentat explicitly has a setting to disable system prompts (`no_parser_prompt: true`) but this is for fine-tuned models only. This implies a default system prompt exists but is not user-accessible.

### Evidence

| Source | Rating | Notes |
|--------|--------|-------|
| [archive-old-cli-mentat/configuration.rst](https://github.com/AbanteAI/archive-old-cli-mentat/blob/main/docs/source/user/configuration.rst) | Primary (archived) | Official configuration docs from archived CLI |
| [WebSearch: configuration options](https://github.com/AbanteAI) | Secondary | General feature descriptions |
| [DEV.to deep dive](https://dev.to/ykgoon/deep-dive-into-mentat-coding-assistant-12no) | Tertiary | Third-party analysis |

## Unknown 2: Framework Internalization

### Findings

**Elaborate Internal Prompts (Not User-Accessible):** A developer who intercepted Mentat's LLM requests discovered "elaborate directives" that demonstrate "what prompt-engineering looks like." However, these are:
- Not documented
- Not user-configurable
- Only visible via middleware interception

**Context Management Over Self-Awareness:**
- Uses ChromaDB for vector storage (RAG)
- Auto-context feature selects relevant code snippets
- Up to 8000 tokens auto-retrieved by default
- Focus is on *project* context, not *self* documentation

**Feature Discovery via Commands:**
- `/help` - List all available commands
- Commands include: `/agent`, `/clear`, `/commit`, `/config`, `/exclude`, `/include`, `/load`, `/save`, `/redo`, `/run`, `/screenshot`, `/search`, `/talk`, `/undo`, `/undo-all`, `/viewer`, `/amend`
- No "what can you do?" self-explanation from the AI

**Parser Formats (Framework Knowledge):**
- Block format, replacement format, or unified-diff
- Mentat tested Aider's format as comparison
- This suggests framework awareness but not self-documentation

### Evidence

| Source | Rating | Notes |
|--------|--------|-------|
| [Commands documentation](https://docs.mentat.ai/en/latest/user/commands.html) | Secondary | Official docs |
| [DEV.to analysis - intercepted prompts](https://dev.to/ykgoon/deep-dive-into-mentat-coding-assistant-12no) | Tertiary | Third-party reverse engineering |
| [Getting Started docs](https://docs.mentat.ai/en/latest/user/getting_started.html) | Secondary | Official docs |

## Unknown 3: First Contact

### Findings

**Minimal First-Run Experience:**
1. **Install:** `pip install mentat` (or in virtualenv)
2. **Configure API Key:** Create `.env` with `OPENAI_API_KEY=<key>` in `~/.mentat/` or project directory
3. **Run:** `mentat [files...]` from project directory
4. **Prerequisite:** Project must have `git init` already

**No Welcome Message or Introduction:**
- Terminal opens to a "textual TUI" with light/dark mode
- Chat interface ready for input
- User must know to specify files as context
- No guided tour or capability explanation

**Context Adding is Manual:**
- Files listed as CLI arguments become context
- `/include` and `/exclude` to manage context mid-session
- Auto-context available but off by default

**No Onboarding Documentation:**
- Setup docs focus on installation and API key
- No "getting to know Mentat" experience
- User expected to learn by doing

**Quality Depends on User:**
> "The quality of how you phrase your wishes determines the quality of the work, and you have to be pretty verbose about it."

This quote reveals: Mentat expects user expertise, doesn't guide novices.

### Evidence

| Source | Rating | Notes |
|--------|--------|-------|
| [Getting Started docs](https://docs.mentat.ai/en/latest/user/getting_started.html) | Secondary | Official installation guide |
| [User Guide](https://docs.mentat.ai/en/latest/user/guides.html) | Secondary | Official usage docs |
| [DEV.to deep dive](https://dev.to/ykgoon/deep-dive-into-mentat-coding-assistant-12no) | Tertiary | User experience description |
| [PyPI mentat](https://pypi.org/project/mentat/) | Secondary | Package metadata |

## Key Insights for RaiSE

### What Mentat Does Well

1. **Focused Scope** - Multi-file editing with context awareness. Does one thing, does it well.

2. **Git Integration** - Requires git, which implies version control discipline. Leaves commits to user (unlike Aider which auto-commits).

3. **Lightweight Config** - Simple JSON config, no elaborate schema. Easy to understand.

4. **Command System** - Slash commands for runtime control (`/include`, `/exclude`, `/config`) is intuitive.

5. **RAG-Based Context** - Auto-context via embeddings scales better than manual file selection.

### Opportunities for RaiSE Differentiation

1. **Named Identity (Rai)** - Mentat has no persona. The name "Mentat" (Dune reference) suggests intelligence but the tool doesn't embody it. Rai can have actual perspective.

2. **First-Contact Experience** - Mentat drops you into a bare terminal. Rai could introduce itself: "I'm Rai. I've noticed this is a Python project with pytest. Would you like me to follow your existing test patterns?"

3. **Self-Documentation** - Mentat's elaborate prompts are hidden. Rai could explain its own governance: "I'm following your guardrails.md which says to use Google docstrings."

4. **Progressive Disclosure** - Mentat assumes expertise. Rai could adapt: Shu (guided) for newcomers, Ha (collaborative) for intermediate, Ri (delegated) for experts.

5. **Memory Persistence** - Mentat has no session memory. Rai remembers patterns, preferences, calibration across sessions.

6. **Framework as Feature** - Mentat is a tool. RaiSE is a methodology with tools. Rai can teach the framework while executing tasks.

### Anti-Patterns to Avoid

1. **Bare First-Run** - No welcome, no introduction, no capability disclosure. Intimidating for new users.

2. **Manual Context Management** - Forcing users to list files is friction. Auto-context should be default.

3. **Hidden System Prompts** - If you have elaborate prompts, let users extend them. Transparency builds trust.

4. **Expert Assumption** - "Quality depends on how verbose you are" punishes newcomers. Help users articulate needs.

5. **Project Pivot Without Migration** - Mentat CLI was archived, replaced by GitHub bot. Users of old tool left stranded. If pivoting, provide migration path.

## Gaps

1. **Actual System Prompts** - Cannot access the "elaborate directives" without code inspection or middleware interception. Archived repo may contain prompts in source.

2. **Welcome Message** - No evidence of any startup message beyond the TUI interface. May exist in source code.

3. **VS Code Extension Details** - Extension exists but limited documentation on how it differs from CLI.

4. **Current State Unclear** - CLI archived January 2025. "Mentat" now refers to GitHub bot. Research may be partially obsolete.

5. **Personality in Prompts** - The intercepted prompts reportedly show "elaborate directives" but no details on whether these include any persona elements.

---

*Research conducted: 2026-02-05*
*Evidence level: Mostly Secondary (official docs) + Tertiary (user analyses)*
*Confidence: Medium for archived CLI features, Low for current product state*
*Note: Project pivoted in January 2025. CLI archived. Current "Mentat" is GitHub bot.*
