---
name: rai-epic-plan
description: >
  Sequence features from epic-design into an executable plan with milestones,
  dependencies, and progress tracking. Use after /rai-epic-design to create a
  realistic implementation roadmap before starting story work.

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "4"
  raise.prerequisites: epic-design
  raise.next: story-design
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
---

# Plan: Epic Implementation Roadmap

## Purpose

Transform the feature list from `/rai-epic-design` into a sequenced implementation plan with intermediate milestones, parallel work streams, and progress tracking mechanisms. Create a roadmap that maximizes learning, minimizes risk, and enables visible progress.

**Core principle:** Risk early, reward early. Tackle uncertain features first while momentum is high; deliver quick wins to validate approach and build confidence.

**Planning philosophy:** Plans are hypotheses, not commitments. The value is in thinking through sequencing, not in perfect predictions. Adjust as you learn.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps completely; create sequenced feature plan with explicit milestones; define at least one walking skeleton milestone and one MVP milestone.

**Ha (破)**: Adjust milestone granularity based on epic size; combine or skip steps for small epics (<5 features); customize risk assessment based on domain knowledge.

**Ri (離)**: Create domain-specific sequencing patterns; develop team velocity models; integrate with organizational planning rhythms (PI Planning, quarterly goals).

## Context

**When to use:**
- After `/rai-epic-design` has produced a scope document with features
- Before starting first feature implementation
- When features have complex dependencies requiring coordination
- When stakeholders need visibility into progress checkpoints
- When multiple work streams could run in parallel

**When to skip:**
- Very small epics (2-3 features) with obvious linear sequence
- Emergency fixes with single critical path
- Epics already in progress (use for new epics only)

**Inputs required:**
- Epic scope document: `work/epics/e{N}-{name}/scope.md`
- Feature list with sizes and dependencies
- Calibration data (`.raise/rai/memory/calibration.jsonl` if available)
- External constraints (deadlines, dependencies, resource availability)

**Outputs:**
- Updated epic scope document with sequenced plan
- Feature execution order with rationale
- Intermediate milestones (walking skeleton, MVP, complete)
- Progress tracking setup
- Parallel work identification

## Steps

### Step 0: Emit Epic Start (Telemetry)

Record the start of the plan phase:

```bash
rai memory emit-work epic {epic_id} --event start --phase plan
```

**Example:** `rai memory emit-work epic E9 -e start -p plan`

### Step 0.5: Query Context

Load relevant sequencing patterns and calibration from unified context:

```bash
rai memory query "sequencing calibration planning" --types pattern,calibration --limit 5
```

Review returned patterns before proceeding. Calibration data informs realistic estimates.

**Verification:** Context loaded; relevant patterns noted.

> **If context unavailable:** Run `rai memory build` first, or proceed without patterns.

### Step 1: Review Epic Design Output

Load and understand the epic scope before planning.

**Review:**
- Epic objective and value proposition
- Feature list with sizes (T-shirt or SP)
- Dependencies identified in `/rai-epic-design`
- Done criteria (feature and epic level)
- Risks identified

**Capture:**
- Total features and estimated effort
- Key constraints (deadline, external dependencies)
- Architectural decisions that affect sequencing

**Verification:** Can explain the epic scope in 60 seconds.

> **If you can't continue:** Epic design incomplete → Run `/rai-epic-design` first.

---

### Step 2: Identify Critical Path

Determine which features are essential for others to proceed.

**Critical path analysis:**
1. List features that block other features (dependencies)
2. Identify features with external dependencies (APIs, infrastructure)
3. Find features with highest uncertainty or risk
4. Map the longest chain of dependent features

**Dependency types:**
- **Hard:** Cannot start B until A complete (technical requirement)
- **Soft:** B could start early but benefits from A (learning, patterns)
- **External:** Depends on factors outside the epic (APIs, approvals)

**Critical path diagram:**
```
F{N}.1 (foundation) ← CRITICAL PATH START
  ↓
F{N}.2 (core capability)
  ↓
F{N}.3 ──┐
         │ (parallel possible)
F{N}.4 ◄─┘
  ↓
F{N}.5 (integration) ← CRITICAL PATH END
```

**Verification:** Critical path identified with duration estimate.

> **If you can't continue:** Dependencies unclear → Return to `/rai-epic-design` Step 6 (Map Dependencies).

---

### Step 3: Apply Sequencing Strategy

Order features using proven sequencing strategies.

**Primary strategy: Risk-First (Lean principle)**

