# Governance Intelligence for Multi-Repo Environments

**Date:** 2026-02-26 | **Session:** SES-294 | **Author:** Emilio + Claude Opus 4.6

---

## 1. Problem Statement

### The Governance Gap in Multi-Repo Organizations

Organizations with multiple repositories face a fundamental governance problem:
**decisions are made centrally but enforced locally (or not at all).**

An architect declares "all APIs must validate input." This decision lives in a
Confluence page, a Slack message, or someone's head. Three months later, 2 of 5
repos follow it, 1 has a waiver nobody documented, and 2 never heard about it.

The gap is not in decision-making. It's in the loop:

```
Declare → Distribute → Check → Report → Enforce
    ↑                                        │
    └────────── feedback ────────────────────┘
```

Today, most organizations complete only the first step (Declare) and sometimes
the last (Enforce, usually via PR review — manual, inconsistent, and after the
fact).

### Why This Matters for AI-Assisted Development

With AI agents doing more of the implementation work, governance becomes both
more critical and more feasible:

- **More critical:** An AI agent can generate 10x more code per day. Without
  governance rails, it can also generate 10x more violations per day.
- **More feasible:** The same AI agent that writes code can check governance
  rules at write time — if the rules are queryable and the agent knows them.

RaiSE's skills already form the developer workflow. Governance checks embedded
in skills are invisible to the developer — they don't slow down, they prevent
rework.

### The Kurigage Context

Kurigage is a software company with:

| Role | Person | Repo | Stack |
|------|--------|------|-------|
| Architect | Rodo | (cross-cutting) | Architecture decisions |
| Tech Lead | Adan | contabilidad | Symphony/PHP (accounting) |
| Tech Lead | Arnulfo | erp | Symphony/PHP (ERP) |
| Tech Lead | Sofi | apis | .NET (APIs) |
| Business Owner | Jorge | (visibility) | Wants to know "are we on track?" |

**Their governance problems today:**
1. Rodo makes architecture decisions in meetings; enforcement depends on memory
2. When Sofi changes an API, Adan finds out when his code breaks
3. No visibility into whether declared standards are actually followed
4. Jorge asks "are we doing things right?" and gets anecdotes, not data

---

## 2. Three Capability Layers

The shared knowledge graph enables three distinct capabilities. Each builds on
the previous one:

```
┌─────────────────────────────────────────────┐
│       4. Organizational Learning             │
│    scorecards, trends, risk heatmaps         │
├─────────────────────────────────────────────┤
│       3. Governance Intelligence             │  ← THIS RESEARCH
│    compliance, poka-yoke, waivers, audit     │
├─────────────────────────────────────────────┤
│       2. Pattern Propagation                 │
│    promote, inherit, cross-repo reinforce    │
├─────────────────────────────────────────────┤
│       1. Cross-Repo Visibility               │
│    dependencies, impact, duplicates          │
├─────────────────────────────────────────────┤
│       0. Shared Memory (EXISTS TODAY)         │
│    graph sync, patterns, telemetry, query    │
└─────────────────────────────────────────────┘
```

### Layer 0: Shared Memory (Exists — E275 complete)

What rai-server does today:
- Store and retrieve knowledge graphs per org/repo (`POST /graph/sync`, `GET /graph/query`)
- Store shared patterns (`POST/GET /memory/patterns`)
- Store agent telemetry (`POST/GET /agent/events`)
- Multi-tenancy by org_id, multi-repo by repo_id
- Full-text search with PostgreSQL GIN indexing

### Layer 1: Cross-Repo Visibility

**Problem:** "What breaks if I change this API?"

Each repo is an island. If I have 5 repos and change a contract in `shared-lib`,
I don't know who consumes what.

**With shared graphs:**
- **Dependency graph cross-repo** — `component`/`module` nodes with `depends_on`
  edges crossing `repo_id` boundaries. Query: "who depends on `AuthService`?"
- **Impact analysis** — BFS from a modified node, crossing repo boundaries.
  "Changing `POST /invoices` affects 3 consumers in 2 repos."
- **Duplicate detection** — Similarity between `component` nodes across repos.
  "3 teams built their own auth wrapper."

**Kurigage example:** Sofi changes `POST /invoices` in `apis`. The graph shows
`contabilidad/InvoiceSync.php` (Adan) and `erp/Billing/ApiClient.cs` (Arnulfo)
depend on it. Blast radius = 2 repos, 4 call sites.

**Reliability gain:** You know what breaks before you break it.

### Layer 2: Pattern Propagation

**Problem:** "Team A discovered a valuable pattern, Team B reinvents it."

