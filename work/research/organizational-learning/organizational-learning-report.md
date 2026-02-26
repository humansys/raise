# Organizational Learning for Multi-Repo Environments (Layer 4)

**Date:** 2026-02-26 | **Session:** SES-294 | **Author:** Emilio + Claude Opus 4.6
**Builds on:** [shared-memory-architecture](../shared-memory-architecture/) (Feb 25), [cross-repo-visibility](../cross-repo-visibility/) (Feb 26), [pattern-propagation](../pattern-propagation/) (Feb 26), [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) (Feb 26)

---

## 1. Problem Statement

### The "Are We Actually Improving?" Problem

Jorge, Kurigage's business owner, asks a simple question every month: "Are we
on track? Are we getting better?" He gets opinions. Adan says "I think so, we
shipped a lot this sprint." Arnulfo says "Coverage is improving." Sofi says
"the APIs are more stable." Rodo says "I feel like architecture is drifting
in erp."

None of them are wrong. All of them are guessing.

This is the default state of software organizations. Process improvement is
funded on faith, not evidence. An organization adopts TDD, code review, sprint
retrospectives, architectural guardrails -- and has no mechanism to measure
whether any of it actually works. The feedback loop from "we changed our
process" to "outcomes improved" is either missing or anecdote-driven.

```
WHAT JORGE GETS TODAY:

  "How are we doing?"
     │
     ├── Adan: "Good, I think" (impression)
     ├── Arnulfo: "Better than last month" (memory bias)
     ├── Sofi: "Fewer bugs in prod" (recency bias)
     └── Rodo: "We need to watch erp" (gut feeling)

     → Decision: "OK, seems fine. Keep going."
     → Cost: Unknown. Could be leaving 30% improvement on the table.

WHAT JORGE SHOULD GET:

  "How are we doing?"
     │
     └── Dashboard:
         contabilidad  92/100  improving (+4 this sprint)
         erp           74/100  needs attention (coverage, 1 waiver)
         apis          95/100  excellent, stable

         Top risks: erp coverage (62%, target 80%)
         Top win: contabilidad adopted TDD, bug density -35%
         Recommendation: Prioritize erp domain test coverage

     → Decision: "Invest 2 stories next sprint in erp coverage"
     → Cost: Known. Evidence-based allocation.
```

### Individual Learning vs Organizational Learning

Individual learning happens naturally: a developer learns from mistakes, gets
faster with tools, discovers patterns. RaiSE already captures this in
`memory_patterns` -- a developer's accumulated knowledge.

Organizational learning is fundamentally different. It requires:

1. **Aggregation** -- combining signals from multiple individuals and repos
2. **Abstraction** -- turning raw data into actionable insight
3. **Feedback loops** -- connecting process changes to outcome changes
4. **Double-loop learning** -- questioning not just "did we do it right" but
   "are we doing the right thing"

The gap between individual and organizational learning is where most process
improvement dies. A team adopts a practice, individual developers improve, but
the organization has no way to measure the aggregate effect or decide whether
to propagate the practice more broadly.

### Why AI Agent Telemetry Is Unprecedented

Traditional engineering analytics depend on git commits, Jira tickets, and CI
logs. These capture what happened, but not how or why.

AI agent telemetry (`agent_events`) captures something no previous data source
could:

| Data Source | What It Captures | Limitation |
|-------------|-----------------|------------|
| Git | Code changes, timestamps | No context for decisions |
| Jira | Stories, status changes, estimates | No execution detail |
| CI/CD | Build results, deploy times | No development process |
| **Agent events** | **Session durations, tool usage, velocity, design decisions, pattern evaluations, governance checks, errors, pivots** | **New -- no historical baseline** |

An agent event like `story_completed` carries payload with cycle time,
estimated vs actual effort, tools used, patterns applied, governance checks
passed, and whether the story required pivots. This is the equivalent of
having a process observer embedded in every development session -- something
impossible with humans.

### The Cost of Not Learning

When an organization does not close the learning loop:

| Failure Mode | Cost | Kurigage Example |
|-------------|------|------------------|
| Same mistake across teams | 2-5x rework | Arnulfo hits the same SQL-in-service bug Adan solved 3 weeks ago |
| No feedback on process changes | Wasted investment | "We mandated code review 6 months ago -- did bug rates change?" Unknown. |
| Anecdote-driven prioritization | Misallocated effort | Jorge funds a "stability sprint" based on gut feel, while the real risk is erp test coverage |
| No early warning | Late discovery | erp velocity drops 30% over 2 sprints, nobody notices until deadline pressure |
| Knowledge concentration | Bus factor risk | Only Adan understands the fiscal module -- discovered when he goes on vacation |

---

## 2. Four Pillars of Organizational Learning

Layer 4 is not one capability. It is four interconnected capabilities, each
building on data from Layers 0-3:

```
                 ┌──────────────────────────────┐
                 │    ORGANIZATIONAL LEARNING     │
                 │                                │
   ┌─────────────┼──────────────┬────────────────┤
   │   Health     │  Velocity &  │     Risk       │  Improvement
   │ Scorecards  │  Capacity    │ Intelligence   │ Recommendations
   │             │  Intelligence │               │
   │  "How are   │  "How fast   │  "What could   │  "What should
   │   we doing?"│   are we?"   │   break?"      │   we change?"
   └──────┬──────┴──────┬───────┴───────┬────────┴───────┬──────┘
          │             │               │                │
   ┌──────┴──────┬──────┴───────┬───────┴────────┬───────┴──────┐
   │ L3:         │ L0:          │ L1:            │ L2:          │
   │ Governance  │ Telemetry    │ Cross-Repo     │ Pattern      │
   │ Compliance  │ (events)     │ Dependencies   │ Propagation  │
   └─────────────┴──────────────┴────────────────┴──────────────┘
```

### 2.1 Health Scorecards

**Question answered:** "How healthy is each repo? The portfolio?"

A health score is a composite metric that distills multiple dimensions into a
single number per repo. It answers Jorge's question without requiring him to
understand guardrails, patterns, or graph edges.

**Components:**

| Component | Weight (default) | Data Source | What It Measures |
|-----------|-----------------|-------------|------------------|
| Governance compliance | 25% | L3 compliance check | MUST + SHOULD guardrail pass rate |
| Test coverage (domain) | 15% | Agent events / CI | Coverage on domain/business logic |
| Architecture health | 15% | L1 dependency graph | Drift from declared architecture, coupling metrics |
| Dependency freshness | 10% | L1 cross-repo edges | Stale dependencies, outdated contracts |
| Pattern adoption | 15% | L2 pattern evaluations | How many org patterns are adopted in this repo |
| Velocity trend | 10% | Agent events | Is the team accelerating, stable, or decelerating |
| Waiver burden | 10% | L3 waivers | Active waivers count, expired waivers |

**Scoring methodology:**

Each component yields a 0-100 sub-score. The health score is a weighted average:

```
health_score = sum(component_score[i] * weight[i]) for i in components
```

Weights are configurable per org. The defaults above reflect a balanced view.
An org focused on compliance might set governance to 40%; an org focused on
delivery speed might increase velocity trend to 20%.

**Traffic light system:**

| Range | Color | Label | Meaning |
|-------|-------|-------|---------|
| 85-100 | Green | Excellent | No intervention needed |
| 60-84 | Yellow | Needs Attention | Some components below threshold |
| 0-59 | Red | Critical | Significant issues, intervention required |

**Trend tracking:**

The score alone is insufficient. The trend matters more. A repo at 72 and
improving is healthier than a repo at 82 and declining. Trend is calculated
as the linear regression slope over the last 4-6 data points (sprints).

```
contabilidad    92/100  trending up    (+4 from 2 sprints ago)
erp             74/100  trending up    (+6 from 2 sprints ago)
apis            95/100  stable         (no significant change)
```

**Kurigage example:**

```
GET /api/v1/org-learning/health?org=kurigage

{
  "org": "kurigage",
  "calculated_at": "2026-03-15T10:00:00Z",
  "portfolio_score": 87,
  "portfolio_trend": "improving",
  "repos": [
    {
      "repo": "contabilidad",
      "score": 92,
      "trend": "improving",
      "components": {
        "governance_compliance": 100,
        "test_coverage": 87,
        "architecture_health": 90,
        "dependency_freshness": 95,
        "pattern_adoption": 85,
        "velocity_trend": 90,
        "waiver_burden": 100
      },
      "top_risk": null
    },
    {
      "repo": "erp",
      "score": 74,
      "trend": "improving",
      "components": {
        "governance_compliance": 75,
        "test_coverage": 62,
        "architecture_health": 70,
        "dependency_freshness": 85,
        "pattern_adoption": 60,
        "velocity_trend": 80,
        "waiver_burden": 70
      },
      "top_risk": "Test coverage at 62%, below 80% SHOULD threshold"
    },
    {
      "repo": "apis",
      "score": 95,
      "trend": "stable",
      "components": {
        "governance_compliance": 100,
        "test_coverage": 91,
        "architecture_health": 95,
        "dependency_freshness": 90,
        "pattern_adoption": 92,
        "velocity_trend": 95,
        "waiver_burden": 100
      },
      "top_risk": null
    }
  ]
}
```

### 2.2 Velocity & Capacity Intelligence

**Question answered:** "How fast are we? Are we predictable?"

Velocity intelligence aggregates `agent_events` telemetry to provide throughput,
cycle time, and predictability metrics. This is distinct from Jira sprint
reporting because it includes AI-agent-observed data (actual development time,
tool usage, pattern application) rather than just status transitions.

