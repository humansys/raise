# Implementation Plan: F8.1 Backlog Parser

## Overview

- **Feature:** F8.1 Backlog Parser
- **Epic:** E8 Work Tracking Graph
- **Story Points:** 2 SP
- **Feature Size:** S
- **Created:** 2026-02-02
- **Design:** `work/features/f8.1-backlog-parser/design.md`

## Tasks

### Task 1: Extend ConceptType enum

- **Description:** Add PROJECT and EPIC to ConceptType enum in models.py
- **Files:** `src/raise_cli/governance/models.py`
- **Verification:** `python -c "from raise_cli.governance.models import ConceptType; print(ConceptType.PROJECT, ConceptType.EPIC)"`
- **Size:** XS
- **Dependencies:** None

### Task 2: Create backlog parser module

- **Description:** Create `backlog.py` with `extract_project()` and `extract_epics()` functions following prd.py pattern. Include `normalize_status()` helper.
- **Files:**
  - `src/raise_cli/governance/parsers/backlog.py` (CREATE)
  - `src/raise_cli/governance/parsers/__init__.py` (MODIFY - add export)
- **Verification:** `python -c "from raise_cli.governance.parsers.backlog import extract_project, extract_epics; print('OK')"`
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Write unit tests

- **Description:** Create tests for backlog parser covering:
  - `extract_project()` with real backlog.md
  - `extract_epics()` returns all 9 epics
  - Status normalization (all variants)
  - Current focus extraction
  - Edge cases (missing file, malformed content)
- **Files:** `tests/governance/parsers/test_backlog.py` (CREATE)
- **Verification:** `pytest tests/governance/parsers/test_backlog.py -v --cov=src/raise_cli/governance/parsers/backlog --cov-fail-under=90`
- **Size:** S
- **Dependencies:** Task 2

### Task 4: Verify integration with existing tests

- **Description:** Run full test suite to ensure no regressions. Verify quality checks pass.
- **Files:** None (verification only)
- **Verification:** `pytest && ruff check src/ && pyright src/`
- **Size:** XS
- **Dependencies:** Task 3

## Execution Order

```
Task 1 (ConceptType enum) ← XS, foundation
    ↓
Task 2 (backlog.py) ← M, core implementation
    ↓
Task 3 (tests) ← S, validation
    ↓
Task 4 (integration check) ← XS, quality gate
```

**Linear execution** — each task depends on previous.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Regex doesn't match all table variants | Medium | Test against real backlog.md first |
| Status normalization misses edge cases | Low | Enumerate all known statuses in test |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1. ConceptType enum | XS | 5 min | — | |
| 2. backlog.py parser | M | 20 min | — | |
| 3. Unit tests | S | 15 min | — | |
| 4. Integration check | XS | 5 min | — | |
| **Total** | | ~45 min | — | |

---

*Plan created: 2026-02-02*
*Next: /feature-implement*
