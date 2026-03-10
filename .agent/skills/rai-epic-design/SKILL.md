---
description: 'Design an epic from strategic objective to feature breakdown. Use when
  starting a new body of work spanning multiple features (3-10), requiring architectural
  decisions, or when establishing technical direction for significant capability delivery.

  '
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '3'
  raise.frequency: per-epic
  raise.gate: ''
  raise.inputs: '- brief: file_path, optional, previous_skill

    - scope: file_path, required, previous_skill

    '
  raise.next: epic-plan
  raise.outputs: '- scope: file_path, next_skill

    - design: file_path, optional, next_skill

    '
  raise.prerequisites: project-backlog
  raise.version: 2.1.0
  raise.visibility: public
  raise.work_cycle: epic
name: rai-epic-design
---

# Epic Design

## Purpose

Design an epic that bridges strategic objectives to executable stories, making key architectural decisions and defining bounded scope for incremental delivery.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, create full scope document and ADRs
- **Ha/Ri**: Adjust depth based on complexity, lightweight ADRs, custom patterns

## Context

**When to use:** Starting work spanning 3-10 stories, requiring architectural decisions, or establishing technical direction.

**When to skip:** Single-story work → `/rai-story-design`. Bug fixes → issue tracker. High uncertainty → `/rai-research` first.

**Inputs:** Business objective, project backlog, constraints. Optionally: Problem Brief from `/rai-problem-shape` or Epic Brief from `/rai-epic-start`.

## Steps

### Step 1: Load Brief & Frame Objective

Check for Epic Brief (`work/epics/e{N}-{name}/brief.md`) or Problem Brief (`work/problem-briefs/*.md`). If found, use hypothesis and boundaries as starting input.

Define what this epic accomplishes:
- **Objective**: Business/user outcome (1-2 sentences, outcome-focused)
- **Value**: Why this matters, what's unlocked after completion
- **In scope (MUST/SHOULD)**: Non-negotiable vs nice-to-have deliverables
- **Out of scope**: Excluded items with rationale and deferral destination

Scoping heuristic: defer what doesn't block the objective; separate what needs its own ADRs.

<verification>
Objective explainable to non-technical stakeholder in 60 seconds. Scope boundaries explicit.
</verification>

### Step 2: Assess Architecture & ADRs

```bash
rai graph context mod-<name>
```

Create ADRs when: multiple valid approaches with significant impact, new technology adoption, decisions other epics depend on. Skip when patterns are established or details are easily changed.

If significant uncertainty: `/rai-research` (timebox 2-4 hours), then create ADRs.
ADR template: `.raise/templates/architecture/adr.md`. One decision per ADR.

<verification>
Technical direction clear enough to define stories. ADRs created for significant decisions.
</verification>

### Step 3: Break Down Stories

Decompose epic into 3-10 independently deliverable stories.

**Per story:** ID (S{N}.{seq}), name, 1-line description, T-shirt size (XS/S/M/L), dependencies.

Target: each story delivers demonstrable value, 1-5 days duration. No dependency cycles. External blockers identified.

<verification>
Each story passes "independently deliverable" test. Dependency graph is acyclic.
</verification>

### Step 4: Define Done & Risks

**Done:** All stories complete + epic-specific measurable criteria + architecture docs updated + retrospective completed.

**Risks:** Top 3 with likelihood/impact/mitigation.

<verification>
Done criteria are measurable. Top risks have mitigations.
</verification>

### Step 5: Write Artifacts & Parking Lot

Create TWO documents using templates:
1. `scope.md` (WHAT + WHY): objective, stories, boundaries, done criteria → `templates/scope.md`
2. `design.md` (HOW): Gemba, target components, key contracts → `templates/design.md`

For simple epics (no architecture changes), `design.md` is optional.

Capture deferred items in `dev/parking-lot.md` with origin, priority, and promotion conditions.

<verification>
Scope document reviewable in <10 minutes. Parking lot updated.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Scope document | `work/epics/e{N}-{name}/scope.md` |
| Design document | `work/epics/e{N}-{name}/design.md` (if architecture) |
| ADRs | `dev/decisions/adr-*.md` (0-3 typical) |
| Parking lot | `dev/parking-lot.md` |
| Next | `/rai-epic-plan` |

## Quality Checklist

- [ ] Epic Brief consumed as input (if exists from `/rai-epic-start`)
- [ ] Objective is outcome-focused, not implementation-focused
- [ ] Scope boundaries explicit (in/out documented)
- [ ] Stories independently deliverable (3-10 range)
- [ ] Dependencies mapped with no cycles
- [ ] Done criteria are measurable
- [ ] NEVER time-box epics — scope-based, not duration-based
- [ ] NEVER over-specify stories — save details for `/rai-story-design`

## References

- Brief template: `rai-epic-start/templates/brief.md`
- Scope template: `templates/scope.md`
- Design template: `templates/design.md`
- ADR template: `.raise/templates/architecture/adr.md`
- Next: `/rai-epic-plan`
- Story design: `/rai-story-design`
- Close: `/rai-epic-close`
