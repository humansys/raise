---
epic_id: "RAISE-275"
grounded_in: "Gemba of src/rai_cli/context/models.py, context/graph.py, context/query.py, adapters/protocols.py, adapters/models.py, graph/filesystem_backend.py, context/builder.py"
architecture_review: "2026-02-25 — PASS with refinements"
---

# Epic Design: Shared Memory Backend

## Affected Surface (Gemba)

| Module/File | Current State | Changes |
|-------------|---------------|---------|
| `src/rai_cli/context/models.py` | 20 classes (GraphNode + 18 subclasses), 0 internal deps | **MOVE** to `rai_core/graph/models.py`, re-export from original location. **RENAME** drop "Unified" prefix where applicable. |
| `src/rai_cli/context/graph.py` | UnifiedGraph wrapping NetworkX MultiDiGraph | **MOVE** to `rai_core/graph/engine.py`. **RENAME** `UnifiedGraph` → `Graph`. Re-export old name. |
| `src/rai_cli/context/query.py` | QueryEngine + scoring (keyword, concept_lookup) | **MOVE** to `rai_core/graph/query.py`. **RENAME** `UnifiedQueryEngine` → `QueryEngine`, `UnifiedQuery` → `Query`, etc. **WITHOUT** `from_file()` — that stays in CLI as helper. |
| `src/rai_cli/adapters/protocols.py` | 5 protocols (KnowledgeGraphBackend, etc.) | **PARTIAL MOVE**: only `KnowledgeGraphBackend` → `rai_core/graph/backends/protocol.py`. Other 4 protocols stay in rai_cli. |
| `src/rai_cli/adapters/models.py` | BackendHealth, ArtifactLocator, etc. | **PARTIAL MOVE**: only `BackendHealth` → `rai_core/graph/backends/models.py`. Other 5 models stay in rai_cli. |
| `src/rai_cli/graph/filesystem_backend.py` | FilesystemGraphBackend + get_active_backend() | **MOVE** to `rai_core/graph/backends/filesystem.py`, re-export |
| `src/rai_cli/context/builder.py` | UnifiedGraphBuilder (depends on CLI infra) | **STAYS** in rai_cli — CLI orchestrator |
| `src/rai_cli/context/__init__.py` | Re-exports all context classes | **REFACTOR** to re-export from rai_core with old names as aliases |
| ~30 files across src/ + tests/ | Import from `rai_cli.context.*` | **UPDATE** imports (or rely on re-exports) |
| `pyproject.toml` | Single package (rai-cli) | **ADD** rai-core as uv workspace package, rai-server as new package |

## Package Architecture

### Three packages, one monorepo (uv workspaces)

```
raise-commons/
├── packages/
│   ├── rai-core/              # COMMUNITY (free, PyPI)
│   │   ├── pyproject.toml     # minimal deps: pydantic, networkx
│   │   └── src/rai_core/
│   │       ├── graph/         # E275 — implemented
│   │       │   ├── models.py  # GraphNode, GraphEdge, node types
│   │       │   ├── engine.py  # Graph (NetworkX wrapper)
│   │       │   ├── query.py   # QueryEngine, scoring, Wilson
│   │       │   └── backends/  # protocol + filesystem impl
│   │       ├── workflow/      # Future — placeholder with docstring
│   │       └── governance/    # Future — placeholder with docstring
│   └── rai-server/            # PRO (paid, separate distribution)
│       ├── pyproject.toml     # deps: rai-core, fastapi, sqlalchemy, asyncpg
│       └── src/rai_server/
├── src/rai_cli/               # COMMUNITY (free, PyPI)
│   └── pyproject.toml         # deps: rai-core==X.Y.Z (exact pin, lockstep)
└── pyproject.toml             # uv workspace root
```

**Version strategy:**
- `rai-core` + `rai-cli`: **lockstep** versions (same number, same release, one CI pipeline)
- `rai-server`: **independent** release, pins `rai-core>=X.Y.0,<X.Y+1.0`
- `pip install --upgrade rai-cli` → automatically upgrades `rai-core` (exact pin)

