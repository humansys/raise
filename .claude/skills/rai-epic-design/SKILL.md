---
name: rai-epic-design
description: >
  Design an epic from strategic objective to feature breakdown. Use when
  starting a new body of work spanning multiple features (3-10), requiring
  architectural decisions, or when establishing technical direction for
  significant capability delivery.

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "3"
  raise.prerequisites: project-backlog
  raise.next: epic-plan
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"
  raise.visibility: public
---

# Epic Design

## Purpose

Design an epic that bridges strategic objectives to executable stories, making key architectural decisions and defining bounded scope for incremental delivery.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, create full scope document and ADRs
- **Ha**: Adjust depth based on epic complexity, lightweight ADRs for simpler decisions
- **Ri**: Custom epic patterns, integrate with portfolio management

## Context

**When to use:** Starting work spanning 3-10 stories, requiring architectural decisions, or establishing technical direction.

**When to skip:** Single-story work → `/rai-story-design`. Bug fixes → issue tracker. High uncertainty → `/rai-research` first.

**Inputs:** Business objective, project backlog, constraints (timeline, dependencies). Optionally: Problem Brief from `/rai-problem-shape`.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

### Step 1: Frame Objective & Scope

Check for a Problem Brief (`work/problem-briefs/*.md`) — if found, use as pre-populated input.

Define what this epic accomplishes:
- **Objective**: Business/user outcome (1-2 sentences, outcome-focused not implementation-focused)
- **Value**: Why this matters, what's unlocked after completion
- **In scope (MUST/SHOULD)**: Non-negotiable vs nice-to-have deliverables
- **Out of scope**: Excluded items with rationale and deferral destination

| Heuristic | Action |
|-----------|--------|
| Can be deferred without blocking objective | Out of scope |
| Another epic depends on it | In scope |
| Requires separate architectural decisions | Consider separate epic |

<verification>
Objective explainable to non-technical stakeholder in 60 seconds. Scope boundaries are explicit.
</verification>

### Step 2: Assess Architecture & ADRs

Load architectural context for affected modules:

```bash
rai graph context mod-<name>
```

**Assessment:** Does this epic introduce new patterns? Multiple valid approaches? Cross-epic impact? Significant uncertainty?

If yes to any: conduct spike or `/rai-research` (timebox 2-4 hours), then create ADRs.

| Create ADR when | Skip ADR when |
|-----------------|---------------|
| Multiple valid approaches with significant impact | Standard patterns already established |
| New technology/pattern adoption | Implementation details easily changed |
| Decisions other epics depend on | Obvious best choice |

ADR template: `.raise/templates/architecture/adr.md`. One decision per ADR.

<verification>
Technical direction clear enough to define stories. ADRs created for significant decisions.
</verification>

### Step 3: Break Down Stories

Decompose epic into 3-10 independently deliverable stories.

**Per story, capture:** ID (S{N}.{seq}), name, 1-line description, T-shirt size (XS/S/M/L), dependencies.

| Heuristic | Target |
|-----------|--------|
| Each story delivers demonstrable value | Can be demoed |
| Story duration | 1-5 days |
| Mix | ~2-3 foundation + ~4-6 core + ~1-2 polish |
| Dependencies | Map critical path, identify parallel tracks |

**Dependency check:** No cycles. External blockers identified.

<verification>
Each story passes "independently deliverable" test. Dependency graph is acyclic.
</verification>

### Step 4: Define Done & Risks

**Epic done criteria:**
- All stories complete
- Epic-specific success criteria (measurable)
- Architecture docs updated
- Epic retrospective completed

**Top risks** (3 max, with likelihood/impact/mitigation):

| Risk | L/I | Mitigation |
|------|:---:|------------|
| {risk} | H/M | {strategy} |

<verification>
Done criteria are measurable. Top risks have mitigations.
</verification>

### Step 5: Write Scope Document & Parking Lot

Create `work/epics/e{N}-{name}/scope.md` using `templates/scope.md`. Consolidate all design work.

Capture deferred items in `dev/parking-lot.md` with origin, priority, and promotion conditions.

<verification>
Scope document reviewable in <10 minutes. Parking lot updated.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Scope document | `work/epics/e{N}-{name}/scope.md` |
| ADRs | `dev/decisions/adr-*.md` (0-3 typical) |
| Parking lot | `dev/parking-lot.md` |
| Next | `/rai-epic-plan` |

## Quality Checklist

- [ ] Objective is outcome-focused, not implementation-focused
- [ ] Scope boundaries explicit (in/out documented)
- [ ] Stories are independently deliverable (3-10 range)
- [ ] Dependencies mapped with no cycles
- [ ] Done criteria are measurable
- [ ] Scope document uses `templates/scope.md`
- [ ] NEVER time-box epics — scope-based, not duration-based
- [ ] NEVER over-specify stories — save details for `/rai-story-design`

## References

- Scope template: `templates/scope.md`
- ADR template: `.raise/templates/architecture/adr.md`
- Next: `/rai-epic-plan`
- Story design: `/rai-story-design`
- Close: `/rai-epic-close`