**Core metrics:**

| Metric | Calculation | Source | Unit |
|--------|------------|--------|------|
| Throughput | Stories completed per sprint | agent_events (story_completed) | count/sprint |
| Cycle time | Mean time from story start to close | agent_events (story_started, story_completed) | hours |
| Throughput variability | StdDev of throughput over last 6 sprints | agent_events | coefficient of variation |
| Estimation accuracy | Abs(estimated - actual) / estimated | calibration nodes | percentage |
| WIP | Stories in progress at any time | agent_events | count |
| Flow efficiency | Active work time / total elapsed time | agent_events (session data) | percentage |

**Per-dev, per-team, per-repo aggregation:**

```
THROUGHPUT (stories/sprint, last 6 sprints):

  contabilidad (Adan):    8  9  7  10  8  9   avg=8.5  CV=0.12
  erp (Arnulfo):          6  5  4   6  7  5   avg=5.5  CV=0.17
  apis (Sofi):           10 11  9  10 12 11   avg=10.5 CV=0.09

  Org total:             24 25 20  26 27 25   avg=24.5 CV=0.10

ESTIMATION ACCURACY (last 6 sprints):

  Adan:     +12% overestimate (conservative, predictable)
  Arnulfo:  -18% underestimate (optimistic, unpredictable)
  Sofi:     +5% overestimate (very accurate)
```

**DORA metrics mapping** (see Section 6 for deep dive):

| DORA Metric | RaiSE Approximation | Data Source |
|-------------|---------------------|-------------|
| Deployment frequency | Release nodes per period | graph_nodes (release) + agent_events |
| Lead time for changes | Story start to story close | agent_events |
| Change failure rate | Error events / total events | agent_events (errors, rollbacks) |
| MTTR | Time between error event and resolution | agent_events (needs correlation) |

**Capacity utilization:**

```
CAPACITY VIEW (Sprint 12):

  Adan:     8/10 capacity  [========  ]  (healthy)
  Arnulfo:  11/8 capacity  [===========] (overloaded, explains velocity drop)
  Sofi:     9/10 capacity  [=========  ] (healthy)

  Org WIP:  7 stories in progress (limit: 9)
  Bottleneck: erp has 4 stories in progress (limit: 3)
```

**CRITICAL WARNING: Goodhart's Law applies here.**

Velocity metrics are DIAGNOSTIC ONLY. They must never be used as targets,
incentives, or performance measures. See Section 7 for full analysis.

### 2.3 Risk Intelligence

**Question answered:** "What could break? Where should we worry?"

Risk intelligence synthesizes signals from all layers to identify threats
before they materialize. This is the proactive counterpart to health
scorecards (which are reactive -- they tell you what IS wrong, not what COULD
go wrong).

**Risk taxonomy:**

| Risk Category | Signal Sources | Example |
|---------------|---------------|---------|
| **Stale repo** | Last agent event timestamp, last graph sync | "erp hasn't synced in 3 weeks" |
| **Coverage decline** | Agent events (coverage delta per sprint) | "contabilidad coverage dropped from 87% to 82% in 2 sprints" |
| **Governance erosion** | L3 compliance trend, waiver accumulation | "3 new waivers this sprint, 2 expired waivers unresolved" |
| **Dependency concentration** | L1 cross-repo edges | "apis is a single point of failure -- 8 cross-repo consumers" |
| **Knowledge concentration** | Session nodes per person per module | "Only Adan has sessions in the fiscal module (bus factor = 1)" |
| **Technical debt accumulation** | Waivers + SHOULD violations + drift | "erp has 12 SHOULD violations -- more than last month" |
| **Velocity anomaly** | Throughput trend analysis | "erp throughput dropped 30% in Sprint 12" |
| **Pattern failure** | L2 pattern evaluations with negatives | "PAT-ORG-022 failed in 2 repos this month" |

**Risk heatmap:**

```
RISK HEATMAP: Kurigage (2026-03-15)

                    Coverage  Governance  Dependencies  Knowledge   Velocity   TOTAL
contabilidad         low       low         low           MEDIUM      low        LOW
erp                  HIGH      MEDIUM      low           low         MEDIUM     HIGH
apis                 low       low         HIGH          low         low        MEDIUM

Legend: low = no action | MEDIUM = monitor | HIGH = investigate

PRIORITY RECOMMENDATIONS:
1. [HIGH] erp test coverage at 62% and declining -- invest 2 stories in domain tests
2. [HIGH] apis is critical provider with 0 redundancy -- discuss failover strategy
3. [MEDIUM] Only Adan works on fiscal module -- cross-train 1 more developer
4. [MEDIUM] erp velocity dropped 30% -- correlates with Arnulfo overload (11/8 capacity)
```

**Early warning system:**

The system should proactively emit alerts when risk thresholds are crossed.
These are not real-time alerts (this is not monitoring). They are sprint-level
or weekly signals:

```
EARLY WARNING (Sprint 12 end):

 erp:
   Velocity declined 30% (5 stories vs 7 avg)
   2 waivers expired without resolution (W-001, W-003)
   Coverage dropped to 62% (was 66% last sprint)

   Severity: INVESTIGATE
   Suggested action: Rodo to review with Arnulfo

 apis:
   No warnings this sprint.

 contabilidad:
   No warnings this sprint.
```

**Knowledge concentration (bus factor):**

Session nodes track which developer worked on which modules. By aggregating
session data, we can identify knowledge concentration:

```
KNOWLEDGE DISTRIBUTION: contabilidad

  Module              Developers    Bus Factor    Risk
  fiscal/             Adan          1             HIGH
  billing/            Adan, Jorge   2             MEDIUM
  reports/            Adan          1             HIGH
  infrastructure/     Adan          1             HIGH

  Overall bus factor: 1 (only Adan works on this repo)
  Recommendation: Cross-train at least 1 developer on fiscal/
```

### 2.4 Improvement Recommendations

**Question answered:** "What should we change to get better?"

This is the highest-value capability and the hardest to get right. It moves
from descriptive analytics ("this is what happened") to prescriptive analytics
("this is what you should do").

**Evidence-based recommendations:**

Recommendations must be backed by data, not opinions. The system generates
recommendations by correlating process changes with outcome changes:

```
RECOMMENDATIONS: Kurigage (March 2026)

1. EVIDENCE-BASED: "Adopt TDD in erp"

   Basis: contabilidad adopted TDD in Sprint 8.
   Before TDD: 4.2 bugs/sprint (sprints 1-7)
   After TDD:  2.7 bugs/sprint (sprints 8-12)
   Reduction: 35% (p < 0.05, Mann-Whitney U)

   erp has similar domain complexity. Predicted impact: 25-40% bug reduction.
   Estimated investment: 2 sprints of learning curve (20% velocity dip).

   Recommendation: Start TDD adoption in erp next sprint.
   Track as process experiment (see below).

2. DATA-DRIVEN: "Resolve erp waivers before they compound"

   erp has 3 active waivers, 2 expired.
   Historical correlation: repos with 3+ unresolved waivers
   see 15% velocity decline within 2 sprints (from Kurigage data).

   Recommendation: Dedicate 1 story/sprint to waiver resolution.

3. STRUCTURAL: "Cross-train on fiscal module"

   Bus factor = 1 for contabilidad/fiscal.
   This is Kurigage's highest-value code (tax compliance).

   Recommendation: Pair programming sessions, 2hrs/week for 4 weeks.
```

**Process experiment tracking:**

Double-loop learning requires treating process changes as experiments:

```
EXPERIMENT: TDD Adoption in erp

  Hypothesis: "Adopting TDD in erp will reduce bug density by 25%+"
  Start date: Sprint 13
  Measurement window: 6 sprints (13-18)

  Baseline (sprints 7-12):
    Bug density: 3.8 bugs/sprint
    Velocity: 5.5 stories/sprint
    Coverage: 62%

  Current (sprint 15):
    Bug density: 3.1 bugs/sprint (-18%)
    Velocity: 4.8 stories/sprint (-13%, expected learning curve)
    Coverage: 71% (+9%)

  Status: ON TRACK -- bug density declining as predicted
  Expected velocity recovery: Sprint 16-17
  Statistical significance: Not yet (need 4 more data points)

  Next check: Sprint 16
```

**Double-loop learning (Argyris):**

Single-loop learning: "Did we follow the process correctly?"
- We said TDD, did we do TDD? Yes/No.

Double-loop learning: "Is the process correct?"
- We do TDD, but is TDD the right approach for this context?
- Evidence says TDD reduced bugs 35% in contabilidad (accounting logic).
- Evidence says TDD had no measurable effect in apis (simple CRUD).
- Conclusion: TDD is high-value for complex domain logic, low-value for
  thin API layers. Adjust the guardrail accordingly.

**Pattern to guardrail promotion:**

The strongest signal of organizational learning is when patterns graduate to
guardrails. This means the org has accumulated enough evidence to make a
recommendation into a rule:

```
PROMOTION CANDIDATE:

  Pattern: "Repository pattern for DB access" (PAT-ORG-042)
  Scope: org
  Wilson score: 0.72 (7 positive, 1 negative)
  Repos validated: contabilidad, erp, apis

  Evidence: Bug density in data access code 40% lower in repos
  using repository pattern vs direct SQL.

  Recommendation: Promote to SHOULD guardrail at org level.
  Requires: Rodo approval.

  Note: The 1 negative evaluation was in apis for a CQRS context.
  Suggested guardrail text: "Use repository pattern for data access
  in CRUD contexts. CQRS/event-sourced contexts may use alternatives
  with documented justification."
```

