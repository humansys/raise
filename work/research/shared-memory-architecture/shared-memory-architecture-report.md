# Shared Memory Architecture — Research Report

**Date:** 2026-02-25 | **Session:** SES-281 | **Depth:** Standard
**Researchers:** Emilio + Rai (3 parallel subagents)

---

## 1. Context

RaiSE needs shared memory for two converging needs:

- **RAISE-274 (Forge POC):** Emilio (backend) and Fernando (Forge app) need a shared knowledge graph across raise-commons and raise-atlassian
- **Open-core product:** Users requesting repo-level shared knowledge (patterns, ADRs, conventions) that benefits all devs on a team

Current state: per-developer knowledge graph stored locally in `.raise/rai/memory/`, NetworkX MultiDiGraph persisted as JSON. Pure Python query engine with keyword search + BFS + Wilson scoring.

---

## 2. Storage Backend

### Decision: PostgreSQL with nodes/edges tables + JSONB

**Confidence: HIGH (4/5 evidence items converge)**

Two core tables:
```
graph_nodes (id, org_id, repo_id, scope, node_type, content, properties JSONB, created)
graph_edges (id, org_id, repo_id, source_id, target_id, edge_type, weight, properties JSONB)
```

**Why PostgreSQL:**
- Linear, Notion, GitHub all use PostgreSQL for graph-like data at this scale
- Multi-tenancy via org_id/repo_id + Row-Level Security
- Recursive CTEs handle BFS traversal for <100K nodes
- JSONB + GIN indexes for flexible property queries
- Standard FastAPI + SQLAlchemy + asyncpg stack
- psqlgraph (NCI) validates the "NetworkX + PostgreSQL persistence" pattern in production

**NetworkX stays** as the in-memory query engine. DB is persistence + multi-tenant filtering. Load subgraph → compute (PPR, scoring, traversal) → persist mutations back.

**Discarded options:**
- Apache AGE: breaks pg_upgrade, no Python ORM, unnecessary at our scale
- Neo4j: JVM dependency, overkill, Community Edition lacks RBAC
- SurrealDB: GA 8 days ago, fails "boring technology" test
- SQLite: single-writer, doesn't solve multi-tenant

**Sources:** psqlgraph (NCI-GDC), Linear engineering blog, "You don't need a graph database" (Qvarfordt), PostgreSQL + FastAPI guides, Alibaba PG graph search at 10B scale

---

## 3. Multi-Repo Shared Graph

### Decision: Four scopes with node-level isolation

**Confidence: VERY HIGH (95%)**

| Scope | Storage | Sharing |
|-------|---------|---------|
| PERSONAL | Local filesystem only, gitignored | Never shared |
| PROJECT | API + local filesystem | Shared within repo team |
| ORG | API only | Shared across repos in org |
| GLOBAL | Local ~/.rai/ | Per-developer cross-repo prefs |

**Key patterns:**
- **Graphiti group_id pattern:** scope + repo_id on every node/edge, single DB, queries scoped by default
- **Data flows UP, never DOWN:** PERSONAL → PROJECT → ORG via promotion with HITL
- **Server is API (not harvester):** CLI and Forge write via POST, read via GET. No crawler.
- **Git is backup, not source of truth for shared:** Server is source of truth. Local filesystem is offline fallback.

### Pattern Promotion (HITL)

```
PERSONAL → PROJECT: dev proposes, dev validates (rai pattern promote)
PROJECT → ORG:     team proposes, architect validates (PR in governance repo)
```

**Classification heuristics (simple first):**
- Contains velocity/sessions/personal refs → NEVER shareable
- Type = architecture or process → candidate
- Reinforcement ≥ 2 → candidate for promotion

### Open-Core Tier Boundary

| Free | Pro | Enterprise |
|------|-----|------------|
| Local graph (personal + project) | Server-backed org graph | SSO + audit trails |
| Git-committed shared patterns | Cross-repo queries | Compliance |
| Pattern promotion personal→project | Automated sync | RBAC |
| | Pattern analytics | |
| | Team curation workflows | |

**Model:** Cal.com pattern — self-hosted free, collaboration features paid. Separate commercial code in `rai_pro/` package.

