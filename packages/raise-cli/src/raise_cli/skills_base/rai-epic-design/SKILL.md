---
name: rai-epic-design
description: Design epic scope, stories, and architecture. Use for work spanning 3-10 features.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "3"
  raise.prerequisites: project-backlog
  raise.next: epic-plan
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.3.0"
  raise.visibility: public
  raise.inputs: |
    - brief: file_path, optional, previous_skill
    - scope: file_path, required, previous_skill
  raise.outputs: |
    - scope: file_path, next_skill
    - design: file_path, optional, next_skill
  raise.aspects: introspection
  raise.introspection:
    phase: epic.design
    context_source: problem brief or strategic objective
    affected_modules: []
    max_tier1_queries: 3
    max_jit_queries: 5
    tier1_queries:
      - "patterns for {affected_modules} architecture decisions"
      - "risks and failure modes in {domain} epics"
      - "prior epic designs with similar scope ({story_count} stories)"
---

# Epic Design

## Purpose

Design an epic that bridges strategic objectives to executable stories, making key architectural decisions and defining bounded scope for incremental delivery.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, create full scope document and ADRs
- **Ha/Ri**: Adjust depth based on complexity, lightweight ADRs, custom patterns

## Context

**When to use:** Starting work spanning 3-10 stories. Design is the gemba walk at epic scale — go see what exists, challenge assumptions, prevent waste.

**When to skip:** Single-story work → `/rai-story-design`. Bug fixes → issue tracker. High uncertainty → `/rai-research` first.

**Inputs:** Business objective, project backlog, constraints. Optionally: Problem Brief from `/rai-problem-shape` or Epic Brief from `/rai-epic-start`.

## Steps

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: No chain read — epic-design is the first skill in the epic chain.
2. **Graph query**: Execute tier1 queries from this skill's metadata using `rai graph query`. If graph is unavailable, note and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Load Brief & Frame Objective

Check for Epic Brief (`work/epics/e{N}-{name}/brief.md`) or Problem Brief (`work/problem-briefs/*.md`). If found, use hypothesis and boundaries as starting input.

Define what this epic accomplishes:
- **Objective**: Business/user outcome (1-2 sentences, outcome-focused)
- **Value**: Why this matters, what's unlocked after completion
- **In scope (MUST/SHOULD)**: Non-negotiable vs nice-to-have deliverables
- **Out of scope**: Excluded items with rationale and deferral destination

Scoping heuristic: defer what doesn't block the objective; separate what needs its own ADRs.

> **JIT**: Before defining scope boundaries, query graph for prior designs with similar scope
> → `aspects/introspection.md § JIT Protocol`

<verification>
Objective explainable to non-technical stakeholder in 60 seconds. Scope boundaries explicit.
</verification>

### Step 2: Gemba Walk (mandatory — do not skip)

Go to the actual codebase. Read what exists before designing what's next.

1. **Read the modules** this epic will touch. Understand current state, not just the graph abstraction.
2. **Search for existing implementations**: grep for similar functionality, patterns, components. Before proposing new stories, verify they won't duplicate what exists.
3. **Check established patterns**: how does the codebase already solve similar problems? Follow existing patterns rather than inventing new ones.
4. **Map the real dependencies**: what actually imports what? What breaks if you change X?

```bash
rai graph context mod-<name>     # graph view
grep -r "similar_pattern" packages/  # real code
```

| Finding | Action |
|---------|--------|
| Similar component exists | Reuse or extend — do NOT propose a duplicate story |
| Established pattern found | Follow it — consistency > novelty |
| Over-engineered existing code | Consider a simplification story instead of building on top |

<verification>
Actual code read. No duplicate components will be proposed. Existing patterns identified.
</verification>

### Step 3: Assess Architecture & ADRs

Create ADRs when: multiple valid approaches with significant impact, new technology adoption, decisions other epics depend on. Skip when patterns are established or details are easily changed.

> **JIT**: Before making architectural decisions, query graph for patterns and known risks
> → `aspects/introspection.md § JIT Protocol`

If significant uncertainty: `/rai-research` (timebox 2-4 hours), then create ADRs.
ADR template: `.raise/templates/architecture/adr.md`. One decision per ADR.

<verification>
Technical direction clear enough to define stories. ADRs created for significant decisions.
</verification>

### Step 4: Break Down Stories (MVP mentality)

Decompose epic into 3-10 independently deliverable stories. Apply lean principles:

- **KISS**: Each story does one thing well. If explanation takes >2 sentences, split it.
- **YAGNI**: Only stories that serve the stated objective. "Nice to have" goes to parking lot.
- **DRY**: Check gemba findings — if a story duplicates existing functionality, remove or reframe as extension.
- **Everything is an MVP**: Each story delivers the simplest version that proves value. Gold-plating goes to follow-up epics.

**Per story:** ID (S{N}.{seq}), name, 1-line description, T-shirt size (XS/S/M/L), dependencies.

> **JIT**: Before finalizing decomposition, query graph for sizing patterns in similar epics
> → `aspects/introspection.md § JIT Protocol`

Target: each story delivers demonstrable value, 1-5 days duration. No dependency cycles. External blockers identified.

**Waste check**: For each proposed story, ask: "What happens if we don't build this?" If the epic still achieves its objective, the story is not essential — defer it.

<verification>
Each story passes "independently deliverable" test. Dependency graph is acyclic. No story duplicates existing functionality.
</verification>

### Step 5: Define Done & Risks

**Done:** All stories complete + epic-specific measurable criteria + architecture docs updated + retrospective completed.

**Risks:** Top 3 with likelihood/impact/mitigation.

> **JIT**: Before assessing risks, query graph for known risks from related epics
> → `aspects/introspection.md § JIT Protocol`

<verification>
Done criteria are measurable. Top risks have mitigations.
</verification>

### Step 6: Write Artifacts & Parking Lot

Create TWO documents using templates:
1. `scope.md` (WHAT + WHY): objective, stories, boundaries, done criteria → `templates/scope.md`
2. `design.md` (HOW): gemba findings, target components, key contracts → `templates/design.md`

Both documents are required. For simple epics, `design.md` is short (gemba findings + approach), not absent.

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
- [ ] Gemba walk done — actual code read, no duplicate components proposed
- [ ] Objective is outcome-focused, not implementation-focused
- [ ] Scope boundaries explicit (in/out documented)
- [ ] Lean principles applied: KISS, DRY, YAGNI, MVP mentality
- [ ] Waste check: every story is essential for the objective
- [ ] Stories independently deliverable (3-10 range)
- [ ] Dependencies mapped with no cycles
- [ ] Done criteria are measurable
- [ ] Both scope.md and design.md produced (design.md is never optional)
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