**Anti-pattern detection:**

Patterns with high negative evaluations are anti-patterns -- things the org
has learned NOT to do:

```
ANTI-PATTERNS DETECTED:

  PAT-ORG-055: "Cache frequently accessed entities in memory"
  Wilson score: 0.28 (4 positive, 4 negative)

  Failed in: erp (high-write workload), apis (cache invalidation bugs)
  Succeeded in: contabilidad (read-heavy reporting)

  Conclusion: Context-dependent. Not suitable as org-level pattern.
  Action: Demote to team-level with context guard:
  "Effective for read-heavy workloads. Counterproductive for
  high-write or real-time consistency requirements."
```

---

## 3. Data Sources & Aggregation

### Data Source Inventory

| Data Source | Table/Location | Already Exists? | Organizational Insight |
|-------------|---------------|----------------|----------------------|
| Agent events (story lifecycle) | `agent_events` | Yes | Velocity, throughput, cycle time |
| Agent events (session data) | `agent_events` | Yes | Developer activity, capacity utilization, tool usage |
| Agent events (errors) | `agent_events` | Yes | Error rates, failure patterns, MTTR |
| Memory patterns | `memory_patterns` | Yes | Pattern adoption rates, confidence trends |
| Pattern evaluations | `pattern_evaluations` | No (L2 gap) | Cross-repo validation, anti-pattern detection |
| Guardrail nodes | `graph_nodes` (guardrail) | Yes | Governance rule inventory |
| Compliance state | L3 compliance check | No (L3 gap) | Compliance score per repo |
| Component nodes | `graph_nodes` (component) | Yes | Architecture inventory |
| Dependency edges | `graph_edges` (depends_on) | Yes | Coupling, risk concentration |
| Cross-repo edges | `graph_edges` (cross-repo) | Possible (L1 gap) | Provider/consumer relationships |
| Calibration nodes | `graph_nodes` (calibration) | Yes | Estimation accuracy, predictability |
| Session nodes | `graph_nodes` (session) | Yes | Developer activity per module, knowledge distribution |
| Release nodes | `graph_nodes` (release) | Yes | Deployment frequency |
| Waiver nodes | L3 waiver type | No (L3 gap) | Technical debt tracking, governance exceptions |
| Jira tickets | External (MCP) | External | Backlog health, sprint metrics, epic progress |

### Aggregation Pipeline

Raw data becomes insight through a three-stage pipeline:

```
STAGE 1: COLLECT (per agent event / graph sync)
  └── Raw events stored in agent_events
  └── Graph nodes/edges stored per sync
  └── Patterns stored with evaluations

STAGE 2: AGGREGATE (periodic, per sprint boundary)
  └── Count stories completed per repo per sprint
  └── Calculate mean cycle time per repo
  └── Calculate compliance score per repo
  └── Calculate coverage delta per repo
  └── Aggregate pattern evaluation stats
  └── Count active/expired waivers
  └── Identify session distribution per module

STAGE 3: SYNTHESIZE (on demand or scheduled)
  └── Compute health scores (weighted composite)
  └── Detect trends (regression over 4-6 data points)
  └── Identify risks (threshold violations + anomalies)
  └── Generate recommendations (correlate changes to outcomes)
  └── Produce natural-language summaries for Rovo/dashboard
```

**Materialization strategy:**

Stage 2 aggregations should be materialized, not computed on every query.
Options:

| Approach | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| PostgreSQL materialized views | Simple, built-in, atomic refresh | No incremental refresh, full recompute | Good for MVP |
| Denormalized snapshot table | Full control, incremental updates | Custom code, schema maintenance | Good for scale |
| Time-series extension (TimescaleDB) | Native time-bucketing, continuous aggregates | New dependency | Future option |

**MVP approach:** Materialized views refreshed on sprint boundaries (bi-weekly).
A background job runs `REFRESH MATERIALIZED VIEW CONCURRENTLY` for each
aggregate view. This is sufficient for Kurigage's scale (3 repos, ~100
events/sprint).

---

## 4. Kurigage Scenarios

### Scenario 1: Jorge's Monthly Dashboard

Jorge opens Rovo chat and types: "How are we doing?"

The Rovo Rai Governance agent calls the org-learning API:

```
── Rovo Agent Response ──────────────────────────────────

Portfolio Health: Kurigage (March 2026)

  contabilidad    92/100   Excellent     trending up
  erp             74/100   Needs Work    trending up
  apis            95/100   Excellent     stable

  Portfolio score: 87/100 (was 83 last month)
  Trend: Improving for 3 consecutive months.

Top Wins This Month:
  - contabilidad test coverage reached 87% (+5%)
  - 0 MUST governance violations across all repos
  - TDD adoption in contabilidad reduced bugs 35%

Top Risks:
  - erp test coverage at 62% (target: 80%)
  - 2 expired waivers in erp need resolution
  - Only 1 developer knows the fiscal module in contabilidad

Recommendations:
  1. Invest 2 stories next sprint in erp domain test coverage
  2. Resolve expired waivers W-001, W-003 in erp
  3. Start cross-training on contabilidad fiscal module

Overall: The team is improving. Focus on erp coverage
and contabilidad knowledge distribution.
```

Jorge does not need to understand guardrails, Wilson scores, or graph edges.
He gets a clear answer with traffic lights, trends, and action items.

### Scenario 2: Rodo's Architecture Health Review

Rodo runs a quarterly architecture review. He queries the system:

```
GET /api/v1/org-learning/architecture-health?org=kurigage

ARCHITECTURE HEALTH REPORT: Kurigage Q1 2026

1. DEPENDENCY RISK
   apis is a pure provider (8 incoming cross-repo edges, 0 outgoing)
   All other repos depend on apis. Single point of failure.

   Recommendation: Discuss failover strategy or API gateway
   for critical endpoints (POST /invoices, GET /tax-rates).

2. ARCHITECTURE DRIFT
   erp declared "layered architecture" in discovery scan.
   Current state: 3 direct SQL queries in service classes
   (bypassing repository layer).
   Drift score: 15% of data access bypasses declared pattern.
   Trend: Stable (no new violations this quarter).

   Tracked: W-001 (waiver for StockService.php, expires April 15)

3. PATTERN ADOPTION RATES
                    contabilidad  erp    apis
   Org patterns:    85%           60%    92%
   Team patterns:   90%           70%    88%

   erp has lowest adoption. Top unadopted patterns:
   - "Repository pattern for DB access" (adopted elsewhere)
   - "Integration tests before merge" (partially adopted)

4. COUPLING METRICS
   Internal coupling (within repo):
     contabilidad: 0.35 (healthy)
     erp:          0.52 (moderately coupled)
     apis:         0.28 (well-decoupled)

   Cross-repo coupling: 0.18 (low -- healthy for 3-repo org)

5. COMPONENT GROWTH
   Components added this quarter: +12
   Components deprecated: -3
   Net growth: +9

   Largest growth: apis (+7 new endpoints)
   Concern: Rapid API surface growth without proportional test growth
```

### Scenario 3: Sprint Retrospective with Data

The team runs Sprint 12 retrospective. Instead of "what went well / what
didn't," they start with data:

```
SPRINT 12 DATA PACKAGE

VELOCITY:
  contabilidad:  9 stories (avg: 8.5)    normal
  erp:           5 stories (avg: 7.0)    -29% below average
  apis:         11 stories (avg: 10.5)   normal

  Org total: 25 stories (avg: 26)        -4% (within variance)

CYCLE TIME:
  contabilidad:  4.2 hrs/story (avg: 4.5)   improving
  erp:           7.8 hrs/story (avg: 5.2)    50% above average
  apis:          3.1 hrs/story (avg: 3.3)    normal

GOVERNANCE:
  New violations: 1 (erp, coverage drop)
  Resolved violations: 2 (contabilidad)
  Net compliance change: +1
  Active waivers: 3 (all erp)

PATTERNS LEARNED:
  New patterns this sprint: 4
  - "Batch API calls reduce N+1 queries by 80%" (contabilidad)
  - "Symphony form validation catches 90% of input errors" (erp)
  Patterns reinforced: 7 (across all repos)

RISKS RESOLVED:
  - contabilidad coverage crossed 85% threshold (was 82%)

RISKS EMERGED:
  - erp velocity anomaly (-29%)
  - erp cycle time spike (50% above average)
  - Correlates with: Arnulfo at 137% capacity (11 stories assigned)

DISCUSSION PROMPT:
  "erp velocity dropped because Arnulfo was overloaded.
   Should we rebalance capacity or reduce erp scope?"
```

The retrospective becomes evidence-based. Instead of opinions, the team
discusses data. The discussion prompt is generated by correlating the velocity
anomaly with capacity data.

### Scenario 4: Process Experiment

Rodo proposed adopting TDD in erp 2 months ago. Now Jorge asks: "Did it
actually work?"