Tackle the most uncertain features early when:
- Energy and focus are highest
- More time remains for pivots
- Learning can inform later features

**Risk indicators:**
- New technology or unfamiliar patterns
- Integration with external systems
- Unclear requirements (even after design)
- Performance or scalability unknowns

**Secondary strategy: Walking Skeleton**

Build minimal end-to-end functionality first:
- Proves architecture works
- Enables early integration testing
- Provides demo-able progress quickly
- Validates assumptions before heavy investment

**Tertiary strategy: Quick Wins**

Include early features that:
- Build momentum and confidence
- Provide immediate value
- Enable parallel work streams
- Validate tooling and processes

**Sequencing decision matrix:**

| Feature Type | Sequence Position | Rationale |
|--------------|-------------------|-----------|
| High risk, blocking | Early | Reduce uncertainty, unblock others |
| Walking skeleton | Early | Prove architecture, enable integration |
| Quick win, non-blocking | Early-middle | Build momentum, validate process |
| Core functionality | Middle | Build on foundation |
| Polish, optimization | Late | Refinement after core complete |
| External dependency | Based on availability | Coordinate with external timeline |

**Verification:** Each feature has sequencing rationale documented.

> **If you can't continue:** Multiple valid orderings → Choose risk-first as default; document alternatives.

> **Deep dive:** See `_references/sequencing-strategies.md` for detailed philosophy and anti-patterns.

---

### Step 4: Identify Parallel Work Streams

Find opportunities for concurrent work.

**Parallel opportunities:**
- Features with no mutual dependencies
- Features in different parts of the codebase
- Features that can share early patterns/infrastructure
- Research/documentation that doesn't block code

**Parallel constraints:**
- Resource availability (single person = limited parallelism)
- Integration risk (too much parallel work = merge conflicts)
- Context switching cost (AI-assisted work has low switching cost)

**Parallel work diagram:**
```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1: F{N}.1 ─────► F{N}.2 ─────► F{N}.5
                         ↓ enables
Stream 2:              F{N}.3 ─────► merge
                                      ↑
Stream 3:              F{N}.4 ───────┘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Verification:** Parallel opportunities documented with merge points.

> **If you can't continue:** No parallel opportunities → Sequential is valid; document why.

---

### Step 5: Define Milestones

Create intermediate checkpoints for progress visibility.

**Standard milestone pattern:**

| Milestone | Definition | Purpose |
|-----------|------------|---------|
| **M1: Walking Skeleton** | Minimal E2E path through system | Prove architecture, enable integration |
| **M2: Core MVP** | Essential features complete | Demonstrate value, gather feedback |
| **M3: Feature Complete** | All planned features done | Ready for polish/release |
| **M4: Epic Complete** | Done criteria met, retro done | Ready for `/rai-epic-close` |

**For each milestone, define:**
- **Name:** Clear, meaningful label
- **Features included:** Which features must be complete
- **Success criteria:** How to verify milestone reached
- **Demo capability:** What can be shown/tested
- **Feedback opportunity:** What questions can be answered

**Milestone heuristics:**
- Walking Skeleton: 1-3 features (smallest demonstrable value)
- Core MVP: 50-70% of features (enough for meaningful feedback)
- Feature Complete: 100% planned features (polish can follow)

**Milestone template:**
```markdown
### Milestone M{N}: {Name}

**Features included:**
- F{X}.{Y}: {Feature name}
- F{X}.{Z}: {Feature name}

**Success criteria:**
- [ ] {Specific, verifiable criterion}
- [ ] {Specific, verifiable criterion}

**Demo capability:** {What can be demonstrated}

