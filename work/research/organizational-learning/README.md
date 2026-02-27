# Research: Organizational Learning for Multi-Repo Environments (Layer 4)

**Date:** 2026-02-26
**Session:** SES-294
**Status:** Exploration Complete -- Ready for Problem Shaping
**Builds on:** [shared-memory-architecture](../shared-memory-architecture/) (Feb 25), [cross-repo-visibility](../cross-repo-visibility/) (Feb 26), [pattern-propagation](../pattern-propagation/) (Feb 26), [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) (Feb 26)

## Research Question

How can RaiSE aggregate data from shared graphs, patterns, telemetry, and
governance compliance across multiple repositories to provide organizational
learning -- including health scorecards, velocity trends, risk heatmaps, and
evidence-based improvement recommendations?

## TL;DR

Layer 4 is the capstone of the shared memory capability stack. It aggregates
signals from all three layers below it (cross-repo visibility, pattern
propagation, governance intelligence) plus raw agent telemetry to answer
the question every business owner asks: "Are we actually improving?"

Four pillars:

1. **Health Scorecards** -- Composite per-repo score (7 weighted components)
   with traffic light system for executive view
2. **Velocity & Capacity Intelligence** -- Throughput, cycle time,
   predictability, capacity utilization from agent telemetry
3. **Risk Intelligence** -- Proactive risk heatmap (coverage, governance,
   dependencies, knowledge concentration, velocity anomalies)
4. **Improvement Recommendations** -- Evidence-based suggestions backed by
   pattern statistics and process experiment tracking (double-loop learning)

**Critical design constraint:** Goodhart's Law. Velocity is diagnostic ONLY,
never a target. Coverage is a signal, not a gate. Composite scores are harder
to game than individual metrics. The Goodhart section (Section 7) is the most
important section in the report.

## Contents

- [This README](./README.md) -- Overview, context, and key decisions
- [Organizational Learning Report](./organizational-learning-report.md) -- Full analysis (~950 lines) with Kurigage scenarios, metrics framework, DORA mapping, schema gaps, endpoint designs
- Related: [shared-memory-architecture](../shared-memory-architecture/) -- Server architecture (Layer 0)
- Related: [cross-repo-visibility](../cross-repo-visibility/) -- Dependencies, impact, duplicates (Layer 1)
- Related: [pattern-propagation](../pattern-propagation/) -- Scope hierarchy, promotion, cross-repo reinforcement (Layer 2)
- Related: [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) -- Compliance, poka-yoke, waivers (Layer 3)

## Relationship to Capability Layers

```
  4. Organizational Learning        <-- THIS RESEARCH
     scorecards, trends, risk, recommendations
  3. Governance Intelligence        (researched -- Feb 26)
     compliance, poka-yoke, waivers, audit
  2. Pattern Propagation            (researched -- Feb 26)
     promote, inherit, cross-repo reinforce
  1. Cross-Repo Visibility          (researched -- Feb 26)
     dependencies, impact, duplicates
  0. Shared Memory (EXISTS -- E275)
     graph sync, patterns, telemetry, query
```

## Key Decisions

| Dimension | Decision | Rationale |
|-----------|----------|-----------|
| Health score model | 7-component weighted composite | Covers governance, quality, architecture, patterns, velocity, waivers, freshness |
| Scoring methodology | Weighted average, configurable weights per org | Different orgs prioritize differently |
| Traffic lights | Green 85+, Yellow 60-84, Red 0-59 | Standard thresholds, tunable |
| Velocity position | Diagnostic ONLY, never target | Goodhart mitigation -- velocity as target causes inflation, gaming |
| Coverage approach | Health score component (15%), not gate | PAT-E-444: fixed gates create Goodhart dynamics |
| Materialization | PostgreSQL materialized views for MVP | Simple, sufficient for 3-repo scale, evolve to TimescaleDB if needed |
| Recommendation engine | Rule-based correlations, not ML | Simple first; ML requires far more data than Kurigage has |
| Experiment tracking | Improvement Kata structure (hypothesis, baseline, measure) | Toyota Kata alignment, scientific method for process changes |
| DORA mapping | Partial (2 of 4 measurable today) | Deployment freq + lead time from existing data; CFR and MTTR need new instrumentation |
| New schema | 2 tables (metric_snapshots, experiments) + 1 materialized view | L4 is aggregation layer, mostly queries over L0-L3 data |
| Audience segmentation | Three views: Jorge (portfolio), Rodo (architecture), leads (sprint) | Each audience sees only what they need |

## Kurigage Validation

Six scenarios tested against Kurigage's structure (Adan/contabilidad, Arnulfo/erp, Sofi/apis, Rodo/architect, Jorge/business):

1. Jorge's monthly dashboard -- portfolio health with traffic lights and recommendations
2. Rodo's architecture health review -- drift, coupling, pattern adoption per repo
3. Sprint retrospective with data -- evidence-based discussion instead of opinions
4. Process experiment -- "Did TDD in erp actually reduce bugs?" with statistical analysis
5. New hire onboarding -- auto-generated knowledge profile from graph + patterns + decisions
6. Early warning -- proactive alert when erp velocity drops 30% with probable root cause

## Effort Estimate

| Phase | Scope | Stories | Timeline |
|-------|-------|---------|----------|
| Phase 1: Foundation (MVP) | Health scores, velocity, basic risks | 5 | 3-4 weeks |
| Phase 2: Intelligence | Trends, recommendations, experiments, early warnings | 4 | 3-4 weeks |
| Phase 3: Experience | Onboarding, DORA, Rovo integration, statistical tests | 4 | 4-5 weeks |
| **Total** | **Full Layer 4** | **13** | **10-13 weeks** |

Note: Assumes L1-L3 prerequisites are implemented.

## Next Steps

1. `/rai-problem-shape` -- Shape Phase 1 into a formal problem brief
2. Prioritize L1-L3 schema prerequisites (cross-repo edges, pattern evaluations, compliance state)
3. Design `metric_snapshots` Alembic migration
4. Validate health score weights with Rodo (do they match Kurigage's priorities?)
5. Prototype Jorge's dashboard via Rovo agent (walking skeleton extension)