```
EXPERIMENT REPORT: TDD in erp

Hypothesis: "TDD in erp reduces bug density by 25%+"
Started: Sprint 9
Current: Sprint 14 (6 sprints elapsed)

BEFORE TDD (Sprints 3-8):
  Bug density:    3.8 bugs/sprint
  Velocity:       7.0 stories/sprint
  Coverage:       58%
  Cycle time:     5.2 hrs/story

AFTER TDD (Sprints 9-14):
  Bug density:    2.6 bugs/sprint (-32%)
  Velocity:       5.8 stories/sprint (-17%, learning curve)
  Coverage:       71% (+13%)
  Cycle time:     6.1 hrs/story (+17%, expected)

STATISTICAL ANALYSIS:
  Bug density reduction: 32% (p = 0.03, Mann-Whitney U test)
  Result: STATISTICALLY SIGNIFICANT

  Velocity dip: -17% (p = 0.08, not yet significant)
  Note: Velocity recovering -- Sprint 14 was 6.5 stories
  Projected recovery to baseline: Sprint 16-17

VERDICT: TDD adoption is working as predicted.
  Bug reduction exceeds 25% hypothesis.
  Velocity dip is within expected learning curve.
  Coverage improvement is a bonus outcome.

RECOMMENDATION: Continue TDD in erp. Consider promoting
  "TDD for domain logic" to org-level SHOULD guardrail.
```

This is double-loop learning in action. The org did not just adopt TDD --
it measured whether TDD works in its specific context, and has data to
inform future decisions.

### Scenario 5: New Hire Onboarding Intelligence

A new developer joins Kurigage and is assigned to the erp repo. The system
generates an onboarding knowledge profile:

```
ONBOARDING BRIEF: erp repository

ARCHITECTURE:
  Type: Layered (Controllers → Services → Repositories → DB)
  Stack: Symphony/PHP
  Domain: Enterprise Resource Planning (inventory, billing, stock)

KEY DECISIONS (from decision nodes):
  ADR-015: Repository pattern for data access (Rodo, 2026-01)
  ADR-019: Event sourcing for inventory changes (Arnulfo, 2026-02)
  ADR-021: API versioning strategy v1/v2 (Sofi+Rodo, 2026-03)

ACTIVE GOVERNANCE:
  MUST:
    - All services must have health check endpoint
    - Breaking API changes require 2-sprint deprecation
  SHOULD:
    - Repository pattern for data access (1 active waiver)
    - 80% coverage on domain logic (currently 71%)

ACTIVE PATTERNS (org-level, relevant to this repo):
  - "Integration tests before merge reduce regression 60%" (0.68 confidence)
  - "Repository pattern for DB access reduces bugs ~40%" (0.72 confidence)
  - "Batch API calls reduce N+1 queries by 80%" (0.65 confidence)

  repo-specific:
  - "Symphony form validation catches 90% of input errors" (0.55 confidence)

EXTERNAL DEPENDENCIES:
  This repo consumes 3 APIs from apis repo (Sofi):
    POST /invoices (1 call site)
    GET /products (1 call site)
    POST /stock-events (1 call site)

  No other repo depends on erp.

CURRENT RISKS:
  - Test coverage below target (71% vs 80%)
  - 1 active waiver (W-001, expires April 15)
  - TDD experiment in progress (Sprint 9+)

WHO TO ASK:
  Arnulfo: Domain expert, primary developer
  Rodo: Architecture decisions
  Sofi: API contracts and integration questions
```

This onboarding brief is auto-generated from the knowledge graph, patterns,
governance rules, and session data. It replaces weeks of "ask around" with
a structured knowledge transfer.

### Scenario 6: Early Warning

The system detects anomalies at sprint boundary and proactively alerts:

```
EARLY WARNING ALERT: Sprint 12 Anomalies

REPO: erp
SEVERITY: Investigate

Signals detected:
  1. Velocity dropped 29% vs 6-sprint average (5 vs 7 stories)
  2. Cycle time increased 50% (7.8 vs 5.2 hrs/story)
  3. 2 waivers expired without resolution (W-001, W-003)
  4. Coverage declined from 66% to 62% (-4%)

  Correlation: Arnulfo assigned 11 stories (capacity: 8).
  Probable root cause: Overload leading to quality shortcuts.

SUGGESTED ACTIONS:
  1. [IMMEDIATE] Rebalance Sprint 13 -- reduce erp to 7 stories max
  2. [THIS SPRINT] Resolve expired waivers (create tickets if needed)
  3. [NEXT SPRINT] Invest 2 stories in coverage recovery

ESCALATION:
  Sent to: Rodo (architect), Arnulfo (tech lead)
  Visible to: Jorge (portfolio dashboard, yellow status)
```

---

## 5. Metrics Framework

### Level 1: Raw Metrics (Collected Automatically)

| Metric | Unit | Source | Collection Frequency |
|--------|------|--------|---------------------|
| Stories completed | count | agent_events (story_completed) | Per event |
| Cycle time per story | hours | agent_events (start - complete) | Per event |
| Session duration | minutes | agent_events (session_start, session_close) | Per event |
| Test coverage % | percentage | agent_events (payload.coverage) | Per story close |
| Guardrails checked | count | agent_events (governance_check) | Per story close |
| Guardrails passed | count | agent_events (governance_check) | Per story close |
| Patterns evaluated | count | pattern_evaluations | Per evaluation |
| Waivers created | count | waiver nodes | Per creation |
| Waivers expired | count | waiver nodes (status check) | Sprint boundary |
| Agent errors | count | agent_events (type=error) | Per event |
| Tools used per session | list | agent_events (payload.tools) | Per session |

**Goodhart risk:** Low. These are raw counts. Difficult to game individually
because they are side effects of actual work.

### Level 2: Composite Metrics (Calculated)

| Metric | Formula | Components | Refresh |
|--------|---------|-----------|---------|
| Health score | Weighted average of 7 components | See Section 2.1 | Sprint boundary |
| Risk score | Max severity across risk categories | See Section 2.3 | Sprint boundary |
| Compliance score | (passed MUST + 0.5*passed SHOULD) / total applicable | L3 compliance | Sprint boundary |
| Velocity index | Throughput / baseline throughput | agent_events | Sprint boundary |
| Predictability index | 1 - abs(estimated - actual) / estimated | calibration nodes | Sprint boundary |
| Pattern confidence trend | Wilson score delta over 3 periods | pattern_evaluations | Monthly |

**Goodhart risk:** Medium. Composite metrics are harder to game than
individual metrics because gaming one component may hurt another. However,
they are still vulnerable if used as targets (see Section 7).

**Kurigage example values (Sprint 12):**

| Metric | contabilidad | erp | apis |
|--------|-------------|-----|------|
| Health score | 92 | 74 | 95 |
| Risk score | LOW | HIGH | MEDIUM |
| Compliance score | 1.0 | 0.75 | 1.0 |
| Velocity index | 1.06 | 0.79 | 1.05 |
| Predictability index | 0.88 | 0.72 | 0.95 |

### Level 3: Insights (Inferred)

| Insight Type | Method | Output | Example |
|-------------|--------|--------|---------|
| Trends | Linear regression over 4-6 data points | Improving / stable / degrading | "erp velocity declining over 3 sprints" |
| Correlations | Pearson/Spearman between metric pairs | "Pattern X adoption correlates with outcome Y" | "TDD adoption correlates with 35% bug reduction (r=0.82)" |
| Anomalies | Z-score > 2.0 vs rolling average | Alert trigger | "erp cycle time 2.3 sigma above mean" |
| Predictions | Linear extrapolation (conservative) | "At current trend, X by date Y" | "erp coverage reaches 80% by Sprint 18 at current pace" |
| Recommendations | Rule-based from correlations + thresholds | Actionable suggestions | "Adopt TDD in erp based on contabilidad evidence" |

**Goodhart risk:** Lower. Insights are derived and qualitative. They cannot
be directly gamed because they are inferences, not measures. However, the
underlying metrics can be gamed (addressed in Section 7).

---

## 6. DORA Metrics Integration

The four DORA metrics from Forsgren, Humble, and Kim's _Accelerate_ research
are the most statistically validated measures of software delivery performance.
RaiSE should map to them where possible.

### Deployment Frequency

**DORA definition:** How often an organization successfully releases to
production.

**RaiSE mapping:**
- `graph_nodes` with `node_type = 'release'` carry timestamps
- `agent_events` with `event_type = 'release_completed'` (needs new event type)
- Aggregation: count release events per period per repo

**What exists today:** Release nodes exist in the graph schema but are not
systematically populated. Agent events do not yet have a release event type.

**Gap:** Need `release_completed` event type in agent_events, populated by
CI/CD hooks or manual `/rai-release` skill.

**Kurigage example:**
```
Deployment frequency (last quarter):
  contabilidad:  2/month   (Low -- monthly cadence)
  erp:           1/month   (Low)
  apis:          4/month   (Medium -- weekly cadence)

  DORA benchmark: Elite = on-demand, High = daily-weekly
  Kurigage: Low-Medium -- room for improvement
```

### Lead Time for Changes

**DORA definition:** Time from code commit to running in production.

**RaiSE mapping:**
- Story nodes have `created_at` and `completed_at` (from agent_events)
- Lead time = story_completed - story_started (this is really cycle time)
- True lead time (commit to production) requires release event correlation

**What exists today:** Story lifecycle events (started, completed) give us
development cycle time. We do not track commit-to-production.

**Gap:** Need to correlate story completion with release events. A story
completed in Sprint 12 but released in Sprint 13 has lead time =
release_date - story_start_date.

**Kurigage example:**
```
Lead time for changes (median, last quarter):
  contabilidad:  5.2 days   (Medium)
  erp:           8.4 days   (High -- longer cycles)
  apis:          2.8 days   (Low -- fast cycles)

  DORA benchmark: Elite = <1hr, High = <1day, Medium = <1week
  Note: These are development lead times, not deployment lead times.
  True deployment lead time requires CI/CD integration.
```

### Change Failure Rate

**DORA definition:** Percentage of deployments causing a failure in production.

