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
so that my adapter can define new node types with custom typed fields without modifying raise-core code.

## Acceptance Criteria

### Scenario: Core node types are registered on import
```gherkin
Given the rai_cli.context.models module is imported
When I call GraphNode.registered_types()
Then all 18 core node types are in the registry
And each maps to its specific subclass (e.g., "epic" → EpicNode)
```

### Scenario: Plugin defines a new node type with custom fields
```gherkin
Given a plugin defines:
  class JiraSprintNode(GraphNode, node_type="jira.sprint"):
      sprint_id: str
      board_id: str
When that module is imported
Then "jira.sprint" appears in GraphNode.registered_types()
And GraphNode.resolve("jira.sprint") returns JiraSprintNode
```

### Scenario: Auto-default type field
```gherkin
Given I create EpicNode(id="E1", content="...", created="...")
When I inspect node.type
Then it equals "epic" (set automatically, not passed explicitly)
And model_dump() includes type="epic"
```

### Scenario: Backward compatibility via alias
```gherkin
Given existing code uses ConceptNode(id="X", type="epic", ...)
When it creates and uses the node
Then all existing tests continue to pass unchanged
```

### Scenario: Graceful fallback for unknown types on load
```gherkin
Given a serialized graph contains a node with type="jira.sprint"
And the jira plugin is NOT installed
When the graph is loaded
Then a GraphNode (base) is returned with all data preserved
And a warning is logged suggesting "rai memory build"
```

### Scenario: EdgeType is open for plugins
```gherkin
Given a plugin creates GraphEdge(type="jira.blocks", source="A", target="B")
When the edge is added to a graph
Then it persists and loads without error
```

## Examples (Specification by Example)

| Input | Expected |
|-------|----------|
| `EpicNode(id="E1", content="...", created="...")` | Instance with type="epic" (auto) |
| `GraphNode.resolve("epic")` | Returns `EpicNode` class |
| `GraphNode.resolve("jira.sprint")` (plugin loaded) | Returns `JiraSprintNode` class |
| `GraphNode.resolve("unknown")` | Raises `KeyError` |
| `GraphNode.registered_types()` | Dict with 18+ entries |
| `ConceptNode(id="X", type="epic", ...)` | Valid GraphNode (alias) |
| Deserialize unknown type from JSON | GraphNode base + warning |

## Notes

### Scope
**In Scope:**
- GraphNode base class with `__init_subclass__` auto-registration
- `model_validator` for auto-default type field
- 18 core node type subclasses (documented as extension points)
- EdgeType → str + CoreEdgeTypes constants
- GraphEdge (renamed from ConceptEdge, alias kept)
- ConceptNode/ConceptEdge backward compat aliases
- UnifiedGraph deserialization with registry lookup + graceful fallback
- All 1610 existing tests pass unchanged (via aliases)

**Out of Scope:**
- Protocol contracts (S211.1)
- Entry points registration (S211.2)
- Builder refactor (S211.3)

### Design References
- Epic design: `work/epics/raise-211-adapter-foundation/design.md` § Key Contracts
- Research: pytest/Airflow/Kedro C+E+D pattern
- Framing: Empty subclasses are documented extension points, not complexity — the codebase IS the portfolio
