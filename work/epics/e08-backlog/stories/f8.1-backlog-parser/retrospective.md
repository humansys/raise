# Retrospective: F8.1 Backlog Parser

## Summary

| Field | Value |
|-------|-------|
| **Feature** | F8.1 Backlog Parser |
| **Epic** | E8 Work Tracking Graph |
| **Started** | 2026-02-02 |
| **Completed** | 2026-02-02 |
| **Estimated** | ~45 min (2 SP) |
| **Actual** | ~45 min |
| **Velocity** | 1.0x |

## What Went Well

- **Pattern reuse worked perfectly** — Following the `prd.py` parser pattern made implementation straightforward. The architecture is now proven repeatable.
- **Design spec was accurate** — The regex patterns in the design doc transferred almost verbatim to implementation. Examples were concrete enough to guide coding.
- **Test coverage was easy to achieve** — 93% coverage on new code with 34 tests. The fixture-based approach (temp files) is clean and fast.
- **Real-world validation** — Integration tests against actual `governance/projects/raise-cli/backlog.md` confirmed the parser works on production data (9 epics extracted correctly).
- **Full kata cycle dogfooding** — Design → Plan → Implement → Review cycle produced quality artifacts and useful calibration data.

## What Could Improve

- **Pre-existing brittle tests** — 6 tests fail with hardcoded expectations like `>= 20 concepts`. These break when governance files evolve. Should use relative assertions or skip-if-unavailable pattern.
- **Coverage threshold on partial runs** — Running `pytest tests/governance/parsers/test_backlog.py --cov=...` shows "failure" because global threshold (90%) applies. This is confusing UX.
- **Context compaction timing** — Session compacted mid-implementation, requiring re-read of progress state. Not a problem, but worth noting for session planning.

## Heutagogical Checkpoint

### What did you learn?

1. **Emoji in regex requires attention** — Status normalization needed to check raw string for emoji (`"✅" in raw`) alongside lowercase text matching. Unicode doesn't lowercase.
2. **Table parsing is brittle but sufficient** — Regex for markdown tables works for our consistent format, but wouldn't generalize to arbitrary markdown. Good enough for RaiSE.
3. **ConceptType is extensible** — Adding PROJECT, EPIC, FEATURE was trivial. The model is well-designed for growth.

### What would you change about the process?

1. **Nothing major** — The full kata cycle (design → plan → implement → review) felt right-sized for this feature.
2. **Consider skipping design for XS features** — For Task 1 (extend enum), a design doc would be overkill. Current judgment threshold (>3 components or >5 SP) seems correct.

### Are there improvements for the framework?

1. **Add pattern for parser tests** — The fixture pattern (`tmp_path` + dedent content) should be documented as canonical approach for parser testing.
2. **Fix brittle integration tests** — Tests that assert on real governance files should be more resilient (e.g., `>= 1` instead of `>= 20`, or skip gracefully).
3. **Add calibration data point** — F8.1 at 2 SP took ~45 min with full kata cycle. This is valuable velocity data.

### What are you more capable of now?

1. **Parser creation** — Can confidently create new parsers following established pattern. F8.2 (Epic Parser) will be faster.
2. **Status normalization** — Understand how to handle mixed emoji/text status indicators.
3. **Concept model extension** — Know how to extend the type system for new domain concepts.

## Improvements Applied

- [x] Added calibration data to `.rai/memory/calibration.jsonl` (pending session close)
- [ ] Document parser test fixture pattern (defer to docs sprint)
- [ ] Fix brittle integration tests (defer to maintenance)

## Action Items

- [ ] **F8.2**: Apply same pattern for epic scope doc parsing
- [ ] **Maintenance**: Review and fix brittle integration tests
- [ ] **Docs**: Document parser test pattern when writing developer guide

## Artifacts Produced

| Artifact | Location | Lines/Tests |
|----------|----------|-------------|
| ConceptType extension | `src/raise_cli/governance/models.py` | +3 enum values |
| Backlog parser | `src/raise_cli/governance/parsers/backlog.py` | 298 lines |
| Parser tests | `tests/governance/parsers/test_backlog.py` | 34 tests |
| Design spec | `work/stories/f8.1-backlog-parser/design.md` | 204 lines |
| Implementation plan | `work/stories/f8.1-backlog-parser/plan.md` | 88 lines |
| Progress log | `work/stories/f8.1-backlog-parser/progress.md` | 52 lines |

---

*Retrospective completed: 2026-02-02*
*Next: F8.2 Epic Parser*
