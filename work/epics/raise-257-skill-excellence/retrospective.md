# Epic Retrospective: E250 Skill Excellence

**Completed:** 2026-02-23
**Duration:** 1 day (started 2026-02-23)
**Stories:** 4 stories delivered

---

## Summary

Redesigned all 27 built-in RaiSE skills to follow the ADR-040 canonical contract: 7 sections, ≤150 lines, ≥80% substance ratio. Total skill lines reduced from ~8,800 to ~3,100 (-65%). Updated the validator and scaffold template to enforce the contract going forward.

## Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Stories Delivered | 4 | M + M + S + XS |
| Lines Removed | ~5,700 net | 83 files, +5699 -13153 |
| Skills Refactored | 27 | All built-in skills |
| Average Velocity | ~3.4x | Across all stories |
| Calendar Days | 1 | Single session day |
| Commits | 41 | On epic branch |

### Story Breakdown

| Story | Size | Velocity | Key Learning |
|-------|:----:|:--------:|--------------|
| S250.1: Contract infra + pilot | M | — | Pilot validates target on 3 diverse skills; preamble extraction works |
| S250.2: Lifecycle skills | M | 5.33x | Batch refactoring with established pattern is mechanical |
| S250.3: Utility skills | S | 4.8x | PAT-E-442 confirmed: 3rd batch is fastest |
| S250.4: Compliance validation | XS | 1.5x | Sync script has double-write bug; silent parse failures hide non-compliant skills |

## What Went Well

- **Research-first approach:** ADR-040 grounded in 23-source evidence catalog. "Compliance ≈ p(each)^n" insight drove the ≤15 rules target.
- **Pilot-then-batch:** S250.1 pilot on 3 diverse skills (smallest/most-used/largest) validated the 150-line target before committing to batch refactoring.
- **Compounding velocity:** PAT-E-442 confirmed — each batch got faster (normal → 5.33x → 4.8x). Pattern established in S250.1, refined in S250.2, mechanical in S250.3.
- **Massive compression:** 65% reduction in total skill lines while preserving all essential content. Decision tables replaced prose paragraphs throughout.
- **Shared preamble:** Cross-cutting content (ShuHaRi definitions, step format, graph context) extracted once, eliminating ~50 lines of duplication per skill.

## What Could Be Improved

- **Sync script reliability:** `update_distributable_list` in `scripts/sync-skills.py` has a bracket-matching bug that duplicates the list. Manual fix was needed in S250.4.
- **Validator completeness:** Skills that fail Pydantic parse (missing `raise.version`) are silently skipped — they don't show up in the error count. Should surface as validation errors.
- **Full test suite earlier:** S250.4 committed the sync before running the full suite, missing the broken `__init__.py`. Pattern captured as PAT-E-480.

## Patterns Discovered

| ID | Pattern | Context |
|----|---------|---------|
| PAT-E-442 | Repetitive extractions compound (3rd batch = mechanical) | Batch refactoring across modules |
| PAT-E-480 | Run full test suite after sync-skills.py (not just validator) | Sync operations |
| PAT-E-481 | Silent parse failures hide non-compliant skills in validator | Skill auditing |

## Process Insights

- **Decision tables > prose:** Converting conditional logic to tables consistently saved 40-60% lines while improving agent compliance (U-shaped attention means tables are easier to follow than paragraphs).
- **7-section contract as forcing function:** Having an exact section count forced extraction of shared content into the preamble. "Where does this go?" always has an answer.
- **Escape valve works:** The ≤150 line target with documented escape valve (≤200 for top-3 complex) was never needed — all skills fit within 150 after compression.

## Artifacts

- **Scope:** `work/epics/raise-257-skill-excellence/scope.md`
- **Stories:** `work/epics/raise-257-skill-excellence/stories/` (16 docs)
- **ADR:** ADR-040 (Skill Contract)
- **Research:** `work/research/skill-contract/` (RES-SKILL-CONTRACT-001)
- **Preamble:** `src/rai_cli/skills_base/preamble.md`
- **Contract template:** `src/rai_cli/skills_base/contract-template.md`

## Next Steps

- Fix sync script double-write bug (deferred from S250.4)
- Make validator surface parse errors as validation errors (deferred from S250.4)
- Merge to `v2` (this close step)
- Next release: include skill excellence in changelog
