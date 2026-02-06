# Implementation Plan: F12.3 Glossary Extractor

## Overview
- **Feature:** F12.3
- **Story Points:** S (~3 SP)
- **Feature Size:** S
- **Created:** 2026-02-03
- **Epic:** E12 Complete Knowledge Graph

## Context

**Patterns loaded:**
- PAT-038: Parser velocity improves with familiarity (expect 1.5x)
- PAT-009: Parser composition: regex → extract → truncate → model

**Source file:** `framework/reference/glossary.md`
- ~980 lines, ~50 terms
- Format: `### Term Name` with prose definitions
- Version tags: `**[NUEVO vX.X]**` or `[NUEVO vX.X]`

**Sections to extract:**
- `## Términos Core de RaiSE`
- `## Ontología Agentic AI`
- `## Artefactos del Flujo de Trabajo`
- `## Conceptos de Preventa/Proyectos`

**Sections to skip:**
- `## Mapeo Español-Inglés` (table)
- `## Anti-Términos` (table)
- `## Changelog` (history)
- `## Jerarquías de Referencia` (reference)
- `## Métricas de Calidad AI` (reference)
- `## Formato de Referencia a Principios` (reference)

## Tasks

### Task 1: Create Glossary Parser Module
- **Description:** Create `glossary.py` parser following established pattern from guardrails.py
- **Files:**
  - `src/raise_cli/governance/parsers/glossary.py` (new)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/governance/parsers/test_glossary.py -v`
- **Size:** S
- **Dependencies:** None

**Implementation details:**
- `_extract_term_header()` — Parse `### Term (Translation)` and version tags
- `_extract_term_definition()` — Get prose until next `###` or `##`
- `extract_glossary_terms()` — Main extraction function
- `extract_all_terms()` — Convenience wrapper for standard location

### Task 2: Integrate into Extractor
- **Description:** Add glossary extraction to unified graph builder
- **Files:**
  - `src/raise_cli/governance/extractor.py` (modify)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/governance/test_extractor.py -v`
- **Size:** XS
- **Dependencies:** Task 1

### Task 3: Manual Integration Test
- **Description:** Validate glossary terms appear in unified graph queries
- **Verification:**
  ```bash
  uv run raise graph build --unified
  uv run raise context query "kata" --unified --types term
  ```
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order

1. **Task 1** — Parser module (foundation)
2. **Task 2** — Extractor integration (depends on 1)
3. **Task 3** — Integration test (validates end-to-end)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Term format variance | Low | Low | Flexible regex, test with edge cases |
| Definition boundary detection | Medium | Low | Use `###` as delimiter, not blank lines |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1 | S | ~15 min | Parser module + 17 tests |
| 2 | XS | ~3 min | Extractor integration |
| 3 | XS | ~2 min | 59 terms in unified graph |

**Total:** ~20 min (expected 30-45 min) = **1.5-2x velocity**

---

*Plan created: 2026-02-03*
*Next: `/story-implement`*
