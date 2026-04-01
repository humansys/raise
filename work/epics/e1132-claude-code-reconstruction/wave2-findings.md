# E1132 Wave 2: Agent Infrastructure — Deep Dive Findings

**Phase:** 2 (Targeted Deep Dives) per ADR-016
**Wave:** 2 — Agent Infrastructure (coordinator, tasks, query, state)
**Source:** `~/Code/claude-code-main/src/`
**Date:** 2026-04-01

---

## Executive Summary

Claude Code's agent infrastructure is **deceptively simple at the API surface but deeply layered underneath**:

1. **Coordination is prompt-driven.** The coordinator module is just a mode flag + 370-line system prompt. Workers are context-blind. Communication is one-way XML notifications.

2. **Two separate task systems.** Runtime execution tracking (in-memory AppState) and planning/coordination (filesystem JSON with file locking). Different purposes, different persistence.

3. **The query loop is a while(true) with 5-layer compaction.** AsyncGenerator-based streaming, explicit State struct, tool execution mid-stream. Five compaction strategies compose in a specific order.

4. **State is a single atom.** One object, one store, no Redux/Zustand. Hand-rolled 35-line store with DeepImmutable wrapper. Tools access state imperatively via ToolUseContext.

---

## Finding F5: Multi-Agent Coordination

**Question:** How does CC coordinate sub-agents? What context do they share?

**Files:** `coordinator/coordinatorMode.ts`, `tools/AgentTool/AgentTool.tsx`, `tools/AgentTool/forkSubagent.ts`, `tools/AgentTool/runAgent.ts`, `tools/AgentTool/agentMemory.ts`, `tools/AgentTool/builtInAgents.ts`, `tools/SendMessageTool/SendMessageTool.ts`, `tasks/LocalAgentTask/LocalAgentTask.tsx`

### Three Multi-Agent Modes

| Mode | Context Sharing | Communication | Isolation |
|------|:--------------:|:-------------:|:---------:|
| **Coordinator** | None — workers context-blind | One-way XML notifications | Full |
| **Fork** | Full conversation cloned | Shared prompt cache | Partial (no recursive fork) |
| **Swarm/Teammates** | Shared task list (filesystem) | Mailbox messages | tmux/in-process |

### Coordinator Mode

- Activated by env var `CLAUDE_CODE_COORDINATOR_MODE=1` + feature gate
- Module is just a flag + system prompt (~370 lines)
- Coordinator **never uses file/shell tools** — only Agent, SendMessage, TaskStop
- Workers must receive self-contained prompts (file paths, line numbers, error text)
- Scratchpad directory for durable cross-worker state (filesystem)
- "Synthesize findings into specific prompts" is the coordinator's primary job

### Agent Spawning

- `Agent({ prompt, subagent_type?, description, run_in_background? })`
- Built-in types: `Explore` (read-only), `Plan` (read-only), general-purpose, verification, code-guide
- Custom agents from `.claude/agents/` directory
- Auto-background after 120s (feature-gated)
- Async agents get restricted tool set (`ASYNC_AGENT_ALLOWED_TOOLS`)

### Context Sharing Detail

| Context | Coordinator Workers | Fork Children | Swarm Teammates |
|---------|:------------------:|:-------------:|:---------------:|
| Conversation history | No | Full clone | No |
| System prompt | Own | Cloned (cache hit) | Own |
| CLAUDE.md | Yes | Yes | Yes |
| File state cache | Fresh | Cloned from parent | Fresh |
| MCP servers | Inherited + own | Inherited | Inherited |
| Agent memory | Per-agent (3 scopes) | Per-agent | Per-agent |
| AppState mutations | Isolated (no-op) | Isolated | Isolated |
| Task state mutations | Via setAppStateForTasks | Via setAppStateForTasks | Via setAppStateForTasks |

### RaiSE Impact (E3)

| Insight | Implication for E3 |
|---------|-------------------|
| Worker isolation is fundamental | Self-contained prompts, no shared conversation |
| Scratchpad = filesystem shared state | Simple, observable, no custom protocol |
| Notification-as-message pattern | Workers report via XML, coordinator treats as signals |
| Fork vs Worker tradeoff | Fork = expensive but full context; Worker = cheap but explicit context |
| Coordinator's job is synthesis | Orchestrator is an intelligence layer, not a router |

**Confidence:** Alta

---

## Finding F6: Task System

**Question:** How does CC persist and coordinate tasks between agents?

**Files:** `Task.ts`, `tasks.ts`, `tasks/types.ts`, `tasks/stopTask.ts`, `tasks/LocalAgentTask/LocalAgentTask.tsx`, `tasks/LocalShellTask/LocalShellTask.tsx`, `tasks/InProcessTeammateTask/types.ts`, `utils/task/framework.ts`, `utils/task/diskOutput.ts`, `utils/tasks.ts`, `tools/TaskCreateTool/TaskCreateTool.ts` + 5 more tool files

### Two Completely Separate Systems

