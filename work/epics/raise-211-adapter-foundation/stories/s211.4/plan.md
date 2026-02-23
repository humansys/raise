# Implementation Plan: KnowledgeGraphBackend

## Overview
- **Story:** S211.4
- **Size:** M
- **Tasks:** 5
- **Derived from:** design.md § Target Interfaces
- **Created:** 2026-02-22

## Tasks

### Task 1: FilesystemGraphBackend class + tests

**Objective:** Create the backend class that implements KnowledgeGraphBackend Protocol with persist, load, and health.

**RED — Write Failing Test:**
- **File:** `tests/graph/test_filesystem_backend.py`
- **Test functions:**
  - `test_persist_saves_graph_to_json` — persist writes index.json with NetworkX node_link_data format
  - `test_load_reads_graph_from_json` — load reconstructs UnifiedGraph from JSON
  - `test_persist_load_roundtrip` — persist then load produces identical graph (node count, edge count, content)
  - `test_load_nonexistent_raises` — load with bad path raises FileNotFoundError
  - `test_health_returns_healthy` — health() returns BackendHealth with status="healthy"
  - `test_implements_protocol` — isinstance(FilesystemGraphBackend(), KnowledgeGraphBackend) is True
- **Setup:** Create UnifiedGraph with sample nodes and edges
- **Assertion:** Persisted graph loads back identically; health reports healthy; satisfies Protocol

```python
def test_persist_saves_graph_to_json(tmp_path: Path) -> None:
    backend = FilesystemGraphBackend()
    graph = _make_sample_graph()
    out = tmp_path / "index.json"
    backend.persist(graph, out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert "nodes" in data  # NetworkX node_link_data format

def test_implements_protocol() -> None:
    assert isinstance(FilesystemGraphBackend(), KnowledgeGraphBackend)
```

**GREEN — Implement:**
- **File:** `src/rai_cli/graph/filesystem_backend.py`
- **Class:** `FilesystemGraphBackend`
```python
class FilesystemGraphBackend:
    def persist(self, graph: UnifiedGraph, path: Path) -> None: ...
    def load(self, path: Path) -> UnifiedGraph: ...
    def health(self) -> BackendHealth: ...
```
- **Logic:** Move serialization logic from `UnifiedGraph.save()`/`load()` into this class. Same NetworkX node_link_data JSON format.

**Verification:**
```bash
pytest tests/graph/test_filesystem_backend.py -v
```

**Size:** M
**Dependencies:** None
**AC Reference:** Scenarios "Protocol contract exists", "Backend discovered via entry points"

---

### Task 2: Remove save/load from UnifiedGraph + fix test_graph.py

**Objective:** Remove `save()` and `load()` from UnifiedGraph. Update `test_graph.py` to use FilesystemGraphBackend instead.

**RED — Write Failing Test:**
- No new tests. Existing `test_graph.py` tests for save/load will fail once methods are removed — that's the signal. Migrate them to `test_filesystem_backend.py` or rewrite to use backend.

**GREEN — Implement:**
- **File:** `src/rai_cli/context/graph.py`
  - Delete `save()` method (lines 283-296)
  - Delete `load()` classmethod (lines 298-320)
- **File:** `tests/context/test_graph.py`
  - Replace `graph.save(path)` → `FilesystemGraphBackend().persist(graph, path)`
  - Replace `UnifiedGraph.load(path)` → `FilesystemGraphBackend().load(path)`

**Verification:**
```bash
pytest tests/context/test_graph.py tests/graph/test_filesystem_backend.py -v
```

**Size:** S
**Dependencies:** T1
**AC Reference:** Scenario "FilesystemGraphBackend replaces hardcoded persistence"

---

### Task 3: Entry point + get_active_backend helper

**Objective:** Register FilesystemGraphBackend as entry point `local` and create helper function for backend resolution.

**RED — Write Failing Test:**
- **File:** `tests/graph/test_filesystem_backend.py` (append)
- **Test functions:**
  - `test_get_active_backend_returns_filesystem` — helper returns FilesystemGraphBackend instance
  - `test_entry_point_registered` — `get_graph_backends()` discovers "local" pointing to FilesystemGraphBackend
```python
def test_get_active_backend_returns_filesystem() -> None:
    backend = get_active_backend()
    assert isinstance(backend, FilesystemGraphBackend)
```

**GREEN — Implement:**
- **File:** `src/rai_cli/graph/filesystem_backend.py` — add `get_active_backend()` function
```python
def get_active_backend() -> FilesystemGraphBackend:
    """Resolve the active graph backend. Always local until S211.5 (TierContext)."""
    return FilesystemGraphBackend()
```
- **File:** `pyproject.toml` — add entry point:
```toml
[project.entry-points."rai.graph.backends"]
local = "rai_cli.graph.filesystem_backend:FilesystemGraphBackend"
```

