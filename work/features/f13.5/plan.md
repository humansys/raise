# Implementation Plan: F13.5 Drift Detection

## Overview

- **Feature:** F13.5 Drift Detection
- **Story Points:** 1 SP (XS)
- **Feature Size:** XS
- **Created:** 2026-02-04
- **Epic:** E13 Discovery

## Concept

**Drift detection** identifies new or modified files that don't follow established patterns from the component baseline.

```
Baseline (validated components)     New/Modified Files
         ↓                                  ↓
    ┌─────────┐                      ┌─────────┐
    │ Symbol  │                      │ FooBar  │
    │ extract_│                      │ process │
    │ scan_   │                      │ weird_  │
    └─────────┘                      └─────────┘
         │                                  │
         └──────────┬───────────────────────┘
                    ↓
              Compare patterns
                    ↓
         ┌─────────────────────┐
         │ Drift Report        │
         │ - naming mismatch   │
         │ - location mismatch │
         │ - missing docstring │
         └─────────────────────┘
```

## Tasks

### Task 1: Create Drift Detection Module

- **Description:** Create `src/raise_cli/discovery/drift.py` with core detection logic
- **Files:**
  - `src/raise_cli/discovery/drift.py` (new)
  - `tests/discovery/test_drift.py` (new)
- **TDD Cycle:**
  - RED: Test `detect_drift()` returns drift warnings for non-conforming files
  - GREEN: Implement `DriftWarning` model and `detect_drift()` function
  - REFACTOR: Extract pattern matching helpers if needed
- **Verification:** `pytest tests/discovery/test_drift.py -v`
- **Size:** S
- **Dependencies:** None

**Key types:**
```python
class DriftWarning(BaseModel):
    file: str           # File with drift
    issue: str          # What's wrong
    severity: str       # "warning" | "error"
    suggestion: str     # How to fix

def detect_drift(
    baseline_components: list[dict],
    scanned_symbols: list[Symbol],
) -> list[DriftWarning]
```

**Detection rules (MVP):**
1. **Location drift:** New file in unexpected directory (e.g., model in `cli/`)
2. **Naming drift:** Class/function doesn't follow baseline naming patterns
3. **Missing docstring:** Public symbol without docstring (if baseline has them)

### Task 2: Add CLI Command

- **Description:** Add `raise discover drift` command that runs detection
- **Files:**
  - `src/raise_cli/cli/commands/discover.py` (modify)
  - `tests/cli/commands/test_discover.py` (modify)
- **TDD Cycle:**
  - RED: Test CLI command exits 0 with no drift, exits 1 with drift warnings
  - GREEN: Add `drift` subcommand to discover_app
  - REFACTOR: Ensure output formatting matches other commands
- **Verification:** `pytest tests/cli/commands/test_discover.py::test_drift* -v`
- **Size:** S
- **Dependencies:** Task 1

**CLI interface:**
```bash
# Check for drift against baseline
raise discover drift

# Check specific directory
raise discover drift src/new_module/

# Output formats
raise discover drift --output json
raise discover drift --output summary
```

### Task 3: Manual Integration Test

- **Description:** Validate drift detection works end-to-end
- **Verification:**
  1. Create a test file that violates naming conventions
  2. Run `raise discover drift`
  3. Verify warning is shown
  4. Delete test file
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order

1. **Task 1** (core logic) — Foundation
2. **Task 2** (CLI) — Depends on Task 1
3. **Task 3** (integration) — Final validation

## Risks

- **Pattern matching too strict:** Start with simple heuristics (location, prefix matching)
- **False positives:** MVP uses warnings only, not blocking

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | Core drift module |
| 2 | S | -- | CLI command |
| 3 | XS | -- | Integration test |

---

*Plan created: 2026-02-04*
