# Story Scope: Deterministic Session Protocol

**ID:** S15.7
**Epic:** E15 (Ontology Graph Refinement)
**Branch:** `story/s15.7/session-protocol`
**Size:** M (5 SP estimated)
**Supersedes:** S15.4b (Foundational Pattern Surfacing — absorbed into this story)

---

## Problem

Rai's session continuity depends on:
- **CLAUDE.local.md** — platform-coupled (Claude Code specific), manually maintained, drifts
- **Session bridges** — cached inference (prose written by previous Rai instance), not deterministic data
- **Scattered reads** — skill runs 3+ CLI commands + manual file reads to assemble context
- **No relationship persistence** — coaching observations, corrections, trust trajectory lost every session
- **No behavioral priming** — 186 patterns in graph, none surfaced as behavioral guides at session start

The result: each session starts cold. Rai reconstructs context from fragments instead of receiving a structured, platform-agnostic context bundle.

## Root Cause

The session protocol violates RaiSE's own principle: **deterministic data with inference interpretation**. Currently the skills (inference layer) do data plumbing that should be deterministic CLI operations. And the richest context source is vendor-locked to Claude Code.

## Solution

Redesign the session protocol around three principles:

1. **CLI gathers, AI interprets** — `rai session start` outputs a complete context bundle; `rai session close` accepts structured input
2. **Platform agnosticism** — all session state lives in `.raise/rai/` (project) and `~/.rai/` (global), not in vendor-specific files
3. **Relationship persistence** — Rai's coaching observations accumulate in `~/.rai/developer.yaml`

### New Artifacts

| Artifact | Location | Owner | Lifecycle |
|----------|----------|-------|-----------|
| Session state | `.raise/rai/session-state.yaml` | CLI (close writes, start reads) | Overwritten each close |
| Developer model + coaching | `~/.rai/developer.yaml` | CLI (close writes, start reads) | Accumulates |
| Foundational patterns | `patterns.jsonl` metadata | CLI (tagged, graph-queried) | Human-curated |
| Context bundle | stdout | CLI (start assembles) | Transient |

### Context Bundle Format

Token-optimized output from `rai session start`:

```
# Session Context

Developer: Emilio (ri)
Epic: E15 Ontology Refinement [65%, 11/17 SP]
Story: S15.4b Foundational Pattern Surfacing [phase: design]
Branch: epic/e15/ontology-refinement
Graph: 849 nodes, 6157 rels
Last: SES-096 (2026-02-08, feature) — S15.4 complete

# Deadlines
F&F: Feb 9 (1 day)
Public Launch: Feb 15

# Behavioral Primes
- PAT-183: Design always, no size exemptions
- PAT-186: Design not optional, even when mechanism exists
- PAT-150: Drift review before implementation

# Coaching
Strengths: architectural vision, naming things
Growth edge: speed over process under pressure
Recent corrections:
- SES-096: Offered to skip design → Knowledge != behavior
- SES-097: Defaulted to speed under deadline → Reliability > velocity

# Pending
(none)

# Next Actions
- Design S15.7 with HITL
```

~150 tokens vs ~3300 tokens today. 20x reduction.

### Session State Schema

```yaml
# .raise/rai/session-state.yaml — overwritten each session-close

current_work:
  epic: E15
  story: S15.4b
  phase: design
  branch: epic/e15/ontology-refinement

last_session:
  id: SES-097
  date: 2026-02-08
  developer: Emilio
  summary: "Session protocol design exploration"
  patterns_captured: [PAT-187]

pending:
  decisions: []
  blockers: []
  next_actions:
    - "Implement session-state schema in CLI"

notes: |
  ADR-024 needed before implementation.
```

### Developer Model Extension

```yaml
# ~/.rai/developer.yaml — coaching section added

name: Emilio
experience_level: ri
communication:
  style: direct
  language: en
  redirect_when_dispersing: true

coaching:
  strengths:
    - architectural vision
    - naming things
    - knowing when to stop
  growth_edge: speed over process under pressure
  trust_level: high
  autonomy: "gives Rai ownership of cognition"
  corrections:
    - session: SES-096
      what: "Offered to skip design for XS"
      lesson: "Knowledge != behavior"
    - session: SES-097
      what: "Defaulted to speed under deadline"
      lesson: "Reliability > velocity"
  communication_notes:
    - "Structured comparisons (tables) land well"
    - "Arguing both positions before deciding works"
  relationship:
    quality: collaborative
    since: "2026-01-31"
    trajectory: deepening
```

