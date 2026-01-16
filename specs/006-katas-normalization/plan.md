# Implementation Plan: Katas Ontology Normalization

**Branch**: `006-katas-normalization` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-katas-normalization/spec.md`

## Summary

Normalize 15 migrated katas (in `src/katas/{principios,flujo,patron}/`) to ontology v2.1 standards by applying Jidoka Inline structure to each step and replacing deprecated terminology with canonical equivalents. Processing is incremental (one kata at a time) with Orquestador validation after each.

## Technical Context

**Language/Version**: Markdown (CommonMark spec) + Text editor
**Primary Dependencies**:
- `docs/framework/v2.1/model/20-glossary-v2.1.md` (terminology source)
- `specs/005-katas-ontology-audit/outputs/migration-roadmap.md` (priority order)
**Storage**: Git repository (versioned Markdown files)
**Testing**: Manual Orquestador review after each kata normalization
**Target Platform**: Any text editor / Git client
**Project Type**: Documentation-centric (no source code)
**Performance Goals**: N/A (human-paced workflow)
**Constraints**: Preserve semantic meaning; no content loss during normalization
**Scale/Scope**: 15 katas total (2 principios + 8 flujo + 5 patrón)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*Reference: `.specify/memory/constitution.md`*

| Principio | Verificación | Estado |
|-----------|--------------|--------|
| I. Coherencia Semántica | Términos normalizados desde glosario v2.1; mapeo explícito DoD→Validation Gate, etc. | [x] |
| II. Governance como Código | Katas versionadas en Git; cambios trazables por commit | [x] |
| III. Validación en Cada Fase | Orquestador valida cada kata antes de continuar (FR-006) | [x] |
| IV. Simplicidad | Solo cambios estructurales mínimos (Jidoka Inline + terminología); no reescritura | [x] |
| V. Mejora Continua | Normalization reports capturan aprendizajes por kata | [x] |

**Gate Status**: ✅ PASSED - All principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/006-katas-normalization/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: Jidoka format, terminology mapping
├── data-model.md        # Phase 1: Kata structure model
├── quickstart.md        # Phase 1: How to run normalization
├── checklists/
│   └── requirements.md  # Validation checklist
└── outputs/             # Normalization reports per kata
```

### Source Files (to be normalized)

```text
src/katas/
├── principios/
│   ├── 00-raise-katas-documentation.md      # MIG-RST-001
│   └── 01-raise-kata-execution-protocol.md  # MIG-RST-002
├── flujo/
│   ├── 04-generacion-plan-implementacion-hu.md     # MIG-RST-003
│   ├── 06-implementacion-hu-asistida-por-ia.md     # MIG-RST-010 + MIG-TERM-005
│   ├── 09-ecosystem-discovery-feature-design.md    # MIG-RST-004
│   ├── 10-alineamiento-convenciones-repositorio.md # MIG-RST-005
│   ├── 12-analisis-granularidad-hus-multi-repo.md  # MIG-RST-006
│   ├── 15-protocolo-verificacion-validation-gate.md # MIG-TERM-001, MIG-TERM-002
│   ├── 16-validation-gate-historias-usuario.md      # MIG-TERM-003
│   └── 17-validation-gate-epicas.md                 # MIG-TERM-004
└── patron/
    ├── 01-tech-design-stack-aware.md               # MIG-RST-011
    ├── 02-analisis-agnostico-codigo-fuente.md      # MIG-RST-007
    ├── 03-ecosystem-discovery-agnostico.md         # MIG-RST-008
    ├── 04-analisis-intercomunicacion-ecosistema.md # MIG-RST-009
    └── 07-validacion-tecnica-dependencias.md       # MIG-RST-010
```

**Structure Decision**: No code structure needed. Source files are the katas themselves. Output structure is `specs/006-katas-normalization/outputs/` for normalization reports.

## Processing Priority

Based on `migration-roadmap.md`, processing order:

