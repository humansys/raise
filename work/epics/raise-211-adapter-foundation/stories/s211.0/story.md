---
story_id: "S211.0"
title: "Open NodeType/EdgeType"
epic_ref: "RAISE-211"
size: "S"
status: "draft"
created: "2026-02-22"
---

# Story: Open NodeType/EdgeType

## User Story
As a raise-cli plugin developer,
I want NodeType and EdgeType to accept any string value,
so that my adapter can produce graph nodes with custom types without modifying raise-core code.

## Acceptance Criteria

### Scenario: Core node types work via constants
```gherkin
Given the rai_cli.context.models module is imported
When I create ConceptNode(id="E1", type=CoreNodeTypes.EPIC, content="...", created="...")
Then the node has type == "epic"
And pyright reports no errors
```

### Scenario: Plugin uses custom node type
```gherkin
Given a plugin creates ConceptNode(id="JS1", type="jira.sprint", content="...", created="...")
When the node is added to a UnifiedGraph
Then the node persists and loads without error
And node.type == "jira.sprint"
```

### Scenario: All existing tests pass unchanged
```gherkin
Given the NodeType is changed from Literal to str
When I run the full test suite (1610 tests)
Then all tests pass without modification
```

### Scenario: Plugin uses custom edge type
```gherkin
Given a plugin creates ConceptEdge(type="jira.blocks", source="A", target="B")
When the edge is added to a graph
Then it persists and loads without error
```

## Examples (Specification by Example)

| Input | Expected |
|-------|----------|
| `ConceptNode(type="epic", ...)` | Valid, type=="epic" |
| `ConceptNode(type="jira.sprint", ...)` | Valid, type=="jira.sprint" |
| `ConceptNode(type=CoreNodeTypes.EPIC, ...)` | Valid, type=="epic" |
| `ConceptEdge(type="learned_from", ...)` | Valid |
| `ConceptEdge(type="jira.blocks", ...)` | Valid |
| `CoreNodeTypes.EPIC` | "epic" |
| `CoreEdgeTypes.PART_OF` | "part_of" |

## Notes

### Scope
**In Scope:**
- NodeType: Literal → str
- EdgeType: Literal → str
- CoreNodeTypes class with 18 constants
- CoreEdgeTypes class with 11 constants
- All 1610 existing tests pass unchanged

**Out of Scope:**
- Renaming ConceptNode → GraphNode (future)
- Class hierarchy / auto-registration (deferred — no current need)
- Protocol contracts (S211.1)
- Entry points (S211.2)

### Design References
- Epic design: `work/epics/raise-211-adapter-foundation/design.md` § Key Contracts → Open NodeType/EdgeType
- Research: Investigated pytest/Airflow/Kedro/HA/Celery patterns. Class hierarchy deferred — all 18 core types have identical shape, no per-type specialization needed today.
- Decision rationale: Pragmatic str + constants. Migrate to hierarchy when plugins need per-type fields (evidence-based trigger).
