# Epic Close: Systemic Learning & Continuity

## Purpose

Close an epic by extracting epic-level learnings, validating architectural decisions across features, and creating comparison data for systemic review. This enables learning at scale - patterns that emerge across multiple features.

**Design Principle:** "As above, so below" - Epic closure mirrors feature review at higher granularity.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps, create complete epic retrospective.

**Ha (破)**: Adjust depth based on epic complexity and systemic review needs.

**Ri (離)**: Develop custom epic closure patterns for specific organizational contexts.

## Context

**When to use:**
- After completing all features in an epic
- Before merging epic branch to main development branch
- To prepare for systemic review (quarterly/milestone)
- To extract epic-level patterns for framework improvement

**When to skip:**
- Never skip for completed epics - this is the meso-level learning layer
- Epic-level learnings enable systemic review across projects

**Inputs required:**
- Completed epic with all features done
- All feature retrospectives for the epic
- Epic scope document (`dev/epic-{id}-scope.md`)
- Parking lot with epic-related items

**Output:**
- Epic retrospective document
- Updated epic scope (marked complete)
- Updated architecture documentation
- Triaged parking lot
- Systemic review markers

## Steps

### Step 1: Verify Epic Completeness

Review epic scope and confirm:
- All planned features delivered (SP complete)
- Any deferred features documented with rationale
- Scope evolution tracked (if any)

**Verification:** Epic scope document shows completion status.

> **If you can't continue:** Features incomplete → Finish features first or document deferral.

---

### Step 2: Calculate Epic-Level Metrics

Aggregate data across all features in the epic:

**Velocity metrics:**
- Total story points delivered
- Total actual time (sum of feature times)
- Velocity trend across features (first → middle → last)
- Average velocity for epic

**Quality metrics:**
- Total tests added
- Test coverage (average or minimum)
- Bugs found during epic
- Technical debt incurred or paid

**Comparison to plan:**
- Estimated vs actual time (if available)
- Planned vs actual scope
- Velocity variance (how much did estimates improve?)

**Verification:** Metrics table complete with all features.

> **If you can't continue:** Missing data → Reconstruct from feature retrospectives.

---

### Step 3: Extract Epic-Level Patterns

Identify patterns that emerged across multiple features (not visible in single-feature retros):

**Process patterns:**
- Did velocity stabilize or vary? Why?
- Which process improvements carried across features?
- What friction points recurred?

**Architecture patterns:**
- Did early features enable later features?
- Architecture reuse? Composition?
- Design decisions validated or invalidated?

