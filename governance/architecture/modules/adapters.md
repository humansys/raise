---
type: module
name: adapters
purpose: "Protocol contracts, boundary models, and entry point registry for raise-cli extensibility"
status: current
depends_on: [context]
depended_by: []
entry_points: []
public_api:
  - "ProjectManagementAdapter"
  - "GovernanceSchemaProvider"
  - "GovernanceParser"
  - "DocumentationTarget"
  - "KnowledgeGraphBackend"
  - "ArtifactLocator"
  - "BackendHealth"
  - "CoreArtifactType"
  - "IssueRef"
  - "IssueSpec"
  - "PublishResult"
  - "get_pm_adapters"
  - "get_governance_schemas"
  - "get_governance_parsers"
  - "get_doc_targets"
  - "get_graph_backends"
  - "EP_PM_ADAPTERS"
  - "EP_GOVERNANCE_SCHEMAS"
  - "EP_GOVERNANCE_PARSERS"
  - "EP_DOC_TARGETS"
  - "EP_GRAPH_BACKENDS"
components: 16
layer: leaf
domain: extensibility
constraints:
  - "MUST remain a leaf module — no runtime imports from context.graph (TYPE_CHECKING only)"
  - "MUST use runtime_checkable Protocols, not ABCs"
  - "MUST validate entry points are classes via inspect.isclass()"
---

# Module: adapters

Open-core extensibility boundary for raise-cli. Defines the Protocol contracts that external packages implement and the registry that discovers them at runtime via `importlib.metadata` entry points.

## Architecture

- **protocols.py** — 5 `@runtime_checkable` Protocol classes (ADR-033/034/036)
- **models.py** — 6 Pydantic boundary models shared between core and adapters
- **registry.py** — Entry point discovery: `_discover(group)` + 5 public `get_*()` functions

## Key Design Decisions

- Protocols over ABCs: structural typing, no inheritance required for community packages
- Registry returns `dict[str, type]`: discovers classes, consumer instantiates with its own config
- `_discover()` validates `inspect.isclass()` and logs warnings for broken/non-class entry points
- Leaf module: depends on `context.models.GraphNode` only, `UnifiedGraph` behind `TYPE_CHECKING`

## Entry Point Groups

| Group | Protocol | ADR |
|-------|----------|-----|
| `rai.adapters.pm` | `ProjectManagementAdapter` | ADR-033 |
| `rai.governance.schemas` | `GovernanceSchemaProvider` | ADR-034 |
| `rai.governance.parsers` | `GovernanceParser` | ADR-034 |
| `rai.docs.targets` | `DocumentationTarget` | ADR-034 |
| `rai.graph.backends` | `KnowledgeGraphBackend` | ADR-036 |
