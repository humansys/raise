# Cline: Identity & Onboarding Research

## Summary

Cline is an open-source VS Code extension (formerly Claude Dev) that positions itself as "a highly skilled software engineer" rather than a distinct AI personality. Identity customization happens through a layered rules system (.clinerules) that users configure, not through a fixed persona. First contact is API-configuration-focused with minimal onboarding narrative.

## Unknown 1: Identity Layering

### Findings

**No distinct personality**: Cline's system prompt identifies it generically as "a highly skilled software engineer with extensive knowledge in many programming languages, frameworks, design patterns, and best practices." There is no unique name-based identity, personality traits, or character narrative.

**Three-layer customization architecture**:
1. **System Prompt (Fixed)**: Located at `src/core/prompts/system.ts`. Defines tool capabilities, XML formatting, and basic identity. Not user-editable.
2. **Global Rules**: Stored in `~/Documents/Cline/Rules/` (or `~/Cline/Rules/` on Linux). Apply across all workspaces.
3. **Workspace Rules**: `.clinerules` file or `.clinerules/` directory in project root. Version-controlled, shareable, AI-editable.

**Rules system features (v3.7+)**:
- Markdown-based files (e.g., `01-coding.md`, `02-documentation.md`)
- Toggleable via popover in chat input (v3.13)
- AI can read/write/edit rules ("self-extending")
- Numeric prefixes for ordering

**Custom Instructions deprecation**: The older "Custom Instructions" text box is being deprecated in favor of `.clinerules` file-based system.

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [docs.cline.bot/features/cline-rules](https://docs.cline.bot/features/cline-rules) | Official docs | Primary |
| [cline.ghost.io/clinerules](https://cline.ghost.io/clinerules-version-controlled-shareable-and-ai-editable-instructions/) | Official blog | Primary |
| [GitHub src/core/prompts/system-prompt](https://github.com/cline/cline/tree/main/src/core/prompts/system-prompt) | Source code | Primary |
| [elifuzz/awesome-system-prompts/cline](https://elifuzz.github.io/awesome-system-prompts/cline) | Community extraction | Secondary |

## Unknown 2: Framework Internalization

### Findings

**Tool definitions embedded in system prompt**: The system prompt serves as "both an API specification and instruction manual." Each tool entry includes:
- What the tool does
- When to use it
- How to format invocations (XML-style tags)

**System prompt structure (three sections)**:
1. **Tools**: Capability definitions with usage guidance
2. **System Information**: Workspace context (paths, environment)
3. **User Preferences**: Coding standards, constraints from rules

**MCP self-awareness**: Cline is notable for understanding its own MCP (Model Context Protocol) capabilities. Beyond just *using* MCP tools, Cline can *build, configure, and debug* them autonomously. This is described as "self-extending AI."

**Memory Bank methodology**: Cline uses a community-developed "Memory Bank" pattern for persistent context:
- Markdown files in `memory-bank/` directory (e.g., `projectbrief.md`)
- Hierarchical documentation that builds context
- Commands: "update memory bank", "follow your custom instructions"
- Note: This is a *methodology/pattern*, not a built-in feature

**Key quote**: "Cline's memory resets completely between sessions... it relies ENTIRELY on its Memory Bank to understand the project and continue work effectively."

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [docs.cline.bot/mcp/mcp-overview](https://docs.cline.bot/mcp/mcp-overview) | Official docs | Primary |
| [cline.ghost.io/mcp-servers-explained](https://cline.ghost.io/mcp-servers-explained-what-they-are-how-they-work-and-why-cline-is-revolutionizing-ai-tools/) | Official blog | Primary |
| [docs.cline.bot/prompting/cline-memory-bank](https://docs.cline.bot/prompting/cline-memory-bank) | Official docs | Primary |
| [github.com/nickbaumann98/cline_docs](https://github.com/nickbaumann98/cline_docs/blob/main/prompting/custom%20instructions%20library/cline-memory-bank.md) | Community docs | Secondary |
| [cline.bot/blog/system-prompt](https://cline.bot/blog/system-prompt) | Official blog | Primary |

## Unknown 3: First Contact

### Findings

**Minimal narrative onboarding**: First-run experience is functional, not narrative:
1. Welcome screen prompting API configuration
2. Choose model provider (OpenRouter, Anthropic, OpenAI, etc.)
3. "Take a Tour" button linking to VS Code walkthrough
4. Ready to use in Plan Mode

**No "meet Cline" introduction**: Unlike assistants with personality, Cline doesn't introduce itself. It starts in **Plan Mode** (read-only) where it can analyze but not modify code.

**Plan/Act paradigm as first contact**:
- **Plan Mode**: "Your architect" - gathers info, proposes strategies, read-only
- **Act Mode**: User-initiated switch to read/write - executes planned solutions
- User controls transition; Cline cannot auto-switch

**Cold start handling**: No prior context assumed. Cline reads workspace files on demand. Users can bootstrap context via:
- `.clinerules` with project context
- Memory Bank files (if configured)
- `@file`, `@folder`, `@url` context annotations

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [docs.cline.bot/getting-started/installing-cline](https://docs.cline.bot/getting-started/installing-cline) | Official docs | Primary |
| [docs.cline.bot/features/plan-and-act](https://docs.cline.bot/features/plan-and-act) | Official docs | Primary |
| [cline.bot/blog/plan-smarter-code-faster](https://cline.bot/blog/plan-smarter-code-faster-clines-plan-act-is-the-paradigm-for-agentic-coding) | Official blog | Primary |
| [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) | Official listing | Primary |
| [DataCamp tutorial](https://www.datacamp.com/tutorial/cline-ai) | Tutorial | Secondary |

## Key Insights for RaiSE

1. **Rules-as-code pattern validated**: Cline's `.clinerules/` directory mirrors RaiSE's approach. Version-controlled, markdown-based, AI-editable. This pattern has market traction (57k+ stars).

2. **Identity is emergent, not declared**: Cline succeeds without a distinct persona. Identity comes from *what it can do* (tools) and *how it behaves* (rules), not *who it is*.

3. **Memory is methodology, not feature**: Cline's Memory Bank is a community pattern, not built-in. RaiSE's `.rai/memory/` could be more integrated while staying file-based.

4. **Plan/Act as safety paradigm**: Explicit read-only mode before write access. Consider for Rai's first contact - could start in "observe" mode.

5. **Self-extending capability notable**: Cline building its own MCP tools is differentiated. Rai's skills system has similar potential.

6. **No introduction ritual**: Cline skips narrative onboarding entirely. Users want to work, not meet the AI. Counter-argument: RaiSE's governance context may benefit from brief "here's how I work" orientation.

7. **Global + Workspace layering**: Two-level rules (user-wide + project-specific) matches RaiSE's `~/.rai/` + `.raise/` pattern.

## Gaps

- **Exact system prompt text**: Could not fetch full `system.ts` source directly. Community extractions exist but may be outdated.
- **Onboarding UX details**: "Take a Tour" walkthrough content not examined.
- **Personality customization limits**: Unclear if users can make Cline adopt a distinct persona through rules alone.
- **Enterprise onboarding**: Enterprise version may have different first-contact experience.

---

*Research conducted: 2026-02-05*
*Evidence level: HIGH (primary sources from official docs + source code)*
*Researcher: Rai (Claude Opus 4.5)*
