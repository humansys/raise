# Session Memory Continuity: Full Report

> RES-SESSION-MEM-001 | 2026-02-14
> Primary question: How do AI coding agents persist and restore session context?

---

## 1. Landscape Analysis

### 1.1 Cline: The Gold Standard for Handoff

Cline has the most mature session handoff mechanism in the open-source space. Two complementary systems:

**new_task tool** — Proactive context handoff triggered at configurable context window % (e.g., 50%). Packages structured context into XML block:
- Completed Work (files modified, decisions made)
- Current State (project status, running processes)
- Next Steps (prioritized, with implementation details)
- Reference Information (code snippets, patterns, preferences)
- Actionable Start (immediate next action)

Key design principle: **"immediately resumable"** — the next session should be able to start working without re-establishing context.

**Memory Bank** — Six markdown files providing long-term project memory:
- `projectbrief.md` (foundation), `productContext.md` (business), `systemPatterns.md` (architecture), `techContext.md` (tech stack), `activeContext.md` (current state), `progress.md` (status)

The Memory Bank is community-created (not official), loaded via custom instructions. Read-verify-execute-update cycle each session.

**Key insight:** new_task handles *between-task* continuity (short-term), Memory Bank handles *between-session* continuity (long-term). Two different time horizons, two different mechanisms.

### 1.2 Claude Code: Background Extraction

Claude Code (our runtime) has built-in session memory since v2.0.64:

- **Background extraction** every ~5,000 tokens or 3 tool calls
- Stores structured markdown summaries in `~/.claude/projects/<hash>/<session>/session-memory/summary.md`
- Captures: session title, current status, key results, work log
- Past sessions injected as background knowledge marked "might not be related"
- `/compact` loads pre-written summary instantly (no re-analysis)
- `/remember` promotes patterns from auto-memory to CLAUDE.local.md

**Key insight:** Claude Code's auto-memory is *within-session* continuity (survives compaction). Cross-session injection is weak — past sessions are treated as possibly irrelevant background.

### 1.3 OpenClaw: Two-Tier Memory via Mem0

OpenClaw agents are stateless by default. Context compaction (summarizing older context) causes lossy compression. The Mem0 plugin adds:

- **Long-term memory** — User-scoped, cross-session: name, tech stack, project structure, decisions
- **Short-term memory** — Session-scoped: current task, active context
- **Auto-Recall** — Pulls relevant long-term memories at session start via vector search

**Key insight:** Two-tier model (long-term patterns + short-term context) with intelligent recall. But vector search adds infrastructure complexity.

### 1.4 OpenAI Agents SDK: Framework-Level Sessions

The SDK provides session as a first-class concept:

- SQLite/SQLAlchemy backends for persistence
- Session protocol: `get_items()`, `add_items()`, `pop_item()`, `clear_session()`
- Two strategies: **context trimming** (drop older turns) vs **context summarization** (compress to summaries)
- Session = memory object. `session.run("...")` handles history automatically.

**Key insight:** Context summarization is the more sophisticated strategy — compress prior context into structured summaries injected into conversation. This is exactly what we need.

### 1.5 Cursor: Static Rules, No Session Memory

Cursor does NOT persist memory across conversations. Workarounds:
- `.cursorrules` / `.cursor/rules/*.mdc` — static project instructions
- Notepads — reusable context snippets
- Memories — emerging feature for fact retention
- MCP-based memory (basic-memory) — community solution

**Key insight:** Cursor's gap validates market demand. Their rules = our CLAUDE.md. Their emerging Memories = our patterns.

### 1.6 Aider: Brute Force History

Aider stores full chat history in `.aider.chat.history.md`. No structured handoff, no summarization. Relies on repo map for code context.

**Key insight:** Works for short, single-task sessions. Doesn't scale for multi-session workflows. No intelligence in what to carry forward.

---

## 2. Triangulated Claims

### Claim 1: Structured summaries outperform raw history for session continuity
**Confidence: HIGH**
- **S1 (Cline):** Structured context blocks with sections (completed, state, next, refs)
- **S3 (Claude Code):** Structured markdown summaries extracted in background
- **S7 (OpenAI SDK):** Context summarization strategy over raw trimming
- **Disagreement:** Aider uses raw history — but Aider targets single-session-per-task, not multi-session workflows

### Claim 2: Two-tier memory (long-term + short-term) is the emerging consensus
**Confidence: HIGH**
- **S2 (Cline Memory Bank):** Long-term project memory in markdown files
- **S4 (OpenClaw Mem0):** Explicit long-term vs short-term memory tiers
- **S5 (Cursor):** Rules (long-term) separate from session context (short-term)
- **S9 (Claude Code):** CLAUDE.md (long-term) vs session-memory (short-term)
- **Disagreement:** None found — all agents that address this use two tiers

