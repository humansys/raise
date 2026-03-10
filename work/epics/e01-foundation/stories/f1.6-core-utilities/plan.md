# Implementation Plan: F1.6 Core Utilities

## Overview
- **Feature:** F1.6 Core Utilities
- **Story Points:** 3 SP
- **Feature Size:** S
- **Created:** 2026-01-31

## Scope

Subprocess wrappers for external tools used by raise-cli:
- **git** — version control operations
- **ast-grep** — AST-based code search
- **ripgrep (rg)** — fast text search

Each wrapper:
- Checks tool availability
- Raises `DependencyError` if missing
- Provides typed interface for common operations
- Returns structured results (not raw strings)

## Tasks

### Task 1: Tool Runner Base + Git Wrapper
- **Description:** Create `core/tools.py` with base runner and git wrapper
- **Files:** `src/rai_cli/core/tools.py`
- **Verification:** `pytest tests/core/test_tools.py -k git`
- **Size:** S
- **Dependencies:** None

### Task 2: ast-grep and ripgrep Wrappers
- **Description:** Add sg and rg wrappers following git pattern
- **Files:** `src/rai_cli/core/tools.py`
- **Verification:** `pytest tests/core/test_tools.py`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Tests + Quality Checks
- **Description:** Complete test coverage, run all quality checks
- **Files:** `tests/core/test_tools.py`
- **Verification:** `pytest --cov=src/rai_cli/core --cov-fail-under=90 && ruff check . && pyright src/`
- **Size:** XS
- **Dependencies:** Task 2

## Execution Order
1. Task 1 (foundation)
2. Task 2 (builds on 1)
3. Task 3 (verification)

## API Design

```python
# Check tool availability
def check_tool(name: str) -> bool: ...

# Git operations
def git_status() -> GitStatus: ...
def git_diff(staged: bool = False) -> str: ...
def git_root() -> Path: ...

# Search operations
def rg_search(pattern: str, path: Path, glob: str | None = None) -> list[Match]: ...
def sg_search(pattern: str, path: Path, lang: str | None = None) -> list[Match]: ...
```

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | XS | -- | |
