# Retrospective: RAISE-266 Contract Chain Lean

**Story:** RAISE-266
**Branch:** `story/standalone/raise-266-contract-chain-lean`
**Date:** 2026-02-24
**Size:** M
**Estimated:** 45 min | **Actual:** ~25 min | **Velocity:** 1.8x

---

## Summary

Restored the Contract Chain (RAISE-249) in the E250-compliant skills. 5 lifecycle
skills now produce/consume typed artifacts: brief.md, story.md, design.md with
templates externalizing format. All skills ≤150 lines (ADR-040).

**Deliverables:**
- 3 templates: brief.md, story.md, design.md
- 5 skills modified: epic-start, epic-design, story-start, story-design, story-plan
- epic-design trimmed from 164→140 (was over budget, now under)
- Contract chain verified end-to-end

---

## What Went Well

- "Templates carry format, skills reference" strategy resolved the ≤150 lines vs
  rich artifacts tension cleanly
- Risk-first ordering (epic-design first) paid off — hardest task done early
- Tasks 3-6 were mechanical after the pattern was established (PAT-E-442)
- Zero blockers, zero plan deviations

## What to Improve

- E250 should have included a "contract preservation" checklist
- The chain gap existed for ~1 day before detection — acceptable but not ideal
- Future skill refactors should verify inter-skill artifact contracts survive

---

## Heutagogical Checkpoint

1. **Learned:** Templates externalize artifact format so skills stay lean but still
   produce rich typed artifacts. The compression vs richness tradeoff is false when
   you have the right separation.

2. **Would change:** Add a chain integrity check to E250-style compression epics.
   "Which skill produces what? Which skill consumes it?"

3. **Framework improvement:** `rai skill validate` should verify chain integrity:
   skills with `raise.next` should have output artifacts that the next skill references.

4. **More capable of:** Surgical skill editing within tight line budgets. The
   epic-design trim (164→140 while adding features) was precise.

---

## Patterns

- **PAT-E-489 (new):** Contract chain preservation — verify inter-skill artifact
  contracts survive compression. Templates externalize format.
- **PAT-E-442 (reinforced, +1):** Repetitive extractions compound — this was the
  3rd+ skill editing session, mechanical velocity.

---

*Completed: 2026-02-24*
