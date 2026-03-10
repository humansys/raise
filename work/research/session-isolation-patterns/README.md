# Research: Session Isolation Patterns in Multi-Agent Frameworks

> **Status:** Complete
> **Date:** 2026-02-15
> **Researcher:** Rai
> **Decision Informs:** RAISE-137 (Session Token Protocol) — ADR-029 validation

---

## Quick Navigation

| Document | Purpose |
|----------|---------|
| `session-isolation-report.md` | Full findings with evidence |
| `sources/evidence-catalog.md` | All sources with ratings |

---

## 15-Minute Overview

### Research Questions

1. **RQ1: Session Identity** — How do frameworks identify concurrent instances? (token vs PID vs lock)
2. **RQ2: Work Thread Continuity** — How is context maintained across sessions?
3. **RQ3: Session Lifecycle** — How are orphans detected, stale sessions cleaned?

### Key Findings

1. **Environment variable + per-session directories is industry standard**
   - Claude Code: `CLAUDE_CODE_TASK_LIST_ID` → `~/.claude/tasks/{id}/`
   - SWE-agent: Per-instance namespaces + chroot (35k evals/day)
   - OpenCode: Session metadata per instance
   - RaiSE: `RAI_SESSION_ID` → `.raise/rai/personal/sessions/SES-NNN/`

2. **Filesystem is the concurrency primitive**
   - No databases, no locks (except append-only logs), no IPC
   - File operations are atomic — filesystem guarantees isolation
   - Directory-per-session scales to production

3. **Orphan detection requires explicit state**
   - tmux: reference counting + timestamp staleness
   - Typical threshold: 24h
   - No automatic cleanup — explicit close or periodic scan
   - RaiSE: `active_sessions` list + `is_stale()` check

4. **PID detection is possible but not preferred**
   - cc-top demonstrates port fingerprinting for PID correlation
   - External tooling required — not native
   - Environment variable token is simpler and more reliable

5. **Most frameworks lack lifecycle management**
   - Claude Code, OpenCode: no documented orphan detection
   - tmux is the gold standard for lifecycle (reference count, deferred cleanup, notifications)
   - RaiSE adopts tmux patterns — stricter about state

### Validation of ADR-029

| ADR-029 Decision | Industry Evidence | Status |
|------------------|-------------------|--------|
| Session token via env var | ✓ Claude Code, SWE-agent, OpenCode | **VALIDATED** |
| Per-session directories | ✓ Claude Code, SWE-agent | **VALIDATED** |
| Resolution: flag > env var > error | ✓ Standard CLI pattern | **VALIDATED** |
| Filesystem for concurrency | ✓ Claude Code, SWE-agent | **VALIDATED** |
| active_sessions list | ✓ tmux reference counting | **VALIDATED** |
| Stale detection (>24h) | ✓ tmux, gastown | **VALIDATED** |

**Conclusion:** No design changes needed. Proceed with RAISE-137 implementation.

### Recommendations

**For RAISE-137 (Current):**
- Proceed with confidence — design validated by industry convergence
- Session token protocol is standard pattern
- Per-session directories proven at scale

**For RAISE-138 (Next):**
- Add explicit cleanup on close (tmux deferred cleanup pattern)
- Remove session directory after state archival

**For Parking Lot:**
- Session directory gc strategy (`rai session gc --older-than 30d`)
- Cross-session coordination protocol (pt2, after Agent Teams exits experimental)

### Confidence Level

**HIGH** — 13 sources (3 Very High, 6 High, 3 Medium, 1 Low). Industry convergence on token + directory pattern. RaiSE design aligns while adding governance (explicit orphan detection, stale warnings).

---

*Full report: `session-isolation-report.md`*
*Evidence catalog: `sources/evidence-catalog.md`*
