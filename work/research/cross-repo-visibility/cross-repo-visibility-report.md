# Cross-Repo Visibility (Layer 1) — Research Report

**Date:** 2026-02-26 | **Session:** SES-294 | **Author:** Emilio + Claude Opus 4.6

---

## 1. Problem Statement

### The Island Repos Problem

In a multi-repo organization, each repository is an island. Developers work
inside their repo, commit to their repo, test their repo. The knowledge graph
for each repo understands its own components, modules, layers, and dependencies
— but has zero visibility into what happens across repo boundaries.

This is not a hypothetical problem. It is the default state of every multi-repo
organization in the world.

```
  contabilidad         erp              apis
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ graph    │    │ graph    │    │ graph    │
  │          │    │          │    │          │
  │ InvoiceSync   │ ApiClient│    │ POST     │
  │ .php     │    │ .cs      │    │ /invoices│
  │          │    │          │    │          │
  │  ???     │    │  ???     │    │  (owner) │
  └──────────┘    └──────────┘    └──────────┘
       │                │                │
       └────────────────┴────────────────┘
              No visibility between repos
```

### The Cost of Late Discovery

| Discovery Timing | Cost | Example |
|-----------------|------|---------|
| **Design time** | ~0 (prevent the problem) | "This endpoint has 4 consumers — design migration plan" |
| **PR review** | Low (rework one PR) | Reviewer catches breaking change, asks for deprecation |
| **CI/CD** | Medium (integration test failure) | Consumer's pipeline fails after provider merges |
| **Staging** | High (blocked release) | QA finds broken integration, blocks sprint delivery |
| **Production** | Very High (incident) | Adan's accounting sync breaks at 2am, invoices stop flowing |

The further right on this spectrum you discover a cross-repo dependency issue,
the more it costs. The "shift left" principle applies here: make cross-repo
dependencies visible as early as possible.

### Why This Matters More With AI Agents

AI agents amplify both velocity and risk:

- **Higher velocity = more changes per day.** An AI-assisted developer makes
  changes faster. If those changes break cross-repo contracts, the breakage
  happens faster too.
- **Agent lacks institutional memory.** A human developer might remember "oh,
  Adan uses this endpoint." An AI agent does not — unless the information is in
  the knowledge graph.
- **Agents work in isolation by default.** Each agent session has context for its
  repo only. Without cross-repo edges, the agent literally cannot know about
  external consumers.

The combination of "faster changes" + "no cross-repo awareness" = faster breakage.
Cross-repo visibility is the safety net that makes AI-assisted development safe
in multi-repo environments.

### The Kurigage Context

| Role | Person | Repo | Stack | Cross-Repo Surface |
|------|--------|------|-------|--------------------|
| Architect | Rodo | (cross-cutting) | Architecture decisions | Sees all repos |
| Tech Lead | Adan | contabilidad | Symphony/PHP (accounting) | Consumes apis endpoints |
| Tech Lead | Arnulfo | erp | Symphony/PHP (ERP) | Consumes apis endpoints |
| Tech Lead | Sofi | apis | .NET (APIs) | Provides endpoints to all |
| Business Owner | Jorge | (visibility) | Wants "are things working?" | No technical visibility |

**The real problem, stated simply:** Sofi changes `POST /invoices` in the `apis`
repo. Adan finds out when his accounting sync breaks in production. Nobody told
him. Nobody knew to tell him. The dependency was invisible.

---

## 2. Three Core Capabilities

Cross-repo visibility breaks into three distinct capabilities, each building
on the graph infrastructure that exists today (Layer 0).

```
┌────────────────────────────────────────────────┐
│ 2.3 Duplicate/Overlap Detection                │
│   "3 repos have their own auth wrapper"         │
├────────────────────────────────────────────────┤
│ 2.2 Impact Analysis                            │
│   "Changing X affects 4 consumers in 2 repos"   │
├────────────────────────────────────────────────┤
│ 2.1 Dependency Graph Cross-Repo                │
│   "Who depends on component X in repo Y?"       │
├────────────────────────────────────────────────┤
│ 0. Shared Memory (EXISTS — E275)               │
│   graph_nodes + graph_edges + multi-tenancy     │
└────────────────────────────────────────────────┘
```

### 2.1 Dependency Graph Cross-Repo

#### The Core Concept

Today, edges in `graph_edges` connect nodes within the same `repo_id`. The
schema already supports cross-repo edges — the `source_id` and `target_id`
are FK references to `graph_nodes.id`, and nodes from different repos live
in the same table. **The schema does not prevent cross-repo edges.** What is
missing is the mechanism to populate them.

A cross-repo dependency edge looks like:

```
graph_nodes:
  id: uuid-A, org_id: kurigage, repo_id: contabilidad, node_id: InvoiceSync
  id: uuid-B, org_id: kurigage, repo_id: apis,          node_id: POST-invoices

graph_edges:
  source_id: uuid-A (contabilidad/InvoiceSync)
  target_id: uuid-B (apis/POST-invoices)
  edge_type: depends_on
  repo_id: contabilidad   ← edge "owned" by the consuming repo
  properties: {"call_sites": 3, "methods": ["syncInvoice", "validateInvoice", "getInvoiceStatus"]}
```

#### Granularity Levels

Cross-repo dependencies can be expressed at three levels:

| Level | Question | Example | Use Case |
|-------|----------|---------|----------|
| **Repo-to-repo** | "Which repos depend on which?" | contabilidad -> apis | Executive dashboard, high-level architecture |
| **Module-to-module** | "Which modules depend on which?" | contabilidad/fiscal -> apis/invoices | Architect planning, team coordination |
| **Component-to-component** | "Which file/class depends on which endpoint?" | InvoiceSync.php -> POST /invoices | Impact analysis, blast radius |

