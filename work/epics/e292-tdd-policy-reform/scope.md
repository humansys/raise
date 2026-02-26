---
epic_id: "RAISE-292"
title: "TDD Policy Reform"
status: "in_progress"
created: "2026-02-26"
branch: "epic/e292/tdd-policy-reform"
jira: "https://humansys.atlassian.net/browse/RAISE-292"
---

# Epic Scope: TDD Policy Reform

## Objective

Eliminate test muda caused by stale >90% coverage targets in agent instructions.
Align all governance documents and skills with the actual policy: coverage as
diagnostic, test quality over test quantity.

## Value

- Agents stop writing tautological tests to hit a number
- Cleanup frees ~2,000 lines of test muda across 4 modules
- Future stories produce fewer, better tests — saving tokens and review time

## Evidence

- **PAT-E-444:** Fixed coverage gates create Goodhart dynamics
- **PAT-E-447:** Pre-implementation arch review + test muda analysis combo
- **S211.2 data:** ~12 of 20 new tests existed for the metric, not for catching bugs
- **Gemba (2026-02-26):** guardrails-stack.md says >90% while guardrails.md says "no fixed gate" — incoherence in agent instructions is the root cause

## Planned Stories

| # | Story | Size | Description | Depends On |
|---|-------|------|-------------|------------|
| S292.1 | Governance: update guardrails + DoD | S | Fix guardrails-stack.md contradictions, update DoD, CLAUDE.md | — |
| S292.2 | Skill: update /rai-story-implement | S | Add test quality heuristics and anti-patterns to skill | S292.1 |
| S292.3 | Cleanup: hooks module (2.7x) | XS | Remove test muda in hooks tests | S292.1 |
| S292.4 | Cleanup: session module (2.1x) | XS | Remove test muda in session tests | S292.1 |
| S292.5 | Cleanup: gates module (2.1x) | XS | Remove test muda in gates tests | S292.1 |
| S292.6 | Cleanup: telemetry module (2.0x) | XS | Remove test muda in telemetry tests | S292.1 |
| S292.7 | Cleanup: schemas module (2.29x) | XS | Remove test muda in schemas tests (~43 lines) | S292.1 |
| S292.8 | Cleanup: adapters module (1.90x) | XS | Remove test muda in adapters tests (~56 lines) | S292.1 |
| S292.9 | Cleanup: context/test_models.py (2.47x) | XS | Remove test muda in context model tests (~78 lines) | S292.1 |

## Out of Scope

- **Research story** — Gemba Walk sufficient; problem is governance incoherence, not knowledge gap
- **Mutation testing CI gate** — too slow; may evaluate mutmut for spot-checks in S292.2
- **Rewriting all tests** — only deletion of tests that fail the 4 heuristics
- **Pre-commit hook changes** — orthogonal concern
- **context module (1.7x)** and **memory module (1.5x)** — initial scan; now partially in scope (test_models.py confirmed muda)
- **rai_base (12x)** — high ratio is artifact of data-only source (markdown/YAML assets); tests are contract tests, not muda
- **test migration (graph/, providers/)** — tests for rai_core/rai_pro packages; tracked separately as RAISE-294
- **context/test_builder.py (2734 lines)** — too large to analyze without dedicated story; deferred

## Done Criteria

- [x] No >90% coverage targets in governance docs
- [x] guardrails-stack.md ↔ guardrails.md coherent on testing
- [x] `/rai-story-implement` includes test quality heuristics
- [x] CLAUDE.md + DoD updated
- [x] 7 target modules cleaned: all deletions justified by heuristic (constant assertions, mock-impl, magic counts, tautological) — ratio measured as outcome, not gate (PAT-E-499)
- [x] Full test suite green (11 pre-existing failures documented, RAISE-293)
- [x] Retrospective complete

## Open Questions

- pre-commit vs RaiSE gates: captured as orthogonal, not blocking this epic

---

## Implementation Plan

### Sequencing Strategy: Quick Wins

No architectural uncertainty — this is governance coherence + mechanical cleanup.
S292.1 establishes the policy, everything else applies it.

### Sequence

| Order | Story | Rationale | Enables |
|-------|-------|-----------|---------|
| 1 | S292.1 — Governance update | **Unblocks all.** Defines the policy that S292.2-6 apply. | S292.2, S292.3-6 |
| 2 | S292.2 — Skill update | Policy must exist before skill can reference it. | — |
| 3-6 | S292.3-6 — Module cleanup (parallel) | Independent modules, no mutual deps. Apply new policy criteria to identify muda. | — |

### Parallel Opportunities

After S292.1 completes:
- **Stream A:** S292.2 (skill update)
- **Stream B:** S292.3-6 (module cleanups — can run in any order or parallel)

S292.2 and S292.3-6 have no mutual dependency. Both only depend on S292.1.
In practice we work sequentially (single developer), but any order works after S292.1.

### Milestones

**M1: Policy Established** (after S292.1 + S292.2)
- Success: All governance docs coherent on testing philosophy. Skill updated.
- Demo: Show guardrails-stack.md, DoD, CLAUDE.md, skill — no >90% references.
- Impact: All future stories immediately benefit from reformed policy.

**M2: Epic Complete** (after S292.3-9)
- Success: All 7 modules cleaned by heuristic (ratio is diagnostic, not gate — PAT-E-499). Full test suite green.
- Demo: Before/after ratio table across all 7 modules.
- Gate: Retrospective complete → `/rai-epic-close`.

### Progress Tracking

| # | Story | Size | Status | Actual | Velocity | Notes |
|---|-------|------|--------|--------|----------|-------|
| S292.1 | Governance update | S | ✅ done | 15 min | 1.67x | 9 files swept |
| S292.2 | Skill update | S | ✅ done | 5 min | 2.0x | QR: 2 fixes (query + bold) |
| S292.3 | Cleanup: hooks (2.7x) | XS | ✅ done | 19 min | 0.63x | 196 lines deleted, ratio 2.78x→2.52x (1.79x ex. wiring) |
| S292.4 | Cleanup: session (2.1x) | XS | ✅ done | 13 min | 1.0x | 94 lines deleted, ratio 2.20x→2.12x, PAT-E-500 |
| S292.5 | Cleanup: gates (2.1x) | XS | ✅ done | 8 min | 1.5x | 21 lines deleted, ratio 2.20x→2.15x (muda in test_protocol.py only) |
| S292.6 | Cleanup: telemetry (2.0x) | XS | ✅ done | 9 min | 1.3x | 123 lines deleted, ratio 1.78x→1.55x |
| S292.7 | Cleanup: schemas (2.29x) | XS | ✅ done | 4 min | 0.5x | 55 lines deleted, 5 tests removed |
| S292.8 | Cleanup: adapters (1.90x) | XS | ✅ done | 8 min | 0.38x | 80 lines deleted, 11 tests removed, QR applied |
| S292.9 | Cleanup: context/test_models.py (2.47x) | XS | ✅ done | 10 min | 0.3x | 102 lines deleted, 7 tests removed, QR: 2 fixes |

### Sequencing Risks

| Risk | Mitigation |
|------|------------|
| S292.1 scope creep (touch too many docs) | Strict boundary: only guardrails-stack, guardrails, DoD, CLAUDE.md |
| Cleanup stories find modules need refactoring, not just test deletion | Cap at test deletion only; refactoring goes to parking lot |
| PAT-E-442 compounding doesn't apply (cleanup is independent per module) | Accept — each XS is isolated, no compounding benefit expected |
