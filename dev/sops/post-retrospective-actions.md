# SOP: Post-Retrospective Action Protocol

> Standard Operating Procedure for implementing retrospective improvements before commit
> Version: 1.0
> Date: 2026-01-31
> Status: Active

---

## Purpose

Ensure that learnings from story retrospectives are systematically applied to the framework and codebase **before** committing the feature, creating a complete learning cycle within each story delivery.

**Problem this solves:** Retrospective insights often languish in parking lots or action item lists, never getting implemented. Meanwhile, the feature is committed without the improvements that were learned during its development.

**Impact of deferred improvements:**
- Framework improvements delayed or forgotten
- Same mistakes repeated in next features
- Learnings don't compound
- Gap between "what we learned" and "what we do"

---

## Philosophy

**"The commit should include the code AND the improvement product of our collaboration in that code."**

Each feature is not just a deliverable — it's a learning cycle. The retrospective closes the loop by:
1. Extracting what was learned
2. Applying improvements immediately
3. Committing feature + improvements together
4. Demonstrating the learning cycle in action

---

## Improvement Classification (Three Types)

When reviewing retrospective improvements, classify each into one of three types:

### Type A: Quick Wins (Before Commit)

**Characteristics:**
- Can be implemented in <30 minutes total
- No design or architectural decisions needed
- Clear, unambiguous action
- Directly related to the completed feature
- Low risk of unintended consequences

**Examples:**
- Add new guardrail to `guardrails.md`
- Update calibration data with actual metrics
- Add pattern to memory files
- Document naming convention in existing docs
- Update component catalog with new module

**Decision Rule:** If you can do it in one session without blocking, **do it now**.

---

### Type B: Strategic Changes (Defer with Intent)

**Characteristics:**
- Requires design work or architectural planning
- Affects multiple components or workflows
- Needs user input or decision-making
- Takes >30 minutes to implement properly
- May have downstream implications

**Examples:**
- Create new ADR for architecture pattern
- Refactor kata/skill structure
- Add new validation gate
- Design new template format
- Implement complex automation

**Decision Rule:** Add to parking lot with **specific next steps** and **champion**.

**Required fields for Type B:**
```markdown
- [ ] **[Improvement name]**
  - **Champion:** [Who will drive this]
  - **Effort:** [Small/Medium/Large]
  - **Next step:** [Specific action to start]
  - **Depends on:** [Blockers, if any]
  - **Evidence:** [What showed this is needed]
```

---

### Type C: Tracking and Metrics (Always)

**Characteristics:**
- Data collection or metric tracking
- No implementation, just documentation
- Takes <5 minutes
- Supports future calibration or analysis

**Examples:**
- Add feature to calibration table
- Update session index
- Log velocity ratio
- Capture task size actuals

**Decision Rule:** **Always do these** — they're the foundation of continuous improvement.

---

## Step-by-Step Protocol

### Step 1: Complete Feature Retrospective

Follow `/story-review` skill:
- Extract learnings
- Identify improvements
- Answer heutagogical questions
- Document in `retrospective.md`

**Verification:** Retrospective complete with improvements section.

---

### Step 2: Classify Improvements

For each improvement identified:
1. Read the improvement description
2. Estimate effort (time + complexity)
3. Classify as Type A, B, or C
4. Tag in retrospective document

**Format in retrospective:**
```markdown
## Improvements Applied

### ✅ Immediate (Type A - Applied Before Commit)
1. [Improvement 1]
2. [Improvement 2]

### 📋 Deferred (Type B - Added to Parking Lot)
1. [Improvement 3] - See parking-lot.md
2. [Improvement 4] - See parking-lot.md

### 📊 Tracking (Type C - Metrics Updated)
1. [Calibration data updated]
2. [Session index updated]
```

**Verification:** All improvements classified.

---

### Step 3: Execute Type C (Tracking)

Update tracking files immediately:
- `.claude/rai/calibration.md` - Add feature metrics
- `.claude/rai/session-index.md` - Add session log
- `.claude/rai/memory.md` - Add patterns discovered

**Verification:** All tracking files updated.

**Time budget:** <5 minutes total.

---

### Step 4: Execute Type A (Quick Wins)

Implement all Type A improvements:
- Update `guardrails.md`, `glossary.md`, or other docs
- Add patterns to framework artifacts
- Document conventions or best practices
- Update component catalog

