---
story_id: "S211.1"
title: "Protocol contracts"
epic_ref: "RAISE-211"
size: "S"
status: "draft"
created: "2026-02-22"
---

# Story: Protocol contracts

## User Story
As a raise-cli extension developer,
I want typed Protocol contracts for PM, Governance, and Documentation adapters,
so that I can implement adapters with clear interfaces and static type checking.

## Acceptance Criteria

### Scenario: Import and use PM adapter protocol
```gherkin
Given a class implementing ProjectManagementAdapter
When I pass it where ProjectManagementAdapter is expected
Then pyright validates the structural subtype with zero errors
And isinstance() checks pass at runtime (runtime_checkable)
```

### Scenario: Governance schema and parser protocols
```gherkin
Given GovernanceSchemaProvider and GovernanceParser protocols
When a built-in or third-party class implements them
Then locate() returns ArtifactLocator instances
And parse() returns list[GraphNode] (not raw ConceptNode)
```

### Scenario: Shared Pydantic models at adapter boundary
```gherkin
Given IssueSpec, IssueRef, ArtifactLocator, ArtifactType, PublishResult models
When constructing from dict or kwargs
Then Pydantic validates all fields
And serialization roundtrips cleanly
```

## Examples (Specification by Example)

| Protocol | Method | Input | Output |
|----------|--------|-------|--------|
| ProjectManagementAdapter | create_issue | project_key="PROJ", IssueSpec(...) | IssueRef(key="PROJ-1", url=...) |
| GovernanceSchemaProvider | list_artifact_types | — | [ArtifactType.BACKLOG, ArtifactType.ADR, ...] |
| GovernanceSchemaProvider | locate | ArtifactType.BACKLOG | [ArtifactLocator(path=..., artifact_type=...)] |
| GovernanceParser | can_parse | ArtifactLocator(artifact_type=BACKLOG) | True |
| GovernanceParser | parse | ArtifactLocator(...) | list[GraphNode] |
| DocumentationTarget | publish | doc_type="architecture", content="...", {} | PublishResult(url=..., success=True) |
| KnowledgeGraphBackend | health | — | BackendHealth(status="healthy", ...) |

## Notes
- Protocols defined in `src/rai_cli/adapters/protocols.py` (new module)
- Shared models in `src/rai_cli/adapters/models.py` (new module)
- `adapters/__init__.py` exports all public API
- S211.0 validated `Pydantic + __init_subclass__` works cleanly (PAT-E-406)
- Epic design.md lines 108-145 define the target contract signatures
- KnowledgeGraphBackend included here (from ADR-036) — pure Protocol, no implementation yet
