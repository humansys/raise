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
  raise.version: "1.0.0"
---

# Design: Epic Specification

## Purpose

Design an epic that bridges strategic objectives to executable features. Create the architectural foundation, make key technical decisions, and define a bounded scope that can be delivered incrementally.

**Core principle:** Epics define vision and direction; features deliver increments. An epic is **scope-based, not time-based** — trying to squeeze an epic into a fixed period defeats its purpose.

**Design philosophy:** "Lean and sufficient" — document enough to provide useful context, start minimal, augment as needed. Comprehensive documentation increases failure risk; concise overviews enable action.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps completely; create epic scope document and required ADRs; break down into 3-10 features with clear boundaries.

**Ha (破)**: Adjust depth based on epic complexity; skip optional sections for straightforward epics; create lightweight ADRs for simpler decisions.

**Ri (離)**: Create custom epic patterns for specific domains; develop organization-specific scope templates; integrate with portfolio management practices.

## Context

**When to use:**
- Starting a new body of work spanning multiple features (typically 3-10)
- When architectural decisions need to be made before implementation
- When establishing technical direction for a significant capability
- After project backlog exists but before feature-level planning
- When multiple features need coordination or share dependencies

**When to skip:**
- Single-story work (go directly to `/rai-story-design`)
- Bug fixes or maintenance (use issue tracker)
- Infrastructure tasks with obvious implementation
- Exploratory spikes (use `/rai-research` skill first)

**Inputs required:**
- Project backlog with candidate features
- Solution vision (if exists)
- Technical design/architecture context (if exists)
- Business objective or outcome this epic serves
- Constraints (timeline, resources, dependencies)

**Outputs:**
- Epic scope document: `work/epics/e{N}-{name}/scope.md`
- ADRs for significant architectural decisions (`dev/decisions/adr-*.md`)
- Feature list with sizes, dependencies, and sequencing
- Updated parking lot with deferred items

## Steps

### Step 0: Emit Epic Start (Telemetry)

Record the start of the design phase:

```bash
rai memory emit-work epic {epic_id} --event start --phase design
```

**Example:** `rai memory emit-work epic E9 -e start -p design`

### Step 0.5: Query Context

Load relevant architecture decisions and prior epic patterns from unified context:

```bash
rai memory query "architecture ADR epic" --types pattern,decision --limit 5
```

Review returned patterns and prior ADRs before proceeding. Prior architectural decisions inform scope decisions.

**What this returns:**
- Learned patterns from prior epics
- Prior architectural decisions (ADRs) relevant to this epic

**Verification:** Context loaded; relevant patterns noted.

> **If context unavailable:** Run `rai memory build` first, or proceed without patterns.

### Step 0.6: Load Architectural Context

For each candidate module the epic might touch, load its architectural context:

```bash
rai memory context mod-<name>
# Example: rai memory context mod-memory
```

**How to identify the relevant module(s):**
- From the epic objective: which source modules will this epic affect?
- Module names use `mod-` prefix (e.g., `mod-memory`, `mod-graph`, `mod-session`)
- Epics typically span multiple modules — query each one
- Focus on modules in the critical path first

**What this returns (per module):**
- **Bounded context:** Which domain this module belongs to
- **Layer:** Architecture layer (leaf, domain, integration, orchestration)
- **Constraints:** Applicable guardrails (MUST and SHOULD)
- **Dependencies:** What this module depends on and what depends on it

**How to use the context in epic design:**
- Map which bounded contexts the epic spans — cross-domain work needs explicit justification
- Identify layer boundaries the epic crosses — inform feature decomposition
- Collect MUST constraints across all affected modules — include in epic done criteria
- Use dependency information to inform feature sequencing
- Present an "Architectural Context" section in the epic scope summarizing affected domains, layers, and key constraints

**If module not found:** The module may not be in the graph yet. Continue without architectural context but note the gap.

**Verification:** Architectural context loaded for key modules OR gaps noted.

### Step 1: Frame the Epic Objective

Define what this epic accomplishes at a strategic level.

**Capture:**
- **Objective**: What business/user outcome does this epic deliver? (1-2 sentences)
- **Value proposition**: Why does this matter? What's unlocked after completion?
- **Success criteria**: How will we know the epic succeeded? (measurable outcomes)

**Quality criteria:**
- Objective is outcome-focused, not implementation-focused
- Value is traceable to solution vision or business case
- Success criteria are measurable or clearly observable

**Verification:** Objective can be explained to a non-technical stakeholder in 60 seconds.

> **If you can't continue:** Objective unclear → Escalate to project/solution level for clarification.

---

### Step 2: Define Scope Boundaries

Establish what's in and out of scope to prevent scope creep.

