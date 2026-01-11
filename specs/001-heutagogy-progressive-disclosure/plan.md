# Implementation Plan: Evaluación Ontológica para Disclosure Progresivo Heutagógico

**Branch**: `001-heutagogy-progressive-disclosure` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-heutagogy-progressive-disclosure/spec.md`

## Summary

Realizar una evaluación sistemática de la ontología RaiSE v2.1 desde la perspectiva heutagógica, con el objetivo de diseñar un camino de "disclosure progresivo" que revele la complejidad del framework gradualmente. El trabajo producirá: (1) auditoría de complejidad ontológica, (2) propuesta de Learning Path por etapas, y (3) lista priorizada de mejoras pre-avance.

## Technical Context

> *Nota: Este es trabajo de análisis conceptual, no desarrollo de software tradicional.*

**Tipo de trabajo**: Análisis ontológico / Diseño de currículo de aprendizaje
**Documentos de entrada**:
- `docs/framework/v2.1/model/00-constitution-v2.md` (8 principios)
- `docs/framework/v2.1/model/20-glossary-v2.1.md` (~40 términos)
- `docs/framework/v2.1/model/21-methodology-v2.md` (8 fases)
- `docs/framework/v2.1/adrs/*.md` (11 ADRs)

**Frameworks de análisis**:
- Lean (Muda/Mura/Muri) para desperdicio conceptual
- ShuHaRi como lente de progresión del Orquestador
- Ley de Miller (7±2) para carga cognitiva

**Artefactos de salida**:
- `audit-report.md` — Inventario de conceptos con niveles de complejidad
- `learning-path.md` — 3-5 etapas de adopción progresiva
- `improvement-proposals.md` — Mejoras priorizadas con formato ADR-lite

**Validación**: Diferida a uso real por Orquestadores (hipótesis a refinar)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*Reference: `.specify/memory/constitution.md`*

| Principio | Verificación | Estado |
|-----------|--------------|--------|
| I. Coherencia Semántica | Usa términos del glosario v2.1 (Orquestador, Validation Gate, ShuHaRi, Kata) | [x] |
| II. Governance como Código | Artefactos serán Markdown versionados en Git en feature directory | [x] |
| III. Validación en Cada Fase | Gates definidos: Gate-Terminología, Gate-Coherencia, Gate-Trazabilidad | [x] |
| IV. Simplicidad | Objetivo es REDUCIR conceptos expuestos, no agregar | [x] |
| V. Mejora Continua | Learning Path es hipótesis a refinar con feedback real | [x] |

**Estado del Gate**: ✅ PASS — Proceder a Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-heutagogy-progressive-disclosure/
├── spec.md              # Feature specification ✅
├── plan.md              # This file ✅
├── research.md          # Phase 0: Patrones de disclosure y análisis de complejidad
├── data-model.md        # Phase 1: Modelo de entidades (Concepto, Barrera, Etapa, Mejora)
├── quickstart.md        # Phase 1: Guía de ejecución del análisis
├── checklists/          # Validación de calidad
│   └── requirements.md  # ✅
└── tasks.md             # Phase 2: Tareas atómicas (generado por /speckit.tasks)
```

### Source Structure (Artefactos Finales)

```text
specs/001-heutagogy-progressive-disclosure/
├── audit-report.md          # Entregable P1: Inventario de complejidad
├── learning-path.md         # Entregable P2: Camino de aprendizaje gradual
└── improvement-proposals.md # Entregable P3: Mejoras priorizadas
```

**Structure Decision**: Todos los artefactos residen en el feature directory hasta validación, luego pueden integrarse a `docs/framework/v2.1/` mediante PR.

## Complexity Tracking

> Sin violaciones de Constitution Check. No se requiere justificación de complejidad adicional.

---

*Plan generado por `/speckit.plan`. Continuar con Phase 0 (research.md).*