The finer the granularity, the more useful for impact analysis, but the harder
to populate automatically. Recommendation: start at module-to-module with
optional component-to-component for API contracts.

#### Cross-Repo Dependency Query

```
Query: "Who depends on POST /invoices in apis?"

Result:
┌─────────────────────────────────────────────────────────────┐
│ Dependents of apis/POST-invoices                             │
│                                                              │
│ REPO              MODULE          COMPONENT       CALL SITES │
│ contabilidad      fiscal          InvoiceSync.php      3     │
│ erp               billing         ApiClient.cs         1     │
│                                                              │
│ Total: 2 repos, 2 modules, 2 components, 4 call sites       │
└─────────────────────────────────────────────────────────────┘
```

#### Dependency Matrix (Repo-to-Repo)

```
                    PROVIDES →
                contabilidad    erp         apis
CONSUMES ↓
contabilidad      -              -          ██ (3)
erp               -              -          █ (1)
apis              -              -            -

Legend: █ = dependency count
```

This matrix is the "cross-repo map" that Rodo (architect) would use to
understand the coupling between repos at a glance.

### 2.2 Impact Analysis

#### BFS Traversal Across Repo Boundaries

Impact analysis answers: "If I change node X, what might break?"

The algorithm is a bounded BFS (Breadth-First Search) starting from the modified
node, following `depends_on` edges in reverse (who depends on me?), crossing
repo boundaries via the shared graph.

```
Algorithm: cross_repo_impact(start_node, max_depth=3)

1. Load subgraph from PostgreSQL:
   SELECT * FROM graph_nodes WHERE org_id = :org
   SELECT * FROM graph_edges WHERE org_id = :org AND edge_type = 'depends_on'

2. Build NetworkX DiGraph (in-memory, already supported by rai-core)

3. BFS from start_node, following REVERSE depends_on edges:
   depth 0: apis/POST-invoices (the changed node)
   depth 1: contabilidad/InvoiceSync, erp/ApiClient  (direct dependents)
   depth 2: contabilidad/FiscalReport (depends on InvoiceSync) (transitive)

4. Classify results:
   - Direct dependencies (depth 1): HIGH impact
   - Transitive dependencies (depth 2+): MEDIUM impact
   - Same repo: no cross-repo coordination needed
   - Different repo: coordination required — flag for notification
```

#### Blast Radius Calculation

```
Impact analysis for: apis/POST-invoices (proposed change)

BLAST RADIUS:
  Direct (depth 1):
    contabilidad/InvoiceSync.php     3 call sites    Owner: Adan
    erp/ApiClient.cs                 1 call site     Owner: Arnulfo

  Transitive (depth 2):
    contabilidad/FiscalReport.php    uses InvoiceSync Owner: Adan
    contabilidad/SATSync.php         uses InvoiceSync Owner: Adan

  Summary:
    Repos affected:        2 / 3
    Direct dependents:     2 components
    Transitive dependents: 2 components
    Total call sites:      4
    Coordination needed:   Adan (contabilidad), Arnulfo (erp)

  RISK LEVEL: HIGH (>1 repo affected, >2 call sites)
```

#### Integration With /rai-story-design

This is where cross-repo visibility becomes actionable. During
`/rai-story-design`, the skill queries the shared graph for impact:

```
── /rai-story-design ──────────────────────────────────────

Story: "Modify POST /invoices to add tax breakdown field"
Repo: apis

Analyzing cross-repo impact...

  This component has cross-repo dependents:
  ┌──────────────────────────────────────────────────────┐
  │ contabilidad/InvoiceSync.php (Adan)                  │
  │   3 call sites — syncInvoice(), validateInvoice(),   │
  │                   getInvoiceStatus()                  │
  │                                                      │
  │ erp/ApiClient.cs (Arnulfo)                           │
  │   1 call site — CreateInvoice()                      │
  └──────────────────────────────────────────────────────┘

  Is this a BREAKING change to the endpoint contract?

  If additive (new optional field):    No coordination needed
  If breaking (field rename/removal):  Migration plan required
```

#### Direct vs. Transitive Dependencies

It is critical to differentiate these in the output:

| Type | Meaning | Action Required |
|------|---------|-----------------|
| **Direct** | Component A directly calls/consumes component B | Must coordinate before change |
| **Transitive** | Component A depends on B which depends on C | Inform, but may not need direct action |

The BFS depth tells you this automatically. Depth 1 = direct. Depth 2+ = transitive.

### 2.3 Duplicate/Overlap Detection

#### The Problem

In multi-repo environments, teams independently build similar solutions. Three
repos might each have their own HTTP client wrapper, their own authentication
helper, their own date formatting utility. This leads to:

- **Maintenance burden**: Fix a bug in 3 places instead of 1
- **Inconsistency**: Three slightly different auth implementations
- **Onboarding friction**: "Which auth wrapper do I use?"

#### Similarity Approaches

| Approach | How It Works | Accuracy | Effort |
|----------|-------------|----------|--------|
| **Name matching** | Compare component `node_id` across repos (fuzzy match) | Low-Medium | Low |
| **Structural similarity** | Compare component metadata: type, dependencies, interfaces | Medium | Medium |
| **Content similarity** | Compare `content` field (descriptions) using TF-IDF or similar | Medium-High | Medium |
| **Semantic similarity** | Embedding-based comparison of component descriptions | High | High (needs embeddings) |

**Recommendation:** Start with name matching + structural similarity. These
are simple, deterministic, and catch the obvious cases (3 components named
`HttpClient`, `HttpWrapper`, `ApiClient` with similar dependency patterns).

#### Detection Algorithm (Phase 1: Simple)