**Document:**
- **In Scope (MUST)**: Non-negotiable deliverables required for epic completion
- **In Scope (SHOULD)**: Nice-to-have deliverables if time permits
- **Out of Scope**: Explicitly excluded items (with rationale and deferral destination)

**Boundary heuristics:**
- If it can be deferred without blocking the objective → Out of scope
- If another epic depends on it → In scope
- If it requires separate architectural decisions → Consider separate epic

**Verification:** Team can clearly answer "Is X in scope?" for any proposed work item.

> **If you can't continue:** Scope unclear → Hold scope definition session with stakeholders.

---

### Step 3: Assess Architectural Impact (Optional Spike)

Determine if architectural decisions are needed before feature breakdown.

**Assessment questions:**
1. Does this epic introduce new technology or patterns?
2. Are there multiple valid implementation approaches?
3. Will decisions made here affect other epics or projects?
4. Is there significant technical uncertainty?

**If "yes" to any:**
- Conduct spike/rai-research if needed (2-4 hours max, not days)
- Document findings for ADR creation in Step 5
- Note: "Gut-check before full spike" — validate hypothesis quickly

**Verification:** Technical direction is clear enough to define features.

> **If you can't continue:** Too many unknowns → Create research task, timebox to 4 hours, then return.

---

### Step 4: Identify Feature Candidates

Break the epic into features that can be independently designed, planned, and delivered.

**Feature identification heuristics:**
- Each feature delivers demonstrable value (can be demoed)
- Features are independently deployable when possible
- Features are small enough to complete in 1-5 days (not weeks)
- Features can have clear acceptance criteria

**For each story, capture:**
- **ID**: F{epic}.{seq} (e.g., F3.1, F3.2)
- **Name**: Short descriptive name
- **Description**: 1-2 sentences of what it delivers
- **Size**: T-shirt size (XS/S/M/L) or story points
- **Dependencies**: Which features must complete first

**Typical epic contains:**
- 3-10 features (fewer = consider if this is really an epic)
- Mix of sizes: ~2-3 foundation features, ~4-6 core features, ~1-2 polish features

**Verification:** Each feature passes the "can be independently delivered" test.

> **If you can't continue:** Features too large → Decompose further. Features too small → Consider consolidating.

---

### Step 5: Create ADRs for Architectural Decisions

Document significant decisions that affect the epic's technical direction.

**When to create an ADR:**
- Choosing between multiple valid approaches (significant impact)
- Adopting new technology, pattern, or framework
- Making trade-offs with long-term consequences
- Decisions that other epics or teams will depend on

**When NOT to create an ADR:**
- Implementation details that can be changed easily
- Standard patterns already established in codebase
- Decisions with obvious best choice

**ADR scope rule:** Each ADR addresses one core technical direction. Don't combine multiple decisions into one ADR.

**For each ADR:**
1. Document context (what situation requires a decision)
2. State decision clearly (1-2 sentences)
3. List consequences (positive, negative, neutral)
4. Note alternatives considered with rejection rationale

**Use template:** `.raise/templates/architecture/adr.md`

**Verification:** ADRs are reviewable in <5 minutes each.

> **If you can't continue:** Decision too complex → Timebox research, then decide. Prolonged discussion = reduce scope.

---

### Step 6: Map Dependencies

Identify internal and external dependencies that affect sequencing.

**Internal dependencies (within epic):**
- Which features must complete before others can start?
- Are there parallel tracks possible?
- What's the critical path?

**External dependencies:**
- Other epics or projects this depends on
- Third-party services or APIs
- Team availability or skill requirements
- Infrastructure or environment needs

**Dependency visualization:**
```
F{N}.1 (foundation)
  ↓
F{N}.2 ──┐
  ↓      │ (parallel possible)
F{N}.3 ◄─┘
  ↓
F{N}.4
```

**Verification:** Dependency graph has no cycles; blockers are identified.

> **If you can't continue:** Circular dependencies → Refactor feature boundaries to break cycles.

---

### Step 7: Define Done Criteria

Establish clear completion criteria at both feature and epic levels.

**Per-Feature Done Criteria (standard):**
- [ ] Code implemented with type annotations
- [ ] Docstrings on all public APIs
- [ ] Component catalog updated (`dev/components.md`)
- [ ] ADR created if architectural decision made
- [ ] Unit tests passing (>90% coverage)
- [ ] Quality checks pass (ruff, pyright, bandit)

**Epic Done Criteria (specific to this epic):**
- [ ] All planned features complete
- [ ] Architecture documentation updated
- [ ] Success metrics validated
- [ ] Epic retrospective completed (`/rai-epic-close`)

**Customize based on epic nature:**
- User-facing epic: Add UX validation criteria
- Infrastructure epic: Add performance/reliability criteria
- Integration epic: Add E2E test criteria

