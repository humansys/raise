# Data Model: Evaluación Ontológica para Disclosure Progresivo

**Feature**: 001-heutagogy-progressive-disclosure
**Date**: 2026-01-11
**Status**: Complete

## Overview

Este documento define el modelo de entidades para el análisis ontológico y la propuesta de disclosure progresivo.

---

## Entidades del Análisis

### 1. Concepto Ontológico

Representa un término definido en la ontología RaiSE v2.1.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `id` | string | Identificador único (ej. `concept-orquestador`) |
| `term` | string | Nombre canónico del término |
| `category` | enum | `core_philosophy`, `workflow`, `agent_ecosystem`, `kata_system`, `roles` |
| `complexity` | enum | `basic`, `intermediate`, `advanced` |
| `dependencies` | array[string] | IDs de conceptos prerequisito |
| `shuhari_phase` | enum | `shu`, `ha`, `ri` |
| `is_seed` | boolean | Si es concepto semilla para fase Shu |
| `learning_stage` | integer | Etapa del Learning Path (0-3) |
| `source_document` | string | Documento donde se define |
| `novice_utility` | enum | `high`, `medium`, `low` |

**Ejemplo**:
```yaml
id: concept-orquestador
term: Orquestador
category: roles
complexity: basic
dependencies: []
shuhari_phase: shu
is_seed: true
learning_stage: 0
source_document: 20-glossary-v2.1.md
novice_utility: high
```

---

### 2. Barrera de Entrada

Representa un obstáculo identificado para la adopción del framework.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `id` | string | Identificador único |
| `type` | enum | `conceptual`, `terminological`, `structural` |
| `description` | string | Descripción del obstáculo |
| `affected_concepts` | array[string] | IDs de conceptos afectados |
| `severity` | enum | `high`, `medium`, `low` |
| `lean_waste` | enum | `muda`, `mura`, `muri` |
| `proposed_mitigation` | string | Cómo reducir/eliminar |

**Ejemplo**:
```yaml
id: barrier-japanese-overload
type: terminological
description: Demasiados términos japoneses expuestos simultáneamente (Kata, Jidoka, Kaizen, ShuHaRi)
affected_concepts: [concept-kata, concept-jidoka, concept-kaizen, concept-shuhari]
severity: medium
lean_waste: muri
proposed_mitigation: Disclosure progresivo por etapa; solo Kata en fase Shu
```

---

### 3. Etapa de Aprendizaje

Representa una fase del Learning Path propuesto.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `id` | string | Identificador (ej. `stage-0-awareness`) |
| `number` | integer | Número de etapa (0-3) |
| `name` | string | Nombre descriptivo |
| `shuhari_phase` | enum | Fase ShuHaRi correspondiente |
| `orchestrator_level` | string | Nivel de competencia objetivo |
| `concepts_exposed` | array[string] | IDs de conceptos disponibles |
| `katas_accessible` | array[string] | Tipos de Kata accesibles |
| `transition_criteria` | string | Cómo saber que pasó a siguiente etapa |
| `heutagogic_checkpoint` | string | Pregunta reflexiva de la etapa |

**Ejemplo**:
```yaml
id: stage-0-awareness
number: 0
name: Primer Contacto
shuhari_phase: shu
orchestrator_level: Pre-Operacional
concepts_exposed: [concept-orquestador, concept-spec, concept-validation-gate]
katas_accessible: []
transition_criteria: Puede escribir una spec simple siguiendo template
heutagogic_checkpoint: "¿Entiendes la diferencia entre especificar QUÉ vs. implementar CÓMO?"
```

---

### 4. Mejora Propuesta

Representa un cambio sugerido a la ontología v2.1.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `id` | string | Identificador único |
| `title` | string | Nombre descriptivo |
| `type` | enum | `quick_win`, `structural`, `fundamental` |
| `description` | string | Descripción del cambio |
| `rationale` | string | Justificación (qué barrera elimina) |
| `affected_documents` | array[string] | Documentos a modificar |
| `constitution_impact` | boolean | Si requiere enmienda de Constitution |
| `complexity_reduction` | integer | % estimado de reducción de complejidad inicial |
| `priority` | enum | `high`, `medium`, `low` |
| `effort` | enum | `small`, `medium`, `large` |

**Ejemplo**:
```yaml
id: improvement-simplify-jidoka
title: Simplificar exposición de Jidoka
type: quick_win
description: En documentos de onboarding, presentar Jidoka como "parar si falla" sin los 4 pasos detallados
rationale: Elimina barrera terminológica (Muri) sin perder concepto esencial
affected_documents: [25-ontology-bundle-v2_1.md, 05-learning-philosophy-v2.md]
constitution_impact: false
complexity_reduction: 10
priority: high
effort: small
```

---

## Relaciones entre Entidades

```
┌─────────────────────┐
│ Concepto Ontológico │
└─────────┬───────────┘
          │ 1:N
          │ tiene
          ▼
┌─────────────────────┐
│ Barrera de Entrada  │
└─────────┬───────────┘
          │ 1:N
          │ propone
          ▼
┌─────────────────────┐
│  Mejora Propuesta   │
└─────────────────────┘

┌─────────────────────┐
│ Etapa de Aprendizaje│◄────────────┐
└─────────┬───────────┘             │
          │ N:M                     │ asigna
          │ expone                  │
          ▼                         │
┌─────────────────────┐             │
│ Concepto Ontológico │─────────────┘
└─────────────────────┘
```

---

## Clasificación Inicial de Conceptos

### Conceptos Semilla (Fase Shu, Stage 0-1)

| Concepto | Complejidad | Dependencias | Utility |
|----------|-------------|--------------|---------|
| Orquestador | basic | 0 | high |
| Spec | basic | 1 | high |
| Validation Gate | basic | 1 | high |
| Guardrail | basic | 1 | high |
| Constitution | basic | 0 | medium |
| Kata | basic | 0 | medium |
| Jidoka (simplificado) | basic | 0 | medium |

### Conceptos Intermedios (Fase Ha, Stage 2)

| Concepto | Complejidad | Dependencias | Utility |
|----------|-------------|--------------|---------|
| Context Engineering | intermediate | 3 | medium |
| Golden Data | intermediate | 2 | medium |
| Escalation Gate | intermediate | 2 | medium |
| Niveles de Kata | intermediate | 1 | medium |
| Checkpoint Heutagógico | intermediate | 2 | medium |

### Conceptos Avanzados (Fase Ri, Stage 3)

| Concepto | Complejidad | Dependencias | Utility |
|----------|-------------|--------------|---------|
| Observable Workflow | advanced | 4 | low |
| MCP | advanced | 3 | low |
| ShuHaRi (filosofía) | advanced | 3 | low |
| Jidoka (4 pasos) | advanced | 2 | low |
| MELT Framework | advanced | 4 | low |

---

## Métricas de Validación

| Métrica | Target | Cómo medir |
|---------|--------|------------|
| Conceptos clasificados | 100% | Todos los términos del glosario tienen `learning_stage` |
| Conceptos semilla | 5-9 | Conteo de `is_seed: true` |
| Cobertura de etapas | 80%+ | % de conceptos con `learning_stage` asignado |
| Reducción inicial | 30%+ | % de conceptos NOT expuestos en Stage 0 vs. total |

---

*Data model completado. Proceder a quickstart.md.*
