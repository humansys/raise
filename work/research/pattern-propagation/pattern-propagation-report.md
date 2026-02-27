# Pattern Propagation for Multi-Repo Environments (Layer 2)

**Date:** 2026-02-26 | **Session:** SES-294 | **Author:** Emilio + Claude Opus 4.6
**Builds on:** [shared-memory-architecture](../shared-memory-architecture/) (Feb 25), [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) (Feb 26), [temporal-decay-pattern-scoring](../temporal-decay-pattern-scoring/) (Feb 7), [collective-intelligence-lineage](../collective-intelligence-lineage/) (Feb 2)

---

## 1. Problem Statement

### The Knowledge Silos Problem

Every repository in an organization is a learning island. When a developer
discovers a valuable pattern -- say, "repository pattern for DB access reduces
bug density by 40% in accounting calculations" -- that knowledge stays locked
in the repo's `.raise/rai/memory/patterns.jsonl`. Other teams with similar
domain logic never learn from it.

This is not a theoretical problem. It is the daily experience of every
multi-repo organization:

```
contabilidad/          erp/                  apis/
  .raise/                .raise/               .raise/
    memory/                memory/               memory/
      patterns.jsonl       patterns.jsonl        patterns.jsonl
      (120 patterns)       (85 patterns)         (60 patterns)

  Adan discovers:       Arnulfo reinvents:    Sofi never hears:
  "repo pattern         "our own abstraction  "could have used
   reduces bugs 40%"     layer... still buggy"  the same pattern"
```

### The Cost of Reinvention

When patterns don't propagate, organizations pay three costs:

| Cost | Description | Kurigage example |
|------|-------------|------------------|
| **Repeated mistakes** | Same error made independently in multiple repos | Adan found that raw SQL in domain logic causes test fragility; Arnulfo discovers this 3 weeks later |
| **Wasted validation** | Statistical evidence gathered once, never aggregated | Pattern validated 5x in contabilidad, 0x in erp, total evidence = 5 instead of potential 8+ |
| **Architectural drift** | Teams converge on different solutions to the same problem | Adan uses repository pattern, Arnulfo uses active record, Sofi uses CQRS -- all for CRUD |

### Why This Matters: Organizational Learning Requires Pattern Flow

An organization that learns is not one where individuals learn in isolation.
It is one where **knowledge flows** -- from where it is discovered to where it
is needed, with quality increasing as more teams validate it.

RaiSE already has the statistical machinery: Wilson score for confidence,
temporal decay for freshness, reinforcement for validation. What is missing is
the **propagation mechanism** -- the pipes that move patterns between repos,
the rules that determine when a pattern is "ready" to graduate, and the
inheritance model that ensures new repos benefit from accumulated wisdom.

### The Balance: Not All Patterns Are Universal

The hardest part of pattern propagation is not the mechanics. It is knowing
**what should propagate and what should not.**

- "Use `capsys` for stdout tests in pytest" -- universal, propagate everywhere
- "Our PHP entity naming convention is `XxxEntity`" -- team/stack specific
- "Emilio prefers TDD with red-green-refactor" -- personal, never propagate
- "Repository pattern reduces bug density 40%" -- strong candidate for org-level

The scope hierarchy must handle all of these without forcing patterns into the
wrong level.

---

## 2. Pattern Scope Hierarchy

### Four Levels

```
┌─────────────────────────────────────────┐
│            ENTERPRISE                    │  Patterns shared across orgs
│    (future: marketplace / community)     │  (e.g., open-source contributors)
├─────────────────────────────────────────┤
│            ORG                           │  All repos in the organization
│    (Kurigage: all 3 repos)              │  Validated across 2+ repos
├─────────────────────────────────────────┤
│            TEAM                          │  Repos sharing a stack/domain
│    (Kurigage: Adan+Arnulfo = PHP team)  │  Validated within team scope
├─────────────────────────────────────────┤
│            REPO                          │  Single repository
│    (where patterns are born)            │  Default scope for all new patterns
└─────────────────────────────────────────┘
```

### Scope Properties

| Property | REPO | TEAM | ORG | ENTERPRISE |
|----------|------|------|-----|------------|
| Visibility | This repo only | Repos in team | All repos in org | Cross-org |
| Who creates | Anyone | Anyone | Anyone (via promotion) | Community |
| Who promotes | Dev (auto) | Tech lead | Architect (HITL) | Governance |
| Decay half-life | 30 days | 45 days | 90 days | 180 days |
| Min evaluations | 1 | 3 across 2 repos | 5 across 3 repos | 10 across 5 orgs |
| Wilson threshold | 0.0 (any) | 0.4 | 0.6 | 0.7 |
| Auto-inherit | No | Yes (team repos) | Yes (all repos) | Opt-in |

### What Makes a Pattern "Promotable"

A pattern is a promotion candidate when it crosses scope-appropriate
statistical thresholds:

```
REPO → TEAM promotion criteria:
  - positives >= 3
  - evaluations >= 3
  - wilson_lower_bound(pos, neg) >= 0.4
  - validated_in_repos >= 2 (within same team)
  - age >= 7 days (no flash-in-the-pan promotions)

TEAM → ORG promotion criteria:
  - positives >= 5
  - evaluations >= 5
  - wilson_lower_bound(pos, neg) >= 0.6
  - validated_in_repos >= 3 (across teams)
  - age >= 14 days
  - HITL approval from architect role
```

### Inheritance Rules

When a new repo is added to an organization:

1. It **automatically receives** all ORG-level patterns in its context bundle
2. It receives TEAM-level patterns if assigned to a team
3. Inherited patterns start with `inherited: true` flag and `local_evaluations: 0`
4. First local evaluation converts it to a locally-tracked pattern
5. Local override is allowed (see Conflict Resolution below)

### Override Rules: Can a Repo Contradict an Org Pattern?

Yes. The model supports **contextual overrides** with traceability:

```json
{
  "id": "PAT-ORG-042",
  "scope": "org",
  "content": "Always use ORM for database access",
  "override_in": {
    "apis": {
      "content": "Raw SQL for performance-critical paths (>1000 TPS)",
      "reason": "ORM overhead unacceptable at API scale",
      "approved_by": "rodo",
      "date": "2026-03-01"
    }
  }
}
```

