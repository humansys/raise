# Scope: E325 Agent-Orchestrated Workflow

**Epic:** [RAISE-325](https://humansys.atlassian.net/browse/RAISE-325)
**Branch:** `epic/e325/agent-orchestrated-workflow`
**Base:** `dev`
**Date:** 2026-03-01
**Research:** `research-synthesis.md` (6 frameworks, 40+ sources)

---

## Objective

Transform the RaiSE interaction model from human-dispatched skill invocation to agent-orchestrated workflow execution with parametrized HITL, so the developer focuses on decisions while the agent handles process.

## Value

After completion: developer says "implement story X" and the agent executes the full lifecycle cycle (start → design → plan → implement → review → close), pausing only at pre-agreed decision/validation points. Process overhead drops from ~40% to ~10% of interaction time. Design is portable across agent runtimes (Claude Code, Roo, Cursor).

## In Scope (MUST)

- Skill I/O contracts — typed inputs/outputs in SKILL.md frontmatter for all lifecycle skills
- Delegation profile — per-developer, per-skill HITL configuration (review/notify/auto)
- CLI output optimization — agent-optimized summaries from `rai backlog` and `rai graph`
- Backlog-aware skills — lifecycle skills call `rai backlog` at key points
- Discovery/onboard compaction — fewer manual steps, subagent offloading
- Story orchestrator — meta-skill `/rai-story-run` chains full story cycle
- Epic orchestrator — meta-skill `/rai-epic-run` chains full epic cycle

## In Scope (SHOULD)

- Delegation profile defaults per ShuHaRi level (Shu=review all, Ha=notify on design, Ri=auto except gates)
- Graceful degradation when `rai backlog` commands unavailable

## Out of Scope

- `rai docs` CLI integration (CLI doesn't exist yet → future epic)
- Multi-agent orchestration (RAISE-127)
- Workflow DSL or visual editor
- Server-side orchestration (local-first only)
- Agent Teams integration (experimental in Claude Code)
- Delegation auto-tuning based on history

## Stories

| ID | Story | Size | Depends On |
|----|-------|------|------------|
| S325.1 | **Skill I/O Contract Definition** — typed inputs/outputs for 12 lifecycle skills in SKILL.md frontmatter | S | — |
| S325.2 | **Delegation Profile Model** — YAML schema, stored in developer.yaml, loaded at session-start | S | — |
| S325.3 | **CLI Output as ACI** — optimize `rai backlog` and `rai graph` output for agent consumption | S | — |
| S325.4 | **Backlog-Aware Skills** — integrate `rai backlog` in lifecycle skills (create, transition, comment) | M | S325.1, S325.3 |
| S325.5 | **Discovery/Onboard Compaction** — reduce manual steps, auto-wire components | M | S325.1 |
| S325.6 | **Story Orchestrator Skill** — `/rai-story-run` chains full story cycle with delegation profile | M | S325.1, S325.2, S325.4 |
| S325.7 | **Epic Orchestrator Skill** — `/rai-epic-run` chains full epic cycle, iterates stories | L | S325.6 |

## Done Criteria

- [ ] Developer says "implement story X" → agent executes full cycle with HITL only at pre-agreed gates
- [ ] Delegation profile loaded at session-start, respected by orchestrator skills
- [ ] Lifecycle skills call `rai backlog` at key points (Jira reflects state without manual intervention)
- [ ] CLI output follows ACI principles (simple, compact, informative)
- [ ] Discovery/onboard completes with ≤50% of current manual steps
- [ ] Manual skill invocation still works (backward compatible)
- [ ] Design portable: all orchestration logic in SKILL.md + rai CLI, no proprietary runtime APIs
- [ ] Architecture docs updated, retrospective complete

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Context explosion in orchestrator — full story cycle exceeds context window | Alta | Alto | Skill I/O contracts as state handoff; each skill operates with fresh context + typed state. CLI offloading for heavy operations. |
| Backlog CLI incomplete — needed commands missing from dev | Media | Medio | Verify in S325.4 before integrating. Critical commands (create, search, transition) confirmed working. Graceful fallback. |
| Delegation profile too rigid or too granular | Media | Medio | Sensible defaults per ShuHaRi level. Progressive adoption, not big-bang. |

## Parking Lot

| Item | Origin | Priority | Promotion Condition |
|------|--------|----------|-------------------|
| `rai docs` CLI + docs-aware skills | Problem brief vertiente 1 | P1 | When `rai docs` CLI exists |
| Delegation auto-tuning | Research (OpenHands dynamic policy) | P2 | After 50+ orchestrated cycles provide data |
| Agent Teams integration | Research (Claude Code experimental) | P3 | When Agent Teams exits experimental |
| Cross-agent memory sharing via rai-server | Problem brief | P3 | When rai-server supports it |

---

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-03-01, SES-305

### Sequencing Strategy

**Walking skeleton + risk-first.** Build metadata foundations first (3 S-sized stories), then integration (2 M-sized), then orchestrators that prove the architecture end-to-end.

### Architecture Review Decisions (SES-305)

Incorporated before planning:

| Question | Decision | Impact |
|----------|----------|--------|
| Q2: I/O contracts value | Keep lean — `raise.inputs`/`raise.outputs` as typed metadata, NOT code-enforced. Orchestrator hardcodes chain order; metadata is documentation for the agent. | S325.1 simpler |
| Q3: Delegation profile scope | Minimal first — `delegation.default_level` in DeveloperProfile, derive per-skill from ShuHaRi. Per-skill overrides only if needed. | S325.2 simpler |
| Q4: S325.5 epic fit | Keep in epic — orthogonal but small enough, and I/O contracts benefit discovery skills too. | No change |
| Q5: state.yaml vs git-derived | Prefer git-derived state (branch exists? plan.md exists?). Orchestrator infers phase from artifacts, no new state file. | S325.6 simpler |
| C1: e301 dependency | Resolved — e301 merged to dev, rebased. All 7 backlog commands available. | S325.3/S325.4 unblocked |

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S325.1 — Skill I/O Contracts | S | None | M1 | Foundation — defines metadata schema all other stories read. Touches all 12 SKILL.md files. Low risk, high unlock. |
| 2 | S325.3 — CLI as ACI | S | None | M1 | Add `--format agent` to `rai backlog` + `rai graph`. Unlocks S325.4. Independent from S325.1 but sequential avoids merge conflicts in shared areas. |
| 3 | S325.2 — Delegation Profile | S | None | M1 | Add delegation section to DeveloperProfile. Minimal: default_level + ShuHaRi derivation. Needed by S325.6. |
| 4 | S325.4 — Backlog-Aware Skills | M | S325.1, S325.3 | M2 | First integration story — lifecycle skills call `rai backlog` at key points. Proves "skills call CLI" pattern. |
| 5 | S325.5 — Discovery Compaction | M | S325.1 | M2 | Reduce manual steps in discover/onboard. Benefits from I/O contracts. Can run in parallel with S325.4 if needed. |
| 6 | S325.6 — Story Orchestrator | M | S325.1, S325.2, S325.4 | M3 | The payoff — `/rai-story-run` chains full cycle. Uses delegation profile, reads I/O metadata, calls backlog-aware skills. First E2E proof. |
| 7 | S325.7 — Epic Orchestrator | L | S325.6 | M3 | `/rai-epic-run` iterates stories via S325.6. Caps the epic. |

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|------------------|
| **M1: Metadata Foundation** | S325.1, S325.3, S325.2 | All 12 skills have I/O contracts. CLI `--format agent` works for backlog + graph. DeveloperProfile has delegation section. All existing tests pass. |
| **M2: Integration** | S325.4, S325.5 | At least 3 lifecycle skills call `rai backlog` at key points (story-start creates Jira, story-close transitions). Discovery completes with ≤50% manual steps. |
| **M3: Orchestration** | S325.6, S325.7 | Developer says "implement story X" → agent executes full cycle. `/rai-epic-run` chains story cycles. Delegation profile respected. Manual invocation still works. |
| **M4: Epic Complete** | — | Done criteria met. Architecture docs updated. Retrospective complete. |

### Work Streams

```
Time →

Stream 1 (Sequential): S325.1 ─► S325.3 ─► S325.2 ─► S325.4 ─► S325.6 ─► S325.7
                                                         │
Stream 2 (Parallel):                                   S325.5 ──────────────┘
                                                    (can start after S325.1,
                                                     merge before S325.6)
```

**Merge point:** S325.5 merges to epic before S325.6 starts. S325.5 is the only parallelizable story — all others form a critical path.

**Practical note:** Single-developer, so "parallel" means S325.5 can be done in any order after S325.1 and before S325.6. If momentum is strong on the critical path, defer S325.5 to after S325.4.

### Progress Tracking

| Story | Size | Status | Actual | Velocity | Notes |
|-------|:----:|:------:|:------:|:--------:|-------|
| S325.1 | S | Done | S | 2.0x | I/O contracts on 12 skills, QR 2 fixes, PAT-E-585+586 |
| S325.S1 | S | Done | S | 1.0x | Spike: journal for compaction resilience, 4 bug layers, pivot hooks→instructions |
| S325.3 | S | Pending | — | — | |
| S325.2 | S | Pending | — | — | |
| S325.4 | M | Pending | — | — | |
| S325.5 | M | Pending | — | — | |
| S325.6 | M | Pending | — | — | |
| S325.7 | L | Pending | — | — | |

### Sequencing Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| I/O contract schema doesn't fit orchestrator needs (designed 5 stories apart) | M/M | Keep contracts minimal in S325.1. Orchestrator (S325.6) is the real consumer — adjust contracts then if needed. |
| Backlog CLI behavior changes on merge from e301 code | L/M | Tests pass post-rebase. Run backlog smoke test at S325.3 start. |
| Context window overflow in orchestrator (full story cycle) | M/H | Git-derived state (Q5 decision) eliminates state.yaml overhead. Each skill invocation starts fresh. CLI offloads heavy ops. |

---

*Planned: 2026-03-01, SES-305*
*Designed: 2026-03-01, SES-304*