| Aspect | System 1: Runtime Execution | System 2: Planning/Coordination |
|--------|:--------------------------:|:-------------------------------:|
| Purpose | Track running processes | Plan and coordinate work |
| Storage | In-memory AppState | Filesystem JSON (`~/.claude/tasks/`) |
| Persistence | Ephemeral | Durable (survives restart) |
| Concurrency | Single-process | File locking (proper-lockfile, ~10 agents) |
| ID scheme | Type prefix + 8 random chars | Sequential integers |
| Statuses | pending/running/completed/failed/killed | pending/in_progress/completed |
| Shared by agents | Via setAppStateForTasks | Via shared task list directory |

### System 1: Runtime Execution (7 task types)

```
local_bash       — background shell commands
local_agent      — subagent spawned locally
remote_agent     — cloud sessions (ultraplan, ultrareview)
in_process_teammate — swarm teammates
local_workflow   — workflow scripts
monitor_mcp      — MCP monitoring
dream            — auto-dream memory consolidation
```

Output goes to per-task disk files with delta-based reading (model gets only new output since last poll). 5GB cap per task.

### System 2: Planning/Coordination

```typescript
type Task = {
  id: string, subject: string, description: string,
  owner?: string,          // agent name for claiming
  status: 'pending' | 'in_progress' | 'completed',
  blocks: string[],        // dependency graph
  blockedBy: string[],
  metadata?: Record<string, unknown>
}
```

Key coordination primitives:
- **claimTask()** — atomic claim with busy-check (one task per agent)
- **blockTask()** — bidirectional dependency linking
- **Mailbox notification** — on ownership change, message sent to new owner
- **TaskListTool** — filters completed blockers, hides `_internal` metadata tasks

### RaiSE Impact (E3)

| Insight | Implication |
|---------|------------|
| Two-system split (runtime + planning) | E3 should separate execution tracking from work planning |
| Filesystem-as-database with locking | Works for ~10 agents; proper-lockfile with 30 retries |
| claimTask() is the coordination primitive | Atomic claiming prevents double-work |
| Explicit dependency graph (blocks/blockedBy) | Topological ordering without separate scheduler |
| Output as per-task disk files | Survives memory pressure, readable by any process |
| 292-agent incident → 50-message UI cap | Hard limits prevent memory blowup in large swarms |

**Confidence:** Alta

---

## Finding F7: Query Pipeline

**Question:** What's the query lifecycle? How does the engine call the LLM?

**Files:** `QueryEngine.ts` (1295 lines), `query.ts` (1729 lines), `query/config.ts`, `query/deps.ts`, `query/stopHooks.ts`, `query/tokenBudget.ts`, `services/api/claude.ts` (3419 lines)

### Three-Layer Architecture

```
QueryEngine (session scope)
  → Owns mutableMessages, abortController, totalUsage
  → submitMessage() is AsyncGenerator yielding SDKMessages
  
  query() / queryLoop() (turn scope)
    → while(true) loop with explicit State struct
    → Each iteration = one API call
    → Exit when no tool_use blocks in response
    
    queryModelWithStreaming() (API call scope)
      → Tool schema building, message normalization
      → withRetry() for rate limits, model fallback
      → anthropic.beta.messages.stream()
```

### Tool-Use Loop

```
while (true) {
  1. Compact if needed (5-layer strategy)
  2. Assemble context (user + system)
  3. Call API (streaming)
  4. Collect tool_use blocks
  5. Execute tools (optionally mid-stream)
  6. Yield tool results as user messages
  7. If no tool_use → run stop hooks → return
  8. Continue with updated messages
}
```

### 5-Layer Compaction (composition order)

| Layer | When | What |
|-------|------|------|
| 1. **Snip** | Before microcompact | Remove old history segments |
| 2. **Microcompact** | Before autocompact | Compress/truncate tool results |
| 3. **Context collapse** | Feature-gated | Projection-based history reduction |
| 4. **Autocompact** | Token count > ~90% window | Full LLM-powered summarization |
| 5. **Reactive** | API returns 413 | Emergency full summary |

Each layer has independent enable/disable gates (compile-time via `bun:bundle feature()`).

### Token Management

- **Autocompact threshold:** ~90-93% of effective context window
- **Token budget:** If `turnTokens < budget * 0.9` and not diminishing returns → auto-continue
- **Diminishing returns:** < 500 token delta for 3+ consecutive checks → stop
- **Max budget USD:** Hard cost cap checked after each yielded message
- **Max turns:** Checked before each loop continuation
- **Circuit breaker:** After N consecutive compact failures, stop trying

### Stop Hooks (post-turn lifecycle)

After model response, before returning to user:
- Memory extraction (auto-memory)
- Prompt suggestion
- Auto-dream (memory consolidation)
- Computer use cleanup
- Job classification
- Verification nudging

### RaiSE Impact

| Insight | Implication |
|---------|------------|
| AsyncGenerator everywhere | Pattern for streaming agent frameworks |
| while(true) + State struct (not recursion) | Explicit state machine for agent loops |
| 5-layer compaction | Understanding CC behavior requires knowing when it compacts |
| DI via QueryDeps (4 injectable functions) | Testable without module mocking |
| Stop hooks = post-turn intelligence | Memory, suggestions, dreams — beyond the LLM itself |
| Feature gates via bun:bundle | Dead code elimination for external builds |

