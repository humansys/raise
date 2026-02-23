# Implementation Plan: S211.3 — rai memory build → registry

## Overview
- **Story:** S211.3
- **Size:** M
- **Tasks:** 6
- **Derived from:** design.md § Target Interfaces
- **Created:** 2026-02-22

## Tasks

### Task 1: Extract concept_to_node utility

**Objective:** Extract the Concept→GraphNode conversion from builder into a shared module so parser wrappers can reuse it.

**RED — Write Failing Test:**
- **File:** `tests/governance/test_convert.py`
- **Test function:** `test_concept_to_node_basic`
- **Setup:** Given a `Concept` with type REQUIREMENT, id, content, file, section, lines, metadata
- **Action:** When `concept_to_node(concept)` is called
- **Assertion:** Then the returned `ConceptNode` has matching id, type="requirement", content, source_file, metadata

**Additional tests:**
- `test_concept_to_node_preserves_all_types` — verify each `ConceptType` maps to the correct string value in the node's `type` field.
- `test_concept_to_node_preserves_section_and_lines` — verify `concept.section` and `concept.lines` are stored in `metadata["section"]` and `metadata["lines"]` (R3 fix: avoid silent data loss).

**GREEN — Implement:**
- **File:** `src/rai_cli/governance/parsers/_convert.py`
- **Function:** `def concept_to_node(concept: Concept) -> ConceptNode`
- **Integration:** Builder's `_concept_to_node()` delegates to this function (or stays as-is since `load_work()` uses it independently)

**Verification:**
```bash
pytest tests/governance/test_convert.py -v
```

**Size:** S
**Dependencies:** None
**AC Reference:** Foundation for all subsequent tasks

---

### Task 2: Create parser wrapper classes (6 simple parsers)

**Objective:** Add GovernanceParser-conformant wrapper classes to the 6 simple parser modules.

**RED — Write Failing Test:**
- **File:** `tests/governance/test_parser_wrappers.py`
- **Test functions:**
  - `test_prd_parser_can_parse_matching_type` — PrdParser.can_parse returns True for PRD locator
  - `test_prd_parser_can_parse_rejects_other` — returns False for VISION locator
  - `test_prd_parser_parse_returns_graph_nodes` — parse() returns list[GraphNode] from a fixture PRD file
  - `test_prd_parser_conforms_to_protocol` — `isinstance(PrdParser(), GovernanceParser)` is True
  - Same pattern for Vision, Constitution, Roadmap (parametrized)
- **Setup:** ArtifactLocator with artifact_type, path to fixture file, project_root in metadata
- **Assertion:** Correct node types returned, non-empty for valid files

**GREEN — Implement:**
- **Files:** `prd.py`, `vision.py`, `constitution.py`, `roadmap.py`, `backlog.py`, `epic.py`
- **Classes:** `PrdParser`, `VisionParser`, `ConstitutionParser`, `RoadmapParser`, `BacklogParser`, `EpicScopeParser`
- Each class: `can_parse(locator) → bool`, `parse(locator) → list[GraphNode]`
- BacklogParser wraps `extract_project()` + `extract_epics()`
- EpicScopeParser wraps `extract_epic_details()` + `extract_stories()`

**Verification:**
```bash
pytest tests/governance/test_parser_wrappers.py -v
```

**Size:** M
**Dependencies:** Task 1
**AC Reference:** Scenario "Built-in parsers discovered via registry"

---

### Task 3: Create explicit parser wrapper classes (3 parsers with path logic)

**Objective:** Add GovernanceParser wrappers for ADR, Guardrails, and Glossary parsers.

**RED — Write Failing Test:**
- **File:** `tests/governance/test_parser_wrappers.py` (extend from T2)
- **Test functions:**
  - `test_adr_parser_parse_single_file` — AdrParser parses one ADR file via locator
  - `test_guardrails_parser_parse` — GuardrailsParser parses guardrails.md
  - `test_glossary_parser_parse` — GlossaryParser parses glossary.md
  - `test_all_parsers_conform_to_protocol` — parametrized isinstance check for all 9

**GREEN — Implement:**
- **Files:** `adr.py`, `guardrails.py`, `glossary.py`
- **Classes:** `AdrParser`, `GuardrailsParser`, `GlossaryParser`
- AdrParser: per-file parsing via `extract_decision_from_file()`
- GuardrailsParser: delegates to `extract_guardrails(path, root)`
- GlossaryParser: delegates to `extract_glossary_terms(path, root)`

**Verification:**
```bash
pytest tests/governance/test_parser_wrappers.py -v
```

**Size:** S
**Dependencies:** Task 1
**AC Reference:** Scenario "Built-in parsers discovered via registry"

---

### Task 4: Register entry points in pyproject.toml + reinstall

**Objective:** Register all 9 parser wrapper classes as entry points and verify discovery.

