# Epic RAISE-127 pt1: Multi-Agent Isolation — Scope

> **Status:** IN PROGRESS
> **JIRA:** [RAISE-127](https://humansys.atlassian.net/browse/RAISE-127)
> **Branch:** `epic/raise-127/multi-agent-pt1`
> **Created:** 2026-02-15
> **Soft launch:** 2026-02-18 (Wed)
> **Community launch:** 2026-03-01

---

## Objective

Developers can use multiple IDEs/agents concurrently on the same project without session corruption or data loss.

**Value proposition:** This is a launch blocker. Real developers use Claude Code + Cursor + terminal simultaneously. Without isolation, session state corrupts silently — the kind of bug that destroys trust on first use.

**Success criteria:**
- Two agents running `rai session start/close` on the same project produce independent, correct session histories
- Running `rai session close` from wrong directory is rejected with clear error
- Existing single-agent setups auto-migrate without data loss

---

## Stories (8 SP estimated)

| # | JIRA | Story | Size | SP | Depends On |
|---|------|-------|:----:|:--:|------------|
| 1 | [RAISE-137](https://humansys.atlassian.net/browse/RAISE-137) | Agent Identity — detect IDE/runtime, assign agent ID | S | 2 | — |
| 2 | [RAISE-138](https://humansys.atlassian.net/browse/RAISE-138) | Namespaced Session State — per-agent isolated directories | M | 3 | RAISE-137 |
| 3 | [RAISE-139](https://humansys.atlassian.net/browse/RAISE-139) | Project-scoped session writes — CWD poka-yoke (fixes RAISE-134) | S | 3 | RAISE-138 |

**Total:** 3 stories, 8 SP estimated

---

## In Scope

**MUST:**
- Agent identity detection via `RAI_AGENT_ID` env var + auto-detection fallback
- Per-agent subdirectories under `.raise/rai/personal/{agent-id}/`
- Migration of existing `personal/` layout to `personal/default/`
- CWD validation before writing to `.raise/` (poka-yoke for RAISE-134)
- `current_session` in developer.yaml becomes dict keyed by agent ID

**SHOULD:**
- Clear error messages when CWD mismatch detected
- `rai session status` shows all active agents

---

## Out of Scope (deferred)

- Agent coordination / shared state → RAISE-127 pt2
- Agent-to-agent communication → RAISE-127 pt2
- IDE-specific plugins / deep integration → RAISE-128
- Hierarchical memory (instance → repo → team → org) → RAISE-135
- Aggregated cross-agent telemetry → parking lot

---

## Architecture

**ADR:** [ADR-029: Agent Isolation Strategy](../../dev/decisions/adr-029-agent-isolation-strategy.md)

### Key Design Decisions

**1. Agent identity = environment variable (not process detection)**
- `RAI_AGENT_ID` env var, set by IDE integration (CLAUDE.md hooks, .cursorrules, etc.)
- Fallback auto-detection from known IDE env vars
- Default: `"default"` for direct terminal use

**2. Isolation = per-agent directories (not file locking)**
- Each agent gets its own subdirectory under `personal/`
- Session state, session history, and telemetry are all per-agent
- Shared project knowledge (patterns, graph) stays shared — fcntl already handles concurrency

**3. Profile stays global, sessions become per-agent**
- `~/.rai/developer.yaml` is about the developer, not the agent
- `current_session` field changes from single value to `dict[str, CurrentSession]`
- Coaching, trust, experience — developer attributes, not agent attributes

### Directory Layout (after)

```
.raise/rai/personal/
├── claude-code/
│   ├── session-state.yaml
│   ├── sessions/index.jsonl
│   └── telemetry/signals.jsonl
├── cursor/
│   └── ...
└── default/
    └── ...
```

### Affected Modules

| Module | Impact | What Changes |
|--------|--------|--------------|
| `mod-config` (paths.py) | **High** | All `get_personal_dir()` calls gain agent_id parameter |
| `mod-session` (state, close, bundle) | **High** | Reads/writes use agent-namespaced paths |
| `mod-onboarding` (profile.py) | **Medium** | `current_session` schema change, migration |
| `mod-cli` (session commands) | **Medium** | Agent ID resolution, CWD validation |
| `mod-telemetry` (writer.py) | **Low** | Path already uses `get_personal_dir()` — inherits change |

---

## Dependencies

```
RAISE-137 (agent identity)
     ↓
RAISE-138 (namespaced state)
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
- [ ] Two agents can run concurrent sessions without corruption (manual verification)
- [ ] CWD mismatch rejected with clear error
- [ ] Existing `personal/` auto-migrates to `personal/default/` on first run
- [ ] RAISE-134 resolved
- [ ] Architecture docs updated
- [ ] Epic retrospective completed
- [ ] Merged to v2

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Migration corrupts existing session data | Low | High | Backup before migrate, atomic move operation, integration test |
| IDE env var detection is wrong/missing | Medium | Low | `RAI_AGENT_ID` explicit override always works, auto-detect is convenience only |
| `current_session` schema change breaks session start | Low | Medium | Backward compat: if old format detected, migrate in place |

---

## Notes

### Why Now
Soft launch is Feb 18. The first external developers to try RaiSE will likely use multiple IDEs. A session corruption bug on first use is a trust-killer. This must land before Wednesday.

### Pt1 vs Pt2
Pt1 (this epic) is isolation — agents don't interfere with each other. Pt2 is coordination — agents can share context intentionally. Pt1 is a prerequisite for pt2, but pt2 is not on the critical path for launch.

---

*Created: 2026-02-15*
*Updated: 2026-02-15*