**Verification:**
```bash
pytest tests/graph/test_filesystem_backend.py -v
pip install -e . && python -c "from rai_cli.adapters.registry import get_graph_backends; print(get_graph_backends())"
```

**Size:** S
**Dependencies:** T1
**AC Reference:** Scenario "Backend discovered via entry points"

---

### Task 4: Migrate all production call sites

**Objective:** Replace all `graph.save()` and `UnifiedGraph.load()` in production code with backend calls.

**GREEN — Implement:**

| File | Line(s) | Before | After |
|------|---------|--------|-------|
| `cli/commands/memory.py` | 515 | `UnifiedGraph.load(output_path)` | `backend.load(output_path)` |
| `cli/commands/memory.py` | 533 | `graph.save(output_path)` | `backend.persist(graph, output_path)` |
| `cli/commands/memory.py` | 621 | `UnifiedGraph.load(index_path)` | `backend.load(index_path)` |
| `cli/commands/memory.py` | 913 | `UnifiedGraph.load(unified_path)` | `backend.load(unified_path)` |
| `cli/commands/discover.py` | 350 | `graph.save(graph_path)` | `backend.persist(graph, graph_path)` |
| `cli/commands/release.py` | 49 | `UnifiedGraph.load(graph_path)` | `backend.load(graph_path)` |
| `session/bundle.py` | 53, 80 | `UnifiedGraph.load(graph_path)` | `backend.load(graph_path)` |
| `context/query.py` | 347 | `UnifiedGraph.load(path)` | `backend.load(path)` |

- Each file: add `from rai_cli.graph.filesystem_backend import get_active_backend` and instantiate `backend = get_active_backend()`.

**Verification:**
```bash
pytest tests/ -x --timeout=60
pyright src/rai_cli/
ruff check src/rai_cli/
```

**Size:** M
**Dependencies:** T1, T2, T3
**AC Reference:** Scenarios "FilesystemGraphBackend replaces hardcoded persistence", "FilesystemGraphBackend replaces hardcoded querying"

---

### Task 5: Migrate test fixtures + integration verification

**Objective:** Update remaining test files that use `graph.save()`/`UnifiedGraph.load()` for fixture setup. Run full suite to verify zero regression.

**GREEN — Implement:**

| Test File | Call Sites |
|-----------|-----------|
| `tests/session/test_bundle.py` | ~5 `graph.save()` calls |
| `tests/context/test_query.py` | 1 `graph.save()` call |
| `tests/cli/commands/test_memory_build_diff.py` | ~4 `graph.save()` calls |
| `tests/cli/test_release.py` | ~2 `graph.save()` calls |

- Replace `graph.save(path)` → `FilesystemGraphBackend().persist(graph, path)`
- Replace `UnifiedGraph.load(path)` → `FilesystemGraphBackend().load(path)`
- Remove unused `UnifiedGraph` imports where applicable

**Verification:**
```bash
# Full test suite — zero regression gate
pytest tests/ -v --timeout=120

# Type + lint gates
pyright src/ tests/
ruff check .

# Manual integration: build the graph and verify identical output
rai memory build
```

**Size:** M
**Dependencies:** T4
**AC Reference:** Scenario "Zero regression on existing tests"

## Execution Order

1. **T1** — FilesystemGraphBackend class + tests (foundation)
2. **T2** — Remove save/load from UnifiedGraph (depends on T1)
3. **T3** — Entry point + helper (parallel with T2, both depend on T1)
4. **T4** — Migrate production call sites (depends on T1, T2, T3)
5. **T5** — Migrate test fixtures + full verification (depends on T4)

## Traceability

| AC Scenario | Task(s) | Design § |
|-------------|---------|----------|
| "Protocol contract exists" | T1 | Target Interfaces → FilesystemGraphBackend |
| "FilesystemGraphBackend replaces hardcoded persistence" | T2, T4 | Gemba → graph.py, memory.py, discover.py |
| "FilesystemGraphBackend replaces hardcoded querying" | T4 | Gemba → memory.py, release.py, bundle.py, query.py |
| "Backend discovered via entry points" | T3 | Target Interfaces → get_active_backend, pyproject.toml |
| "Zero regression on existing tests" | T5 | Constraints → zero regression |

## Risks
- **Serialization format mismatch:** FilesystemGraphBackend must produce byte-identical JSON to old `UnifiedGraph.save()`. Mitigation: roundtrip test compares output.
- **Hidden UnifiedGraph.load() callers:** grep may miss dynamic or aliased calls. Mitigation: after removing save/load, pyright will catch any remaining references as errors.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| T1 | M | -- | |
| T2 | S | -- | |
| T3 | S | -- | |
| T4 | M | -- | |
| T5 | M | -- | |