```
Algorithm: detect_duplicates(org_id, min_similarity=0.6)

1. Load all component/module nodes for the org:
   SELECT * FROM graph_nodes
   WHERE org_id = :org AND node_type IN ('component', 'module')

2. Group by node_type, then compare across repos:
   For each pair (nodeA from repoX, nodeB from repoY):
     name_sim  = fuzzy_ratio(nodeA.node_id, nodeB.node_id)  # 0-1
     type_sim  = 1.0 if same component type, else 0.5
     desc_sim  = cosine_sim(tfidf(nodeA.content), tfidf(nodeB.content))
     score     = 0.4 * name_sim + 0.2 * type_sim + 0.4 * desc_sim

3. Filter pairs where score >= min_similarity

4. Return ranked list of potential duplicates
```

#### What To Do When Duplicates Found

Not all duplicates should be consolidated. The decision framework:

| Signal | Action | Rationale |
|--------|--------|-----------|
| Same functionality, same interface | **Consolidate** into shared lib | Clear duplication, extract to shared package |
| Same functionality, different interface | **Evaluate** | May be intentional divergence (different contexts) |
| Similar name, different functionality | **Rename** for clarity | False positive — reduce naming confusion |
| Same functionality, intentional fork | **Accept divergence** with documentation | Team autonomy outweighs DRY at repo boundary |