Patterns today live per-org in `memory_patterns`, but there's no mechanism for:
- **Promotion:** repo pattern → org pattern (when it works in 3+ repos)
- **Inheritance:** org patterns inherited by new repos automatically
- **Cross-repo reinforcement:** "this pattern worked in repos A, B, and C" →
  Wilson score increases

**What's missing:** A scope hierarchy for patterns:
`repo → team → org → enterprise` with propagation rules.

**Kurigage example:** Adan discovers that "repository pattern for DB access
reduces bug density by 40% in accounting calcs." Arnulfo's ERP has similar
domain logic. The pattern gets promoted to org level, and Arnulfo's agent
surfaces it during his next story design.

**Reliability gain:** Patterns are validated statistically across repos.
A pattern with 8 positives across 3 repos is more trustworthy than one with
3 positives in 1 repo.

### Layer 3: Governance Intelligence (THIS RESEARCH)

See sections 3-7 below.

### Layer 4: Organizational Learning

**Problem:** "Is the organization actually improving over time?"

With telemetry (`agent_events`) + patterns + graphs from N repos:
- **Velocity trends cross-repo** — Do teams that adopt pattern X deliver faster?
- **Architecture health scorecards** — Score per repo based on drift, debt, coverage
- **Knowledge freshness** — When was this pattern last validated? (temporal decay
  already exists in core)
- **Risk heatmap** — Repos inactive for 6 months, no tests, guardrails violated

**Kurigage example:** Jorge sees a dashboard:
```
contabilidad  🟢 92/100
erp           🟡 74/100  (coverage + 1 waiver)
apis          🟢 95/100
Tendencia: ↗ mejorando (was 88% 2 sprints ago)
```

**Reliability gain:** Data-driven organizational improvement, not anecdotes.

---

## 3. Governance Intelligence — Deep Dive

### 3.1 What RaiSE Already Does (Poka-yoke v0)

RaiSE's skill lifecycle already enforces governance, but it's hardcoded:

| Current Gate | Enforcement Point | Mechanism |
|-------------|-------------------|-----------|
| Story branch exists | Before story work | `/rai-story-start` checks |
| Plan exists | Before implementation | `/rai-story-plan` required |
| Tests + types + lint pass | Before any commit | Pre-commit validation |
| Retrospective complete | Before story close | `/rai-story-review` required |
| Epic retro complete | Before epic merge | `/rai-epic-close` required |

**What works:** These gates prevent process violations reliably.

**What doesn't scale:**

| Limitation | Consequence |
|------------|-------------|
| Hardcoded in skills | Changing a rule = changing code |
| Same for everyone | Can't have different rules per team/repo |
| No traceability | "Why can't I do X?" → "because the skill says no" |
| No exceptions | No mechanism for "this repo is exempt from Y because Z" |
| Not auditable | No record of what was validated and when |
| Local only | Rules don't cross repo boundaries |

### 3.2 Governance as Graph

The central idea: **governance rules are nodes, not code.**

```
principle                              guardrail
┌──────────────────┐    governed_by    ┌───────────────────────┐
│ id: P-001        │◄─────────────────│ id: G-001             │
│ content:         │                   │ content: "All public  │
│ "Security first" │                   │  APIs must validate   │
│ scope: org       │                   │  input"               │
│                  │                   │ enforcement: MUST      │
└──────────────────┘                   │ scope: org             │
                                       │ applies_to: [apis,erp]│
                                       │ validation_fn: ...     │
                                       └───────────┬───────────┘
                                                   │
                                          constrained_by
                                                   │
                                                   ▼
                                       ┌───────────────────────┐
                                       │ component             │
                                       │ id: UserController    │
                                       │ repo: apis            │
                                       │ type: controller      │
                                       └───────────────────────┘
```

Three key concepts make this work:

#### Concept 1: Scope Hierarchy with Inheritance

```
Enterprise   ─── "All code must pass SAST"                    [MUST]
  │
  └─ Org     ─── "Use Pydantic/validation for data models"    [MUST]
      │
      ├─ Team: Backend ─── "TDD red-green-refactor"           [MUST]
      │   │
      │   ├─ Repo: apis ─── "OpenAPI spec for all endpoints"  [MUST]
      │   └─ Repo: erp  ─── "90% coverage for domain logic"   [SHOULD]
      │
      └─ Team: Accounting ─── "2 reviewers for tax calcs"     [MUST]
          │
          └─ Repo: contabilidad ─── (inherits all above)
```

**Inheritance rules:**
1. A child scope inherits ALL rules from parent scopes
2. A child scope can ADD stricter rules (SHOULD → MUST for their scope)
3. A child scope CANNOT relax parent rules (MUST → SHOULD is forbidden)
4. Conflict resolution: strictest wins

