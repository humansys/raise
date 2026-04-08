---
title: Create a Custom Adapter
description: How to create a RaiSE adapter — implement a Protocol contract, register via entry points, and validate.
---

Adapters connect RaiSE to external services. They implement Python Protocol contracts and are discovered via entry points.

## Protocol Contracts

RaiSE defines two primary adapter protocols in `rai_cli.adapters.protocols`:

**ProjectManagementAdapter** — for issue trackers:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ProjectManagementAdapter(Protocol):
    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef: ...
    def get_issue(self, key: str) -> IssueDetail: ...
    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef: ...
    def transition_issue(self, key: str, status: str) -> IssueRef: ...
    def search(self, query: str, limit: int = 50) -> list[IssueSummary]: ...
    def health(self) -> AdapterHealth: ...
```

**DocumentationTarget** — for docs platforms:

```python
@runtime_checkable
class DocumentationTarget(Protocol):
    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool: ...
    def publish(self, doc_type: str, content: str, metadata: dict[str, Any]) -> PublishResult: ...
    def get_page(self, identifier: str) -> PageContent: ...
    def search(self, query: str, limit: int = 10) -> list[PageSummary]: ...
    def health(self) -> AdapterHealth: ...
```

Both are `@runtime_checkable`, so RaiSE verifies compliance with `isinstance()`.

## Async-First Architecture

Concrete adapters implement the async variants (`AsyncProjectManagementAdapter`, `AsyncDocumentationTarget`). The CLI consumes sync wrappers:

```python
from rai_cli.adapters.sync import SyncPMAdapter

class MyTrackerAsync:
    async def create_issue(self, project_key, issue):
        # Your async implementation
        ...

# CLI consumption
adapter = SyncPMAdapter(MyTrackerAsync())
```

## Entry Point Registration

Register your adapter in `pyproject.toml`:

```toml
[project.entry-points."rai.adapters.pm"]
my-tracker = "my_package.adapter:MyTrackerAdapter"

[project.entry-points."rai.docs.targets"]
my-docs = "my_package.docs:MyDocsTarget"
```

The entry point group names are stable contracts:
- `rai.adapters.pm` — project management
- `rai.docs.targets` — documentation
- `rai.governance.schemas` — governance schemas
- `rai.governance.parsers` — governance parsers
- `rai.graph.backends` — graph storage

## Validation

After registration, verify your adapter:

```bash
# List all discovered adapters
rai adapter list

# Check Protocol compliance
rai adapter check

# Validate declarative YAML config
rai adapter validate .raise/adapters/my-tracker.yaml
```

`rai adapter check` loads every registered entry point and runs `isinstance()` against the Protocol contract. Failures show which methods are missing.