The system surfaces duplicates. Humans (Rodo, in Kurigage's case) decide what
to do about them. The graph records the decision.

#### Kurigage Example

```
Duplicate Detection Report: Kurigage

POTENTIAL DUPLICATES (similarity >= 0.7):

1. HTTP Client Wrappers (similarity: 0.85)
   contabilidad/src/Http/ApiClient.php        (Adan)
   erp/src/Infrastructure/HttpClient.php      (Arnulfo)
   apis/src/Clients/InternalHttpClient.cs     (Sofi)

   Recommendation: Evaluate consolidation.
   All three wrap Guzzle/HttpClient for internal API calls.

2. Auth Token Management (similarity: 0.78)
   contabilidad/src/Auth/TokenManager.php     (Adan)
   erp/src/Auth/JwtHelper.php                 (Arnulfo)

   Recommendation: Consolidate.
   Both manage JWT refresh for the same auth server.

3. Date Formatting (similarity: 0.72)
   contabilidad/src/Utils/MexicanDate.php     (Adan)
   erp/src/Helpers/DateFormatter.php          (Arnulfo)

   Recommendation: Accept divergence.
   contabilidad has SAT-specific date formats; erp has ERP-specific.
   Different enough to justify separate implementations.
```

---

## 3. How Cross-Repo Edges Get Populated

This is the critical question. The graph schema supports cross-repo edges today.
But how do they get into the graph?

### Option A: Manual Declaration

Developer explicitly declares cross-repo dependencies.

```yaml
# In contabilidad/.raise/cross-repo-deps.yaml
dependencies:
  - from: InvoiceSync
    to:
      repo: apis
      component: POST-invoices
    call_sites: 3
    methods: [syncInvoice, validateInvoice, getInvoiceStatus]
```

| Pros | Cons |
|------|------|
| Explicit, precise, intentional | Manual labor — devs won't maintain it |
| No false positives | Stale data — dependencies change but file doesn't |
| Works across any language/stack | Missing data — devs forget to declare |
| Simple to implement | Doesn't scale with repo count |

### Option B: Automatic Discovery

Scan source code to find cross-repo references automatically.

```
Scanner finds:
  InvoiceSync.php line 42: $this->httpClient->post('/invoices', $data)
  ↓ resolves to
  apis repo, POST /invoices endpoint
```

| Pros | Cons |
|------|------|
| Always up to date | Requires multi-language parsing (PHP, .NET, etc.) |
| No developer effort | Can't scan repos you don't have access to |
| Catches all references | False positives (string matching is imprecise) |
| Scales automatically | Hard to resolve dynamic URLs, config-driven endpoints |

### Option C: Hybrid (Recommended)

Combine automatic intra-repo discovery with explicit cross-repo contract
registration.

```
WITHIN REPO (automatic):
  Discovery scan → finds components, modules, internal dependencies
  This already exists: `rai discover scan`

BETWEEN REPOS (contract-based):
  API providers register their contracts (OpenAPI specs, shared types)
  Consumers declare which contracts they depend on
  The server matches consumers to providers automatically
```

#### How the Hybrid Approach Works

**Step 1: Provider registers API contract**

```yaml
# apis/.raise/contracts.yaml (or auto-extracted from openapi.yaml)
provides:
  - id: POST-invoices
    type: rest_endpoint
    path: /api/v1/invoices
    method: POST
    version: v1
    schema_ref: openapi.yaml#/paths/~1invoices/post
```

When `apis` syncs its graph to the server, this contract becomes a node:

```
node_type: component
node_id: contract:POST-invoices
repo_id: apis
properties: {
  "contract_type": "rest_endpoint",
  "path": "/api/v1/invoices",
  "method": "POST",
  "version": "v1"
}
```

**Step 2: Consumer declares dependency on contract**

```yaml
# contabilidad/.raise/contracts.yaml
consumes:
  - contract: POST-invoices
    provider_repo: apis
    used_by: [InvoiceSync, ValidateInvoice]
    call_sites: 3
```

When `contabilidad` syncs its graph, the dependency becomes a cross-repo edge:

```
graph_edges:
  source_id: (contabilidad/InvoiceSync)
  target_id: (apis/contract:POST-invoices)
  edge_type: depends_on
  repo_id: contabilidad
  properties: {"call_sites": 3, "contract_version": "v1"}
```

**Step 3: Server matches and validates**

The server knows about both the provider's contract and the consumer's
declaration. It can:

1. Validate that the referenced contract exists
2. Detect version mismatches (consumer expects v1, provider moved to v2)
3. Aggregate all consumers for a contract (blast radius)
4. Alert when a contract changes but consumers haven't updated

### Option D: OpenAPI/Schema Registry (Extension of C)

For REST APIs specifically, auto-extract contracts from OpenAPI specs:

```
Provider syncs OpenAPI spec → server parses → creates contract nodes
Consumer declares consumption → server creates cross-repo edges

Bonus: server detects breaking changes by diffing OpenAPI versions
```

This is powerful but only works for well-documented APIs. Not all endpoints
have OpenAPI specs. In Kurigage's case, Sofi's .NET APIs likely have OpenAPI
(Swagger is default in .NET), but Arnulfo's PHP endpoints might not.

### Recommendation

**Start with Option C (Hybrid)** for these reasons:

1. **Pragmatic**: Manual contract declaration is low-effort for the common case
   (3-10 cross-repo dependencies)
2. **Correct by construction**: Explicit declarations are always accurate
3. **Stack-agnostic**: Works regardless of language (PHP, .NET, Python, etc.)
4. **Incremental**: Start with manual YAML, evolve to OpenAPI auto-extraction
5. **Fits existing workflow**: `.raise/contracts.yaml` fits the existing
   `.raise/` configuration pattern

For Kurigage specifically, the three repos likely have 5-10 cross-repo
dependencies. Manual declaration takes 10 minutes per repo. The value is
immediate. Auto-discovery can be added later for repos with 50+ dependencies.

---

## 4. Kurigage Scenarios

### Scenario 1: Sofi Changes POST /invoices — Blast Radius During Design

Sofi is working on a story to add a mandatory `tax_breakdown` field to the
`POST /invoices` request body. This is a breaking change.

She runs `/rai-story-design`:

```
── /rai-story-design ──────────────────────────────────────

Story: "Add mandatory tax_breakdown field to POST /invoices"
Repo: apis

Querying shared graph for cross-repo impact...

CROSS-REPO IMPACT ANALYSIS:
┌─────────────────────────────────────────────────────────────┐
│ apis/contract:POST-invoices has 2 cross-repo consumers:      │
│                                                              │
│  REPO             COMPONENT             CALL SITES  OWNER    │
│  contabilidad     InvoiceSync.php            3     Adan     │
│  erp              ApiClient.cs               1     Arnulfo  │
│                                                              │
│  This is a BREAKING CHANGE (new mandatory field).            │
│                                                              │
│  Required actions:                                           │
│  1. Version the endpoint (POST /v2/invoices)                 │
│  2. Maintain v1 for deprecation period                       │
│  3. Notify consumer teams:                                   │
│     - Adan: 3 call sites in contabilidad need updates        │
│     - Arnulfo: 1 call site in erp needs update               │
│  4. Create migration tickets for consumers                   │
│                                                              │
│  Blast radius: 2 repos, 4 call sites                         │
│  Risk level: HIGH                                            │
└─────────────────────────────────────────────────────────────┘

Include migration plan in story design? [y/n]
```

**Result:** The problem is surfaced at design time. Sofi designs her change
with migration in mind. Adan and Arnulfo get tickets before the breaking
change ships. Zero production incidents.

### Scenario 2: Rodo Asks "Show Me All Cross-Repo Dependencies"

Rodo wants to understand the coupling between Kurigage's three repos.

```
Query: GET /api/v1/visibility/dependencies?org=kurigage

CROSS-REPO DEPENDENCY MATRIX:
                    PROVIDES →
                contabilidad    erp         apis
CONSUMES ↓
contabilidad      -              -          ██ (5)
erp               -              -          ██ (3)
apis              -              -            -

DETAILED DEPENDENCIES:

contabilidad → apis:
  InvoiceSync.php  → POST /invoices      (3 calls)
  SATSync.php      → GET /invoices/{id}  (1 call)
  TaxCalc.php      → GET /tax-rates      (1 call)

erp → apis:
  ApiClient.cs     → POST /invoices      (1 call)
  ProductSync.cs   → GET /products       (1 call)
  StockService.php → POST /stock-events  (1 call)

TOPOLOGY:
  apis is a pure PROVIDER (0 outgoing, 8 incoming)
  contabilidad is a pure CONSUMER (5 outgoing, 0 incoming)
  erp is a pure CONSUMER (3 outgoing, 0 incoming)

RISK ASSESSMENT:
  apis is a critical dependency — all other repos depend on it
  No circular dependencies detected
  Coupling level: MODERATE (8 cross-repo edges across 3 repos)
```

### Scenario 3: New Dev Joins — "What Does This Repo Depend On?"

A new developer joins the contabilidad team. They ask: "What external
dependencies does this repo have?"

```
Query: GET /api/v1/visibility/dependencies?repo=contabilidad&direction=outgoing

EXTERNAL DEPENDENCIES FOR contabilidad:

  apis/POST /invoices      ← InvoiceSync.php (3 calls)
  apis/GET /invoices/{id}  ← SATSync.php (1 call)
  apis/GET /tax-rates      ← TaxCalc.php (1 call)

  Summary: 3 external API dependencies, all to apis repo
  Owner of apis: Sofi
  Contract versions: all v1

  TIP: If you need to understand any of these APIs, check
  apis/openapi.yaml or ask Sofi.
```

This onboarding query replaces the typical "ask around until someone tells you
what depends on what" process. The answer is always current because it comes
from the graph.

### Scenario 4: Duplicate Detection

Rodo runs a duplicate scan across all Kurigage repos:

```
Query: GET /api/v1/visibility/duplicates?org=kurigage

POTENTIAL DUPLICATES DETECTED:

1. Authentication Token Management (similarity: 0.82)
   ┌──────────────────────────────────────────────────┐
   │ contabilidad/src/Auth/TokenManager.php           │
   │   "Manages JWT token refresh for API auth"       │
   │                                                  │
   │ erp/src/Auth/JwtHelper.php                       │
   │   "JWT token helper with automatic refresh"      │
   │                                                  │
   │ Shared traits: same auth server, same token      │
   │ format, same refresh logic                       │
   │                                                  │
   │ Recommendation: CONSOLIDATE — extract to         │
   │ shared-auth package                              │
   └──────────────────────────────────────────────────┘

2. HTTP Client Abstraction (similarity: 0.78)
   ┌──────────────────────────────────────────────────┐
   │ contabilidad/src/Http/ApiClient.php              │
   │ erp/src/Infrastructure/HttpClient.php            │
   │ apis/src/Clients/InternalHttpClient.cs           │
   │                                                  │
   │ Three HTTP client wrappers with retry/timeout    │
   │                                                  │
   │ Recommendation: EVALUATE — different stacks      │
   │ (PHP vs .NET) may justify separate implementations│
   └──────────────────────────────────────────────────┘

3. Invoice DTO Models (similarity: 0.75)
   ┌──────────────────────────────────────────────────┐
   │ contabilidad/src/Models/InvoiceDTO.php           │
   │ erp/src/Models/Invoice.php                       │
   │ apis/src/Models/InvoiceRequest.cs                │
   │                                                  │
   │ All three define invoice data structures          │
   │                                                  │
   │ Recommendation: ACCEPT DIVERGENCE — each repo    │
   │ has different fields for their specific context.  │
   │ Consider shared-contracts package for the         │
   │ canonical API contract fields only.               │
   └──────────────────────────────────────────────────┘

Summary: 3 duplicate clusters found across 3 repos
  CONSOLIDATE: 1 (auth token management)
  EVALUATE:    1 (HTTP clients)
  ACCEPT:      1 (invoice DTOs)
```

---

## 5. Graph Schema Gap Analysis

### What Exists Today

The current schema already supports most of Layer 1:

| Component | Status | Cross-Repo Ready? |
|-----------|--------|-------------------|
| `graph_nodes` table | Exists | YES — org_id + repo_id scoping |
| `graph_edges` table | Exists | YES — source/target are FK to graph_nodes, cross-repo edges possible |
| UNIQUE(org_id, repo_id, node_id) | Exists | YES — nodes are unique per repo |
| `depends_on` edge type | Exists | YES — can be used for cross-repo deps |
| `component` node type | Exists | YES — can represent API contracts |
| `module` node type | Exists | YES — can represent module-level deps |
| Full-text search | Exists | Partial — searches within org, not cross-repo aware |
| NetworkX in-memory engine | Exists | YES — BFS traversal already supported |
| GIN index on properties | Exists | YES — can query contract metadata |

### What is Missing

| Gap | Description | Effort | Priority |
|-----|-------------|--------|----------|
| **Cross-repo edge population mechanism** | No way to sync edges that reference nodes in other repos. Current `sync_graph` resolves node_ids within a single repo_id. | Medium | P0 |
| **Contract node convention** | No convention for representing API contracts as nodes (e.g., `contract:POST-invoices` prefix) | Low | P0 |
| **Cross-repo edge resolution in sync** | `resolve_node_ids()` only searches within one repo_id. Needs to support `target_repo_id` parameter. | Low | P0 |
| **Dependency direction metadata** | No `direction` field on edges to distinguish provider vs consumer perspective | Low | P1 |
| **Contract version tracking** | No convention for versioning contract nodes | Low | P1 |
| **Duplicate detection query** | No server-side query for finding similar nodes across repos | Medium | P2 |
| **Impact analysis traversal** | No server-side BFS traversal endpoint. Today queries return flat results, not graph traversals. | Medium | P1 |
| **Owner metadata on nodes** | No structured field for team/person ownership of components | Low | P2 |
| **Edge repo_id semantics** | Current edge `repo_id` = "which repo owns this edge." For cross-repo edges, need clear convention: edge belongs to consumer repo. | Low (convention only) | P0 |

### Assessment

**~80% of the data model is already in place.** The PostgreSQL schema with
`graph_nodes` and `graph_edges` using UUID foreign keys already allows
cross-repo edges. The gaps are primarily in:

1. **Sync logic** — `resolve_node_ids()` needs to support cross-repo target
   resolution
2. **Query logic** — Need traversal queries (BFS), not just keyword search
3. **Conventions** — Need node naming and metadata conventions for contracts
4. **Population** — Need a mechanism (YAML + sync) to declare cross-repo deps

No schema migrations are needed for the basic capability. The existing JSONB
`properties` column handles all additional metadata (contract type, version,
call sites, owner).

---

## 6. Required Server Endpoints

### Existing Endpoints (7)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /health` | GET | Health check |
| `POST /api/v1/graph/sync` | POST | Full graph sync for a repo |
| `GET /api/v1/graph/query` | GET | Keyword search across nodes |
| `POST /api/v1/agent/events` | POST | Store agent telemetry |
| `GET /api/v1/agent/events` | GET | Retrieve agent events |
| `POST /api/v1/memory/patterns` | POST | Store memory patterns |
| `GET /api/v1/memory/patterns` | GET | Retrieve memory patterns |

### New Endpoints Needed

#### 6.1 Cross-Repo Dependencies

```
GET /api/v1/visibility/dependencies
  ?org=kurigage
  &repo=contabilidad        (optional: filter to one repo)
  &direction=outgoing        (optional: outgoing|incoming|both)
  &granularity=component     (optional: repo|module|component)

Response:
{
  "org": "kurigage",
  "dependencies": [
    {
      "source_repo": "contabilidad",
      "source_node": "InvoiceSync",
      "source_type": "component",
      "target_repo": "apis",
      "target_node": "contract:POST-invoices",
      "target_type": "component",
      "edge_type": "depends_on",
      "properties": {
        "call_sites": 3,
        "methods": ["syncInvoice", "validateInvoice", "getInvoiceStatus"],
        "contract_version": "v1"
      }
    }
  ],
  "matrix": {
    "contabilidad->apis": 5,
    "erp->apis": 3
  },
  "total_cross_repo_edges": 8
}
```

#### 6.2 Impact Analysis

```
GET /api/v1/visibility/impact
  ?node_id=contract:POST-invoices
  &repo=apis
  &max_depth=3

Response:
{
  "source": {
    "repo": "apis",
    "node_id": "contract:POST-invoices",
    "node_type": "component"
  },
  "impact": {
    "direct": [
      {
        "repo": "contabilidad",
        "node_id": "InvoiceSync",
        "node_type": "component",
        "depth": 1,
        "call_sites": 3,
        "owner": "Adan"
      },
      {
        "repo": "erp",
        "node_id": "ApiClient",
        "node_type": "component",
        "depth": 1,
        "call_sites": 1,
        "owner": "Arnulfo"
      }
    ],
    "transitive": [
      {
        "repo": "contabilidad",
        "node_id": "FiscalReport",
        "node_type": "component",
        "depth": 2,
        "via": "InvoiceSync",
        "owner": "Adan"
      }
    ]
  },
  "blast_radius": {
    "repos_affected": 2,
    "direct_dependents": 2,
    "transitive_dependents": 1,
    "total_call_sites": 4,
    "risk_level": "HIGH"
  }
}
```

#### 6.3 Duplicate Detection

```
GET /api/v1/visibility/duplicates
  ?org=kurigage
  &min_similarity=0.7
  &node_types=component,module

Response:
{
  "org": "kurigage",
  "clusters": [
    {
      "label": "Authentication Token Management",
      "similarity": 0.82,
      "members": [
        {"repo": "contabilidad", "node_id": "TokenManager", "content": "Manages JWT token refresh..."},
        {"repo": "erp", "node_id": "JwtHelper", "content": "JWT token helper with auto refresh..."}
      ],
      "recommendation": "consolidate"
    }
  ],
  "total_clusters": 3
}
```

#### 6.4 Contract Registration (Extension of Graph Sync)

Rather than a new endpoint, extend the existing `POST /api/v1/graph/sync` to
support cross-repo edge references:

```
POST /api/v1/graph/sync
{
  "project_id": "contabilidad",
  "nodes": [...],
  "edges": [
    {
      "source_node_id": "InvoiceSync",
      "target_node_id": "contract:POST-invoices",
      "target_repo_id": "apis",           ← NEW FIELD (optional)
      "edge_type": "depends_on",
      "properties": {"call_sites": 3}
    }
  ]
}
```

The `target_repo_id` field on `EdgeInput` enables cross-repo edge resolution.
When present, the server resolves the target node in the specified repo instead
of the current repo. This is the minimal change needed to enable cross-repo
edges.

### How New Endpoints Differ From GET /graph/query

| Dimension | GET /graph/query (existing) | New visibility endpoints |
|-----------|---------------------------|------------------------|
| **Scope** | Single org, all repos | Cross-repo awareness |
| **Query type** | Keyword search (text) | Structural queries (graph traversal) |
| **Result type** | Flat list of nodes | Dependency tree, matrix, clusters |
| **Algorithm** | PostgreSQL full-text search | BFS traversal, similarity scoring |
| **Use case** | "Find nodes matching X" | "Who depends on X?", "What's similar to X?" |

---

## 7. Competitive Landscape

### Feature Comparison

| Tool | Cross-Repo Deps | Impact Analysis | Duplicate Detection | AI-Integrated | Multi-Stack | Graph-Based |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| **Backstage** | Partial (catalog-info.yaml) | No | No | No | Yes | Partial |
| **Sourcegraph** | Yes (SCIP indexing) | Yes (Find References) | Partial (code search) | Yes (Cody) | Yes | No (index-based) |
| **GitHub Dependency Graph** | Partial (package deps only) | Dependabot alerts | No | No | Partial | Yes |
| **Nx Cloud Workspace Graph** | Yes (import analysis) | Yes (affected commands) | No | No | JS/TS focused | Yes |
| **Turborepo** | Monorepo only | Yes (task graph) | No | No | JS/TS focused | Yes |
| **Bazel** | Monorepo only | Yes (query language) | No | No | Yes | Yes |
| **Dependabot/Renovate** | Package deps only | Security alerts | No | No | Yes | No |
| **RaiSE (proposed)** | Yes (contract-based) | Yes (BFS + blast radius) | Yes (similarity) | Yes (skill integration) | Yes | Yes |

### Detailed Comparison

#### Backstage (Spotify)

Backstage provides a service catalog with a dependency graph via the
`catalog-graph` plugin. Each entity has a `catalog-info.yaml` declaring
relationships (`dependsOn`, `consumesApi`, `providesApi`).

**Strengths:** Strong entity model, wide adoption, mature plugin ecosystem.

**Limitations compared to RaiSE:**
- Catalog-only: knows services exist, not internal structure (modules, components)
- No impact analysis: you see the graph, but it doesn't tell you blast radius
- No AI integration: developers must manually check the catalog
- No duplicate detection
- Observation only: shows dependencies, doesn't prevent breaking changes

**RaiSE differentiator:** RaiSE knows the internal structure of each repo
(from discovery scan) AND the cross-repo contracts. It can tell you not just
"repo A depends on repo B" but "InvoiceSync.php on line 42 calls POST /invoices
with 3 call sites, and FiscalReport depends on InvoiceSync transitively."

#### Sourcegraph

Sourcegraph provides cross-repository code navigation using SCIP (Source Code
Intelligence Protocol). You can click on a symbol and jump to its definition
in another repository.

**Strengths:** Precise code intelligence, cross-repo navigation, powerful
search.

**Limitations compared to RaiSE:**
- Code-level only: no architectural concepts (modules, layers, bounded contexts)
- No design-time integration: you must go to Sourcegraph to look
- No governance awareness: finds references but doesn't evaluate impact
- Expensive: enterprise pricing for cross-repo features
- Symbol-level: works great for function calls, less useful for REST API
  consumption (string URLs are hard to index)

**RaiSE differentiator:** RaiSE operates at the architectural level, not just
the code level. It integrates into the development workflow (skills surface
impact during design), and it works for any dependency type (REST APIs, message
queues, shared schemas, not just code imports).

#### Nx Cloud Workspace Graph

Nx Cloud recently added Workspace Graph that visualizes dependencies across
multiple repositories, even non-Nx repos. It analyzes imports to draw
connections.

**Strengths:** Excellent visualization, automatic import analysis, integrated
with build system.

**Limitations compared to RaiSE:**
- JavaScript/TypeScript focused (other languages are second-class)
- Build-system centric (optimized for task scheduling, not architecture)
- No AI integration
- No governance or blast radius calculation
- Monorepo-adjacent: designed to make multi-repo feel like monorepo

**RaiSE differentiator:** Stack-agnostic (PHP, .NET, Python, etc.), AI-
integrated, architecture-aware (knows about modules, layers, bounded contexts,
not just import paths).

#### GitHub Dependency Graph

GitHub's built-in dependency graph analyzes package manifests (package.json,
Gemfile, requirements.txt, etc.) to show dependencies.

