---
epic_id: "E1286"
title: "Bugfix Pipeline Orchestration"
status: "active"
release: "2.4.0"
parent_epic: "E1001"
---

# E1286: Bugfix Pipeline Orchestration

## Objective

Decompose the monolithic `/rai-bugfix` skill into 7 atomic skills and build a `/rai-bugfix-run` orchestrator that enforces all phases via subagent isolation and HITL gates — eliminating the 77% step-skipping rate documented in E1133.

## Evidence

- E1133 S1133.6: 77% adoption failure — agents skip "optional" steps in monolithic skills
- E1001 dogfood: 38% full-cycle completeness (26/68 bugs with all 4 artifacts)
- E1001 Jira backfill: 1/80+ bugs had custom fields populated before today's fix
- E1065 bugfix.yaml: pipeline definition exists but references 7 skills that don't exist yet

## Stories

| ID | Title | Size | Depends |
|----|-------|------|---------|
| S1286.1 | Research: Benchmark dev agent bug-handling workflows | S | — |
| S1286.2 | Extract 7 atomic bugfix skills from monolithic | M | S1286.1 |
| S1286.3 | Build `/rai-bugfix-run` orchestrator | M | S1286.2 |
| S1286.4 | Dogfood: process 2+ bugs through orchestrated pipeline | S | S1286.3 |

## Done Criteria

- [ ] 7 atomic skills exist and are individually invocable
- [ ] `/rai-bugfix-run` orchestrates all 7 with subagent isolation
- [ ] Triage gate is mandatory (pauses even in AUTO delegation)
- [ ] Jira custom fields populated automatically in triage phase
- [ ] ≥2 bugs processed end-to-end through `/rai-bugfix-run` with 100% artifact completeness
- [ ] Skill names match E1065 `bugfix.yaml` references (forward-compatible with pipeline engine)