**Sources:** Backstage (Spotify), Graphiti (Zep), Dendron multi-vault, GitLab/Cal.com pricing, Apollo Federation (negative — overkill), multi-tenant DB patterns

---

## 4. Graph Search Algorithms

### Current foundation is correct
Keyword search + BFS + Wilson scoring — extend, don't replace.

### Phase 1: Quick wins (days)

| Algorithm | Use Case | Effort | Confidence |
|-----------|----------|--------|-----------|
| **Personalized PageRank** | "What's relevant to my current task?" | ~10 lines (NetworkX built-in) | HIGH |
| **Reachability slicing** | Impact analysis (all nodes on paths between A and B) | ~50 lines (2x BFS + intersect) | HIGH |
| **Edge-type weighting** | `governs` weighs more than `relates_to` | Modify existing BFS | HIGH |

### Phase 2: Spreading Activation (week)
Seeds from query context, propagation via typed edges with decay (c=0.3-0.5), threshold tau=0.4-0.6, 3-4 hop limit. SA-RAG shows 25-39% improvement. Cognitively grounded.

### Phase 3: Structural analysis (future)
- Leiden community detection for thematic clustering
- Betweenness centrality for gap detection

### Dead ends confirmed
- **Pure embeddings (TransE, DistMult):** No chain-of-reasoning, need training data we don't have
- **GNNs:** Overkill, black box, need labeled data
- **LLM-dependent traversal (DRIFT, GraphRAG global):** Latency + cost + non-determinism
- **Global PageRank (without personalization):** Important ≠ relevant to my task
- **KG embeddings at <100K nodes:** Overhead vastly exceeds benefit

**Sources:** SA-RAG (arXiv 2512.15922), Neural-Symbolic KG Survey (arXiv 2412.10390), PPR Survey (arXiv 2403.05198), Microsoft GraphRAG, change impact analysis literature

---

## 5. Write Path & Offline Sync

### Online (normal)
```
write → API + local filesystem (dual write)
read  → API (server has complete graph)
```

### Offline (degraded)
```
write → local filesystem only, marked "pending_sync"
read  → local filesystem only (incomplete, no cross-repo)
```

### Reconnect
```
push pending_sync → API (append-only, no conflicts via UUIDs)
pull → refresh local cache (optional)
```

No merge conflicts because:
- Patterns are append-only
- IDs are UUIDs or prefixed (PAT-{dev}-{N})
- Mutations use last-write-wins with timestamp (sufficient for 2-6 person teams)

CRDTs/merge strategies deferred to Enterprise tier.

---

## 6. Core Code Reusability (from codebase exploration)

**Directly reusable (90% of value):**
- Graph model: 18 typed nodes with auto-registry, edges, NetworkX (`context/models.py`, `context/graph.py`)
- Query engine: keyword search, concept lookup, scoring (`context/query.py`)
- Memory models: MemoryConcept, MemoryRelationship, scopes (`memory/models.py`)
- Telemetry signals: discriminated union of 6 event types (`telemetry/schemas.py`)
- Adapter protocols: KnowledgeGraphBackend, ProjectManagementAdapter (`adapters/protocols.py`)
- Session state: CurrentWork, EpicProgress (`schemas/session_state.py`)

**Needs abstraction:**
- `memory/writer.py` → extract MemoryStore protocol
- `graph/filesystem_backend.py` → implement PostgresGraphBackend (protocol already exists via ADR-036)
- `session/state.py` → extract SessionStore protocol

**Architecture for server:**
```
Core (shared):  models, graph logic, query engine, scoring
CLI:            commands → core functions → FilesystemBackend
Server:         FastAPI routes → core functions → PostgresBackend
```

Same functions, different transport and persistence.

---

## 7. Next Steps

1. Problem brief for Shared Memory Architecture epic
2. API contract design (OpenAPI spec) for Fernando
3. Storage protocol extraction in raise-commons core
4. PostgresGraphBackend implementation
5. FastAPI server scaffold with endpoints from walking skeleton

---

## 8. Open Questions (Parking Lot)

- Exact API authentication model (API key for POC, OAuth for Pro?)
- Where does the server live? (HumanSys infra, cloud, Forge remote?)
- Research skill adaptation to publish to Confluence
- Repo clutter in MRs (user feedback: non-code directories make reviews hard)