**Strengths:** Built into GitHub, no setup required, powers Dependabot.

**Limitations compared to RaiSE:**
- Package-level only: knows "repo A uses library X" but not internal structure
- No cross-repo awareness for internal dependencies (only public packages)
- No architectural understanding
- No impact analysis for API changes
- Security-focused (vulnerability alerts), not architecture-focused

**RaiSE differentiator:** Internal dependency tracking (not just public
packages), architectural awareness, design-time integration.

### RaiSE's Unique Position

```
                    Code-Level ←──────────────→ Architecture-Level
                         │                           │
    Sourcegraph ─────────┤                           │
                         │                           │
    Nx Graph ────────────┤                           │
                         │                           │
    GitHub Dep Graph ────┤                           │
                         │                           │
                         │            Backstage ─────┤
                         │                           │
                         │              RaiSE ───────┤ ← Graph-based +
                         │                           │   AI-integrated +
                         │                           │   Multi-stack
    ─────────────────────┴───────────────────────────┘
    Observation Only          →          Actionable (design-time)
```

No existing tool combines:
1. **Architecture-level** graph (modules, layers, bounded contexts)
2. **Code-level** component tracking (discovery scan)
3. **Cross-repo** dependency visibility (contract-based)
4. **AI-integrated** workflow (skills surface impact during design)
5. **Multi-stack** support (PHP, .NET, Python, etc.)

