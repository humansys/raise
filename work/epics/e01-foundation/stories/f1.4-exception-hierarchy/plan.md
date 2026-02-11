# Implementation Plan: F1.4 Exception Hierarchy

## Overview
- **Feature:** F1.4
- **Stories:** Exception Hierarchy (from E1 backlog)
- **Total Estimate:** 3 SP (~3h)
- **Created:** 2026-01-31

## Tasks

### Task 1: Create Exception Module
- **Description:** Implement `src/rai_cli/exceptions.py` with complete exception hierarchy per design §4.1
- **Files:** `src/rai_cli/exceptions.py` (create)
- **Verification:** `pyright --strict src/rai_cli/exceptions.py && ruff check src/rai_cli/exceptions.py`
- **Estimate:** 30m
- **Dependencies:** None

**Exceptions to implement:**
- `RaiseError` (base, exit_code=1, error_code="E000")
- `ConfigurationError` (exit_code=2, E001)
- `KataNotFoundError` (exit_code=3, E002)
- `GateNotFoundError` (exit_code=3, E003)
- `ArtifactNotFoundError` (exit_code=4, E004)
- `DependencyError` (exit_code=5, E005)
- `StateError` (exit_code=6, E006)
- `ValidationError` (exit_code=7, E007)
- `GateFailedError` (exit_code=10, E010)

### Task 2: Create Error Handler
- **Description:** Implement `src/rai_cli/cli/error_handler.py` with Rich formatting per design §4.3
- **Files:** `src/rai_cli/cli/error_handler.py` (create)
- **Verification:** `pyright --strict src/rai_cli/cli/error_handler.py && ruff check src/rai_cli/cli/error_handler.py`
- **Estimate:** 30m
- **Dependencies:** Task 1

**Features:**
- Panel display with error code title
- Details section (key-value pairs)
- Hint section (cyan text)
- JSON output mode for `--format json`

### Task 3: Integrate with CLI Main
- **Description:** Wire error handler into CLI app with try/except around command execution
- **Files:** `src/rai_cli/cli/main.py` (modify)
- **Verification:** `rai --help` still works, manual error test
- **Estimate:** 20m
- **Dependencies:** Task 2

### Task 4: Unit Tests for Exceptions
- **Description:** Test exception hierarchy, exit codes, error codes, message formatting
- **Files:** `tests/unit/test_exceptions.py` (create)
- **Verification:** `pytest tests/unit/test_exceptions.py -v`
- **Estimate:** 30m
- **Dependencies:** Task 1

### Task 5: Unit Tests for Error Handler
- **Description:** Test Rich output formatting, JSON mode, details/hints rendering
- **Files:** `tests/unit/cli/test_error_handler.py` (create)
- **Verification:** `pytest tests/unit/cli/test_error_handler.py -v`
- **Estimate:** 30m
- **Dependencies:** Task 2

### Task 6: Integration Test
- **Description:** Test end-to-end error handling through CLI
- **Files:** `tests/integration/test_cli_errors.py` (create)
- **Verification:** `pytest tests/integration/test_cli_errors.py -v`
- **Estimate:** 20m
- **Dependencies:** Task 3

### Task 7: Export from Package
- **Description:** Update `__init__.py` files to export exceptions publicly
- **Files:** `src/rai_cli/__init__.py` (modify)
- **Verification:** `python -c "from raise_cli import RaiseError"`
- **Estimate:** 10m
- **Dependencies:** Task 1

## Execution Order

1. Task 1 (exception module - foundation)
2. Task 4 (unit tests for exceptions - TDD)
3. Task 2 (error handler - depends on 1)
4. Task 5 (unit tests for error handler - TDD)
5. Task 3 (CLI integration - depends on 2)
6. Task 7 (exports - finalization)
7. Task 6 (integration tests - end-to-end)

## Risks

- **Rich Console mocking:** May need careful mocking for output tests
  - *Mitigation:* Use `io.StringIO` capture or Rich's `Console(file=...)` pattern
- **Typer error handling:** Need to understand Typer's exception propagation
  - *Mitigation:* Research Typer patterns, test incrementally

## Definition of Done

- [ ] All exceptions per design §4.1 implemented
- [ ] Error handler with Rich output per design §4.3
- [ ] Exit codes match design §4.2 table
- [ ] JSON output mode works with `--format json`
- [ ] Unit tests >90% coverage on new code
- [ ] Integration test verifies exit codes
- [ ] `ruff check` and `pyright --strict` pass
- [ ] Exceptions exported from package root
