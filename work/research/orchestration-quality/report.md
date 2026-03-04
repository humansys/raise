# Research Report: Orchestration Quality Preservation

## Question
How do teams run long-running, multi-phase AI agent workflows with Claude Code without quality degradation from context saturation?

## Finding Summary

| # | Finding | Confidence | Sources |
|---|---------|-----------|---------|
| F1 | `context: fork` in skill frontmatter runs the skill in an isolated subagent with fresh context | HIGH | Official docs (3), GitHub (1) |
| F2 | Custom agents (`.claude/agents/`) can preload skills, set models, permissions, and memory | HIGH | Official docs (2) |
| F3 | Context beyond ~60% degrades quality 15-25%; our orchestrator fills context by phase 5 | HIGH | SFEIR, internal measurement (4.6x gap) |
| F4 | "Document & Clear" (checkpoint to disk, reset, continue) is an established pattern | HIGH | Practitioner evidence (2) |
| F5 | Subagents cannot spawn other subagents — orchestration must remain in the main thread | HIGH | Official docs (1) |

## Contrary Evidence

- Shrivu Shankar (Source 4) argues against custom subagents, preferring main-agent delegation. However, this applies to **rigid subagents** where the subagent prompt is generic. Our case is different: the **skill content IS the detailed instruction set** — the subagent gets exactly the same SKILL.md it would get inline, but in a fresh context.
- Agent Teams (Source 2) are experimental and add significant complexity. Overkill for sequential skill chains.

## Recommended Architecture

### Pattern: "Checkpoint & Fork"

The orchestrator (`rai-story-run`) stays in the main thread as a **lightweight coordinator**. Heavy skills execute via `context: fork` in isolated subagents. Between phases, the orchestrator writes structured checkpoint data to disk and reads back only the summary.

```
Main thread (orchestrator):
  ┌─ Phase detect ─────────────────────┐
  │ Read checkpoint files               │
  │ Determine next phase                │
  └─────────────────────────────────────┘
          │
          ▼
  ┌─ Phase N (fork) ───────────────────┐
  │ Skill runs in isolated subagent     │
  │ Full context: SKILL.md + CLAUDE.md  │
  │ Writes artifacts to disk            │
  │ Returns structured summary          │
  └─────────────────────────────────────┘
          │
          ▼
  ┌─ Gate check ───────────────────────┐
  │ Orchestrator reads summary          │
  │ Applies delegation gate             │
  │ Decides continue/pause              │
  └─────────────────────────────────────┘
          │
          ▼
  ┌─ Phase N+1 (fork) ─────────────────┐
  │ Fresh context!                      │
  │ Reads only: prior phase artifacts   │
  │ Not: 200 tool results from phase N  │
  └─────────────────────────────────────┘
```

### Implementation Options

#### Option A: `context: fork` on individual skills (minimal change)

Add `context: fork` to heavy skills (implement, AR, QR, review). The orchestrator invokes them via the Skill tool, which handles forking automatically.

**Pros:** Minimal changes to existing skills. Uses built-in Claude Code mechanism.
**Cons:** Orchestrator still accumulates context from light phases. Subagent doesn't have conversation context from prior phases (only CLAUDE.md + SKILL.md + artifacts on disk).

#### Option B: Custom agent for story execution

Create `.claude/agents/story-executor.md` with preloaded skills. The orchestrator spawns it per-phase with a precise prompt including checkpoint data.

**Pros:** Full control over agent context. Can include phase-specific context in spawn prompt.
**Cons:** More setup. Agent Teams (for inter-agent communication) are experimental.

#### Option C: Hybrid — orchestrator manages, heavy phases fork (RECOMMENDED)

The orchestrator runs lightweight phases (start, close) inline and forks heavy phases (design, plan, implement, AR, QR, review) as subagents. Each forked phase:
1. Receives its SKILL.md instructions (via `context: fork` or Agent tool)
2. Reads prior artifacts from disk (design.md, plan.md, etc.) — NOT from conversation history
3. Writes its own artifacts to disk
4. Returns a structured summary to the orchestrator

**Pros:**
- Fresh context for every heavy skill (solves the 4.6x quality gap)
- Orchestrator stays lightweight (only handles phase detection + gates)
- Artifacts on disk are the explicit contract between phases
- Each skill produces identical quality whether standalone or orchestrated
- Uses proven Claude Code mechanisms (`context: fork` or Agent tool)

**Cons:**
- Subagent doesn't see conversation context from other phases
- Additional latency per fork (~150-250ms per Source 7)
- Phase skills need to be self-contained (read their own context from disk)

### Key Design Decisions

1. **Artifacts are the API:** Phase N writes files. Phase N+1 reads files. No implicit context passing.
2. **Orchestrator is thin:** Only phase detection, delegation, gate checks. No heavy reasoning.
3. **Skills are self-contained:** Each skill reads its own inputs from disk. Works identically standalone or forked.
4. **Summary protocol:** Each forked skill returns a structured summary (not raw output) to keep orchestrator context lean.

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Forked skill doesn't have enough context | Each skill already reads prior artifacts from disk (design.md informs plan, plan informs implement) |
| Additional latency | ~150-250ms per fork. For 8 phases, ~1-2s total. Negligible vs. quality gain. |
| Subagent can't interact with user | Delegation gates happen in main thread, between forks. HITL preserved. |
| `context: fork` not yet supported for Skill tool invocations | Use Agent tool directly as fallback. Both achieve context isolation. |

## Governance

- **ADR:** Create ADR for "Checkpoint & Fork" orchestration pattern
- **Backlog:** Story to implement hybrid orchestration in `rai-story-run`
- **Pattern:** `checkpoint-and-fork` — architectural pattern for quality-preserving orchestration