**Business boundary:**
- `rai-core` + `rai-cli` = COMMUNITY tier (free, open, PyPI)
- `rai-server` = PRO tier (paid, separate distribution)
- `rai-core` is the shared domain contract between free and paid offerings

### rai-core: Shared RaiSE Domain (not just graph)

`rai-core` is the **shared domain model** of RaiSE — the vocabulary, protocols, and logic
that any RaiSE component needs. It accommodates three domain axes:

| Domain | E275 Status | Contents |
|--------|:-----------:|----------|
| **graph** | Implemented | Models (GraphNode, GraphEdge, 18 node types), engine (Graph), query (QueryEngine, scoring), backends (protocol + filesystem) |
| **workflow** | Placeholder | Work item types, state machines, gates, default workflow definitions |
| **governance** | Placeholder | Extensible artifact type schema, governance vocabulary |

DDD grounding: rai-core maps to the **Ontology bounded context** from `governance/architecture/domain-model.md`
— "the ontological backbone of RaiSE" — plus shared domain models for workflow and governance
that multiple components (CLI, server, Forge, future UIs) need to agree on.

## Target Components

| Component | Responsibility | Key Interface |
|-----------|---------------|---------------|
| `rai_core.graph` | Shared models, graph engine, query, backends | `GraphNode`, `Graph`, `KnowledgeGraphBackend` protocol |
| `rai_server` | FastAPI API server over PostgreSQL | 8 REST endpoints at `/api/v1/graph/*` |
| `rai_server.db` | SQLAlchemy models + Alembic migrations | `GraphNodeRow`, `GraphEdgeRow`, `OrgRow`, `ApiKeyRow` |
| `rai_server.api.v1` | Route handlers + auth dependency | `verify_api_key() → OrgContext` |
| `rai_core.graph.backends.api` | HTTP client backend for CLI→Server | `ApiGraphBackend`, `DualWriteBackend` |
| Docker Compose | PG + server dev environment | `docker compose up` |

## Key Contracts

### rai_core.graph — Backend Protocol (unchanged from ADR-036)

```python
@runtime_checkable
class KnowledgeGraphBackend(Protocol):
    def persist(self, graph: Graph) -> None: ...
    def load(self) -> Graph: ...
    def health(self) -> BackendHealth: ...
```

### rai_core.graph — ApiGraphBackend (new)

```python
class ApiGraphBackend:
    def __init__(self, base_url: str, api_key: str) -> None: ...
    def persist(self, graph: Graph) -> None: ...
    def load(self) -> Graph: ...
    def health(self) -> BackendHealth: ...

class DualWriteBackend:
    def __init__(self, local: FilesystemGraphBackend, remote: ApiGraphBackend) -> None: ...
    def persist(self, graph: Graph) -> None: ...  # local always, remote best-effort
    def load(self) -> Graph: ...  # from remote if available, else local
    def health(self) -> BackendHealth: ...
```

### rai_server — API Endpoints

```
GET  /health                          → {status, version, db_ok}
POST /api/v1/graph/nodes              → create single node
GET  /api/v1/graph/nodes/{id}         → get node by id
POST /api/v1/graph/nodes/batch        → create/upsert multiple nodes
POST /api/v1/graph/edges              → create single edge
POST /api/v1/graph/edges/batch        → create/upsert multiple edges
GET  /api/v1/graph/query?q=&types=    → keyword search with scope filtering
GET  /api/v1/graph/subgraph?root_id=  → BFS subgraph for NetworkX client-side
```

### rai_server — Auth

```python
async def verify_api_key(authorization: str = Header(...)) -> OrgContext:
    """FastAPI dependency. Validates API key, returns org context."""

class OrgContext(BaseModel):
    org_id: UUID
    org_name: str
```

### rai_server — DB Schema

```sql
-- 4 tables total
orgs (id UUID PK, name, created_at)
api_keys (key_hash TEXT PK, org_id FK, expires_at, created_at)
graph_nodes (id UUID PK, org_id FK, repo_id, scope, node_type, content, source_file, properties JSONB, created_at, updated_at)
graph_edges (id UUID PK, org_id FK, source_id FK, target_id FK, edge_type, weight, properties JSONB, created_at)
```

