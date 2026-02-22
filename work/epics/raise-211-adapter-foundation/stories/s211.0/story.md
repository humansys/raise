---
story_id: "S211.0"
title: "GraphNode class hierarchy with auto-registration"
epic_ref: "RAISE-211"
size: "M"
status: "draft"
created: "2026-02-22"
---

# Story: GraphNode class hierarchy with auto-registration

## User Story
As a raise-cli plugin developer,
I want graph node types to be an open class hierarchy with auto-registration,
so that my adapter can define new node types without modifying raise-core code.

## Acceptance Criteria

### Scenario: Core node types are registered on import
```gherkin
Given the rai_cli.context.models module is imported
When I call GraphNode.registered_types()
Then all 18 core node types are in the registry
And each maps to its specific subclass (e.g., "epic" → EpicNode)
```

### Scenario: Plugin defines a new node type
```gherkin
Given a plugin defines `class JiraSprintNode(GraphNode, node_type="jira.sprint")`
When that module is imported
Then "jira.sprint" appears in GraphNode.registered_types()
And GraphNode.resolve("jira.sprint") returns JiraSprintNode
```

### Scenario: Backward compatibility via alias
```gherkin
Given existing code uses `from rai_cli.context.models import ConceptNode`
When it creates ConceptNode(id="X", type="epic", ...)
Then the instance is a valid GraphNode
And all existing tests continue to pass
```

### Scenario: Graph serialization roundtrip
```gherkin
Given a UnifiedGraph with mixed node types (core + plugin)
When I call graph.save(path) then graph.load(path)
Then all nodes are deserialized to their correct subclass
And node_type attributes are preserved
```

### Scenario: EdgeType is open for plugins
```gherkin
Given a plugin creates GraphEdge(type="jira.blocks", ...)
When the edge is added to a graph
Then it persists and loads without error
And core edge types still work via CoreEdgeTypes constants
```

## Examples (Specification by Example)

| Input | Action | Expected Output |
|-------|--------|----------------|
| `GraphNode.resolve("epic")` | Resolve type | Returns `EpicNode` class |
| `GraphNode.resolve("jira.sprint")` | Resolve plugin type | Returns `JiraSprintNode` class |
| `GraphNode.resolve("nonexistent")` | Resolve unknown | Raises `KeyError` |
| `GraphNode.registered_types()` | List all | Dict with 18+ entries |
| `EpicNode(id="E1", content="...", created="...")` | Create typed node | Instance with `__node_type__ == "epic"` |
| `ConceptNode(id="X", content="...", type="epic", created="...")` | Backward compat | Valid GraphNode instance |

## Notes

### Scope
**In Scope:**
- GraphNode base class with `__init_subclass__` auto-registration
- 18 core node type subclasses (one per current Literal value)
- EdgeType → str + CoreEdgeTypes constants
- GraphEdge (renamed from ConceptEdge, alias kept)
- ConceptNode/ConceptEdge backward compat aliases
- UnifiedGraph updated to accept GraphNode
- Serialization roundtrip with class hierarchy
- All 1610 existing tests pass

**Out of Scope:**
- Protocol contracts (S211.1)
- Entry points registration (S211.2)
- Builder refactor (S211.3)

### Design References
- Epic design: `work/epics/raise-211-adapter-foundation/design.md` § Key Contracts → GraphNode Base
- Pattern precedent: `CodeAnalyzer` Protocol in `context/analyzers/protocol.py`
- Research: pytest/Airflow/Kedro C+E+D pattern (session decision)
- Backward compat strategy: ConceptNode alias, rebuild on upgrade
