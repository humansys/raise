# Epic Design: Agile HR Performance Management

> Partner: Just Leading Solutions (JLS)
> Domain: HR Performance Management for HRBPs

## Domain Model

```
PerformanceCycle (annual)
  ├── Participant (collaborator, manager, HRBP)
  ├── OKR (objective + measurable key results, quarterly review)
  ├── CheckIn (monthly 1:1 manager↔collaborator)
  │     ├── Agenda (AI-suggested topics for manager)
  │     ├── CoachingBrief (AI-generated context for HRBP)
  │     └── Agreement (action + owner + date)
  ├── Feedback (manager→collaborator, drafted with AI assistance)
  └── GateResult (advisory validation outcome)
```

### Key Types

| Type | Responsibility | Key Fields |
|------|---------------|------------|
| `PerformanceCycle` | Annual container | client, year, participants, status |
| `Participant` | Person in cycle | name, role (collaborator/manager/hrbp), team |
| `OKR` | Objective + Key Results | objective, key_results[], quarter, progress |
| `CheckIn` | Monthly 1:1 record | date, manager, collaborator, agenda, agreements[] |
| `Agenda` | Prep for 1:1 | topics[], okrs_to_review[], pending_feedback[] |
| `CoachingBrief` | HRBP context | alerts[], patterns[], suggestions[] |
| `Agreement` | Post-1:1 commitment | action, owner, due_date, status |
| `Feedback` | Feedback artifact | from, to, content, type, gate_results[] |
| `GateResult` | Advisory validation | gate_id, passed, findings[], severity |

## Workflow: Monthly Check-in Kata

### Phase: PREPARE (dual, async)

**For HRBP** (`prepare-coaching-brief`):
1. Load collaborator's cycle data (OKRs, prior check-ins, feedback history)
2. Detect patterns (missed deadlines, stalled OKRs, positive trends)
3. Generate alerts (overdue agreements, OKR risk)
4. Produce coaching brief: "Here's what the manager should know going in"
5. HRBP sends brief to manager

**For Manager** (`prepare-check-in`):
1. Load OKR status, last check-in agreements, pending feedback
2. Suggest concrete topics ("Discuss Q1 OKR on customer retention — 40% behind target")
3. Flag overdue agreements from last check-in
4. Produce agenda with prioritized talking points

### Phase: CONDUCT (human, offline)
- Manager and collaborator meet 1:1
- No AI involvement — this is a human conversation
- Manager uses prep agenda as guide, not script

### Phase: CAPTURE (`capture-agreements`)
1. Manager/HRBP inputs key outcomes from 1:1
2. AI structures into formal Agreements (action, owner, date)
3. OKR adjustments captured if discussed
4. Feedback observations noted for later drafting

### Phase: VALIDATE (advisory gates)
1. Run all configured gates against captured data
2. Surface findings as suggestions, not blockers
3. HRBP reviews and decides action

## JLS Configurability

JLS consultants customize per client via YAML:

| Parameter | Default | What it controls |
|-----------|---------|-----------------|
| `cycle.duration` | annual | Performance cycle length |
| `check_in.frequency` | monthly | How often 1:1s happen |
| `gates.mode` | advisory | advisory or blocking |
| `gates.*` | all true | Toggle individual gates |
| `prepare.coaching_brief` | true | Whether HRBP gets brief |
| `prepare.manager_prep` | true | Whether manager gets agenda |
| `okr.framework` | okr | okr, kpi, or hybrid |
| `okr.review_cadence` | quarterly | When OKRs are formally reviewed |
| `feedback.type` | manager_direct | Only manager↔collaborator in v1 |
| `feedback.language` | en | Language for AI-generated content |

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Advisory gates, not blocking | HR is human context; AI suggests, HRBP decides |
| Dual prepare (HRBP + Manager) | HRBP coaches manager, doesn't attend 1:1 |
| No HRIS integration in v1 | File-based import (CSV/JSON) avoids scope creep |
| Manager→collaborator feedback only | 360 feedback is a separate epic |
| Annual cycle with monthly check-ins | Matches most enterprise performance calendars |
| YAML config per client | JLS needs to customize without code changes |
| Pydantic models for all types | RaiSE standard: validation at boundaries |

## Migration Path

This is a **new module** — no existing code to migrate. New package location:
- `src/raise_cli/hr/` or `src/raise_hr/` (TBD in S477.1)
- Skills in `.raise/skills/hr/` or `.claude/skills/`
- Gates in `.raise/gates/hr/`
- Client configs in `.raise/clients/` or project-level config