**Implementation in the graph:**
- `guardrail` nodes have a `scope` field: `enterprise`, `org`, `team:{name}`,
  `repo:{name}`
- Query "what guardrails apply to repo X?" = collect guardrails from repo X +
  team of X + org + enterprise
- Edge `applies_to` connects guardrails to their targets (repos, modules, components)

#### Concept 2: Enforcement Levels (RFC 2119 inspired)

| Level | Semantics | Poka-yoke Type | Agent Behavior |
|-------|-----------|----------------|----------------|
| **MUST** | Violation blocks work | Contact — skill stops | Cannot proceed without compliance |
| **SHOULD** | Violation generates warning, requires justification | Motion-step — can continue but recorded | Warns, asks for waiver justification |
| **CAN** | Recommendation, no enforcement | Informative — appears in design context | Surfaces as suggestion during design |

**Mapping to poka-yoke taxonomy (Shingo):**

- **Contact poka-yoke:** Physical constraint that prevents the error.
  In our case: the skill literally won't execute the next step until the MUST
  guardrail is satisfied.
- **Fixed-value poka-yoke:** Comparison against a known correct value.
  In our case: guardrail has an `expected_value` or `validation_fn` that checks
  against a known-good state.
- **Motion-step poka-yoke:** Ensures correct sequence of steps.
  In our case: process guardrails define required step sequences per story size
  (e.g., M+ stories MUST have design phase).

#### Concept 3: The Governance Loop

```
         ┌──────────┐
         │ DECLARE   │  Guardrails defined as graph nodes
         │           │  by architects, leads, or org policy
         └─────┬─────┘
               │
         ┌─────▼─────┐
         │ DISTRIBUTE │  Scope hierarchy cascades rules
         │            │  to applicable repos/teams
         └─────┬──────┘
               │
         ┌─────▼──────────────────────────────────┐
         │            CHECK (2 modes)               │
         │                                          │
         │  ┌─────────────────────────────────┐    │
         │  │ POKA-YOKE (during work)          │    │
         │  │                                  │    │
         │  │ /rai-story-design queries        │    │
         │  │  guardrails → surfaces           │    │
         │  │  applicable rules                │    │
         │  │                                  │    │
         │  │ /rai-story-implement checks      │    │
         │  │  MUST constraints → blocks        │    │
         │  │  if violated                      │    │
         │  │                                  │    │
         │  │ /rai-story-close validates       │    │
         │  │  all applicable guardrails        │    │
         │  │  → compliance report              │    │
         │  └─────────────────────────────────┘    │
         │                                          │
         │  ┌─────────────────────────────────┐    │
         │  │ VALIDATION (pre-merge / on-demand)│   │
         │  │                                  │    │
         │  │ CI/CD checks compliance          │    │
         │  │ PR review shows governance       │    │
         │  │  status                          │    │
         │  │ Architect queries compliance     │    │
         │  │  across all repos                │    │
         │  └─────────────────────────────────┘    │
         └─────────────────┬───────────────────────┘
                           │
         ┌─────────────────▼───────────────────────┐
         │              REPORT                       │
         │                                           │
         │  Per-repo compliance score                │
         │  Drift detection (declared vs actual)     │
         │  Waiver tracking (active, expired)        │
         │  Trend analysis (improving/degrading)     │
         └─────────────────┬───────────────────────┘
                           │
                    feedback loop
                           │
         ┌─────────────────▼───────────────────────┐
         │              EVOLVE                       │
         │                                           │
         │  Update guardrails based on evidence      │
         │  Promote patterns to guardrails           │
         │  Retire obsolete rules                    │
         │  Adjust enforcement levels                │
         └─────────────────────────────────────────┘
```

### 3.3 Waiver Mechanism

Governance without exceptions is tyranny. The waiver mechanism provides a
structured, auditable path for exceptions:

```yaml
# Waiver as a graph node
waiver:
  id: W-001
  guardrail: G-004           # Which rule is waived
  repo: erp                  # Where the waiver applies
  scope: "src/Modules/Inventory/StockService.php"  # Optional: specific file/module
  reason: "Hotfix urgente, refactor planned in RAISE-310"
  approved_by: "arnulfo"     # Who approved (must have authority)
  created: "2026-03-01"
  expires: "2026-04-15"      # Mandatory expiration
  tracked_in: "RAISE-310"    # Jira ticket for the fix
  status: active             # active | expired | resolved
```

