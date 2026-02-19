# Story Scope: RAISE-170 — Temporal Decay and Pattern Scoring

**Epic:** RAISE-168 (Neurosymbolic Memory Density)
**Size:** M
**Branch:** `story/raise-170/temporal-decay-pattern-scoring`
**Started:** 2026-02-19

## Problem

All 346 patterns have equal weight regardless of age, validation frequency, or reinforcement.
A pattern learned yesterday has the same prominence as one from 3 months ago.
Research RES-MEMORY-002 (RQ1 P4, RQ3 AP4) shows graceful forgetting is a required property
of neurosymbolic memory.

## In Scope

- Add scoring metadata to patterns: `last_referenced`, `reference_count`, `reinforcement_count`
- Implement decay function in graph build (time-based weight reduction)
- Update query ranking to use scores (higher-scored patterns surface first)
- Update context bundle assembly to respect pattern scores

## Out of Scope

- Consolidation of similar/redundant patterns (deferred — complex, may be RAISE-171 or new story)
- UI or visualization of scores
- Cross-project pattern sharing or normalization
- Changes to pattern content or schema beyond scoring metadata

## Done When

- [ ] Scoring metadata fields present in pattern schema (Pydantic model updated)
- [ ] Decay function implemented and applied during `rai memory build`
- [ ] `rai memory query` returns patterns ranked by score
- [ ] Context bundle includes top-scored patterns first
- [ ] Tests pass (coverage ≥ 90%)
- [ ] Pyright and ruff pass
- [ ] Retrospective complete
