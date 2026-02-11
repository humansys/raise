# Research: Memory System Impact for Multi-Source Architecture

> **ID:** RES-MULTIDEV-002
> **Date:** 2026-02-05
> **Decision:** F14.15 Multi-Developer Architecture
> **Status:** Complete

## Question

What changes are needed to the memory system to support three-tier data sources (global, project, personal) while maintaining the graph as the primary abstraction layer?

## Executive Summary

**Finding:** The memory system requires moderate refactoring, primarily in the builder and paths modules. The key architectural principle — **graph as abstraction layer** — is already partially implemented but needs enhancement.

**Scope:** 6 files need modification, ~200 lines of new code, ~50 lines modified.

**Risk:** LOW — Changes are additive, existing tests provide safety net.

## Current Architecture

### Data Flow

```
JSONL Files                    →  UnifiedGraphBuilder  →  UnifiedGraph  →  Query Engine
(.raise/rai/memory/*.jsonl)       (builds nodes)          (stores)         (searches)
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| `UnifiedGraphBuilder` | `context/builder.py` | Loads JSONL, creates graph |
| `UnifiedGraph` | `context/graph.py` | NetworkX wrapper, stores nodes |
| `ConceptNode` | `context/models.py` | Node schema (id, type, content, metadata) |
| `load_memory_from_directory` | `memory/loader.py` | Parses JSONL files |
| `get_memory_dir` | `config/paths.py` | Returns `.raise/rai/memory/` |

### Current Limitations

1. **Single source:** `load_memory()` only reads from `.raise/rai/memory/`
2. **No scope tracking:** Nodes don't indicate if they're global/project/personal
3. **No precedence:** Can't handle same ID in multiple sources
4. **Hardcoded paths:** `get_memory_dir()` returns single path

## Required Changes

### 1. Path Configuration (`config/paths.py`)

**Add:**
```python
def get_global_rai_dir() -> Path:
    """Get ~/.rai/ directory for global developer data."""
    return Path.home() / ".rai"

def get_personal_memory_dir(project_root: Path | None = None) -> Path:
    """Get .raise/rai/personal/ for developer-specific project data."""
    return get_rai_dir(project_root) / "personal"
```

**Impact:** ~20 lines, no breaking changes.

### 2. Memory Loader (`memory/loader.py`)

**Add:**
```python
class MemorySource(str, Enum):
    """Source tier for memory concepts."""
    GLOBAL = "global"      # ~/.rai/
    PROJECT = "project"    # .raise/rai/memory/
    PERSONAL = "personal"  # .raise/rai/personal/

def load_memory_from_sources(
    global_dir: Path | None,
    project_dir: Path,
    personal_dir: Path | None,
) -> MemoryLoadResult:
    """Load memory from all three tiers with source tracking."""
```

**Impact:** ~50 lines, existing function unchanged (backward compatible).

### 3. Graph Builder (`context/builder.py`)

**Modify `load_memory()`:**
```python
def load_memory(self) -> list[ConceptNode]:
    """Load concepts from all memory sources.

    Sources loaded in precedence order (later wins on ID conflict):
    1. Global (~/.rai/) — universal patterns/calibration
    2. Project (.raise/rai/memory/) — shared project knowledge
    3. Personal (.raise/rai/personal/) — developer-specific data
    """
    nodes: list[ConceptNode] = []

    # Load global
    global_dir = get_global_rai_dir()
    if global_dir.exists():
        nodes.extend(self._load_memory_tier(global_dir, "global"))

    # Load project
    project_dir = get_memory_dir(self.project_root)
    if project_dir.exists():
        nodes.extend(self._load_memory_tier(project_dir, "project"))

    # Load personal
    personal_dir = get_personal_memory_dir(self.project_root)
    if personal_dir.exists():
        nodes.extend(self._load_memory_tier(personal_dir, "personal"))

    return nodes

def _load_memory_tier(
    self,
    memory_dir: Path,
    scope: Literal["global", "project", "personal"]
) -> list[ConceptNode]:
    """Load memory from a single tier, adding scope to metadata."""
    nodes = []
    # ... load patterns, calibration, sessions ...
    for node in nodes:
        node.metadata["scope"] = scope
    return nodes
```

**Impact:** ~40 lines modified, ~30 lines new.

### 4. Node Model (`context/models.py`)

**Option A — Metadata field (recommended):**
```python
# No schema change needed
# scope stored in metadata["scope"]
```

**Option B — Explicit field:**
```python
class ConceptNode(BaseModel):
    # ... existing fields ...
    scope: Literal["global", "project", "personal"] | None = Field(
        default=None,
        description="Source tier for provenance"
    )
```

**Recommendation:** Use metadata (Option A) — simpler, no migration needed.

### 5. Memory Writer (`memory/writer.py`)

**Add scope-aware writing:**
```python
def append_pattern(
    memory_dir: Path,
    pattern: PatternInput,
    scope: Literal["project", "personal"] = "personal",
) -> str:
    """Append pattern to appropriate location based on scope."""