**Confidence:** Alta

---

## Finding F8: State Management

**Question:** How is state shared across components in Claude Code?

**Files:** `state/store.ts`, `state/AppStateStore.ts` (~570 lines), `state/AppState.tsx`, `state/onChangeAppState.ts`, `state/selectors.ts`, `Tool.ts` (ToolUseContext)

### Architecture: Single Atom Store

```
createStore<T>() — 35 lines of code
  let state: T
  Set<Listener>
  onChange callback
  
  setState(updater: (prev: T) => T)
    → Object.is equality check
    → fire onChange
    → notify listeners
```

No Redux. No Zustand. No middleware. Hand-rolled, synchronous, single-threaded.

### AppState Shape (~450 lines of types)

| Domain | Key Fields |
|--------|-----------|
| Settings | `settings`, `verbose`, `mainLoopModel`, `effortValue`, `fastMode` |
| Permissions | `toolPermissionContext` (mode, bypass, session rules) |
| Agents/Tasks | `tasks` dict, `agentNameRegistry`, `viewingAgentTaskId` |
| MCP | `mcp.clients`, `mcp.tools`, `mcp.commands`, `mcp.resources` |
| Plugins | `plugins.enabled`, `plugins.disabled`, `plugins.errors` |
| UI | `expandedView`, `viewSelectionMode`, `footerSelection`, `activeOverlays` |
| Bridge | ~15 fields for `replBridge*` state |
| Speculation | `speculation` (mutable refs for streaming perf) |

Wrapped in `DeepImmutable<...>` with escape hatches for function-containing fields.

### Two Access Paths

| Path | Mechanism | Used By |
|------|-----------|---------|
| **React** | `useAppState(selector)` via `useSyncExternalStore` | Components |
| **Imperative** | `ToolUseContext.getAppState/setAppState` | Tools, non-React code |

### Subagent Isolation

- `setAppState` → no-op for subagents (isolated)
- `setAppStateForTasks` → always reaches root store (infrastructure mutations bypass isolation)

### Selective Persistence (onChange reactor)

| State Change | Side Effect |
|-------------|-------------|
| `mainLoopModel` | Write to user settings |
| `expandedView` | Save to global config |
| `verbose` | Save to global config |
| `toolPermissionContext.mode` | Notify CCR + SDK |
| `settings` | Clear auth credential cache |

### RaiSE Impact

| Insight | Implication |
|---------|------------|
| Single atom state = maximum simplicity | No distributed state for CLI apps |
| ToolUseContext = imperative state bridge | How tools read/mutate global state |
| onChange reactor pattern | Selective persistence without framework overhead |
| DeepImmutable + updater functions | Type-safe immutability without Immer |
| Two-tier mutation (setAppState vs setAppStateForTasks) | Subagent isolation with infrastructure bypass |

**Confidence:** Alta

---

## Cross-Cutting Insights for E3

### The Agent Orchestration Stack

```
Level 5: Coordinator System Prompt    ← Intelligence layer (what to do)
Level 4: Agent Tool + Task Tools      ← Orchestration API (how to do it)
Level 3: Query Pipeline               ← LLM interaction loop
Level 2: Task System (dual)           ← Execution tracking + work planning
Level 1: State Store                  ← Single atom, reactive
Level 0: Filesystem + File Locking    ← Persistence + cross-agent coordination
```

### Key Design Decisions CC Made

| Decision | Rationale | RaiSE Alignment |
|----------|-----------|:--------------:|
| Prompt-driven coordination | Flexible, no code changes needed | ✓ Our skills are prompts |
| Worker context isolation | Prevents confusion, forces explicit context | ✓ Match for our agent design |
| Filesystem for cross-agent state | Simple, observable, debuggable | ✓ Already use filesystem |
| AsyncGenerator streaming | Progressive output, composable layers | Consider for E3 |
| Single atom state | Simplicity for CLI apps | ✓ Match our Pydantic models |
| File locking for task coordination | Works for ~10 agents | Evaluate scaling needs |

### What E3 Should Adopt

1. **Coordinator-as-prompt pattern** — orchestrator intelligence in system prompt, not code
2. **Self-contained worker prompts** — every worker gets complete context, no conversation inheritance
3. **Filesystem scratchpad** — shared state between agents via files
4. **Dual task system** — separate runtime tracking from work planning
5. **claimTask() atomic claiming** — prevents double-work in multi-agent scenarios
6. **Delta-based output reading** — only new output since last poll

### What E3 Should Improve On

1. **CC's coordinator is a single mode flag** — E3 can have typed orchestration strategies
2. **CC's task claiming is file-lock based** — E3 could use server-side coordination for better scaling
3. **CC's compaction is 5 layers of complexity** — E3 should design context management upfront
4. **CC's 292-agent incident** — hard limits from day 1

---

*Generated by 4 parallel research agents analyzing Claude Code source.*
*Method: ADR-016 Phase 2 — Targeted Deep Dives.*
