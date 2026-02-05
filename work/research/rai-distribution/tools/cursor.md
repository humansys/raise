# Cursor: Identity & Onboarding Research

## Summary

Cursor is a VS Code fork that provides AI assistance through three modes (Chat, Composer, Agent) but has **no distinct personality or named identity**. Customization happens entirely through a rules system (.cursor/rules/*.mdc files) that injects developer-defined context into prompts. Onboarding focuses on VS Code migration and account setup rather than introducing AI capabilities.

## Unknown 1: Identity Layering

### Findings

**No Built-in Personality:** Cursor's AI is described as "conversational but professional" with no named persona. The assistant refers to users in second person and itself in first person, but has no distinct identity beyond being "Cursor" or "the AI."

**Rules System (Three Tiers):**
1. **User Rules** - Global to Cursor environment, defined in Settings > General > Rules for AI. Always applied across all projects.
2. **Project Rules** - Stored in `.cursor/rules/` as `.mdc` files. Version-controlled, scoped to project.
3. **Legacy .cursorrules** - Deprecated single file in project root. Still supported but migration recommended.

**.mdc File Format:**
```yaml
---
description: Short description of rule purpose
globs: optional/path/pattern/**/*
alwaysApply: true|false
---

# Rule Content (Markdown)

Instructions, examples, guidelines...
```

**What's Configurable:**
- Coding style, naming conventions, structure preferences
- Framework-specific guidelines
- Security and error handling patterns
- File-pattern-based rule activation (glob patterns)
- Reference files as context (@filename.ts)

**What's Fixed:**
- Core AI behavior and safety constraints
- Model selection (though user chooses between available models)
- The fact that rules are injected at prompt start

### Evidence

| Source | Rating | Notes |
|--------|--------|-------|
| [Cursor Docs - Rules](https://docs.cursor.com/context/rules) | Secondary | Official documentation |
| [Cursor Docs - Rules for AI](https://docs.cursor.com/context/rules-for-ai) | Secondary | Official documentation |
| [awesome-cursorrules (GitHub)](https://github.com/PatrickJS/awesome-cursorrules) | Tertiary | Community collection |
| [Forum: MDC structure](https://forum.cursor.com/t/optimal-structure-for-mdc-rules-files/52260) | Tertiary | Community discussion |

## Unknown 2: Framework Internalization

### Findings

**No Explicit Self-Documentation:** Cursor does not appear to inject documentation about its own capabilities into context. The AI learns capabilities through:
1. **Codebase embedding model** - Indexes entire project for context-aware suggestions
2. **Tool discovery** - Agent mode learns to use semantic search, file editors, terminal
3. **Reinforcement learning** - Composer trained in real codebases using actual dev tools

**Feature Surfacing:**
- Features (Tab, Chat, Agent) are presented through UI, not AI self-awareness
- User discovers features through:
  - Welcome documentation
  - Command palette (Cmd+Shift+P)
  - Settings exploration
  - Community guides

**AI Knows Context, Not Self:**
- Cursor analyzes codebase, recent changes, open tabs, project structure
- Makes predictions based on "intent-driven edits"
- No evidence of system prompt containing "here are your capabilities"

### Evidence

| Source | Rating | Notes |
|--------|--------|-------|
| [Cursor Features Page](https://cursor.com/features) | Secondary | Official marketing |
| [Cursor Docs - Tab](https://cursor.com/docs/tab/overview) | Secondary | Official docs |
| [Cursor Docs - Agent](https://docs.cursor.com/agent) | Secondary | Official docs |
| [Codecademy - Cursor 2.0](https://www.codecademy.com/article/cursor-2-0-new-ai-model-explained) | Tertiary | Third-party guide |

## Unknown 3: First Contact

### Findings

**Setup Wizard Steps:**
1. **Welcome Screen** - Sign up/login required (email, Google, or GitHub)
2. **Plan Selection** - 14-day Pro trial (250 fast uses), then Hobby plan (50 slow uses)
3. **Customization Options** - Three coding style presets, pick one
4. **Quick Start Guide** - Brief overview of how tool works
5. **Privacy Consent** - Optional: allow Cursor to learn from your code

**VS Code Migration Focus:**
- Import extensions, themes, keybindings from VS Code
- Keyboard shortcut selection (VS Code, Sublime, etc.)
- Theme selection (colors, syntax highlighting)

**What's Missing:**
- No AI "introduction" or personality reveal
- No guided tour of AI features (Chat vs Composer vs Agent)
- No explanation of rules system during onboarding
- No interactive tutorial with the AI
- Revisit anytime: Cmd+Shift+P > "Cursor: Start Onboarding"

**First AI Contact:**
- User must discover how to open AI pane (Cmd+L)
- No proactive introduction from the AI
- User-initiated interaction only

### Evidence

| Source | Rating | Notes |
|--------|--------|-------|
| [daily.dev - Setup Cursor first time](https://daily.dev/blog/setup-cursor-first-time) | Tertiary | Step-by-step guide |
| [Cursor Docs - Installation](https://docs.cursor.com/get-started/installation) | Secondary | Official docs |
| [apidog.com - Cursor Setup Guide](https://apidog.com/blog/cursor-setup-guide/) | Tertiary | Third-party guide |
| [sidetool.co - Getting Started](https://www.sidetool.co/post/getting-started-with-cursor-installation-and-setup-guide/) | Tertiary | Third-party guide |

## Key Insights for RaiSE

### What Cursor Does Well

1. **Layered Rules Architecture** - Global + Project rules is elegant. The glob-based activation (auto-attach when file matches) is smart.

2. **Version-Controlled Configuration** - `.cursor/rules/*.mdc` being in repo enables team consistency.

3. **Escape Hatch Philosophy** - Rules customize behavior without touching core AI. Separation of concerns.

4. **VS Code Migration Path** - Reduces friction for largest target audience.

### Opportunities for RaiSE Differentiation

1. **Named Identity (Rai)** - Cursor has no persona. Rai has identity, perspective, memory. This is a differentiator.

2. **Self-Aware Onboarding** - Cursor's AI doesn't introduce itself. Rai could have a first-contact experience where *Rai* welcomes the user, explains capabilities, and establishes relationship.

3. **Framework Internalization** - Cursor rules are passive (injected into prompt). Rai could actively reference its own governance, explain *why* it follows certain patterns.

4. **Progressive Disclosure** - Cursor dumps features via UI. Rai could reveal capabilities organically through conversation: "I can help with X, would you like me to show you?"

5. **Memory as Differentiator** - Cursor has no persistent memory of user preferences or project history. Rai's memory infrastructure is unique.

### Anti-Patterns to Avoid

1. **Configuration Sprawl** - Multiple rule formats (.cursorrules deprecated, .mdc current, global settings) creates confusion. Pick one canonical format.

2. **Silent AI** - User must discover AI capabilities through exploration. Proactive but non-intrusive guidance would help.

3. **Account-Gated Experience** - Requiring login before any interaction creates friction. Consider offline-first for initial experience.

## Gaps

1. **Internal System Prompt** - Cursor is closed source; cannot verify what's injected beyond user rules
2. **Exact Onboarding Flow** - No official video/documentation of complete first-run experience
3. **Rules Processing Order** - Unclear how conflicts between global and project rules resolve
4. **Memory Persistence** - No clear documentation on whether any user preferences persist across sessions beyond settings

---

*Research conducted: 2026-02-05*
*Evidence level: Mostly Secondary (official docs) + Tertiary (community guides)*
*Confidence: Medium-High for public features, Low for internal implementation*
