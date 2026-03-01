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

*Designed: 2026-03-01, SES-304*