```

**Impact:** ~20 lines, signature change (backward compatible with default).

### 6. CLI Commands (`cli/commands/memory.py`)

**Modify emit commands:**
```python
@memory_app.command("emit-pattern")
def emit_pattern(
    # ... existing args ...
    scope: Annotated[
        str,
        typer.Option("--scope", "-s", help="Scope: personal or project"),
    ] = "personal",
):
    """Emit a pattern to memory."""
```

**Impact:** ~10 lines per command.

## The "Graph as Abstraction" Principle

### Current State

```
Agent → rai memory query "TDD" → Graph → Results
        (already abstracts file location)
```

The graph IS already the abstraction layer. Agents don't read JSONL files directly.

### Enhanced State (Option B)

```
Agent → rai memory query "TDD" → Graph → Results with scope metadata
                                            ↓
                                   [{content: "...", scope: "global"},
                                    {content: "...", scope: "project"}]
```

**Key principle:** The agent queries the graph. The graph knows provenance but presents unified results. The agent doesn't need to know WHERE data came from, only that it exists.

### Query Behavior

| Scenario | Behavior |
|----------|----------|
| Same pattern in global + project | Both returned, ranked by scope (project > global) |
| Session query | Only personal sessions returned (sessions are always personal) |
| Calibration query | Returns merged (personal overrides global for same metric) |

## Precedence Rules

When the same concept ID exists in multiple tiers:

```
GLOBAL (lowest)  →  PROJECT  →  PERSONAL (highest)
```

**Implementation:**
```python
def _deduplicate_by_precedence(nodes: list[ConceptNode]) -> list[ConceptNode]:
    """Keep highest-precedence node when IDs conflict."""
    precedence = {"global": 0, "project": 1, "personal": 2}
    by_id: dict[str, ConceptNode] = {}
    for node in nodes:
        node_scope = node.metadata.get("scope", "project")
        existing = by_id.get(node.id)
        if not existing:
            by_id[node.id] = node
        else:
            existing_scope = existing.metadata.get("scope", "project")
            if precedence[node_scope] > precedence[existing_scope]:
                by_id[node.id] = node
    return list(by_id.values())
```

## Migration Strategy

### Existing Data

1. `.raise/rai/memory/sessions/` → `.raise/rai/personal/sessions/`
2. `.raise/rai/telemetry/` → `.raise/rai/personal/telemetry/`
3. `.raise/rai/memory/calibration.jsonl` → `.raise/rai/personal/calibration.jsonl`
4. `.raise/rai/memory/patterns.jsonl` → stays (shared project patterns)

### Migration on First Access

```python
def ensure_personal_dir(project_root: Path) -> Path:
    """Ensure personal directory exists, migrate if needed."""
    personal_dir = get_personal_memory_dir(project_root)
    if not personal_dir.exists():
        personal_dir.mkdir(parents=True)
        _migrate_personal_data(project_root, personal_dir)
    return personal_dir
```

### Global Directory Bootstrap

```python
def ensure_global_dir() -> Path:
    """Ensure ~/.rai/ exists with minimal structure."""
    global_dir = get_global_rai_dir()
    if not global_dir.exists():
        global_dir.mkdir(parents=True)
        (global_dir / "patterns.jsonl").touch()
        (global_dir / "calibration.jsonl").touch()
    return global_dir
```

## Test Coverage

### New Tests Needed

| Test | Purpose |
|------|---------|
| `test_load_memory_global` | Global dir loading |
| `test_load_memory_personal` | Personal dir loading |
| `test_load_memory_precedence` | ID conflict resolution |
| `test_scope_in_metadata` | Scope tracking |
| `test_migration` | Data migration |
| `test_query_across_tiers` | Unified query results |

**Estimate:** ~15 new tests, ~100 lines.

## Impact Summary

| File | Lines Changed | Risk |
|------|---------------|------|
| `config/paths.py` | +20 | Low |
| `memory/loader.py` | +50 | Low |
| `context/builder.py` | +70, ~40 modified | Medium |
| `context/models.py` | 0 (use metadata) | None |
| `memory/writer.py` | +20, ~10 modified | Low |
| `cli/commands/memory.py` | +30 | Low |
| **Total** | ~200 new, ~50 modified | **Low** |

## Risks and Mitigations

| Risk | L | I | Mitigation |
|------|:-:|:-:|------------|
| Breaking existing queries | L | H | Scope in metadata, not breaking schema |
| Migration data loss | L | H | Copy, don't move; verify before delete |
| Performance (3x file reads) | L | L | Files are small, reads are fast |
| Precedence confusion | M | M | Clear documentation, logging |

## Recommendation

**Proceed with Option B implementation.** The changes are:
1. **Additive** — No breaking changes to existing code
2. **Testable** — Existing 1028 tests provide safety net
3. **Aligned** — Follows the "graph as abstraction" principle
4. **Moderate scope** — ~250 lines total, achievable in 1 day

### Implementation Order

1. `paths.py` — Add new path helpers
2. `loader.py` — Add multi-source loading
3. `builder.py` — Modify `load_memory()` for three tiers
4. `writer.py` — Add scope-aware writing
5. `memory.py` — Update CLI commands
6. Migration logic
7. Tests

## References

- Current architecture: `src/rai_cli/context/builder.py`
- Graph implementation: `src/rai_cli/context/graph.py`
- ADR-019: Unified Context Graph Architecture
