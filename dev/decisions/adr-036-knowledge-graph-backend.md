---
id: "ADR-036"
title: "KnowledgeGraphBackend — Abstracción del storage del knowledge graph"
date: "2026-02-20"
status: "Accepted"
---

# ADR-036: KnowledgeGraphBackend

## Context

`rai memory build` construye el knowledge graph y lo persiste en el filesystem local
(`.raise/rai/memory/index.json` + archivos JSONL). `rai memory query` lee de ahí con
búsqueda por keywords y graph traversal. Ambas operaciones están hardcodeadas al filesystem.

Este supuesto funciona perfectamente para COMMUNITY — el developer trabaja solo, el grafo
es suyo, vive en su repo. Pero rompe en cuanto introducimos PRO:

1. **Shared memory:** El diferenciador principal de PRO es que el knowledge graph es del
   equipo, no del developer. Esto requiere PostgreSQL + pgvector en Supabase — no el
   filesystem local del developer.

2. **Semantic search:** `rai memory query` con búsqueda por keywords es suficiente para
   grafos personales pequeños. Con un grafo de equipo con cientos de patterns, la búsqueda
   semántica (pgvector) produce resultados cualitativamente mejores.

3. **Aggregation:** `rai memory build` para memoria compartida debe agregar datos de
   múltiples developers. Esa agregación no puede ocurrir en la máquina de un solo developer.

ADR-034 (GovernanceParser) estableció el patrón correcto para el **input side** de
`rai memory build`: las fuentes de datos son extensibles via entry points. Este ADR aplica
el mismo patrón al **output side**: dónde se persiste el grafo resultante.

Dos constraints:

1. **COMMUNITY debe funcionar con zero backend** — sin servidor, sin cuenta, sin internet
   (más allá de la API key del LLM del developer). El filesystem local es el backend de
   COMMUNITY y no puede degradarse.

2. **La interfaz debe ser idéntica** — desde el punto de vista del caller (`rai memory build`,
   `rai memory query`), el backend es opaco. Si el comportamiento observable cambia según
   el backend instalado, la UX se fragmenta.

## Decision

### 1. `KnowledgeGraphBackend` Protocol en raise-core (Apache 2.0)

```python
# src/rai_cli/adapters/graph_backend.py

from typing import Protocol, runtime_checkable
from rai_cli.adapters.models import GraphNode, QueryStrategy, SearchResult

@runtime_checkable
class KnowledgeGraphBackend(Protocol):
    """Storage and retrieval backend for the RaiSE knowledge graph."""

    def persist(self, graph: Graph) -> None:
        """Persist the full graph. Replaces existing data."""
        ...

    def query(
        self,
        query: str,
        strategy: QueryStrategy,
        limit: int = 20,
    ) -> list[SearchResult]:
        """Search the graph. Strategy determines the algorithm."""
        ...

    def merge(self, partial: Graph) -> ConflictReport:
        """Merge a partial graph (e.g. from a team member) into the stored graph.
        Returns a report of conflicts that require human resolution."""
        ...

    def health(self) -> BackendHealth:
        """Check if the backend is reachable and operational."""
        ...
```

Entry point group: `rai.graph.backends`

### 2. `FilesystemGraphBackend` como built-in (comportamiento actual refactorizado)

```python
# src/rai_cli/graph/filesystem_backend.py

class FilesystemGraphBackend:
    """Built-in backend — persists graph to local .raise/rai/memory/ directory.

    This is the COMMUNITY backend. Zero external dependencies.
    Registered as entry point 'local' in rai.graph.backends.
    """

    def __init__(self, base_path: Path = Path(".raise/rai/memory")):
        self.base_path = base_path

    def persist(self, graph: Graph) -> None:
        # Current implementation — write index.json + JSONL files
        ...

    def query(self, query: str, strategy: QueryStrategy, limit: int) -> list[SearchResult]:
        # Current implementation — keyword search + BFS graph traversal
        ...

    def merge(self, partial: Graph) -> ConflictReport:
        # Local merge — naive last-write-wins for COMMUNITY
        # (no team conflicts in single-developer mode)
        ...

    def health(self) -> BackendHealth:
        return BackendHealth(ok=True, latency_ms=0, backend="filesystem")
```

Registrado como entry point built-in en `pyproject.toml` de raise-core:

```toml
[project.entry-points."rai.graph.backends"]
local = "rai_cli.graph.filesystem_backend:FilesystemGraphBackend"
```

### 3. `SupabaseGraphBackend` en raise-pro (no en raise-core)

```python
# En raise-pro: raise_pro/graph/supabase_backend.py

class SupabaseGraphBackend:
    """PRO backend — persists graph to PostgreSQL + pgvector on Supabase.

    Requires backend configuration in .raise/manifest.yaml.
    Registered as entry point 'supabase' in rai.graph.backends.
    """

    def query(self, query: str, strategy: QueryStrategy, limit: int) -> list[SearchResult]:
        if strategy == QueryStrategy.SEMANTIC:
            # pgvector similarity search
            return self._vector_search(query, limit)
        else:
            # Keyword search on PostgreSQL
            return self._keyword_search(query, limit)

    def merge(self, partial: Graph) -> ConflictReport:
        # Row-level conflict detection — compare against team graph
        # Returns conflicts for human resolution
        ...
```

### 4. Selección del backend

El backend activo se resuelve por este orden de precedencia:

