# Evidence Catalog: Shared Memory Architecture

**Date:** 2026-02-25 | **Total sources:** 45+ | **Depth:** Standard

---

## Storage Backend (Research 1)

| ID | Source | Type | Level | Key Finding |
|----|--------|------|-------|-------------|
| E-S01 | psqlgraph (NCI-GDC) | Primary | High | Production PG graph lib — nodes/edges tables + JSONB, SQLAlchemy |
| E-S02 | Linear engineering blog | Primary | High | Linear uses PostgreSQL (Cloud SQL) for complex issue relationships |
| E-S03 | "You don't need a graph database" (Qvarfordt) | Secondary | High | Sub-100K nodes: PG recursive CTEs sufficient |
| E-S04 | Notion data model (HN discussion) | Secondary | Medium | Block-based model on PostgreSQL, each row is JSON |
| E-S05 | Apache AGE FAQ | Primary | Medium | pg_upgrade not supported, complex model |
| E-S06 | Neo4j Community limitations | Primary | High | No RBAC, no clustering, 4 CPU cap |
| E-S07 | SurrealDB 3.0 GA | Primary | Medium-Low | Just shipped Feb 2026, thin production track record |
| E-S08 | NetworkDisk (INRIA) | Primary | Medium | NetworkX-compatible SQLite backend, 10x perf penalty |
| E-S09 | Alibaba PG graph search | Primary | High | PostgreSQL graph search at 10B scale with ms response |
| E-S10 | PostgreSQL 18 release notes | Primary | High | Async I/O, faster JSON operators |
| E-S11 | Multi-tenant KM with FastAPI | Secondary | Medium | FastAPI + PG multi-tenant pattern validated |

## Multi-Repo Shared Graph (Research 2)

| ID | Source | Type | Level | Key Finding |
|----|--------|------|-------|-------------|
| E-M01 | Backstage (Spotify) | Primary | Very High | YAML-in-repo, central catalog harvests, entity graph with relationships |
| E-M02 | Nx monorepo docs | Primary | High | Project graph derived from code analysis, generators encode conventions |
| E-M03 | Turborepo remote cache | Primary | High | Content-addressable cache, teamId isolation, self-hostable |
| E-M04 | Graphiti (Zep) group_id | Primary | Very High | group_id on ALL nodes/edges for tenant isolation, single DB |
| E-M05 | Zep paper (arXiv 2501.13956) | Primary | High | Temporal knowledge graph architecture for agent memory |
| E-M06 | Memgraph multi-tenancy | Primary | High | <100 tenants: row-level isolation sufficient |
| E-M07 | Dendron multi-vault | Primary | Medium | Private/shared vault separation, Pods for import/export |
| E-M08 | Obsidian shared vaults | Primary | Medium | All-or-nothing sharing — cautionary example |
| E-M09 | Apollo Federation | Primary | High | Supergraph from subgraphs — overkill at <20 repos |
| E-M10 | SPARQL Federation (FedX) | Primary | Medium | Graph federation solved at protocol level but RDF too heavy |
| E-M11 | ADR cross-repo patterns | Secondary | Medium | Each repo owns ADRs, publication (not sync) as sharing mechanism |
| E-M12 | GitLab pricing/tiers | Secondary | High | Tier by buyer persona, not feature complexity |
| E-M13 | Cal.com open-core model | Primary | High | Self-hosted free, /ee directory for commercial code |
| E-M14 | HITL classification patterns | Secondary | Medium | AI handles 70% routine, humans curate edge cases |
| E-M15 | Multi-tenant DB patterns (Bytebase) | Secondary | High | Three classic models: shared schema, separate schema, separate DB |

## Graph Search Algorithms (Research 3)

| ID | Source | Type | Level | Key Finding |
|----|--------|------|-------|-------------|
| E-A01 | SA-RAG (arXiv 2512.15922) | Primary | Medium-High | Spreading activation: 25-39% improvement over naive RAG, deterministic |
| E-A02 | Microsoft GraphRAG | Primary | High | Leiden community detection + map-reduce, production system |
| E-A03 | DRIFT Search (MS Research) | Secondary | Medium | "Start broad (community), narrow (local)" insight |
| E-A04 | PPR Survey (arXiv 2403.05198) | Primary | High | Proven at massive scale, trivial to implement on NetworkX |
| E-A05 | PPR on KGs (EDBT 2020) | Primary | High | Particle filtering for 2-100x speedup on KGs |
| E-A06 | Neural-Symbolic KG Survey (arXiv 2412.10390) | Primary | High | Symbolic for deterministic + neural for fuzzy = sweet spot |
| E-A07 | Embeddings + KGs (TDS) | Secondary | Medium | Pure embeddings fail at transitivity and chain-of-reasoning |
| E-A08 | Change impact analysis (Lehnert) | Primary | High | Typed reachability, forward/backward slicing, O(V+E) |
| E-A09 | Network-based change propagation (PMC) | Primary | High | Software change impact via graph reachability |
| E-A10 | InfraNodus PKM graphs | Tertiary | Low-Medium | Betweenness centrality for "structural gap" detection |
| E-A11 | NetworkX Leiden docs | Primary | High | Available but requires leidenalg backend |
| E-A12 | Enterprise KG anti-patterns (Semantic Arts) | Tertiary | Medium | #1 anti-pattern: KG as separate silo, not embedded in workflow |
| E-A13 | Graph-RAG Survey (ACM TOIS) | Primary | High | Comprehensive GraphRAG landscape taxonomy |
| E-A14 | SpreadPy (arXiv 2507.09628) | Primary | Medium | Reference Python implementation of spreading activation |

---

## Triangulation Summary

### Claims with 3+ independent confirmations:
- **PostgreSQL sufficient for <100K node graphs**: E-S01, E-S02, E-S03, E-S04, E-S09
- **Row-level scope isolation (group_id) is correct pattern**: E-M04, E-M05, E-M06, E-M15
- **PPR is highest-value next algorithm**: E-A04, E-A05, E-A06
- **Pure embeddings are dead end at our scale**: E-A06, E-A07, E-A12
- **NetworkX stays as in-memory engine**: E-S01, E-S08, E-A04

### Contrary evidence documented:
- Apollo Federation suggests federation protocol needed at >50 subgraphs (E-M09) — not our scale
- SA-RAG promising but only one paper with limited evaluation (E-A01) — investigate, don't commit
- SurrealDB multi-model appealing but too new (E-S07) — revisit in 2-3 years
