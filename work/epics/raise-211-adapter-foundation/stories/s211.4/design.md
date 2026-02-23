---
story_id: "S211.4"
title: "KnowledgeGraphBackend"
epic_ref: "RAISE-211"
phase: "design"
status: "draft"
created: "2026-02-22"
---

# Design: KnowledgeGraphBackend

## 1. What & Why

**Problem:** Graph persistence (save/load) is hardcoded in `UnifiedGraph.save()`/`load()` and called directly from the `rai memory build` command. PRO cannot plug in alternative storage (Supabase) without modifying core code.

**Value:** After this story, persistence is behind a Protocol + entry point. raise-pro can register `SupabaseGraphBackend` as a plugin that replaces filesystem storage — zero core modifications needed.

## 2. Approach

Refactor graph persistence into a `FilesystemGraphBackend` class that implements the existing `KnowledgeGraphBackend` Protocol (already in `protocols.py`). Migrate **all** production call sites of `graph.save()` and `UnifiedGraph.load()` to use the backend. Register as entry point `local` in `rai.graph.backends`.

**Scope:** persist + load + health only. No query abstraction (UnifiedQueryEngine works), no merge (no PRO consumer yet). YAGNI.

**Full migration** (from architecture review Q1): all production save/load sites go through the backend, not just memory build. This avoids a half-abstraction where some code uses the backend and some doesn't.

**Production call sites to migrate:**

Save (2):
- `cli/commands/memory.py:533` — `rai memory build`
- `cli/commands/discover.py:350` — `rai discover scan`

Load (6):
- `cli/commands/memory.py:515` — build: load old graph for diff
- `cli/commands/memory.py:621` — `rai memory query`
- `cli/commands/memory.py:913` — `rai memory context`
- `cli/commands/release.py:49` — `rai release`
- `session/bundle.py:53,80` — session start bundle
- `context/query.py:347` — `UnifiedQueryEngine.from_file()`

**Components affected:**
- `src/rai_cli/graph/filesystem_backend.py` — **create** (FilesystemGraphBackend + get_active_backend)
- `src/rai_cli/adapters/protocols.py` — **no change** (Protocol already exists)
- `src/rai_cli/cli/commands/memory.py` — **modify** (3 call sites)
- `src/rai_cli/cli/commands/discover.py` — **modify** (1 call site)
- `src/rai_cli/cli/commands/release.py` — **modify** (1 call site)
- `src/rai_cli/session/bundle.py` — **modify** (2 call sites)
- `src/rai_cli/context/query.py` — **modify** (1 call site)
- `pyproject.toml` — **modify** (add entry point)
- `tests/` — **create** (backend tests)

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `src/rai_cli/adapters/protocols.py:85-95` | `KnowledgeGraphBackend` Protocol with `persist(graph)`, `load(path)`, `health()` | No change — Protocol already has the right shape | All methods |
| `src/rai_cli/adapters/models.py` | `BackendHealth` model already exists | No change | Model definition |
| `src/rai_cli/context/graph.py:283-320` | `UnifiedGraph.save(path)` and `UnifiedGraph.load(path)` | Stay as-is — backend wraps them | Both methods unchanged |
| `src/rai_cli/cli/commands/memory.py:509-533` | `build()` calls `graph.save(output_path)` and `UnifiedGraph.load(output_path)` | Replace with `backend.persist(graph)` and `backend.load(path)` | Build orchestration, diff logic, formatting |
| `src/rai_cli/cli/commands/memory.py:621` | `query()` calls `UnifiedGraph.load(index_path)` | Replace with `backend.load(path)` | Query logic |
| `src/rai_cli/cli/commands/memory.py:913` | `context()` calls `UnifiedGraph.load(unified_path)` | Replace with `backend.load(path)` | Context logic |
| `src/rai_cli/cli/commands/discover.py:350` | `graph.save(graph_path)` | Replace with `backend.persist(graph)` | Discovery logic |
| `src/rai_cli/cli/commands/release.py:49` | `UnifiedGraph.load(graph_path)` | Replace with `backend.load(path)` | Release logic |
| `src/rai_cli/session/bundle.py:53,80` | `UnifiedGraph.load(graph_path)` (2 sites) | Replace with `backend.load(path)` | Bundle assembly |
| `src/rai_cli/context/query.py:347` | `UnifiedQueryEngine.from_file()` calls `UnifiedGraph.load(path)` | Replace with `backend.load(path)` | Query engine init |
| `src/rai_cli/adapters/registry.py:88-90` | `get_graph_backends()` discovers `rai.graph.backends` | No change — already implemented | Discovery function |

## 4. Target Interfaces

### New Class

```python
# src/rai_cli/graph/filesystem_backend.py

class FilesystemGraphBackend:
    """Built-in graph backend — persists to local .raise/rai/memory/.

    COMMUNITY backend. Zero external dependencies.
    Registered as entry point 'local' in rai.graph.backends.
    """

    def __init__(self, base_path: Path | None = None) -> None: ...

    def persist(self, graph: UnifiedGraph) -> None:
        """Save graph to base_path/index.json using NetworkX node_link_data."""
        ...

    def load(self, path: Path) -> UnifiedGraph:
        """Load graph from JSON file."""
        ...

    def health(self) -> BackendHealth:
        """Return BackendHealth(ok=True, backend='filesystem')."""
        ...
```

### New Helper

```python
# src/rai_cli/graph/filesystem_backend.py (or adapters/registry.py)

def get_active_backend(base_path: Path | None = None) -> KnowledgeGraphBackend:
    """Resolve the active graph backend.

    For now: always returns FilesystemGraphBackend (COMMUNITY).
    S211.5 (TierContext) will add tier-based selection.
    """
    ...
```

### Modified Call Sites (all production save/load)

```python
# Save — before:
graph.save(output_path)
# Save — after:
backend = get_active_backend()
backend.persist(graph)  # persist resolves path internally

# Load — before:
graph = UnifiedGraph.load(path)
# Load — after:
backend = get_active_backend()
graph = backend.load(path)
```

### Integration Points
- All production save/load sites use `get_active_backend()` to obtain the backend
- `get_active_backend()` returns `FilesystemGraphBackend` directly (no entry point discovery yet — trivial until S211.5)
- `FilesystemGraphBackend` delegates to `UnifiedGraph.save()`/`load()` internally
- Entry point `local` registered in `pyproject.toml` under `rai.graph.backends`
- `UnifiedGraph.save()`/`load()` remain public for test code and backward compat

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **Zero regression:** All 1610+ tests must pass without modification
- **Identical output:** `rai memory build` produces byte-identical `index.json`
- **No TierContext dependency:** Backend selection is simple (always local) until S211.5
- **Backward compat:** `UnifiedGraph.save()`/`load()` remain public — used extensively in test code