**RaiSE mapping:**
- `agent_events` with `event_type = 'error'` or `'rollback'` or `'hotfix'`
- Calculation: error_events / release_events * 100

**What exists today:** Agent events capture errors, but there is no
structured distinction between development errors (normal) and production
failures (concerning).

**Gap:** Need `production_incident` event type or integration with incident
management (PagerDuty, Jira Service Management). This is the hardest DORA
metric to measure from agent data alone.

**Kurigage example:**
```
Change failure rate (last quarter):
  contabilidad:  12%   (Medium)
  erp:           20%   (High)
  apis:            8%  (Low)

  DORA benchmark: Elite = 0-5%, High = 6-15%
  Note: Measured as "stories requiring hotfix within 1 sprint of close"
  (proxy metric -- true CFR requires production monitoring)
```

### Mean Time to Recovery (MTTR)

**DORA definition:** How long it takes to restore service after a failure.

**RaiSE mapping:**
- Requires incident tracking: `incident_opened` -> `incident_resolved`
- Currently: NOT measurable from RaiSE data alone

**What exists today:** Nothing. RaiSE tracks development process, not
production operations.

**Gap:** This metric requires either:
1. Integration with incident management tools (Jira Service Management,
   PagerDuty, OpsGenie) via MCP or webhooks
2. A new `production_incident` event type manually recorded

**Recommendation:** Defer MTTR to Phase 3. It requires operational tooling
integration that is out of scope for the development-focused MVP.

### DORA Summary

| Metric | Measurable Today? | Gap | Priority |
|--------|------------------|-----|----------|
| Deployment frequency | Partially (release nodes) | Need release events | P1 |
| Lead time | Partially (cycle time proxy) | Need release correlation | P1 |
| Change failure rate | No (proxy possible) | Need incident/hotfix tracking | P2 |
| MTTR | No | Need operational tooling integration | P3 |

---

## 7. Goodhart's Law & Anti-Patterns

**"When a measure becomes a target, it ceases to be a good measure."**
-- Charles Goodhart (1975), paraphrased by Marilyn Strathern (1997)

This section is the most important in the entire research. Most engineering
analytics products fail not because their metrics are wrong, but because
their metrics are used wrong. RaiSE must design for this from the start.

### The Fundamental Problem

The moment you show a metric on a dashboard, someone will try to optimize it.
This is not malice -- it is human nature. A manager sees velocity, wants
velocity to go up, rewards teams with higher velocity. The team inflates
story points, splits stories artificially, counts tasks as stories. Velocity
goes up. Actual output stays the same (or decreases, because gaming takes
effort).

This is not hypothetical. It happens in every organization that targets
velocity. The Jellyfish blog documents this phenomenon explicitly:
organizations that reward velocity see story point inflation of 30-50% within
2-3 quarters.

### Metric Safety Classification

Not all metrics are equally dangerous as targets. Here is a classification
for every metric in the framework:

| Metric | Safe as Target? | Risk if Targeted | Mitigation |
|--------|----------------|------------------|------------|
| **Velocity (throughput)** | NEVER | Story inflation, gaming, Goodhart | Diagnostic only. Never display on performance reviews. |
| **Coverage %** | DANGEROUS | Test muda, meaningless tests to hit % | Use as diagnostic, not gate. Cover domain logic, not glue. (PAT-E-444) |
| **Story points** | NEVER | Point inflation, gaming | Use only for estimation, never for productivity. |
| **Cycle time** | CAUTION | Rushing, skipping design/review | Diagnostic only. Contextualize with quality metrics. |
| **DORA deployment freq.** | MODERATE | Smaller, riskier deploys to hit target | Pair with change failure rate to balance. |
| **Compliance score** | SAFER | Binary pass/fail is harder to game | MUST rules are binary -- you comply or you don't. |
| **Health score** | SAFER | Composite is harder to game | Gaming one component may hurt another. |
| **Pattern adoption** | MODERATE | Superficial adoption without understanding | Track adoption AND outcome correlation. |
| **Waiver count** | CAUTION | Underreporting waivers, hiding violations | Pair with audit trail -- waivers are discoverable. |
| **Bug density** | MODERATE | Reclassifying bugs, not filing bugs | Correlate with customer-reported issues. |
| **Estimation accuracy** | MODERATE | Overestimate to be "accurate" | Use range estimation, not point. |

### Why Velocity Is Especially Dangerous

Velocity deserves special attention because it is the most commonly abused
metric in software:

1. **Story point inflation:** Teams learn that bigger numbers = better reviews.
   A story that was 3 points becomes 5, then 8. Velocity "increases" while
   throughput stays flat.

2. **Story splitting:** Instead of 1 medium story, teams create 3 trivial
   stories. Count goes up, value stays the same.

3. **Scope reduction:** Teams cherry-pick easy stories to boost count,
   deferring hard (high-value) work.

4. **Quality shortcuts:** To deliver more stories, teams skip tests, design,
   review. Technical debt accumulates invisibly.

**RaiSE's position on velocity:** Velocity is a team-internal diagnostic
tool. It tells a team whether they are faster or slower than their own
baseline. It must NEVER be used to:
- Compare teams
- Set targets
- Reward or punish
- Report to management as a performance metric

The dashboard should display velocity with an explicit warning label:
```
Velocity: 8.5 stories/sprint (diagnostic only)
  This metric is for team self-assessment. It is not
  comparable across teams and must not be used as a target.
```

### The Coverage Trap (PAT-E-444)

From prior RaiSE pattern research:

> "Fixed coverage gates (e.g., --cov-fail-under=90) create Goodhart dynamics:
> penalize cleanup, incentivize test muda. Use coverage as diagnostic, not
> gate. Cover domain logic and edge cases, not glue/wrappers."

Example: A team has a 90% coverage gate. A developer refactors 500 lines of
untested boilerplate into 50 lines. Coverage drops from 91% to 88% because
the denominator changed. The gate blocks the merge. The developer adds
meaningless tests for getter/setter methods to get back to 90%. The code is
now "tested" but the tests are muda (waste).

**RaiSE's approach:** Coverage is a component of the health score with 15%
weight. It is not a gate. A repo with 62% coverage on domain logic and 40%
on glue code is healthier than a repo with 90% coverage that tests nothing
meaningful. The system should track domain coverage separately.

### Composite Metrics Are Harder to Game

This is a key design principle. A single metric (velocity, coverage) is easy
to game because there is one lever. A composite metric (health score) is
harder to game because:

- Gaming coverage (adding meaningless tests) hurts velocity (time spent on muda)
- Gaming velocity (splitting stories) hurts cycle time (more overhead per story)
- Gaming compliance (not filing waivers) hurts audit trail (discoverable)

The health score's 7 components create natural tension. Optimizing one at the
expense of others is visible in the component breakdown.

### The Observer Effect

Measuring behavior changes behavior. This is not always bad:

**Positive observer effects:**
- Team knows compliance is tracked -> team follows governance -> fewer violations
- Team knows bus factor is visible -> team cross-trains -> lower risk
- Team knows coverage is tracked -> team writes more tests -> fewer bugs

**Negative observer effects:**
- Team knows velocity is tracked -> team inflates points -> metric is useless
- Team knows cycle time is tracked -> team rushes -> quality drops
- Team knows waiver count is tracked -> team stops filing waivers -> hidden violations

**Design principle: Make the positive observer effects easy and the negative
ones difficult.**

How:
1. Make compliance binary (pass/fail) -- can't game binary metrics easily
2. Make velocity descriptive, not prescriptive -- "your velocity is X" not "your target is Y"
3. Make health scores composite -- gaming one component hurts another
4. Make waivers the path of least resistance -- easier to file a waiver than to hide a violation
5. Correlate metrics -- display velocity WITH quality, never alone

### Anti-Pattern: The Dashboard Arms Race

A subtle failure mode: organizations that create increasingly detailed
dashboards with increasingly many metrics, to the point where nobody looks
at any of them. Metric fatigue is real.

**RaiSE's approach:** Three views, three audiences, three levels of detail:

| Audience | View | Metrics Shown | Detail Level |
|----------|------|--------------|-------------|
| Jorge (business) | Portfolio health | Health score, trend, top 3 risks | Traffic light |
| Rodo (architect) | Architecture health | Compliance, coupling, drift, patterns | Component breakdown |
| Tech leads (devs) | Sprint data | Velocity, cycle time, coverage, patterns | Raw data + trend |

Each audience sees only what they need. Jorge never sees velocity. Rodo sees
compliance detail. Tech leads see sprint-level data.

---

## 8. Literature & Theoretical Grounding

### Accelerate / DORA (Forsgren, Humble, Kim, 2018)

The foundational work on measuring software delivery performance. Four key
metrics (deployment frequency, lead time, change failure rate, MTTR)
statistically validated across 30,000+ teams.

**RaiSE connection:** DORA metrics are the industry standard. RaiSE maps to
them where possible (Section 6) but acknowledges gaps. The key insight from
DORA is that throughput and stability are NOT trade-offs -- elite teams are
fast AND stable.

**Design implication:** RaiSE never presents speed metrics without stability
metrics. Velocity is always paired with quality indicators.

### The Fifth Discipline (Senge, 1990)

Five disciplines of learning organizations: personal mastery, mental models,
shared vision, team learning, systems thinking.

**RaiSE connection:** The knowledge graph IS a shared mental model. Patterns
represent team learning. The scope hierarchy (repo -> team -> org) mirrors
Senge's personal -> team -> organizational learning levels.

