# Retrospective: F7.2 Convention Detection

## Summary
- **Feature:** F7.2 Convention Detection
- **Epic:** E7 Onboarding
- **Started:** 2026-02-05
- **Completed:** 2026-02-05
- **Estimated:** 150 min (plan total)
- **Actual:** ~40 min
- **Velocity:** 3.75x

## What Went Well

1. **Risk assessment upfront paid off** — We discussed the risks (detection accuracy, confidence scoring, scope creep) before diving in. This led to clear scoping: "detect the obvious stuff well."

2. **Simple approach worked** — Regex over AST was the right call. Fast (~85ms), accurate enough, easy to understand and maintain.

3. **Confidence scoring is honest** — The sample-size aware algorithm (LOW for <5 files, capped MEDIUM for 5-10) prevents false confidence. This was a design goal and it works.

4. **TDD kept momentum** — Writing tests first, especially for edge cases (mixed indentation, single-char names), caught issues before they became problems.

5. **Real-world validation** — Testing on raise-commons itself proved the detection is accurate (HIGH confidence, correct conventions detected).

## What Could Improve

1. **Task 7 (fixtures) was unnecessary** — Used pytest `tmp_path` fixtures inline instead of separate fixture files. Could have merged this into other tasks in the plan.

2. **Parallel task execution** — Tasks 3, 4, 5 (style, naming, structure) were planned as parallel but executed sequentially. No real issue, but plan didn't match execution.

## Heutagogical Checkpoint

### What did you learn?

- **Majority voting is simple and effective** — 90% threshold for HIGH confidence works well in practice. No need for ML or complex heuristics.

- **Regex for naming detection is good enough** — Full AST parsing would be more accurate but 10x more complex. Regex catches the common patterns.

- **Sample size matters as much as consistency** — A 100% consistent 3-file project should NOT have HIGH confidence. This insight shaped the algorithm.

### What would you change about the process?

- **The "estudio en la duda, acción en la fe" moment was valuable** — Risk discussion before implementation clarified scope. Would formalize this as part of design phase for HIGH RISK features.

- **Parking lot the quality gate discussion** — Builder-verifier separation insight deserves research, not just noting.

### Are there improvements for the framework?

1. **Feature risk tags** — Epic scopes mark features as HIGH RISK but skills don't have a formal "risk assessment" step. Consider adding to `/feature-design`.

2. **Builder-verifier separation** — Self-review checklists are muda. Worth researching lean approaches to quality gates. (Already parking-lotted)

### What are you more capable of now?

- **Convention detection patterns** — Can apply majority voting + confidence scoring to other detection problems (e.g., detecting architectural patterns, API styles).

- **Regex-based code analysis** — Simple patterns extract surprisingly useful information without AST complexity.

## Improvements Applied

1. **Parking lot updated** — Added "Separation of Builder and Verifier (Lean Quality)" item with research directions.
2. **`/feature-design` v1.1.0** — Added Step 1.5: Risk Assessment for HIGH RISK features with "estudio en la duda" principle.
3. **Known Limitations section** — Added acknowledgment of self-review limitation with pointer to parking lot.

## Patterns to Persist

- **PAT-087:** Majority voting with sample-size aware confidence (HIGH >90% + >10 samples, cap MEDIUM for 5-10 samples) works well for convention detection
- **PAT-088:** Risk assessment conversation before HIGH RISK features clarifies scope and builds confidence ("estudio en la duda, acción en la fe")

## Action Items

- [x] Add risk assessment step to `/feature-design` for HIGH RISK features ✅ Done (v1.1.0)
- [x] Research lean quality gate approaches ✅ Parking lot item created, acknowledged in skill

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 40 |
| Coverage | 91% (conventions.py) |
| LOC | ~400 |
| Velocity | 3.75x |
| Confidence | HIGH on raise-commons |

---

*Retrospective completed: 2026-02-05*
