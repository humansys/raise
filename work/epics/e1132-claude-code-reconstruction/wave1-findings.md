# E1132 Wave 1: Extension Points — Deep Dive Findings

**Phase:** 2 (Targeted Deep Dives) per ADR-016
**Wave:** 1 — Extension Points (skills, hooks, tools, commands)
**Source:** `~/Code/claude-code-main/src/`
**Date:** 2026-04-01

---

## Executive Summary

Claude Code's extension model is **simpler than expected**:

1. **Skills = Commands.** There is no separate skill registry. Every `SKILL.md` becomes a `Command` object with `type: 'prompt'`. Two invocation paths: user types `/name` (slash command dispatch) or model calls `Skill` tool.

2. **MCP is THE tool extension mechanism.** No plugin API exists for injecting `Tool` objects. Custom tools must be MCP servers. Tools named `mcp__<server>__<tool>`.

3. **Hooks are the control plane.** 27 events, 6 command types (shell, prompt, agent, http, callback, function). PreToolUse hooks can override permission decisions. Settings.json is the registration surface for external hooks.

4. **DEPRECATED wave is active.** 262 DEPRECATED signals across the codebase. Primarily bash command parsing (`splitCommand_DEPRECATED` → AST-based `parseForSecurity`) and settings accessors. Target new APIs.

---

## Finding F1: Skills Lifecycle

**Question:** How does Claude Code load, validate, and execute skills?

**Files:** `skills/loadSkillsDir.ts`, `skills/bundledSkills.ts`, `skills/bundled/index.ts`, `tools/SkillTool/SkillTool.ts`, `tools/SkillTool/prompt.ts`, `types/command.ts`, `commands.ts`

**Finding:**

### Loading (3 sources, parallel at startup)

| Source | Mechanism | Example |
|--------|-----------|---------|
| **Bundled** | `registerBundledSkill()` → in-memory array | `/compact`, `/simplify` |
| **Disk** | 4 tiers: managed, user, project, additional | `.claude/skills/<name>/SKILL.md` |
| **MCP** | Filtered from MCP server tool listings | MCP servers exposing skills |

Deduplication by resolved file path (handles symlinks). Skills with `paths` frontmatter are "conditional" — hidden until model touches matching files.

### Validation (frontmatter contract)

YAML frontmatter in `SKILL.md` is the entire contract. Key fields:

| Field | Purpose | RaiSE Relevance |
|-------|---------|-----------------|
| `description` | Human-readable description | Also used as fallback for model |
| `when_to_use` | Model discovery text (max ~250 chars in listing) | **Optimize for model matching** |
| `allowed-tools` | Tools this skill can use | Without it → auto-approved |
| `context` | `inline` (default) or `fork` (sub-agent) | Fork = own token budget |
| `agent` | Agent type when forked | Controls sub-agent behavior |
| `hooks` | Lifecycle hooks (Zod-validated) | Skills can register hooks |
| `paths` | Glob patterns for conditional activation | Project-specific visibility |
| `arguments` | Named argument definitions | Parameterized skills |
| `model` | Model override or `"inherit"` | Per-skill model selection |
| `disable-model-invocation` | Boolean | User-only skills |

**Unrecognized fields are silently ignored** — our custom frontmatter (governance metadata) is safe.

### Execution

Two paths, both call `getPromptForCommand()`:

1. **User types `/skill-name args`** → `processSlashCommand()` → prompt injection
2. **Model calls `Skill` tool** → `SkillTool.call()` → prompt injection (inline) or sub-agent (fork)

