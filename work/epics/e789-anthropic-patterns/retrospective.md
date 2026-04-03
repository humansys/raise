# E-ANTHROPIC Epic Retrospective

## Summary

| Field | Value |
|-------|-------|
| Epic | RAISE-789 (E-ANTHROPIC) |
| Objective | Benchmark Anthropic's published agent patterns against RaiSE |
| Stories | 4/4 complete |
| Total time | ~400 min (~6.7 hours) |
| Gaps evaluated | 16 |
| Evidence items | 52+ |
| Implementation stories | 12 (RAISE-806) |
| ADRs proposed | 1 (ADR-034: P1 reformulation) |
| Patterns documented | 7 (PAT-E-008 through PAT-E-014) |
| Confluence pages | 12 created/updated |
| Strategic decisions | 2 new (STRAT-31, STRAT-32) |

---

## What Went Well

1. **Methodology validated and amortized.** 4-phase approach (deep read → evidence → benchmark → verdicts) required zero adaptation after first application. Velocity improved consistently: 180→90→75→55 min. The methodology is now a reusable template for any systematic evaluation.

2. **ADR-034 was the most valuable unexpected finding.** G13 was mischaracterized in the epic scope. Instead of forcing a verdict, we traced it to the root: P1 itself needed reformulation. This produced more value than any single gap verdict — it unblocks 3+ capabilities while preserving all original protections.

3. **PAT-E-008 (OSS/Enterprise from start) paid off across all 4 stories.** Having the 5th dimension from the beginning made every verdict immediately actionable. No post-analysis reclassification needed.

4. **Research → Strategy pipeline worked.** E-ANTHROPIC findings directly informed STRAT-31 (Partnership Stack), STRAT-32 (Anthropic Partner KR), positioning update (STRAT-15), and the Capability Cockpit. Research wasn't academic — it shaped real strategic decisions same day.

5. **7 Anthropic articles distilled into 12 actionable stories with clear phasing.** Phase 1 (4 stories, priority 4-5) gives an immediate implementation path for release 2.4.0.

---

## What to Improve

1. **URL verification should happen at epic design.** 3 of 4 stories had article URL issues (Art.3→404, Art.8→308 redirect, Art.7→wrong URL). Cumulative ~25 min wasted. Fix: add URL verification step to `/rai-epic-design` for research epics.

2. **S789.1 took almost double estimated.** First application of methodology (180 min vs 125 estimated). The learning curve was steep but amortized quickly. For future research epics, budget 1.5x for the first story.

3. **Epic scope had gaps mischaracterized.** G13 ("contract negotiation") didn't match what Anthropic actually describes. Pre-research validation of gap characterizations would have saved deliberation time — though the deliberation produced ADR-034, so the waste was productive.

4. **Blog post and Confluence publishing done ad-hoc.** Should have been planned as a task in the last story or as a separate documentation story. Instead it was done post-close which made tracking harder.

---

## Heutagogical Checkpoint

### 1. What did I learn?

Three things that will change how I work:

- **RaiSE has the mechanisms, needs the policies.** The pattern repeated across domains: context (mechanisms exist, policy missing), evaluation (gates exist, scoring missing), tools (CLI exists, disclosure missing). The theme is formalization, not invention.

- **P1 as written was a useful lie.** "Humans Define, Machines Execute" protected us for 500+ sessions but stopped describing reality around session 200. The reformulation (ADR-034) is more honest and more useful.

- **Anthropic's evidence quality varies.** Art.6 (multi-agent) has real metrics (90.2%, 40% time reduction). Art.1 and Art.4 are principle-based with examples. Treating all articles as equal evidence would be a mistake — triangulation matters.

### 2. What would I change about the process?

- Add URL verification to epic design
- Budget 1.5x for first story in a new methodology
- Plan documentation/publishing as explicit tasks, not afterthoughts
- Pre-validate gap characterizations before research starts

### 3. Are there improvements for the framework?

Yes — multiple:
- ADR-034 (P1 reformulation) — framework-level governance change
- "Gates Always, Ceremony Scales" (RAISE-808) — process rule refinement
- Scope fence (RAISE-809) — skill improvement
- Progressive disclosure (RAISE-825) — context engineering improvement
- Capability Cockpit as governance artifact — new document type

### 4. What am I more capable of now?

- Systematic evaluation methodology that I can apply to any external source
- Distinguishing scope-level decisions from execution-level optimization (ADR-034 lens)
- Simplicity test (PAT-E-010) as instant OSS/Enterprise filter
- Research→Strategy pipeline: findings to decisions in the same session

---

## Velocity Data

| Story | Estimated | Actual | Velocity | Domain |
|-------|-----------|--------|----------|--------|
| S789.1 | 125 min | 180 min | 0.69x | Context & Harness |
| S789.2 | 125 min | 90 min | 1.39x | Evaluation |
| S789.3 | 100 min | 75 min | 1.33x | Tool & MCP |
| S789.4 | 65 min | 55 min | 1.18x | Multi-Agent |
| **Total** | **415 min** | **400 min** | **1.04x** | — |

---

## Patterns Added During Epic

| Pattern | Description | Story |
|---------|-------------|-------|
| PAT-E-008 | OSS/Enterprise dimension from start of evaluation | S789.1 |
| PAT-E-009 | WebFetch in main thread, not subagents | S789.1 |
| PAT-E-010 | Simplicity test: "Would a developer apply this mid-session?" | S789.2 |
| PAT-E-011 | AC as machine-readable verifiable artifacts | S789.2 |
| PAT-E-012 | Scope negotiation vs execution evaluation distinction | S789.2 |
| PAT-E-013 | Use gaps as test cases for proposed principle changes | S789.3 |
| PAT-E-014 | Verify article URLs before starting research | S789.3 |

---

## Success Criteria — All Met ✅

| Criterion | Evidence |
|-----------|----------|
| All 14+ gaps evaluated | 16 gaps scored on 4+1 dimensions |
| At least 3 Adopt | 4: G5, G7, G12, G14 |
| At least 1 Reject | G1 (CLI-first, complexity > value) |
| G10 tension resolved | "Gates Always, Ceremony Scales" (RAISE-808) |
| RAISE-783 informed | Context policy (RAISE-807) feeds session design |
| Backlog reprioritized | 12 stories in RAISE-806, phased by priority |

---

*Epic retrospective complete: 2026-03-27*