**Waiver rules:**
1. Every waiver MUST have an expiration date
2. Every waiver MUST be tracked in a ticket (traceability)
3. Every waiver MUST have a reason (auditable)
4. MUST-level waivers require architect approval (Rodo in Kurigage's case)
5. SHOULD-level waivers can be self-approved by tech leads
6. Expired waivers revert to violations (the system reminds you)

**In the graph:**
- Waiver is a node (type: `waiver`)
- Edge: `waiver --waives--> guardrail`
- Edge: `waiver --applies_to--> component/module/repo`
- Query: "show me all active waivers" = filter waiver nodes where status=active

---

## 4. Kurigage Scenarios — Detailed Walkthrough

### Scenario 1: Rodo Declares Governance

Rodo (architect) defines organizational guardrails. These could be declared via:
- A Confluence page that gets parsed into graph nodes (Forge integration path)
- A YAML file in a governance repo that gets synced to the server
- Direct API calls from a Rovo agent or CLI

**Kurigage guardrails (org level):**

```yaml
guardrails:
  - id: G-001
    content: "All public APIs must have versioned OpenAPI contract"
    enforcement: MUST
    scope: org
    applies_to:
      repos: [apis, erp]       # repos that expose APIs
    principle: "Contract-first design"
    validation:
      type: file_exists
      params:
        pattern: "openapi.yaml"

  - id: G-002
    content: "Breaking API changes require 2-sprint deprecation period"
    enforcement: MUST
    scope: org
    applies_to:
      repos: [apis]             # only the API repo exposes public contracts
    principle: "No surprises between teams"
    validation:
      type: manual_check
      description: "Verify deprecated endpoint still available"

  - id: G-003
    content: "All services must have health check endpoint"
    enforcement: MUST
    scope: org
    applies_to:
      repos: [apis, erp, contabilidad]
    principle: "Observable systems"
    validation:
      type: endpoint_exists
      params:
        path: "/health"

  - id: G-004
    content: "Use repository pattern for data access"
    enforcement: SHOULD
    scope: org
    applies_to:
      repos: [apis, erp, contabilidad]
    principle: "Separation of concerns"
    validation:
      type: architecture_check
      description: "No direct SQL outside repository classes"

  - id: G-005
    content: "Minimum 80% coverage on domain logic"
    enforcement: SHOULD
    scope: org
    applies_to:
      repos: [apis, erp, contabilidad]
    validation:
      type: coverage_threshold
      params:
        threshold: 80
        scope: "domain"
```

**Adan's repo-specific guardrails (stricter):**

```yaml
guardrails:
  - id: G-100
    content: "Tax calculations require 2 reviewers"
    enforcement: MUST
    scope: "repo:contabilidad"
    applies_to:
      modules: [fiscal, tax, sat]
    principle: "El SAT no perdona"
    validation:
      type: review_count
      params:
        min_reviewers: 2
        paths: ["src/Fiscal/**", "src/Tax/**"]

  - id: G-101
    content: "All monetary amounts use Decimal, never float"
    enforcement: MUST
    scope: "repo:contabilidad"
    applies_to:
      modules: [fiscal, billing, payments]
    principle: "Precision in financial calculations"
    validation:
      type: type_check
      description: "No float types in monetary fields"
```

### Scenario 2: Sofi Changes an API Endpoint

Sofi is working on a story to change `POST /invoices` in the `apis` repo.
She runs `/rai-story-design`.

**What happens today (without governance intelligence):**
- Sofi designs the change in isolation
- She may or may not remember that other repos consume this endpoint
- If she makes a breaking change, Adan and Arnulfo find out when CI fails
  (best case) or in production (worst case)

**What happens with governance intelligence:**

```
── /rai-story-design ──────────────────────────────────────

Analyzing story scope... POST /invoices modification detected.

Cross-repo impact analysis (from shared graph):
┌─────────────────────────────────────────────────────────┐
│ This endpoint is consumed by:                            │
│                                                          │
│  contabilidad/src/Services/InvoiceSync.php (Adan)       │
│    → depends_on: 3 direct calls                          │
│    → Methods: syncInvoice(), validateInvoice(),          │
│               getInvoiceStatus()                         │
│                                                          │
│  erp/src/Modules/Billing/ApiClient.cs (Arnulfo)         │
│    → depends_on: 1 direct call                           │
│    → Methods: CreateInvoice()                            │
└─────────────────────────────────────────────────────────┘

Applicable guardrails:
┌─────────────────────────────────────────────────────────┐
│ 🔴 G-001 [MUST] All public APIs must have versioned     │
│    OpenAPI contract                                      │
│    → Action required: Update openapi.yaml                │
│                                                          │
│ 🔴 G-002 [MUST] Breaking API changes require 2-sprint   │
│    deprecation period                                    │
│    → Question: Is this change breaking? (yes/no)         │
└─────────────────────────────────────────────────────────┘
```

If Sofi answers "yes, this is a breaking change":

```
G-002 requires:
  1. ✅ Version new endpoint (e.g., POST /v2/invoices)
  2. ✅ Maintain v1 for 2 sprints (until Sprint 14)
  3. ✅ Notify consumers:
     - Adan (contabilidad) — 3 call sites to update
     - Arnulfo (erp) — 1 call site to update
  4. ✅ Update OpenAPI contract with deprecation notice

Include migration plan in story design? [Required by MUST enforcement]

Suggested design additions:
  - Task: Add v2 endpoint with new contract
  - Task: Add deprecation header to v1 responses
  - Task: Create migration tickets for consumers
    - RAISE-XXX: contabilidad migration (assign: Adan)
    - RAISE-XXX: erp migration (assign: Arnulfo)
  - Task: Update openapi.yaml with both versions
```

**The error is prevented at design time, not discovered in production.**

### Scenario 3: Arnulfo Writes Direct SQL

Arnulfo is implementing a story in the `erp` repo. During `/rai-story-implement`,
he writes a raw SQL query in a service class.

```
── /rai-story-implement ──────────────────────────────────

Implementing task 3 of 7: Add inventory stock check...

⚠ Governance check triggered:

G-004 [SHOULD]: "Use repository pattern for data access"
  Scope: org (applies to all repos)
  File: erp/src/Modules/Inventory/StockService.php
  Line 42: Direct SQL query detected

  This is a SHOULD guardrail. You may proceed, but a
  justification is required.

  Options:
  a) Refactor to use repository pattern (recommended)
  b) Register waiver with justification
  c) Show me why this guardrail exists (principle + evidence)
```

If Arnulfo chooses (b):

```
Registering waiver for G-004:

  Guardrail: G-004 (Repository pattern for data access)
  File: erp/src/Modules/Inventory/StockService.php
  Reason: [Arnulfo enters] "Hotfix urgente para inventario,
    refactor planificado"

  Waiver requirements:
  ✅ Reason provided
  ✅ SHOULD-level: tech lead self-approval sufficient
  ⚠  Tracking ticket required — create one? (yes/no)

  → Created RAISE-310: "Refactor StockService to repository pattern"
  → Waiver W-001 registered, expires: 2026-04-15 (45 days)
  → Continuing implementation...
```

If Arnulfo chooses (c):

```
G-004 rationale:

  Principle: "Separation of concerns"

  Evidence from org patterns:
  - PAT-ORG-012: "Direct SQL in service classes correlates
    with 2.3x higher bug density in accounting module"
    (confidence: 0.87, evaluated across 3 repos)

  - PAT-ORG-019: "Repository pattern reduced data-layer
    bugs by 40% after adoption in contabilidad repo"
    (confidence: 0.92, 6 evaluations, 5 positive)

  Decision: ADR-015 "Repository pattern as standard data
    access layer" (approved: 2026-01-15, by: Rodo)
```

### Scenario 4: Pre-Merge Compliance Check

Sofi is closing her story with `/rai-story-close`. Before merge, a compliance
check runs:

```
── /rai-story-close ──────────────────────────────────────

Pre-merge compliance report for story/s274.1/invoice-v2:

  Guardrails checked: 8

  MUST guardrails:
    ✅ G-001: OpenAPI contract updated (openapi.yaml modified)
    ✅ G-002: Deprecation plan documented (v1 maintained)
    ✅ G-003: Health check endpoint exists

  SHOULD guardrails:
    ✅ G-004: Repository pattern followed (no direct SQL)
    ✅ G-005: Coverage at 91% (threshold: 80%)

  Repo-specific:
    ✅ All applicable guardrails passed

  Cross-repo impact:
    ⚠ 2 consumer migration tickets created:
      - RAISE-311: contabilidad migration (Adan) — status: Open
      - RAISE-312: erp migration (Arnulfo) — status: Open

  Result: ✅ COMPLIANT — ready to merge
  Compliance score: 8/8 (100%)
```

### Scenario 5: Rodo Reviews Organizational Compliance

Rodo (architect) wants to see how the three repos are doing. He queries the
governance dashboard (via Rovo agent, CLI, or API):

```
── Compliance Report: Kurigage (2026-03-15) ──────────────

                       contabilidad    erp       apis
  G-001 OpenAPI        n/a             ✅         ✅
  G-002 Deprecation    n/a             n/a        ✅
  G-003 Health check   ✅               ✅         ✅
  G-004 Repository     ✅               ⚠ [W-001] ✅
  G-005 Coverage 80%   ✅ (87%)         ❌ (62%)   ✅ (91%)

  Repo-specific:
  G-100 2 reviewers    ✅ (contabilidad)
  G-101 Decimal types  ✅ (contabilidad)

  ──────────────────────────────────────────────────
  MUST compliance:     100%      100%      100%
  SHOULD compliance:   100%       50%      100%
  Overall:             100%       75%       100%

  Active waivers: 1
    W-001: G-004 in erp (StockService.php)
      Reason: Hotfix, refactor planned
      Tracked: RAISE-310
      Expires: 2026-04-15 (31 days remaining)

  ⚠ erp coverage at 62% — below SHOULD threshold of 80%
    Trend: 58% → 62% (improving, +4% this sprint)

  Recommendations:
  1. RAISE-310 (erp repository refactor) due in 31 days
  2. erp coverage needs +18% — suggest prioritizing domain
     test coverage in next sprint
```

### Scenario 6: Jorge Gets Business Visibility

Jorge (business owner) doesn't need guardrail details. He needs confidence:

```
── Portfolio Health: Kurigage ────────────────────────────

  contabilidad    🟢 92/100   Excellent
  erp             🟡 74/100   Needs attention
  apis            🟢 95/100   Excellent

  Governance compliance: 94% (16/17 checks passing)
  Technical debt: 1 active waiver, 1 SHOULD violation
  Trend: ↗ improving (was 88% two sprints ago)

  🔴 Attention needed:
     erp coverage below standard — team is aware, improving

  ✅ No MUST violations across any repository
```

---

## 5. Graph Schema Analysis — Gaps

### What Exists Today (18 node types, 11 edge types)

**Node types directly relevant to governance:**

| Node Type | Governance Role | Status |
|-----------|----------------|--------|
| `guardrail` | Governance rules with enforcement level, exceptions | ✅ Exists |
| `principle` | The "why" behind guardrails | ✅ Exists |
| `decision` | ADRs — specific architectural choices | ✅ Exists |
| `component` | What guardrails apply to | ✅ Exists |
| `module` | Higher-level grouping for guardrail scope | ✅ Exists |
| `pattern` | Evidence for guardrail effectiveness | ✅ Exists |
| `architecture` | Declared architecture (fitness function baseline) | ✅ Exists |
| `layer` | Architectural layers (dependency constraints) | ✅ Exists |
| `bounded_context` | DDD contexts (team ownership, API surface) | ✅ Exists |

**Edge types directly relevant to governance:**

| Edge Type | Governance Role | Status |
|-----------|----------------|--------|
| `governed_by` | Component governed by principle | ✅ Exists |
| `constrained_by` | Component constrained by guardrail | ✅ Exists |
| `applies_to` | Rule applies to context | ✅ Exists |
| `depends_on` | Cross-repo dependencies | ✅ Exists |
| `implements` | Component implements requirement | ✅ Exists |

### What's Missing

| Gap | Description | Implementation Complexity |
|-----|-------------|--------------------------|
| **Waiver node type** | New node type for structured exceptions | Low — subclass `GraphNode`, add fields |
| **Scope hierarchy** | Structured `scope` field with inheritance logic | Medium — scope resolution query logic |
| **Enforcement level** | Structured field on guardrail nodes | Low — metadata field, already possible with JSONB |
| **Compliance state** | Snapshot of compliance per repo at a point in time | Medium — new node type or materialized query |
| **Validation functions** | How to check each guardrail (not just what) | Medium — validation DSL (see governance-as-code-agents research) |
| **Cross-repo edges** | Edges that reference nodes in different `repo_id` | Low — already possible, just needs sync to populate them |
| **Waives edge** | `waiver --waives--> guardrail` relationship | Low — new edge type |

### Assessment

**~70% of the schema already supports governance.** The gaps are additive
(new node types, new metadata fields, new edge types), not breaking. The
`GraphNode` subclass system allows adding new types at runtime without schema
changes.

The biggest gap is not in the data model — it's in the **query layer** and
**skill integration**. The graph can store governance data today. What's missing
is:
1. Skills that query governance during workflow
2. Scope resolution logic (collect applicable guardrails for a given context)
3. Compliance reporting queries

---

## 6. Required Server Endpoints

Beyond the existing 7 endpoints, governance intelligence needs:

### New Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /api/v1/governance/applicable` | GET | Get guardrails applicable to a repo/module/component, resolving scope hierarchy |
| `POST /api/v1/governance/check` | POST | Run compliance check for a repo against all applicable guardrails |
| `GET /api/v1/governance/compliance` | GET | Get compliance report for org (all repos) or specific repo |
| `POST /api/v1/governance/waiver` | POST | Register a waiver for a guardrail |
| `GET /api/v1/governance/waivers` | GET | List active/expired waivers |
| `GET /api/v1/governance/impact` | GET | Get cross-repo impact analysis for a component change |

### Example: Applicable Guardrails Query

```
GET /api/v1/governance/applicable?repo=apis&module=invoices

Response:
{
  "repo": "apis",
  "module": "invoices",
  "guardrails": [
    {
      "id": "G-001",
      "content": "All public APIs must have versioned OpenAPI contract",
      "enforcement": "MUST",
      "scope": "org",
      "inherited_from": "org",
      "has_waiver": false
    },
    {
      "id": "G-002",
      "content": "Breaking API changes require 2-sprint deprecation",
      "enforcement": "MUST",
      "scope": "org",
      "inherited_from": "org",
      "has_waiver": false
    }
  ],
  "total": 2,
  "scope_chain": ["enterprise", "org", "team:backend", "repo:apis"]
}
```

### Example: Compliance Check

```
POST /api/v1/governance/check
{
  "repo": "erp",
  "include_waivers": true
}

Response:
{
  "repo": "erp",
  "checked_at": "2026-03-15T10:30:00Z",
  "guardrails_checked": 5,
  "results": [
    {"id": "G-001", "status": "pass", "enforcement": "MUST"},
    {"id": "G-003", "status": "pass", "enforcement": "MUST"},
    {"id": "G-004", "status": "waived", "enforcement": "SHOULD", "waiver": "W-001"},
    {"id": "G-005", "status": "fail", "enforcement": "SHOULD", "detail": "Coverage 62%, threshold 80%"}
  ],
  "must_compliance": 1.0,
  "should_compliance": 0.5,
  "overall_score": 0.75,
  "active_waivers": 1
}
```

---

## 7. Competitive Differentiation

### What Exists in the Market

| Tool | What it Does | Governance Scope | Limitation |
|------|-------------|-----------------|-----------|
| **SonarQube** | Static analysis (code quality, security) | Code rules only | No process, architecture, or cross-repo governance |
| **OPA / Rego** | Policy as code engine | Infrastructure and authorization | Not developer workflow; infra/deploy focused |
| **Backstage** | Developer portal + scorecards | Catalog + health checks | Observes and reports; doesn't prevent violations |
| **ArchUnit** | Architecture tests (Java) | Dependency rules | Single language, single repo, no process governance |
| **Semgrep** | Custom static analysis rules | Code patterns | Code only; no architecture, process, or cross-repo |
| **Jira Portfolio** | Capacity and roadmap | Project management | No code governance, no architecture awareness |
| **GitHub Advanced Security** | Vulnerability scanning | Security rules | Security only; no architecture or process governance |

### What RaiSE Does Differently

| Dimension | Others | RaiSE |
|-----------|--------|-------|
| **When** | After the fact (PR review, CI scan) | During work (skills check governance as you code) |
| **What** | Code rules OR process OR infra | Code + architecture + process + cross-repo in unified graph |
| **How** | Separate tool to install and configure | Embedded in the AI dev workflow (invisible to developer) |
| **Scope** | Single repo or infra | Multi-repo with scope hierarchy and inheritance |
| **Exceptions** | Ad-hoc (suppress warnings, //nolint) | Structured waivers with expiration, traceability, audit |
| **Evidence** | Rules are declared | Rules are backed by pattern evidence with statistical confidence |
| **Learning** | Static rules | Patterns promote to guardrails based on cross-repo evidence |

### The Unique Value Proposition

**RaiSE is not a governance checker. It's governance guardrails — built into the workflow.**

It doesn't run after you're done to tell you what you did wrong. It works
alongside you, knows the rules, surfaces them at the right moment, and makes it
structurally difficult to violate them — while providing a clear path for
legitimate exceptions.

The closest analogy is the difference between:
- A speed camera (SonarQube, Backstage) — catches you after the violation
- Lane assist (RaiSE) — keeps you in the lane while you drive

---

## 8. Implementation Priority

### Bottom-Up Build Order

Each layer depends on the one below:

| Priority | Capability | Depends On | Effort Estimate |
|----------|-----------|------------|-----------------|
| **P0** | Cross-repo edge sync (dependencies across repos) | Existing graph sync | S — extend sync to cross-repo edges |
| **P1** | Guardrail nodes with enforcement level + scope | Existing node types | S — metadata fields on guardrail nodes |
| **P2** | Scope resolution query (applicable guardrails) | P1 | M — query logic for hierarchy traversal |
| **P3** | Skill integration (design, implement, close) | P2 | M — modify 3 skills to query governance |
| **P4** | Waiver mechanism | P1 | S — new node type + edge |
| **P5** | Compliance check endpoint | P2, P4 | M — new API endpoint |
| **P6** | Compliance reporting (architect view) | P5 | S — aggregation query |
| **P7** | Portfolio health score (business view) | P6 | S — weighted scoring |

### Suggested Phasing

**Phase 1: Foundation (1 epic)**
- P0 + P1 + P2: Cross-repo edges, guardrail metadata, scope resolution
- Deliverable: "query applicable guardrails for any repo/module"

**Phase 2: Poka-yoke (1 epic)**
- P3 + P4: Skill integration + waiver mechanism
- Deliverable: "governance checks run during story design/implement/close"

**Phase 3: Visibility (1 epic)**
- P5 + P6 + P7: Compliance endpoint, architect report, business dashboard
- Deliverable: "Rodo sees compliance across all repos; Jorge sees health scores"

### Kurigage Validation Points

| Phase | What Kurigage Gets | Who Validates |
|-------|-------------------|---------------|
| Phase 1 | Rodo can define guardrails in the graph | Rodo |
| Phase 2 | Tech leads get governance during their workflow | Adan, Arnulfo, Sofi |
| Phase 3 | Rodo gets compliance dashboard, Jorge gets health score | Rodo, Jorge |

---

## 9. Open Questions

### Q1: Where do guardrails live? (Source of truth)

**Options:**
- A) YAML files in a governance repo (version controlled, PR-reviewed)
- B) Confluence pages parsed by Forge (content-first, Rovo-accessible)
- C) Direct API calls (programmatic, flexible)
- D) Hybrid: YAML as source, synced to server, accessible via API and Confluence

