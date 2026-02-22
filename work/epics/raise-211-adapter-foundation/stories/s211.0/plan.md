# Implementation Plan: GraphNode class hierarchy with auto-registration

## Overview
- **Story:** S211.0
- **Size:** M
- **Tasks:** 5
- **Derived from:** design.md § Target Interfaces
- **Created:** 2026-02-22

## Tasks

### Task 1: GraphNode base class with auto-registration

**Objective:** Implement the GraphNode base with `__init_subclass__` auto-registration, `model_validator` for auto-default type, and class methods `resolve()` / `registered_types()`.

**RED — Write Failing Test:**
- **File:** `tests/context/test_models.py`
- **Test functions:**
  - `test_graphnode_subclass_registers_type` — define a test subclass, verify it appears in registry
  - `test_graphnode_resolve_returns_class` — resolve("test_type") returns the test subclass
  - `test_graphnode_resolve_unknown_raises` — resolve("nonexistent") raises KeyError
  - `test_graphnode_subclass_auto_sets_type` — create subclass instance without type param, verify type is auto-set
  - `test_graphnode_model_dump_includes_type` — model_dump() includes the auto-set type
  - `test_graphnode_token_estimate` — verify token_estimate property works on base
- **Setup:** Define `class TestNode(GraphNode, node_type="test_type"): ...` in test
- **Assertion:** `GraphNode.registered_types()["test_type"] is TestNode`, `TestNode(id="T1", content="x", created="now").type == "test_type"`

```python
def test_graphnode_subclass_registers_type():
    class TestNode(GraphNode, node_type="test_reg"):
        ...
    assert "test_reg" in GraphNode.registered_types()
    assert GraphNode.resolve("test_reg") is TestNode

def test_graphnode_subclass_auto_sets_type():
    class AutoNode(GraphNode, node_type="auto_test"):
        ...
    node = AutoNode(id="A1", content="hello", created="2026-01-01")
    assert node.type == "auto_test"
    assert node.model_dump()["type"] == "auto_test"
```

**GREEN — Implement:**
- **File:** `src/rai_cli/context/models.py`
- **Class:** `GraphNode(BaseModel)` with `__init_subclass__`, `_set_default_type` model_validator, `resolve()`, `registered_types()`, `token_estimate`

**Verification:**
```bash
pytest tests/context/test_models.py -v -k "graphnode"
```

**Size:** M
**Dependencies:** None
**AC Reference:** Scenarios "Core node types are registered on import", "Auto-default type field"

---

### Task 2: 18 core subclasses + backward compat aliases

**Objective:** Define 18 core node type subclasses with extension point docstrings. Add ConceptNode = GraphNode and NodeType = str aliases.

**RED — Write Failing Test:**
- **File:** `tests/context/test_models.py`
- **Test functions:**
  - `test_all_18_core_types_registered` — verify all 18 types in registry
  - `test_epic_node_creates_with_correct_type` — `EpicNode(id="E1", content="...", created="...").type == "epic"`
  - `test_conceptnode_alias_is_graphnode` — `ConceptNode is GraphNode`
  - `test_conceptnode_backward_compat` — `ConceptNode(id="X", type="epic", content="...", created="...")` works
  - `test_nodetype_is_str` — `NodeType is str`

```python
EXPECTED_CORE_TYPES = {
    "pattern", "calibration", "session", "principle", "requirement",
    "outcome", "project", "epic", "story", "skill", "decision",
    "guardrail", "term", "component", "module", "architecture",
    "bounded_context", "layer", "release",
}

def test_all_18_core_types_registered():
    registered = set(GraphNode.registered_types().keys())
    assert EXPECTED_CORE_TYPES.issubset(registered)

def test_conceptnode_backward_compat():
    node = ConceptNode(id="X", type="epic", content="test", created="2026-01-01")
    assert isinstance(node, GraphNode)
    assert node.type == "epic"
```

**GREEN — Implement:**
- **File:** `src/rai_cli/context/models.py`
- **Classes:** `PatternNode`, `CalibrationNode`, `SessionNode`, `PrincipleNode`, `RequirementNode`, `OutcomeNode`, `ProjectNode`, `EpicNode`, `StoryNode`, `SkillNode`, `DecisionNode`, `GuardrailNode`, `TermNode`, `ComponentNode`, `ModuleNode`, `ArchitectureNode`, `BoundedContextNode`, `LayerNode`, `ReleaseNode`
- **Aliases:** `ConceptNode = GraphNode`, `NodeType = str`

**Verification:**
```bash
pytest tests/context/test_models.py -v
```

**Size:** S
**Dependencies:** Task 1
**AC Reference:** Scenarios "Core node types are registered on import", "Backward compatibility via alias"

---

### Task 3: GraphEdge + CoreEdgeTypes + ConceptEdge alias

**Objective:** Rename/alias ConceptEdge to GraphEdge, open EdgeType to str, add CoreEdgeTypes constants.

**RED — Write Failing Test:**
- **File:** `tests/context/test_models.py`
- **Test functions:**
  - `test_graphedge_accepts_any_type` — `GraphEdge(type="jira.blocks", source="A", target="B")` works
  - `test_conceptedge_alias_is_graphedge` — `ConceptEdge is GraphEdge`
  - `test_core_edge_types_constants` — `CoreEdgeTypes.LEARNED_FROM == "learned_from"`
  - `test_edgetype_is_str` — `EdgeType is str`

