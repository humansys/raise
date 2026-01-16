# Implementation Plan: Ciclos de Trabajo RaiSE

**Branch**: `004-operation-layers` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-operation-layers/spec.md`

## Summary

Crear documento ontológico `26-work-cycles-v2.1.md` que defina los cuatro ciclos de trabajo de RaiSE (Onboarding, Proyecto, Feature, Mejora), clarificando dónde opera spec-kit (solo Ciclo Feature) y referenciando las katas existentes que implementan el Ciclo de Onboarding. Actualizar glosario con entrada "Work Cycle".

## Technical Context

**Language/Version**: Markdown (CommonMark spec)
**Primary Dependencies**: Git 2.0+ (versionado)
**Storage**: Archivos .md en repositorio Git
**Testing**: Validation Gates (Gate-Terminología, Gate-Coherencia, Gate-Estructura)
**Target Platform**: Repositorio raise-commons (docs/framework/v2.1/model/)
**Project Type**: Documentación ontológica (no código)
**Performance Goals**: N/A (documentación estática)
**Constraints**: Coherencia semántica con ontología existente, formato consistente con v2.1
**Scale/Scope**: 1 documento nuevo + 1 actualización de glosario

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*Reference: `.specify/memory/constitution.md`*

| Principio | Verificación | Estado |
|-----------|--------------|--------|
| I. Coherencia Semántica | Términos "Work Cycle" y ciclos alineados con glosario (pendiente actualización) | [x] |
| II. Governance como Código | Documento versionado en Git, branch dedicada | [x] |
| III. Validación en Cada Fase | Gates: Gate-Terminología, Gate-Coherencia, Gate-Estructura | [x] |
| IV. Simplicidad | 4 ciclos, 1 tabla resumen, sin abstracciones adicionales (KISS) | [x] |
| V. Mejora Continua | Documento describe estructura existente, permite iteración futura | [x] |

## Project Structure

### Documentation (this feature)

```text
specs/004-operation-layers/
├── spec.md              # Feature specification (completado)
├── plan.md              # This file
├── research.md          # Phase 0: Análisis de katas existentes
├── data-model.md        # Phase 1: Modelo de entidades (Work Cycle schema)
├── quickstart.md        # Phase 1: Guía rápida de uso del documento
├── checklists/
│   └── requirements.md  # Checklist de calidad (completado)
└── tasks.md             # Phase 2: Tareas de implementación
```

### Target Artifacts (repository root)

```text
docs/framework/v2.1/model/
├── 20-glossary-v2.1.md          # Actualizar con "Work Cycle"
├── 21-methodology-v2.md         # Referencia (sin cambios)
├── 26-work-cycles-v2.1.md       # NUEVO: Documento principal
└── kata-shuhari-schema-v2.1.md  # Referencia (sin cambios)

src/katas/cursor_rules/          # Fuente de verdad para Ciclo Onboarding
├── L0-01-gestion-integral-reglas-cursor.md
├── L2-01-analisis-exploratorio-repositorio.md
├── L2-02-inicializacion-gobernanza-reglas.md
└── ... (otras katas referenciadas)
```

**Structure Decision**: Documentación ontológica pura. El artefacto principal es un documento Markdown que define conceptos, no código ejecutable.

## Complexity Tracking

> No hay violaciones de Constitution. El plan es minimal y alineado con KISS/YAGNI.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Phase 0: Research

### Objetivo

Consolidar el conocimiento de las katas existentes que implementan el Ciclo de Onboarding y validar el mapeo de ciclos a fases RaiSE.

### Tareas de Investigación

1. **Análisis de katas de Onboarding**: Confirmar que L0-01, L2-01, L2-02 cubren el ciclo completo
2. **Mapeo Fases-Ciclos**: Validar que el mapeo propuesto (Fases 0-3 → Proyecto, Fases 4-6 → Feature, Fase 7+ → Mejora) es coherente con 21-methodology-v2.md
3. **Cobertura spec-kit**: Confirmar qué comandos de spec-kit mapean a qué fases

### Output

→ `research.md` con decisiones y rationale

---

## Phase 1: Design

### Objetivo

Definir el modelo de datos (schema de Work Cycle) y generar guía de uso.

### Artefactos

1. **data-model.md**: Schema de Work Cycle (atributos: trigger, unidad, fases, katas, cobertura)
2. **quickstart.md**: Cómo usar el documento de ciclos (para Orquestadores)

### Output

→ `data-model.md`, `quickstart.md`

---

## Phase 2: Tasks

> Generado por `/speckit.tasks` (no por este comando)

Tareas esperadas:
1. Crear `26-work-cycles-v2.1.md` con estructura y contenido
2. Actualizar `20-glossary-v2.1.md` con entrada "Work Cycle"
3. Validar contra Gates (Terminología, Coherencia, Estructura)
4. Crear MR para revisión
