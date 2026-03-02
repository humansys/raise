# Research Synthesis: Agent-Orchestrated Workflow

**Epic:** RAISE-325
**Date:** 2026-03-01
**Method:** 6 parallel research agents, primary sources prioritized

---

## Cross-Framework Comparison Matrix

| Dimension | OpenHands | SWE-agent | Aider | Cline/Roo | CrewAI/LangGraph | **Claude Code** |
|-----------|-----------|-----------|-------|-----------|------------------|-----------------|
| **Mental model** | Digital worker with event log | LLM as end-user needing good UX | Pair programmer | Assistant with permissions | Team of specialists / State machine | Model-driven loop with primitive tools |
| **Orchestration** | Event-sourced step loop | Sequential thought-action-obs | Interactive conversation | Plan/Act phases; Roo: Boomerang subtasks | Crews (sequential/hierarchical) / Graph nodes+edges | Skills + Subagents + Hooks |
| **HITL model** | SecurityAnalyzer + ConfirmationPolicy (per-action) | None (fully autonomous) | Scope control (files in context) + auto-commit/lint/test | Per-action approval; Roo: per-task-boundary | CrewAI: task-level pause; LangGraph: interrupt() at any node | Permission modes + hooks (PreToolUse can gate) |
| **Autonomy spectrum** | Policy-based (AlwaysConfirm → NeverConfirm) | Binary (autonomous only) | Mode-based (ask → code → architect) | Category-based toggles (8 categories) | Human tool / interrupt primitives | 5 modes (plan → default → acceptEdits → dontAsk → bypass) |
| **Skill composition** | Tools as Action-Execution-Observation | Bash + ACI custom commands | Monolithic (modes, not tools) | MCP tools + modes | Agents + Tasks + Flows | Skills (SKILL.md) + Subagents + Agent Teams |
| **State management** | Event stream (append-only, immutable) | Message history (linear) | Git as safety net | Conversation context | CrewAI: Pydantic state; LangGraph: checkpointed TypedDict | CLAUDE.md + auto-memory + session compaction |
| **Context strategy** | Condenser (compress old events) | Collapse old observations | Repo map (PageRank on AST) | Conversation window | Explicit state passing | CLAUDE.md hierarchy + rules + auto-compact |

---

## Key Insights by Theme

### 1. HITL Is Not Binary — It's a Spectrum

Every mature framework offers granularity:
- **OpenHands**: AlwaysConfirm → ConfirmRisky → NeverConfirm (dynamic, mid-session)
- **Cline/Roo**: 8 action categories, each independently toggleable
- **Claude Code**: 5 permission modes + per-tool rules + hooks as override
- **LangGraph**: interrupt_before/after any node + interrupt() inline + HumanInTheLoopMiddleware

**Implication for RaiSE:** The delegation protocol should be per-skill granular, not global. A developer might trust `story-start` (mechanical) but want to review `story-design` (decisions).

### 2. The Orchestration Split: Model-Driven vs. Code-Driven

Two camps:
- **Model-driven** (OpenHands, Claude Code, Aider): The LLM decides what to do next based on context. No explicit workflow graph. Flexible but less predictable.
- **Code-driven** (LangGraph, CrewAI Flows): Explicit graph/DAG defines execution order. Predictable but rigid.

**RaiSE's position:** We're model-driven (Claude Code runtime) but with **declarative metadata** (raise.next, raise.prerequisites) that guides the model. This is a hybrid — the model orchestrates, but the skill metadata provides rails.

### 3. The ACI Insight (SWE-agent): Interface Design > Model Intelligence

SWE-agent's core thesis: the interface you give the agent matters more than the model's raw capability. Their 4 principles:
1. Actions must be simple and easy to understand
2. Actions must be compact and efficient (token cost)
3. Feedback must be informative but concise
4. Guardrails mitigate error propagation

**Implication for RaiSE:** The `rai` CLI is our ACI. Its commands should produce high-density, agent-optimized output. Not raw JSON dumps — structured, concise summaries that fit the model's reasoning style.

### 4. Context Isolation Is Critical for Multi-Step

- **Roo Code Boomerang**: Subtasks get isolated context; only summaries flow back
- **Claude Code Subagents**: Fresh context per subagent; CLAUDE.md reloaded but not parent conversation
- **LangGraph**: Explicit state schema per subgraph; parent-child communicate through channels

