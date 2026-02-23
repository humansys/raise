---
story_id: "S211.1"
title: "Protocol contracts"
size: "S"
tasks: 3
derived_from: "design.md § Target Interfaces"
created: "2026-02-22"
---

# Implementation Plan: Protocol Contracts

## Overview
- **Story:** S211.1
- **Size:** S (3 tasks)
- **Derived from:** design.md § Target Interfaces
- **Patterns:** PAT-E-363 (Protocol > ABC), PAT-F-007 (Pydantic v2 frozen config)

## Tasks

### Task 1: Adapter boundary models

**Objective:** Create `src/rai_cli/adapters/models.py` with all Pydantic models and CoreArtifactType StrEnum.

**RED — Write Failing Test:**
- **File:** `tests/adapters/test_models.py`
- **Tests:**
  - `test_core_artifact_type_values` — all 9 core types exist as StrEnum members
  - `test_artifact_locator_validates` — construct from dict, required fields enforced
  - `test_issue_spec_defaults` — defaults for optional fields (issue_type="Task", labels=[], etc.)
  - `test_issue_ref_required_key` — key is required, url defaults to ""
  - `test_publish_result_roundtrip` — dict → model → dict roundtrip
  - `test_backend_health_roundtrip` — dict → model → dict roundtrip

```python
def test_core_artifact_type_values():
    assert CoreArtifactType.BACKLOG == "backlog"
    assert CoreArtifactType.ADR == "adr"
    assert len(CoreArtifactType) == 9

def test_artifact_locator_validates():
    loc = ArtifactLocator(path="governance/backlog.md", artifact_type="backlog")
    assert loc.path == "governance/backlog.md"
    assert loc.artifact_type == "backlog"

def test_issue_spec_defaults():
    spec = IssueSpec(summary="Fix login bug")
    assert spec.issue_type == "Task"
    assert spec.labels == []
    assert spec.description == ""
```

**GREEN — Implement:**
- **File:** `src/rai_cli/adapters/models.py`
- CoreArtifactType(StrEnum) — 9 members
- ArtifactLocator(BaseModel) — path, artifact_type, metadata
- IssueSpec(BaseModel) — summary, description, issue_type, labels, metadata
- IssueRef(BaseModel) — key, url, metadata
- PublishResult(BaseModel) — success, url, message
- BackendHealth(BaseModel) — status, message, metadata

**Verification:**
```bash
pytest tests/adapters/test_models.py -v
```

**Size:** S
**Dependencies:** None
**AC Reference:** Scenario "Shared Pydantic models at adapter boundary" from story.md

---

### Task 2: Protocol contracts

**Objective:** Create `src/rai_cli/adapters/protocols.py` with 5 `@runtime_checkable` Protocol classes.

**RED — Write Failing Test:**
- **File:** `tests/adapters/test_protocols.py`
- **Tests:**
  - `test_pm_adapter_is_runtime_checkable` — isinstance check with a conforming stub
  - `test_governance_schema_provider_is_runtime_checkable` — same
  - `test_governance_parser_is_runtime_checkable` — same
  - `test_documentation_target_is_runtime_checkable` — same
  - `test_knowledge_graph_backend_is_runtime_checkable` — same
  - `test_pm_adapter_rejects_non_conforming` — class missing methods fails isinstance
  - `test_governance_parser_returns_graph_node_type` — type annotation check via get_type_hints

```python
def test_pm_adapter_is_runtime_checkable():
    class StubPM:
        def create_issue(self, project_key, issue): ...
        def get_issue(self, ref): ...
        def update_issue(self, ref, fields): ...
        def transition_issue(self, ref, transition): ...
    assert isinstance(StubPM(), ProjectManagementAdapter)

def test_pm_adapter_rejects_non_conforming():
    class Incomplete:
        def create_issue(self, project_key, issue): ...
    assert not isinstance(Incomplete(), ProjectManagementAdapter)
```

**GREEN — Implement:**
- **File:** `src/rai_cli/adapters/protocols.py`
- ProjectManagementAdapter(Protocol) — 4 methods
- GovernanceSchemaProvider(Protocol) — 2 methods
- GovernanceParser(Protocol) — 2 methods
- DocumentationTarget(Protocol) — 2 methods
- KnowledgeGraphBackend(Protocol) — 3 methods
- All `@runtime_checkable`
- `TYPE_CHECKING` guard for `UnifiedGraph` import

**Verification:**
```bash
pytest tests/adapters/test_protocols.py -v
```

**Size:** S
**Dependencies:** Task 1 (models imported by protocols)
**AC Reference:** Scenarios "Import and use PM adapter protocol" + "Governance schema and parser protocols" from story.md

---

### Task 3: Public API + integration verification

**Objective:** Create `__init__.py` with re-exports. Verify pyright strict, full test suite, isinstance roundtrips.

**RED — Write Failing Test:**
- **File:** `tests/adapters/test_init.py`
- **Tests:**
  - `test_public_api_exports_all_protocols` — import from `rai_cli.adapters`
  - `test_public_api_exports_all_models` — import from `rai_cli.adapters`

```python
def test_public_api_exports_all_protocols():
    from rai_cli.adapters import (
        ProjectManagementAdapter,
        GovernanceSchemaProvider,
        GovernanceParser,
        DocumentationTarget,
        KnowledgeGraphBackend,
    )
    # All are Protocol classes
    assert hasattr(ProjectManagementAdapter, '__protocol_attrs__')

def test_public_api_exports_all_models():
    from rai_cli.adapters import (
        ArtifactLocator, BackendHealth, CoreArtifactType,
        IssueRef, IssueSpec, PublishResult,
    )
    assert issubclass(ArtifactLocator, BaseModel)
```

**GREEN — Implement:**
- **File:** `src/rai_cli/adapters/__init__.py`
- Re-export all 5 Protocols + 6 models
- `__all__` list

**Verification:**
```bash
pytest tests/adapters/ -v
pyright --project . src/rai_cli/adapters/
ruff check src/rai_cli/adapters/
pytest --tb=short  # full suite — zero regression
```

**Size:** XS
**Dependencies:** Task 1, Task 2
**AC Reference:** All scenarios (integration gate)

## Execution Order

1. Task 1 — models (leaf, no deps)
2. Task 2 — protocols (needs models)
3. Task 3 — __init__ + integration gate (needs both)

Sequential — each task builds on the previous.

## Traceability

| AC Scenario | Task(s) | Design § |
|-------------|---------|----------|
| "Shared Pydantic models at adapter boundary" | T1 | Target Interfaces → models.py |
| "Import and use PM adapter protocol" | T2, T3 | Target Interfaces → protocols.py |
| "Governance schema and parser protocols" | T2, T3 | Target Interfaces → protocols.py |

## Risks

- **pyright + TYPE_CHECKING for UnifiedGraph:** Protocol method using forward ref under TYPE_CHECKING might confuse pyright. Mitigation: test with `pyright --project .` in Task 3 before committing.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 — models | S | -- | |
| 2 — protocols | S | -- | |
| 3 — init + integration | XS | -- | |