Rules:
- **Repo can be stricter** than org (always allowed)
- **Repo can override** with documented reason + approval
- **Repo cannot silently ignore** -- override must be explicit
- Override appears in governance dashboard (Layer 3 integration)

---

## 3. Core Mechanisms

### 3.1 Cross-Repo Reinforcement

#### The Problem

Pattern PAT-E-042 exists in `contabilidad` with 3 positives, 0 negatives.
Arnulfo in `erp` encounters the same insight independently. Today, he creates
a new pattern PAT-A-017 with the same content. Two islands, no connection.

#### The Mechanism

When a pattern is reinforced in any repo, the server checks for **similar
patterns** across repos in the same org:

```
Agent in erp reinforces local pattern
  → Server receives: POST /memory/patterns/{id}/reinforce
    → Server checks: "Are there similar patterns in other repos?"
    → Match found: PAT-E-042 in contabilidad (cosine similarity > 0.85
       OR exact context keyword overlap >= 60%)
    → Server creates cross-repo evaluation link
    → Aggregated Wilson score recalculated across repos
```

#### Detecting "Same Pattern" Across Repos

Three strategies, in order of complexity (simple first):

| Strategy | How | Precision | Recall | Effort |
|----------|-----|-----------|--------|--------|
| **Exact content match** | Normalize + hash | 100% | Low | Trivial |
| **Context keyword overlap** | Jaccard similarity >= 0.6 on context arrays | ~85% | Medium | Low |
| **Semantic similarity** | Embedding cosine >= 0.85 | ~90% | High | Medium (requires embedding model) |

**Recommendation:** Start with context keyword overlap (Jaccard). It uses
data we already have (the `context` array), requires no ML infrastructure,
and handles 80%+ of cases. Add semantic similarity in a later phase if needed.

#### Aggregated Wilson Score

When patterns are linked across repos, Wilson score aggregates all evaluations:

```python
# Per-repo Wilson scores are NOT averaged.
# Instead, raw counts are summed and a single Wilson score computed.

# contabilidad: 3 positives, 0 negatives
# erp:          2 positives, 1 negative
# apis:         1 positive,  0 negatives

total_pos = 3 + 2 + 1  # = 6
total_neg = 0 + 1 + 0  # = 1
aggregated_wilson = wilson_lower_bound(6, 1)  # ≈ 0.56

# This is more conservative than averaging per-repo scores,
# which is correct -- more data should tighten the bound,
# not inflate confidence.
```

#### Negative Reinforcement

Pattern fails in repo C -- what happens?

```
Repo A: 3 pos, 0 neg → wilson ≈ 0.56
Repo B: 2 pos, 0 neg → wilson ≈ 0.34
Repo C: 0 pos, 2 neg → wilson = 0.0

Aggregated: 5 pos, 2 neg → wilson ≈ 0.44
```

The negative evidence from repo C reduces overall confidence but does not
kill the pattern. This is correct -- patterns that work in some contexts and
fail in others are **contextual**, not wrong.

If negative reinforcement drops aggregated Wilson below 0.3, the system:
1. Flags pattern for review (not auto-demoted)
2. Notifies architect (Rodo)
3. Resolution: add context tags or split into context-specific patterns

### 3.2 Promotion

#### Promotion Flow

```
                        AUTOMATIC                    HITL
                     ┌─────────────┐          ┌─────────────┐
                     │             │          │             │
  Pattern born  ─────▶   REPO     ├──────────▶   TEAM      ├──────────▶  ORG
  in repo            │  (default) │  3+ pos   │  tech lead  │  5+ pos    │ architect
                     │            │  2+ repos │  approves   │  3+ repos  │ approves
                     └─────────────┘          └─────────────┘            └──────────
```

#### Promotion Criteria (Detailed)

**REPO to TEAM (automatic with notification):**

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Positive evaluations | >= 3 | Minimum sample for Wilson confidence |
| Cross-repo validation | >= 2 repos within team | Proves it's not repo-specific |
| Wilson lower bound | >= 0.4 | Conservative -- not enough data for high bar |
| Pattern age | >= 7 days | Avoid promoting patterns that haven't been tested over time |
| No active negative trend | neg/eval ratio < 0.3 | Don't promote contested patterns |

**TEAM to ORG (requires architect HITL):**

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Positive evaluations | >= 5 | Stronger evidence required |
| Cross-repo validation | >= 3 repos across teams | Must transcend team context |
| Wilson lower bound | >= 0.6 | Higher bar for org-wide guidance |
| Pattern age | >= 14 days | More time for counter-evidence |
| Architect approval | Required | HITL gate prevents noise at org level |

#### What Happens When a Pattern Gets Promoted

```
1. EVENT: Pattern PAT-E-042 meets TEAM promotion criteria
2. SERVER: Creates promotion record in pattern_promotions table
   {
     "pattern_id": "PAT-E-042",
     "from_scope": "repo",
     "to_scope": "team",
     "promoted_at": "2026-03-01T14:30:00Z",
     "promoted_by": "system",  // or "rodo" for HITL
     "evidence": {
       "positives": 4,
       "negatives": 0,
       "repos": ["contabilidad", "erp"],
       "wilson": 0.63
     }
   }
3. SERVER: Updates pattern scope to "team"
4. SERVER: Emits agent_event: "pattern_promoted"
5. AGENTS: Next context bundle for team repos includes this pattern
6. NOTIFICATION: Tech lead notified (Adan or Arnulfo)
```

### 3.3 Inheritance

#### New Repo Onboarding

When Kurigage adds a fourth repo (e.g., `mobile-app` for Flutter):

```
1. Repo registered: POST /orgs/{org_id}/repos
   body: { "repo_id": "mobile-app", "team": "mobile" }

2. Server computes inherited patterns:
   - All ORG-level patterns (scope = "org")
   - All TEAM-level patterns for "mobile" team (if team exists)
   - Filtered by relevance: context keywords match repo's stack tags

3. Agent context bundle for mobile-app includes:
   ┌─────────────────────────────────────────────┐
   │ INHERITED ORG PATTERNS (12 patterns)         │
   │                                               │
   │ PAT-ORG-001: Repository pattern reduces bugs  │
   │   confidence: 0.71 | repos: 3 | scope: org   │
   │   [inherited, not yet locally evaluated]      │
   │                                               │
   │ PAT-ORG-007: Integration tests before merge   │
   │   confidence: 0.83 | repos: 3 | scope: org   │
   │   [inherited, not yet locally evaluated]      │
   └─────────────────────────────────────────────┘
```