This is RaiSE's moat for Layer 1.

---

## 8. Implementation Priority

### Build Order

Each item depends on the ones above it:

| Priority | Capability | Depends On | Effort | Deliverable |
|----------|-----------|------------|--------|-------------|
| **P0** | Cross-repo edge support in sync | Existing graph sync | **S** | `EdgeInput.target_repo_id` + cross-repo resolution in `resolve_node_ids()` |
| **P1** | Contract node convention | P0 | **XS** | Documentation + `.raise/contracts.yaml` schema |
| **P2** | `GET /visibility/dependencies` | P0 | **S** | Cross-repo dependency query with matrix |
| **P3** | `GET /visibility/impact` | P0, P2 | **M** | BFS traversal with blast radius calculation |
| **P4** | Skill integration (story-design) | P3 | **M** | `/rai-story-design` queries impact during design |
| **P5** | `GET /visibility/duplicates` | P0 | **M** | Similarity detection across repos |
| **P6** | Contract version tracking | P1 | **S** | Version metadata on contract nodes, drift detection |

### Suggested Phasing

**Phase 1: Cross-Repo Edges (1 story, S)**
- P0 + P1: Enable cross-repo edges in graph sync
- Deliverable: `contabilidad` can declare it depends on `apis/POST-invoices`
- Validation: Rodo syncs all 3 graphs, cross-repo edges appear in DB

