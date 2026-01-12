# Quickstart: Katas Ontology Alignment Audit

**Feature**: 005-katas-ontology-audit
**Date**: 2026-01-11

## Overview

This guide explains how to execute the kata ontology alignment audit and interpret results.

## Prerequisites

- Access to raise-commons repository
- Familiarity with RaiSE ontology v2.1 (glossary, methodology)
- Understanding of Jidoka Inline structure

## Input Files

| File | Purpose | Location |
|------|---------|----------|
| Glossary v2.1 | Kata definition, levels, terminology | `docs/framework/v2.1/model/20-glossary-v2.1.md` |
| Methodology v2 | Kata examples, expected coverage | `docs/framework/v2.1/model/21-methodology-v2.md` |
| Existing katas | Files to audit | `src/katas/*.md` |

## Execution Steps

### Step 1: Review Target State

Before auditing, understand what the ontology says SHOULD exist.

**Expected Kata Slots** (from research.md):

| Level | Expected Topics |
|-------|-----------------|
| Principios | Rol del Orquestador, Heutagogía |
| Flujo | Discovery, Planning, Generación de Plan |
| Patrón | Tech Design, Análisis de Código, Discovery de Ecosistema |
| Técnica | Modelado de Datos, API Design |

### Step 2: Audit Each Kata

For each file in `src/katas/`:

1. **Identify Level Mapping**
   - L0 → principios
   - L1 → flujo
   - L2 → patrón
   - L3 → técnica

2. **Check Jidoka Inline Compliance**
   - Look for `### Paso N:` or `### Step N:` headings
   - Verify each has `**Verificación:**` line
   - Verify each has `> **Si no puedes continuar:**` block

3. **Scan for Deprecated Terms**
   - DoD → Validation Gate
   - Rule → Guardrail
   - Developer → Orquestador

4. **Check for Project Markers**
   - Jafra, SAR, PROSA, PMO, RAG in filename or content

5. **Classify**
   - **Mapped**: Fills an ontology slot
   - **Orphan**: No matching slot (project-specific or deprecated)

### Step 3: Generate Outputs

Create the following files in `specs/005-katas-ontology-audit/outputs/`:

#### kata-coverage-matrix.md

```markdown
# Kata Coverage Matrix

## Summary
- Total Ontology Slots: X
- Filled Slots: Y (Z%)
- Gap Slots: W

## By Level

### Principios (L0)
| Slot | Topic | Status | Filled By |
|------|-------|--------|-----------|
| PRIN-001 | Rol del Orquestador | filled | L0-00-... |
| PRIN-002 | Heutagogía | gap | - |

[Continue for all levels]
```

#### kata-coverage-matrix.json

Generate JSON matching `contracts/coverage-matrix.schema.json`.

#### migration-roadmap.md

```markdown
# Migration Roadmap

## High Priority (Rename Only)
| Task | Current | Target | Effort |
|------|---------|--------|--------|
| MIG-001 | L1-04-generacion-plan... | flujo/04-generacion-plan.md | Low |

## Medium Priority (Restructure - Add Jidoka Inline)
[Tasks requiring structural changes]

## Low Priority (Archive)
[Orphan katas to archive]
```

#### orphan-katas.md

```markdown
# Orphan Katas Analysis

## Project-Specific Orphans

### L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md
- **Reason**: Project-specific (Jafra)
- **Project Markers**: Jafra in filename
- **Recommendation**: Archive to `archive/projects/jafra/`

[Continue for all orphans]
```

### Step 4: Validate Outputs

Run validation against JSON schema:

```bash
# Using ajv-cli (if available)
ajv validate -s contracts/coverage-matrix.schema.json -d outputs/kata-coverage-matrix.json
```

Or manually verify:
- [ ] All katas classified (mapped or orphan)
- [ ] All ontology slots assessed (filled or gap)
- [ ] Migration tasks have valid type, priority, effort
- [ ] No deprecated terminology in output files

## Output File Locations

```
specs/005-katas-ontology-audit/
├── outputs/
│   ├── kata-coverage-matrix.md      # Human-readable matrix
│   ├── kata-coverage-matrix.json    # Machine-readable matrix
│   ├── migration-roadmap.md         # Human-readable tasks
│   ├── migration-roadmap.json       # Machine-readable tasks
│   └── orphan-katas.md              # Detailed orphan analysis
└── contracts/
    └── coverage-matrix.schema.json  # JSON schema for validation
```

## Success Criteria Validation

After completing the audit, verify:

- [ ] **SC-001**: 100% of katas classified (check `summary.totalKatas == summary.mappedKatas + summary.orphanKatas`)
- [ ] **SC-002**: 100% of slots assessed (check `summary.totalSlots == summary.filledSlots + summary.gapSlots`)
- [ ] **SC-003**: Coverage matrix shows target vs. current state clearly
- [ ] **SC-004**: Migration roadmap includes tasks for non-compliant katas
- [ ] **SC-005**: Orphan katas tagged with reason
- [ ] **SC-006**: Coverage percentage visible in summary

## Next Steps

After audit completion:

1. **Review results** with framework maintainers
2. **Prioritize migration tasks** based on roadmap
3. **Execute migrations** in separate feature branches
4. **Fill gaps** by creating new katas for missing slots

---

*Quickstart completed: 2026-01-11*