#### Context-Aware Filtering

Not all org patterns are relevant to every repo. The agent surfaces inherited
patterns based on **context keyword matching** against the current task:

```
Story: "Implement user authentication for mobile-app"
Context keywords: ["auth", "security", "api", "tokens"]

Inherited patterns matched:
  ✓ PAT-ORG-012: "JWT rotation reduces session hijack risk" (context: ["auth", "security"])
  ✓ PAT-ORG-003: "Validate all API inputs" (context: ["api", "validation"])
  ✗ PAT-ORG-019: "PHP entity naming convention" (context: ["php", "naming"])  -- filtered out
```

### 3.4 Conflict Resolution

#### The Core Tension

Repo A says: "Always use ORM for database access"
Repo B says: "Raw SQL for performance-critical paths"

Both are valid. This is not a contradiction -- it is **context-dependent truth.**

#### Resolution Strategy

Patterns carry context tags. The agent considers local context when surfacing
inherited patterns:

```
┌──────────────────────────────────────────────────┐
│ PATTERN: "Always use ORM for database access"     │
│ scope: org | confidence: 0.71                     │
│ context: ["database", "orm", "crud"]              │
│                                                    │
│ LOCAL OVERRIDE in apis:                            │
│   "Raw SQL for performance-critical paths          │
│    (>1000 TPS measured by load test)"              │
│   context: ["database", "performance", "scale"]    │
│   approved_by: rodo | reason: documented           │
│                                                    │
│ AGENT BEHAVIOR:                                    │
│ - In contabilidad (CRUD-heavy): surfaces ORM       │
│ - In apis (perf-critical): surfaces raw SQL        │
│ - In new repo: surfaces ORM (default org pattern)  │
│   + mentions override exists in apis               │
└──────────────────────────────────────────────────┘
```

#### Classification: Contextual vs. Universal Patterns

| Type | Example | Propagation rule |
|------|---------|------------------|
| **Universal** | "Test before commit" | Promote freely, no context filter |
| **Stack-specific** | "Use capsys for stdout tests" | Promote within repos sharing pytest |
| **Domain-specific** | "Repository pattern for accounting" | Promote within repos with financial domain |
| **Contradictory** | ORM vs raw SQL | Both exist as contextual; agent picks based on local tags |

---

## 4. Pattern Lifecycle Across Repos

```
LEARN          VALIDATE        PROMOTE         DISTRIBUTE      REINFORCE/DECAY
(repo)         (repo)          (team/org)      (all repos)     (continuous)
  │               │                │                │                │
  ▼               ▼                ▼                ▼                ▼
Developer      Pattern used     Criteria met    Inherited by     Evaluated in
discovers      in 3+ stories    auto or HITL    team/org repos   each repo
pattern        Wilson >= 0.4    → new scope     via context      aggregated
               in source repo                   bundle           Wilson score
                                                                 + decay
```

### Stage Details

| Stage | Trigger | Criteria | Mechanism | Output |
|-------|---------|----------|-----------|--------|
| **LEARN** | Developer/agent adds pattern | None | `rai pattern add` or story-review auto-capture | Pattern with scope=repo, evaluations=0 |
| **VALIDATE** | Story-review reinforcement | 3+ evaluations, Wilson >= 0.4 | `rai pattern reinforce` | Pattern with statistical confidence |
| **PROMOTE** | Threshold met + HITL (for org) | See S3.2 criteria tables | Server-side promotion engine | Scope upgraded, promotion record |
| **DISTRIBUTE** | Pattern promoted | Higher scope | Context bundle includes pattern | New repos see pattern automatically |
| **REINFORCE** | Used in new repo | Local evaluation (+1/-1) | Cross-repo reinforcement endpoint | Aggregated Wilson recalculated |
| **DECAY** | Time passes | None (continuous) | Exponential decay with scope-specific half-life | Score decreases unless re-evaluated |

### Decay at Different Scope Levels

Org-level patterns should decay slower than repo-level patterns. They
represent validated organizational knowledge, not ephemeral local insights.

| Scope | Half-life | Rationale |
|-------|-----------|-----------|
| REPO | 30 days | Local patterns may become stale quickly |
| TEAM | 45 days | Team knowledge validated across 2+ repos |
| ORG | 90 days | Org knowledge validated across 3+ repos |
| ENTERPRISE | 180 days | Community knowledge with broad validation |
| FOUNDATIONAL | No decay | Core principles (TDD, HITL, etc.) |

This mirrors how organizational knowledge actually ages: a local trick may
become irrelevant in a month, but an org-wide architectural decision stays
relevant for quarters.

---

## 5. Kurigage Scenarios

### Scenario 1: Pattern Discovered and Propagated

**Adan discovers "repository pattern reduces bug density 40%"**

```
Week 1: Adan in contabilidad
  Session: Implementing PaymentRepository
  rai pattern add "Repository pattern for DB access reduces bug density ~40%
    in accounting calculations" -c "architecture,repository,database,accounting"
  → PAT-E-042 created, scope=repo, evaluations=0

Week 2: Story review in contabilidad
  rai pattern reinforce PAT-E-042 --vote 1 --from RAISE-301
  → PAT-E-042: positives=1, evaluations=1

Week 3: Two more stories use it
  → PAT-E-042: positives=3, evaluations=3, wilson≈0.56

Week 3: Arnulfo in erp encounters similar pattern
  rai pattern add "Repository abstraction reduces coupling in domain logic"
    -c "architecture,repository,database,domain"
  → PAT-A-017 created in erp

Week 4: Server detects similarity (context overlap: architecture, repository, database)
  → Links PAT-E-042 ↔ PAT-A-017
  → Aggregated: 4 positives across 2 repos
  → Meets TEAM promotion criteria

Week 4: Arnulfo's agent during next story design:
  ┌─────────────────────────────────────────────────┐
  │ SUGGESTED PATTERN (recently promoted to team):   │
  │                                                   │
  │ "Repository pattern for DB access reduces bug     │
  │  density ~40% in accounting calculations"         │
  │                                                   │
  │ Confidence: 0.63 | Validated in: contabilidad,   │
  │ erp | Scope: team                                 │
  │                                                   │
  │ Related local pattern: PAT-A-017                  │
  └─────────────────────────────────────────────────┘
```

