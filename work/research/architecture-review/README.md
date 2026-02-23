# Research: Architecture Review Heuristics

**Date:** 2026-02-22
**Session:** SES-248
**Decision:** Design of `/rai-architecture-review` skill
**Confidence:** HIGH

## 15-Minute Overview

### Question
What design principles (KISS, DRY, YAGNI, SOLID) are evaluable via LLM-based code review with concrete heuristics?

### Key Conclusions

1. **Design principles manifest as code smells, not metrics.** Speculative Generality, Lazy Element, Middle Man are the detectable indicators of YAGNI/KISS violations.

2. **LLMs are weak at design smells without specific prompts.** Generic "check YAGNI" fails (F1 <0.40). Specific heuristic questions achieve 2.54x better results (ESEM 2024).

3. **Story and epic reviews are fundamentally different lenses.** Story = "did I build this simply?" Epic = "did the whole remain simple across stories?" Emergent problems (cyclic deps, orphaned abstractions) only visible at epic scope.

4. **Beck's four rules unify all principles.** Tests > Intent > No Duplication > Fewest Elements. This hierarchy is the evaluation framework.

5. **False positive mitigation = ask, don't assert.** "Protocol X has one implementation — is a consumer planned?" beats "Remove Protocol X."

### Recommendation
Single skill, two scopes (`story|epic`), 14 heuristics, Beck hierarchy as framework. Complements `/rai-quality-review` (correctness) — doesn't overlap.

## Files

| File | Content |
|------|---------|
| `architecture-review-report.md` | Full findings, triangulated claims, recommendation |
| `sources/evidence-catalog.md` | 15 sources with evidence levels |
