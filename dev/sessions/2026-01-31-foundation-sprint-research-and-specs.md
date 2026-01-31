# Session: Foundation Sprint - Research Infrastructure & Lean Feature Specs

**Date:** 2026-01-31
**Type:** Research → Implementation → Dogfooding → Process Improvement
**Duration:** ~6-7 hours
**Branch:** foundation-jan2026 (renamed from project/raise-cli)
**Participants:** Emilio + Claude Sonnet 4.5

---

## Session Goal

Started as: "What's next for raise-cli project scaffolding?"
Evolved to: "Build research infrastructure, then use it to design lean feature specs"

**Actual outcome:** Complete research infrastructure + feature spec v2 template + branch management SOP

---

## What We Built

### 1. Research Infrastructure (Meta-Research)

**Research Question:** How to structure AI research prompts for epistemological rigor?

**Deliverables:**
- `.raise/templates/tools/research-prompt.md` - Structured template with 7 core sections
- `.raise/templates/tools/examples/tech-stack-evaluation-prompt.md` - Example usage
- `.raise/katas/tools/research.md` - Updated to v1.1.0 with Step 1.5 (tool selection + delegation)
- `work/research/ai-research-prompts/` - Complete research output (README, recommendation, synthesis, evidence catalog)

**Evidence:** 20 sources (7 Very High, 8 High, 5 Medium)

**Key Findings:**
- Structured prompts + hierarchical delegation + reproducibility metadata
- Tool selection: ddgr → perplexity → WebSearch (fallback chain)
- Human-AI collaboration essential for epistemological rigor
- Two-step approaches outperform single-pass
- Research as code (version prompts, log tools, timestamp)

---

### 2. Lean Feature Specification v2 (Dogfooding Research)

**Research Question:** What are the critical success factors for a lean feature spec that enables both human understanding and AI alignment?

**Deliverables:**
- `.raise/templates/tech/tech-design-feature-v2.md` - YAML+Markdown template with examples-first approach
- `.raise/katas/feature/design.md` - 8-step process for creating feature specs
- `work/research/lean-feature-specs/` - Complete research output (used new research template!)

**Evidence:** 25 sources (9 Very High, 13 High, 3 Medium)

**8 Critical Success Factors (72% HIGH confidence):**
1. **Clarity & Structure** (6 sources) - Template must enforce structure; ambiguity = defect
2. **Examples > Prose** (5 sources) - Concrete examples REQUIRED, not optional
3. **YAML + Markdown** (4 sources) - Hybrid format optimal for human+AI
4. **Iterative Refinement** (4 sources) - Specs must be easy to update
5. **Specs as Prompts** (3 sources) - Optimize for Claude's context processing
6. **What/Why Over How** (3 sources) - Focus on goals, not implementation
7. **Formal Specs** (3 sources) - MEDIUM confidence; overkill for web/CLI
8. **Gherkin/BDD** (3 sources) - MEDIUM confidence; optional, use for complex features

**Template Structure:**
- 4 Required: What/Why, Approach, Examples, Acceptance Criteria
- 4 Optional: Scenarios, Algorithm, Constraints, Testing
- Target: <30 min to write, <5 min to review

---

### 3. Branch Management SOP

**Trigger:** Realized `project/raise-cli` branch had drifted to include framework work

**Deliverable:** `dev/sops/branch-management.md` (663 lines)

**Contents:**
- Branch naming: `<type>/<scope>/<description>`
- 7 branch types: feature/, framework/, experiment/, bugfix/, hotfix/, docs/, refactor/
- Scope definition template (document before creating branch)
- Daily scope check ritual (session start)
- Weekly branch hygiene (Friday review)
- Rename vs split decision matrix
- Parking lot discipline
- Common drift patterns and prevention
- Automated guardrails (pre-commit hook)
- Good vs bad examples

**Memory Update:** CLAUDE.md now references branch management SOP in Git Practices section

---

## Key Decisions

### Decision 1: Do Meta-Research First

**Context:** Needed to research lean spec formats for F1.1
**Decision:** First research "how to research" then apply it
**Rationale:** Get the process right once, use it many times (20+ features in backlog)
**Outcome:** ✓ SUCCESS - Research template validated by dogfooding

### Decision 2: Dogfood the Research Template

**Context:** Had just created research prompt template
**Decision:** Use it immediately for lean spec research
**Rationale:** "As above, so below" - validate what we build
**Outcome:** ✓ SUCCESS - Template worked well; minor adjustments identified

### Decision 3: Rename Branch to Match Reality

**Context:** Branch named `project/raise-cli` but contained framework work
**Decision:** Rename to `foundation-jan2026` to reflect actual scope
**Rationale:** Branch name should match content; this was foundation sprint work
**Outcome:** ✓ Completed; prompted creation of branch management SOP

### Decision 4: Create SOP to Prevent Future Drift

