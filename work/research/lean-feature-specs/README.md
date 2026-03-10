# Research: Lean Feature Specification Format

> What makes a good story spec for human understanding + AI alignment?
> Research completed: 2026-01-31
> Confidence: HIGH

---

## 5-Minute Overview

### Research Question

**What are the critical success factors for a lean story specification format that optimizes for both human understanding (reviewability, clarity) and AI alignment (sufficient context for accurate code generation)?**

### Decision Context

Design of `feature/design` kata and `.raise/templates/tech/tech-design-story-v2.md` template for RaiSE framework

### Key Finding

**YAML frontmatter + Markdown body with concrete examples and acceptance criteria outperforms prose-only specs for human-AI collaboration.**

**Evidence**: 25 sources (9 Very High, 13 High, 3 Medium evidence level)
**Confidence**: HIGH (72% of critical factors triangulated from 3+ sources)

### Recommendation

**Implement lean story spec template with:**
1. **YAML frontmatter** - Structured metadata (story_id, complexity, etc.)
2. **4 Required sections** - What/Why, Approach, Examples, Acceptance Criteria
3. **4 Optional sections** - Scenarios, Algorithm, Constraints, Testing (use for complex features)
4. **Concrete examples** - Code samples, not just prose (most critical for AI)
5. **Emphasis patterns** - "IMPORTANT", "MUST" for Claude optimization

**Trade-off**: ~30 min to write spec vs better AI alignment + faster human review

**Next Action**: Create v2 template → Validate with F1.1 → Iterate

---

## Navigation

| Document | Purpose | Time |
|----------|---------|------|
| **README.md** (this file) | Quick overview and navigation | 5 min |
| [recommendation.md](./recommendation.md) | Detailed recommendation with template + kata | 20 min |
| [synthesis.md](./synthesis.md) | 8 critical success factors, triangulated | 15 min |
| [sources/evidence-catalog.md](./sources/evidence-catalog.md) | All 25 sources with ratings | 30 min |
| [prompt.md](./prompt.md) | Research prompt used (dogfooding template) | 10 min |

---

## Critical Success Factors (Ranked)

| CSF | Evidence | Confidence | Implication |
|-----|----------|------------|-------------|
| **1. Clarity & Structure** | 6 sources | HIGH | Template must enforce structure; ambiguity = critical defect |
| **2. Examples > Prose** | 5 sources | HIGH | Examples section REQUIRED, not optional |
| **3. Hybrid Format (YAML+MD)** | 4 sources | HIGH | Use YAML frontmatter + Markdown body |
| **4. Iterative Refinement** | 4 sources | HIGH | Specs must be easy to update, Git-friendly |
| **5. Specs as Prompts** | 3 sources | HIGH | Optimize for Claude's context processing |
| **6. What/Why Over How** | 3 sources | HIGH | Focus on goals/constraints, not implementation |
| **7. Formal Specs** | 3 sources | MEDIUM | Overkill for web/CLI; reserve for critical features |
| **8. Gherkin/BDD** | 3 sources | MEDIUM | Optional, use for complex features only |

---

## Template Structure (Proposed)

### Required Sections (4 core)

```
1. What & Why       → Problem + Value (1-2 sentences each)
2. Approach         → Solution approach (high-level)
3. Examples         → Concrete code, API, output (CRITICAL for AI)
4. Acceptance       → MUST/SHOULD/MUST NOT criteria
```

### Optional Sections (progressive disclosure)

```
5. Scenarios        → Gherkin (complex features)
6. Algorithm/Logic  → Pseudocode (non-obvious implementations)
7. Constraints      → Non-functional requirements
8. Testing          → Test strategy (if non-obvious)
```

**Estimated length**: 50-80 lines (simple), 100-150 lines (complex)
**Target time**: <30 min to write, <5 min to review

---

## Paradigm Shifts

### Traditional → AI-Assisted

| Aspect | Traditional | AI-Assisted | Implication |
|--------|-------------|-------------|-------------|
| **Spec consumers** | Humans only | Humans + AI | Optimize for both (examples bridge gap) |
| **Spec detail** | How to implement | What to build | Focus on goals, not steps |
| **Spec lifecycle** | Spec → Code → Done | Spec → Code → Refine Spec → Regenerate | Must support iteration |
| **Value driver** | Prose descriptions | Concrete examples | Examples are first-class |

