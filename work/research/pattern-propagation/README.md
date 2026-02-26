# Research: Pattern Propagation for Multi-Repo Environments (Layer 2)

**Date:** 2026-02-26
**Session:** SES-294
**Status:** Exploration Complete -- Ready for Problem Shaping
**Builds on:** [shared-memory-architecture](../shared-memory-architecture/) (Feb 25), [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) (Feb 26), [temporal-decay-pattern-scoring](../temporal-decay-pattern-scoring/) (Feb 7), [collective-intelligence-lineage](../collective-intelligence-lineage/) (Feb 2)

## Research Question

How can RaiSE propagate learned patterns between repositories in an organization,
with promotion based on statistical evidence, inheritance by scope hierarchy, and
cross-repo reinforcement -- while maintaining pattern quality and relevance?

## TL;DR

Patterns today are knowledge silos: each repo learns independently, teams
reinvent solutions, and organizational learning stalls. Layer 2 adds a
**propagation mechanism** on top of the shared memory server (Layer 0):

1. **Scope hierarchy:** repo -> team -> org -> enterprise
2. **Promotion:** patterns graduate scope when they meet statistical criteria
   (Wilson score + cross-repo validation count)
3. **Inheritance:** new repos automatically receive org-level patterns via
   context bundles
4. **Cross-repo reinforcement:** evaluations from any repo aggregate into a
   single Wilson score -- more repos validating = higher confidence
5. **Conflict resolution:** contextual overrides with traceability (not
   binary right/wrong)

Grounded in SECI (Nonaka), Communities of Practice (Wenger), and Double-Loop
Learning (Argyris). No competitive tool combines statistical confidence,
organizational scope hierarchy, and agent-integrated delivery.

## Contents

- [This README](./README.md) -- Overview, context, and key decisions
- [Pattern Propagation Report](./pattern-propagation-report.md) -- Full analysis with Kurigage scenarios, schema gaps, endpoint designs
- Related: [shared-memory-architecture](../shared-memory-architecture/) -- Server architecture (Layer 0)
- Related: [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) -- Governance rules (Layer 3)
- Related: [collective-intelligence-lineage](../collective-intelligence-lineage/) -- Lineage vision (future)

## Key Decisions

| Dimension | Decision | Rationale |
|-----------|----------|-----------|
| Scope hierarchy | repo -> team -> org -> enterprise | Maps to real org structure; each level has different confidence requirements |
| Promotion model | Auto for repo->team, HITL for team->org | Low-scope promotions are low risk; org-level requires architect review |
| Pattern matching | Jaccard on context keywords (Phase 1) | Uses existing data (context arrays), no ML dependency, catches 80%+ cases |
| Cross-repo scoring | Aggregate raw counts, compute single Wilson | More conservative than averaging per-repo scores; mathematically correct |
| Decay by scope | 30d repo / 45d team / 90d org / 180d enterprise | Org knowledge ages slower than repo hacks; foundational patterns skip decay |
| Conflict resolution | Contextual overrides with traceability | Both can be right; the system supports nuance, not binary rules |
| MVP for Pro launch | Scope column + evaluations table + context bundle + manual promote | Covers 3 of 5 Kurigage scenarios without ML or automation |

## Kurigage Validation

Five scenarios tested against Kurigage's 3-repo structure (Adan/contabilidad, Arnulfo/erp, Sofi/apis, Rodo/architect):

1. Adan discovers pattern, Arnulfo's agent surfaces it during story design
2. Sofi validates a PHP-team pattern in .NET -- cross-stack promotion
3. Pattern fails in ERP -- negative reinforcement reduces confidence
4. Rodo queries org-wide pattern catalog
5. New repo inherits high-confidence org patterns automatically

## Effort Estimate

| Phase | Scope | Effort | Timeline |
|-------|-------|--------|----------|
| Phase 1: Foundation (Pro MVP) | Scope column, evaluations, context bundle, manual promote | L (4-5 stories) | 3-4 weeks |
| Phase 2: Automation | Pattern linking, auto-suggestions, promotion history | L (3-4 stories) | 3-4 weeks |
| Phase 3: Intelligence | Semantic matching, conflict detection, analytics | XL (6-8 stories) | 6-8 weeks |

## Next Steps

1. `/rai-problem-shape` -- Shape Phase 1 into a formal problem brief
2. Gap analysis -- Alembic migration design for new columns + tables
3. Endpoint design -- OpenAPI spec for reinforcement + promotion + context-bundle
4. Kurigage pilot -- Validate with Rodo that the scope model matches their org structure
