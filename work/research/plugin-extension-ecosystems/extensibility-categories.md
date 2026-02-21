# Extension Categories Beyond Adapters & Hooks

> Research context: Identify extensibility patterns across AI-assisted dev CLIs and
> infrastructure tools that go beyond the two traditional categories (adapters
> implementing a protocol, lifecycle hooks reacting to events). Goal is to inform
> an open-core CLI extensibility architecture for RaiSE.
>
> Complements: `sources/evidence-catalog.md` (update/separation/conflict patterns)

---

## Taxonomy of Extension Categories

Analysis of 8+ tools reveals **10 distinct extension categories**. Only two of them
(Adapters and Lifecycle Hooks) are the "traditional" patterns. The remaining eight
represent genuinely different extension surfaces.

---

### Category 1: Custom Commands / Skills

**What it is:** User-defined or third-party commands that extend the CLI's verb space.
Not hooks (they don't react to events) and not adapters (they don't implement a
protocol to provide a capability). They ARE new capabilities.

**Examples:**
| Tool | Mechanism | Discovery |
|------|-----------|-----------|
| **Cursor** | `.cursor/commands/*.md` — prompt files become `/commands`. Since 2026 Marketplace: Skills bundled in plugins. | File convention + marketplace install |
| **Claude Code** | `.claude/commands/*.md` + `.claude/skills/*/SKILL.md` with YAML frontmatter. Name field becomes `/slash-command`. | File convention. Skills have `description` for auto-discovery by agent. |
| **Continue.dev** | Custom slash commands via config.yaml (deprecated) -> prompt files (current). | Config file, then convention |
| **Aider** | No custom commands. Feature request open (issue #894). Built-in `/commands` only. | N/A |
| **oclif** (Salesforce CLI framework) | Commands discovered from plugins via three strategies: `pattern` (convention-based directory), `explicit` (declared in config), `single` (one command per plugin). | npm package install + `plugins:install` CLI command |
| **dbt** | Macros act as callable commands (`dbt run-operation my_macro`). Distributed via packages. | `packages.yml` + `dbt deps` installs from dbt Hub or git |

**What's unique:** Cursor's 2026 plugin model packages skills alongside subagents,
MCP servers, hooks, and rules into a single installable unit. This "skill bundle"
pattern is the most sophisticated packaging of custom commands seen.

**Key insight for RaiSE:** Skills are already our primary extension surface. The
differentiation is in *discovery* — Cursor and Claude Code both use file-convention
discovery (drop a file, get a command) plus optional metadata for agent auto-selection.

---

### Category 2: Context Providers

**What it is:** Extensions that supply information to the AI/tool context without
being commands or adapters. They answer "what does the AI know about?" rather than
"what can the AI do?".

**Examples:**
| Tool | Mechanism | Interface |
|------|-----------|-----------|
| **Continue.dev** | `@` dropdown context providers. Built-in: `@file`, `@code`, `@docs`, `@web`. Custom: `HttpContextProvider` (POST to URL, returns ContextItems) or MCP servers. | TypeScript interface: `getContextItems(query, extras)` returns `ContextItem[]` |
| **Aider** | Repo-map (automatic code structure), `/read` files, conventions files (always-loaded context). | File-based. No programmatic provider API. |
| **Cursor** | MCP servers as context sources. Rules files (`.cursor/rules/*.mdc`) provide static context. | MCP protocol + file convention |
| **Claude Code** | `CLAUDE.md` files (layered: global, project, local). MCP servers for dynamic context. | File convention (markdown) + MCP protocol |
| **Roo Code** | Custom instructions per mode. `custom_instructions_dir` pointing to `kb/` directory for mode-specific knowledge base. | File convention (per-mode directories) |

**What's unique:** Continue.dev's `HttpContextProvider` is the simplest dynamic
context extension — just a POST endpoint returning structured items. No SDK needed,
any language can provide context. Roo Code's per-mode knowledge base directories
are interesting for role-specific context.

**Key insight for RaiSE:** We already have `rai memory context` and CLAUDE.md, but
there's no pluggable "context provider" interface. A provider that can answer
"give me context for module X" from any source (Confluence, Notion, local docs)
would be a valuable extension point distinct from both adapters and commands.

---

### Category 3: Persona / Mode Definitions

**What it is:** Extensions that define *who* the AI acts as, including role
definition, tool permissions, and file access restrictions. Fundamentally different
from commands (what to do) or context (what to know) — this is about *how to behave*.

**Examples:**
| Tool | Mechanism | Schema |
|------|-----------|--------|
| **Roo Code** | Custom Modes with full schema: `slug`, `roleDefinition`, `groups` (tool permissions: read/edit/browser/command/mcp), `customInstructions`, file restrictions (`read_allow`, `write_allow` glob patterns). | YAML or JSON. Global (`custom_modes.yaml`) or project (`.roomodes`). |
| **Cursor** | Agent rules (`.cursor/rules/*.mdc`, `AGENTS.md`). Team rules via dashboard. | Markdown with frontmatter. Rules apply globally, not per-persona. |
| **Claude Code** | CLAUDE.md layers provide behavioral instructions but no tool permission scoping. | Markdown. No schema for permissions. |

**What's unique:** Roo Code is the only tool that provides *tool-level permission
scoping per persona*. A "Security Auditor" mode can be restricted to read-only file
access + no command execution. This is a genuinely novel extension category.

**Key insight for RaiSE:** Our agent support (Claude, Windsurf, Cursor, Roo, etc.)
distributes rules files, but we don't have a "mode" concept with permission
boundaries. For enterprise contexts (least-privilege AI agents), this could be
significant.

---

### Category 4: Custom Validators / Linters

**What it is:** Extensions that validate inputs, configurations, or outputs against
custom rules. Not lifecycle hooks (they don't react to workflow events) — they're
declarative rules applied to data.

**Examples:**
| Tool | Mechanism | Interface |
|------|-----------|-----------|
| **Terraform** | Plugin Framework validators: pre-built (`stringvalidator.LengthBetween`, `int64validator.AtLeast`) + custom validators implementing `Validate(ctx, req, resp)` interface. Also schema-level validation via `PlanModifiers`. | Go interfaces |
| **dbt** | Custom generic tests: SQL templates in `tests/generic/` or `macros/`. Reusable across models. Example: `test_is_positive(model, column)`. Packages like `dbt-expectations` provide 50+ custom tests. | Jinja SQL macros |
| **Aider** | `--lint-cmd` per language (e.g., `python: flake8 --select=...`). Auto-runs after changes. | External process (any linter). |
| **pre-commit** | Each hook is a validator: `.pre-commit-hooks.yaml` declares `id`, `name`, `entry`, `language`, `types`. Framework handles installation, environment setup, and execution. | Any language. Convention-based discovery via git repo + YAML manifest. |
| **Cursor** | Hooks (beta): custom scripts at specific execution points. Can validate and reject agent actions. | Shell scripts triggered at lifecycle points. |

**What's unique:** dbt's approach of making validators (tests) first-class
distributable units via packages is powerful. Any team can publish a package of
domain-specific data quality tests that others can use declaratively in YAML.
pre-commit's language-agnostic model (any executable + YAML manifest) is the
simplest possible validator distribution mechanism.

**Key insight for RaiSE:** We don't have custom validation beyond what's in skill
gates. A "custom gate" extension — define validation rules that must pass at
specific workflow points — would fit naturally with our existing gate architecture.

---

### Category 5: Custom Output Formatters / Renderers

**What it is:** Extensions that control how results are displayed or exported.
Distinct from adapters (they don't provide data) and from hooks (they don't react
to events). They transform output representation.

**Examples:**
| Tool | Mechanism |
|------|-----------|
| **dbt** | Macro-based: custom materializations control how SQL is rendered and executed. `materialization` blocks define the SQL wrapper, pre/post hooks, and output handling. |
| **Terraform** | Provider-defined functions (Terraform 1.8): providers can expose custom functions usable in any HCL expression. E.g., `provider::aws::arn_parse("arn:...")`. |
| **VS Code** | Custom editors, webview panels, tree views, notebook renderers. Contribution points in `package.json`. |
| **Claude Code** | Output styles (configurable response formatting). |

**What's unique:** dbt's custom materializations are the most powerful example — they
don't just format output, they define entirely new strategies for how models are
built (e.g., incremental, snapshot, custom CDC patterns). This goes beyond
formatting into "output strategy."

**Key insight for RaiSE:** Our retrospective and reporting could benefit from
pluggable formatters — Jira comment format, Confluence page format, Slack summary
format, etc. Currently hardcoded.

---

### Category 6: Provider-Defined Functions

**What it is:** Extensions that add new *functions* (not commands) callable within
the tool's expression/configuration language. Different from commands (invoked by
users) — these are invoked by the tool's own configuration processing.

**Examples:**
| Tool | Mechanism |
|------|-----------|
| **Terraform** | Provider-defined functions (v1.8+): providers declare functions usable in HCL expressions. `function` block in provider schema. Called as `provider::name::function()`. |
| **dbt** | UDFs (v1.11+): Python files in `functions/` directory define user-defined functions executable in SQL context (warehouse-dependent). |
| **Terraform** | Custom types: extend base types with semantic equality and validation logic. E.g., a `CIDRType` that validates CIDR notation. |

**What's unique:** Terraform's provider-defined functions blur the line between
"extension" and "language feature." They extend the *configuration language itself*,
not just the tool's capabilities. This is a meta-extensibility pattern.

**Key insight for RaiSE:** Could RaiSE skills define "functions" usable in other
skills' configurations? E.g., a `jira::current_sprint()` function usable in
any skill's context section. Probably over-engineering for now, but worth noting.

---

### Category 7: Template / Scaffold Extensibility

**What it is:** Extensions that define project scaffolding, boilerplate generation,
or code template patterns. Different from commands (these produce files from
templates) and different from formatters (these create new content, not transform
existing content).

**Examples:**
| Tool | Mechanism |
|------|-----------|
| **dbt** | Packages include models, seeds, and docs that serve as scaffolding for analytics patterns. `dbt init` generates project scaffold. |
| **Cursor** | Skills can include code templates and scaffold instructions. |
| **Claude Code** | Skills with scaffold-oriented instructions. `SKILL.md` can include template patterns. |
| **pre-commit** | `.pre-commit-config.yaml` itself is a scaffold — `pre-commit sample-config` generates starter config. |

**What's unique:** dbt packages that include models (not just macros) are essentially
"scaffold packages" — install `dbt-date` and you get a pre-built date dimension
table. This is "executable scaffolding" that produces production artifacts, not
just starting points.

**Key insight for RaiSE:** `rai init --detect` already scaffolds from conventions.
The extension point would be custom scaffold templates per technology stack.
Currently hardcoded. A `scaffold-provider` extension type could let community
members contribute stack-specific initialization.

---

### Category 8: Model / LLM Provider Switching

**What it is:** Extensions that allow swapping the underlying AI model or LLM
provider. Specific to AI-assisted tools. Not quite an "adapter" in the traditional
sense — it's more about hot-swapping the reasoning engine.

**Examples:**
| Tool | Mechanism |
|------|-----------|
| **Aider** | `--model` flag + `.aider.model.settings.yml` for custom model configs. `extra_params` passed to `litellm.completion()`. Supports any LiteLLM-compatible provider. |
| **Continue.dev** | `models` array in config. Multiple models for different tasks (chat, autocomplete, embedding). Custom model providers via TypeScript class implementing model interface. |
| **Cursor** | Built-in model switching. MCP-based model providers. |
| **Roo Code** | Multi-model support. Different models assignable per custom mode. |
| **Claude Code** | Claude models only (by design). MCP for tool extension, not model switching. |

**What's unique:** Aider's LiteLLM integration is the most open — any model that
LiteLLM supports works with zero custom code. Continue.dev's per-task model
assignment (one model for chat, another for autocomplete, another for embeddings)
is the most granular.

**Key insight for RaiSE:** RaiSE is model-agnostic at the skill layer (skills are
markdown, any agent can execute them). The "model provider" question is delegated
to the agent tool (Claude Code, Cursor, etc.). This is the right level of
abstraction for us.

---

### Category 9: Subagents / Parallel Execution Units

**What it is:** Extensions that define specialized agents that can be spawned by
the primary agent to handle subtasks. Distinct from commands (which the user
invokes) — subagents are invoked *by the AI* to decompose work.

**Examples:**
| Tool | Mechanism |
|------|-----------|
| **Cursor** | Subagents in plugin bundles. Can run async (since 2026). Can spawn their own subagents (tree of work). |
| **Claude Code** | Task tool spawns subagents. Skills can suggest subagent decomposition. |
| **Roo Code** | Custom modes effectively act as switchable subagents — the "orchestrator" mode delegates to specialized modes. |

**What's unique:** Cursor's 2026 async subagent model with nested spawning
(subagents spawning subagents) is the most advanced. The plugin marketplace
bundles subagents alongside the skills and tools they need, creating self-contained
capability packages.

**Key insight for RaiSE:** Our skill system already supports multi-agent
distribution. The gap is a formal "subagent definition" that packages a persona +
tools + instructions as a spawnable unit. Currently this is implicit in skill
design.

---

### Category 10: Configuration Providers / Settings Cascades

**What it is:** Extensions that define how configuration is discovered, layered,
and resolved. Not about *what* is configured, but about the configuration *system
itself* being extensible.

**Examples:**
| Tool | Mechanism |
|------|-----------|
| **VS Code** | 5-level cascade: Default < Extension defaults < User < Workspace < Language-specific. Extensions declare `configurationDefaults` to set defaults for ANY setting. |
| **Aider** | 3 sources: CLI args > `.aider.conf.yml` > `.env` variables. No extensibility of the cascade itself. |
| **Cursor** | 4-level rules: Agent rules < Team rules < Project rules < User rules. |
| **Claude Code** | 3-level CLAUDE.md: `~/.claude/CLAUDE.md` < `project/CLAUDE.md` < `project/CLAUDE.local.md`. |
| **Helm** | Values cascade: Chart defaults < Parent chart < User values files (multiple, ordered) < `--set` flags. |

**What's unique:** VS Code's contribution point `configurationDefaults` lets
extensions inject defaults into *other* configuration namespaces. Extension A can
set default values for settings that Extension B defined. This is meta-configuration.

**Key insight for RaiSE:** Our `.raise/` configuration is currently flat. A
cascade (built-in defaults < organization config < project config < user overrides)
is already loosely implemented but could be formalized as an extension point where
third-party packages contribute default configurations.

---

## Cross-Category Analysis

### The Full Taxonomy

| # | Category | Traditional? | Example Tools |
|---|----------|-------------|---------------|
| 1 | Adapters (protocol implementations) | Yes | Terraform providers, dbt adapters |
| 2 | Lifecycle Hooks (event reactions) | Yes | pre-commit, Cursor hooks |
| 3 | Custom Commands / Skills | **No** | Cursor, Claude Code, oclif, dbt macros |
| 4 | Context Providers | **No** | Continue.dev, Claude Code MCP |
| 5 | Persona / Mode Definitions | **No** | Roo Code custom modes |
| 6 | Custom Validators / Gates | **No** | Terraform validators, dbt tests, pre-commit |
| 7 | Output Formatters / Renderers | **No** | dbt materializations, VS Code renderers |
| 8 | Provider-Defined Functions | **No** | Terraform 1.8 functions, dbt UDFs |
| 9 | Template / Scaffold Providers | **No** | dbt packages, rai init detect |
| 10 | Model / LLM Provider Switching | **No** | Aider LiteLLM, Continue.dev models |
| 11 | Subagent Definitions | **No** | Cursor plugins, Claude Code Task |
| 12 | Configuration Cascades | **No** | VS Code, Helm, Cursor rules |

### Discovery / Registration Patterns

| Pattern | How it works | Used by |
|---------|-------------|---------|
| **File convention** | Drop a file in a known directory, it's discovered. | Cursor commands, Claude Code skills, Roo Code modes, pre-commit |
| **Manifest declaration** | Declare extensions in a config file (YAML/JSON). | dbt packages.yml, pre-commit config, Continue.dev config.yaml |
| **Package manager** | Install via npm/pip/registry. | oclif plugins, dbt packages, Terraform providers, VS Code extensions |
| **Marketplace** | Browse/install from curated catalog. | Cursor Marketplace (2026), VS Code Marketplace, Cline MCP Marketplace |
| **Protocol auto-discovery** | Tool finds extensions implementing a known protocol. | MCP servers (stdio/SSE), Terraform provider registry |

### Packaging Patterns

| Pattern | What's bundled | Used by |
|---------|---------------|---------|
| **Single-concern package** | One extension type per package. | Terraform providers, pre-commit hooks, VS Code extensions |
| **Capability bundle** | Multiple extension types in one package. | Cursor plugins (skills + subagents + MCP + hooks + rules), dbt packages (models + macros + tests + docs) |
| **Prompt-as-package** | Markdown/text files that define behavior. | Claude Code skills, Cursor commands, Roo Code modes |

---

## Implications for RaiSE Open-Core Architecture

### Currently Implemented (Map to Taxonomy)

| RaiSE Feature | Category | Status |
|---------------|----------|--------|
| Skills (`.raise/skills/`) | Custom Commands (#3) | Implemented |
| Agent rules distribution | Persona/Mode (#5) | Implemented (multi-agent) |
| Discovery scanner | Template/Scaffold (#9) | Implemented |
| CLAUDE.md / agent config | Configuration Cascade (#12) | Implemented |
| Lifecycle (epic/story/session) | Lifecycle Hooks (#2) | Implemented |

### Potential Extension Points (Not Yet Implemented)

| Extension Point | Category | Priority | Rationale |
|----------------|----------|----------|-----------|
| **Custom gates** | Validators (#6) | High | Natural fit with existing gate architecture. Let teams define "must pass X before commit/merge." |
| **Context providers** | Context Providers (#4) | High | Pluggable sources for `rai memory context` — Confluence, Notion, custom wikis. |
| **Output formatters** | Formatters (#7) | Medium | Retrospective -> Jira comment, Confluence page, Slack message. Currently hardcoded. |
| **Scaffold templates** | Scaffold Providers (#9) | Medium | Per-stack `rai init` templates. Community-contributed. |
| **Capability bundles** | Packaging | Medium | Package skills + rules + gates as a single installable unit (like Cursor plugins). |
| **Configuration providers** | Config Cascade (#12) | Low | Organization-level config packages. |
| **Provider functions** | Functions (#8) | Low | Over-engineering for current stage. |

### Recommended Architecture Principles

1. **File-convention discovery first.** Drop a file, it works. No registration
   ceremony. (Pattern shared by Cursor, Claude Code, Roo Code, pre-commit.)

2. **Manifest for packages.** When distributing bundles, use a manifest file
   (like dbt's `packages.yml` or pre-commit's config). Keep it declarative.

3. **Capability bundles over single-concern packages.** The Cursor 2026 plugin
   model proves that packaging skills + rules + tools together reduces friction.
   RaiSE skill packs should be able to include gates, formatters, and agent rules.

4. **Separate extension from packaging.** Any extension should work as a local
   file (file convention) OR as part of an installed package. Don't couple the
   extension mechanism to the distribution mechanism.

5. **Permission boundaries per persona.** Roo Code's tool-permission scoping
   per mode is enterprise-relevant. Consider for RaiSE agent configurations.

---

## Sources

### Aider
- [In-chat commands](https://aider.chat/docs/usage/commands.html)
- [Configuration](https://aider.chat/docs/config.html)
- [Advanced model settings](https://aider.chat/docs/config/adv-model-settings.html)
- [Conventions](https://aider.chat/docs/usage/conventions.html)
- [Custom commands feature request #894](https://github.com/Aider-AI/aider/issues/894)

### Continue.dev
- [Customization Overview](https://docs.continue.dev/customize/overview)
- [Custom Context Providers](https://docs.continue.dev/customize/deep-dives/custom-providers)
- [Slash Commands](https://docs.continue.dev/customize/slash-commands)
- [MCP Integration](https://docs.continue.dev/customize/deep-dives/mcp)

### Cursor
- [Cursor Marketplace Plugins announcement](https://www.adwaitx.com/cursor-marketplace-plugins/)
- [Cursor Marketplace first impressions](https://engincanveske.substack.com/p/i-tried-cursors-new-plugin-marketplace)
- [Cursor plugin specification (GitHub)](https://github.com/cursor/plugins)
- [Cursor plugin template (GitHub)](https://github.com/cursor/plugin-template)
- [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)
- [Cursor CLI updates Jan 2026](https://www.theagencyjournal.com/cursors-cli-just-got-a-whole-lot-smarter-fresh-updates-from-last-week/)

### Cline / Roo Code
- [Roo Code Custom Modes docs](https://docs.roocode.com/features/custom-modes)
- [Roo Code Using Modes](https://docs.roocode.com/basic-usage/using-modes)
- [Roo Code Custom Instructions](https://docs.roocode.com/features/custom-instructions)
- [Roo Code vs Cline comparison](https://www.qodo.ai/blog/roo-code-vs-cline/)

### Claude Code
- [Skills documentation](https://code.claude.com/docs/en/skills)
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [Claude Code customization guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/)

### dbt
- [Packages & Plugins extensibility patterns (2025)](https://medium.com/tech-with-abhishek/dbt-packages-plugins-extensibility-patterns-building-publishing-and-best-practices-2025-78b81d9ff4b2)
- [Custom materializations](https://docs.getdbt.com/guides/create-new-materializations)
- [Custom generic tests](https://docs.getdbt.com/best-practices/writing-custom-generic-tests)
- [dbt Core v1.11 (UDFs)](https://www.getdbt.com/blog/dbt-core-v1-11-is-ga)

### pre-commit
- [pre-commit.com](https://pre-commit.com/)
- [pre-commit hooks repo](https://github.com/pre-commit/pre-commit-hooks)

### Terraform
- [Plugin Framework](https://developer.hashicorp.com/terraform/plugin/framework)
- [How Terraform works with plugins](https://developer.hashicorp.com/terraform/plugin/how-terraform-works)
- [Custom types](https://developer.hashicorp.com/terraform/plugin/framework/handling-data/types/custom)
- [Provider-defined functions (v1.8)](https://www.hashicorp.com/en/blog/terraform-1-8-improves-extensibility-with-provider-defined-functions)
- [Validators](https://github.com/hashicorp/terraform-plugin-framework-validators)

### VS Code
- [Contribution Points API](https://code.visualstudio.com/api/references/contribution-points)
- [Extension API overview](https://code.visualstudio.com/api)
- [Building extensions in 2026](https://abdulkadersafi.com/blog/building-vs-code-extensions-in-2026-the-complete-modern-guide)

### oclif
- [oclif Configuration and Plugins](https://deepwiki.com/oclif/core/3-configuration-and-plugins)
- [oclif GitHub](https://github.com/oclif/oclif)
- [Developing CLI Plugins (Heroku)](https://devcenter.heroku.com/articles/developing-cli-plugins)