**RED — Write Failing Test:**
- **File:** `tests/adapters/test_registry.py` (extend existing)
- **Test function:** `test_governance_parsers_discovered`
- **Setup:** Package installed with entry points
- **Action:** Call `get_governance_parsers()`
- **Assertion:** Expected names are a subset of result keys: `assert {"prd", "vision", "constitution", "roadmap", "backlog", "epic_scope", "adr", "guardrails", "glossary"}.issubset(result.keys())`. No hardcoded count — future parsers don't break this test (R2 fix, PAT-E-241).

**GREEN — Implement:**
- **File:** `pyproject.toml`
- Add `[project.entry-points."rai.governance.parsers"]` section with 9 entries
- Run `pip install -e .` to register

**Verification:**
```bash
pip install -e . && pytest tests/adapters/test_registry.py -v -k governance
```

**Size:** S
**Dependencies:** Tasks 2, 3
**AC Reference:** Scenario "Built-in parsers discovered via registry"

---

### Task 5: Refactor GovernanceExtractor to use registry

**Objective:** Refactor extractor internals to build locators and delegate to registry parsers. Maintain backward compat for `extract_with_result()` and `extract_from_file()`.

**RED — Write Failing Test:**
- **File:** `tests/governance/test_extractor.py` (extend existing)
- **Test functions:**
  - `test_extract_all_returns_graph_nodes` — `extract_all()` returns `list[GraphNode]`, not `list[Concept]`
  - `test_extract_all_with_broken_parser` — one parser raises, others still work, warning logged
  - `test_extract_with_result_backward_compat` — still returns `ExtractionResult` with `list[Concept]`, preserving `.file`, `.section`, `.lines` fields (C1 fix: legacy path independent of `extract_all()`)
  - `test_extract_all_identical_output` — snapshot: compare node IDs from registry path vs current hardcoded path (regression guard). This is the behavioral test that replaces a mock-based registry check (R1 fix).
- **Setup:** Test fixtures with governance files
- **Assertion:** Same node IDs produced, broken parsers gracefully skipped

**GREEN — Implement:**
- **File:** `src/rai_cli/governance/extractor.py`
- Add `_build_locators() → list[ArtifactLocator]`
- Add `_find_parser(locator, parsers) → GovernanceParser | None`
- Refactor `extract_all()` to return `list[GraphNode]` via registry path
- Keep `extract_with_result()` as independent legacy path with direct `extract_*` imports — does NOT call `extract_all()`. Two paths coexist: `extract_all()` (new, returns GraphNode) and `extract_with_result()` (legacy, returns ExtractionResult with Concept). Mark `extract_with_result()` as deprecated (C1 fix).
- Accept optional `parsers` param in `__init__` for DI/testing
- Simplify `builder.load_governance()` — remove `_concept_to_node` loop

**Verification:**
```bash
pytest tests/governance/test_extractor.py tests/context/test_builder.py -v
```

**Size:** L
**Dependencies:** Tasks 2, 3, 4
**AC Reference:** Scenarios "GovernanceExtractor uses registry path", "Broken parser degrades gracefully"

---

### Task 6 (Final): Integration Verification

**Objective:** Validate story works end-to-end with running `rai memory build`.

**Verification:**
1. Run `rai memory build` — succeeds with no errors
2. Compare graph output (node count, node types) vs pre-refactor baseline
3. Run full test suite: `pytest --tb=short`
4. Run `ruff check . && pyright`
5. Run `rai memory extract` — backward compat works

**Size:** S
**Dependencies:** All previous tasks

## Execution Order

1. **T1** — concept_to_node utility (foundation)
2. **T2, T3** — parser wrappers (parallel, both depend on T1 only)
3. **T4** — entry point registration (depends on T2, T3)
4. **T5** — extractor refactor (depends on T4)
5. **T6** — integration verification (final)

## Traceability

| AC Scenario | Task(s) | Design § |
|-------------|---------|----------|
| "Built-in parsers discovered via registry" | T2, T3, T4 | Target Interfaces → Parser wrapper pattern, Entry points |
| "External parser registered via entry point" | T4 | Target Interfaces → Entry points in pyproject.toml |
| "Broken parser degrades gracefully" | T5 | Target Interfaces → GovernanceExtractor refactored |
| "GovernanceExtractor uses registry path" | T5, T6 | Target Interfaces → GovernanceExtractor refactored |

## Risks

- **Backward compat for `extract_with_result()`:** `rai memory extract` CLI expects `Concept` objects with `.type.value`, `.file`, `.section`, `.lines`. Must maintain dual path or bridge. Mitigation: T5 test explicitly covers this.
- **Entry point discovery in test env:** `get_governance_parsers()` requires package to be installed with entry points. Tests in CI must run after `pip install -e .`. Mitigation: T4 test validates this explicitly.
- **Hardcoded count tests (PAT-E-241):** Existing tests may have hardcoded node/concept counts. Adding entry points or changing extractor output could break them. Mitigation: run full suite in T6.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | M | -- | |
| 3 | S | -- | |
| 4 | S | -- | |
| 5 | L | -- | |
| 6 | S | -- | Integration verification |
