---
epic_id: "RAISE-275"
title: "Shared Memory Backend"
status: "designed"
created: "2026-02-25"
designed: "2026-02-25"
---

# Epic Brief: Shared Memory Backend

## Hypothesis
For RaiSE developers working in teams who need shared governance knowledge across repos,
the Shared Memory Backend is a server-side graph store
that enables cross-repo pattern sharing, governance validation, and team intelligence.
Unlike the current local-only graph, our solution provides real-time shared knowledge
accessible from CLI, Forge apps, and any API client.

## Success Metrics
- **Leading:** OpenAPI spec delivered to Fernando, mock server functional (story 1-2)
- **Lagging:** Two developers share patterns across two repos via the API; Forge app queries real backend

## Appetite
M — 7 stories, ~7 calendar days to March 4 demo

## Architecture Decisions (resolved in design)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Repo structure | `rai-core` + `rai-server` in monorepo | Clean dependency graph; server never imports CLI deps. 6 files, 0 circular deps, 8-12h extraction. |
| 2 | Auth model | API key per org (`rsk_` prefix) | 2h implementation, stateless, sufficient for POC + first Pro customers. JWT upgrade path later. |
| 3 | DB schema | 2 tables (nodes + edges) + JSONB | Validated by psqlgraph (NCI), Linear, Notion. 4 tables total with orgs + api_keys. |
| 4 | API surface | 8 REST endpoints (CRUD + query + subgraph) | Minimal surface. Trace/impact done client-side with NetworkX on downloaded subgraph. |
| 5 | ORM | SQLAlchemy 2.0 async + asyncpg + Alembic | Standard Python stack. Declarative models, auto-migrations, async driver. |
| 6 | CLI integration | `ApiGraphBackend` + `DualWriteBackend` | Implements existing KnowledgeGraphBackend protocol. Activated by env vars. Filesystem fallback always. |
| 7 | Dev environment | Docker Compose (PG + server) | `docker compose up` → API running. Fernando: clone, compose up, done. |

## Scope Boundaries
### In (MUST)
- Extract `rai-core` package from `rai-cli` (6 files, shared models + protocols)
- OpenAPI spec + working server for Fernando (unblocks RAISE-274)
- PostgreSQL schema with nodes/edges + JSONB + Alembic migrations
- FastAPI server with 8 endpoints (health, CRUD nodes/edges, batch, query, subgraph)
- API key authentication per org
- `DualWriteBackend` in CLI (local + remote, best-effort)
- Docker Compose for local dev

### In (SHOULD)
- Offline fallback with pending_sync marker and sync-on-reconnect
- Pattern classification heuristics (personal vs shared)
- Four-scope filtering (PERSONAL stays local, PROJECT/ORG go to server)

### No-Gos
- Forge app development (RAISE-274, Fernando's scope)
- Multi-tenant SaaS infrastructure
- CRDTs or advanced merge (last-write-wins sufficient)
- Embedding-based search (dead end at our scale)
- Marketplace, billing, SSO
- GraphQL (overkill for 8 endpoints)
- JWT/OAuth (API key sufficient for POC)

### Rabbit Holes
- Over-engineering the sync protocol — append-only + UUIDs is enough
- Building a custom graph query language — reuse existing NetworkX traversal
- RLS at the DB level — WHERE clause filtering sufficient for now
- SQLModel — async support immature, quirks with JSONB
