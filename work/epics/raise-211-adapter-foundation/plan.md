---
epic_id: "RAISE-211"
created: "2026-02-22"
strategy: "risk-first + walking skeleton"
---

# Epic Plan: Adapter Foundation

> Added by `/rai-epic-plan` — 2026-02-22

## Feature Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S211.0: GraphNode class hierarchy | M | None | M1 | Risk-first: hierarchy + deserialization. Foundation for all subsequent stories. |
| 2 | S211.1: Protocol contracts | S | S0 | M1 | Defines all contracts others consume. Pure types, fast. |
| 3 | S211.2: Entry point registry | S | S1 | M2 | Enables registry dispatch for S3/S4/S6. |
| 4 | S211.5: TierContext | S | S1 | M2 | Independent of S2. Can start once contracts exist. |
| 5 | S211.3: rai memory build → registry | M | S0, S2 | M3 | Walking skeleton: proves the architecture works end-to-end. |
| 6 | S211.4: KnowledgeGraphBackend | M | S0, S2 | M3 | Parallel with S3 if capacity allows. |
| 7 | S211.6: rai adapters list/check | S | S2, S5 | M4 | CLI surface — last, needs everything else. Low risk. |

## Milestones

| Milestone | Stories | Success Criteria | Demo |
|-----------|---------|------------------|------|
| **M1: Foundation** | S0, S1 | GraphNode hierarchy works, all 1610 tests pass. Protocols importable, pyright strict clean. | `from rai_cli.adapters.protocols import GovernanceParser` works |
| **M2: Registry** | +S2, S5 | Entry points discover built-in schema/parsers. `TierContext.community()` returns correct tier. | `get_governance_schemas()` returns `RaiSEDefaultSchema` |
| **M3: Integration** | +S3, S4 | `rai memory build` via registry path produces functionally identical graph. `FilesystemGraphBackend.persist()`/`load()` roundtrips. | `rai memory build && rai memory query "epic"` returns same results |
| **M4: Complete** | +S6 | `rai adapters list` shows installed adapters. Epic retro done. | Full CLI demo of adapter ecosystem |

## Parallel Work Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1 (Critical): S0 ──► S1 ──► S2 ──► S3 ──► S6
                                     │             ↑
Stream 2 (Parallel):       S5 ◄──┘  S4 ────────┘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                     M1 ────── M2 ─────── M3 ──── M4
```

**Merge points:**
- After S1: S5 can start in parallel with S2
- After S2: S3 and S4 can run in parallel
- Before S6: S5 must complete (needs TierContext)

## Progress Tracking

| Story | Size | Status | Actual | Velocity | Notes |
|-------|:----:|:------:|:------:|:--------:|-------|
| S211.0 | M | Done ✓ | ~45 min | 2.5x | Pydantic + __init_subclass__ validated |
| S211.1 | S | Done ✓ | ~18 min | 3.3x | Clean greenfield, full ceremony |
| S211.2 | S | Pending | — | — | |
| S211.5 | S | Pending | — | — | |
| S211.3 | M | Pending | — | — | |
| S211.4 | M | Pending | — | — | |
| S211.6 | S | Pending | — | — | |

**Milestone Progress:**
- [x] M1: Foundation (S211.0 + S211.1 done)
- [ ] M2: Registry
- [ ] M3: Integration
- [ ] M4: Complete

## Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| S0 Pydantic + __init_subclass__ edge cases | Medium | Medium | Test auto-registration + model_validator early. Known friction area. |
| S3 regression — builder refactor produces different graph | Medium | High | Snapshot test: serialize graph before/after, diff. Must be identical. |
| S4 serialization — class hierarchy JSON roundtrip | Low | Medium | Test roundtrip early in S4. Registry lookup handles deserialization. |

## Velocity Assumptions

- **Baseline:** ~3x multiplier with full kata cycle (from PAT-E-094, PAT-E-285)
- **S0:** Hierarchy + deserialization. Expect 2-3x (Pydantic interaction needs care).
- **S1-S2:** Pure contracts/plumbing. Expect 3-4x (PAT-E-288: TDD as spec).
- **S3-S4:** Refactor stories. Expect 2-3x (more careful, snapshot validation).
- **Buffer:** 20% for integration surprises.

---

*Plan created: 2026-02-22*
*Next: `/rai-story-start` for S211.0 (GraphNode class hierarchy)*