**Implication for RaiSE:** Long-running epic orchestration will hit context limits. The solution is NOT one infinite conversation. It's skill-level isolation with structured state handoff between skills.

### 5. Claude Code Already Has Most Primitives We Need

**Do NOT rebuild:**
- Task tracking with dependencies (TaskCreate/TaskUpdate)
- Pre/post tool hooks with gating (hooks system)
- Permission modes and per-tool rules
- Subagent spawning with worktree isolation
- Skill discovery and invocation
- Quality gates (TaskCompleted hook, Stop hook with prompt type)
- Dynamic context injection (SessionStart hook, `!`command`` in skills)

**What RaiSE ADDS:**
- Process knowledge (which skills in what order, with what HITL)
- Domain CLI (`rai backlog`, `rai graph`, `rai docs`)
- Epistemological standards and pattern capture
- Cross-session continuity via structured memory (beyond auto-memory)

### 6. The Delegation Protocol Pattern

Across frameworks, the pattern converges:
1. **Define what the agent CAN do** (permissions/tools/capabilities)
2. **Define when to ASK** (confirmation policies, HITL gates, interrupt points)
3. **Define how to RESUME** (state checkpointing, event injection, Command(resume=))

RaiSE needs all three. Currently we have (1) via skill tool restrictions and (2) partially via verification blocks in skills, but (3) is missing — there's no structured state handoff between skills.

---

## Architectural Implications for E325

### What We Should Build

1. **Delegation Profile** — Per-developer, per-skill HITL configuration
   - Stored in developer.yaml or project manifest
   - Three levels per skill: `review` (always pause), `notify` (show output, continue), `auto` (proceed silently)
   - Loaded at session start, respected by the orchestrating agent

2. **Skill I/O Contracts** — Structured inputs/outputs for each lifecycle skill
   - Not free text — typed state that flows skill-to-skill
   - Enables the agent to chain skills without losing context between compactions
   - Analogous to LangGraph's TypedDict state or CrewAI Flow's Pydantic state

3. **CLI as ACI** — Optimize `rai` CLI output for agent consumption
   - `rai backlog` and `rai docs` produce agent-optimized summaries
   - High-density semantic output (not raw API responses)
   - Skills call CLI, not MCP/APIs directly

4. **Orchestrator Skill** — A meta-skill that reads the skill DAG and executes it
   - Uses Claude Code's native skill invocation
   - Respects delegation profile for HITL gates
   - Uses `rai` CLI for state persistence between skills (not conversation memory)

### What We Should NOT Build

- Workflow engine / state machine runtime (Claude Code IS the runtime)
- Custom permission system (use Claude Code's native permissions + hooks)
- Custom task tracking (use Claude Code's TaskCreate/TaskUpdate)
- Event sourcing / event stream (overkill for our use case)
- Multi-agent orchestration (Claude Code's Agent Teams, when stable)

---

## Evidence Catalog

| Source | Type | Confidence | Key Signal |
|--------|------|------------|------------|
| OpenHands ICLR 2025 paper | Academic | Very High | Event-sourced architecture, SecurityAnalyzer + ConfirmationPolicy |
| OpenHands SDK paper (Nov 2025) | Academic | Very High | V1 modular architecture, AEO tool pattern |
| SWE-agent NeurIPS 2024 | Academic | High | ACI design > model intelligence |
| SWE-agent official docs | Primary | High | Sequential loop, no HITL by design |
| Aider official docs (6 pages) | Primary | High | Pair programming framing, git as safety net, repo map |
| Cline official docs | Primary | High | Category-based approval, model-driven safety classification |
| Roo Code official docs | Primary | High | Boomerang mode, 8-category permissions, context isolation |
| CrewAI official docs | Primary | Medium-High | Flows + Crews, human_input=True, hierarchical process |
| LangGraph official docs | Primary | High | interrupt(), checkpointing, Command primitive, state machines |
| Claude Code official docs (7 pages) | Primary | Very High | Skills, hooks, permissions, subagents, agent teams, memory |
| Anthropic engineering blog | Primary | High | Sandboxing reduced permission prompts 84% |

**Total sources consulted:** 40+
**Primary sources:** 30+
**Academic papers:** 3

---

*Research completed: 2026-03-01, SES-304*