**Leaning:** D (Hybrid). YAML for version control + PR review, synced to server
for querying, mirrored to Confluence for human reading. This aligns with the
Forge integration design.

### Q2: How granular should validation functions be?

**Options:**
- A) Declarative only (guardrail says what, human/AI checks manually)
- B) Simple validators (file_exists, coverage_threshold, endpoint_exists)
- C) Full DSL with custom validators (see governance-as-code-agents research)

**Leaning:** Start with A (AI agent interprets guardrail during work), evolve to
B (automated checks for common patterns). C is over-engineering for now.

### Q3: How do cross-repo edges get populated?

**Options:**
- A) Manual declaration (dev says "repo X depends on repo Y")
- B) Automatic discovery (scan imports/API calls across repos)
- C) Hybrid: auto-discover within repos, manually declare cross-repo contracts

**Leaning:** C. Within a repo, discovery scan finds components and dependencies.
Cross-repo contracts (API consumption) are declared explicitly — you can't
auto-scan other people's repos without access.

### Q4: Enforcement at what level initially?

For Kurigage pilot:
- Start with MUST guardrails only (3-5 critical rules)
- Add SHOULD after the team is comfortable
- CAN is informational only — low priority

### Q5: Integration with existing Forge/Rovo design?

The walking skeleton (RAISE-274) already plans for governance validation via
the Rovo Rai Governance agent. The governance endpoints defined here (section 6)
would be the backend for that agent. The Forge app provides the UI, the server
provides the intelligence.