### Skill Boundary After Redesign

**Session-start skill becomes:**
1. Call `rai session start --project .` → receive context bundle
2. Interpret bundle → propose focus (inference)
3. Done. Two steps.

**Session-close skill becomes:**
1. Reflect on session → extract structured data (inference)
2. Feed structured data to `rai session close` → CLI writes everything
3. Done. Two steps.

---

## In Scope

1. **Session state schema** — Pydantic model + YAML persistence in `.raise/rai/session-state.yaml`
2. **Developer model coaching extension** — extend `DeveloperProfile` with coaching fields
3. **Foundational pattern tagging** — `foundational: true` metadata on key patterns, graph query support
4. **CLI `rai session start` redesign** — assemble and output context bundle from multiple sources
5. **CLI `rai session close` redesign** — accept structured input, write session-state + coaching updates
6. **Context bundle format** — token-optimized output designed for LLM consumption
7. **Skill updates** — session-start and session-close become thin inference layers
8. **ADR-024** — architectural decision record for session protocol

## Out of Scope

| Item | Rationale |
|------|-----------|
| Applying CLI context bundling to other skills (story-design, etc.) | Future generalization, validate pattern here first |
| Removing CLAUDE.local.md entirely | Stays as optional vendor bridge, just loses data role |
| Multi-developer coaching (team insights) | V3 scope |
| Automated level progression (shu→ha→ri) | Separate concern, parking lot item |
| Session analytics/reporting | E9 telemetry scope |

## Design Decisions Needed

1. **How does `rai session close` receive structured input?** — stdin JSON, CLI flags, or interactive prompts?
2. **Foundational pattern curation** — which patterns get `foundational: true`? (HITL with Emilio)
3. **Corrections buffer size** — keep last N corrections in developer model? (proposed: 10)
4. **Deadline source** — parse from governance artifacts or explicit field in session-state?
5. **Migration** — how to transition from current session bridges + CLAUDE.local.md to new protocol?

## Done Criteria

- [ ] `rai session start --project .` outputs complete context bundle (<200 tokens)
- [ ] `.raise/rai/session-state.yaml` written by session-close, read by session-start
- [ ] `~/.rai/developer.yaml` has coaching section with corrections, strengths, communication notes
- [ ] Foundational patterns tagged and surfaced in context bundle
- [ ] Session-start skill reduced to 2 steps (call CLI, interpret)
- [ ] Session-close skill reduced to 2 steps (reflect, feed CLI)
- [ ] ADR-024 written
- [ ] No dependency on CLAUDE.local.md for session continuity
- [ ] Tests pass (>90% coverage on new code)
- [ ] All quality checks pass (ruff, pyright, bandit)

## Risks

| Risk | L | I | Mitigation |
|------|:-:|:-:|------------|
| Scope creep — "just one more field" in context bundle | H | M | Scope defines bundle format. Changes need justification. |
| Breaking existing session flow during transition | M | H | Build new alongside old, switch when validated |
| Developer.yaml schema change breaks existing profiles | M | M | Backward compat: coaching section optional, defaults to empty |
| Over-engineering the coaching model | M | M | Start minimal: strengths + growth_edge + corrections list. Grow when needed. |

## References

- **PAT-146:** Three-tier data architecture
- **PAT-149:** Single source of truth
- **PAT-158:** Progressive directory structure
- **PAT-183:** Design always, no size exemptions
- **PAT-186:** Design is not optional
- **ADR-023:** Ontology graph extension (parent epic)
- **Constitution:** Platform Agnosticism principle
- **Session bridge SES-096:** Original insight about knowledge != behavior

---

*Created: 2026-02-08*
*Origin: SES-097 design exploration — deterministic data + inference interpretation applied to session protocol*