**Design implication:** Layer 4's recommendation engine supports "team
learning" by making cross-repo insights available. The process experiment
feature supports "systems thinking" by showing how process changes affect
system-level outcomes.

### Double-Loop Learning (Argyris, 1977)

Single-loop: "Are we doing things right?" (correct errors within existing
framework). Double-loop: "Are we doing the right things?" (question the
framework itself).

**RaiSE connection:** Layer 3 (governance) is single-loop: "did we follow the
guardrails?" Layer 4 (org learning) adds double-loop: "are the guardrails
effective?" Process experiments test whether rules actually improve outcomes.
Pattern-to-guardrail promotion (or demotion) is the org changing its own
rules based on evidence.

**Design implication:** The experiment tracking feature and anti-pattern
detection are explicit double-loop mechanisms. The system must make it easy
to question and change rules, not just enforce them.

### Toyota Kata (Rother, 2009)

Two kata: the Improvement Kata (scientific method for improvement: target
condition, current condition, obstacles, next experiment) and the Coaching
Kata (questions a coach asks to guide improvement).

**RaiSE connection:** Process experiments follow the Improvement Kata
pattern: target condition (reduce bugs 25%), current condition (3.8
bugs/sprint), obstacles (no TDD practice), experiment (adopt TDD), measure
(did bugs drop?). The recommendation engine acts as the "coaching kata" --
it asks the questions the data suggests.

**Design implication:** Experiment tracking should follow the Improvement
Kata structure: hypothesis, baseline, measurement, evaluation.

### Thinking in Systems (Meadows, 2008)

Leverage points: places in a system where a small change can produce large
effects. The most effective leverage points are changing the rules of the
system (goals, paradigms), not adjusting parameters.

**RaiSE connection:** Pattern-to-guardrail promotion is a leverage point
change. When evidence shows a pattern works, promoting it to a guardrail
changes the rules of the system. This is more powerful than adjusting
coverage thresholds or velocity targets.

**Design implication:** Layer 4 should prioritize identifying and recommending
leverage-point interventions over parametric adjustments. "Adopt TDD" (rule
change) is higher leverage than "increase coverage to 85%" (parameter tweak).

### Goodhart's Law (Goodhart, 1975; Strathern, 1997)

"When a measure becomes a target, it ceases to be a good measure."

**RaiSE connection:** See Section 7 for the full treatment. This is the
primary design constraint for Layer 4. Every metric must be classified by
its safety as a target.

### Westrum Organizational Culture (Westrum, 2004)

Three culture types: pathological (power-oriented, information hoarded),
bureaucratic (rule-oriented, information neglected), generative
(performance-oriented, information shared and sought).

**RaiSE connection:** RaiSE's design assumes and promotes generative culture.
Pattern propagation requires information sharing. Waivers require
psychological safety to file. Process experiments require curiosity. The
system works best in generative cultures and may actively harm pathological
ones (where metrics become weapons).

**Design implication:** The system should include culture-safety checks.
If metrics are being used punitively (correlation: low waiver filing + high
compliance violations = waivers suppressed), emit a warning.

### SPACE Framework (Forsgren et al., 2021)

Five dimensions of developer productivity: Satisfaction and well-being,
Performance, Activity, Communication and collaboration, Efficiency and flow.

**RaiSE connection:** RaiSE currently covers Activity (throughput, cycle
time), Performance (quality, compliance), and Efficiency (flow metrics from
session data). Satisfaction and Communication are not captured and may not
be appropriate for automated measurement.

**Design implication:** Do not claim to measure "developer productivity"
holistically. RaiSE measures process outcomes and technical health. Developer
satisfaction requires surveys, not automation.

---

## 9. Competitive Landscape

### Engineering Analytics Platforms

| Platform | What It Does | Data Sources | Strengths | Limitations vs RaiSE |
|----------|-------------|-------------|-----------|---------------------|
| **LinearB** | Workflow optimization, PR automation, DORA metrics | Git, Jira, CI | Strong PR-level analytics, workflow rules | No knowledge graph, no governance, no pattern learning |
| **Jellyfish** | Engineering intelligence, financial modeling | Git, Jira, calendar, roadmap | Business alignment, scenario planning | No code-level intelligence, no governance, no AI agent integration |
| **Pluralsight Flow** | Team velocity, code analytics | Git, Jira | Granular code contribution analysis | Acquired by Appfire (Feb 2025), no governance, no cross-repo learning |
| **Haystack** | Developer productivity | Git | Simple, focused | Limited scope -- git metrics only |
| **Sleuth** | Deploy tracking, DORA metrics | Git, CI/CD | Strong deploy analytics | Deployment-focused, no process or architecture |
| **Backstage + Soundcheck** | Developer portal, tech health scorecards | Service catalog, custom checks | Extensible, open-source, Spotify-backed | Observes and reports, does not prevent violations. No AI integration. |
| **Jira Advanced Roadmaps** | Portfolio planning, capacity management | Jira | Deep Jira integration | Project management only, no code or architecture awareness |
| **Cortex** | Service scorecards, standards | Service catalog, custom | Similar to Backstage Soundcheck | No knowledge graph, no pattern learning |

### DORA / SPACE Frameworks

DORA and SPACE are measurement frameworks, not products. They define WHAT to
measure but not HOW to aggregate, learn, or recommend. RaiSE implements the
metrics while adding the intelligence layer on top.

| Aspect | DORA/SPACE | RaiSE L4 |
|--------|-----------|----------|
| Defines metrics | Yes | Yes (maps to DORA where possible) |
| Collects data | No (framework only) | Yes (agent_events, graph, patterns) |
| Aggregates across repos | No | Yes (shared graph + multi-repo queries) |
| Provides governance | No | Yes (L3 compliance integrated into health score) |
| Learns from patterns | No | Yes (L2 pattern propagation feeds recommendations) |
| AI-integrated | No | Yes (agent telemetry is the primary data source) |

### What RaiSE Does Differently

The fundamental differentiator is not any single feature. It is the
**integration of knowledge graph, pattern evidence, governance compliance,
and AI agent telemetry into a unified organizational learning system.**

No existing tool combines these:

1. **Knowledge graph-based** -- not just git/Jira metrics but architectural
   understanding (components, modules, layers, dependencies, decisions)

2. **AI-integrated** -- the AI agent that writes code also generates the
   telemetry and checks governance. The observer IS the worker.

3. **Governance-aware** -- health scores include compliance, not just speed.
   An organization that ships fast but ignores guardrails is not healthy.

4. **Pattern-evidence-linked** -- recommendations are backed by statistical
   evidence (Wilson scores, cross-repo validation), not heuristics.

5. **Double-loop** -- the system does not just measure compliance with rules.
   It measures whether the rules themselves are effective.

The closest competitor is Backstage + Soundcheck (tech health scorecards),
but Backstage is a portal (observes and reports) while RaiSE is a copilot
(prevents and recommends during work).

---

## 10. Graph Schema Gap Analysis

### What Exists Today

| Schema Element | Exists? | Used by L4? | How |
|---------------|---------|-------------|-----|
| `agent_events` table | Yes | Yes | Velocity, capacity, cycle time, errors |
| `memory_patterns` table | Yes | Yes | Pattern adoption, confidence trends |
| `graph_nodes` (18 types) | Yes | Yes | Components, modules, guardrails, calibrations, sessions, releases |
| `graph_edges` (11 types) | Yes | Yes | Dependencies, governance relationships |
| `organizations` table | Yes | Yes | Org-level aggregation |
| `scope` column on graph_nodes | Yes | Partial | Used for node scoping, not metric scoping |
| `properties` JSONB | Yes | Yes | Extensible metadata for all tables |

### What's Missing from Layers 1-3 (Prerequisites)

These gaps were identified in the L1, L2, L3 research. Layer 4 depends on
them being resolved:

| Gap | Identified In | Needed For L4 | Priority |
|-----|--------------|---------------|----------|
| Cross-repo edges (L1) | cross-repo-visibility | Dependency risk heatmap | P0 |
| `scope` column on memory_patterns (L2) | pattern-propagation | Pattern adoption metrics per scope | P0 |
| `repo_id` column on memory_patterns (L2) | pattern-propagation | Per-repo pattern tracking | P0 |
| `pattern_evaluations` table (L2) | pattern-propagation | Cross-repo validation counts, anti-pattern detection | P0 |
| Waiver node type (L3) | governance-intelligence | Waiver burden metric, governance erosion tracking | P1 |
| Compliance state snapshot (L3) | governance-intelligence | Compliance trend tracking | P1 |
| Scope resolution logic (L3) | governance-intelligence | Applicable guardrails per repo | P0 |

### What's Genuinely New for L4

| New Schema Element | Purpose | Type | Effort |
|-------------------|---------|------|--------|
| `metric_snapshots` table | Store computed metrics per repo per sprint | New table | M |
| `health_scores` materialized view | Pre-computed health scores | Materialized view | S |
| `experiments` table | Track process experiments with baseline/current | New table | M |
| `alerts` table | Store generated early warnings | New table | S |
| `release_completed` event type | Track deployment frequency | Event type convention | XS |
| `production_incident` event type | Track change failure rate, MTTR | Event type convention | XS |

**Proposed `metric_snapshots` table:**

```sql
CREATE TABLE metric_snapshots (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id       UUID REFERENCES organizations(id),
    repo_id      VARCHAR(255) NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end   TIMESTAMP WITH TIME ZONE NOT NULL,
    period_type  VARCHAR(20) NOT NULL,  -- 'sprint', 'month', 'quarter'
    metrics      JSONB NOT NULL,        -- all raw + composite metrics
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE UNIQUE INDEX ix_snapshot_org_repo_period
    ON metric_snapshots(org_id, repo_id, period_start, period_type);
```