**Collaboration patterns:**
- Communication patterns that worked
- Decision-making that improved
- Friction that resolved (or didn't)

**Verification:** At least 2-3 epic-level patterns identified.

> **If you can't continue:** Read all feature retrospectives to find cross-feature themes.

---

### Step 4: Assess Architectural Impact

Document how this epic changed the system:

**New capabilities unlocked:**
- What can future work now do that it couldn't before?
- What modules/patterns are now available for reuse?

**Architectural decisions validated:**
- Which design choices paid off?
- Which created technical debt?
- What would we do differently?

**System evolution:**
- How did the architecture change?
- Diagram updates needed?
- ADRs created during epic?

**Verification:** Architectural impact section complete.

> **If you can't continue:** Review ADRs and code changes to identify impact.

---

### Step 5: Review Process Innovations

Identify process changes introduced during the epic:

**Innovations introduced:**
- New skills, SOPs, or practices created
- Framework improvements applied
- Tools or techniques adopted

**Adoption and stickiness:**
- Which innovations were used across features?
- Which were one-time experiments?
- Which should carry forward to next epic?

**ROI assessment:**
- Which changes delivered value?
- Which consumed time without benefit?
- What should we double down on?

**Verification:** Process innovations documented with adoption notes.

> **If you can't continue:** Review feature retrospectives for "Improvements Applied" sections.

---

### Step 6: Triage Parking Lot

Review all parking lot items added during the epic:

**Classification:**
- **Promote to backlog:** High priority, ready to implement
- **Defer with intent:** Medium priority, needs more design
- **Archive:** Low priority or no longer relevant

**For each promoted item:**
- Assign priority (High/Medium/Low)
- Estimate effort (Small/Medium/Large)
- Identify champion or next step

**For each deferred item:**
- Document why deferred
- Conditions for promotion
- Review date

**For archived items:**
- Document why archived
- Remove from parking lot

**Verification:** All epic-related parking lot items triaged.

> **If you can't continue:** Review `dev/parking-lot.md` for items from this epic.

---

### Step 7: Compare to Previous Epics

If this isn't the first epic, compare metrics and patterns:

**Velocity comparison:**
- How does epic velocity compare to previous epics?
- Trending up, down, or stable?

**Quality comparison:**
- Test coverage trends
- Bug rate trends
- Technical debt trends

**Process maturity:**
- Are estimates improving?
- Is friction decreasing?
- Are innovations sticking?

**Verification:** Comparison table created (if previous epics exist).

> **If you can't continue:** First epic → Skip this step, but create baseline for next epic.

---

### Step 8: Create Epic Retrospective

Write comprehensive epic retrospective document:

**Location:** `dev/epic-{id}-retrospective.md`

**Required sections:**
1. Summary (SP, duration, features)
2. Epic-Level Metrics (velocity, quality, comparison)
3. Patterns Across Features (process, architecture, collaboration)
4. Architectural Impact (new capabilities, validated decisions)
5. Process Innovations (introduced, adopted, ROI)
6. Parking Lot Triage (promoted, deferred, archived)
7. Comparison to Previous Epics (if applicable)
8. Recommendations for Next Epic
9. Systemic Review Markers (checklist for quarterly review)

**Verification:** Epic retrospective complete and comprehensive.

> **If you can't continue:** Use template from this skill.

---

### Step 9: Update Documentation

Update related documents:

**Epic scope document (`dev/epic-{id}-scope.md`):**
- Status: COMPLETE
- Completion date
- Actual vs planned metrics
- Scope evolution summary

**Architecture overview (`dev/architecture-overview.md`):**
- Add new modules from epic
- Update system diagrams (if applicable)
- Document architectural changes

**Component catalog (`dev/components.md`):**
- Verify all epic components documented
- Add cross-references if needed

**Parking lot (`dev/parking-lot.md`):**
- Update with triage results
- Archive completed items
- Promote high-priority items

**Verification:** All documents updated and consistent.

> **If you can't continue:** Minimum = update epic scope to COMPLETE.

---

### Step 10: Update Context for Next Work

Update session context files:

**CLAUDE.local.md:**
- Mark epic as complete
- Update "Next Feature" or "Next Epic"
- Add to "Completed Epics" list

**Memory files (`.claude/rai/`):**
- Add epic-level patterns to `memory.md`
- Update calibration data if new insights
- Update session index with epic closure

**Verification:** Context files reflect epic completion.

---

### Step 11: Create Systemic Review Markers

Add markers to enable future systemic review:

**In epic retrospective, include:**
- [ ] Epic-level velocity data captured for comparison
- [ ] Architectural impact documented with evidence
- [ ] Process changes tracked (introduced, adopted, ROI)
- [ ] Parking lot triaged with rationale
- [ ] Comparison to previous epics (if applicable)
- [ ] Recommendations for next epic documented
- [ ] Ready for quarterly/milestone systemic review

**Verification:** All systemic review markers checked.

---

## Output

- **Primary:** `dev/epic-{id}-retrospective.md` - Epic retrospective
- **Updated:** `dev/epic-{id}-scope.md` - Marked complete with metrics
- **Updated:** `dev/architecture-overview.md` - Architectural changes
- **Updated:** `dev/parking-lot.md` - Triaged items
- **Updated:** `CLAUDE.local.md` - Epic completion status
- **Updated:** `.claude/rai/memory.md` - Epic-level patterns

## Epic Retrospective Template

```markdown
# Epic Retrospective: {Epic Name}

**Epic ID:** {E1, E2, E3...}
**Story Points:** {X} SP
**Duration:** {Y} hours/days
**Completed:** YYYY-MM-DD
**Features:** {N} features delivered

---

## Summary

### Scope
- **Planned:** {Original epic scope}
- **Delivered:** {What was actually delivered}
- **Deferred:** {Features deferred with rationale}
- **Evolution:** {How scope changed and why}

### Features Delivered

| Feature | SP | Estimated | Actual | Velocity | Tests | Coverage |
|---------|:--:|-----------|--------|:--------:|:-----:|:--------:|
| F{N}.1 | X | Y min | Z min | A.Bx | N | X% |
| F{N}.2 | X | Y min | Z min | A.Bx | N | X% |
| F{N}.3 | X | Y min | Z min | A.Bx | N | X% |
| **Total** | **X** | **Y** | **Z** | **Avg** | **N** | **X%** |

---

## Epic-Level Metrics

### Velocity
- **Total SP:** {X} SP delivered
- **Total Time:** {Y} hours actual
- **Velocity Trend:** {First feature → Last feature pattern}
- **Average Velocity:** {X.Yx faster than estimates}

### Quality
- **Total Tests:** {N} tests added
- **Coverage:** {X-Y%} range, {Z%} average
- **Bugs Found:** {N} bugs during development
- **Technical Debt:** {Incurred / Paid / Neutral}

### Comparison to Plan
- **Time:** {X%} of estimated (if available)
- **Scope:** {100% / X% with deferrals}
- **Velocity Variance:** {How much estimates improved across epic}

---

## Patterns Across Features

### Process Patterns

**What emerged across multiple features:**
- {Pattern 1: Description and evidence from features}
- {Pattern 2: Description and evidence from features}
- {Pattern 3: Description and evidence from features}

**Velocity patterns:**
- {Did velocity stabilize? Trend up/down? Why?}

**Friction points:**
- {What slowed us down repeatedly?}
- {What friction was resolved?}

### Architecture Patterns

**Reuse and composition:**
- {How did early features enable later features?}
- {Examples of architecture reuse}
- {Composition vs duplication}

**Design decisions validated:**
- ✅ {Decision 1: Why it worked}
- ✅ {Decision 2: Why it worked}
- ❌ {Decision 3: Why it didn't work}

**Technical debt:**
- {Debt incurred and why}
- {Debt paid down}
- {Debt carried forward}

### Collaboration Patterns

**Communication:**
- {What communication patterns worked?}
- {What improved over the epic?}

**Decision-making:**
- {How did decisions get made?}
- {What worked? What didn't?}

**Learnings:**
- {User feedback that shaped work}
- {Mid-flight corrections that worked}

---

## Architectural Impact

### New Capabilities Unlocked

**Future work can now:**
- {Capability 1: Module/pattern available}
- {Capability 2: Module/pattern available}
- {Capability 3: Module/pattern available}

### Modules Added

```
{Directory structure showing new modules}
```

### Design Decisions

**Validated:**
- {Decision 1: Evidence it worked}
- {Decision 2: Evidence it worked}

**Invalidated or uncertain:**
- {Decision 3: Why it didn't work as expected}

**Would do differently:**
- {What we'd change if starting over}

### System Evolution

**Before this epic:**
{Brief description of system state}

**After this epic:**
{Brief description of new system state}

**Diagrams updated:**
- [ ] Architecture overview diagram
- [ ] Component diagram
- [ ] Other: {specify}

---

## Process Innovations

### Innovations Introduced During Epic

| Innovation | Introduced In | Adopted Across Features? | ROI |
|------------|---------------|--------------------------|-----|
| {Innovation 1} | {F{N}.X} | ✅ Used in F{N}.Y, F{N}.Z | High/Medium/Low |
| {Innovation 2} | {F{N}.X} | ❌ One-time experiment | Low |
| {Innovation 3} | {F{N}.X} | ✅ Used in F{N}.Y | High |

### Skills/SOPs Created

- {Skill 1: Description, usage}
- {Skill 2: Description, usage}
- {SOP 1: Description, impact}

### Framework Improvements Applied

**Type A (before commits):**
- {Improvement 1}
- {Improvement 2}

**Type B (deferred to parking lot):**
- {Improvement 3}
- {Improvement 4}

### Adoption and Stickiness

**Innovations that stuck:**
- {Innovation 1: Why it stuck}
- {Innovation 2: Why it stuck}

**Innovations that faded:**
- {Innovation 3: Why it faded}

**Should carry forward to next epic:**
- {Practice 1}
- {Practice 2}

### ROI Assessment

**High ROI (double down):**
- {Practice 1: Value delivered vs cost}

**Medium ROI (continue):**
- {Practice 2: Some value, some cost}

**Low ROI (reconsider):**
- {Practice 3: Cost > value}

---

## Parking Lot Triage

### Items Added During Epic

**Total items:** {N} items added to parking lot during E{X}

### Promoted to Backlog (High Priority)

- [ ] **{Item 1}**
  - Priority: High
  - Effort: {Small/Medium/Large}
  - Champion: {Owner or TBD}
  - Next step: {Specific action}

- [ ] **{Item 2}**
  - Priority: High
  - Effort: {Small/Medium/Large}
  - Champion: {Owner or TBD}
  - Next step: {Specific action}

### Deferred with Intent (Medium Priority)

- [ ] **{Item 3}**
  - Priority: Medium
  - Effort: {Small/Medium/Large}
  - Deferred because: {Rationale}
  - Review date: {YYYY-MM-DD}
  - Conditions for promotion: {Criteria}

### Archived (Low Priority / No Longer Relevant)

- ~~{Item 4}~~ - Archived: {Why no longer relevant}
- ~~{Item 5}~~ - Archived: {Why deprioritized}

---

## Comparison to Previous Epics

{Skip this section if this is the first epic}

### Epic Comparison Table

| Epic | SP | Duration | Avg Velocity | Tests | Coverage | Process Innovations |
|------|:--:|:--------:|:------------:|:-----:|:--------:|---------------------|
| E1 | {X} | {Y} | {Z.Wx} | {N} | {X%} | {Innovation 1, 2} |
| E{current} | {X} | {Y} | {Z.Wx} | {N} | {X%} | {Innovation 3, 4} |

### Velocity Trends

- **E1 → E{current}:** {Trending up/down/stable? Why?}
- **Calibration:** {Are estimates improving? Evidence?}

### Quality Trends

- **Coverage:** {Trending up/down/stable?}
- **Tests:** {Growing proportionally? Faster?}
- **Bugs:** {Fewer bugs? Better quality?}

### Process Maturity

- **Estimate accuracy:** {Getting better? Worse? Why?}
- **Friction:** {Decreasing? Same? Why?}
- **Innovation stickiness:** {More innovations carrying forward?}

### Key Insights from Comparison

- {Insight 1: What comparison reveals}
- {Insight 2: What comparison reveals}
- {Insight 3: What comparison reveals}

---

## Recommendations for Next Epic

### Continue (What Worked)

- {Practice 1: Keep doing this}
- {Practice 2: Keep doing this}
- {Practice 3: Keep doing this}

### Improve (What Needs Adjustment)

- {Area 1: How to improve}
- {Area 2: How to improve}
- {Area 3: How to improve}

### Experiment (What to Try)

- {Experiment 1: Why worth trying}
- {Experiment 2: Why worth trying}

### Stop (What Didn't Work)

- {Practice 1: Why stop}
- {Practice 2: Why stop}

---

## Systemic Review Markers

Checklist for quarterly/milestone systemic reviews:

- [ ] Epic-level velocity data captured for comparison
- [ ] Velocity trend documented (stable/improving/declining)
- [ ] Architectural impact documented with evidence
- [ ] Process innovations tracked (introduced, adopted, ROI)
- [ ] Parking lot triaged with rationale
- [ ] Comparison to previous epics complete (if applicable)
- [ ] Recommendations for next epic documented
- [ ] Quality metrics tracked (tests, coverage, bugs)
- [ ] Technical debt tracked (incurred, paid, carried)
- [ ] Ready for aggregation into systemic review

---

## Meta-Learning (Heutagogical Checkpoint)

### 1. What did we learn at epic scale?

{Learnings that only became visible across multiple features}

### 2. How did our process evolve during this epic?

{Process maturity, innovations adopted, practices refined}

### 3. What capabilities did this epic unlock?

{For future work, for the framework, for the team}

### 4. What are we more capable of now?

{Skills, patterns, confidence gained across the epic}

---

## Next Steps

**After epic closure:**
1. {Immediate next action}
2. {Follow-up work}
3. {Next epic or maintenance}

**Merge decision:**
- [ ] Merge epic branch to {v2/main/etc} now
- [ ] Wait for: {reason if not merging immediately}

**Handoff for next work:**
- {What next epic should know}
- {Risks or dependencies carried forward}
- {Capabilities available for reuse}

---

*Epic retrospective completed: YYYY-MM-DD*
*Kata cycle: Design → Plan → Implement → Review → **Epic Close** ✓*
```

---

## Notes

### As Above, So Below (Design Principle)

This skill mirrors `/feature-review` at epic scale:

| Level | Skill | Granularity | Aggregates |
|-------|-------|-------------|------------|
| Immediate | `/session-close` | Session | Raw learnings |
| Micro | `/feature-review` | Feature | Session learnings |
| Meso | `/epic-close` | Epic | Feature learnings |
| Macro | Systemic review | Quarterly/Yearly | Epic learnings |

**Fractal pattern:** Same retrospective structure, different scale.

### Systemic Review Enablement

Epic retrospectives create the **meso-level learning layer** that enables systemic review:

**Without epic retrospectives:**
- Compare 20+ feature retrospectives manually
- Patterns lost in noise
- No epic-level velocity trends

**With epic retrospectives:**
- Compare 3-5 epic retrospectives
- Patterns visible immediately
- Clear trends across time

### Knowledge Compounding

```
Session close → Feature review → Epic close → Systemic review
     ↓              ↓               ↓              ↓
  Learnings   →  Patterns    →  Trends    →   Strategy
  (daily)        (weekly)        (monthly)      (quarterly)
```

Knowledge doesn't just accumulate — it compounds through aggregation.

### When to Create vs Skip

**Always create for completed epics.**

Epic retrospectives are lightweight compared to their value:
- 30-45 minutes to create
- Enables hours of systemic review insights
- Creates comparison baseline for future epics

---

## Integration with Other Skills

### Feature Review (`/feature-review`)
- Epic close aggregates all feature reviews from the epic
- Feature retrospectives are input to epic retrospective

### Session Close (`/session-close`)
- Epic close happens after final session of epic
- Session close updates immediate context; epic close updates epic-level context

### Post-Retrospective Action Protocol SOP
- Epic close may identify framework improvements
- Apply Type A/B/C classification to epic-level improvements

### Branch Management SOP
- Epic closure informs merge decision
- Epic branch ready to merge after closure complete

---

## References

- **Feature Review Skill:** `.claude/skills/feature-review/`
- **Session Close Skill:** `.claude/skills/session-close/`
- **Post-Retro Actions SOP:** `dev/sops/post-retrospective-actions.md`
- **Epic Scope Template:** `dev/epic-{id}-scope.md`
- **Hermetic Principle:** "As above, so below" - patterns repeat at all scales

---

**Status:** Active
**Version:** 1.0
**Created:** 2026-01-31 (E2 completion - gift to ourselves)
**Author:** Rai + Emilio