**Process per improvement:**
1. Read relevant file to understand structure
2. Add improvement following existing patterns
3. Update version/changelog if applicable
4. Verify consistency

**Verification:** All Type A improvements applied.

**Time budget:** <30 minutes total for all Type A items.

---

### Step 5: Defer Type B (With Intent)

For each Type B improvement:
1. Add to `dev/parking-lot.md` with complete context
2. Include champion, effort, next step, evidence
3. Link to retrospective for full context
4. Tag with priority (High/Medium/Low)

**Template:**
```markdown
- [ ] **[Improvement name]**
  - **Type:** Strategic improvement
  - **From:** [Feature ID] retrospective
  - **Champion:** [Owner or TBD]
  - **Effort:** [Small/Medium/Large]
  - **Next step:** [Specific action - design, ADR, spike, etc.]
  - **Depends on:** [Blockers or prerequisites]
  - **Evidence:** [What showed need - quote from retro]
  - **Details:** See `work/stories/[feature]/retrospective.md`
```

**Verification:** All Type B improvements captured with actionable next steps.

**Time budget:** <10 minutes total for documentation.

---

### Step 6: Update Retrospective Status

In `retrospective.md`, update "Improvements Applied" section:
- Mark Type A as ✅ Applied (with file locations)
- Mark Type B as 📋 Deferred (with parking lot reference)
- Mark Type C as 📊 Updated (with files updated)

**Verification:** Retrospective shows clear status of all improvements.

---

### Step 7: Commit Feature + Improvements

Create feature commit that includes:
- Feature code
- Feature tests
- Feature documentation
- Type A improvements applied
- Type C tracking updates
- Updated retrospective

