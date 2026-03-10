# Epic E275: Shared Memory Backend — Retrospective

## Summary

| Field | Value |
|-------|-------|
| Epic | RAISE-275: Shared Memory Backend |
| Branch | `epic/e275/shared-memory-backend` |
| Started | 2026-02-25 |
| Completed | 2026-02-26 |
| Stories | 7 (3S + 3M + 1S) |
| Commits | 91 |
| Tests | 2950 total (passing), ~300 new in epic |
| Demo deadline | 2026-03-04 (Coppel) — on track |

## Velocity

| Story | Size | Actual | Velocity | QR Findings |
|-------|:----:|--------|:--------:|:-----------:|
| S275.1 — Extract rai-core | S | ~3h | 1.3x | QR + TN-003 |
| S275.2 — PG schema + Docker | S | ~1.1h | 1.15x | 2 (server_default) |
| S275.3 — FastAPI bootstrap | M | ~3h total | 1.5x | 6 |
| S275.4 — Graph sync + query | M | ~90 min | 1.1x | 6 |
| S275.5 — Agent telemetry + memory | S | ~2h total | 2.7x impl | 4 |
| S275.6 — ApiGraphBackend + DualWrite | M | ~50 min | 1.2x | 5 |
| S275.7 — Dogfood + offline | S | ~55 min | 0.8x | 3 QR + 4 E2E |

**Average velocity:** ~1.3x (faster than estimated)
**Total QR findings:** 30 (all fixed before merge)

## Deliverables

1. **rai-core package** — shared domain (graph engine, backends protocol)
2. **rai-server package** — FastAPI + PostgreSQL + Alembic
   - `POST /api/v1/graph/sync` — idempotent upsert + edge replace + orphan prune
   - `GET /api/v1/graph/query` — GIN full-text search
   - `POST/GET /api/v1/agent/events` — telemetry
   - `POST/GET /api/v1/memory/patterns` — pattern sharing
   - API key auth (org-scoped)
3. **DualWriteBackend** — CLI writes local + remote best-effort
4. **Offline fallback** — `pending_sync.json` marker, cleared on reconnect
5. **Docker Compose** — PG 16 + server, one-command dev env
6. **E2E verified** — 1589 nodes + 33k edges synced from real raise-commons graph

## Architecture Decisions

| Decision | Outcome |
|----------|---------|
| 3-package monorepo (rai-core, rai-cli, rai-server) | Clean separation, uv workspaces |
| Subgraph-on-demand (not full graph in memory) | Research-validated, 4 studies |
| API key auth (not JWT) | Simple, sufficient for POC |
| DualWrite (not queue) | Simpler, local is source of truth |
| Three-layer architecture (routes → services → db) | Clean, testable |
| Rovo via Confluence (not API) | Skills = Confluence pages, our API = data only |

## Patterns Extracted

| ID | Pattern |
|----|---------|
| PAT-E-523 | Data mutation: declare missing-entity strategy explicitly |
| PAT-E-530 | Research-first for external integration (Rovo: 2 pivots saved) |
| PAT-E-531 | Endpoint minimalism: build only what POC needs |
| PAT-E-538 | getattr Gemba: verify attribute names against source class |
| PAT-E-539 | E2E integration gate for multi-component epics |

## What Went Well

- **Velocity sustained across 7 stories** — no story blocked, no major rework
- **QR consistently valuable** — caught real bugs in every story (30 total)
- **Research-grounded design** — Rovo research (10 sources) prevented building unnecessary endpoints
- **Walking skeleton approach** — Docker + server + DB working from S275.3, incremental delivery
- **Full skill cycle even for S stories** — discipline paid off

## What to Improve

- **E2E was missing from the plan** — S275.7 "Dogfood" was designed as a unit-testable feature, not an actual E2E validation. Found 4 cross-story integration bugs only when running real infra (PAT-E-539)
- **Auth header contract** — client (S275.6) and server (S275.3) used different header formats. Mock-based testing can't catch this. Integration checkpoint should be a milestone.
- **asyncpg param limit** — never encountered in tests (small data), only with real graph (33k edges). Batch INSERT was an obvious need that should have been anticipated.
- **Alembic config** — `alembic.ini` hardcodes `localhost`, doesn't work inside Docker. Should read from env var.

## Process Improvements Applied

1. **rai-story-design**: Added Integration gate (PAT-E-539) — multi-component stories must include real infra E2E in AC
2. **rai-epic-plan**: Added Integration checkpoint — multi-component epics must schedule E2E milestone before final story
3. Both skills synced to base + .claude + .agent

## Risks Review

| Risk (from scope) | Actual |
|-------------------|--------|
| Timeline too tight for 7 stories | Completed in 2 days, well ahead of Mar 4 deadline |
| rai-core extraction breaks tests | Clean extraction, no breakage |
| Docker differences across machines | Worked first time locally |
| Rovo can't follow complex skills | Skills = Confluence pages, no API needed (research pivot) |

## Parking Lot (carried forward)

- RLS for multi-tenant isolation → enterprise epic
- JWT/OAuth auth upgrade → when user management needed
- Pattern promotion workflow (PERSONAL → PROJECT → ORG) → separate story
- Alembic env.py should read DATABASE_URL from env var (not just alembic.ini)
- Duplicate node IDs in graph build (44 warnings) → graph builder cleanup