**Verification:** Team agrees on what "done" means before starting.

> **If you can't continue:** Unclear done criteria → Default to standard guardrails + measurable success criteria.

---

### Step 8: Estimate and Prioritize

Provide rough estimates and establish feature priority.

**Estimation approach:**
- Use T-shirt sizing (XS/S/M/L) for features
- Reference calibration data (`.claude/rai/calibration.md` if available)
- Apply velocity multipliers based on kata cycle usage

**T-shirt sizing guide:**

| Size | Typical Scope | Features | Duration (with kata cycle) |
|:----:|---------------|:--------:|:----------------------:|
| XS | Single-feature polish | 1-2 | <1 day |
| S | Foundation work | 2-4 | 1-2 days |
| M | Core capability | 3-6 | 3-5 days |
| L | Major initiative | 5-10 | 1-2 weeks |

**Priority factors:**
- Business value delivery
- Risk reduction (risky features early)
- Dependency unblocking
- Quick wins (momentum builders)

**Verification:** Total estimated effort is realistic for timeline.

> **If you can't continue:** Estimates exceed timeline → Reduce scope (cut SHOULD items), or negotiate timeline.

---

### Step 9: Document Risks and Mitigations

Identify what could go wrong and how to address it.

**Risk categories:**
- **Technical**: New technology, integration complexity, performance uncertainty
- **Scope**: Feature creep, unclear requirements, changing priorities
- **Resource**: Skill gaps, availability, dependencies on others
- **Timeline**: External deadlines, dependencies, holidays

**For each risk, document:**
- Risk description
- Likelihood (High/Medium/Low)
- Impact (High/Medium/Low)
- Mitigation strategy

**Verification:** Top 3 risks have mitigation strategies.

> **If you can't continue:** Too many high risks → Consider smaller scope or spike to reduce uncertainty.

---

### Step 10: Create Epic Scope Document

Consolidate all design work into the epic scope document.

**Location:** `work/epics/e{N}-{name}/scope.md`

**Required sections:**
1. Objective (from Step 1)
2. In Scope / Out of Scope (from Step 2)
3. Features table with sizes and dependencies (from Step 4)
4. Done Criteria (from Step 7)
5. Dependencies (from Step 6)
6. Notes (risks, assumptions, timeline)

**Optional sections:**
- Architecture references (if ADRs created)
- Success metrics (if quantifiable)
- Migration/rollout plan (if applicable)

**Verification:** Scope document is reviewable in <10 minutes.

---

### Step 11: Update Parking Lot

Capture deferred items for future consideration.

**For each out-of-scope item:**
- Add to `dev/parking-lot.md`
- Note origin (this epic design)
- Classify priority (High/Medium/Low)
- Note conditions for promotion

**Verification:** All explicitly deferred items are captured.

> **If you can't continue:** Parking lot doesn't exist → Create it with template.

---

### Step 12: Review & Validate (Optional)

Self-review checklist before proceeding:

- [ ] Objective is clear and outcome-focused
- [ ] Scope boundaries are explicit (in/out documented)
- [ ] Features are independently deliverable (3-10 features)
- [ ] Dependencies mapped (no cycles)
- [ ] ADRs created for architectural decisions
- [ ] Done criteria defined (feature + epic level)
- [ ] Estimates are realistic for timeline
- [ ] Top risks have mitigations
- [ ] Scope document reviewable in <10 minutes
- [ ] Parking lot updated with deferred items

**Validation questions:**
1. Can someone unfamiliar with this work understand what the epic delivers?
2. Is there a clear path from first feature to epic completion?
3. Are architectural decisions documented, not assumed?

---

### Step 13: Emit Epic Complete (Telemetry)

Record the completion of the design phase:

```bash
rai memory emit-work epic {epic_id} --event complete --phase design
```

**Example:** `rai memory emit-work epic E9 -e complete -p design`

---

## Output

- **Primary:** `work/epics/e{N}-{name}/scope.md`
- **Secondary:** `dev/decisions/adr-*.md` - ADRs for architectural decisions (0-3 typical)
- **Updated:** `dev/parking-lot.md` - Deferred items captured
- **Next:** `/rai-epic-plan` (sequence features, plan milestones)

## Epic Scope Template