**Commit message format:**
```
feat(scope): Feature description

Complete feature implementation with retrospective learnings applied.

Feature delivered:
- [Key deliverable 1]
- [Key deliverable 2]

Improvements applied:
- [Type A improvement 1]
- [Type A improvement 2]

Metrics tracked:
- [Type C tracking]

Deferred to parking lot:
- [Type B improvement - with reasoning]

Velocity: [X]x faster than estimate
Coverage: [Y]%
Tests: [N] passing

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Verification:** Commit demonstrates complete learning cycle.

---

## Decision Matrix

When classifying improvements, use this matrix:

| Criteria | Type A (Now) | Type B (Defer) | Type C (Always) |
|----------|--------------|----------------|-----------------|
| **Time** | <30 min total | >30 min | <5 min |
| **Design needed** | No | Yes | No |
| **Risk** | Low | Medium-High | None |
| **Scope** | Single file/doc | Multiple components | Data only |
| **Blocking** | No blockers | May have dependencies | No blockers |
| **Action** | Implement now | Add to parking lot | Update tracking |

**When in doubt:** Start with Type B (defer). Better to capture with intent than rush and create technical debt.

---

## Examples from F2.3 Retrospective

### Type A: Implemented Before Commit ✅

1. **Add Python naming guardrail**
   - Time: ~15 minutes
   - File: `governance/solution/guardrails.md`
   - Action: Added SHOULD-CODE-002 with examples
   - Risk: None (documentation only)
   - **Result:** ✅ Applied

2. **Update calibration data**
   - Time: ~5 minutes
   - File: `.claude/rai/calibration.md`
   - Action: Added F2.2 and F2.3 metrics
   - Risk: None (data tracking)
   - **Result:** ✅ Applied

### Type B: Deferred to Parking Lot 📋

1. **Document "compose, don't duplicate" pattern**
   - Time: ~60-90 minutes (requires ADR or concept doc)
   - Scope: New framework concept document
   - Design: Needs structure, examples, when-to-apply guidance
   - Dependencies: May wait for 1-2 more examples to solidify pattern
   - **Result:** 📋 Deferred with champion and next steps

2. **Add "Simple First" concrete examples to constitution**
   - Time: ~45 minutes (requires careful constitutional language)
   - Scope: Framework reference document (high visibility)
   - Design: Needs review to ensure alignment with existing principles
   - Dependencies: None, but benefit from more evidence
   - **Result:** 📋 Deferred with specific examples to add

### Type C: Tracking ✅

1. **Update session index**
   - Time: 2 minutes
   - Action: Add F2.3 session row
   - **Result:** ✅ Applied

---

## Benefits of This Protocol

### 1. Compounding Learning
Each feature makes the framework better for the next feature. Improvements accumulate rather than decay in parking lots.

### 2. Demonstrated Value
The commit itself shows the learning cycle: "We built X, learned Y, improved Z."

### 3. Reduced Friction
Quick wins (Type A) are implemented while context is fresh. Harder work (Type B) is captured with enough detail to resume later.

### 4. Quality Signal
High ratio of Type A to Type B indicates healthy framework maturity. Too many Type B may signal need for framework stabilization sprint.

### 5. Velocity Amplification
Framework improvements from Feature N directly speed up Feature N+1. The kata cycle compounds.

---

## Anti-Patterns to Avoid

### ❌ "We'll Do It Later"
**Problem:** Deferring Type A improvements that take <30 minutes.
**Impact:** Improvements never happen; context lost.
**Fix:** If it's truly <30 min, do it now. If not, it's Type B — classify correctly.

### ❌ "Just One More Thing"
**Problem:** Treating Type B improvements as Type A ("this will be quick").
**Impact:** Commit delayed; scope creep; technical debt.
**Fix:** Be honest about effort. Type B goes to parking lot with intent.

### ❌ "Perfect Documentation"
**Problem:** Spending too much time polishing Type A changes.
**Impact:** Time budget exceeded; process feels heavy.
**Fix:** Good enough is good enough for Type A. Document clearly, not perfectly.

### ❌ "Vague Parking Lot Entries"
**Problem:** Type B items added without champion, next step, or context.
**Impact:** Items decay; never actionable.
**Fix:** Use Type B template with all required fields.

---

## Calibration and Evolution

### Track Protocol Adherence

| Feature | Type A Count | Type B Count | Type C Count | Time Spent | Notes |
|---------|:------------:|:------------:|:------------:|:----------:|-------|
| F2.3 | 2 | 2 | 2 | ~25 min | Protocol creation session |

**Healthy ratios:**
- Type A: 1-3 per story (quick wins common, but not overwhelming)
- Type B: 1-2 per story (strategic improvements identified but deferred)
- Type C: Always 1+ (always track metrics)

**Red flags:**
- Zero Type A for 3+ features → Framework may be stagnating
- 5+ Type B per story → May need framework stabilization sprint
- Zero Type C → Not tracking, can't improve

### Adjust Protocol Based on Data

Review quarterly:
- Are Type A improvements being applied consistently?
- Are Type B items being promoted from parking lot?
- Is time budget realistic (<30 min for Type A)?

Evolve protocol based on evidence.

---

## Integration with Other SOPs

### Branch Management SOP
- Post-retrospective improvements go in **same branch** as feature
- Commit includes feature + improvements
- Branch scope covers "feature delivery + retrospective closure"

### Session Close Skill
- Post-retrospective protocol happens **before** session close
- Session close captures "applied improvements" as part of session summary
- Memory files updated by Type C tracking

### Feature Review Skill
- Feature review (`/story-review`) triggers this protocol
- Retrospective document is input to protocol
- Protocol execution completes the review cycle

---

## Checklist: Before Committing Feature

**After retrospective complete:**

- [ ] All improvements classified (Type A, B, or C)
- [ ] Type C tracking files updated (<5 min)
- [ ] Type A improvements implemented (<30 min total)
- [ ] Type B improvements added to parking lot with full context
- [ ] Retrospective updated with improvement status
- [ ] Commit message documents learning cycle
- [ ] Total time <45 minutes for all post-retro work

**If checklist incomplete:** Stop and complete before committing.

---

## Revision History

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0 | 2026-01-31 | Initial protocol based on F2.3 retrospective experience | Rai + Emilio |

---

## References

- **Feature Review Skill:** `.claude/skills/story-review/`
- **Session Close Skill:** `.claude/skills/session-close/`
- **Branch Management SOP:** `dev/sops/branch-management.md`
- **Kaizen (Continuous Improvement):** Toyota Production System
- **Learning Cycles:** Kolb's Experiential Learning Theory

---

**Status**: Active
**Review Frequency**: Quarterly or after 5 features using protocol
**Owner**: RaiSE Framework Team
**Next Review**: 2026-04-30
