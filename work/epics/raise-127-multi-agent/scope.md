# Epic RAISE-127 pt1: Session Instance Isolation — Scope

> **Status:** IN PROGRESS
> **JIRA:** [RAISE-127](https://humansys.atlassian.net/browse/RAISE-127)
> **Branch:** `epic/raise-127/multi-agent-pt1`
> **Created:** 2026-02-15
> **Soft launch:** 2026-02-18 (Wed)
> **Community launch:** 2026-03-01

---

## Objective

Any number of AI agents or terminals can run concurrent sessions on the same project without state corruption or data loss.

**Value proposition:** This is a launch blocker. Real developers run 3 Claude Code terminals + 3 Gemini tasks simultaneously. Without session isolation, state corrupts silently — the kind of bug that destroys trust on first use.

**Success criteria:**
- 6 concurrent sessions on the same project produce independent, correct session histories
- Running `rai session close` from wrong directory is rejected with clear error
- Existing single-session setups auto-migrate without data loss
- Platform agnostic — no IDE-specific detection required

---

## Stories (8 SP estimated)

| # | JIRA | Story | Size | SP | Depends On |
|---|------|-------|:----:|:--:|------------|
| 1 | [RAISE-137](https://humansys.atlassian.net/browse/RAISE-137) | Session Token Protocol — start returns ID, `--session` on commands, env var fallback | S | 2 | — |
| 2 | [RAISE-138](https://humansys.atlassian.net/browse/RAISE-138) | Per-Session State Isolation — session directories, migration, concurrent access | M | 3 | RAISE-137 |
| 3 | [RAISE-139](https://humansys.atlassian.net/browse/RAISE-139) | Project-Scoped Session Writes — CWD poka-yoke (fixes RAISE-134) | S | 3 | RAISE-138 |
| 4 | [RAISE-146](https://humansys.atlassian.net/browse/RAISE-146) | Wire --session through telemetry CLI commands | XS | 1 | RAISE-138 |

**Total:** 4 stories, 9 SP estimated

---

## In Scope

**MUST:**
- Session token protocol: `rai session start` returns `SES-NNN`, all commands accept `--session`
- Resolution order: `--session` flag > `RAI_SESSION_ID` env var > error
- Per-session directories under `.raise/rai/personal/sessions/{SES-NNN}/`
- Per-session state.yaml and signals.jsonl (telemetry)
- Shared session ledger (`index.jsonl`) with fcntl locking
- `active_sessions` list in `developer.yaml` (replaces single `current_session`)
- Migration from old flat layout to per-session directories
- CWD validation before writing to `.raise/` (poka-yoke for RAISE-134)
- Agent type as optional metadata (`--agent`) on session start, not isolation key

**SHOULD:**
- Clear error messages when CWD mismatch detected
- Session directory cleanup on `rai session close`
- Stale session detection (>24h) across all active sessions

---

## Out of Scope (deferred)

- Agent coordination / shared context between sessions → RAISE-127 pt2
- Agent-to-agent communication → RAISE-127 pt2
- IDE-specific plugins / deep integration → RAISE-128
- Hierarchical memory (instance → repo → team → org) → RAISE-135
- Aggregated cross-session telemetry → parking lot
- Session directory garbage collection (beyond close cleanup) → parking lot

---

## Architecture

**ADR:** [ADR-029: Session Instance Isolation](../../dev/decisions/adr-029-agent-isolation-strategy.md)

### Core Design: Token-Based Session Protocol

The CLI follows a REST-like token model. The caller is responsible for identifying which session it belongs to. The CLI is stateless — no magic detection.

```
AI Agent                          CLI
   │                               │
   ├─ rai session start ──────────►│ generates SES-177
   │◄── "Session SES-177 started" ─┤
   │                               │
   │  (agent remembers SES-177)    │
   │                               │
   ├─ rai emit-work --session 177 ─►│ writes to SES-177/
   ├─ rai emit-work --session 177 ─►│ writes to SES-177/
   │                               │
   ├─ rai session close --session ─►│ finalizes SES-177/
   │◄── "Session SES-177 closed" ──┤
```

### Directory Layout (after)

```
.raise/rai/personal/
├── sessions/
│   ├── index.jsonl              # Shared ledger (fcntl-locked)
│   ├── SES-177/                 # Claude Code terminal 1
│   │   ├── state.yaml
│   │   └── signals.jsonl
│   ├── SES-178/                 # Claude Code terminal 2
│   │   └── ...
│   └── SES-179/                 # Gemini task 1
│       └── ...

.raise/rai/memory/               # Shared project knowledge (unchanged)
├── patterns.jsonl               # fcntl-locked for concurrent appends
├── calibration.jsonl
└── index.json

~/.rai/developer.yaml            # Global profile
├── active_sessions: [           # Replaces current_session
│     {session_id: SES-177, started_at: ..., project: ..., agent: claude-code},
│     {session_id: SES-178, started_at: ..., project: ..., agent: claude-code},
│     {session_id: SES-179, started_at: ..., project: ..., agent: gemini},
│   ]
```

### Affected Modules

| Module | Impact | What Changes |
|--------|--------|--------------|
| `mod-session` (state, close, bundle) | **High** | Token protocol, per-session paths, active_sessions |
| `mod-config` (paths.py) | **High** | `get_session_dir(session_id)` replaces flat `get_personal_dir()` for session state |
| `mod-onboarding` (profile.py) | **Medium** | `active_sessions` schema, migration from `current_session` |
| `mod-cli` (session commands) | **Medium** | `--session` flag on all commands, `--agent` on start |
| `mod-telemetry` (writer.py) | **Medium** | Write signals to per-session directory, not shared file |
| `mod-memory` (writer.py) | **Low** | Session index append uses fcntl lock (already does for patterns) |

---

## Dependencies

```
RAISE-137 (session token protocol)
     ↓
RAISE-138 (per-session state isolation)
     ↓
RAISE-139 (CWD poka-yoke)
```

Strictly sequential — each story builds on the previous. No parallel tracks.

**External:** None. All changes are internal to rai-cli.

---

## Done Criteria

### Per Story
- [ ] Code implemented with type annotations (pyright strict)
- [ ] Unit tests passing (>90% coverage on new code)
- [ ] Ruff + pyright + bandit pass
- [ ] Story retrospective complete

### Epic Complete
- [ ] All 3 stories complete
- [ ] 6 concurrent sessions produce independent, correct histories (manual verification)
- [ ] CWD mismatch rejected with clear error
- [ ] Existing `personal/` auto-migrates on first run
- [ ] RAISE-134 resolved
- [ ] Architecture docs updated
- [ ] Epic retrospective completed
- [ ] Merged to v2

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Migration corrupts existing session data | Low | High | Backup before migrate, atomic move, integration test |
| AI agent forgets to pass `--session` | Medium | Medium | Clear error message when missing, `RAI_SESSION_ID` env var as fallback |
| Session directories accumulate unbounded | Low | Low | Cleanup on close, gc strategy deferred to parking lot |
| `active_sessions` schema change breaks session start | Low | Medium | Backward compat: detect old `current_session` format, migrate in place |

---

## Notes

### Why Session Instance, Not Agent Type
Original design namespaced by agent type (claude-code, cursor). Emilio's insight: 3 Claude Code terminals are the same agent but different sessions. The isolation unit is the session instance. Agent type is useful metadata but the wrong isolation key.

### Why Now
Soft launch is Feb 18. External developers will use multiple terminals/agents. Session corruption on first use is a trust-killer.

### Pt1 vs Pt2
Pt1 (this epic) = isolation — sessions don't interfere. Pt2 = coordination — sessions can share context intentionally. Pt1 is prerequisite for pt2, but pt2 is not on the critical path for launch.

---

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-02-15

### Story Sequence

| Order | Story | Size | SP | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|:--:|--------------|-----------|-----------|
| 1 | RAISE-137: Session Token Protocol | S | 2 | None | M1 | Foundation — all other work depends on session ID resolution |
| 2 | RAISE-138: Per-Session State Isolation | M | 3 | RAISE-137 | M2 | Core isolation — proves the architecture works |
| 3 | RAISE-139: Project-Scoped Writes (CWD poka-yoke) | S | 3 | RAISE-138 | M3 | Safety net — requires session paths to exist |

Strictly sequential. No parallel streams — each story builds on the previous.

### Milestones

| Milestone | After | Target | Success Criteria |
|-----------|-------|--------|------------------|
| **M1: Token Protocol** | RAISE-137 | Feb 16 | `rai session start` returns SES-NNN; `--session` and `RAI_SESSION_ID` accepted |
| **M2: Isolation Works** | RAISE-138 | Feb 17 | Two concurrent sessions produce independent state dirs; migration from old layout works |
| **M3: Launch Ready** | RAISE-139 | Feb 17 | CWD mismatch rejected with clear error; RAISE-134 closed; all tests green |
| **M4: Epic Complete** | retro | Feb 18 | Retrospective done, merged to v2, soft launch ready |

### Timeline

| Day | Work | Milestone |
|-----|------|-----------|
| Sat Feb 15 | RAISE-137 (S/2SP) | M1 |
| Sun Feb 16 | RAISE-138 (M/3SP) | M2 |
| Mon Feb 17 | RAISE-139 (S/3SP) | M3 |
| Tue Feb 18 | Buffer / retro / merge | M4 → soft launch |

### Progress Tracking

| Story | Size | Status | Actual | Notes |
|-------|:----:|:------:|:------:|-------|
| RAISE-137 | S | ✅ Done | 2h | 1.25x velocity |
| RAISE-138 | M | ✅ Done | ~1h | 1.0x velocity |
| RAISE-139 | S | ✅ Done | ~20min | 1.5x velocity |
| RAISE-146 | XS | Pending | — | Telemetry CLI wiring |

**Milestones:**
- [x] M1: Token Protocol (Feb 15 — completed ahead of schedule)
- [x] M2: Isolation Works (Feb 15 — completed ahead of schedule)
- [ ] M3: Launch Ready (Feb 17)
- [ ] M4: Epic Complete (Feb 18)

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| RAISE-137 `--session` plumbing touches many commands | Medium | Medium | Start with session start/close only, extend to other commands incrementally |
| RAISE-138 migration logic more complex than estimated | Low | High | Test with actual `~/.rai/developer.yaml` and `.raise/rai/personal/` before merging |
| Buffer day consumed by demo prep (Feb 16 Coppel) | Low | Low | Demo is handled via live workflow, no prep needed |

---

*Plan created: 2026-02-15*
*Next: `/rai-story-start` for RAISE-137*

---

*Created: 2026-02-15*
*Updated: 2026-02-15*
