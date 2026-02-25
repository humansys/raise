# Epic RAISE-275: Shared Memory Backend — Scope

> **Status:** IN PROGRESS
> **Branch:** `epic/e275/shared-memory-backend`
> **Created:** 2026-02-25
> **Demo deadline:** 2026-03-04 (Coppel)

## Objective

Deliver a server-side knowledge graph backend that enables cross-repo pattern sharing
and governance validation — with OpenAPI spec as first deliverable to unblock Fernando's
Forge app (RAISE-274).

**Value:** Unlocks team intelligence (shared patterns, cross-repo queries), differentiates
Pro tier, and provides the API contract Fernando needs for RAISE-274.

## Stories (7 stories estimated)

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S275.1 | Extract rai-core package | S | Pending | Move 6 files (models, graph, query, protocols, backends) to rai_core. Re-exports for backward compat. ~30 import updates. |
| S275.2 | PostgreSQL schema + Alembic | S | Pending | 4 tables (orgs, api_keys, graph_nodes, graph_edges). Docker Compose with PG. Alembic initial migration. |
| S275.3 | FastAPI server bootstrap | M | Pending | App skeleton, config (env vars), auth middleware (API key → OrgContext), health endpoint. Dockerfile.server. |
| S275.4 | Graph CRUD endpoints | M | Pending | 6 endpoints: single + batch for nodes and edges, get node by id. SQLAlchemy async queries. |
| S275.5 | Query + Subgraph endpoints | S | Pending | 2 endpoints: keyword query with scope/type filtering, BFS subgraph extraction. OpenAPI spec auto-generated. |
| S275.6 | ApiGraphBackend + DualWrite | M | Pending | `ApiGraphBackend` (httpx client), `DualWriteBackend` (local + remote). `get_active_backend()` selection via env vars. |
| S275.7 | Dogfood + offline fallback | S | Pending | Test with raise-commons real graph. pending_sync marker for offline writes. Sync-on-reconnect. |

**Total:** 7 stories (2S + 3M + 2S = estimated M appetite)

## Scope

**In scope (MUST):**
- `rai-core` package extraction (shared models, protocols, backends)
- PostgreSQL with nodes/edges + JSONB, Alembic migrations
- FastAPI server with 8 REST endpoints
- API key authentication per org
- `DualWriteBackend` in CLI (local always + remote best-effort)
- Docker Compose (PG + server)
- OpenAPI spec (auto-generated from FastAPI, delivered to Fernando)

**In scope (SHOULD):**
- Offline fallback with pending_sync + sync-on-reconnect
- Scope filtering (PERSONAL stays local, PROJECT/ORG go to server)
- Pattern classification heuristics (personal vs shared)

**Out of scope:**
- Forge app → RAISE-274 (Fernando)
- Multi-tenant SaaS → future enterprise epic
- CRDTs / advanced merge → not needed (append-only + UUIDs)
- Embedding search → dead end at our scale (research validated)
- JWT / OAuth → upgrade path from API key when needed
- RLS → WHERE clause sufficient, RLS for enterprise
- GraphQL → overkill for 8 endpoints

## Done Criteria

**Per story:**
- [ ] Code with type annotations
- [ ] Tests passing (TDD: red-green-refactor)
- [ ] Quality checks pass (ruff, pyright)

**Epic complete:**
- [ ] All stories complete (S275.1–S275.7)
- [ ] `POST /api/v1/graph/nodes/batch` persists nodes, queryable via `GET /api/v1/graph/query`
- [ ] Two developers share patterns across two repos via the API
- [ ] CLI dual-write works (local + remote) with env var activation
- [ ] Personal data (sessions, telemetry) never leaves local filesystem
- [ ] Fernando can build Forge actions against auto-generated OpenAPI spec
- [ ] `docker compose up` provides working dev environment
- [ ] Epic retrospective done
- [ ] Merged to `dev`

## Dependencies

```
S275.1 (rai-core extraction)
  ↓
S275.2 (PG schema + Docker)
  ↓
S275.3 (FastAPI bootstrap + auth)
  ↓
S275.4 (CRUD endpoints) ──┐
  ↓                        │ S275.5 can start after S275.3
S275.5 (query + subgraph) ◄┘
  ↓
S275.6 (ApiGraphBackend + DualWrite) — needs S275.1 (rai-core) + S275.4/5 (endpoints)
  ↓
S275.7 (dogfood + offline)
```

**External:** Fernando needs OpenAPI spec from S275.5 to start Forge actions.

**Critical path:** S275.1 → S275.2 → S275.3 → S275.4 → S275.5 → deliver spec to Fernando.

## Architecture

| Decision | Summary |
|----------|---------|
| Repo structure | `rai-core` + `rai-server` in monorepo (uv workspaces) |
| Auth | API key per org (`rsk_` prefix), hash in DB |
| DB | PostgreSQL 16 + 2 tables (nodes/edges) + JSONB + GIN indexes |
| API | 8 REST endpoints, FastAPI, SQLAlchemy 2.0 async |
| CLI integration | `DualWriteBackend` via `KnowledgeGraphBackend` protocol |
| Dev env | Docker Compose (PG + server) |
| Portability | 12-factor (env vars), Docker image, no cloud-specific services |

> Problem Brief: `work/research/shared-memory-architecture/problem-brief.md`
> Research: `work/research/shared-memory-architecture/`

## Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| Timeline too tight for 7 stories in ~7 days | M/H | Critical path delivers OpenAPI spec by S275.5 (~day 4). Fernando unblocked even if S275.6-7 slip. |
| rai-core extraction breaks existing tests | L/M | Re-export layer ensures backward compat. Run full test suite after extraction. |
| Docker Compose differences across dev machines | L/L | Standard PG image, pinned versions, documented env vars. |

## Parking Lot

- RLS for multi-tenant isolation → enterprise epic
- JWT/OAuth auth upgrade → when user management needed
- Pattern promotion workflow (PERSONAL → PROJECT → ORG) → separate story post-epic
- Graph algorithms (PPR, spreading activation) → phase 2 after backend stable
- pgAdmin in Docker Compose → nice-to-have, add if debugging needed
