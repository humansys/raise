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

Refactor graph persistence into a `FilesystemGraphBackend` class that implements the existing `KnowledgeGraphBackend` Protocol (already in `protocols.py`). Wire the `rai memory build` command to use the backend instead of calling `graph.save()` directly. Register the backend as entry point `local` in `rai.graph.backends`.

**Scope:** persist + load + health only. No query abstraction (UnifiedQueryEngine works), no merge (no PRO consumer yet). YAGNI.

**Components affected:**
- `src/rai_cli/graph/filesystem_backend.py` — **create** (FilesystemGraphBackend)
- `src/rai_cli/adapters/protocols.py` — **no change** (Protocol already exists)
- `src/rai_cli/cli/commands/memory.py` — **modify** (use backend for persist + load)
- `pyproject.toml` — **modify** (add entry point)
- `tests/` — **create** (backend tests)

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `src/rai_cli/adapters/protocols.py:85-95` | `KnowledgeGraphBackend` Protocol with `persist(graph)`, `load(path)`, `health()` | No change — Protocol already has the right shape | All methods |
| `src/rai_cli/adapters/models.py` | `BackendHealth` model already exists | No change | Model definition |
| `src/rai_cli/context/graph.py:283-320` | `UnifiedGraph.save(path)` and `UnifiedGraph.load(path)` | Stay as-is — backend wraps them | Both methods unchanged |
| `src/rai_cli/cli/commands/memory.py:509-533` | `build()` calls `graph.save(output_path)` and `UnifiedGraph.load(output_path)` | Replace with `backend.persist(graph)` and `backend.load(path)` | Build orchestration, diff logic, formatting |
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

### Modified: memory.py build()

```python
# Before:
graph.save(output_path)
old_graph = UnifiedGraph.load(output_path)

# After:
backend = get_active_backend(base_path=output_path.parent)
backend.persist(graph)
old_graph = backend.load(output_path)
```

### Integration Points
- `FilesystemGraphBackend` is instantiated in `memory.py:build()` via `get_active_backend()`
- `get_active_backend()` uses `get_graph_backends()` from registry to discover backends
- `FilesystemGraphBackend` delegates to `UnifiedGraph.save()`/`load()` internally
- Entry point `local` registered in `pyproject.toml` under `rai.graph.backends`

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **Zero regression:** All 1610+ tests must pass without modification
- **Identical output:** `rai memory build` produces byte-identical `index.json`
- **No TierContext dependency:** Backend selection is simple (always local) until S211.5
- **Backward compat:** `UnifiedGraph.save()`/`load()` remain public — they're used in tests and other call sites
