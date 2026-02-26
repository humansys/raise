---
epic_id: "RAISE-292"
title: "TDD Policy Reform — Design"
created: "2026-02-26"
---

# Epic Design: TDD Policy Reform

## Gemba Walk (Current State)

### What the code says

1. **pyproject.toml** — No `--cov-fail-under`. Coverage runs as informational (`--cov=src/rai_cli`).
   The hard gate was already removed at some point.

2. **governance/guardrails.md** — `MUST-TEST-001` says "informative, no fixed gate" and principle #4
   is "Test What Matters." This is already aligned with our goal.

3. **governance/guardrails-stack.md** — **Contradicts guardrails.md:**
   - §4.7: "Target: >90% line coverage + >85% branch coverage"
   - Jidoka checklist: "Coverage >90%?"
   - Quick Reference table: ">90% coverage"
   - These are the instructions agents actually follow during implementation.

4. **`/rai-story-implement` skill** — Says "RED → GREEN → REFACTOR" but gives no guidance on
   what makes a good test vs muda. No heuristics for test quality.

5. **CLAUDE.md** — "TDD always" but no definition of what constitutes a meaningful test.

### Test-to-source ratios (measured 2026-02-26)

| Module | Source (lines) | Test (lines) | Ratio | Status |
|--------|---------------|-------------|-------|--------|
| hooks | 744 | 2,070 | 2.7x | Above threshold |
| session | 1,884 | 4,125 | 2.1x | Above threshold |
| gates | 436 | 958 | 2.1x | At threshold |
| telemetry | 614 | 1,242 | 2.0x | At threshold |
| context | 3,656 | 6,324 | 1.7x | Below (improved) |
| memory | 2,166 | 3,272 | 1.5x | Below (improved) |

Context and memory dropped below 2.0x — likely from E247/E248 extractions which moved code
out while leaving tests that were later cleaned up. Only **4 modules** need cleanup, not 6.

### The real problem

The incoherence is not in the CI pipeline (gate already removed) — it's in the **agent instructions**.
`guardrails-stack.md` tells agents to target >90% coverage, which directly causes test muda.
The fix is primarily a **documentation coherence** problem with a **skill update** component.

## Key Decisions

### D1: Coverage philosophy
**Decision:** Coverage as diagnostic alarm at 70% floor, not gate. No hard `--cov-fail-under`.
**Rationale:** Already the de facto state. Formalize it.
**Impact:** Update guardrails-stack.md, remove >90% references.

### D2: Test quality heuristics (for agent instructions)
**Decision:** Add explicit heuristics to guardrails-stack.md and /rai-story-implement:
- Each test must assert behavior, not implementation
- No constant assertions (`assert "x" == "x"`)
- No mock-implementation tests (verify internal call was made)
- No magic-number counts (`assert len(items) == 21`)
- Prefer boundary tests (empty, one, many, error) over happy-path-only
**Rationale:** Agents need explicit anti-patterns to avoid muda.

### D3: Cleanup threshold
**Decision:** Clean modules with ratio ≥ 2.0x. Currently: hooks (2.7x), session (2.1x),
gates (2.1x), telemetry (2.0x).
**Rationale:** 2.0x is a reasonable signal of bloat for a CLI tool. Below that, individual
test review is more appropriate than bulk cleanup.

### D4: No ADR needed
**Decision:** No formal ADR for this epic.
**Rationale:** This is a governance coherence fix, not an architectural decision. The direction
(coverage as diagnostic, not gate) was already decided in practice. We're formalizing it.

## Target Components

### Documents to update
1. `governance/guardrails-stack.md` — Remove >90% targets, add quality heuristics
2. `governance/guardrails.md` — Minor: ensure consistency (already mostly correct)
3. `governance/backlog.md` — Update Definition of Done §6
4. `.claude/skills/rai-story-implement/SKILL.md` — Add test quality guidance to Step 2
5. `CLAUDE.md` — Add "test quality over coverage" to Critical Rules

### Test files to clean (per module)
- `tests/**/test_*hooks*` — identify and remove muda tests
- `tests/**/test_*session*` — identify and remove muda tests
- `tests/**/test_*gates*` — identify and remove muda tests
- `tests/**/test_*telemetry*` — identify and remove muda tests

## Story Breakdown

| # | Story | Size | Description | Dependencies |
|---|-------|------|-------------|--------------|
| S292.1 | Governance: update guardrails + DoD | S | Fix guardrails-stack.md contradictions, update DoD, update CLAUDE.md | — |
| S292.2 | Skill: update /rai-story-implement | S | Add test quality heuristics to Step 2, add anti-patterns | S292.1 |
| S292.3 | Cleanup: hooks module (2.7x) | XS | Identify and remove test muda in hooks tests | S292.1 |
| S292.4 | Cleanup: session module (2.1x) | XS | Identify and remove test muda in session tests | S292.1 |
| S292.5 | Cleanup: gates module (2.1x) | XS | Identify and remove test muda in gates tests | S292.1 |
| S292.6 | Cleanup: telemetry module (2.0x) | XS | Identify and remove test muda in telemetry tests | S292.1 |

**Total: 6 stories** (1S + 1S + 4×XS)

### Why no research story
The Gemba Walk revealed the problem is well-understood: governance incoherence between
guardrails.md (correct) and guardrails-stack.md (stale >90% targets). Existing evidence
(PAT-E-444, S211.2 data, parking lot analysis) is sufficient. Research would be muda.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Cleanup removes tests that catch real bugs | Medium | High | Run full test suite after each module cleanup; verify no regression |
| New policy too vague for agents | Low | Medium | Include concrete anti-patterns with examples in guardrails |
| Ratio threshold too aggressive | Low | Low | Start with ≥2.0x, review after first module |

## Done Criteria

- [ ] No >90% coverage targets anywhere in governance docs
- [ ] guardrails-stack.md aligned with guardrails.md on testing philosophy
- [ ] `/rai-story-implement` includes test quality heuristics
- [ ] CLAUDE.md Critical Rules updated
- [ ] Definition of Done updated (backlog.md §6)
- [ ] All 4 target modules below 2.0x ratio
- [ ] Full test suite passes after all changes
- [ ] Retrospective complete
