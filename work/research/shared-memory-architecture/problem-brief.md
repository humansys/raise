# Problem Brief: Shared Memory Backend

**Date:** 2026-02-25 | **Author:** Emilio + Rai | **Session:** SES-281

---

## Problem Statement

**Hypothesis:** RaiSE's knowledge graph is currently per-developer and per-machine, which prevents teams from sharing learned patterns, architectural decisions, and governance knowledge across developers and repositories. This limits the value of the graph to individual productivity instead of team intelligence.

**Who feels it:**
- **HumanSys team (immediate):** Emilio and Fernando need shared knowledge between raise-commons and raise-atlassian for RAISE-274. 6+ active repos need coordinated governance.
- **Open-core users:** Technical users requesting repo-level shared knowledge that benefits all devs on a team.
- **RaiSE Pro customers (future):** Teams of 5-50 devs needing governance traceability, impact analysis, and shared patterns across repos.

**Cost of inaction:**
- RAISE-274 demo (March 4) requires a backend API — Forge app has no filesystem, can't use local graph
- HumanSys can't dogfood multi-repo governance on our own products
- No Pro tier differentiation — open-core stays feature-equivalent to local-only

---

## Context & Constraints

**What exists today:**
- NetworkX in-memory graph with 18 node types, 11 edge types
- Pure Python query engine (keyword + BFS + Wilson scoring)
- `KnowledgeGraphBackend` protocol (ADR-036) — abstraction already designed
- 90% of core code is pure logic, reusable for server (see research report)
- Adapter protocols for PM, governance, docs targets

**Hard constraints:**
- March 4 deadline for Coppel demo — Fernando needs API contract to build Forge actions against
- 2-person team (Emilio backend, Fernando Forge)
- Must be production-quality architecture, not throwaway (dogfooding from day 1)
- Personal data (sessions, velocity, coaching) must NEVER leave the developer's machine

**Soft constraints:**
- PostgreSQL as storage (research recommends, HIGH confidence)
- FastAPI for API layer (existing Python ecosystem)
- NetworkX stays for in-memory scoring/traversal

---

## Scope

### In scope
- **Storage protocol extraction** — MemoryStore interface in raise-commons core
- **PostgresGraphBackend** — implements existing KnowledgeGraphBackend protocol
- **Four-scope model** — PERSONAL, PROJECT, ORG, GLOBAL with node-level isolation
- **API endpoints** — graph-index, graph-query, graph-trace, graph-impact, governance-validate, dev-constraints
- **Dual write** — CLI writes to API + local filesystem simultaneously
- **Offline fallback** — CLI works degraded when server unreachable, syncs on reconnect
- **Pattern classification** — personal vs shared heuristics, AI proposes, human validates
- **OpenAPI spec** — contract for Fernando's Forge actions
- **Dogfooding** — HumanSys uses it for raise-commons + raise-atlassian coordination

### NOT in scope
- Forge app (RAISE-274, Fernando's epic)
- Multi-tenant SaaS (single org for now)
- CRDTs or advanced merge strategies (last-write-wins with UUIDs sufficient)
- Embedding-based search (dead end at our scale per research)
- Production deployment infrastructure (local Docker for POC)
- Marketplace, billing, SSO

---

## Success Criteria

1. `POST /api/v1/graph/index` persists a node to PostgreSQL and it's queryable via `GET /api/v1/graph/query`
2. Two developers (Emilio, Fernando) share a knowledge graph across two repos
3. CLI writes patterns that appear in the shared graph within seconds
4. Personal data (sessions, telemetry) stays local — never hits the API
5. Fernando can build Forge actions against the OpenAPI spec using a mock server
6. Offline: CLI works without server, syncs when reconnected

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| March 4 deadline too tight for real backend | Medium | High | Deliver OpenAPI spec + mock first, real backend follows |
| Core refactor breaks existing CLI | Low | High | Storage protocol is additive, not replacing filesystem backend |
| PostgreSQL schema wrong for graph queries | Low | Medium | Research validated pattern at production scale (psqlgraph, Linear) |
| Offline sync creates data inconsistencies | Low | Low | Append-only + UUIDs eliminate conflicts; last-write-wins for mutations |

---

## Research Foundation

- **45+ sources** across 3 parallel research tracks
- Full report: `work/research/shared-memory-architecture/`
- Confluence: [Research: Shared Memory Architecture](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3078619137)

---

## Stakeholders

| Person | Role | Interest |
|--------|------|----------|
| Emilio | Backend developer, product owner | Builds it, dogfoods it |
| Fernando | Forge developer | Consumes API contract |
| Rodo (Coppel) | Architect, demo audience | Sees governance validation in action |
| Jorge (Coppel) | Business owner, demo audience | Sees governance → dev loop |

---

## Next Steps

1. Create epic in Jira
2. `/rai-epic-design` to break into stories
3. Deliver OpenAPI spec to Fernando (blocks his Forge work)
4. Implement PostgresGraphBackend
5. Stand up FastAPI server with core endpoints
