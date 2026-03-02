# E325 — Agent-Orchestrated Workflow: Retrospective

**Date:** 2026-03-01
**Duration:** Sessions SES-305 through SES-314 (10 sessions)
**Branch:** `epic/e325/agent-orchestrated-workflow`

---

## Objective vs Outcome

**Objective:** Transform RaiSE from human-dispatched skill invocation to agent-orchestrated workflow execution with parametrized HITL.

**Outcome:** Delivered. Developer says `/rai-story-run S999.1` or `/rai-epic-run E999` → agent executes the full cycle, pausing only at delegation gates. Process overhead target was ~40% → ~10%. All 7/7 done criteria met (+ retrospective = 8/8).

---

## Metrics

| Metric | Value |
|--------|-------|
| Stories | 8 (7 planned + 1 spike) |
| Total size | 3S + 1 spike + 2M + 1M + 1L |
| Average velocity | 2.1x |
| Fastest | S325.2 (3.0x), S325.7 (3.0x) |
| Slowest | S325.S1 (1.0x — spike), S325.4 (1.5x) |
| Tests | 3105 passing, 0 introduced failures |
| Skills created | 3 new (/rai-discover, /rai-story-run, /rai-epic-run) |
| Skills modified | 5 (project-onboard v3.0.0 + 4 deprecated discover-*) |
| Patterns added | 10 (PAT-E-585 through PAT-E-604) |
| Code changes | BacklogHook (S325.4), DelegationConfig (S325.2), CLI --format agent (S325.3), I/O contracts (S325.1) |
| SKILL.md-only stories | 3 (S325.5, S325.6, S325.7) |

---

## What Went Well

### 1. Walking skeleton + risk-first sequencing
M1 (metadata foundation) → M2 (integration) → M3 (orchestration) — each milestone built on the previous. No story was blocked by an incomplete dependency. The spike (S325.S1) was done exactly when needed (between M1 and M2).

### 2. SKILL.md-only stories accelerated M3
S325.5, S325.6, S325.7 required no Python code — only well-designed SKILL.md files. This meant no test overhead, no type checking, no linting gates beyond `rai skill validate`. M3 completed at 2.4x and 3.0x velocity.

### 3. User-driven design pivots
- S325.5: "se podria hacer todo en un skill?" → unified /rai-discover replaced 5 individual skills (80% HITL reduction vs 64-73% from original plan)
- S325.6-S325.7: "cuáles son más confiables?" → reliability framing shaped all design decisions

### 4. Pattern reuse compounded
S325.6 established the orchestrator pattern (PAT-E-602, PAT-E-603). S325.7 was mechanical application at 3.0x velocity. The second orchestrator was essentially free.

### 5. Architecture decisions held
Q5 (git-derived state) eliminated state.yaml complexity in both orchestrators. Q2 (lean I/O contracts) kept metadata simple. Q3 (minimal delegation) kept DelegationConfig to 3 fields. No decision needed revision during implementation.

---

## What to Improve

### 1. BacklogHook debugging was trial-and-error
S325.4 bugfix (adapter resolution + timeout) took multiple attempts before checking the working configuration in the main worktree. Lesson learned: go to Gemba first (check what works before guessing).

### 2. Interactive design framing
In S325.6 I presented 3 equally-weighted options per decision. The user redirected to "which is most reliable?" twice before I adapted. By S325.7 I led with reliability framing. Should be default from the start (PAT-E-604).

### 3. L-sized story was actually M
S325.7 was estimated L but delivered as M (3.0x velocity). The pattern reuse from S325.6 made it smaller than planned. Better to recognize "pattern application" stories and size them accordingly.

---

## Key Patterns (from this epic)

| ID | Pattern | Type |
|----|---------|------|
| PAT-E-585 | I/O contracts: type,cardinality,source tuples | architecture |
| PAT-E-586 | Contracts as documentation, not enforcement | process |
| PAT-E-590 | ACI: --format agent flag, not separate command | architecture |
| PAT-E-593 | DelegationLevel as StrEnum for YAML serialization | technical |
| PAT-E-595 | Hook architecture: events + bridge, not direct calls | architecture |
| PAT-E-598 | Consolidate linear pipelines into one skill (YAGNI) | process |
| PAT-E-599 | SKILL.md-only stories still benefit from design cycle | process |
| PAT-E-602 | Orchestrator skills: design control flow, not domain content | process |
| PAT-E-603 | Phase-detection-as-resumption: artifact table + reverse check | architecture |
| PAT-E-604 | Lead with reliability framing in interactive design | process |

---

## Deliverables

### M1: Metadata Foundation
- I/O contracts on 12 lifecycle skills (raise.inputs/raise.outputs)
- `--format agent` on 5 CLI commands (backlog search/create/transition, graph query/context)
- DelegationLevel enum + DelegationConfig + resolve_delegation() in DeveloperProfile

### M2: Integration
- BacklogHook: fires on `rai signal emit-work`, creates/transitions Jira issues
- Unified `/rai-discover`: replaces 5 discovery skills, 80% HITL reduction
- project-onboard v3.0.0 delegates to /rai-discover

### M3: Orchestration
- `/rai-story-run`: chains 6 story skills, phase detection (6 states), delegation gates at post-design + post-implement
- `/rai-epic-run`: chains 4 epic skills + story iteration, phase detection (5 states), delegation gates at post-design + post-plan

### Bugfixes
- BacklogHook: explicit "jira" adapter (not auto-detect) + 30s timeout for MCP cold start

---

## Architecture Summary

```
/rai-epic-run
  ├── /rai-epic-start
  ├── /rai-epic-design     ── GATE: post-design
  ├── /rai-epic-plan        ── GATE: post-plan
  ├── Story iteration (from Progress Tracking table)
  │     ├── /rai-story-run S1
  │     │     ├── /rai-story-start
  │     │     ├── /rai-story-design   ── GATE: post-design
  │     │     ├── /rai-story-plan
  │     │     ├── /rai-story-implement ── GATE: post-implement
  │     │     ├── /rai-story-review
  │     │     └── /rai-story-close
  │     ├── /rai-story-run S2 ...
  │     └── /rai-story-run SN
  └── /rai-epic-close
```

Key properties:
- **Stateless:** Phase detection from git artifacts, no state.yaml
- **Portable:** All logic in SKILL.md, no proprietary runtime APIs
- **Resumable:** Re-invoke after failure, auto-detects progress
- **Delegated:** REVIEW/NOTIFY/AUTO per developer profile
- **Backward compatible:** All individual skills work independently
