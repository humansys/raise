# RAISE-1060: Adapter Models Restructure — Design

## Problem
`raise_cli/adapters/models.py` mixes 4 concerns in one 213-line file: PM boundary
models, Docs boundary models, Governance schema models, and filesystem adapter
internals (BacklogItem). This violates adapter-vision.md §5 (adapters as shared
infrastructure with clear ownership) and makes it unclear where new models belong.

## Value
Clean separation by protocol concern. New adapter models (SpaceInfo for Confluence,
future Jira discovery models) have an obvious home. Filesystem internals don't pollute
the shared boundary contract.

## Approach

### Target structure
```
raise_cli/adapters/
  models/
    __init__.py       ← re-exports everything (backwards compat)
    pm.py             ← IssueSpec, IssueRef, IssueDetail, IssueSummary,
                        Comment, CommentRef, FailureDetail, BatchResult
    docs.py           ← PageContent, PageSummary, PublishResult, SpaceInfo (NEW)
    governance.py     ← CoreArtifactType, ArtifactLocator
    health.py         ← AdapterHealth
  filesystem_models.py ← BacklogItem, BacklogLink, BacklogComment (MOVED)
```

### Why this structure
- **Per-protocol modules** mirror the protocol split (PM, Docs, Governance)
- **health.py** is cross-cutting (used by all adapters) — own module
- **filesystem_models.py** at same level as filesystem.py — co-located internal models
- **__init__.py** re-exports all public names → zero breaking changes for 47+ import sites

### Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D1 | `models/` package, not separate top-level files | Preserves `from raise_cli.adapters.models import X` |
| D2 | `filesystem_models.py` not `models/filesystem.py` | These are NOT boundary models — they don't belong in the models package |
| D3 | Shared field descriptions stay in `pm.py` | Most descriptions are PM-specific; `_DESC_UPDATED_TS` used by docs too but that's fine — it's a string constant |
| D4 | `SpaceInfo` added in this story | Needed by RAISE-1051 S1051.1, natural to add while creating docs.py |

### Components affected

| File | Change |
|------|--------|
| `adapters/models.py` | DELETE — replaced by `models/` package |
| `adapters/models/__init__.py` | NEW — re-exports all public models |
| `adapters/models/pm.py` | NEW — PM boundary models |
| `adapters/models/docs.py` | NEW — Docs boundary models + SpaceInfo |
| `adapters/models/governance.py` | NEW — Governance schema models |
| `adapters/models/health.py` | NEW — AdapterHealth |
| `adapters/filesystem_models.py` | NEW — BacklogItem, BacklogLink, BacklogComment |
| `adapters/filesystem.py` | MODIFY — update import path |
| `adapters/__init__.py` | MODIFY — add SpaceInfo to exports |
| `tests/adapters/test_filesystem.py` | MODIFY — update import path |
| `tests/integration/conftest.py` | CHECK — may reference BacklogItem |

### SpaceInfo model

```python
class SpaceInfo(BaseModel):
    """Confluence space metadata from discovery."""
    key: str = Field(..., description="Space key (e.g., 'RaiSE1')")
    name: str = Field(..., description="Space display name")
    url: str = Field(default="", description="Web URL to the space")
    type: str = Field(default="global", description="Space type (global, personal)")
```

## Acceptance Criteria
- AC1: `from raise_cli.adapters.models import PageContent` works (re-export)
- AC2: `BacklogItem` NOT in `raise_cli.adapters.models.__all__` (was never there)
- AC3: `from raise_cli.adapters.filesystem_models import BacklogItem` works (3 consumers updated)
- AC4: `from raise_cli.adapters.models import SpaceInfo` works
- AC5: All tests pass, pyright clean, ruff clean
