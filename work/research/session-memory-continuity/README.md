# Research: Session Memory Continuity in AI Coding Agents

> RES-SESSION-MEM-001 | 2026-02-14
> Informs: Session narrative hotfix for RaiSE v2
> Depth: Standard | Sources: 10

## Navigation

- [Evidence Catalog](sources/evidence-catalog.md) — All sources with ratings
- [Report](session-memory-report.md) — Full findings + recommendation

## 5-Minute Summary

### The Problem

RaiSE loses session reasoning between conversations. The context bundle preserves "what to do next" (~30 tokens) but drops "why we decided this" (~550 tokens). PAT-E-279.

### What Others Do

| Agent | Approach | Session Handoff |
|-------|----------|----------------|
| **Cline** | new_task tool + Memory Bank | Structured context block (completed, state, next, refs). Triggered at % threshold. Best practice in the space. |
| **Claude Code** | Auto session memory | Background extraction every ~5k tokens. Stored as markdown summaries. Loaded as "past sessions that might not be related." |
| **OpenAI SDK** | Session objects | SQLite-backed. Context trimming or summarization. Framework-level. |
| **OpenClaw** | Mem0 plugin | Two tiers: long-term (user-scoped) + short-term (session-scoped). Vector recall. |
| **Cursor** | Rules + Notepads | No built-in session memory. Static rules only. Memories feature emerging. |
| **Aider** | Chat history file | Full append-only `.aider.chat.history.md`. No structured handoff. Brute force. |

### Key Patterns (triangulated)

1. **Structured > raw history** — Cline, OpenAI SDK, and Claude Code all use structured summaries, not full history replay. (S1, S3, S7)

2. **"Immediately resumable" as design goal** — Cline's docs explicitly name this. The handoff should let the next session start working without re-establishing context. (S1, S8)

3. **Two-tier memory** — Long-term (patterns, decisions, architecture) + short-term (current task, session state). OpenClaw and Cline both converge here. (S2, S4)

4. **Narrative + structured, not either/or** — Cline uses structured sections WITH free-form content inside each section. Pure structured loses reasoning; pure narrative loses parsability. (S1, S8)

5. **Rolling window, not accumulation** — Load last session's context, not all sessions. OpenAI SDK supports trimming; Claude Code marks past sessions as "might not be related." (S3, S7)

### Recommendation

**Confidence: HIGH**

Add a `narrative` field to SessionState that captures structured-but-readable session context:

```yaml
narrative:
  decisions: "Key decisions made and WHY"
  research: "Research completed + conclusions"
  artifacts: "Files created/modified with purpose"
  branch_state: "Exact state for git continuity"
```

This is what Cline's new_task context block does, adapted to our architecture. We already have the write path (session close) and read path (session start bundle). The field goes in SessionState, gets overwritten each close, loaded each start. No new infrastructure.

**What we're NOT doing:**
- Vector recall (OpenClaw/Mem0) — overengineered for our use case
- Full history persistence (Aider) — doesn't scale
- Background extraction (Claude Code) — we're on top of Claude Code, complement don't duplicate
- Memory Bank files (Cline) — we already have governance docs serving this purpose