Variable substitution: `$1`/named args, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_SESSION_ID}`. Shell commands in markdown (`` !`command` ``) execute before expansion.

### RaiSE Impact

| Insight | Action |
|---------|--------|
| `when_to_use` is what model sees | Optimize our skill descriptions for model matching |
| `context: fork` isolates token budget | Consider for heavy skills like `/rai-story-implement` |
| `allowed-tools` controls permission escalation | Declare tools for transparency |
| `paths` enables conditional visibility | Language-specific skills only when relevant |
| Custom frontmatter is safe | Our governance metadata won't break CC |
| Shell commands in prompts | Can use `` !`rai session context` `` for dynamic context |

**Confidence:** Alta

---

## Finding F2: Hooks & Permission Model

**Question:** How are permissions resolved? What info does the hook have at execution time?

**Files:** `entrypoints/sdk/coreTypes.ts`, `schemas/hooks.ts`, `utils/hooks.ts` (5000+ lines), `utils/hooks/hooksSettings.ts`, `utils/hooks/hooksConfigSnapshot.ts`, `utils/hooks/sessionHooks.ts`, `utils/hooks/execAgentHook.ts`, `utils/hooks/execHttpHook.ts`, `utils/permissions/permissions.ts`, `types/permissions.ts`, `types/hooks.ts`, `hooks/useCanUseTool.tsx`

**Finding:**

### 27 Hook Events

| Category | Events |
|----------|--------|
| **Tool lifecycle** | PreToolUse, PostToolUse, PostToolUseFailure |
| **Permission** | PermissionRequest, PermissionDenied |
| **Session** | SessionStart, SessionEnd, Setup, Stop, StopFailure |
| **Subagent** | SubagentStart, SubagentStop |
| **Compaction** | PreCompact, PostCompact |
| **User input** | UserPromptSubmit |
| **Config** | ConfigChange, InstructionsLoaded |
| **Workspace** | WorktreeCreate, WorktreeRemove, CwdChanged, FileChanged |
| **Tasks** | TaskCreated, TaskCompleted, TeammateIdle |
| **MCP** | Elicitation, ElicitationResult |
| **Notify** | Notification |

### 6 Hook Command Types

| Type | Mechanism | Use Case |
|------|-----------|----------|
| `command` | Shell command (stdin = JSON) | External tools, gates |
| `prompt` | LLM prompt with `$ARGUMENTS` | AI-powered validation |
| `agent` | Multi-turn subagent with tools | Complex verification |
| `http` | HTTP POST (SSRF-protected) | Server-side enforcement |
| `callback` | Internal TypeScript function | Analytics, attribution |
| `function` | In-memory boolean function | Structured output enforcement |

### Permission Resolution Chain (strict order)

```
1. Deny rules          → blocked immediately
2. Ask rules           → forces user prompt
3. Tool.checkPerms()   → tool-specific logic (e.g., Bash subcommand rules)
4. Tool deny           → blocked
5. Content-specific    → bypass-immune ask rules
6. Safety checks       → .git/, .claude/, shell configs (ALWAYS ask)
7. Bypass mode         → if enabled, allow
8. Always-allow rules  → explicit settings allow
9. Default             → ask user
```

Post-resolution transforms: `dontAsk` mode converts ask→deny, `auto` mode runs AI classifier.

Permission rules from 8 sources: `userSettings`, `projectSettings`, `localSettings`, `flagSettings`, `policySettings`, `cliArg`, `command`, `session`.

### Hook Dispatch

- All matching hooks run **in parallel** with individual timeouts
- Hook input: JSON on stdin with `session_id`, `transcript_path`, `cwd`, `permission_mode`, `agent_id`, `agent_type` + event-specific fields
- Exit code protocol: 0=success, 2=blocking error (stderr shown to model), other=non-blocking
- **PreToolUse hooks can override permissions** via `hookSpecificOutput.permissionDecision`: `allow`/`deny`/`ask`

### Hook Registration (5 channels)

| Channel | Persistence | Enterprise Control |
|---------|:-----------:|:------------------:|
| Settings files (user/project/local) | Persistent | Can be blocked by `allowManagedHooksOnly` |
| Policy/managed settings | Persistent | Cannot be overridden |
| Plugin hooks | Persistent | Can be restricted |
| Session hooks (`addSessionHook`) | In-memory | No |
| Registered hooks (callbacks) | In-memory | No |

### RaiSE Impact

| Insight | Action |
|---------|--------|
| PreToolUse + `if` conditions = gate enforcement | `if: "Bash(git commit*)"` → `rai gate check` |
| Settings.json is the registration surface | Our hooks must be settings entries, not code |
| PostCompact fires with `trigger` field | Confirms our compaction hook approach is correct |
| HTTP hooks enable server-side governance | Could enforce gates via RaiSE server without local process |
| `allowManagedHooksOnly` is the enterprise kill switch | Enterprise deployments can lock down to managed hooks only |
| 27 events cover full lifecycle | We have control points for every phase |

**Confidence:** Alta

---

## Finding F3: Tool System

**Question:** How is a tool registered and dispatched? Is it extensible?

**Files:** `Tool.ts` (30K), `tools.ts` (17K), `services/tools/toolExecution.ts`, `tools/MCPTool/MCPTool.ts`, `services/mcp/client.ts`, `tools/ToolSearchTool/prompt.ts`, `hooks/useMergedTools.ts`

**Finding:**

### Tool Protocol

`Tool<Input, Output, P>` is a comprehensive interface with ~40 members. Key required methods:

| Method | Purpose |
|--------|---------|
| `name` | Unique tool identifier |
| `inputSchema` | Zod schema for validation |
| `call()` | Execution (async generator for streaming) |
| `description()` | Human-readable description |
| `prompt()` | System prompt section for the model |
| `checkPermissions()` | Tool-specific permission logic |
| `isReadOnly()` | Read-only classification |
| `isConcurrencySafe()` | Parallel execution safety |
| `isEnabled()` | Dynamic enable/disable |

`buildTool()` factory fills safe defaults for 7 commonly-stubbed methods.

### Tool Registry — Hardcoded, No Plugin API

`getAllBaseTools()` is a **hardcoded function** returning an array of all ~40+ built-in tools. No dynamic registry. No plugin hook for injecting Tool objects. Tools conditionally included via feature flags.

### Tool Execution Flow

```
Model returns tool_use block
  → runToolUse()
    → Zod validation (inputSchema.safeParse)
    → tool.validateInput()
    → runPreToolUseHooks()
    → canUseTool() → tool.checkPermissions() + permission chain
    → tool.call(args, context)
    → runPostToolUseHooks()
    → ToolResult<T> with optional newMessages, contextModifier
