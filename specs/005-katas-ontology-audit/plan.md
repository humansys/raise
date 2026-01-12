# Implementation Plan: Katas Ontology Alignment Audit

**Branch**: `005-katas-ontology-audit` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-katas-ontology-audit/spec.md`

## Summary

This feature audits existing katas against the RaiSE ontology v2.1 to determine alignment status and generate a migration roadmap. Using an **ontology-driven approach**, the analysis produces:
1. A Kata Coverage Matrix (target state vs. current state)
2. A Migration Roadmap (rename, restructure, archive tasks)
3. Multi-format output (Markdown for humans, JSON for automation)

**Key Principle:** The ontology defines what SHOULD exist; katas are classified as Mapped/Gap/Orphan based on whether they fill defined ontology slots.

## Technical Context

**Artifact Type**: Documentation-centric analysis (not production software)
**Primary Outputs**: Markdown + JSON documents
**Analysis Scope**: 23 kata files in `/home/emilio/Code/raise-commons/src/katas`
**Storage**: Git repository (versioned Markdown and JSON files)
**Validation**: Checklist verification against ontology source documents
**Target Location**: `specs/005-katas-ontology-audit/outputs/`

**Input Sources (Read-Only)**:
- `docs/framework/v2.1/model/20-glossary-v2.1.md` → Kata definition, levels, Jidoka Inline requirement
- `docs/framework/v2.1/model/21-methodology-v2.md` → Kata level examples, expected coverage
- `src/katas/*.md` → 23 existing kata files to audit

**Output Artifacts**:
| Artifact | Format | Purpose |
|----------|--------|---------|
| `kata-coverage-matrix.md` | Markdown | Human-readable target vs. current state |
| `kata-coverage-matrix.json` | JSON | Machine-readable for automation |
| `migration-roadmap.md` | Markdown | Human-readable migration tasks |
| `migration-roadmap.json` | JSON | Machine-readable task list |
| `orphan-katas.md` | Markdown | Detailed orphan analysis with rationale |

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*Reference: `.specify/memory/constitution.md`*

| Principio | Verificación | Estado |
|-----------|--------------|--------|
| I. Coherencia Semántica | Audit uses ontology as source of truth (glossary v2.1, methodology v2); all output terms align with canonical definitions | [x] |
| II. Governance como Código | All outputs versioned in Git under `specs/005-katas-ontology-audit/outputs/`; JSON enables automation | [x] |
| III. Validación en Cada Fase | Each output has defined validation criteria (see Phase 1); checklists verify completeness | [x] |
| IV. Simplicidad | No new abstractions; uses existing ontology structure; KISS/DRY/YAGNI applied to migration recommendations | [x] |
| V. Mejora Continua | Audit itself is a Kaizen cycle—identifies gaps and improvements for kata ecosystem | [x] |

**Gate Status: ✅ PASSED** — Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/005-katas-ontology-audit/
├── spec.md                    # Feature specification
├── plan.md                    # This file
├── research.md                # Phase 0: Ontology parsing findings
├── data-model.md              # Phase 1: Entity schemas
├── quickstart.md              # Phase 1: How to run the audit
├── checklists/
│   └── requirements.md        # Spec quality checklist
└── outputs/                   # Analysis outputs (Phase 2+)
    ├── kata-coverage-matrix.md
    ├── kata-coverage-matrix.json
    ├── migration-roadmap.md
    ├── migration-roadmap.json
    └── orphan-katas.md
```

### Source Code (N/A for this feature)

This is a documentation-centric analysis feature. No production source code is created. The "implementation" consists of:
1. Manual or assisted analysis of kata files against ontology
2. Generation of structured output documents
3. Version control of analysis artifacts

**Structure Decision**: Documentation-only structure under `specs/005-katas-ontology-audit/`. All outputs are versioned Git artifacts, not runtime software.

## Complexity Tracking

> No Constitution violations. Complexity is minimal—this is a read-only analysis producing structured documentation.

| Aspect | Justification |
|--------|---------------|
| Multi-format output (MD + JSON) | Required by clarification; MD for humans, JSON for automation. Both generated from same analysis. |
| Orphan-katas.md separate file | Keeps main coverage matrix focused; orphan analysis may be lengthy with rationale |

---

## Phase 0: Research

### Research Tasks

Based on Technical Context, the following research is needed:

| Unknown | Research Task | Status |
|---------|---------------|--------|
| Ontology slot extraction | Parse glossary + methodology to derive expected kata slots per level | ✅ Complete |
| Jidoka Inline format | Extract exact structural requirements from methodology | ✅ Complete |
| Project-specific markers | Compile list of known project markers (Jafra, SAR, PROSA PMO, etc.) | ✅ Complete |
| Deprecated terminology | Extract complete list from glossary migration notes | ✅ Complete |

### Research Output

See [research.md](./research.md) for consolidated findings:
- **10 ontology slots** identified across 4 levels
- **Jidoka Inline format** documented with exact pattern
- **5 project markers** cataloged (Jafra, SAR, PROSA, PMO, RAG)
- **6 deprecated terms** mapped to canonical equivalents

---

## Phase 1: Design

**Status**: ✅ Complete

### Data Model

See [data-model.md](./data-model.md) for entity schemas:
- **OntologySlot**: Position in target kata ecosystem
- **Kata**: Existing kata file being audited
- **MappingResult**: Classification (mapped/gap/orphan)
- **MigrationTask**: Actionable alignment step

### Output Contracts

See [contracts/coverage-matrix.schema.json](./contracts/coverage-matrix.schema.json) for JSON schema.

### Quickstart

See [quickstart.md](./quickstart.md) for how to execute the audit.

---

## Phase 2: Tasks

**Status**: ✅ Complete

See [tasks.md](./tasks.md) for implementation task breakdown:
- **53 total tasks** organized by user story
- **29 parallelizable** tasks for efficiency
- **MVP scope**: US1 + US2 (35 tasks) delivers complete kata coverage matrix
