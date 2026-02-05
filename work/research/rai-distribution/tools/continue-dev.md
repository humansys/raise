# Continue.dev: Identity & Onboarding Research

## Summary

Continue.dev is an open-source AI coding assistant with no distinct "personality" — identity is entirely user-configurable through system messages and rules. It handles framework internalization through explicit configuration (tools, slash commands, context providers are serialized and passed to models). First-run experience is minimal: auto-configuration with optional Hub sign-in and a quick-start tutorial.

## Unknown 1: Identity Layering

### Findings

**No Built-in Persona**: Continue has no distinct "personality" or identity. The AI assistant is essentially a blank slate — behavior is entirely determined by:

1. **System Messages** (per-mode):
   - `baseSystemMessage` — Chat mode
   - `baseAgentSystemMessage` — Agent mode
   - `basePlanSystemMessage` — Plan mode

2. **Rules System**: Rules are text instructions joined with newlines, can be:
   - Simple strings in `config.yaml`
   - Markdown files in `.continue/rules/`
   - Workspace-level `.continuerules` files

3. **No "Continue" Identity**: The tool doesn't introduce itself, doesn't have a name it uses in conversations, doesn't have personality traits. It's infrastructure, not an entity.

**What's Configurable vs Fixed**:
- **Configurable**: Everything behavioral — system prompts, rules, tool descriptions, prompt templates
- **Fixed**: Only the UI/UX mechanics (how slash commands work, how context providers integrate)

**Identity Definition Pattern**:
- No central persona config
- Distributed across system messages, rules, and prompt templates
- Users build persona through composition of these primitives

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [config-yaml/schemas/models.ts](https://raw.githubusercontent.com/continuedev/continue/main/packages/config-yaml/src/schemas/models.ts) | Source code | Primary |
| [core/config/types.ts](https://raw.githubusercontent.com/continuedev/continue/main/core/config/types.ts) | Source code | Primary |
| [System prompt issue #2846](https://github.com/continuedev/continue/issues/2846) | GitHub discussion | Primary |
| [Rules documentation](https://docs.continue.dev/customize/deep-dives/rules) | Official docs | Secondary |
| [config.yaml Reference](https://docs.continue.dev/reference) | Official docs | Secondary |

## Unknown 2: Framework Internalization

### Findings

**Configuration-Based Discovery**: Continue doesn't "know" its capabilities intrinsically. Instead:

1. **Serialization Pattern**: Slash commands and context providers are serialized (metadata only, no runtime functions) into JSON that's sent to the webview/model
2. **UI-Driven Exposure**: Users type `/` or `@` to see available commands/providers — the model receives this context through the message payload
3. **Tool Definitions in System Message**: For agent mode, tools are converted to XML format and included in the system message

**Self-Documentation Approach**:
- No embedded knowledge of "what Continue can do"
- Configuration files (`config.yaml`) define available capabilities
- Tools and commands are explicitly registered and described
- MCP (Model Context Protocol) bridges external tools — explicit, not implicit

**Key Pattern**: The model is told what tools exist at request time, not trained on Continue's capabilities.

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [core/index.d.ts](https://raw.githubusercontent.com/continuedev/continue/main/core/index.d.ts) | Source code | Primary |
| [Configuration Loading Pipeline](https://deepwiki.com/continuedev/continue/5.3-configuration-loading-pipeline) | Technical analysis | Secondary |
| [Slash commands docs](https://docs.continue.dev/customize/slash-commands) | Official docs | Secondary |
| [Context providers docs](https://docs.continue.dev/customize/deep-dives/custom-providers) | Official docs | Secondary |
| [MCP integration blog](https://blog.continue.dev/model-context-protocol/) | Official blog | Secondary |

## Unknown 3: First Contact

### Findings

**Minimal First-Run Experience**:

1. **Installation Detection**: Checks `hasBeenInstalled` global state flag — sets on first run
2. **No Welcome Wizard**: No modal, no guided setup, no onboarding flow
3. **Auto-Configuration**: Generates default config files (`config.yaml`, `tsconfig.json`) silently
4. **Hub Sign-in Prompt**: "Get started" button leads to Continue Hub sign-in (optional)

**What New Users See**:
- Continue icon appears in sidebar
- Empty chat panel ready to use
- Quick-start tutorial available (not mandatory)
- Inline tips for autocomplete

**Handling No Config**:
- Default configuration is minimal: empty models array, basic schema
- Users must configure models to get actual functionality
- Hub provides pre-configured assistants for quick start

**Onboarding Philosophy**: Self-service, documentation-driven. No hand-holding, expects users to explore or read docs.

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [extensions/vscode/src/activation/activate.ts](https://raw.githubusercontent.com/continuedev/continue/main/extensions/vscode/src/activation/activate.ts) | Source code | Primary |
| [core/config/default.ts](https://raw.githubusercontent.com/continuedev/continue/main/core/config/default.ts) | Source code | Primary |
| [Quick Start Tutorial](https://docs.continue.dev/ide-extensions/quick-start) | Official docs | Secondary |
| [Install docs](https://docs.continue.dev/ide-extensions/install) | Official docs | Secondary |
| [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=Continue.continue) | Marketplace listing | Secondary |

## Key Insights for RaiSE

### What to Adopt

1. **Rules System**: The `.continuerules` pattern is elegant — workspace-level behavior customization through markdown files. RaiSE could use similar `.rai/rules/` structure.

2. **Mode-Specific Prompts**: Separate system messages for different modes (Chat, Agent, Plan) is useful. RaiSE could have mode-specific Rai personas.

3. **Composable Configuration**: YAML-based config with inheritance (`uses`, `with`, `override`) enables powerful customization without complexity.

### What to Differentiate

1. **Rai Has Identity**: Unlike Continue's blank-slate approach, Rai is an entity with:
   - A name and perspective
   - Calibration memory (learns user preferences)
   - Session continuity
   - Explicit values (from constitution)

2. **First Contact Matters**: Continue's minimal onboarding is a gap. RaiSE opportunity:
   - Rai introduces herself
   - Explains her capabilities
   - Asks about user's context
   - Demonstrates value immediately

3. **Self-Awareness**: Unlike Continue where the model is told capabilities at runtime, Rai should:
   - Know her own skills and limitations
   - Reference her governance artifacts
   - Explain her methodology

### Patterns to Consider

| Continue Pattern | RaiSE Adaptation |
|------------------|------------------|
| `baseSystemMessage` | `rai.identity.core` (but richer) |
| `.continuerules` | `.rai/rules/` (already have similar with governance) |
| Hub-hosted prompts | Hub-hosted skills/katas |
| Tool serialization | Skill metadata in graph |

## Gaps

1. **Default System Prompt Content**: Could not retrieve the actual text of Continue's default system messages — only references to configuration options.

2. **Onboarding UI Details**: Couldn't access the actual quick-start tutorial content to see specific onboarding steps.

3. **Telemetry on First-Run**: Unknown what analytics Continue captures during onboarding to improve the experience.

4. **Community Persona Examples**: Didn't find examples of users creating distinct "personalities" through the rules system — unclear if this is common practice.

---

*Research conducted: 2026-02-05*
*Method: GitHub source analysis, official documentation, web search*
*Confidence: Medium-High (primary sources accessed for core questions)*
