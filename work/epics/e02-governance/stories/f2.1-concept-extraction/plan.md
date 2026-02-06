# Implementation Plan: F2.1 Concept Extraction

## Overview
- **Feature:** F2.1 Concept Extraction
- **Story Points:** 3 SP
- **Feature Size:** S (3 components, straightforward regex parsing)
- **Created:** 2026-01-31

## Tasks

### Task 1: Create Pydantic Models
- **Description:** Implement `Concept`, `ConceptType`, and `ExtractionResult` models in `src/raise_cli/governance/models.py`
- **Files:**
  - CREATE `src/raise_cli/governance/__init__.py`
  - CREATE `src/raise_cli/governance/models.py`
- **Verification:**
  - Models instantiate correctly with valid data
  - `pyright --strict src/raise_cli/governance/models.py` passes
  - `pytest tests/governance/test_models.py -v` passes
- **Size:** S
- **Dependencies:** None

### Task 2: Implement PRD Requirements Parser
- **Description:** Create `parsers/prd.py` with `extract_requirements()` function using regex `### RF-\d+: (.+)` to extract requirements with metadata
- **Files:**
  - CREATE `src/raise_cli/governance/parsers/__init__.py`
  - CREATE `src/raise_cli/governance/parsers/prd.py`
  - CREATE `tests/governance/parsers/test_prd.py`
- **Verification:**
  - Extract 8 requirements from real `governance/projects/raise-cli/prd.md`
  - Handle edge cases (empty file, malformed sections, special chars)
  - `pytest tests/governance/parsers/test_prd.py -v --cov=src/raise_cli/governance/parsers/prd.py --cov-fail-under=90` passes
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Implement Vision Outcomes Parser
- **Description:** Create `parsers/vision.py` with `extract_outcomes()` function to parse markdown tables and extract outcome rows
- **Files:**
  - CREATE `src/raise_cli/governance/parsers/vision.py`
  - CREATE `tests/governance/parsers/test_vision.py`
- **Verification:**
  - Extract 7+ outcomes from real `governance/solution/vision.md`
  - Table parsing handles variations (spacing, formatting)
  - `pytest tests/governance/parsers/test_vision.py -v --cov=src/raise_cli/governance/parsers/vision.py --cov-fail-under=90` passes
- **Size:** S
- **Dependencies:** Task 1

### Task 4: Implement Constitution Principles Parser
- **Description:** Create `parsers/constitution.py` with `extract_principles()` function using regex `### §\d+\. (.+)` to extract principles
- **Files:**
  - CREATE `src/raise_cli/governance/parsers/constitution.py`
  - CREATE `tests/governance/parsers/test_constitution.py`
- **Verification:**
  - Extract 8+ principles from real `framework/reference/constitution.md`
  - Section content extraction works correctly
  - `pytest tests/governance/parsers/test_constitution.py -v --cov=src/raise_cli/governance/parsers/constitution.py --cov-fail-under=90` passes
- **Size:** S
- **Dependencies:** Task 1

### Task 5: Implement GovernanceExtractor Orchestrator
- **Description:** Create `extractor.py` with `GovernanceExtractor` class that orchestrates all parsers, provides `extract_from_file()` and `extract_all()` methods
- **Files:**
  - CREATE `src/raise_cli/governance/extractor.py`
  - CREATE `tests/governance/test_extractor.py`
- **Verification:**
  - `extract_all()` returns 23+ concepts from raise-commons governance
  - `extract_from_file()` works for individual files
  - Error handling for missing files works (skip with warning)
  - `pytest tests/governance/test_extractor.py -v --cov=src/raise_cli/governance/extractor.py --cov-fail-under=90` passes
- **Size:** M
- **Dependencies:** Task 2, Task 3, Task 4

### Task 6: Add CLI Command `raise graph extract`
- **Description:** Create `src/raise_cli/cli/commands/graph.py` with `extract` command supporting `--format json` option
- **Files:**
  - CREATE `src/raise_cli/cli/commands/graph.py`
  - MODIFY `src/raise_cli/cli/app.py` (register graph commands)
  - CREATE `tests/cli/commands/test_graph.py`
- **Verification:**
  - `raise graph extract` works and displays human-readable output
  - `raise graph extract --format json` returns valid JSON
  - `raise graph extract governance/projects/raise-cli/prd.md` works for single file
  - CLI integration test passes
  - `pytest tests/cli/commands/test_graph.py -v` passes
- **Size:** M
- **Dependencies:** Task 5

### Task 7: Documentation & Component Catalog
- **Description:** Update component catalog, add docstrings (Google-style) to all public APIs, verify all quality gates pass
- **Files:**
  - MODIFY `dev/components.md` (add governance module entry)
  - VERIFY all files have complete docstrings
- **Verification:**
  - All public APIs have Google-style docstrings
  - `dev/components.md` documents governance module
  - `ruff check src/raise_cli/governance/` passes
  - `pyright --strict src/raise_cli/governance/` passes
  - `pytest tests/governance/ --cov=src/raise_cli/governance --cov-fail-under=90` passes
- **Size:** XS
- **Dependencies:** Task 6

## Execution Order

**Sequential foundation:**
1. Task 1 (models) - Foundation for all parsers

**Parallel parsers:**
2. Task 2 (PRD parser), Task 3 (Vision parser), Task 4 (Constitution parser) - Can be done in parallel

**Sequential integration:**
3. Task 5 (Extractor orchestrator) - Integrates all parsers
4. Task 6 (CLI command) - User-facing interface
5. Task 7 (Documentation) - Final polish

**Optimal order:**
```
Task 1
  ├─→ Task 2 ┐
  ├─→ Task 3 ├─→ Task 5 ─→ Task 6 ─→ Task 7
  └─→ Task 4 ┘
```

## Risks

| Risk | Mitigation |
|------|------------|
| Governance file formats vary | Use spike code as reference; handle variations gracefully |
| Content truncation loses important data | Limit to 500 chars is reasonable; can adjust if needed |
| ID generation conflicts | Sanitize IDs consistently; test with real governance files |
| Missing governance files in test env | Use fixtures with minimal test data; integration tests use real files |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | Models creation |
| 2 | S | -- | PRD parser |
| 3 | S | -- | Vision parser |
| 4 | S | -- | Constitution parser |
| 5 | M | -- | Extractor orchestrator |
| 6 | M | -- | CLI command |
| 7 | XS | -- | Documentation |

## Definition of Done (Feature-Level)

- [ ] All tasks complete (1-7)
- [ ] Extract 23+ concepts from raise-commons governance files
- [ ] CLI command `raise graph extract` functional
- [ ] >90% test coverage on governance module
- [ ] All type checks pass (`pyright --strict`)
- [ ] All linting passes (`ruff check`)
- [ ] Component catalog updated
- [ ] No security issues (`bandit -r src/raise_cli/governance/`)

---

*Created: 2026-01-31*
*Ready for: `/story-implement`*
