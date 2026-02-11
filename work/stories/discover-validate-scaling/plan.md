# Implementation Plan: Scale discover-validate for brownfield projects

## Overview
- **Story:** discover-validate-scaling
- **Story Points:** 8 SP
- **Feature Size:** L
- **Created:** 2026-02-07
- **Updated:** 2026-02-07 (simplified: removed semantic chunking, replaced with module grouping)
- **Design:** `work/stories/discover-validate-scaling/design.md`

## Tasks

### Task 1: Create analyzer module with Pydantic models and confidence scoring

- **Description:** Create `src/rai_cli/discovery/analyzer.py` with Pydantic models (`ConfidenceSignals`, `ConfidenceResult`, `AnalyzedComponent`, `AnalysisResult`) and the core `compute_confidence()` function. Also implement `match_path_category()` with `DEFAULT_CATEGORY_MAP`, `NAME_CATEGORY_OVERRIDES`, and `BASE_CLASS_CATEGORIES`. This is the foundation — all other tasks depend on these models and the scoring logic.
- **Files:**
  - Create: `src/rai_cli/discovery/analyzer.py`
  - Create: `tests/discovery/test_analyzer.py`
- **TDD Cycle:**
  - RED: Tests for `compute_confidence()` covering all 6 signals, boundary scores (39/40/69/70), tier assignment. Tests for `match_path_category()` with all default paths, custom map, no match.
  - GREEN: Implement models and scoring functions.
  - REFACTOR: Ensure type annotations are strict, docstrings complete.
- **Verification:** `pytest tests/discovery/test_analyzer.py -v && pyright src/rai_cli/discovery/analyzer.py`
- **Size:** M
- **Dependencies:** None
- **Status:** DONE (44 tests passing)

### Task 2: Implement hierarchy builder, module grouping, and analyze pipeline

- **Description:** Implement `build_hierarchy()` in `analyzer.py` that takes a list of `Symbol` objects, folds methods into their parent classes, and returns `AnalyzedComponent` units. Also implement `determine_category()` (path → name override → base class → default), `extract_first_sentence()` for auto-purpose, `group_by_module()` for batching components by source file, and the top-level `analyze()` function that orchestrates the full pipeline: separate public/internal → build hierarchy → score confidence → categorize → group by module.
- **Files:**
  - Modify: `src/rai_cli/discovery/analyzer.py`
  - Modify: `tests/discovery/test_analyzer.py`
- **TDD Cycle:**
  - RED: Tests for method folding (class with 5 methods → 1 unit), orphan methods (parent not in symbols), standalone functions, modules, mixed scenarios. Tests for `determine_category()` priority chain. Tests for `extract_first_sentence()` edge cases (None, empty, multiline, period-delimited). Tests for `group_by_module()`. Integration test: `ScanResult` → `AnalysisResult`.
  - GREEN: Implement hierarchy building, category determination, module grouping, and analyze pipeline.
  - REFACTOR: Extract helpers if hierarchy builder grows.
- **Verification:** `pytest tests/discovery/test_analyzer.py -v`
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Add `rai discover analyze` CLI command and formatter

- **Description:** Add the `analyze` subcommand to `discover_app` in `src/rai_cli/cli/commands/discover.py`. Accepts `--input` (JSON file or stdin), `--output` (human/json/summary), `--category-map` (optional YAML override). Add `format_analyze_result()` to `src/rai_cli/output/formatters/discover.py` with all three output formats. The command reads `ScanResult` JSON, calls `analyze()`, writes `work/discovery/analysis.json`, and prints formatted output.
- **Files:**
  - Modify: `src/rai_cli/cli/commands/discover.py`
  - Modify: `src/rai_cli/output/formatters/discover.py`
  - Create: `tests/cli/commands/test_discover_analyze.py` (or extend existing test file)
- **TDD Cycle:**
  - RED: Tests for CLI invocation with `--input` file (JSON format), all 3 output formats, missing input file error, invalid JSON error.
  - GREEN: Implement command and formatter.
  - REFACTOR: Ensure consistent error handling with existing discover commands.
- **Verification:** `pytest tests/cli/commands/test_discover_analyze.py -v && ruff check src/rai_cli/cli/commands/discover.py src/rai_cli/output/formatters/discover.py`
- **Size:** M
- **Dependencies:** Task 2

### Task 4: Rewrite `/discover-scan` and `/discover-validate` skills

- **Description:** Update `/discover-scan` SKILL.md to include a new step after scanning: call `rai discover analyze` on the scan output. The analysis.json becomes the primary artifact for validation. Rewrite `/discover-validate` SKILL.md with the new flow: load analysis.json, auto-validate high-confidence components, present medium-confidence as module batches for parallel AI synthesis, flag low-confidence for individual human review. Human decisions go from O(components) to O(modules + exceptions).
- **Files:**
  - Modify: `.claude/skills/discover-scan/SKILL.md`
  - Rewrite: `.claude/skills/discover-validate/SKILL.md`
- **TDD Cycle:** N/A (markdown skills, not code)
- **Verification:** Manual review — skills reference correct CLI commands, flow is coherent, confidence tiers match design spec.
- **Size:** M
- **Dependencies:** Task 3

### Task 5: Quality gates and manual integration test

- **Description:** Run full quality suite: `ruff check . && ruff format --check . && pyright src/ && pytest --cov=src --cov-fail-under=90`. Then dogfood: run `rai discover scan src/rai_cli -l python -o json | rai discover analyze` on our own codebase and verify the confidence distribution is reasonable. Verify the analysis.json is well-formed and module_groups are correct.
- **Files:** None (validation only)
- **TDD Cycle:** N/A
- **Verification:**
  - `ruff check . && ruff format --check .`
  - `pyright src/`
  - `pytest --cov=src --cov-fail-under=90`
  - `rai discover scan src/rai_cli -l python -o json | rai discover analyze --output human`
  - Verify output shows confidence tiers and module groups
- **Size:** S
- **Dependencies:** Task 4

## Execution Order

```
Task 1 (models + confidence scoring) ✓ DONE
  └→ Task 2 (hierarchy + module grouping + analyze pipeline)
       └→ Task 3 (CLI command + formatter)
            └→ Task 4 (skill rewrites)
                 └→ Task 5 (quality gates + dogfood)
```

All tasks are sequential. No parallelism opportunities due to layered dependencies.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Confidence thresholds (70/40) may not distribute well on real codebases | Medium | Task 5 dogfood will calibrate; thresholds are constants, easy to tune |
| stdin piping on Windows may behave differently | Low | Test with `--input` file path as primary; stdin as secondary |
| Skill rewrite may miss edge cases in AI interaction flow | Medium | Test validate skill manually on raise-cli after Task 4 |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 — Models + confidence scoring | M | Done | 44 tests, 2 fixes (path boundary, islower) |
| 2 — Hierarchy + grouping + pipeline | M | -- | |
| 3 — CLI command + formatter | M | -- | |
| 4 — Skill rewrites | M | -- | |
| 5 — Quality gates + dogfood | S | -- | |