**Context:** Recognized scope drift as recurring pattern
**Decision:** Document professional SOPs for branch management
**Rationale:** Learn from experience; prevent future issues
**Outcome:** ✓ SUCCESS - Comprehensive SOP created; added to memory system

---

## Challenges & Solutions

### Challenge 1: Tool Availability Variance

**Issue:** ddgr failed (HTTP 202), llm/perplexity not installed
**Solution:** Used WebSearch fallback; documented in research prompt template
**Learning:** Research infrastructure must handle tool unavailability gracefully

### Challenge 2: Scope Drift Unnoticed

**Issue:** Branch scope evolved from project to framework work without early recognition
**Solution:** Created branch management SOP with daily check ritual
**Learning:** Need explicit scope checks at session start to catch drift early

### Challenge 3: Research Taking Longer Than Expected

**Issue:** Meta-research + lean spec research took 5-6 hours
**Solution:** Accepted as investment; quality over speed
**Learning:** Research time is proportional to decision importance; this was foundational

### Challenge 4: Balancing Depth vs Timeline

**Issue:** Feb 9 deadline approaching but doing research instead of implementation
**Solution:** Prioritized getting process right; will pay off across 20+ features
**Learning:** Strategic slowdown (research) enables tactical speedup (implementation)

---

## Metrics

### Quantitative

| Metric | Value |
|--------|-------|
| Duration | ~6-7 hours |
| Files created | 17 |
| Lines written | ~5,200 |
| Research sources | 45 (20 meta + 25 lean specs) |
| Evidence catalogs | 2 |
| Templates created | 2 (research prompt + feature spec v2) |
| Katas created/updated | 2 (feature/design new, tools/research v1.1.0) |
| SOPs documented | 1 |
| Commits | 2 (framework + SOP) |
| Confidence level | HIGH (72-75% of critical factors) |

### Qualitative

**Research Quality:** Very High
- Systematic evidence gathering
- Proper triangulation (3+ sources per major claim)
- No contested claims
- Confidence levels explicit

**Dogfooding Success:** ✓ Validated
- Research template used successfully
- Only minor adjustments needed
- Process worked as designed

**Process Improvement:** ✓ Documented
- Branch management SOP comprehensive
- Added to memory system
- Future drift preventable

---

## Learnings & Insights

### What Worked Well

1. **Meta-research first approach** - Getting process right before using it
2. **Dogfooding immediately** - Using new template for next research validated design
3. **Inference economy discipline** - Used WebSearch instead of burning tokens
4. **Parallel tool calls** - Multiple searches at once for efficiency
5. **Evidence-based decisions** - 45 sources gave high confidence
6. **Acknowledging scope drift** - Renaming branch honestly instead of forcing fit
7. **Creating SOP immediately** - Documenting learning while fresh

### What Didn't Work Well

1. **Branch naming upfront** - Started as `project/raise-cli` but evolved
   - **Fix:** Use `experiment/` for discovery work (expect to rename)
2. **No daily scope check** - Didn't notice drift until end of session
   - **Fix:** Daily check ritual now in SOP (session start)
3. **Tool availability assumptions** - Expected ddgr/perplexity to work
   - **Fix:** Fallback chain documented; check availability first

### Improvements for Future Sessions

1. **Session Start Ritual:**
   ```markdown
   1. State session type and goal
   2. Check branch: git diff v2 --name-only (does it match scope?)
   3. Review parking lot for deferred items
   4. Confirm timeline vs complexity
   ```

2. **Use `experiment/` for Discovery:**
   - If scope uncertain, use `experiment/` type
   - Rename when scope becomes clear
   - Document evolution in commits

3. **Time-box Research:**
   - Set max time upfront (e.g., "4 hours max")
   - Check at 2-hour mark: sufficient evidence?
   - Parking lot tangent discoveries

4. **Validate Templates Immediately:**
   - Dogfood new templates in same session
   - Iterate while context is fresh
   - Don't wait weeks to validate

5. **Commit Smaller, More Often:**
   - Commit research output as created
   - Don't accumulate 17 files before committing
   - Easier to revert if needed

---

## Paradigm Shifts Identified

### Shift 1: Research is Infrastructure Work

**Traditional:** Research is pre-work; document and discard
**RaiSE:** Research outputs are versioned artifacts; templates are code

**Implication:** `work/research/` is not temporary; it's evidence base for decisions

### Shift 2: Specs ARE Prompts for AI

**Traditional:** Specs for humans; code for machines
**AI-Assisted:** Specs consumed by both humans AND AI

**Implication:** Optimize specs for Claude's context processing (examples, emphasis, structure)

### Shift 3: Branch Drift is Normal in Discovery

**Traditional:** Branch scope should never change
**Agile/Lean:** Discovery work naturally evolves scope

**Implication:** Use `experiment/` type; rename early; document evolution

### Shift 4: SOPs Should Be Living Documents

**Traditional:** Write SOP once, set and forget
**Kaizen:** SOPs evolve based on experience

