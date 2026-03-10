# Research: OpenClaw Architecture Analysis

> **Status:** Complete
> **Date:** 2026-02-01
> **Researcher:** Rai
> **Decision Informs:** V3 Rai as Service architecture + V2 improvements

## Quick Navigation

| Document | Purpose |
|----------|---------|
| `openclaw-report.md` | Full findings with evidence |
| `sources/evidence-catalog.md` | All sources with ratings |
| `learnings-for-raise.md` | Actionable recommendations |

## 15-Minute Overview

### Research Question

**Primary:** What architectural patterns from OpenClaw/Moltbot can RaiSE adopt for V3 (Rai as Service)?

**Secondary:**
1. How is the codebase structured?
2. How do multi-channel messaging patterns work?
3. How do skills/plugins enable extensibility?
4. How does session memory/state persist?
5. What drove community adoption velocity?

### Key Findings

1. **Gateway Architecture** — Single WebSocket control plane decouples channels from intelligence
2. **Workspace-as-Memory** — Plain markdown files (AGENTS.md, SOUL.md, MEMORY.md) are the source of truth
3. **Pi Agent Runtime** — Minimal core (4 tools) + self-extensibility > bloated toolset
4. **Lobster Pipelines** — Typed, approval-gated workflows for deterministic multi-step operations
5. **Pre-compaction Flush** — Silent memory writes before context truncation preserves state
6. **Skills as Functions** — JSON schema + JS/TS implementation = easily extensible

### Recommendations for RaiSE

| Priority | Recommendation | Informs |
|----------|----------------|---------|
| HIGH | Adopt workspace-as-memory pattern (markdown files) | V2 + V3 |
| HIGH | Implement pre-compaction memory flush | V3 |
| MEDIUM | Consider typed workflow pipelines (Lobster-inspired) | V3 |
| MEDIUM | Gateway pattern for multi-interface support | V3 (Rovo, Jira) |
| LOW | Skills marketplace for community extensibility | V3+ |

### Confidence Level

**HIGH** — Based on 15+ sources including official documentation, GitHub issues, and expert analysis (Armin Ronacher).

---

*Full report: `openclaw-report.md`*