### Scenario 2: Cross-Stack Pattern Validation

**Sofi's .NET repo confirms a pattern from PHP repos**

```
ORG pattern: "Integration tests before merge reduce regression by 60%"
  Originally from: contabilidad (PHP), erp (PHP)
  Scope: team (PHP team)

Sofi in apis (.NET):
  Applies pattern independently
  rai pattern reinforce PAT-ORG-007 --vote 1 --from RAISE-315

Result:
  - Pattern now validated in .NET stack (not just PHP)
  - Crosses team boundary → eligible for ORG promotion
  - Aggregated: 6 positives, 0 negatives, across 3 repos, 2 stacks
  - Wilson ≈ 0.68 → exceeds ORG threshold (0.6)
  - Rodo receives notification: "Pattern ready for ORG promotion"

Rodo reviews:
  rai pattern promote PAT-TEAM-007 --to org --approved-by rodo
  "This makes sense cross-stack. Approve."
```

### Scenario 3: Pattern Fails in One Repo

**Negative reinforcement, confidence drops**

```
ORG pattern: "Cache frequently accessed entities in memory"
  Confidence: 0.71 | Repos: contabilidad, apis

Arnulfo in erp:
  Tries caching approach. ERP has high-write workload.
  Cache invalidation causes stale data bugs.
  rai pattern reinforce PAT-ORG-022 --vote -1 --from RAISE-320

Before: 5 pos, 0 neg → wilson ≈ 0.64
After:  5 pos, 1 neg → wilson ≈ 0.50

System response:
  - Wilson still above 0.3 → not flagged for review
  - Pattern now carries context note: "Failed in high-write workload (erp)"
  - Agent in future repos will mention: "Note: this pattern failed in
    high-write contexts (erp). Consider your write/read ratio."

If 2 more failures:
  5 pos, 3 neg → wilson ≈ 0.30 → flagged for review
  Rodo notified: "Pattern PAT-ORG-022 has declining confidence"
  Options: split into context-specific patterns, demote, or archive
```

### Scenario 4: Pattern Catalog for Architect

**Rodo wants to see "what patterns are shared across all repos?"**

```
GET /api/v1/memory/patterns?scope=org&sort=wilson_desc&limit=20

Response:
{
  "patterns": [
    {
      "id": "PAT-ORG-007",
      "content": "Integration tests before merge reduce regression by 60%",
      "scope": "org",
      "wilson_score": 0.68,
      "total_positives": 6,
      "total_negatives": 0,
      "repos_validated": ["contabilidad", "erp", "apis"],
      "promoted_at": "2026-03-01T14:30:00Z",
      "promoted_by": "rodo"
    },
    {
      "id": "PAT-ORG-042",
      "content": "Repository pattern for DB access reduces bug density ~40%",
      "scope": "org",
      "wilson_score": 0.63,
      "total_positives": 5,
      "total_negatives": 0,
      "repos_validated": ["contabilidad", "erp"],
      "overrides": [{"repo": "apis", "reason": "CQRS pattern used instead"}]
    }
  ],
  "count": 20,
  "scope_summary": {
    "org": 12,
    "team": 28,
    "repo_total": 265
  }
}
```

### Scenario 5: New Repo Inherits Org Patterns

**mobile-app repo added, automatically inherits high-confidence patterns**

```
POST /api/v1/orgs/{org_id}/repos
body: { "repo_id": "mobile-app", "team": "mobile", "stack_tags": ["flutter", "dart"] }

Server response:
{
  "repo_id": "mobile-app",
  "inherited_patterns": {
    "org_level": 12,
    "team_level": 0,  // new team, no team patterns yet
    "filtered_out": 5  // PHP-specific patterns excluded
  }
}

First session in mobile-app, agent context bundle includes:
  12 org patterns sorted by wilson score
  Agent says: "This repo inherits 12 organizational patterns.
  Key ones relevant to your current task:
  - Integration tests before merge (confidence: 0.68)
  - Validate all API inputs (confidence: 0.65)
  - Repository pattern for data access (confidence: 0.63)"
```

---

## 6. Graph Schema Gap Analysis

### Current State

**Local (JSONL):**
```json
{
  "id": "PAT-E-042",
  "type": "architecture",
  "content": "Repository pattern for DB access reduces bug density ~40%",
  "context": ["architecture", "repository", "database"],
  "learned_from": "RAISE-301",
  "created": "2026-03-01",
  "positives": 3,
  "negatives": 0,
  "evaluations": 3,
  "last_evaluated": "2026-03-15"
}
```

**Server (`memory_patterns` table):**
```sql
id          UUID PK
org_id      UUID FK → organizations
content     TEXT
context     JSONB (array)
properties  JSONB (dict)
created_at  TIMESTAMP
```

### What Is Missing for Propagation

| Gap | Description | Priority | Effort |
|-----|-------------|----------|--------|
| `scope` column | Pattern scope (repo/team/org/enterprise) | P0 | S (migration) |
| `repo_id` column | Which repo created/owns this pattern | P0 | S (migration) |
| `pattern_type` column | codebase/process/architecture/technical | P1 | S (migration) |
| `evaluations` table | Per-repo evaluation tracking with votes | P0 | M (new table + endpoints) |
| `promotions` table | Promotion history with evidence snapshots | P1 | M (new table + endpoints) |
| `pattern_links` table | Cross-repo pattern similarity links | P1 | M (new table + matching logic) |
| Aggregated Wilson | Computed from all evaluations across repos | P0 | S (query/view) |
| `inherited` flag | Whether pattern was inherited or locally created | P1 | XS (properties JSONB) |
| `override` records | Repo-level overrides of higher-scope patterns | P2 | S (properties or table) |
| `team_id` mapping | Repo-to-team assignment | P1 | S (new column or table) |