Example `metrics` JSONB payload:
```json
{
  "raw": {
    "stories_completed": 9,
    "cycle_time_mean_hours": 4.2,
    "test_coverage_pct": 87,
    "guardrails_checked": 8,
    "guardrails_passed": 8,
    "patterns_evaluated": 7,
    "waivers_active": 0,
    "waivers_expired": 0,
    "agent_errors": 2,
    "sessions_count": 14
  },
  "composite": {
    "health_score": 92,
    "compliance_score": 1.0,
    "velocity_index": 1.06,
    "predictability_index": 0.88,
    "risk_level": "LOW"
  },
  "trends": {
    "health_score_delta": 4,
    "health_score_direction": "improving",
    "velocity_delta": 0.5,
    "coverage_delta": 5
  }
}
```

**Proposed `experiments` table:**

```sql
CREATE TABLE experiments (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id        UUID REFERENCES organizations(id),
    repo_id       VARCHAR(255) NOT NULL,
    name          VARCHAR(255) NOT NULL,
    hypothesis    TEXT NOT NULL,
    metric_target VARCHAR(100) NOT NULL,  -- which metric to track
    target_value  FLOAT,                  -- expected outcome
    baseline      JSONB NOT NULL,         -- snapshot at experiment start
    started_at    TIMESTAMP WITH TIME ZONE NOT NULL,
    ends_at       TIMESTAMP WITH TIME ZONE,
    status        VARCHAR(20) DEFAULT 'active',  -- active, concluded, cancelled
    conclusion    TEXT,
    concluded_at  TIMESTAMP WITH TIME ZONE,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### Assessment

Layer 4 introduces 2 new tables (`metric_snapshots`, `experiments`) and
1 materialized view (`health_scores`). It also adds an `alerts` table for
proactive warnings. The total new schema is small because L4 is primarily
an **aggregation and intelligence layer** over data that already exists in
the tables defined by L0-L3.

The critical dependency is that L1-L3 schema gaps must be resolved first.
Without pattern evaluations (L2) and compliance state (L3), the health
score has missing components.

---

## 11. Required Server Endpoints

### New Endpoints

| Endpoint | Method | Purpose | Depends On |
|----------|--------|---------|-----------|
| `GET /api/v1/org-learning/health` | GET | Portfolio + per-repo health scores | L3 compliance, L2 patterns, agent_events |
| `GET /api/v1/org-learning/velocity` | GET | Velocity dashboard with throughput, cycle time, capacity | agent_events |
| `GET /api/v1/org-learning/risks` | GET | Risk heatmap with priority recommendations | All layers |
| `GET /api/v1/org-learning/recommendations` | GET | Evidence-based improvement suggestions | All layers |
| `POST /api/v1/org-learning/experiments` | POST | Create a process experiment | metric_snapshots |
| `GET /api/v1/org-learning/experiments` | GET | List and check experiment status | metric_snapshots, experiments |
| `GET /api/v1/org-learning/trends` | GET | Trend analysis for any metric over time | metric_snapshots |
| `GET /api/v1/org-learning/onboarding/{repo}` | GET | Auto-generated onboarding brief | All layers |
| `POST /api/v1/org-learning/snapshot` | POST | Trigger metric snapshot (sprint boundary) | agent_events, L1-L3 |

### Endpoint Details

**Health Score Endpoint:**

```
GET /api/v1/org-learning/health?org=kurigage

Response:
{
  "org": "kurigage",
  "calculated_at": "2026-03-15T10:00:00Z",
  "portfolio_score": 87,
  "portfolio_trend": "improving",
  "repos": [
    {
      "repo": "contabilidad",
      "score": 92,
      "trend": "improving",
      "trend_delta": 4,
      "components": { ... },
      "top_risk": null,
      "period": "sprint-12"
    }
  ],
  "top_wins": [
    "contabilidad test coverage reached 87% (+5%)",
    "0 MUST violations across all repos"
  ],
  "top_risks": [
    "erp test coverage at 62% (target: 80%)",
    "2 expired waivers in erp"
  ],
  "recommendations": [
    {
      "action": "Invest 2 stories in erp domain test coverage",
      "evidence": "erp coverage below 80% SHOULD threshold for 3 sprints",
      "priority": "high",
      "category": "coverage"
    }
  ]
}
```

**Velocity Endpoint:**

```
GET /api/v1/org-learning/velocity?org=kurigage&periods=6

Response:
{
  "org": "kurigage",
  "period_type": "sprint",
  "periods": 6,
  "repos": {
    "contabilidad": {
      "throughput": [8, 9, 7, 10, 8, 9],
      "cycle_time": [4.5, 4.3, 4.8, 4.1, 4.3, 4.2],
      "estimation_accuracy": [0.85, 0.88, 0.82, 0.90, 0.87, 0.88],
      "trend": "stable"
    },
    "erp": { ... },
    "apis": { ... }
  },
  "aggregate": {
    "throughput": [24, 25, 20, 26, 27, 25],
    "trend": "stable"
  },
  "warning": "Velocity metrics are diagnostic only. Not for targets or comparison."
}
```

**Risk Endpoint:**

```
GET /api/v1/org-learning/risks?org=kurigage

Response:
{
  "org": "kurigage",
  "calculated_at": "2026-03-15T10:00:00Z",
  "heatmap": {
    "contabilidad": {
      "coverage": "low", "governance": "low", "dependencies": "low",
      "knowledge": "medium", "velocity": "low", "overall": "low"
    },
    "erp": {
      "coverage": "high", "governance": "medium", "dependencies": "low",
      "knowledge": "low", "velocity": "medium", "overall": "high"
    },
    "apis": {
      "coverage": "low", "governance": "low", "dependencies": "high",
      "knowledge": "low", "velocity": "low", "overall": "medium"
    }
  },
  "priority_recommendations": [
    {
      "rank": 1,
      "risk": "erp test coverage at 62% and declining",
      "severity": "high",
      "action": "Invest 2 stories in domain test coverage",
      "expected_impact": "Coverage to 70%+ in 2 sprints"
    },
    {
      "rank": 2,
      "risk": "apis is critical provider with 0 redundancy",
      "severity": "high",
      "action": "Discuss failover strategy for critical endpoints",
      "expected_impact": "Reduce single-point-of-failure risk"
    }
  ],
  "alerts": [
    {
      "repo": "erp",
      "type": "velocity_anomaly",
      "message": "Velocity dropped 29% vs 6-sprint average",
      "severity": "investigate",
      "correlation": "Arnulfo at 137% capacity"
    }
  ]
}
```

**Experiment Endpoint:**

```
POST /api/v1/org-learning/experiments
{
  "repo_id": "erp",
  "name": "TDD Adoption",
  "hypothesis": "TDD reduces bug density by 25%+",
  "metric_target": "bug_density",
  "target_value": 2.85,
  "baseline": {
    "bug_density": 3.8,
    "velocity": 7.0,
    "coverage": 58
  },
  "started_at": "2026-02-15",
  "ends_at": "2026-05-15"
}