**Feedback questions:**
- {What we want to learn by this milestone}
```

**Verification:** At least 2-3 milestones defined with clear success criteria.

> **If you can't continue:** Milestones unclear → Default to: Walking Skeleton (2 features) → MVP (60% features) → Complete (100%).

---

### Step 6: Estimate Timeline (Optional)

Map features to time periods if deadline exists.

**Timeline estimation approach:**

1. **Reference calibration data:** Use `.claude/rai/calibration.md` for velocity
2. **Apply velocity multiplier:** Kata cycle = 2-3x faster than traditional estimates
3. **Add buffer:** 20-30% buffer for unknowns, integration, polish
4. **Back-calculate from deadline:** Work backward from external dates

**Timeline mapping:**

| Period | Features | Milestone | Cumulative |
|--------|----------|-----------|------------|
| Day 1-2 | F{N}.1, F{N}.2 | M1: Walking Skeleton | 30% |
| Day 3-4 | F{N}.3, F{N}.4 | - | 60% |
| Day 5-6 | F{N}.5 | M2: Core MVP | 80% |
| Day 7-8 | F{N}.6, F{N}.7 | M3: Feature Complete | 100% |
| Day 9 | Integration, polish | M4: Epic Complete | Done |

**Velocity assumptions (based on calibration):**

| Feature Size | Without Kata | With Full Kata Cycle |
|--------------|--------------|---------------------|
| XS | 1-2 hours | 20-40 min |
| S | 2-4 hours | 40-90 min |
| M | 4-8 hours | 1.5-3 hours |
| L | 8-16 hours | 3-6 hours |

**Verification:** Timeline fits constraints, or scope adjusted.

> **If you can't continue:** No deadline → Skip detailed timeline; use milestones for progress.

---

### Step 7: Plan Progress Tracking

Define how progress will be measured and communicated.

**Tracking mechanisms:**

1. **Feature completion:** Simple checklist (most reliable)
2. **Milestone achievement:** Binary checkpoints (good for stakeholders)
3. **Burndown:** Story points over time (useful for trending)
4. **Time tracking:** Actual vs estimated (calibration data)

**Recommended approach (RaiSE):**

```markdown
## Progress Tracking

| Feature | Size | Status | Actual Time | Notes |
|---------|:----:|:------:|:-----------:|-------|
| F{N}.1 | S | ✓ | 45 min | - |
| F{N}.2 | M | ✓ | 2h | - |
| F{N}.3 | S | IN PROGRESS | - | Started Day 3 |
| F{N}.4 | S | Pending | - | - |

**Milestones:**
- [x] M1: Walking Skeleton (Day 2) ✓
- [ ] M2: Core MVP (Day 5)
- [ ] M3: Feature Complete (Day 7)
- [ ] M4: Epic Complete (Day 9)

**Velocity:** {X.Y}x average (updated per story)
```

**Tracking cadence:**
- Update after each story completion
- Milestone check at end of each day/session
- Velocity recalculation after 3+ features

**Verification:** Tracking table added to epic scope document.

> **If you can't continue:** Tracking seems overhead → Minimum = feature checklist + milestone dates.

---

### Step 8: Document Sequencing Rationale

Capture why features are ordered this way for future reference.

**For each story, note:**
- Position rationale (why this order?)
- Dependencies (what does it need? what does it enable?)
- Risk factors (what could go wrong?)
- Parallel opportunity (can it run with others?)

**Rationale template:**
```markdown
## Feature Sequencing Rationale

### F{N}.1: {Feature Name}
- **Position:** First
- **Rationale:** Foundation required by all other features
- **Dependencies:** None
- **Enables:** F{N}.2, F{N}.3, F{N}.4
- **Risk:** Low (well-understood pattern)
- **Parallel:** No (blocking)

### F{N}.2: {Feature Name}
- **Position:** Second (after F{N}.1)
- **Rationale:** Core capability, validates architecture
- **Dependencies:** F{N}.1
- **Enables:** F{N}.5
- **Risk:** Medium (new integration)
- **Parallel:** No (on critical path)
```

**Verification:** Sequencing rationale documented for each story.

> **If you can't continue:** Rationale obvious → Brief notes sufficient; don't over-document.

---

### Step 9: Identify Risks and Mitigations

Review risks with sequencing lens.

**Sequencing-specific risks:**

| Risk Type | Example | Mitigation |
|-----------|---------|------------|
| **Blocker risk** | Foundation feature harder than expected | Early start, timebox spike |
| **Integration risk** | Parallel streams conflict at merge | Plan integration points |
| **Velocity risk** | First features slower than expected | Build in buffer, adjust after |
| **External risk** | API not ready when needed | Sequence dependent features later |

**Risk-based sequencing adjustments:**
- High-risk feature early → More time for recovery
- External dependency mid-epic → Plan fallback path
- Integration complexity → Reduce parallel streams

**Verification:** Top 3 sequencing risks identified with mitigations.

> **If you can't continue:** Risks identified in `/rai-epic-design` → Reference those; add sequencing-specific risks.

---

### Step 10: Update Epic Scope Document

Add planning outputs to the scope document.

**Sections to add:**

```markdown
## Implementation Plan

### Feature Sequence