**Phase 2: Dependency Visibility (1 epic, 3-4 stories)**
- P2 + P3 + P4: Dependency query, impact analysis, skill integration
- Deliverable: Sofi gets blast radius during `/rai-story-design`
- Validation: Kurigage walkthrough of Scenario 1 (POST /invoices change)

**Phase 3: Intelligence (1-2 stories)**
- P5 + P6: Duplicate detection, contract versioning
- Deliverable: Rodo sees duplicates, version drift alerts
- Validation: Kurigage walkthrough of Scenario 4 (duplicate detection)

### Effort Summary

| Phase | Stories | Total Effort | Calendar Estimate |
|-------|---------|-------------|-------------------|
| Phase 1 | 1 | S | 1-2 days |
| Phase 2 | 3-4 | M+S+S+M | 1-2 weeks |
| Phase 3 | 1-2 | M+S | 3-5 days |
| **Total** | **5-7** | **~3 weeks** | |

### Dependency Diagram

```
P0: Cross-repo edge sync ──────┐
     │                          │
P1: Contract convention ──┐     │
     │                    │     │
P2: Dependencies endpoint ┤     │
     │                    │     │
P3: Impact analysis ──────┤     │
     │                    │     │
P4: Skill integration ────┘     │
                                │
P5: Duplicate detection ────────┘
     │
P6: Contract versioning ───────
```