## What Moves vs What Stays (Architecture Review Refinement)

### To rai_core (shared domain)

| Current Location | New Location | What | Rename |
|-----------------|-------------|------|--------|
| `context/models.py` | `rai_core/graph/models.py` | GraphNode + 18 subclasses, GraphEdge, CoreEdgeTypes, NodeType, EdgeType | — |
| `context/graph.py` | `rai_core/graph/engine.py` | UnifiedGraph | → `Graph` |
| `context/query.py` | `rai_core/graph/query.py` | UnifiedQueryEngine, UnifiedQuery, UnifiedQueryResult, UnifiedQueryMetadata, UnifiedQueryStrategy, scoring functions | → drop `Unified` prefix |
| `adapters/protocols.py` | `rai_core/graph/backends/protocol.py` | `KnowledgeGraphBackend` only | — |
| `adapters/models.py` | `rai_core/graph/backends/models.py` | `BackendHealth` only | — |
| `graph/filesystem_backend.py` | `rai_core/graph/backends/filesystem.py` | `FilesystemGraphBackend`, `get_active_backend()` | — |

### Stays in rai_cli

| File | What Stays | Why |
|------|-----------|-----|
| `adapters/protocols.py` | `ProjectManagementAdapter`, `GovernanceSchemaProvider`, `GovernanceParser`, `DocumentationTarget` | Governance/PM concerns, not graph domain |
| `adapters/models.py` | `CoreArtifactType`, `ArtifactLocator`, `IssueSpec`, `IssueRef`, `PublishResult` | Governance/PM vocabulary, not needed by server |
| `context/builder.py` | `UnifiedGraphBuilder` | Depends on CLI infra (config, memory, governance extractors) |
| `context/query.py` | `from_file()` factory method | Convenience helper that couples to filesystem path; CLI-specific glue |

## Migration Path

### Backward Compatibility Strategy

1. **Re-export layer:** `rai_cli.context.models` re-exports everything from `rai_core.graph.models`. Old names (`UnifiedGraph`, `UnifiedQueryEngine`, etc.) are aliased. Existing code keeps working with zero changes.

2. **Backend selection:** `get_active_backend()` checks for `RAI_SERVER_URL` + `RAI_API_KEY` env vars:
   - Both set → `DualWriteBackend(local, remote)`
   - Neither set → `FilesystemGraphBackend` (current behavior, zero change)

3. **No breaking changes to CLI commands.** All changes are additive.

4. **Import migration:** Can be done incrementally — re-exports ensure old paths work. Direct `rai_core` imports are preferred for new code.

## Architecture Review Log

**Review date:** 2026-02-25
**Scope:** Epic (pre-implementation)
**Verdict:** PASS

### Refinements from review

| # | Finding | Resolution |
|---|---------|-----------|
| R1 | `protocols.py` mixes graph + governance concerns | Partial move: only `KnowledgeGraphBackend` to core |
| R2 | `adapters/models.py` mixes graph + governance concerns | Partial move: only `BackendHealth` to core |
| Q1 | Package structure | 3 packages (core+cli lockstep on PyPI, server PRO separate) |
| Q2 | `query.py` in core | Yes, without `from_file()`. Engine receives Graph, no I/O. |
| Q3 | DualWriteBackend necessity | Justified — real resilience logic (fallback, best-effort) |
| Q4 | 8 endpoints vs batch-only | 8 justified — batch for CLI, single for Forge/API consumers |
| Rename | Drop "Unified" prefix | During S275.1 extraction, re-exports for backward compat |
| Scope | rai-core is shared domain, not just graph | Structure accommodates graph + workflow + governance axes |

### Parking lot items captured

- Workflow engine with per-org extensibility (future epic)
- Extensible governance schema for custom artifact types (future epic)
- rai-core three-axis structure (graph/workflow/governance placeholders in S275.1)