| Order | Feature | Size | Dependencies | Milestone | Notes |
|:-----:|---------|:----:|--------------|-----------|-------|
| 1 | F{N}.1 | S | None | M1 | Foundation |
| 2 | F{N}.2 | M | F{N}.1 | M1 | Core capability |
| 3 | F{N}.3 | S | F{N}.2 | M2 | Can parallel with F{N}.4 |
| 4 | F{N}.4 | S | F{N}.1 | M2 | Can parallel with F{N}.3 |
| 5 | F{N}.5 | S | F{N}.3, F{N}.4 | M3 | Integration |

### Milestones

| Milestone | Features | Target | Success Criteria |
|-----------|----------|--------|------------------|
| M1: Walking Skeleton | F{N}.1, F{N}.2 | Day 2 | E2E path works |
| M2: Core MVP | +F{N}.3, F{N}.4 | Day 5 | Demo-able value |
| M3: Feature Complete | +F{N}.5 | Day 7 | All features done |
| M4: Epic Complete | - | Day 9 | Done criteria met |

### Parallel Opportunities

- **Stream 1:** F{N}.1 → F{N}.2 → F{N}.5 (critical path)
- **Stream 2:** F{N}.3, F{N}.4 (after F{N}.1, parallel with Stream 1)

### Progress Tracking

| Feature | Size | Status | Actual Time | Notes |
|---------|:----:|:------:|:-----------:|-------|
| F{N}.1 | S | Pending | - | - |
| F{N}.2 | M | Pending | - | - |
| ... | ... | ... | ... | ... |
```

**Verification:** Epic scope document updated with planning sections.

> **If you can't continue:** Scope doc not found → Create minimal planning section in appropriate location.

---

### Step 11: Validate Plan

Self-review checklist before starting implementation.

**Plan validation:**
- [ ] All features sequenced with rationale
- [ ] Critical path identified
- [ ] At least 2 milestones defined (Walking Skeleton + MVP minimum)
- [ ] Dependencies verified (no cycles, blockers identified)
- [ ] Parallel opportunities documented (or explained why sequential)
- [ ] Progress tracking setup in scope document
- [ ] Top risks have mitigation strategies
- [ ] Timeline fits deadline (if applicable)

**Validation questions:**
1. Could someone else start implementation from this plan?
2. Is the first feature clear and unblocked?
3. Are milestones meaningful (not just arbitrary splits)?
4. Does the plan reflect what we learned in `/rai-epic-design`?

**Verification:** All validation checkboxes checked.

> **If you can't continue:** Validation fails → Address gaps before starting implementation.

---

### Step 12: Emit Epic Complete (Telemetry)

Record the completion of the plan phase:

```bash
rai memory emit-work epic {epic_id} --event complete --phase plan
```

**Example:** `rai memory emit-work epic E9 -e complete -p plan`

---

## Output

- **Primary:** `work/epics/e{N}-{name}/scope.md` — updated with implementation plan
- **Sections added:** Feature sequence, milestones, parallel opportunities, progress tracking
- **Next:** `/rai-story-design` for first feature in sequence

## Implementation Plan Template

Add to epic scope document:

```markdown
---

## Implementation Plan

> Added by `/rai-epic-plan` - YYYY-MM-DD

### Feature Sequence

| Order | Feature | Size | Dependencies | Milestone | Rationale |
|:-----:|---------|:----:|--------------|-----------|-----------|
| 1 | F{N}.1 | {S} | None | M1 | {Why first?} |
| 2 | F{N}.2 | {M} | F{N}.1 | M1 | {Why second?} |
| 3 | F{N}.3 | {S} | F{N}.2 | M2 | {Why here?} |
| ... | ... | ... | ... | ... | ... |

### Milestones

| Milestone | Features | Target | Success Criteria | Demo |
|-----------|----------|--------|------------------|------|
| **M1: Walking Skeleton** | F{N}.1, F{N}.2 | {Date/Day} | {What proves it works?} | {What can be shown?} |
| **M2: Core MVP** | +F{N}.3, F{N}.4 | {Date/Day} | {What proves value?} | {What feedback to gather?} |
| **M3: Feature Complete** | +F{N}.5... | {Date/Day} | All planned features done | Full capability demo |
| **M4: Epic Complete** | - | {Date/Day} | Done criteria met | `/rai-epic-close` ready |

### Parallel Work Streams

```
Time →
Stream 1 (Critical): F{N}.1 ─► F{N}.2 ─► F{N}.5
                              ↓
Stream 2 (Parallel):        F{N}.3 ─► merge
                                       ↑
Stream 3 (Parallel):        F{N}.4 ───┘
```

**Merge points:**
- After F{N}.1: Split into parallel streams
- Before F{N}.5: Merge parallel streams

