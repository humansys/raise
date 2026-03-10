# Epic Retrospective: E16 Incremental Coherence

**Completed:** 2026-02-09
**Duration:** 2 days (started 2026-02-08)
**Stories:** 5 delivered (3S + 2M)

---

## Summary

E16 closed the coherence loop between code and architecture documentation. Starting from a graph that was blind to actual code structure, we built code-aware analysis (S16.1), a graph diff engine (S16.2), a docs-update skill (S16.3), and wired it all into the story lifecycle (S16.4). Architecture docs now auto-sync with code truth on every story close.

---

## Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Stories Delivered | 5 | 3S + 2M |
| Commits | 49 | On epic branch |
| Tests Added | 83 | Across 8 test files |
| Test Coverage | 92.61% | Above 90% gate |
| Calendar Days | 2 | |

### Story Breakdown

| Story | Size | Actual | Velocity | Key Learning |
|-------|:----:|:------:|:--------:|--------------|
| S16.1: Code-Aware Graph | S | 30 min | 1.5x | Real drift detected day one — justified the entire epic |
| S16.5: Component ID Uniqueness | S | - | 1.5x | Jidoka caught unforeseen collision (345/345 unique) |
| S16.2: Graph Diff Engine | M | 35 min | 1.71x | Deliberate design → zero rework, 39 tests, 8 design decisions |
| S16.3: Docs Update Skill | M | 120 min | 0.75x | Narrative drift harder than frontmatter; trigger A/B pattern emerged |
| S16.4: Lifecycle Integration | S | 10 min | 1.5x | Clean wiring when upstream skill owns HITL |

---

## What Went Well

- **Prerequisite-first sequencing** paid off — each story built cleanly on the last with zero rework
- **S16.1 validated the epic on day one** — real code analysis immediately found drift between docs and code
- **S16.2 deliberate design** produced zero-rework implementation with 39 tests
- **Skill-as-step composition** (S16.4) proved trivially simple when S16.3 owned its own HITL
- **Two-day epic** for a coherence infrastructure that will compound across all future stories

## What Could Be Improved

- **S16.3 was 0.75x** — narrative drift detection is harder than mechanical frontmatter comparison. The trigger A/B pattern was discovered during implementation, not design
- **Flaky integration tests** (test_diff_integration.py) — tests that depend on real graph node counts break when the codebase grows. Need a more stable assertion strategy
- **No progress.md** files — skipped progress tracking for speed; acceptable for S-sized stories but would help for M-sized ones

## Patterns Discovered

| ID | Pattern | Context |
|----|---------|---------|
| (from S16.1) | Real code analysis validates architecture assumptions — run it early | When starting coherence or drift work |
| (from S16.2) | Deliberate design with explicit decisions produces zero-rework implementation | For M+ stories with multiple design choices |
| (from S16.3) | Narrative drift is harder than frontmatter drift — mechanical triggers help | When updating prose sections from data changes |
| (from S16.4) | Skill-as-step composition is trivial when upstream skill owns HITL | When integrating skills into lifecycle flows |

## Process Insights

- **Epic sequencing matters more than individual story estimates** — the prerequisite chain (S16.1→S16.5→S16.2→S16.3→S16.4) meant each story had exactly the foundation it needed
- **ADR-025 (Incremental Coherence)** proved viable — the three-layer architecture (code analysis → diff engine → skill) worked as designed
- **Skill definitions are powerful wiring** — S16.4 delivered in 10 minutes because it was pure Markdown integration, no code

---

## Artifacts

- **Scope:** `work/epics/e16-incremental-coherence/scope.md`
- **Stories:** `work/epics/e16-incremental-coherence/stories/`
- **ADRs:** ADR-025 (Incremental Coherence)
- **Skills:** `/docs-update` (new), `/story-close` Step 1.75 (modified)
- **Code:** `src/rai_cli/context/analyzers/`, `src/rai_cli/context/diff.py`
- **Tests:** 83 new tests across 8 files

---

## Next Steps

- Fix flaky `test_diff_integration.py` tests (known, low priority)
- Document "skill-as-step" composition pattern (parking lot from S16.4)
- Next epic TBD

---

*Epic retrospective — captures learning for continuous improvement*
