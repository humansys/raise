---
epic_id: "RAISE-292"
title: "TDD Policy Reform"
date_closed: "2026-02-26"
stories: 9
branch: "epic/e292/tdd-policy-reform"
dev_branch: "dev"
---

# Epic Retrospective: E292 — TDD Policy Reform

## Objective Achieved

Eliminated test muda caused by stale >90% coverage targets in agent instructions.
Aligned all governance documents and skills with actual policy: coverage as
diagnostic, test quality over quantity.

## Metrics

### Story Velocity

| Story | Size | Estimated | Actual | Velocity |
|-------|------|-----------|--------|----------|
| S292.1 Governance update | S | 9 min | 15 min | 1.67x |
| S292.2 Skill update | S | 10 min | 5 min | 2.0x |
| S292.3 Cleanup: hooks | XS | 12 min | 19 min | 0.63x |
| S292.4 Cleanup: session | XS | 13 min | 13 min | 1.0x |
| S292.5 Cleanup: gates | XS | 10 min | 8 min | 1.25x |
| S292.6 Cleanup: telemetry | XS | 10 min | 9 min | 1.11x |
| S292.7 Cleanup: schemas | XS | 2 min | 4 min | 0.5x |
| S292.8 Cleanup: adapters | XS | 3 min | 8 min | 0.38x |
| S292.9 Cleanup: context/models | XS | 3 min | 10 min | 0.3x |

Stories S292.7-9 velocity drop explained by QR addition (~5 min each).
QR consistently found real defects — worth the cost.

### Muda Deleted

| Module | Lines Deleted | Tests Removed | Pattern |
|--------|---------------|---------------|---------|
| hooks | 196 | ~15 | tautological, wiring |
| session | 94 | ~8 | tautological |
| gates | 21 | ~3 | tautological |
| telemetry | 123 | ~9 | tautological |
| schemas | 55 | 5 | tautological-constructor |
| adapters | 80 | 11 | tautological-constructor, mock-impl |
| context/models | 102 | 7 | tautological-constructor |
| **Total** | **~671** | **~58** | |

### Pattern Scores (end of epic)

| Pattern | Positives | Evaluations | Wilson |
|---------|-----------|-------------|--------|
| PAT-E-444 (fixed coverage gates → Goodhart) | 7 | 7 | 0.65 |
| PAT-E-503 (mock-impl muda) | 2 | 2 | 0.34 |

## What Went Well

1. **Gemba scan in SES-003** was the right investment — one session produced the
   complete muda catalog for S292.7-9, eliminating re-analysis per story.

2. **QR addition (S292.8-9)** found real defects: import ordering, blank lines,
   misleading test name, incorrect type count. Cost ~5 min, value concrete.

3. **Scope decisions held** — rai_base (12x, data assets), graph/providers
   (RAISE-294 migration), test_builder.py (deferred) all stayed out of scope.

4. **Policy coherence achieved** — guardrails-stack.md ↔ guardrails.md now
   coherent. Agent instructions no longer create Goodhart dynamics.

## What to Improve

1. **QR should be standard for XS cleanup** — not optional. Found bugs in 2/3
   stories where it was run. Low cost, high signal.

2. **Worktree venv isolation (RAISE-293)** — running tests in worktree against
   main repo code is confusing. Next manual worktree should install its own venv.

3. **Velocity estimate for QR stories** — estimate should account for +5 min QR.

## Heutagogical Checkpoint

1. **What did we learn?**
   - QR catches semantic bugs linters can't: misleading names, incorrect counts,
     missing blank lines post-deletion
   - Mock-impl tests (PAT-E-503) test stubs, not contracts — the isinstance and
     incomplete_fails tests are the valuable ones to keep
   - Worktree venv sharing creates invisible test failures — document early

2. **What would we change?**
   - Make QR mandatory in story skill for cleanup epics
   - Add ruff check to verification gate in plan template

3. **Framework improvements?**
   - Candidate pattern: "QR post-cleanup always, even XS"
   - Update `/rai-story-plan` template to include `ruff check` in verification

4. **More capable of?**
   - Distinguishing tautological-constructor (echoes values) from mixed tests
     (tautological assertion + meaningful default assertion)
   - Recognizing structural stubs (needed for isinstance checks) vs test-only stubs

## Open Items → Parking Lot / Backlog

| Item | Destination |
|------|-------------|
| context/test_builder.py (2734 lines) | Future cleanup epic |
| graph/ + providers/ test migration | RAISE-294 |
| Worktree venv isolation | RAISE-293 |
| QR mandatory for cleanup stories | Update `/rai-story-plan` skill |

## Done Criteria Status

- [x] No >90% coverage targets in governance docs
- [x] guardrails-stack.md ↔ guardrails.md coherent
- [x] `/rai-story-implement` includes test quality heuristics
- [x] CLAUDE.md + DoD updated
- [x] 7 target modules cleaned by heuristic
- [x] Suite: 2571 passed (11 pre-existing failures, RAISE-293)
- [x] Retrospective complete