**Implication:** `dev/sops/` with version control; review quarterly; update as we learn

---

## Next Session Preparation

### Immediate Next Steps

1. **Push foundation-jan2026 branch**
   ```bash
   git push -u origin foundation-jan2026
   ```

2. **Create MR to v2** (or continue working on branch)

3. **Apply feature spec v2 to F1.1**
   - Create `work/features/f1.1-project-scaffolding/design.md`
   - Use feature/design kata
   - Validate template with real feature
   - Measure: creation time, review time, AI alignment

4. **Iterate based on F1.1 learnings**
   - Adjust template if needed
   - Update kata based on experience
   - Document in commit

5. **Create ADR: Lean Feature Spec Adoption**
   - Document decision to use v2 template
   - Reference research evidence
   - Mark v1 as legacy

### Context for Next Session

**Where we are:**
- ✓ Research infrastructure complete
- ✓ Feature spec v2 template ready
- ✓ Branch management SOP in place
- ⏳ Need to validate templates with F1.1
- ⏳ Then implement F1.1 (Project Scaffolding)

**Timeline:**
- Feb 9: Friends & Family pre-launch (16 days)
- Feb 15: Public launch (21 days)
- Backlog: 22 MVP features, 92 SP

**Critical path:**
- Validate spec template with F1.1 (1 session)
- Implement F1.1-F1.6 (Core Foundation - 22 SP)
- Then proceed to Kata/Gate engines

---

## Artifacts Created

### Research Outputs
```
work/research/ai-research-prompts/
├── README.md                      (15-min overview)
├── recommendation.md              (template design + kata updates)
├── synthesis.md                   (triangulated findings)
└── sources/evidence-catalog.md    (20 sources, rated)

work/research/lean-feature-specs/
├── README.md                      (5-min overview)
├── prompt.md                      (dogfooding: used new template)
├── recommendation.md              (v2 template + feature/design kata)
├── synthesis.md                   (8 critical success factors)
└── sources/evidence-catalog.md    (25 sources, rated)
```

### Templates
```
.raise/templates/tools/
├── research-prompt.md             (NEW - structured research template)
└── examples/
    └── tech-stack-evaluation-prompt.md

.raise/templates/tech/
└── tech-design-feature-v2.md      (NEW - lean feature spec)
```

### Katas
```
.raise/katas/feature/
└── design.md                      (NEW - 8-step feature spec process)

.raise/katas/tools/
└── research.md                    (UPDATED - v1.1.0 with tool selection)
```

### SOPs
```
dev/sops/
└── branch-management.md           (NEW - 663 lines, comprehensive)
```

### Memory/Context
```
CLAUDE.md                          (UPDATED - Git Practices section)
.raise/templates/README.md         (UPDATED - v2 references)
```

---

## Session Retrospective Summary

### Keep Doing ✓

- Meta-research before implementation
- Dogfooding immediately
- Evidence-based decisions (triangulated sources)
- Inference economy (use tools, not tokens)
- Creating SOPs when patterns emerge
- Honest branch naming (rename when scope evolves)
- Comprehensive commit messages

### Start Doing ⭐

- Daily scope check at session start
- Use `experiment/` for discovery work
- Time-box research sessions
- Commit smaller, more often
- Validate templates immediately

### Stop Doing ❌

- Assuming tools are available without checking
- Letting scope drift go unnoticed
- Accumulating many files before committing
- Using ambiguous branch types (like `project/`)

---

## Quality Assessment

**Research Quality:** ⭐⭐⭐⭐⭐ (5/5)
- Systematic, evidence-based, triangulated
- High confidence levels (72-75%)
- Reproducible process

**Implementation Quality:** ⭐⭐⭐⭐⭐ (5/5)
- Templates comprehensive and usable
- Katas clear and actionable
- Evidence-based design

**Process Quality:** ⭐⭐⭐⭐☆ (4/5)
- Good: Research, dogfooding, SOP creation
- Improvement: Branch scope control, daily checks

**Timeline Impact:** ⭐⭐⭐☆☆ (3/5)
- Strategic investment but high time cost
- Should pay off across 20+ features
- Need to validate ROI with F1.1

**Overall:** ⭐⭐⭐⭐☆ (4.5/5) - Excellent quality, strategic value, with room for process improvement

---

## Quotes from Session

> "Yes please go ahead lets beggin dogfooding ourselves, that's the way we roll." - Emilio

> "Quality all the way. As above so below" - Emilio (on meta-research approach)

> "ok and how do we sync our work branches withs that. it all needs to be below v2" - Emilio (catching branch structure issue)

> "we do need a process to prevent this from happening to us. We drift, with a reason and we may find later better to rename the branches. What are the SOPs in professional development environment for this kind of things?" - Emilio (recognizing need for SOPs)

---

**Session Status:** COMPLETE
**Ready for:** Validation (F1.1) → Implementation → Launch

---

*Foundation laid. Process validated. Ready to build.*
