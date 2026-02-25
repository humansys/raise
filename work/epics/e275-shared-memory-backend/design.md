---
epic_id: "RAISE-275"
grounded_in: "Gemba of src/rai_cli/context/models.py, context/graph.py, context/query.py, adapters/protocols.py, adapters/models.py, graph/filesystem_backend.py, context/builder.py"
---

# Epic Design: Shared Memory Backend

## Affected Surface (Gemba)

| Module/File | Current State | Changes |
|-------------|---------------|---------|
| `src/rai_cli/context/models.py` | 20 classes (GraphNode + 18 subclasses), 0 internal deps | **MOVE** to `rai_core/models.py`, re-export from original location |
| `src/rai_cli/context/graph.py` | UnifiedGraph wrapping NetworkX MultiDiGraph | **MOVE** to `rai_core/graph.py`, re-export |
| `src/rai_cli/context/query.py` | QueryEngine + scoring (keyword, concept_lookup) | **MOVE** to `rai_core/query.py`, re-export |
| `src/rai_cli/adapters/protocols.py` | 5 protocols (KnowledgeGraphBackend, etc.) | **MOVE** to `rai_core/adapters/protocols.py`, re-export |
| `src/rai_cli/adapters/models.py` | BackendHealth, ArtifactLocator, etc. | **MOVE** to `rai_core/adapters/models.py`, re-export |
| `src/rai_cli/graph/filesystem_backend.py` | FilesystemGraphBackend + get_active_backend() | **MOVE** to `rai_core/backends/filesystem.py`, re-export |
| `src/rai_cli/context/builder.py` | UnifiedGraphBuilder (depends on CLI infra) | **STAYS** in rai_cli — CLI orchestrator |
| `src/rai_cli/context/__init__.py` | Re-exports all context classes | **REFACTOR** to re-export from rai_core |
| ~30 files across src/ + tests/ | Import from `rai_cli.context.*` | **UPDATE** imports (or rely on re-exports) |
| `pyproject.toml` | Single package (rai-cli) | **ADD** rai-core as workspace package, rai-server as new package |

## Target Components

| Component | Responsibility | Key Interface |
|-----------|---------------|---------------|
| `rai_core` | Shared models, graph, query, protocols, backends | `GraphNode`, `UnifiedGraph`, `KnowledgeGraphBackend` protocol |
| `rai_server` | FastAPI API server over PostgreSQL | 8 REST endpoints at `/api/v1/graph/*` |
| `rai_server.db` | SQLAlchemy models + Alembic migrations | `GraphNodeRow`, `GraphEdgeRow`, `OrgRow`, `ApiKeyRow` |
| `rai_server.api.v1` | Route handlers + auth dependency | `verify_api_key() → OrgContext` |
| `rai_core.backends.api` | HTTP client backend for CLI→Server | `ApiGraphBackend`, `DualWriteBackend` |
| Docker Compose | PG + server dev environment | `docker compose up` |

## Key Contracts

### rai_core — Shared Protocol (unchanged from ADR-036)

```python
@runtime_checkable
class KnowledgeGraphBackend(Protocol):
    def persist(self, graph: UnifiedGraph) -> None: ...
    def load(self) -> UnifiedGraph: ...
    def health(self) -> BackendHealth: ...
```

### rai_core — ApiGraphBackend (new)

```python
class ApiGraphBackend:
    def __init__(self, base_url: str, api_key: str) -> None: ...
    def persist(self, graph: UnifiedGraph) -> None: ...
    def load(self) -> UnifiedGraph: ...
    def health(self) -> BackendHealth: ...

class DualWriteBackend:
    def __init__(self, local: FilesystemGraphBackend, remote: ApiGraphBackend) -> None: ...
    def persist(self, graph: UnifiedGraph) -> None: ...  # local always, remote best-effort
    def load(self) -> UnifiedGraph: ...  # from remote if available, else local
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

## Migration Path

### Backward Compatibility Strategy

1. **Re-export layer:** `rai_cli.context.models` re-exports everything from `rai_core.models`. Existing code keeps working with zero changes.

2. **Backend selection:** `get_active_backend()` checks for `RAI_SERVER_URL` + `RAI_API_KEY` env vars:
   - Both set → `DualWriteBackend(local, remote)`
   - Neither set → `FilesystemGraphBackend` (current behavior, zero change)

3. **No breaking changes to CLI commands.** All changes are additive.

4. **Import migration:** Can be done incrementally — re-exports ensure old paths work. Direct `rai_core` imports are preferred for new code.