```python
def get_active_backend(tier_context: TierContext) -> KnowledgeGraphBackend:
    backends = get_graph_backends()  # entry_points("rai.graph.backends")

    if tier_context.has(Capability.SHARED_MEMORY) and "supabase" in backends:
        return backends["supabase"]()

    # Default: filesystem (always available)
    return backends["local"]()
```

En COMMUNITY (sin backend configurado): siempre `FilesystemGraphBackend`.
En PRO (backend configurado, raise-pro instalado): `SupabaseGraphBackend`.
En PRO (backend configurado pero no disponible): `FilesystemGraphBackend` + warning.

### 5. Impacto en `rai memory build` y `rai memory query`

```python
# Antes (hardcoded):
def build_graph() -> None:
    graph = _parse_all_sources()
    _write_to_filesystem(graph, Path(".raise/rai/memory"))

# Después (extensible):
def build_graph(tier_context: TierContext) -> None:
    graph = _parse_all_sources()  # usa GovernanceParser registry (ADR-034)
    backend = get_active_backend(tier_context)
    backend.persist(graph)

# rai memory query (antes):
def query_graph(query: str) -> list[SearchResult]:
    return _keyword_search_jsonl(query, Path(".raise/rai/memory"))

# rai memory query (después):
def query_graph(query: str, strategy: QueryStrategy, tier_context: TierContext) -> list[SearchResult]:
    backend = get_active_backend(tier_context)
    return backend.query(query, strategy)
```

**Comportamiento observable en COMMUNITY:** idéntico al actual.
**Comportamiento en PRO:** `rai memory query` retorna resultados semánticos del equipo.

### 6. `QueryStrategy` enum (en raise-core)

```python
class QueryStrategy(str, Enum):
    KEYWORD = "keyword"       # BFS + keyword match (COMMUNITY default)
    CONCEPT = "concept"       # Graph traversal por tipo de concepto
    SEMANTIC = "semantic"     # Vector similarity (requiere PRO backend)
```

`rai memory query` acepta `--strategy` flag. En COMMUNITY, `--strategy semantic` produce
un mensaje claro: "Semantic search requires PRO — uses pgvector on team knowledge graph."

### 7. `ConflictReport` y merge semantics

```python
class ConflictReport(BaseModel):
    conflicts: list[GraphConflict] = []
    merged_count: int = 0
    skipped_count: int = 0

class GraphConflict(BaseModel):
    node_id: str
    local_value: str
    remote_value: str
    conflict_type: Literal["contradiction", "duplicate", "outdated"]
```

En COMMUNITY: `merge()` es un no-op (no hay remote). Siempre retorna `ConflictReport(merged_count=0)`.
En PRO: `merge()` sincroniza con el grafo del equipo en Supabase y retorna conflictos reales.

## Consequences

| Tipo | Impacto |
|------|---------|
| + | raise-pro puede enchufar `SupabaseGraphBackend` sin tocar raise-core |
| + | COMMUNITY continúa funcionando exactamente igual — `FilesystemGraphBackend` es el built-in |
| + | `rai memory query` en PRO tiene búsqueda semántica sin cambios de comando |
| + | Comportamiento de degradación claro: si backend no disponible, usa filesystem y avisa |
| + | `ConflictReport` prepara la arquitectura para resolución de conflictos en teams |
| - | `rai memory build` ahora depende de `TierContext` para seleccionar el backend (ADR-037) |
| - | Testar el backend requiere un backend mock para tests de integración |

## Relationship to other ADRs

```
ADR-034: GovernanceParser — extensibilidad del INPUT side de rai memory build
ADR-036 (this): KnowledgeGraphBackend — extensibilidad del OUTPUT side de rai memory build

ADR-035: Backend Deployment Topology — SupabaseGraphBackend corre en el servidor (server-side)
ADR-037: TierContext — selecciona el backend activo según el tier configurado
```

## Alternatives Considered

| Alternativa | Razón para rechazar |
|-------------|---------------------|
| Hardcoded Supabase en raise-core | Viola la separación open-core/commercial; contamina Apache 2.0 con dependencia de Supabase |
| Config-driven (YAML selecciona backend class) | Menos idiomático que entry points; no sigue el patrón establecido en ADR-033/034 |
| Único backend que soporta ambos modos | Crea una clase con demasiadas responsabilidades; imposible testear en aislamiento |
| Deprecar filesystem en PRO | Viola "COMMUNITY must work with zero backend"; crea experiencias divergentes |

## Open Questions

1. **Conflict resolution UX:** Cuando `rai memory build` en PRO detecta conflictos, ¿debe
   pausar y mostrarlos interactivamente, o escribir un reporte y continuar?
   Propuesta: continuar con warn + reporte en `.raise/rai/memory/conflicts-YYYY-MM-DD.yaml`.

2. **Sync frequency:** ¿`rai memory build` sincroniza al backend siempre, o solo cuando
   hay cambios? La opción eficiente es diff-based sync — solo subir nodos modificados.

3. **Offline resilience en PRO:** Si el developer está offline, `rai memory build` debería
   acumular cambios locales y sincronizar cuando vuelva la conexión (como git push offline).

---

*Status: Accepted*
*Created: 2026-02-20 (SES-224)*
*Extends: ADR-034 (GovernanceParser input side), ADR-035 (Backend Deployment Topology)*
*Implemented by: RAISE-211 Story 4*
*Enables: RAISE-209 (Team Memory — SupabaseGraphBackend en raise-pro)*