| Priority | Kata | Task IDs | Type |
|----------|------|----------|------|
| 1 | principios/00-raise-katas-documentation.md | MIG-RST-001 | Jidoka |
| 2 | principios/01-raise-kata-execution-protocol.md | MIG-RST-002 | Jidoka |
| 3 | flujo/04-generacion-plan-implementacion-hu.md | MIG-RST-003 | Jidoka |
| 4 | flujo/09-ecosystem-discovery-feature-design.md | MIG-RST-004 | Jidoka |
| 5 | flujo/10-alineamiento-convenciones-repositorio.md | MIG-RST-005 | Jidoka |
| 6 | flujo/12-analisis-granularidad-hus-multi-repo.md | MIG-RST-006 | Jidoka |
| 7 | patron/02-analisis-agnostico-codigo-fuente.md | MIG-RST-007 | Jidoka |
| 8 | patron/03-ecosystem-discovery-agnostico.md | MIG-RST-008 | Jidoka |
| 9 | patron/04-analisis-intercomunicacion-ecosistema.md | MIG-RST-009 | Jidoka |
| 10 | patron/07-validacion-tecnica-dependencias.md | MIG-RST-010 | Jidoka |
| 11 | patron/01-tech-design-stack-aware.md | MIG-RST-011 | Jidoka |
| 12 | flujo/15-protocolo-verificacion-validation-gate.md | MIG-TERM-001,002 | Terminology |
| 13 | flujo/16-validation-gate-historias-usuario.md | MIG-TERM-003 | Terminology |
| 14 | flujo/17-validation-gate-epicas.md | MIG-TERM-004 | Terminology |
| 15 | flujo/06-implementacion-hu-asistida-por-ia.md | MIG-RST-010, MIG-TERM-005 | Both |

## Normalization Workflow Per Kata

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Read kata file                                           │
├─────────────────────────────────────────────────────────────┤
│ 2. Semantic coherence check                                 │
│    ├─ If misaligned → STOP, flag for reclassification      │
│    └─ If aligned → continue                                 │
├─────────────────────────────────────────────────────────────┤
│ 3. Identify steps lacking Jidoka Inline structure          │
│    ├─ Missing **Verificación:** → Add                       │
│    └─ Missing > **Si no puedes continuar:** → Add          │
├─────────────────────────────────────────────────────────────┤
│ 4. Identify deprecated terminology                         │
│    ├─ DoD → Validation Gate                                │
│    ├─ Developer (role) → Orquestador                       │
│    ├─ Rule (governance) → Guardrail                        │
│    └─ L0/L1/L2/L3 → principios/flujo/patrón/técnica       │
├─────────────────────────────────────────────────────────────┤
│ 5. Apply changes (preserve existing content)               │
├─────────────────────────────────────────────────────────────┤
│ 6. Generate normalization report                           │
├─────────────────────────────────────────────────────────────┤
│ 7. Present to Orquestador for validation                   │
│    ├─ Approved → Commit, proceed to next kata              │
│    ├─ Changes requested → Adjust, re-validate              │
│    └─ Skip → Move to next kata without changes             │
└─────────────────────────────────────────────────────────────┘
```

## Jidoka Inline Format Reference

From `20-glossary-v2.1.md`:

```markdown
### Paso N: [Acción]
[Instrucciones]
**Verificación:** [Cómo saber si funcionó]
> **Si no puedes continuar:** [Causa → Resolución]
```

## Terminology Mapping Reference

| Deprecated | Canonical | Context |
|------------|-----------|---------|
| DoD | Validation Gate | Quality checkpoint |
| Developer | Orquestador | Human role in RaiSE |
| Rule | Guardrail | Governance directive |
| L0 | principios | Kata level |
| L1 | flujo | Kata level |
| L2 | patrón | Kata level |
| L3 | técnica | Kata level |

## Complexity Tracking

> No violations detected. All changes are minimal structural additions.

| Aspect | Complexity Level | Justification |
|--------|------------------|---------------|
| Jidoka addition | Low | Append-only; no content rewrite |
| Terminology replacement | Low | Find-replace with context awareness |
| Coherence validation | Medium | Requires human judgment |