### Proposed Schema Changes

**New columns on `memory_patterns`:**
```sql
ALTER TABLE memory_patterns ADD COLUMN scope VARCHAR(20) DEFAULT 'repo';
ALTER TABLE memory_patterns ADD COLUMN repo_id VARCHAR(255);
ALTER TABLE memory_patterns ADD COLUMN pattern_type VARCHAR(50);
ALTER TABLE memory_patterns ADD COLUMN source_pattern_id UUID;  -- links to parent if promoted
```

**New table: `pattern_evaluations`:**
```sql
CREATE TABLE pattern_evaluations (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id  UUID REFERENCES memory_patterns(id),
    org_id      UUID REFERENCES organizations(id),
    repo_id     VARCHAR(255) NOT NULL,
    vote        SMALLINT NOT NULL CHECK (vote IN (-1, 1)),  -- no 0 (N/A not stored)
    story_ref   VARCHAR(255),  -- e.g., "RAISE-301"
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX ix_eval_pattern ON pattern_evaluations(pattern_id);
CREATE INDEX ix_eval_repo ON pattern_evaluations(repo_id);
```

**New table: `pattern_promotions`:**
```sql
CREATE TABLE pattern_promotions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id   UUID REFERENCES memory_patterns(id),
    org_id       UUID REFERENCES organizations(id),
    from_scope   VARCHAR(20) NOT NULL,
    to_scope     VARCHAR(20) NOT NULL,
    promoted_by  VARCHAR(255),  -- "system" or user identifier
    evidence     JSONB NOT NULL,  -- snapshot of stats at promotion time
    promoted_at  TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

**New table: `pattern_links`:**
```sql
CREATE TABLE pattern_links (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_a_id UUID REFERENCES memory_patterns(id),
    pattern_b_id UUID REFERENCES memory_patterns(id),
    org_id       UUID REFERENCES organizations(id),
    similarity   FLOAT NOT NULL,  -- 0.0 to 1.0
    match_method VARCHAR(50),     -- "keyword_overlap", "semantic", "exact"
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(pattern_a_id, pattern_b_id)
);
```

### Effort Estimate

| Component | Size | Dependencies |
|-----------|------|--------------|
| Alembic migration (columns + tables) | M | None |
| Evaluation tracking endpoint | M | Migration |
| Promotion engine (server-side) | L | Evaluations |
| Pattern matching (Jaccard) | S | Pattern links table |
| Aggregated Wilson query | S | Evaluations table |
| CLI integration (promote command) | M | Promotion endpoint |
| Context bundle with inherited patterns | M | Scope + inheritance query |
| **Total** | **XL (3-4 stories)** | |

---

## 7. Required Server Endpoints

### 7.1 Pattern Reinforcement (Cross-Repo)

**`POST /api/v1/memory/patterns/{pattern_id}/reinforce`**

```json
// Request
{
  "repo_id": "erp",
  "vote": 1,
  "story_ref": "RAISE-320"
}

// Response
{
  "pattern_id": "uuid-here",
  "vote": 1,
  "repo_evaluations": {
    "contabilidad": {"positives": 3, "negatives": 0},
    "erp": {"positives": 1, "negatives": 0}
  },
  "aggregated": {
    "total_positives": 4,
    "total_negatives": 0,
    "wilson_score": 0.63,
    "repos_count": 2
  },
  "promotion_eligible": true,
  "promotion_target": "team"
}
```

### 7.2 Pattern Promotion

**`POST /api/v1/memory/patterns/{pattern_id}/promote`**

```json
// Request
{
  "to_scope": "org",
  "approved_by": "rodo",
  "comment": "Validated across PHP and .NET stacks"
}

// Response
{
  "pattern_id": "uuid-here",
  "new_scope": "org",
  "promotion_record": {
    "from_scope": "team",
    "to_scope": "org",
    "promoted_by": "rodo",
    "evidence": {
      "positives": 6,
      "negatives": 0,
      "wilson": 0.68,
      "repos": ["contabilidad", "erp", "apis"]
    }
  }
}
```

### 7.3 Cross-Repo Pattern Search

**`GET /api/v1/memory/patterns?scope=org&context=database,repository&sort=wilson_desc`**

```json
// Response
{
  "patterns": [
    {
      "id": "uuid",
      "content": "Repository pattern for DB access reduces bug density ~40%",
      "scope": "org",
      "pattern_type": "architecture",
      "context": ["architecture", "repository", "database"],
      "wilson_score": 0.63,
      "evaluations": {
        "total": 5,
        "positives": 5,
        "negatives": 0,
        "repos": ["contabilidad", "erp"]
      },
      "promoted_at": "2026-03-01T14:30:00Z"
    }
  ],
  "count": 1,
  "filters_applied": {
    "scope": "org",
    "context_match": ["database", "repository"]
  }
}
```

### 7.4 Pattern Context Bundle (for Agents)

**`GET /api/v1/memory/patterns/context-bundle?repo_id=mobile-app&task_context=auth,security`**

```json
// Response
{
  "repo_id": "mobile-app",
  "patterns": {
    "local": [],
    "inherited_team": [],
    "inherited_org": [
      {
        "id": "uuid",
        "content": "JWT rotation reduces session hijack risk",
        "scope": "org",
        "wilson_score": 0.71,
        "match_reason": "context overlap: auth, security"
      }
    ]
  },
  "total": 3,
  "note": "Inherited patterns have not been locally evaluated yet"
}
```

### 7.5 Pattern Similarity Check

**`POST /api/v1/memory/patterns/find-similar`**

```json
// Request
{
  "content": "Repository abstraction reduces coupling in domain logic",
  "context": ["architecture", "repository", "database", "domain"],
  "repo_id": "erp"
}

