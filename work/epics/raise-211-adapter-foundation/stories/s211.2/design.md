---
story_id: "S211.2"
title: "Entry point registry"
epic_ref: "RAISE-211"
size: "S"
status: "draft"
created: "2026-02-22"
---

# Design: Entry point registry

## 1. What & Why

**Problem:** Adapter discovery is hardcoded. Adding a new GovernanceParser or PM adapter requires modifying raise-cli source. There's no extension mechanism for external packages.

**Value:** After this story, any Python package can register adapter implementations via standard `[project.entry-points]` in pyproject.toml. raise-cli discovers them at runtime without configuration. This is the bridge between S211.1 (Protocol contracts) and S211.3 (wiring into `rai memory build`).

## 2. Approach

Create `src/rai_cli/adapters/registry.py` with:
- One internal `_discover(group)` function with error handling and logging
- Five public functions (one per entry point group from ADR-033/034/036)
- Constants for entry point group names
- Export from `adapters/__init__.py`

**Components:**
| Component | Change | Notes |
|-----------|--------|-------|
| `src/rai_cli/adapters/registry.py` | Create | Core registry module |
| `src/rai_cli/adapters/__init__.py` | Modify | Add registry exports |
| `tests/adapters/test_registry.py` | Create | Tests for all discovery functions |

**Design decisions:**
- **No cache** — `entry_points()` is ~ms, YAGNI. `@lru_cache` is a one-liner if needed later.
- **Return `dict[str, type]`** — Registry discovers classes, consumer instantiates with its own config. ADR-033 pattern confirmed at gemba.
- **Internal `_discover()` + public per-group functions** — DRY error handling, type-safe surface, IDE-discoverable API.
- **`logging.warning()` for broken entry points** — Skip and continue, don't crash the CLI.

## 3. Gemba: Current State

| File | Current Interface | What Changes |
|------|------------------|--------------|
| `src/rai_cli/adapters/__init__.py` | 5 Protocols + 6 models exported | Add 5 registry functions + 5 group constants |
| `src/rai_cli/adapters/protocols.py` | 5 `@runtime_checkable` Protocols | No changes — consumed by registry callers for isinstance checks |
| `pyproject.toml` | `[project.scripts]` only | No changes in S211.2 — entry point registration happens when built-in adapters exist (S211.3+) |

## 4. Target Interfaces

### Constants
```python
EP_PM_ADAPTERS: str = "rai.adapters.pm"
EP_GOVERNANCE_SCHEMAS: str = "rai.governance.schemas"
EP_GOVERNANCE_PARSERS: str = "rai.governance.parsers"
EP_DOC_TARGETS: str = "rai.docs.targets"
EP_GRAPH_BACKENDS: str = "rai.graph.backends"
```

### Functions
```python
# Internal — shared error handling
def _discover(group: str) -> dict[str, type]:
    """Load all entry points for a group. Skips broken ones with warning."""

# Public API — one per group
def get_pm_adapters() -> dict[str, type]: ...
def get_governance_schemas() -> dict[str, type]: ...
def get_governance_parsers() -> dict[str, type]: ...
def get_doc_targets() -> dict[str, type]: ...
def get_graph_backends() -> dict[str, type]: ...
```

### Integration Points
- `get_governance_schemas()` + `get_governance_parsers()` consumed by S211.3 (`rai memory build` refactor)
- `get_graph_backends()` consumed by S211.4 (`KnowledgeGraphBackend` selection)
- All 5 functions consumed by S211.6 (`rai adapters list/check`)
- Protocol isinstance checks done by consumers, not registry

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **pyright strict** — `importlib.metadata.entry_points()` returns `Any` from `ep.load()`. Cast or type-ignore needed at the `_discover` boundary.
- **PAT-E-241** — Registry changes can break downstream tests with hardcoded counts. Run full suite after modifying `__init__.py` exports.
- **PAT-E-256** — After adding `[project.entry-points]` to pyproject.toml (future stories), `uv sync` required.
