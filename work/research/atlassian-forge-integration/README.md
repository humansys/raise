# Research: Atlassian Forge Integration for Governance Copilot

**RAISE-273** | 2026-02-24 | **Updated: 2026-02-26 (post-E275)**

## Question
Can we build a governance copilot on Atlassian Forge that uses RaiSE's
neuro-symbolic knowledge graph for deterministic governance, with Confluence
as content store and Jira as process orchestrator?

## TL;DR
**YES.** Three-layer architecture:

1. **Confluence** = Content Store (documents, skills-as-pages, standards)
2. **RaiSE Backend** = Knowledge Layer (neuro-symbolic graph, deterministic)
3. **Forge App** = UI Layer (Rovo Agents — Rai Governance + Rai Dev)

Skills are Confluence pages — adding a governance process = creating a page.
No code, no deploy. The knowledge graph closes the governance → dev loop
deterministically. Teamwork Graph can't do this.

---

## Post-E275 Update (2026-02-26)

**Epic RAISE-275 (Shared Memory Backend) is complete and merged to dev.**
The backend that this research designed now exists. This section documents
what changed and what remains for RAISE-274 (Forge App).

### Backend API — What Exists (rai-server)

| Endpoint | Method | What it does | Schema |
|----------|--------|-------------|--------|
| `/health` | GET | Server status + DB check | `{status, version, db_ok}` |
| `/api/v1/graph/sync` | POST | Idempotent full graph upsert (nodes + edges) | `{project_id, nodes: [{node_id, node_type, scope, content, source_file, properties}], edges: [{source_node_id, target_node_id, edge_type, weight, properties}]}` |
| `/api/v1/graph/query` | GET | GIN full-text search | `?q=...&limit=N` → `{results: [{node_id, node_type, scope, content, source_file, properties, rank}], total, query}` |
| `/api/v1/agent/events` | POST | Store agent telemetry event | `{agent_id, event_type, payload}` |
| `/api/v1/agent/events` | GET | List agent events | `?agent_id=...&limit=N` |
| `/api/v1/memory/patterns` | POST | Store shared pattern | `{content, context, pattern_type, source}` |
| `/api/v1/memory/patterns` | GET | List shared patterns | `?limit=N` |

**Auth:** API key per org (`Authorization: Bearer rsk_...`), hash stored in DB.
**Infrastructure:** Docker Compose (PG 16 + FastAPI server), Alembic async migrations.
**Validated:** E2E with 1589 nodes + 33k edges from real raise-commons graph.

### Walking Skeleton Endpoints — Mapping to Reality

| WS Design (Feb 24) | E275 Reality (Feb 26) | Status |
|---|---|---|
| `POST /graph/index` (from Confluence) | `POST /graph/sync` (from CLI) | **Available** — Forge action pre-parses Confluence content into nodes/edges, calls sync |
| `GET /graph/query` | `GET /graph/query` | **Available** — keyword search with GIN. WS wanted type/scope filters; current API has `q` + `limit` only. Sufficient for POC. |
| `POST /governance/validate` | Not implemented | **Deferred** — parking lot. POC validates via LLM + graph query, not dedicated endpoint. |
| `GET /dev/constraints` | Not implemented | **Deferred** — parking lot. Achievable via `graph/query` with type filtering. |
| `GET /graph/trace` | Not implemented | **Deferred** — parking lot. Post-POC. |
| `GET /graph/impact` | Not implemented | **Deferred** — parking lot. Post-POC. |
| Agent telemetry | `POST/GET /agent/events` | **Available** — not in original WS, added after Rovo research. |
| Pattern sharing | `POST/GET /memory/patterns` | **Available** — not in original WS, added after Rovo research. |

### Impact on Walking Skeleton Phases

| WS Phase | Original Estimate | Post-E275 Status |
|----------|-------------------|------------------|
| Phase 0: Setup | 1-2 days | **Unchanged** — Confluence space, skill pages, Jira automation still needed |
| Phase 1: Forge Actions (Confluence + Jira) | 2-3 days | **Unchanged** — Forge app code doesn't exist yet |
| Phase 2: RaiSE Backend | 3-4 days | **DONE** — E275 delivered this. Fernando connects Forge actions to existing endpoints. |
| Phase 3: E2E Cycle | 2-3 days | **Reduced** — backend exists, only Forge↔Backend integration needed |
| Phase 4: Rai Dev Agent | 1-2 days | **Unchanged** — prompt + dev-constraints via graph/query workaround |
| Phase 5: Second Doc Type | 1 day | **Unchanged** — zero-code test |
| Phase 6: CI/CD | 1-2 days | **Can defer** — post-demo |

### Key Pivots from E275

1. **Skills = Confluence pages, not API endpoints.** Rovo reads them natively. Server provides graph context only.
2. **Templates = Confluence templates.** No need to serve via API.
3. **Subgraph-on-demand architecture.** Server loads subgraphs from PG into rai-core Graph objects for domain logic.
4. **Three-package monorepo:** rai-core (shared domain) + rai-cli (community) + rai-server (pro).
5. **DualWriteBackend in CLI** — local always, remote best-effort. Offline fallback with `pending_sync.json`.

### OpenAPI Spec

Auto-generated from FastAPI. Fernando can access at `http://localhost:8000/docs` with `docker compose up`.
Schemas in `packages/rai-server/src/rai_server/schemas/`.

---

## Architecture

```
Confluence (content) → RaiSE Backend (knowledge, deterministic)
                              ↕
                    Rai Governance + Rai Dev (Rovo Agents)
```

## Key Decisions
1. Three layers, three responsibilities (UI / Content / Knowledge)
2. One contextual agent that executes skills from Confluence pages
3. Skills as Confluence pages (governance team edits, zero code)
4. Document state in Confluence (version history, properties, comments)
5. Knowledge state in RaiSE graph (relations, traceability, validation)
6. Deterministic validation via graph (not RAG, not probabilistic)
7. Two agents: Rai Governance + Rai Dev (shared actions)
8. Jira as orchestrator (Automation creates structure, Rai operates within)
9. Backend is the core differentiator (not an add-on)

## Files
- [Walking Skeleton Design](walking-skeleton-design.md) — full architecture, manifest, code, prompts, implementation plan (pre-E275 — see Post-E275 Update above for current status)
- [Viability Report](atlassian-forge-integration-report.md) — initial research, Forge capabilities
- [Evidence Catalog](sources/evidence-catalog.md) — 24 sources, triangulated claims

## FREE vs PRO
- **FREE:** local graph, local skills, one dev, one repo
- **PRO:** centralized graph, Confluence skills, governance→dev loop, deterministic, multi-team