// Response
{
  "matches": [
    {
      "pattern_id": "uuid-of-PAT-E-042",
      "content": "Repository pattern for DB access reduces bug density ~40%",
      "repo_id": "contabilidad",
      "similarity": 0.78,
      "match_method": "keyword_overlap",
      "overlapping_context": ["architecture", "repository", "database"]
    }
  ],
  "suggestion": "Consider reinforcing existing pattern instead of creating new one"
}
```

---

## 8. Knowledge Management Literature

### 8.1 SECI Model (Nonaka & Takeuchi, 1995)

The SECI model describes knowledge creation as a spiral through four
conversion modes. RaiSE patterns map directly to this spiral:

```
                    TACIT                      EXPLICIT
              ┌──────────────┐          ┌──────────────┐
              │              │          │              │
   TACIT      │ Socialization│─────────▶│Externalization│
              │              │          │              │
   from       │  Developer   │          │  Developer   │
              │  observes    │          │  writes      │
              │  something   │          │  pattern     │
              │  working     │          │  via `rai    │
              │              │          │  pattern add`│
              └──────┬───────┘          └──────┬───────┘
                     │                         │
                     │                         ▼
              ┌──────┴───────┐          ┌──────────────┐
              │              │          │              │
   EXPLICIT   │Internalization│◀────────│ Combination  │
              │              │          │              │
   from       │  Agent       │          │  Server      │
              │  surfaces    │          │  aggregates  │
              │  pattern     │          │  patterns    │
              │  during      │          │  across      │
              │  story design│          │  repos,      │
              │  → dev       │          │  computes    │
              │  applies it  │          │  Wilson      │
              └──────────────┘          └──────────────┘
```

| SECI Phase | KM Description | RaiSE Mechanism |
|------------|---------------|-----------------|
| **Socialization** (Tacit-Tacit) | Sharing experience through observation | Developer sees pattern working in code reviews, pair programming |
| **Externalization** (Tacit-Explicit) | Articulating tacit knowledge | `rai pattern add` -- developer captures insight as explicit pattern |
| **Combination** (Explicit-Explicit) | Combining explicit knowledge sources | Server aggregates patterns across repos, computes Wilson, links similar patterns |
| **Internalization** (Explicit-Tacit) | Learning by doing | Agent surfaces pattern in story design; dev applies it; pattern becomes tacit knowledge |

**Key insight:** Traditional SECI requires human facilitation at every step.
RaiSE automates the Combination phase (cross-repo aggregation) and partially
automates Internalization (agent surfaces relevant patterns at the right
moment in the workflow). This dramatically reduces the friction that makes
organizational knowledge management fail in practice.

**Source:** Nonaka, I. & Takeuchi, H. (1995). _The Knowledge-Creating Company_. Oxford University Press. See also [SECI Model operationalization (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6914727/).

### 8.2 Communities of Practice (Wenger, 1998)

Wenger defines Communities of Practice (CoPs) as groups that share a concern
and learn how to do it better through regular interaction. Three structural
elements define a CoP: **mutual engagement**, **joint enterprise**, and
**shared repertoire**.

RaiSE creates a form of **automated CoP** where the "regular interaction" is
mediated by the agent and the shared graph:

| CoP Element | Traditional | RaiSE Equivalent |
|-------------|------------|------------------|
| **Mutual engagement** | Regular meetings, Slack channels | Shared pattern graph; cross-repo reinforcement |
| **Joint enterprise** | Shared goals negotiated by group | Org-level patterns represent collective agreement |
| **Shared repertoire** | Jargon, tools, stories | Context keywords, pattern types, Wilson scores |

**What RaiSE adds to CoP theory:** Wenger notes that CoPs are fragile --
they depend on regular participation and fade without it. RaiSE patterns
persist independently of participation. A pattern validated by 5 people
across 3 repos retains its confidence even if those people move on. The
knowledge graph is the **institutional memory** that CoPs typically lack.

**Source:** Wenger, E. (1998). _Communities of Practice: Learning, Meaning, and Identity_. Cambridge University Press. See also [Introduction to Communities of Practice](https://www.wenger-trayner.com/introduction-to-communities-of-practice/) and [HBR: Communities of Practice: The Organizational Frontier](https://hbr.org/2000/01/communities-of-practice-the-organizational-frontier).

### 8.3 Double-Loop Learning (Argyris, 1977)

Argyris distinguishes:
- **Single-loop learning:** Detecting and correcting errors without questioning
  underlying assumptions. "The code has a bug; fix the bug."
- **Double-loop learning:** Questioning and modifying the governing values
  that led to the error. "Why does our architecture keep producing this class
  of bugs?"

```
Single-loop:  action → outcome → correction → action
                                      ↑
Double-loop:  action → outcome ─────────────→ change governing variable
                                              "change how we think about this"