```

### Two Extension Points

| Mechanism | How | Naming |
|-----------|-----|--------|
| **MCP tools** | MCP server → `tools/list` → cloned MCPTool per tool | `mcp__<server>__<tool>` |
| **Agent definitions** | Directory-based agent definitions | Via AgentTool dispatch |

MCP tools are **deferred by default** behind ToolSearchTool. Model must call ToolSearch to fetch schemas first. Exception: tools with `_meta['anthropic/alwaysLoad']`.

### Deprecation Pattern

The 52 DEPRECATED signals in tools/ are NOT removed tools. They're function renames during incremental migration:
- `splitCommand_DEPRECATED` → AST-based `parseForSecurity`
- `bashCommandIsSafeAsync_DEPRECATED` → new safety checker
- `getSettings_DEPRECATED` → new settings accessor

Pattern: suffix `_DEPRECATED`, migrate callers incrementally.

### RaiSE Impact

| Insight | Action |
|---------|--------|
| **MCP is THE extension mechanism** | Our tools must be MCP servers (`rai mcp install/scaffold`) |
| No internal plugin API | Cannot inject Tool objects from outside CC |
| MCP tools deferred by default | Our tools invisible on turn 1 unless `alwaysLoad` |
| Permission: MCP tools default to `passthrough` (always prompt) | Configure `alwaysAllowRules` for trusted RaiSE tools |
| Tool naming: `mcp__<server>__<tool>` | Permission rules can target `mcp__<server>` for blanket allow |
| `buildTool()` factory pattern | Worth adopting if we create programmatic tools |

**Confidence:** Alta

---

## Finding F4: Command System (Slash Commands)

**Question:** How are slash commands registered and dispatched?

**Files:** `types/command.ts`, `commands.ts` (25K), `utils/slashCommandParsing.ts`, `utils/processUserInput/processSlashCommand.tsx`, `skills/loadSkillsDir.ts`, `tools/SkillTool/SkillTool.ts`

**Finding:**

### Command Protocol (Discriminated Union)

```typescript
type Command = CommandBase & (PromptCommand | LocalCommand | LocalJSXCommand)
```

| Type | Mechanism | Who Can Create |
|------|-----------|---------------|
| `prompt` | Markdown → conversation injection | Anyone (SKILL.md) |
| `local` | TypeScript → `LocalCommandResult` | CC developers only |
| `local-jsx` | TypeScript → React JSX (modals) | CC developers only |

**Skills can ONLY create `prompt` commands.** `local` and `local-jsx` require compiled TypeScript.

### Command Aggregation (8 sources, priority order)

1. Bundled skills
2. Built-in plugin skills
3. Skill directory commands (managed → user → project)
4. Workflow commands (feature-flagged)
5. Plugin commands
6. Plugin skills
7. Built-in commands (~70: `/help`, `/compact`, `/config`, etc.)
8. Dynamic skills (discovered via file path matching)

Memoized per `cwd`. Deduplicated. Filtered by availability and enablement.

### Dispatch

User types `/something`:

```
parseSlashCommand(input) → { commandName, args, isMcp }
  → hasCommand(name, commands)?
    → Yes: getMessagesForSlashCommand()
      → prompt: getPromptForCommand(args, context) → inject content
      → local: load() → call(args, context) → LocalCommandResult
      → local-jsx: load() → call(onDone, context, args) → render JSX
    → No (looks like command): "Unknown skill" error
    → No (doesn't look like command): pass through as user message
```

### RaiSE Impact

| Insight | Action |
|---------|--------|
| Skills ARE commands (no separate registry) | Our SKILL.md files are first-class commands |
| Only `prompt` type available to external skills | We cannot create interactive (JSX) commands |
| 8 aggregation sources with priority | Managed > user > project — enterprise can override |
| Memoized per cwd | Changing directories can change available commands |
| Unknown `/name` → error, unknown text → passthrough | Model-style invocation via Skill tool is more robust |

**Confidence:** Alta

---

## Cross-Cutting Insights

### Architecture Pattern: Convention Over Configuration

Claude Code's extension model follows a clear pattern:
- **Skills:** Convention is `SKILL.md` in a directory. No registration needed.
- **Tools:** Convention is MCP server. No registration needed (discovered via config).
- **Hooks:** Convention is `settings.json` entries. Declarative, not programmatic.
- **Commands:** Skills auto-register as commands. No separate registration.

### The Three Extension Surfaces for RaiSE

```
1. SKILL.MD files     → Commands (user-invoked + model-invoked)
2. MCP servers        → Tools (model-invoked)
3. Settings.json      → Hooks (event-driven control)
```

Everything RaiSE needs to extend Claude Code flows through these three surfaces. No internal APIs needed. No monkey-patching. No forks.

### Deprecation Strategy

CC is mid-migration on bash command parsing (AST-based `parseForSecurity` replacing regex `splitCommand`). **Target new APIs.** When we see `_DEPRECATED` functions in CC source, find their replacement.

---

*Generated by 4 parallel research agents analyzing Claude Code source.*
*Method: ADR-016 Phase 2 — Targeted Deep Dives.*
