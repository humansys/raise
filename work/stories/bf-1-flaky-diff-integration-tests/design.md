---
story_id: BF-1
type: bugfix
module: mod-context
domain: bc-ontology
layer: lyr-integration
complexity: simple
---

# BF-1: Fix Flaky Diff Integration Tests

## Problem

`test_diff_integration.py` calls `UnifiedGraphBuilder().build()` which reads live
`.raise/` files. When governance content changes (new patterns, modules, node count
shifts), assertions break. The tests are testing `diff_graphs`, not the builder.

## Value

Deterministic CI. Tests that don't break when unrelated governance files change.

## Approach

Replace `_build_real_graph()` (which reads disk) with a **fixture graph** built
from `UnifiedGraph()` + programmatic `ConceptNode` additions. The fixture graph
has a known, fixed set of nodes — enough to exercise diff logic without depending
on live data.

**Components:**
- `tests/context/test_diff_integration.py` — modify (replace `_build_real_graph`)

**What stays the same:**
- `diff_graphs` is still called with real `UnifiedGraph` instances (not mocks)
- `ConceptNode` objects are real Pydantic models
- All 5 test cases preserved with same intent

## Examples

### Fixture graph (replaces _build_real_graph)

```python
def _build_fixture_graph(self) -> UnifiedGraph:
    """Build a deterministic graph for diff testing."""
    graph = UnifiedGraph()
    graph.add_concept(ConceptNode(
        id="mod-alpha",
        type="module",
        content="Alpha module",
        created="2026-01-01",
        metadata={"code_imports": ["config"], "code_exports": ["alpha_func"]},
    ))
    graph.add_concept(ConceptNode(
        id="mod-beta",
        type="module",
        content="Beta module",
        created="2026-01-01",
        metadata={"code_imports": [], "code_exports": []},
    ))
    graph.add_concept(ConceptNode(
        id="PAT-001",
        type="pattern",
        content="Test pattern one",
        created="2026-01-01",
    ))
    # ~5-8 nodes total — enough to test diff, not enough to be fragile
    return graph
```

### Test adaptation (modify metadata test)

```python
def test_detect_modified_module_metadata(self) -> None:
    old_graph = self._build_fixture_graph()
    new_graph = self._build_fixture_graph()

    mod_node = new_graph.get_concept("mod-alpha")
    assert mod_node is not None

    modified = ConceptNode(
        id=mod_node.id, type=mod_node.type, content=mod_node.content,
        created=mod_node.created, source_file=mod_node.source_file,
        metadata={**mod_node.metadata, "code_imports": ["config", "new-dep"]},
    )
    new_graph.add_concept(modified)

    diff = diff_graphs(old_graph, new_graph)
    mod_changes = [c for c in diff.node_changes if c.node_id == "mod-alpha"]
    assert len(mod_changes) == 1
    assert mod_changes[0].change_type == "modified"
```

### Node count test → remove

The "sufficient nodes" test (`>= 300`) validated the builder, not diff. Remove it.
If builder coverage is needed, that belongs in a separate test file.

## Acceptance Criteria

**MUST:**
- All 5 tests pass without reading live `.raise/` files
- Tests exercise real `diff_graphs` with real `UnifiedGraph` and `ConceptNode`
- No test depends on current codebase state
- All other tests still pass

**MUST NOT:**
- Mock `diff_graphs` or `UnifiedGraph` internals
- Add dependencies on external fixtures/files

## Relevant Patterns

- **PAT-169:** Integration tests must not depend on Path.cwd() — use deterministic roots
- **PAT-202:** Templates-as-contract — tests should validate contracts, not live state