```

Most pattern systems are single-loop: "record what went wrong, avoid next
time." RaiSE patterns enable double-loop learning when:

1. **Negative reinforcement triggers reflection:** A pattern that fails in a
   new context forces questioning: "Is this really a universal pattern, or is
   it context-dependent?" This is double-loop -- the failure changes the
   governing variable (the pattern's scope/context), not just the action.

2. **Cross-repo contradiction creates dialogue:** When `contabilidad` says
   "always use ORM" and `apis` says "raw SQL for performance," the system
   surfaces this as a governance topic, not an error. The organization
   learns that the right answer depends on context -- a meta-pattern.

3. **Pattern promotion requires evidence:** Moving from repo to org requires
   cross-repo validation. This forces the question: "Is this pattern
   actually universal, or do we just believe it is?" Statistical evidence
   (Wilson score) replaces assumption.

**What RaiSE adds to double-loop theory:** Argyris notes that organizations
resist double-loop learning due to defensive routines. RaiSE reduces
defensiveness by making it **statistical, not personal**. A pattern that fails
is not "your idea was wrong" -- it is "the data shows 2/5 repos had negative
outcomes." The Wilson score is neutral; it does not blame.

**Source:** Argyris, C. (1977). Double loop learning in organizations. _Harvard Business Review_, 55(5), 115-125. See also [Double-loop learning (Wikipedia)](https://en.wikipedia.org/wiki/Double-loop_learning) and [Kanban Zone on Argyris](https://kanbanzone.com/2026/chris-argyris-organizational-learning-ii-double-loop-learning/).

### 8.4 How RaiSE Differs from Traditional KM

Traditional knowledge management fails for well-documented reasons:

| KM Problem | Traditional Approach | RaiSE Approach |
|------------|---------------------|----------------|
| "Nobody reads the wiki" | Confluence pages, Notion docs | Agent surfaces patterns in workflow -- you don't read, the agent brings it to you |
| "Knowledge goes stale" | Manual review cycles | Temporal decay (exponential, scope-specific half-life) |
| "No quality signal" | Upvotes, likes (popularity) | Wilson score (statistical confidence with sample size) |
| "Knowledge doesn't flow" | Newsletters, all-hands | Automatic promotion based on cross-repo validation |
| "Context is lost" | Tags, categories | Context keywords + scope hierarchy + local overrides |
| "Tribal knowledge" | Onboarding docs | Inherited patterns for new repos + agent context bundles |

The fundamental difference: traditional KM is **push-based** (someone writes
a document, hopes someone reads it). RaiSE is **pull-based with automated
delivery** (the agent surfaces what is relevant when it is needed).

---

## 9. Competitive Landscape

### 9.1 Organizational Knowledge Sharing Models

| Approach | How It Works | Strengths | Weaknesses |
|----------|-------------|-----------|------------|
| **InnerSource Commons** | Open-source practices within organizations; pattern books | Well-documented patterns; community-driven | Manual; no automation; patterns are documents not data |
| **Google Code Health** | Readability reviews, style guides enforced by tooling | Scales to 1000s of repos; automated checks | Binary (pass/fail); no confidence; no cross-repo learning |
| **Spotify Guilds/Chapters** | Cross-team interest groups that share knowledge | Organic; developer-driven | Depends on participation; knowledge stays in heads |
| **SAFe CoPs** | Formal communities of practice within SAFe framework | Structured; enterprise-friendly | Heavy process; meetings, not data |

### 9.2 Knowledge Management Tools

| Tool | Approach | How Patterns Flow | Limitation for Our Use Case |
|------|----------|-------------------|-----------------------------|
| **Confluence** | Wiki pages with labels, spaces | Manual: someone writes, others read | No statistical confidence; no agent integration |
| **Notion** | Collaborative docs, databases | Manual + some automation | No cross-repo scope hierarchy |
| **Guru** | Verified knowledge cards with expiry | Manual curation + staleness alerts | Human-curated; doesn't scale with velocity |
| **Backstage (Spotify)** | Service catalog + TechDocs | Plugin-based documentation aggregation | Read-only catalog; no pattern learning loop |

### 9.3 AI-Specific Tools

| Tool | Knowledge Model | Cross-Repo Learning | Gap vs RaiSE |
|------|----------------|---------------------|---------------|
| **GitHub Copilot** | Learns from all public code | Global patterns (implicit in weights) | No organizational hierarchy; no explicit patterns; no statistical confidence |
| **Sourcegraph Cody** | Code search + context from all repos | Cross-repo code search | Code-level, not pattern-level; no Wilson score; no promotion |
| **Cursor** | Codebase indexing per-repo | Per-repo context only | No cross-repo propagation at all |
| **Windsurf** | Per-repo memory | Per-repo context only | Same limitation as Cursor |

### 9.4 RaiSE's Differentiation

What makes RaiSE pattern propagation unique:

1. **Statistical confidence:** Patterns have Wilson scores, not upvotes.
   A pattern validated 5x across 3 repos has a mathematically bounded
   confidence interval.

2. **Organizational hierarchy:** repo -> team -> org -> enterprise scope
   with promotion criteria and inheritance. Nobody else has this.

3. **Agent-integrated delivery:** Patterns surface in the development
   workflow (story design, implementation) -- not in a wiki nobody reads.

4. **Automated combination:** Cross-repo pattern matching and aggregation
   happen server-side. Developers don't need to search for related patterns.

5. **Evidence-based promotion:** Promotion requires statistical evidence
   across repos. Not "someone thought this was important" but "this worked
   in 3 repos with Wilson >= 0.6."

6. **Contextual overrides:** Higher-scope patterns can be overridden with
   documentation. The system supports nuance, not just binary rules.

No competitive tool combines all six. Most have 0-1.

---

## 10. Implementation Priority

### Phase 1: Foundation (MVP for Pro launch)

**Goal:** Enable cross-repo pattern visibility and manual promotion.

| Task | Size | What It Enables |
|------|------|-----------------|
| Alembic migration: scope, repo_id, pattern_type columns | S | Patterns carry scope metadata |
| `pattern_evaluations` table + reinforcement endpoint | M | Cross-repo evaluation tracking |
| Enhanced `GET /patterns` with scope filter + aggregated Wilson | M | Rodo can see org-wide pattern catalog |
| Context bundle endpoint with inherited patterns | M | Agents in new repos see org patterns |
| `rai pattern promote` CLI command (manual, HITL) | S | Architect can promote patterns |
| **Phase 1 Total** | **L** (1 epic, 4-5 stories) | |

### Phase 2: Automation

**Goal:** Automatic detection of similar patterns and promotion suggestions.

| Task | Size | What It Enables |
|------|------|-----------------|
| `pattern_links` table + Jaccard matching engine | M | Server detects "same pattern" across repos |
| Automatic promotion suggestions (meets criteria -> notification) | M | Reduced HITL burden |
| `pattern_promotions` table + promotion history | S | Audit trail for promotions |
| Team-level scope (repo-to-team mapping) | S | Intermediate scope between repo and org |
| **Phase 2 Total** | **L** (1 epic, 3-4 stories) | |

### Phase 3: Intelligence

**Goal:** Semantic matching, conflict detection, analytics.

| Task | Size | What It Enables |
|------|------|-----------------|
| Semantic similarity (embedding model integration) | L | Better cross-repo pattern detection |
| Conflict detection + override workflow | M | Manages contradictions proactively |
| Pattern analytics dashboard (for Rovo/Forge app) | L | Organizational learning metrics |
| Enterprise scope (cross-org patterns for marketplace) | M | Community patterns |
| **Phase 3 Total** | **XL** (1-2 epics) | |

### Build Order

```
Phase 1 (Pro launch MVP) ──▶ Phase 2 (automation) ──▶ Phase 3 (intelligence)
    ~3-4 weeks                    ~3-4 weeks                ~6-8 weeks