---

## 9. Open Questions

### Q1: Should cross-repo edges be bidirectional or directed?

**Options:**
- A) **Directed** — consumer declares dependency on provider (one edge)
- B) **Bidirectional** — both consumer and provider declare the relationship
- C) **Directed with auto-reverse** — consumer declares, server creates reverse
  index for impact queries

**Leaning:** A (Directed). The consumer knows it depends on the provider. The
provider does not need to declare its consumers — the server can query reverse
edges for impact analysis. This follows the principle of minimal declaration.

### Q2: Where should contract declarations live?

**Options:**
- A) `.raise/contracts.yaml` in each repo
- B) A central governance repo with all contracts
- C) Auto-extracted from OpenAPI specs + manual overrides
- D) Declared in the graph sync payload (no separate file)

**Leaning:** A for initial, evolving to C. `.raise/contracts.yaml` is simple,
version-controlled, and fits the existing `.raise/` convention. Auto-extraction
from OpenAPI specs is a natural evolution for repos that have them.

### Q3: How do we handle stale cross-repo edges?

When a consumer declares `depends_on apis/POST-invoices` but the endpoint no
longer exists in the apis graph, what happens?

**Options:**
- A) **Hard fail** — sync rejects the edge if target doesn't exist
- B) **Soft warning** — sync creates the edge but marks it as "unresolved"
- C) **Periodic validation** — background job checks edge validity

**Leaning:** B (Soft warning). Hard fail would block syncs when repos are out
of sync. Soft warning allows the graph to be populated incrementally while
surfacing staleness in queries.

### Q4: Should impact analysis run server-side or client-side?

**Options:**
- A) **Server-side** — new endpoint does BFS traversal in PostgreSQL
- B) **Client-side** — client downloads subgraph, runs NetworkX BFS locally
- C) **Hybrid** — server provides edges, client does traversal

**Leaning:** A (Server-side). The server has the complete cross-repo graph.
The client only has its own repo's graph. Impact analysis must cross repo
boundaries, which requires server data. Keep the algorithm simple (BFS is
O(V+E), well under PostgreSQL's capacity for <100K nodes).

### Q5: How granular should duplicate detection be?

**Options:**
- A) Node name similarity only (fast, simple)
- B) Name + content similarity (TF-IDF on descriptions)
- C) Name + content + structural similarity (compare dependency patterns)

**Leaning:** Start with A, evolve to B. Name matching catches the obvious
duplicates (`TokenManager` vs `JwtHelper` with similar descriptions). Content
similarity adds precision. Structural similarity is powerful but complex —
save for Phase 3+ if simple approaches prove insufficient.

---

## 10. References

### Internal Research

| Document | Date | Relevance |
|----------|------|-----------|
| [shared-memory-architecture](../shared-memory-architecture/) | Feb 25 | Server architecture, multi-tenancy, PostgreSQL schema |
| [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) | Feb 26 | Layer 3 (Governance), builds on this Layer 1 |
| [governance-as-code-agents](../governance-as-code-agents/) | Jan 29 | Policy DSL, local enforcement patterns |
| [atlassian-forge-integration](../atlassian-forge-integration/) | Feb 24 | Forge app, Rovo agents, walking skeleton |
| [architecture-representation-for-ai](../architecture-representation-for-ai/) | earlier | How architectural knowledge is represented in the graph |

### Internal Code

| File | Relevance |
|------|-----------|
| `packages/rai-core/src/rai_core/graph/models.py` | 18 node types, 11 edge types |
| `packages/rai-server/alembic/versions/001_initial_schema.py` | DB schema (graph_nodes, graph_edges) |
| `packages/rai-server/src/rai_server/services/graph.py` | Graph sync + query service |
| `packages/rai-server/src/rai_server/db/queries.py` | SQL queries (upsert, search, prune) |
| `packages/rai-server/src/rai_server/schemas/graph.py` | API request/response models |

### External Tools and Concepts

| Tool/Concept | URL | Relevance |
|-------------|-----|-----------|
| Backstage catalog-graph | [backstage.io/docs](https://backstage.io/docs/features/software-catalog/creating-the-catalog-graph/) | Service catalog dependency graph |
| Sourcegraph cross-repo nav | [sourcegraph.com/blog](https://sourcegraph.com/blog/cross-repository-code-navigation) | SCIP-based cross-repo code intelligence |
| GitHub Dependency Graph | [docs.github.com](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-the-dependency-graph) | Package-level dependency tracking |
| Nx Cloud Workspace Graph | [nx.dev/blog](https://nx.dev/blog/nx-cloud-workspace-graph) | Multi-repo dependency visualization |
| Port.io Dependency Graph | [port.io/blog](https://www.port.io/blog/announcing-the-software-catalog-dependency-graph) | Catalog dependency visualization |

### Algorithms

| Algorithm | Use | Reference |
|-----------|-----|-----------|
| BFS (Breadth-First Search) | Impact analysis traversal | Standard graph algorithm |
| TF-IDF | Content similarity for duplicate detection | sklearn / simple implementation |
| Fuzzy string matching | Name similarity for duplicate detection | fuzzywuzzy / rapidfuzz |
| Personalized PageRank | Relevance ranking for query results | NetworkX `pagerank` built-in |

---

*Research by: Emilio + Claude Opus 4.6 | Session: SES-294 | Date: 2026-02-26*
*Status: Exploration complete — ready for epic planning*
