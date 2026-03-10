---
story_id: "S211.4"
title: "KnowledgeGraphBackend"
epic_ref: "RAISE-211"
size: "M"
status: "draft"
created: "2026-02-22"
---

# Story: KnowledgeGraphBackend

## User Story
As a raise-cli developer,
I want graph persistence and querying abstracted behind a Protocol,
so that raise-pro can plug in alternative backends (Supabase) without modifying core code.

## Acceptance Criteria

### Scenario: Protocol contract exists
```gherkin
Given the adapters module
When I import KnowledgeGraphBackend
Then it is a runtime_checkable Protocol with persist, query, merge, and health methods
```

### Scenario: FilesystemGraphBackend replaces hardcoded persistence
```gherkin
Given a built knowledge graph
When rai memory build persists the graph
Then it delegates to FilesystemGraphBackend.persist()
And the output is identical to current behavior (index.json + JSONL)
```

### Scenario: FilesystemGraphBackend replaces hardcoded querying
```gherkin
Given a persisted knowledge graph
When rai memory query runs a keyword search
Then it delegates to FilesystemGraphBackend.query()
And results are identical to current UnifiedQueryEngine behavior
```

### Scenario: Backend discovered via entry points
```gherkin
Given FilesystemGraphBackend registered as entry point "local" in rai.graph.backends
When the registry discovers graph backends
Then "local" resolves to FilesystemGraphBackend
```

### Scenario: Zero regression on existing tests
```gherkin
Given the current 1610+ test suite
When all tests run after the refactor
Then all pass with no modifications to existing test assertions
```

## Examples (Specification by Example)

| Input | Action | Expected Output |
|-------|--------|----------------|
| UnifiedGraph with 50 nodes | FilesystemGraphBackend.persist() | index.json written, identical format |
| query="pattern", strategy=KEYWORD | FilesystemGraphBackend.query() | Same results as current UnifiedQueryEngine |
| FilesystemGraphBackend | .health() | BackendHealth(ok=True, backend="filesystem") |
| No backends installed | get_graph_backends() | {"local": FilesystemGraphBackend} (built-in) |

## Notes
- ADR-036 is the authoritative design document
- S211.0 (GraphNode) and S211.2 (registry) are dependencies — both done
- Scope is COMMUNITY only: FilesystemGraphBackend. SupabaseGraphBackend is raise-pro (out of scope)
- `merge()` is a no-op for filesystem (single developer, no remote)
- `get_active_backend()` depends on TierContext (S211.5) — use a simplified version or default to "local"
- Key refactor: extract persistence from UnifiedGraph.save()/load() and query from UnifiedQueryEngine into the backend
