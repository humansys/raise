# Epic Scope: RAISE-275 Shared Memory Backend

## Objective
Deliver a server-side knowledge graph backend that enables cross-repo pattern sharing,
governance validation, and team intelligence — with OpenAPI spec as first deliverable
to unblock Fernando's Forge app (RAISE-274).

## In Scope
- OpenAPI spec defining all graph endpoints (contract-first)
- PostgresGraphBackend implementing KnowledgeGraphBackend protocol (ADR-036)
- FastAPI server with core CRUD + query endpoints
- Four-scope model with node-level isolation
- Dual-write from CLI (API + local)
- Offline fallback (degraded mode, sync on reconnect)
- Docker Compose for local development
- Dogfooding on raise-commons + raise-atlassian

## Out of Scope
- Forge app (RAISE-274)
- Multi-tenant SaaS
- Advanced merge/CRDT
- Embedding search
- Production deployment infra (beyond Docker)

## Planned Stories (draft, refined in epic-design)
1. OpenAPI spec + mock server
2. PostgreSQL schema + migrations
3. PostgresGraphBackend implementation
4. FastAPI server bootstrap
5. CLI dual-write integration
6. Offline fallback + sync

## Done Criteria
1. `POST /graph/index` → persists node → `GET /graph/query` returns it
2. Two devs share a graph across two repos
3. CLI patterns appear in shared graph within seconds
4. Personal data stays local (sessions, telemetry never hit API)
5. Fernando builds Forge actions against OpenAPI spec