---

## Evidence Quality

| Metric | Value |
|--------|-------|
| **Total sources** | 25 |
| **Very High evidence** | 9 (36%) |
| **High evidence** | 13 (52%) |
| **Medium evidence** | 3 (12%) |
| **Recent (2024-2025)** | 24 (96%) |
| **Academic research** | 6 (24%) |
| **Vendor guidance** | 3 (12%) |
| **Industry practice** | 13 (52%) |

**No contested claims** - All evidence convergent

---

## Implementation Checklist

### Phase 1: Template Creation ✓ NEXT
- [ ] Create `.raise/templates/tech/tech-design-story-v2.md`
- [ ] Create `.raise/katas/story/design.md`
- [ ] Update `.raise/templates/README.md`

### Phase 2: Validation
- [ ] Apply template to F1.1 (Project Scaffolding)
- [ ] Measure: creation time, review time, AI alignment
- [ ] Document learnings
- [ ] Iterate template

### Phase 3: Rollout
- [ ] Create ADR documenting decision
- [ ] Use v2 for all future features (F1.2+)
- [ ] Mark v1 as legacy

---

## Dogfooding Results

**This research used the new research prompt template** (`work/research/ai-research-prompts/`)

**Observations**:
- ✓ Template helped structure research systematically
- ✓ YAML frontmatter useful for metadata tracking
- ✓ Evidence catalog template worked well
- ✓ Tool selection guidance (WebSearch fallback) was accurate
- ✓ Quality checklist caught gaps before synthesis

**Template validation**: SUCCESS - Research prompt template is effective

---

## Key Insights

1. **Examples are king** - 5 independent sources confirm examples outperform prose for AI
2. **Clarity compounds** - Ambiguity in specs → poor code → security vulnerabilities (not just bugs)
3. **Specs ARE prompts** - Claude reads CLAUDE.md files; specs will be in context - optimize accordingly
4. **Human role shifted** - Define goals/constraints, review outputs; AI handles implementation
5. **Iteration is normal** - 2-3 cycles of spec → code → refine spec → regenerate is expected pattern

---

## What This Enables

For raise-cli development:
- **Faster feature development** - Better AI alignment = less rework
- **Better human oversight** - 5-min review of spec vs 30-min code review
- **Reproducible quality** - Template enforces best practices
- **Iterative improvement** - Specs easy to refine based on AI output

For RaiSE framework:
- **Evidence-based process** - Not opinions, but 25-source research
- **Validated methodology** - Dogfooded our own research template
- **Scalable pattern** - Works for 20+ features in backlog

---

## Sources Summary (Top 5)

1. [Why AI Code Needs Better Requirements](https://www.inflectra.com/Ideas/Topic/Why-Your-AI-Generated-Code-Needs-Better-Requirements.aspx) - Clarity/structure more critical than traditional dev
2. [CLAUDE.md Best Practices (Anthropic)](https://www.anthropic.com/engineering/claude-code-best-practices) - Specs as prompts; use emphasis; iterate
3. [Spec-Driven Development 2025](https://www.softwareseni.com/spec-driven-development-in-2025-the-complete-guide-to-using-ai-to-write-production-code/) - Iterative refinement pattern
4. [SE 3.0 AI Teammates](https://arxiv.org/html/2507.15003v1) - Human role: define goals, review; AI handles implementation
5. [Best Practices AI Coding](https://graphite.com/guides/best-practices-ai-coding-assistants) - Examples + preferences upfront

[Full catalog: 25 sources](./sources/evidence-catalog.md)

---

## Next Steps

1. **Immediate**: Implement v2 template and feature/design kata
2. **This session**: Apply to F1.1 to validate
3. **Next session**: Iterate based on real usage
4. **Before F1.2**: Finalize and create ADR

---

**Research Status**: COMPLETE
**Recommendation Status**: READY FOR IMPLEMENTATION
**Dogfooding Status**: ✓ SUCCESS (validated own template)
**Total Research Time**: ~3 hours (prompt + searches + synthesis)

---

*Research demonstrates: Structured research process works; template is effective; ready to apply to feature development*