```python
def test_graphedge_accepts_any_type():
    edge = GraphEdge(type="jira.blocks", source="A", target="B")
    assert edge.type == "jira.blocks"

def test_core_edge_types_constants():
    assert CoreEdgeTypes.LEARNED_FROM == "learned_from"
    assert CoreEdgeTypes.PART_OF == "part_of"
```

**GREEN — Implement:**
- **File:** `src/rai_cli/context/models.py`
- **Classes:** `GraphEdge(BaseModel)`, `CoreEdgeTypes`
- **Aliases:** `ConceptEdge = GraphEdge`, `EdgeType = str`

**Verification:**
```bash
pytest tests/context/test_models.py -v -k "edge"
```

**Size:** S
**Dependencies:** None (parallel with Task 1-2)
**AC Reference:** Scenario "EdgeType is open for plugins"

---

### Task 4: Deserialization with registry lookup + graceful fallback

**Objective:** Update UnifiedGraph to reconstruct correct GraphNode subclass from serialized data, with graceful fallback for unknown types.

**RED — Write Failing Test:**
- **File:** `tests/context/test_graph.py`
- **Test functions:**
  - `test_get_concept_returns_correct_subclass` — add EpicNode, get_concept returns EpicNode instance
  - `test_get_concepts_by_type_returns_subclasses` — filter returns correct subclass instances
  - `test_iter_concepts_yields_subclasses` — iteration yields correct subclasses
  - `test_save_load_roundtrip_preserves_subclass` — save → load → get_concept returns correct subclass
  - `test_unknown_type_falls_back_to_graphnode` — node with unregistered type loads as GraphNode base

```python
def test_get_concept_returns_correct_subclass():
    graph = UnifiedGraph()
    node = EpicNode(id="E1", content="test", created="2026-01-01")
    graph.add_concept(node)
    retrieved = graph.get_concept("E1")
    assert isinstance(retrieved, EpicNode)
    assert retrieved.type == "epic"

def test_unknown_type_falls_back_to_graphnode(tmp_path, caplog):
    graph = UnifiedGraph()
    # Manually add a node with unknown type via NetworkX
    graph.graph.add_node("U1", type="jira.sprint", content="test", created="2026-01-01", metadata={})
    retrieved = graph.get_concept("U1")
    assert isinstance(retrieved, GraphNode)
    assert retrieved.type == "jira.sprint"
    assert "not registered" in caplog.text
```

**GREEN — Implement:**
- **File:** `src/rai_cli/context/graph.py`
- **Method:** `_reconstruct_node(self, node_id: str, data: dict) -> GraphNode` — new private helper
- **Modified:** `get_concept()`, `get_concepts_by_type()`, `iter_concepts()` — use `_reconstruct_node`
- **Integration:** All existing graph consumers get subclass instances transparently

**Verification:**
```bash
pytest tests/context/test_graph.py -v
```

**Size:** M
**Dependencies:** Task 1, Task 2
**AC Reference:** Scenarios "Graceful fallback for unknown types on load", "Auto-default type field"

---

### Task 5 (Final): Integration Verification

**Objective:** Validate the full test suite passes (1610 tests) and the story works end-to-end.

**Verification:**
```bash
# Full test suite — zero regressions
pytest --tb=short -q

# Type checking
pyright src/rai_cli/context/models.py src/rai_cli/context/graph.py

# Lint
ruff check src/rai_cli/context/models.py src/rai_cli/context/graph.py
```

**Size:** XS
**Dependencies:** All previous tasks

---

## Execution Order

1. **Task 1** — GraphNode base (foundation, everything depends on it)
2. **Task 3** — GraphEdge + CoreEdgeTypes (parallel with T1, no dependency)
3. **Task 2** — 18 subclasses + aliases (needs T1)
4. **Task 4** — Deserialization (needs T1 + T2)
5. **Task 5** — Integration verification (needs all)

## Traceability

| AC Scenario | Task(s) | Design § |
|-------------|---------|----------|
| "Core node types are registered on import" | T1, T2 | Target Interfaces → GraphNode Base + Subclasses |
| "Plugin defines a new node type with custom fields" | T1 | Target Interfaces → GraphNode.__init_subclass__ |
| "Auto-default type field" | T1 | Target Interfaces → model_validator |
| "Backward compatibility via alias" | T2 | Target Interfaces → ConceptNode = GraphNode |
| "Graceful fallback for unknown types on load" | T4 | Target Interfaces → Deserialization |
| "EdgeType is open for plugins" | T3 | Target Interfaces → GraphEdge + CoreEdgeTypes |

## Risks

- **Pydantic + `__init_subclass__` interaction:** Known friction area. Mitigated by testing early in T1 with isolated test subclass before touching production code.
- **Registry pollution in tests:** Test subclasses register globally. Mitigate with unique type names per test or registry cleanup fixture.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| T1: GraphNode base | M | — | |
| T2: 18 subclasses + aliases | S | — | |
| T3: GraphEdge + CoreEdgeTypes | S | — | |
| T4: Deserialization | M | — | |
| T5: Integration | XS | — | |