```markdown
# Epic E{N}: {Epic Name} - Scope

> **Status:** IN PROGRESS
> Branch: `feature/e{n}/{epic-slug}`
> Created: YYYY-MM-DD
> Target: YYYY-MM-DD (deadline or milestone)

---

## Objective

{1-2 sentences: What business/user outcome does this epic deliver?}

**Value proposition:** {Why this matters, what's unlocked after completion}

---

## Features ({X} SP estimated)

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F{N}.1 | {Feature Name} | S | Pending | {1-line description} |
| F{N}.2 | {Feature Name} | M | Pending | {1-line description} |
| F{N}.3 | {Feature Name} | S | Pending | {1-line description} |

**Total:** {X} features, {Y} SP estimated

---

## In Scope

**MUST:**
- {Non-negotiable deliverable 1}
- {Non-negotiable deliverable 2}
- {Non-negotiable deliverable 3}

**SHOULD:**
- {Nice-to-have 1}
- {Nice-to-have 2}

---

## Out of Scope (defer to {destination})

- {Excluded item 1} → {Why excluded, where deferred}
- {Excluded item 2} → {Why excluded, where deferred}

---

## Done Criteria

### Per Feature
- [ ] Code implemented with type annotations
- [ ] Docstrings on all public APIs (Google-style)
- [ ] Component catalog updated (`dev/components.md`)
- [ ] ADR created if architectural decision (`dev/decisions/`)
- [ ] Unit tests passing (>90% coverage on feature code)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [ ] All planned features complete (F{N}.1-F{N}.X)
- [ ] {Epic-specific success criterion 1}
- [ ] {Epic-specific success criterion 2}
- [ ] Architecture guide updated (`dev/architecture-overview.md`)
- [ ] Epic merged to {target branch}

---

## Dependencies

```
F{N}.1 (foundation)
  ↓
F{N}.2 ──┐
  ↓      │ (parallel possible)
F{N}.3 ◄─┘
  ↓
F{N}.4
```

**External blockers:** {None / List external dependencies}

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| {Decision 1} | ADR-{XXX} | {One-line summary} |
| {Decision 2} | ADR-{YYY} | {One-line summary} |

---

## Notes

### Why This Epic
- {Context for why this work is happening now}
- {Alignment to solution vision or business case}

### Key Risks
- {Risk 1}: {Mitigation}
- {Risk 2}: {Mitigation}

### Velocity Assumption
- {Expected velocity based on calibration data}
- {Factors that might affect velocity}

---

*Epic tracking - update per story completion*
*Created: YYYY-MM-DD*
```

## Quality Standards

| Metric | Target |
|--------|--------|
| Design time | <2 hours for typical epic |
| Scope document | Reviewable in <10 minutes |
| Features per epic | 3-10 (sweet spot: 5-7) |
| ADRs per epic | 0-3 (most epics: 1-2) |
| Feature sizing accuracy | Within 50% of actual (improves with calibration) |

## Common Pitfalls

1. **Time-boxing epics instead of scope-boxing** — Epic is defined by scope, not duration
2. **Skipping scope boundaries** — Leads to scope creep; explicit out-of-scope prevents this
3. **Too many features** — If >10 features, consider splitting into multiple epics
4. **Too few features** — If <3 features, consider if this is really an epic
5. **ADRs for everything** — Only document significant decisions; implementation details don't need ADRs
6. **No ADRs at all** — Architectural decisions without documentation are lost knowledge
7. **Over-specifying features** — Save details for `/rai-story-design`; epic level is high-level
8. **Ignoring dependencies** — Unmapped dependencies cause blocked work during implementation
9. **Unclear done criteria** — "We'll know it when we see it" is not a done criterion

## Integration with Memory Model

This skill supports the three-layer memory model:

**Identity Layer (always loaded):** Core values and principles guide scope decisions
**Memory Layer (MVC queryable):** Past epic patterns inform current design
**Long-term Layer (on-demand):** Historical velocity data calibrates estimates

**Update memory after epic design:**
- Add notable patterns to `memory.md` if new approaches discovered
- Reference calibration data for estimates
- Capture architectural insights for future epics

## References

- **Epic Scope Examples:** `work/epics/e01-foundation/scope.md`, `work/epics/e02-governance/scope.md`
- **ADR Template:** `.raise/templates/architecture/adr.md`
- **Feature Design:** `/rai-story-design` (next level down)
- **Epic Plan:** `/rai-epic-plan` (sequence features after design)
- **Epic Close:** `/rai-epic-close` (retrospective after completion)
- **Constitution:** `framework/reference/constitution.md` (principles governing design)
- **Parking Lot:** `dev/parking-lot.md` (capture deferred items)

## Relationship to Other Skills

```
Project Level
    ↓
/rai-epic-design  ← YOU ARE HERE
    ↓
/rai-epic-plan    ← Sequence features, milestones
    ↓
/rai-story-design → /rai-story-plan → /rai-story-implement → /rai-story-review
    ↓
/rai-epic-close   ← Retrospective, learnings
```

---

**Status:** Active
**Version:** 1.0
**Created:** 2026-02-01
**Author:** Rai + Emilio
