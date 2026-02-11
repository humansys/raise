# Implementation Plan: F12.2 Guardrails Extractor

## Overview
- **Feature:** F12.2
- **Story Points:** 3 SP (S)
- **Feature Size:** S
- **Created:** 2026-02-03
- **Pattern:** Follows F12.1 ADR Extractor pattern (PAT-038: 1.3x velocity)

## Source Analysis

**File:** `governance/solution/guardrails.md`

**Structure:**
- Summary tables in sections: Code Quality, Testing, Security, Architecture, Development Workflow, Inference Economy
- Detailed guardrail sections: MUST-CODE-001, MUST-CODE-002, etc.
- Each detailed section has: Regla, Contexto, Verificación, Ejemplos

**Extraction strategy:** Extract from summary tables (ID, Level, Guardrail, Verificación columns) for MVC. Detailed sections available via source file link.

## Tasks

### Task 1: Guardrails Parser Module
- **Description:** Create `src/rai_cli/governance/parsers/guardrails.py` with section-based extraction
- **Files:**
  - `src/rai_cli/governance/parsers/guardrails.py` (new)
  - `src/rai_cli/governance/parsers/__init__.py` (update export)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `uv run pytest tests/governance/parsers/test_guardrails.py -v`
- **Size:** S
- **Dependencies:** None

**Implementation notes:**
- Extract guardrails from tables in each section (Code Quality, Testing, Security, etc.)
- Parse table rows: ID, Level, Guardrail, Verificación, Derivado de
- Create Concept with type=ConceptType.GUARDRAIL
- Include section name in metadata for context queries

### Task 2: Extractor Integration
- **Description:** Integrate guardrails parser into `GovernanceExtractor.extract_all()`
- **Files:**
  - `src/rai_cli/governance/extractor.py` (modify)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `uv run pytest tests/governance/test_extractor.py -v -k guardrail`
- **Size:** XS
- **Dependencies:** Task 1

**Implementation notes:**
- Import `extract_guardrails` from guardrails parser
- Add extraction call in `extract_all()` and `extract_with_result()`
- Update `_infer_concept_type()` for guardrails.md

### Task 3 (Final): Manual Integration Test
- **Description:** Verify guardrails appear in unified graph with correct type and metadata
- **Verification:**
  ```bash
  uv run raise graph build --unified
  uv run raise context query "type safety testing security" --unified
  ```
- **Size:** XS
- **Dependencies:** Task 1, Task 2

**Expected output:**
- ~15-20 guardrail nodes in unified graph
- Queryable by section (Code Quality, Testing, Security, etc.)
- Queryable by level (MUST, SHOULD)

## Execution Order
1. Task 1 (parser foundation)
2. Task 2 (extractor integration)
3. Task 3 (integration test)

## Risks
- **Table parsing edge cases:** Mitigation: Handle multi-line cells and markdown formatting
- **Section detection:** Mitigation: Use heading patterns (### Code Quality, etc.)

## Duration Tracking
| Task | Size | Estimated | Actual | Notes |
|------|------|-----------|--------|-------|
| 1 | S | 20 min | -- | Parser (1.3x from F12.1) |
| 2 | XS | 5 min | -- | Integration |
| 3 | XS | 5 min | -- | Manual test |
| **Total** | **S** | **30 min** | -- | |
