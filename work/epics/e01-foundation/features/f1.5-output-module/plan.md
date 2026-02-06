# Implementation Plan: F1.5 Output Module

## Overview

- **Feature:** F1.5 Output Module
- **Design:** `work/features/f1.5-output-module/design.md`
- **Total Estimate:** 2-3 hours
- **Created:** 2026-01-31

## Tasks

### Task 1: OutputConsole Core Class

- **Description:** Create `OutputConsole` class with constructor and `print_message` method as foundation. Implement the three output formats (human/json/table) for simple messages.
- **Files:**
  - Create: `src/raise_cli/output/console.py`
  - Modify: `src/raise_cli/output/__init__.py`
- **Verification:** `pytest tests/output/test_console.py -v && ruff check src/raise_cli/output/`
- **Estimate:** 1h
- **Dependencies:** None

### Task 2: Success/Warning Methods

- **Description:** Add `print_success` and `print_warning` methods with styled output (checkmark/warning symbols, colors, optional details).
- **Files:**
  - Modify: `src/raise_cli/output/console.py`
  - Modify: `tests/output/test_console.py`
- **Verification:** `pytest tests/output/test_console.py -v`
- **Estimate:** 30min
- **Dependencies:** Task 1

### Task 3: Data and List Methods

- **Description:** Add `print_data` (single dict → tree/json/key-value) and `print_list` (list of dicts → bullets/json array/table) methods.
- **Files:**
  - Modify: `src/raise_cli/output/console.py`
  - Modify: `tests/output/test_console.py`
- **Verification:** `pytest tests/output/test_console.py -v`
- **Estimate:** 45min
- **Dependencies:** Task 1

### Task 4: Module-Level API & Exports

- **Description:** Add `get_console()`, `set_console()`, `configure_console()` singleton functions. Export public API from `raise_cli.output` and optionally from package root.
- **Files:**
  - Modify: `src/raise_cli/output/console.py`
  - Modify: `src/raise_cli/output/__init__.py`
  - Modify: `src/raise_cli/__init__.py` (optional export)
- **Verification:** `python -c "from raise_cli.output import get_console, OutputConsole, configure_console"` && `pytest tests/output/ -v`
- **Estimate:** 20min
- **Dependencies:** Task 1

### Task 5: Verbosity & Quiet Mode

- **Description:** Implement verbosity handling - when `verbosity=-1` (quiet mode), suppress all non-error output. Test integration with RaiseSettings.
- **Files:**
  - Modify: `src/raise_cli/output/console.py`
  - Create: `tests/output/test_verbosity.py`
- **Verification:** `pytest tests/output/test_verbosity.py -v`
- **Estimate:** 20min
- **Dependencies:** Task 4

### Task 6: Update Component Catalog

- **Description:** Document new components in `dev/components.md` following the established pattern.
- **Files:**
  - Modify: `dev/components.md`
- **Verification:** Visual review
- **Estimate:** 10min
- **Dependencies:** Tasks 1-5

## Execution Order

```
Task 1 (foundation)
    │
    ├──► Task 2 (success/warning)
    │
    ├──► Task 3 (data/list) ─────┐
    │                            │
    └──► Task 4 (module API) ────┼──► Task 5 (verbosity)
                                 │
                                 └──► Task 6 (docs)
```

**Linear execution:** 1 → 2 → 3 → 4 → 5 → 6

Tasks 2 and 3 could run in parallel after Task 1, but for clean git history we'll do them sequentially.

## Verification Summary

| Task | Command |
|------|---------|
| All | `pytest tests/output/ -v --cov=src/raise_cli/output --cov-fail-under=90` |
| Lint | `ruff check src/raise_cli/output/` |
| Types | `pyright src/raise_cli/output/` |
| Import | `python -c "from raise_cli.output import OutputConsole, get_console"` |

## Risks

| Risk | Mitigation |
|------|------------|
| Rich Table API unfamiliar | Refer to F1.4 error_handler for patterns |
| JSON output formatting edge cases | Test with nested dicts, empty lists |

## Commit Strategy

One commit per task with format:
```
feat(output): [Task description] (F1.5 Task N)

Co-Authored-By: Rai <rai@humansys.ai>
```

---

**Plan Version:** 1.0
**Ready for:** `/feature-implement`