```

### Minimum Viable Propagation for Pro Launch

The absolute minimum for the Pro launch demo:

1. Patterns have scope (repo/org) in the DB
2. Cross-repo evaluation tracking (POST reinforcement from any repo)
3. Aggregated Wilson score across repos
4. Context bundle endpoint (agent gets inherited patterns)
5. Manual promote command (HITL by architect)

This covers Kurigage Scenarios 1, 4, and 5 without any ML, semantic matching,
or automation. Scenarios 2 and 3 work too, but pattern linking (detecting
"same pattern") is manual.

---

## 11. Open Questions

### Q1: Should pattern matching use keywords only or add embeddings?

**Options:**
- (A) Keywords only (Jaccard on context arrays) -- simple, no ML dependency
- (B) Keywords + lightweight embeddings (sentence-transformers) -- better recall
- (C) LLM-based comparison -- highest quality, highest cost

**Leaning:** A for Phase 1, B for Phase 2. We have context keyword arrays on
every pattern. Jaccard similarity >= 0.6 catches most cases. Embeddings add
value for semantic near-misses (e.g., "repository pattern" vs "data access
layer abstraction") but require infrastructure.

### Q2: Should promotion be fully automatic or always HITL?

**Options:**
- (A) Fully automatic based on criteria -- scales, but noise risk
- (B) Always HITL (architect reviews) -- safe, but bottleneck
- (C) Automatic for repo->team, HITL for team->org -- graduated trust

**Leaning:** C. Low-scope promotions (repo->team) are low risk and high
volume. Org-level patterns affect everyone and should have architect review.
This maps to Kurigage: Adan/Arnulfo auto-promote within PHP team, Rodo
approves for org.

### Q3: How do patterns interact with governance rules (Layer 3)?

**Options:**
- (A) Independent -- patterns are suggestions, governance is enforcement
- (B) Patterns can become governance rules via formal adoption
- (C) Shared continuum -- same data model, different enforcement level

**Leaning:** B. A pattern with Wilson >= 0.8 and org scope is a strong
candidate for a SHOULD-level governance rule. The promotion from pattern to
rule should be explicit (Rodo's decision) but the data is the same.

### Q4: What is the right decay half-life for org-level patterns?

**Options:**
- (A) Same as repo (30 days) -- aggressive, forces re-evaluation
- (B) 90 days -- 3x repo, appropriate for validated knowledge
- (C) 180 days -- 6x repo, org decisions should be stable
- (D) No decay for org patterns -- they are promoted, therefore validated

**Leaning:** B. 90 days provides appropriate stability without allowing
stale org patterns to persist indefinitely. Foundational patterns (explicitly
marked) skip decay entirely, as they already do at repo level.

### Q5: Should the context bundle be pull-based (agent requests) or push-based (server notifies)?

**Options:**
- (A) Pull: Agent calls context-bundle endpoint at session/story start
- (B) Push: Server notifies when new patterns are inherited
- (C) Hybrid: Pull for context bundles, push for promotion notifications

**Leaning:** C. The agent should pull its context bundle at story-start
(this is the natural integration point). But promotion events should push
notifications (via agent_events) so architects know when patterns are ready
for review.

---

## 12. References

### Internal Research

| ID | Title | Date | Relevance |
|----|-------|------|-----------|
| [shared-memory-architecture](../shared-memory-architecture/) | Storage backend, multi-tenancy, scope model | Feb 25 | Foundation: DB schema, scope levels, Graphiti pattern |
| [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) | Layer 3: governance rules, poka-yoke | Feb 26 | Sister research: patterns may become governance rules |
| [temporal-decay-pattern-scoring](../temporal-decay-pattern-scoring/) | Wilson score, half-life decay formula | Feb 7 | Core algorithm: Wilson lower bound + exponential decay |
| [collective-intelligence-lineage](../collective-intelligence-lineage/) | Pattern provenance, contribution modes | Feb 2 | Vision: lineage metadata, attribution, sharing spectrum |
| [governance-as-code-agents](../governance-as-code-agents/) | Local policy enforcement DSL | Jan 29 | Precursor: single-repo governance, now extended to multi-repo |

### External Literature

| Author | Work | Year | Relevance |
|--------|------|------|-----------|
| Nonaka, I. & Takeuchi, H. | _The Knowledge-Creating Company_ | 1995 | SECI model: tacit/explicit knowledge conversion spiral |
| Wenger, E. | _Communities of Practice: Learning, Meaning, and Identity_ | 1998 | CoP theory: mutual engagement, shared repertoire |
| Argyris, C. | "Double loop learning in organizations" (HBR) | 1977 | Double-loop learning: questioning governing variables |
| InnerSource Commons | [InnerSource Patterns](https://innersourcecommons.org/learn/) | 2025 | Cross-team collaboration patterns in software orgs |
| Spotify Engineering | [Guilds: Knowledge Sharing in Large-Scale Agile](https://ieeexplore.ieee.org/document/8648260/) | 2019 | Cross-team knowledge sharing model |
| SAFe | [Communities of Practice (Extended Guidance)](https://framework.scaledagile.com/communities-of-practice) | 2025 | Formal CoP structure within scaled agile |

### External Technical References

| Source | URL | Relevance |
|--------|-----|-----------|
| Wilson score interval | [Wikipedia](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Wilson_score_interval) | Statistical foundation for pattern confidence |
| Jaccard similarity | [Wikipedia](https://en.wikipedia.org/wiki/Jaccard_index) | Keyword overlap metric for pattern matching |
| PMC SECI operationalization | [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6914727/) | Empirical validation of SECI model |
| Wenger-Trayner intro to CoP | [wenger-trayner.com](https://www.wenger-trayner.com/introduction-to-communities-of-practice/) | Accessible overview of CoP theory |
| Argyris double-loop (original) | [HBR 1977 PDF](https://theisrm.org/documents/Argyris%20(1977)%20Double%20Loop%20Learning%20in%20Organizations.pdf) | Original paper on double-loop learning |

---

*Research ID: RES-PROPAGATION-001*
*Contributors: Emilio Osorio, Rai (Claude Opus 4.6)*
*Session: SES-294, 2026-02-26*