### Claim 3: "Immediately resumable" is the right design goal for handoff
**Confidence: HIGH**
- **S1/S8 (Cline):** Explicitly names this as the design principle
- **S7 (OpenAI SDK):** Session.run() enables seamless continuation
- **S3 (Claude Code):** Auto-injection of past summaries as background
- **Disagreement:** None — all structured approaches aim for this

### Claim 4: Rolling window (last N sessions) beats accumulation
**Confidence: MEDIUM**
- **S7 (OpenAI SDK):** Context trimming drops older turns
- **S3 (Claude Code):** Past sessions marked "might not be related"
- **S4 (OpenClaw Mem0):** Short-term memory is session-scoped, not accumulated
- **Disagreement:** Cline Memory Bank accumulates (but it's project-level, not session-level)

### Claim 5: Session handoff should include decision rationale, not just decisions
**Confidence: MEDIUM**
- **S1 (Cline):** "Key decisions" in Completed Work section
- **S8 (Cline):** "References to previous decisions and their rationale"
- **Our own evidence (PAT-E-279):** Carry-forward with reasoning > bundle without reasoning
- **Disagreement:** No agent explicitly structures "why" separately — it's mixed into narrative sections

---

## 3. Gaps & Unknowns

1. **No agent separates "what" from "why" explicitly** — Cline comes closest with "key decisions" but doesn't formalize decision rationale as a distinct field.

2. **Token budget for handoff is undefined** — No agent documents how much context to carry. Cline lets users configure the threshold. Claude Code extracts ~every 5k tokens. Nobody measures the output size.

3. **Research/evidence carryover is unique to RaiSE** — No other agent has a research skill that produces evidence catalogs. Our narrative needs to handle this case.

4. **Multi-developer handoff is unexplored** — All agents assume single-developer. RaiSE's personal/ directory structure is ahead of the field here.

---

## 4. Recommendation

### Design: Structured Narrative in SessionState

Add a `narrative` field to `SessionState` with structured sections. This mirrors Cline's new_task context block, adapted to RaiSE's architecture:

```python
class SessionNarrative(BaseModel):
    """Structured session context for cross-session continuity.

    Designed to make the next session 'immediately resumable' —
    the AI can start working without re-establishing context.
    """
    decisions: str = ""     # Key decisions + rationale (WHY, not just WHAT)
    research: str = ""      # Research completed + conclusions
    artifacts: str = ""     # Files created/modified with purpose
    branch_state: str = ""  # Git state for exact continuity
    context: str = ""       # Free-form reasoning that doesn't fit above
```

**Why this structure:**
- `decisions` captures what PAT-E-279 identified as the primary loss
- `research` is unique to RaiSE — no other agent needs this
- `artifacts` provides the file inventory that was missing
- `branch_state` provides git continuity
- `context` is the safety valve for anything else

### Integration

**Write path (session close):**
1. Skill produces `narrative` section in YAML state file
2. `CloseInput` receives it
3. `process_session_close` passes to `SessionState`
4. Written to `session-state.yaml` (already overwritten each close)

**Read path (session start):**
1. `bundle.py` reads `state.narrative`
2. Formats as `# Session Narrative` section (NOT truncated)
3. Placed after "Last:" and before primes

**Token budget:** ~300-500 tokens for narrative. No hard enforcement — trust the skill to be concise. The skill template should provide size guidance ("2-3 sentences per field").

### What we're NOT doing (and why)

| Alternative | Why Not |
|---|---|
| Vector recall (Mem0) | Overengineered for our 1-developer use case |
| Full history (Aider) | Doesn't scale, no intelligence |
| Separate files per session (log_path) | SessionState already has write/read flow — extra files = extra plumbing for same result |
| Background extraction (Claude Code) | We run ON Claude Code — complement, don't duplicate |
| Memory Bank (Cline) | We already have governance docs + CLAUDE.md serving this role |

### Trade-offs

| Accepting | Because |
|---|---|
| Only last session's narrative survives | Rolling window is the consensus; patterns capture long-term |
| No vector search for relevant memories | Deterministic loading is simpler and sufficient |
| Skill must produce good narrative | Garbage in, garbage out — but skill template guides quality |
| No token budget enforcement | Trust over control; field size guidance in skill template |

### Risks

| Risk | Mitigation |
|---|---|
| Narrative bloat (skill writes too much) | Size guidance in template ("2-3 sentences per field") |
| Narrative staleness (close skipped) | Orphan session detection already exists |
| Duplication with Claude Code auto-memory | Different purposes: auto-memory = patterns, narrative = reasoning |

---

## 5. Governance Linkage

- **Hotfix:** Session narrative field in SessionState
- **Pattern:** PAT-E-279 (session handoff loses reasoning)
- **No ADR needed** — this is a field addition to existing schema, not architectural change
