---
id: ADR-043
title: "Workflow as Abstraction — Configurable Lifecycle Phases"
status: "accepted"
date: "2026-03-03"
epic: "E347"
decision_makers: ["Emilio"]
---

# ADR-043: Workflow as Abstraction

## Context

RaiSE has a well-defined skill lifecycle for epics and stories (start → design → plan → implement → review → close). Backlog adapters (Jira, FileAdapter) have their own status models. Currently, BacklogHook hardcodes status names ("in-progress", "done") and skills don't interact with backlog statuses at all.

With E347 making `rai backlog` the single channel for work state, we need to decide how lifecycle phases map to backlog statuses.

Additionally, teams like Kurigage will have their own Jira workflows with custom statuses and transitions. RaiSE should not force its lifecycle on them.

## Decision

**Workflow is an abstraction layer between skills and adapter statuses.**

Three layers:

1. **Workflow Definition** — what phases exist and in what order (configurable per project)
2. **Phase-to-Status Mapping** — how phases translate to adapter-specific statuses/transitions (in adapter config)
3. **Skill Binding** — which skill runs at each phase (optional, enables custom skills per phase)

RaiSE ships a default workflow. Teams can override it.

### Default Workflow

```yaml
# .raise/workflow.yaml
workflows:
  epic:
    phases: [backlog, started, designing, planning, implementing, reviewing, done]
    default_skills:
      started: rai-epic-start
      designing: rai-epic-design
      planning: rai-epic-plan
      reviewing: rai-architecture-review
      done: rai-epic-close
  story:
    phases: [backlog, started, designing, planning, implementing, reviewing, done]
    default_skills:
      started: rai-story-start
      designing: rai-story-design
      planning: rai-story-plan
      implementing: rai-story-implement
      reviewing: rai-story-review
      done: rai-story-close
```

### Adapter Mapping

```yaml
# .raise/jira.yaml
workflow:
  status_mapping:
    backlog: "11"       # Jira transition IDs
    started: "21"
    designing: "31"
    planning: "31"      # multiple phases can map to same Jira status
    implementing: "31"
    reviewing: "41"
    done: "51"
```

### Interaction Model

- Skills transition by phase name: `rai backlog transition S347.1 designing`
- Adapter translates phase → backend-specific status/transition
- Session-start reads backend status, reverse-maps to phase name
- Teams customize by editing workflow.yaml and adapter mapping

## Consequences

### Positive
- Teams can define their own workflows without forking skills
- Jira workflows of any complexity can be mapped
- Skills are decoupled from adapter status models
- Enables future: teams create custom skills per phase of their workflow

### Negative
- One more config file (workflow.yaml) to manage
- Reverse mapping (Jira status → phase) can be ambiguous when multiple phases share a Jira status
- More indirection in the transition path

### Mitigations
- Default workflow ships with `rai init`, zero config for standard use
- Reverse mapping uses phase order as tiebreaker (later phase wins)
- Config validation at `rai adapter check` time

## Alternatives Considered

1. **Hardcode lifecycle statuses** — simpler but locks teams into RaiSE's workflow. Rejected.
2. **Only map to Jira statuses, no workflow layer** — works for Jira but doesn't generalize. Rejected.
3. **Full workflow engine (BPMN-like)** — over-engineering. Rejected. YAML config is sufficient.
