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

| ID | JIRA | Story | Size | Status | Description |
|----|------|-------|:----:|:------:|-------------|
| S275.1 | [RAISE-276](https://humansys.atlassian.net/browse/RAISE-276) | Extract rai-core package | S | Done ✓ | Created `rai-core` as uv workspace package. Moved graph domain (6 files), renamed 6 classes (dropped "Unified" prefix, RAISE-145). ~50 import updates. No backward compat shims — clean cut. Quality reviewed, dead aliases removed. TN-003 published. |
| S275.2 | [RAISE-277](https://humansys.atlassian.net/browse/RAISE-277) | PostgreSQL schema + Alembic | S | Done ✓ | `rai-server` uv workspace package. 4 SA 2.0 models (Organization, ApiKey, GraphNodeRow, GraphEdgeRow). Alembic async migration. Docker Compose (PG 16 + server placeholder). 24 tests. Quality reviewed — server_default consistency fixed. 1.15x velocity. |
| S275.3 | [RAISE-278](https://humansys.atlassian.net/browse/RAISE-278) | FastAPI server bootstrap | M | Done ✓ | App factory, pydantic-settings config, API key auth (OrgContext), health endpoint, Dockerfile, Docker Compose. Epic design revised: domain-level API + subgraph-on-demand (4 research studies, 47 sources). QR: 6 findings fixed. 18 tests. 1.5x velocity. |
| S275.4 | [RAISE-279](https://humansys.atlassian.net/browse/RAISE-279) | Graph sync + query endpoints | M | Pending | Domain-level endpoints: `POST /graph/sync` (full graph upsert), `GET /graph/query` (keyword search). Internal CRUD service layer. OpenAPI spec auto-generated. |
| S275.5 | [RAISE-280](https://humansys.atlassian.net/browse/RAISE-280) | Trace, impact + dev constraints | S | Pending | Domain-level endpoints: `GET /graph/trace`, `GET /graph/impact`, `GET /dev/constraints`. High-value operations for Rovo agents and Forge. |
| S275.6 | [RAISE-281](https://humansys.atlassian.net/browse/RAISE-281) | ApiGraphBackend + DualWrite | M | Pending | `ApiGraphBackend` (httpx client), `DualWriteBackend` (local + remote). `get_active_backend()` selection via env vars. |
| S275.7 | [RAISE-282](https://humansys.atlassian.net/browse/RAISE-282) | Dogfood + offline fallback | S | Pending | Test with raise-commons real graph. pending_sync marker for offline writes. Sync-on-reconnect. |

**Total:** 7 stories (2S + 3M + 2S = estimated M appetite)

## Scope

**In scope (MUST):**
- `rai-core` package extraction (shared RaiSE domain — graph implemented, workflow/governance placeholders)
- Three-package monorepo: rai-core + rai-cli (COMMUNITY, lockstep PyPI), rai-server (PRO, separate)
- Drop "Unified" prefix during extraction (RAISE-145, absorbed into S275.1)
- PostgreSQL with nodes/edges + JSONB, Alembic migrations
- FastAPI server with domain-level endpoints (sync, query, trace, impact, constraints)
- Internal CRUD service layer (not exposed publicly — server holds intelligence)
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
- GraphQL → overkill for domain-level endpoints

## Done Criteria

**Per story:**
- [ ] Code with type annotations
- [ ] Tests passing (TDD: red-green-refactor)
- [ ] Quality checks pass (ruff, pyright)

**Epic complete:**
- [ ] All stories complete (S275.1–S275.7)
- [ ] `POST /api/v1/graph/sync` persists full graph, queryable via `GET /api/v1/graph/query`
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
S275.4 (graph sync + query) — internal CRUD layer + sync/query endpoints
  ↓
S275.5 (trace, impact, constraints) — domain intelligence endpoints
  ↓
S275.6 (ApiGraphBackend + DualWrite) — needs S275.1 (rai-core) + S275.4 (sync endpoint)
  ↓
S275.7 (dogfood + offline)
```

**External:** Fernando needs OpenAPI spec from S275.4 to start Forge actions.

**Critical path:** S275.1 → S275.2 → S275.3 → S275.4 → deliver spec to Fernando → S275.5 → S275.6 → S275.7.

## Architecture

| Decision | Summary |
|----------|---------|
| Repo structure | 3 packages in monorepo (uv workspaces): rai-core (domain) + rai-cli (community) + rai-server (PRO) |
| rai-core scope | Shared RaiSE domain: `graph/` (E275), `workflow/` (placeholder), `governance/` (placeholder) |
| Version strategy | rai-core + rai-cli lockstep (exact pin), rai-server independent (range pin) |
| Extraction boundary | Only graph domain to core: `KnowledgeGraphBackend` + `BackendHealth`. Governance/PM protocols stay in CLI |
| Rename | Drop "Unified" prefix (RAISE-145): `Graph`, `QueryEngine`, `Query`, etc. Re-exports for compat |
| Auth | API key per org (`rsk_` prefix), hash in DB |
| DB | PostgreSQL 16 + 2 tables (nodes/edges) + JSONB + GIN indexes |
| API | Domain-level REST endpoints (sync, query, trace, impact, constraints). Internal CRUD service layer. FastAPI, SQLAlchemy 2.0 async. Aligned with RAISE-273 DA-9. |
| Server architecture | Subgraph-on-demand (Option B) — PG loads subgraphs → rai-core domain logic. Research-grounded (4 studies, 47 sources). |
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

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-02-25

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S275.1 — Extract rai-core | S | None | M1 | **Risk-first.** Create rai-core package, move graph domain (partial: only graph models/engine/query/scoring + KnowledgeGraphBackend + BackendHealth + FilesystemBackend). Drop "Unified" prefix (RAISE-145). Re-exports for compat. ~30 import updates. Must pass full test suite. |
| 2 | S275.2 — PG schema + Docker | S | S275.1 | M1 | **Walking skeleton base.** DB + Docker Compose = infrastructure foundation. rai-server package created here. |
| 3 | S275.3 — FastAPI bootstrap | M | S275.2 | M1 | **Skeleton complete.** Health endpoint + auth middleware + config. Proves the server runs, connects to DB, validates API keys. |
| 4a | S275.4 — Graph sync + query | M | S275.3 | M2 | **Core value.** Internal CRUD service layer + `POST /graph/sync` + `GET /graph/query`. After this, CLI can sync graphs and query them. OpenAPI spec deliverable to Fernando. |
| 4b | S275.5 — Trace, impact, constraints | S | S275.4 | M2 | **Domain intelligence.** `GET /graph/trace`, `GET /graph/impact`, `GET /dev/constraints`. High-value for Rovo agents. Depends on S275.4 service layer. |
| 5 | S275.6 — ApiGraphBackend | M | S275.1 + S275.4 + S275.5 | M3 | **CLI integration.** Needs rai-core (protocols) and working endpoints. DualWriteBackend connects CLI to server. |
| 6 | S275.7 — Dogfood + offline | S | S275.6 | M4 | **Validation.** Real graph data through the full pipeline. Offline fallback. Epic done criteria verified. |

### Milestones

| Milestone | Stories | Target | Success Criteria |
|-----------|---------|--------|------------------|
| **M1: Walking Skeleton** | S275.1, S275.2, S275.3 | Day 3 (~Feb 27) | `docker compose up` → server running, `/health` returns 200, API key validated, all existing tests pass. |
| **M2: API Complete** | +S275.4, S275.5 | Day 5 (~Mar 1) | `POST /graph/sync` persists graph, `GET /graph/query` returns results. Trace/impact/constraints work. **OpenAPI spec delivered to Fernando after S275.4.** |
| **M3: CLI Connected** | +S275.6 | Day 6 (~Mar 2) | CLI with `RAI_SERVER_URL` set → `rai graph build` persists to both local and server. |
| **M4: Epic Complete** | +S275.7 | Day 7 (~Mar 3) | Real raise-commons graph in shared server. Offline fallback works. Done criteria met. Retro done. |

### Parallel Work Streams

```
Time →  Day 1    Day 2    Day 3    Day 4    Day 5    Day 6    Day 7
        ──────   ──────   ──────   ──────   ──────   ──────   ──────
Main:   S275.1 → S275.2 → S275.3 → S275.4 → S275.5 → S275.6 → S275.7
                                      ↓
                               OpenAPI spec → Fernando
```

**Sequential:** S275.5 (trace/impact/constraints) depends on S275.4's service layer. No longer parallel.

**Fernando unblock:** After S275.4 (target Day 4 / Feb 28). He gets the OpenAPI spec with sync + query endpoints and can start Forge actions immediately.

### Progress Tracking

| Story | Size | Status | Actual | Velocity | Notes |
|-------|:----:|:------:|:------:|:--------:|-------|
| S275.1 — Extract rai-core | S | Done ✓ | ~3h | 1.3x | Quality review + TN-003 |
| S275.2 — PG schema + Docker | S | Done ✓ | ~1.1h | 1.15x | QR caught server_default bugs |
| S275.3 — FastAPI bootstrap | M | Done ✓ | ~1h impl, ~3h total | 1.5x | Epic design revised + 4 research studies. QR: 6 fixes. |
| S275.4 — Graph sync + query | M | Pending | — | — | Internal CRUD + domain endpoints |
| S275.5 — Trace, impact, constraints | S | Pending | — | — | Depends on S275.4 service layer |
| S275.6 — ApiGraphBackend | M | Pending | — | — | |
| S275.7 — Dogfood + offline | S | Pending | — | — | |

### Sequencing Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| S275.1 extraction takes longer than 1 day (hidden deps) | L/H | Gemba already mapped blast radius: 6 files, 0 circular deps, ~30 mechanical imports. Re-exports eliminate risk of breaking existing code. |
| S275.5 domain endpoints more complex than expected | M/M | Trace/impact require graph traversal logic. Can be simplified (BFS only) for E275, advanced algorithms in future epic. |
| Fernando needs spec before Mar 1 | M/H | Spec delivered after S275.4 (sync+query). Fernando unblocked earlier than before. |

## Parking Lot

- RLS for multi-tenant isolation → enterprise epic
- JWT/OAuth auth upgrade → when user management needed
- Pattern promotion workflow (PERSONAL → PROJECT → ORG) → separate story post-epic
- Graph algorithms (PPR, spreading activation) → phase 2 after backend stable
- pgAdmin in Docker Compose → nice-to-have, add if debugging needed
