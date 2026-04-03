---
name: rai-epic-plan
description: Sequence epic stories into milestones and dependencies. Use after epic design.

allowed-tools:
  - Read
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "4"
  raise.prerequisites: epic-design
  raise.next: story-start
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.3.0"
  raise.visibility: public
  raise.inputs: |
    - scope: file_path, required, previous_skill
  raise.outputs: |
    - scope: file_path, next_skill
  raise.aspects: introspection
  raise.introspection:
    phase: epic.plan
    context_source: scope doc from epic-design
    affected_modules: []
    max_tier1_queries: 3
    max_jit_queries: 3
    tier1_queries:
      - "sequencing patterns for {strategy} ordering"
      - "estimation patterns for {size} epics"
      - "milestone patterns for multi-story epics"
---

# Epic Plan

## Purpose

Transform the story list from `/rai-epic-design` into a sequenced implementation plan with milestones, parallel work streams, and progress tracking.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, create sequenced plan with walking skeleton + MVP milestones
- **Ha**: Adjust milestone granularity based on epic size, skip timeline for small epics
- **Ri**: Domain-specific sequencing patterns, team velocity models

## Context

**When to use:** After `/rai-epic-design` has produced a scope document with stories. Before starting first story.

**When to skip:** Very small epics (2-3 stories) with obvious linear sequence. Emergency fixes.

**Inputs:** Epic scope document (`work/epics/e{N}-{name}/scope.md`), calibration data (if available).

## Steps

> **PRIME**: Before Step 1, follow PRIME protocol in `aspects/introspection.md`.
> Chain read: read epic-design's learning record at `.raise/rai/learnings/rai-epic-design/{work_id}/record.yaml`.
> Enrich epic-design's record with `downstream: {scope_clear: bool, stories_sequenceable: bool}`.

### Step 1: Review Epic Scope

Load and understand the epic scope document:
- Story list with sizes and dependencies
- Done criteria and risks
- Architectural decisions that affect sequencing

<verification>
Can explain epic scope and story dependencies in 60 seconds.
</verification>

<if-blocked>
Epic design incomplete → run `/rai-epic-design` first.
</if-blocked>

### Step 2: Sequence & Rationalize

Order stories using these strategies (in priority order):

| Strategy | When | Rationale |
|----------|------|-----------|
| **Risk-first** | High uncertainty features | Tackle unknowns early while energy is high and time for pivots remains |
| **Walking skeleton** | Architecture unproven | Build minimal E2E path first to prove architecture |
| **Quick wins** | Need momentum | Early deliverable value, validate tooling |
| **Dependency-driven** | Hard blockers exist | Unblock others on critical path |

For each story, document: position, rationale, dependencies (hard/soft/external), what it enables.

> **JIT**: Before choosing sequencing strategy, query graph for ordering patterns and calibration data
> → `aspects/introspection.md § JIT Protocol`

**Identify parallel opportunities:** Stories with no mutual dependencies, different codebase areas, or independent concerns can run concurrently.

<verification>
Every story has sequencing rationale. Critical path identified. Parallel opportunities documented.
</verification>

### Step 3: Define Milestones

Create 2-4 intermediate checkpoints:

| Milestone | Typical scope | Purpose |
|-----------|---------------|---------|
| **M1: Walking Skeleton** | 1-3 stories (smallest E2E) | Prove architecture, enable integration |
| **M2: Core MVP** | 50-70% of stories | Demonstrate value, gather feedback |
| **M3: Feature Complete** | 100% planned stories | Ready for polish |
| **M4: Epic Complete** | Done criteria met | Ready for `/rai-epic-close` |

Per milestone: stories included, success criteria (verifiable), demo capability.

> **JIT**: Before defining milestones, query graph for calibration patterns and checkpoint strategies
> → `aspects/introspection.md § JIT Protocol`

**Integration checkpoint:** For epics with multiple components (client/server, CLI/API, frontend/backend), schedule an **E2E integration milestone** before the final story. This checkpoint runs real infrastructure (docker compose, actual DB) and verifies cross-story contracts (auth headers, payload schemas, parameter limits). Unit tests with mocks cannot catch these mismatches — only real E2E validates the seams between stories.

<verification>
At least 2 milestones defined with clear success criteria. Multi-component epics include E2E integration checkpoint.
</verification>

### Step 4: Setup Tracking

Add progress tracking to epic scope using `templates/plan-section.md`:
- Story sequence table with status/actual/velocity columns
- Milestone checklist with target dates
- Velocity assumptions from calibration data (if available)

<verification>
Tracking table added to epic scope document.
</verification>

### Step 5: Update Scope Document

Append the implementation plan section to `work/epics/e{N}-{name}/scope.md`. Include:
- Story sequence with rationale
- Milestones with success criteria
- Parallel work streams (if any)
- Progress tracking table
- Sequencing risks (top 3)

Present plan to human for review before starting first story.

<verification>
Scope document updated. Plan reviewable in <5 minutes. Human acknowledges.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Implementation plan | Appended to `work/epics/e{N}-{name}/scope.md` |
| Plan template | `templates/plan-section.md` |
| Next | `/rai-story-design` for first story in sequence |

> **LEARN**: After completing Step 5, follow LEARN protocol in `aspects/introspection.md`.
> Record path: `.raise/rai/learnings/rai-epic-plan/{work_id}/record.yaml`

## Quality Checklist

- [ ] All stories sequenced with rationale
- [ ] Critical path identified
- [ ] At least 2 milestones (walking skeleton + MVP minimum)
- [ ] Dependencies verified — no cycles, blockers identified
- [ ] Parallel opportunities documented (or explained why sequential)
- [ ] Progress tracking in scope document
- [ ] NEVER over-plan — plans are hypotheses, not commitments
- [ ] NEVER sequence by size alone — use risk-first as default
- [ ] Multi-component epics include E2E integration checkpoint

## References

- Plan template: `templates/plan-section.md`
- Previous: `/rai-epic-design` (produces scope input)
- Next: `/rai-story-design` for first story
- Close: `/rai-epic-close`
- Calibration: `.raise/rai/memory/calibration.jsonl`
