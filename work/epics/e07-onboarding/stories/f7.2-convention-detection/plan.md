# Implementation Plan: Convention Detection

## Overview
- **Feature:** F7.2
- **Story Points:** 3 SP
- **Feature Size:** M
- **Created:** 2026-02-05
- **Design:** `work/stories/f7.2-convention-detection/design.md`

## Tasks

### Task 1: Create Convention Schemas
- **Description:** Define Pydantic models for all convention types (Confidence, IndentationConvention, NamingConvention, etc.) and the ConventionResult container.
- **Files:**
  - Create `src/raise_cli/onboarding/conventions.py` (schemas section)
- **TDD Cycle:**
  - RED: Write test that imports and instantiates ConventionResult with sample data
  - GREEN: Implement all Pydantic models from design spec
  - REFACTOR: Ensure proper docstrings and type annotations
- **Verification:** `pytest tests/onboarding/test_conventions.py -k "schema" -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Implement Confidence Calculation
- **Description:** Implement `calculate_confidence()` function with the sample-size aware logic (<5 = LOW, 5-10 = cap MEDIUM, >10 = ratio-based).
- **Files:**
  - `src/raise_cli/onboarding/conventions.py`
- **TDD Cycle:**
  - RED: Write tests for edge cases (<5 samples, exactly 5, 10, 11, various ratios)
  - GREEN: Implement confidence calculation per design algorithm
  - REFACTOR: Clean up, add docstring
- **Verification:** `pytest tests/onboarding/test_conventions.py -k "confidence" -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Implement Style Detection
- **Description:** Implement detection for indentation (spaces/tabs, width), quote style (single/double), and line length (80th percentile).
- **Files:**
  - `src/raise_cli/onboarding/conventions.py`
- **TDD Cycle:**
  - RED: Write tests with fixture files (consistent 4-space, mixed indent, etc.)
  - GREEN: Implement `detect_indentation()`, `detect_quotes()`, `detect_line_length()`
  - REFACTOR: Extract common file-reading logic
- **Verification:** `pytest tests/onboarding/test_conventions.py -k "style" -v`
- **Size:** M
- **Dependencies:** Task 2

### Task 4: Implement Naming Detection
- **Description:** Implement detection for function, class, and constant naming patterns using regex extraction.
- **Files:**
  - `src/raise_cli/onboarding/conventions.py`
- **TDD Cycle:**
  - RED: Write tests for snake_case functions, PascalCase classes, UPPER_SNAKE constants
  - GREEN: Implement `classify_name()`, `detect_naming_conventions()`
  - REFACTOR: Ensure regex patterns are clear and documented
- **Verification:** `pytest tests/onboarding/test_conventions.py -k "naming" -v`
- **Size:** M
- **Dependencies:** Task 2

### Task 5: Implement Structure Detection
- **Description:** Detect project structure conventions (source_dir, test_dir, has_src_layout, common_patterns).
- **Files:**
  - `src/raise_cli/onboarding/conventions.py`
- **TDD Cycle:**
  - RED: Write tests for src-layout project, flat project, various test directories
  - GREEN: Implement `detect_structure()`
  - REFACTOR: Reuse directory walking from detection.py if applicable
- **Verification:** `pytest tests/onboarding/test_conventions.py -k "structure" -v`
- **Size:** S
- **Dependencies:** Task 1 (uses existing detection.py infrastructure)

### Task 6: Integrate into detect_conventions()
- **Description:** Create main `detect_conventions()` function that orchestrates all detectors and calculates overall confidence.
- **Files:**
  - `src/raise_cli/onboarding/conventions.py`
  - Update `src/raise_cli/onboarding/__init__.py` exports
- **TDD Cycle:**
  - RED: Write integration test calling detect_conventions() on fixture project
  - GREEN: Wire up all detectors, implement overall_confidence calculation
  - REFACTOR: Ensure clean API, proper timing measurement
- **Verification:** `pytest tests/onboarding/test_conventions.py -k "integration" -v`
- **Size:** S
- **Dependencies:** Tasks 3, 4, 5

### Task 7: Create Test Fixtures
- **Description:** Create fixture projects for testing (consistent, inconsistent, minimal, empty).
- **Files:**
  - Create `tests/fixtures/conventions/consistent_python/`
  - Create `tests/fixtures/conventions/inconsistent_python/`
  - Create `tests/fixtures/conventions/minimal_python/`
- **TDD Cycle:** N/A (fixtures support other tests)
- **Verification:** Fixtures exist and are used by other tests
- **Size:** S
- **Dependencies:** None (can parallel with Task 1)

### Task 8: Validate on raise-commons
- **Description:** Run convention detection on raise-commons itself and verify results match known conventions (4-space indent, snake_case functions, src/ layout).
- **Files:**
  - Add test in `tests/onboarding/test_conventions.py`
- **TDD Cycle:**
  - RED: Write test asserting raise-commons conventions
  - GREEN: Should pass if detection is correct
  - REFACTOR: Document expected conventions
- **Verification:** `pytest tests/onboarding/test_conventions.py -k "raise_commons" -v`
- **Size:** XS
- **Dependencies:** Task 6

### Task 9 (Final): Manual Integration Test
- **Description:** Run `detect_conventions()` interactively on raise-commons and another project, verify output is sensible and confidence scores are honest.
- **Verification:** Demo detection working in Python REPL, inspect ConventionResult
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order

```
Task 1 (schemas) ──┬──► Task 2 (confidence) ──┬──► Task 3 (style) ────┐
                   │                          │                        │
Task 7 (fixtures) ─┘                          ├──► Task 4 (naming) ───┼──► Task 6 (integrate) ──► Task 8 (validate) ──► Task 9 (manual)
                                              │                        │
                                              └──► Task 5 (structure) ─┘
```

**Parallelizable:**
- Task 1 + Task 7 (schemas and fixtures are independent)
- Tasks 3, 4, 5 (after Task 2, all detection tasks can proceed in parallel)

## Risks

| Risk | Likelihood | Mitigation |
|------|:----------:|------------|
| Regex extraction misses edge cases | Medium | Test with real code (raise-commons), add edge case fixtures |
| Inconsistent projects cause LOW confidence everywhere | Low | That's correct behavior — honest confidence is the goal |
| Performance slow on large codebases | Low | Sample first N files if >100, document limitation |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1. Schemas | S | 15 min | -- | |
| 2. Confidence | S | 15 min | -- | |
| 3. Style | M | 30 min | -- | |
| 4. Naming | M | 30 min | -- | |
| 5. Structure | S | 15 min | -- | |
| 6. Integrate | S | 15 min | -- | |
| 7. Fixtures | S | 15 min | -- | Can parallel |
| 8. Validate | XS | 10 min | -- | |
| 9. Manual | XS | 5 min | -- | |
| **Total** | **M** | **~150 min** | -- | With kata cycle |

**Velocity assumption:** 2x with kata cycle → ~75 min actual

---

*Plan created: 2026-02-05*
*Next: `/story-implement`*