---

## 10. References

### Internal Research
- [governance-as-code-agents](../governance-as-code-agents/) — Policy DSL spec,
  enforcement patterns, implementation roadmap (Jan 29, 2026)
- [shared-memory-architecture](../shared-memory-architecture/) — Server architecture,
  multi-tenancy, scoping decisions (Feb 25, 2026)
- [atlassian-forge-integration](../atlassian-forge-integration/) — Forge app design,
  Rovo agents, walking skeleton (Feb 24, updated Feb 26)

### External Concepts
- **Poka-yoke** — Shigeo Shingo, Toyota Production System. Error-proofing
  mechanism that makes it impossible or immediately obvious when an error occurs.
  Three types: contact, fixed-value, motion-step.
- **RFC 2119** — "Key words for use in RFCs to Indicate Requirement Levels"
  (MUST, SHOULD, MAY). Standard for expressing enforcement levels.
- **Fitness Functions** — "Building Evolutionary Architectures" (Ford, Parsons,
  Kua). Automated checks that architecture conforms to declared intentions.
- **DORA Metrics** — "Accelerate" (Forsgren, Humble, Kim). Four key metrics for
  software delivery performance.
- **Policy as Code** — HashiCorp Sentinel, OPA/Rego. Encoding policies as
  executable code rather than documentation.

---

*Research by: Emilio + Claude Opus 4.6 | Session: SES-294 | Date: 2026-02-26*
*Status: Exploration complete — ready for /rai-problem-shape*
