---
story_id: "S211.2"
title: "Entry point registry"
size: "S"
tasks: 3
derived_from: "design.md § Target Interfaces"
created: "2026-02-22"
---

# Implementation Plan: Entry point registry

## Overview
- **Story:** S211.2
- **Size:** S
- **Tasks:** 3
- **Derived from:** design.md § Target Interfaces
- **Created:** 2026-02-22

## Tasks

### Task 1: registry.py — _discover + constants + public functions + tests

**Objective:** Create the full registry module with internal discovery, constants, and all 5 public functions. TDD with tests covering happy path, empty group, and broken entry point.

**RED — Write Failing Tests:**
- **File:** `tests/adapters/test_registry.py`
- **Tests:**
  - `test_discover_returns_empty_dict_for_unknown_group` — Given no packages register a group, When _discover(group) called, Then returns `{}`
  - `test_discover_loads_entry_point_by_name` — Given a mocked entry point in group, When _discover(group) called, Then returns `{name: loaded_class}`
  - `test_discover_skips_broken_entry_point_with_warning` — Given entry point that raises on load(), When _discover(group) called, Then logs warning and returns dict without the broken one
  - `test_get_pm_adapters_delegates_to_discover` — Verify `get_pm_adapters()` calls `_discover(EP_PM_ADAPTERS)`
  - `test_get_governance_schemas_delegates` — Same for schemas
  - `test_get_governance_parsers_delegates` — Same for parsers
  - `test_get_doc_targets_delegates` — Same for doc targets
  - `test_get_graph_backends_delegates` — Same for graph backends
  - `test_constants_are_correct_group_strings` — Verify all 5 EP_* constants match expected group strings

```python
# Test sketch — mock importlib.metadata.entry_points
from unittest.mock import patch, MagicMock

def test_discover_returns_empty_dict_for_unknown_group():
    from rai_cli.adapters.registry import _discover
    result = _discover("rai.nonexistent.group")
    assert result == {}

def test_discover_loads_entry_point_by_name():
    mock_ep = MagicMock()
    mock_ep.name = "test_adapter"
    mock_ep.load.return_value = type("FakeAdapter", (), {})
    with patch("rai_cli.adapters.registry.entry_points", return_value=[mock_ep]):
        from rai_cli.adapters.registry import _discover
        result = _discover("rai.adapters.pm")
    assert "test_adapter" in result

def test_discover_skips_broken_entry_point(caplog):
    good_ep = MagicMock(); good_ep.name = "good"; good_ep.load.return_value = type("Good", (), {})
    bad_ep = MagicMock(); bad_ep.name = "bad"; bad_ep.load.side_effect = ImportError("missing dep")
    with patch("rai_cli.adapters.registry.entry_points", return_value=[good_ep, bad_ep]):
        from rai_cli.adapters.registry import _discover
        result = _discover("rai.adapters.pm")
    assert "good" in result
    assert "bad" not in result
    assert "bad" in caplog.text
```

**GREEN — Implement:**
- **File:** `src/rai_cli/adapters/registry.py`
- **Contents:** 5 EP_* constants, `_discover(group: str) -> dict[str, type]`, 5 public `get_*()` functions
- **Key:** `from importlib.metadata import entry_points`, try/except per ep.load(), `logging.warning()` on failure

**Verification:**
```bash
pytest tests/adapters/test_registry.py -v
pyright src/rai_cli/adapters/registry.py
ruff check src/rai_cli/adapters/registry.py
```

**Size:** S
**Dependencies:** None
**AC Reference:** Scenarios "Discover PM adapters", "No adapters registered", "Broken entry point handled gracefully"

---

### Task 2: Public API exports + downstream test fix

**Objective:** Export registry functions and constants from `adapters/__init__.py`. Update `test_init.py` hardcoded count (PAT-E-241).

**RED — Write Failing Test:**
- **File:** `tests/adapters/test_init.py`
- **Test:** Update `test_all_has_eleven_entries` → `test_all_has_expected_entries` with new count (11 existing + 5 functions + 5 constants = 21)
- **Add:** `test_import_registry_functions` — verify all 5 `get_*` functions importable from `rai_cli.adapters`

**GREEN — Implement:**
- **File:** `src/rai_cli/adapters/__init__.py`
- Add imports from `rai_cli.adapters.registry` (5 functions + 5 constants)
- Update `__all__` to include all 21 exports

**Verification:**
```bash
pytest tests/adapters/ -v
pytest tests/ --tb=short  # Full suite per PAT-E-241
```

**Size:** XS
**Dependencies:** T1
**AC Reference:** Scenario "Discover governance schemas" (verifies full public API surface)

---

### Task 3: Integration verification

**Objective:** Validate story works end-to-end — registry discovers nothing (no entry points registered yet), functions callable, no regressions.

**Verification:**
```bash
# All adapters tests
pytest tests/adapters/ -v

# Full test suite (zero regression)
pytest tests/ --tb=short

# Type + lint gates
pyright src/rai_cli/adapters/
ruff check src/rai_cli/adapters/
```

**Size:** XS
**Dependencies:** T1, T2

## Execution Order
1. T1 — registry.py + tests (foundation)
2. T2 — __init__.py exports + test fix (depends on T1)
3. T3 — Integration verification (final gate)

## Risks
- **pyright strict + `ep.load()` returns Any**: Mitigation — cast at `_discover` boundary with type comment
- **PAT-E-241 downstream breakage**: Mitigation — T2 explicitly runs full test suite

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| T1 | S | -- | |
| T2 | XS | -- | |
| T3 | XS | -- | |