Response:
{
  "id": "exp-001",
  "status": "active",
  "periods_elapsed": 6,
  "current_metrics": {
    "bug_density": 2.6,
    "velocity": 5.8,
    "coverage": 71
  },
  "delta": {
    "bug_density": -32,
    "velocity": -17,
    "coverage": 22
  },
  "statistical_significance": {
    "bug_density": {"p_value": 0.03, "significant": true},
    "velocity": {"p_value": 0.08, "significant": false}
  },
  "verdict": "ON_TRACK"
}
```

### How Endpoints Build on Layers 1-3

```
L4 Endpoints              L3 Dependencies        L2 Dependencies        L1 Dependencies
─────────────            ────────────────        ────────────────       ────────────────
/health          ←───── /governance/compliance   pattern adoption       dependency freshness
/velocity        ←───── (none)                   (none)                (none)
/risks           ←───── waiver burden            pattern failures      dependency concentration
/recommendations ←───── compliance trends        cross-repo evidence   impact analysis
/experiments     ←───── (none)                   (none)                (none)
/trends          ←───── compliance history       evaluation history    (none)
/onboarding      ←───── applicable guardrails    inherited patterns    external dependencies
```

---

## 12. Implementation Priority

### What Comes "Free" from Layers 1-3

If L1-L3 are implemented, these L4 capabilities require only aggregation
queries (no new infrastructure):

| Capability | Source | New Work |
|-----------|--------|----------|
| Compliance score per repo | L3 `/governance/compliance` | Query + aggregate |
| Pattern adoption rate per repo | L2 `pattern_evaluations` count | Query + aggregate |
| Dependency concentration risk | L1 `/visibility/dependencies` | Count edges per provider |
| Waiver burden metric | L3 waiver nodes | Count active/expired per repo |
| Knowledge distribution | L0 session nodes | Count sessions per person per module |

### What's Genuinely New Work

| Capability | What's New | Effort |
|-----------|-----------|--------|
| Health score computation | Weighted composite formula, snapshot storage | M |
| Velocity aggregation | Aggregate agent_events by repo/period, trend calc | M |
| Risk heatmap | Multi-signal threshold evaluation | M |
| Recommendation engine | Rule-based correlation + priority ranking | L |
| Experiment tracking | New table, baseline/current comparison, stats | M |
| Trend analysis | Linear regression over metric_snapshots | S |
| Early warning system | Anomaly detection (z-score) + alert generation | M |
| Onboarding brief | Multi-source aggregation into structured response | M |

### Phased Build Order

**Phase 1: Foundation (MVP for Pro launch)**

| Story | Scope | Effort | Depends On |
|-------|-------|--------|-----------|
| S1: metric_snapshots table + migration | Schema + Alembic | S | L0 |
| S2: Snapshot trigger endpoint | POST /snapshot, compute raw metrics | M | S1 |
| S3: Health score computation | GET /health, weighted composite | M | S2, L3 |
| S4: Velocity aggregation | GET /velocity, throughput + cycle time | M | S2 |
| S5: Basic risk heatmap | GET /risks, threshold-based | S | S2, L1, L3 |

Deliverable: Jorge sees health scores. Rodo sees risk heatmap. Tech leads see
velocity. MVP with 5 stories.

**Phase 2: Intelligence**

| Story | Scope | Effort | Depends On |
|-------|-------|--------|-----------|
| S6: Trend analysis | GET /trends, regression over snapshots | S | S2 |
| S7: Recommendation engine | GET /recommendations, rule-based | M | S3, S5 |
| S8: Experiment tracking | POST/GET /experiments, before/after | M | S2 |
| S9: Early warning system | Anomaly detection + alerts table | M | S2, S4 |

Deliverable: Evidence-based recommendations. Process experiments. Proactive
alerts. 4 stories.

**Phase 3: Experience**

| Story | Scope | Effort | Depends On |
|-------|-------|--------|-----------|
| S10: Onboarding brief | GET /onboarding/{repo}, multi-source | M | L1, L2, L3 |
| S11: DORA metrics integration | Release events + mapping | M | S4 |
| S12: Rovo agent integration | Natural language queries via Rovo | L | S3, S5, S7 |
| S13: Statistical significance | Mann-Whitney U for experiments | S | S8 |

Deliverable: New hire onboarding intelligence. DORA mapping. Rovo
conversational access. 4 stories.

### Total Estimate

| Phase | Stories | Effort | Timeline |
|-------|---------|--------|----------|
| Phase 1: Foundation | 5 | M-L | 3-4 weeks |
| Phase 2: Intelligence | 4 | M-L | 3-4 weeks |
| Phase 3: Experience | 4 | L | 4-5 weeks |
| **Total** | **13** | **L-XL** | **10-13 weeks** |

Note: This assumes L1-L3 are implemented. Without them, Phase 1 expands
significantly because prerequisites must be built first.

---

## 13. Open Questions

### Q1: What time period defines a "sprint" for aggregation?

**Options:**
- A) Fixed 2-week windows starting from org creation
- B) Jira sprint boundaries (query via MCP)
- C) Configurable per org (period_start, period_end in snapshot trigger)

**Leaning:** C. Not all teams use sprints. Some use Kanban. The snapshot
trigger should accept arbitrary period boundaries, defaulting to 2-week
windows.

### Q2: Should health scores be visible to developers or only to leads?

**Options:**
- A) Visible to everyone (transparency, generative culture)
- B) Visible to leads + architect only (avoid Goodhart)
- C) Component-level visible to devs, composite visible to leads only

**Leaning:** A with guardrails. Full transparency, but with explicit
messaging that scores are diagnostic, not performance measures. If the org
culture is pathological (metrics used punitively), restrict visibility.

### Q3: How far back should baseline data extend?

**Options:**
- A) From first sync to server (all available history)
- B) Rolling 6-sprint window
- C) Configurable window with 6-sprint default

**Leaning:** C. Trends are most meaningful over 4-8 data points. Older data
decays in relevance. But allow orgs to look back further for experiments.

### Q4: Should recommendations be auto-generated or require architect approval?

**Options:**
- A) Auto-generated, shown immediately
- B) Auto-generated, queued for architect review before showing
- C) Auto-generated, shown with "suggested by system, not reviewed" label

**Leaning:** C for Phase 1. Recommendations are suggestions, not commands.
Label them as system-generated. If adoption is high and accuracy is good,
consider removing the label in Phase 3.

### Q5: What metrics should we explicitly NOT measure yet?

**Recommendation: Do not measure in MVP:**
- Developer satisfaction (requires surveys, not automation)
- Lines of code (universally acknowledged as useless)
- PR review time (can create pressure to rubber-stamp)
- Individual developer velocity (creates perverse incentives)
- Meeting time / communication metrics (privacy concerns)

These are omitted deliberately, not overlooked. Each has a specific reason
for exclusion. They may be added later with appropriate safeguards.

### Q6: How to handle orgs with < 3 sprints of data?

**Options:**
- A) Show scores with "low confidence" warning
- B) Don't show scores until 3+ data points exist
- C) Show raw metrics without composite scores

**Leaning:** B. Composite scores require trend data. Showing a health score
of 72 with 1 data point is misleading. Show raw metrics and say "health
score available after 3 sprints."

### Q7: Should the system recommend against the org's current practices?

Example: The org mandates 90% coverage. Data shows no correlation between
90% coverage and bug reduction (because the extra tests are muda). Should
the system say "your coverage target may be counterproductive"?

**Leaning:** Yes, but carefully. This is double-loop learning -- the highest
form of organizational learning. The system should present the evidence and
let the architect decide. "Data suggests no correlation between coverage
>80% and bug reduction in your repos. Consider focusing on domain coverage
rather than overall percentage."

---

## 14. References

### Internal Research (Layers 0-3)

| Research | Date | Scope | Relevance to L4 |
|----------|------|-------|-----------------|
| [shared-memory-architecture](../shared-memory-architecture/) | Feb 25 | PostgreSQL schema, multi-tenancy, scoping | Foundation: where all data lives |
| [cross-repo-visibility](../cross-repo-visibility/) | Feb 26 | Dependency graph, impact analysis, duplicate detection | L1: dependency risk, coupling metrics |
| [pattern-propagation](../pattern-propagation/) | Feb 26 | Scope hierarchy, promotion, cross-repo reinforcement | L2: pattern adoption metrics, anti-pattern detection |
| [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) | Feb 26 | Compliance, poka-yoke, waivers, audit | L3: compliance score, waiver burden, governance erosion |
| [temporal-decay-pattern-scoring](../temporal-decay-pattern-scoring/) | Feb 7 | Wilson score, exponential decay, reinforcement | Scoring: pattern confidence, freshness metrics |
| [collective-intelligence-lineage](../collective-intelligence-lineage/) | Feb 2 | Knowledge lineage, telemetry vision | Vision: org learning from agent data |
| [governance-as-code-agents](../governance-as-code-agents/) | Jan 29 | Policy DSL, local enforcement | L3 precursor: governance model |
| [atlassian-forge-integration](../atlassian-forge-integration/) | Feb 24 | Forge app, Rovo agents, walking skeleton | Delivery: how L4 reaches users via Rovo |

### External Literature

| Source | Authors | Year | Key Concept | RaiSE Application |
|--------|---------|------|-------------|-------------------|
| _Accelerate: The Science of Lean Software and DevOps_ | Forsgren, Humble, Kim | 2018 | Four DORA metrics, statistical validation | DORA metrics mapping (Section 6) |
| _The Fifth Discipline_ | Senge | 1990 | Five disciplines of learning organizations, systems thinking | Knowledge graph as shared mental model |
| "Double-Loop Learning in Organizations" | Argyris | 1977 | Single-loop vs double-loop learning | Process experiments, guardrail questioning |
| _Toyota Kata_ | Rother | 2009 | Improvement kata, coaching kata | Experiment tracking structure |
| _Thinking in Systems_ | Meadows | 2008 | Leverage points, feedback loops | Pattern-to-guardrail as leverage point change |
| "Goodhart's Law" | Goodhart (1975), Strathern (1997) | 1975/1997 | Measure becomes target ceases to be good measure | Metric safety classification (Section 7) |
| "A Typology of Organisational Cultures" | Westrum | 2004 | Pathological / bureaucratic / generative culture | Culture prerequisite for metric transparency |
| "The SPACE of Developer Productivity" | Forsgren et al. | 2021 | Five dimensions: S.P.A.C.E. | Scope boundaries: what RaiSE measures vs doesn't |
| _Accelerate State of DevOps Reports_ | DORA Team | 2018-2024 | Annual benchmarking, elite/high/medium/low | Benchmark classification |
| "Goodhart's Law in Software Engineering" | Jellyfish Blog | 2024 | Velocity inflation, gaming behaviors | Section 7 anti-patterns |

### Industry Sources

- [DORA Metrics: Four Keys Guide](https://dora.dev/guides/dora-metrics-four-keys/) -- Official DORA team guidance
- [LinearB: DORA Metrics](https://linearb.io/blog/dora-metrics) -- Competitor perspective on metric implementation
- [Backstage Soundcheck: Tech Health](https://backstage.spotify.com/docs/plugins/soundcheck/core-concepts/tech-health) -- Spotify's approach to health scorecards
- [Jellyfish: Goodhart's Law in Software Engineering](https://jellyfish.co/blog/goodharts-law-in-software-engineering-and-how-to-avoid-gaming-your-metrics/) -- Practical Goodhart mitigation
- [SPACE Framework (ACM Queue)](https://queue.acm.org/detail.cfm?id=3454124) -- Original SPACE publication

---

*Research by: Emilio + Claude Opus 4.6 | Session: SES-294 | Date: 2026-02-26*
*Status: Exploration complete -- ready for /rai-problem-shape*
*This is the capstone layer (Layer 4) of the shared memory capability stack.*