### Progress Tracking

| Feature | Size | Status | Actual | Velocity | Notes |
|---------|:----:|:------:|:------:|:--------:|-------|
| F{N}.1 | S | Pending | - | - | |
| F{N}.2 | M | Pending | - | - | |
| F{N}.3 | S | Pending | - | - | |
| ... | ... | ... | ... | ... | |

**Milestone Progress:**
- [ ] M1: Walking Skeleton ({target date})
- [ ] M2: Core MVP ({target date})
- [ ] M3: Feature Complete ({target date})
- [ ] M4: Epic Complete ({target date})

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| {Risk 1} | {H/M/L} | {H/M/L} | {Strategy} |
| {Risk 2} | {H/M/L} | {H/M/L} | {Strategy} |

### Velocity Assumptions

- **Baseline:** {X.Y}x multiplier with kata cycle (from calibration)
- **Adjustment:** {Any epic-specific factors}
- **Buffer:** {20-30%} for integration/polish

---

*Plan created: YYYY-MM-DD*
*Next: `/rai-story-design` for F{N}.1*
```

## Quality Standards

| Metric | Target |
|--------|--------|
| Planning time | <1 hour for typical epic |
| Plan reviewable | <5 minutes to understand sequence |
| Milestones per epic | 2-4 (Walking Skeleton + MVP minimum) |
| Sequencing rationale | 1-2 sentences per story |
| Risk coverage | Top 3 sequencing risks addressed |

## Common Pitfalls

1. **Over-planning** — Detailed hour-by-hour schedules that become obsolete immediately
2. **Ignoring risk** — Sequencing by size instead of uncertainty; save risky features for last
3. **No walking skeleton** — Jumping to complex features without proving architecture works
4. **Milestone-free** — No intermediate checkpoints; progress invisible until end
5. **Ignoring parallel opportunities** — Sequential when parallel is possible (especially with AI-assisted work)
6. **Timeline without buffer** — Every hour accounted for; no room for learning
7. **Planning without calibration** — Estimates based on intuition instead of measured velocity
8. **Sunk cost sequencing** — "We already started X, so finish it" instead of re-evaluating

## Integration with Memory Model

This skill supports the three-layer memory model:

**Identity Layer (always loaded):** Core values guide sequencing decisions (risk-first, lean principles)

**Memory Layer (MVC queryable):**
- Past epic patterns inform sequencing
- Calibration data enables realistic estimates
- Process learnings (what worked before)

**Long-term Layer (on-demand):**
- Historical velocity trends
- Similar epic comparisons

**Update memory after planning:**
- Note sequencing decisions in session log
- Capture velocity assumptions for calibration
- Document novel sequencing patterns

## References

- **Epic Design:** `/rai-epic-design` (produces input for this skill)
- **Epic Scope Examples:** `work/epics/e01-foundation/scope.md`, `work/epics/e02-governance/scope.md`
- **Feature Planning:** `/rai-story-plan` (similar concept at story level)
- **Epic Close:** `/rai-epic-close` (retrospective after completion)
- **Calibration Data:** `.raise/rai/memory/calibration.jsonl` (velocity patterns)
- **Constitution:** `framework/reference/constitution.md` (Lean principles)
- **Guardrails:** `governance/guardrails.md` (quality standards)

## External References

- [Walking Skeleton - Product Manager's Guide](https://fibery.com/blog/product-management/walking-skeleton/)
- [Epic Implementation Strategies - Scaled Agile](https://framework.scaledagile.com/implementation-strategies-for-business-epics)
- [Milestones for Agile Project Management](https://medium.com/agile-adapt/milestones-for-agile-project-management-6fcaa27b255e)
- [Master Agile Projects with Epics and Milestones](https://lukepivac.com/2025/04/28/mastering-agile-projects-the-power-of-epics-and-milestones/)

## Relationship to Other Skills

```
Project Level
    ↓
/rai-epic-design   ← Scope, features, ADRs
    ↓
/rai-epic-plan     ← YOU ARE HERE (sequence, milestones, tracking)
    ↓
/rai-story-design → /rai-story-plan → /rai-story-implement → /rai-story-review
    ↓
/rai-epic-close    ← Retrospective, learnings
```

**From `/rai-epic-design`:** Receives feature list with sizes, dependencies, risks
**To `/rai-story-design`:** Provides sequenced list, identifies first feature to start

---

**Status:** Active
**Version:** 1.0.0
**Created:** 2026-02-01
**Author:** Rai + Emilio
