---
epic_id: "RAISE-275"
title: "Shared Memory Backend"
status: "draft"
created: "2026-02-25"
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
M — 5-7 stories, ~7 calendar days to March 4 demo

## Scope Boundaries
### In (MUST)
- OpenAPI spec + mock server for Fernando (unblocks RAISE-274)
- PostgresGraphBackend implementing KnowledgeGraphBackend protocol
- FastAPI server with graph-index, graph-query endpoints
- Four-scope model (PERSONAL, PROJECT, ORG, GLOBAL)
- Node-level scope isolation (personal data never leaves local)
- Dual-write from CLI (API + local filesystem)

### In (SHOULD)
- Offline fallback with sync-on-reconnect
- Pattern classification heuristics (personal vs shared)
- Docker Compose for local dev (PostgreSQL + FastAPI)
- graph-trace and graph-impact endpoints

### No-Gos
- Forge app development (RAISE-274, Fernando's scope)
- Multi-tenant SaaS infrastructure
- CRDTs or advanced merge (last-write-wins sufficient)
- Embedding-based search (dead end at our scale)
- Marketplace, billing, SSO

### Rabbit Holes
- Over-engineering the sync protocol — append-only + UUIDs is enough
- Building a custom graph query language — reuse existing NetworkX traversal
- Premature auth system — API key for POC, upgrade later
