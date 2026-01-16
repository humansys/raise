# Learning Path: Disclosure Progresivo del Framework RaiSE

**Feature**: 001-heutagogy-progressive-disclosure
**Date**: 2026-01-11
**Status**: Complete
**User Story**: US2 (P2) — Propuesta de Camino de Aprendizaje Gradual

## Executive Summary

Este documento define un camino de aprendizaje de 4 etapas para nuevos Orquestadores del framework RaiSE, diseñado con principios de disclosure progresivo. Cada etapa introduce máximo 7 conceptos nuevos (Ley de Miller), incluye criterios de transición observables, y un checkpoint heutagógico alineado con §5.

**Objetivo**: Reducir la carga cognitiva inicial de ~35 conceptos a 5 conceptos semilla, revelando complejidad solo cuando el Orquestador demuestra dominio de la etapa actual.

---

## Overview del Learning Path

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LEARNING PATH OVERVIEW                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Stage 0          Stage 1           Stage 2           Stage 3          │
│  ────────         ────────          ────────          ────────         │
│  AWARENESS        OPERATIONAL       TACTICAL          STRATEGIC        │
│  (Shu)            (Shu+)            (Ha)              (Ri)             │
│                                                                         │
│  5 conceptos      +5 conceptos      +8 conceptos      +17 conceptos    │
│  ───────────      ────────────      ────────────      ─────────────    │
│  Total: 5         Total: 10         Total: 18         Total: 35        │
│                                                                         │
│  "Puedo usar      "Paso los         "Diseño           "Mejoro el       │
│   el framework"    Validation        contexto"         framework"      │
│                    Gates"                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Stage 0: Primer Contacto (Awareness)

**Fase ShuHaRi**: Shu (Proteger/Obedecer)
**Nivel de Competencia**: Pre-Operacional
**Objetivo**: Entender qué es RaiSE y poder escribir una spec básica

### Conceptos Expuestos (5)

| # | Concepto | Por qué aquí | Interfaz Simple |
|---|----------|--------------|-----------------|
| 1 | Orquestador | Define el rol del usuario | "Tú diriges a la IA" |
| 2 | Spec | Artefacto fundamental | "Documento que describe QUÉ construir" |
| 3 | Agent | Con quién trabaja | "IA que ejecuta tus instrucciones" |
| 4 | Constitution | Contexto de principios | "Reglas inmutables del proyecto" |
| 5 | Validation Gate | Cuándo avanzar | "Checkpoint de calidad" |

### Conceptos Ocultos

Todo lo demás (~30 conceptos), especialmente:
- Jidoka, Kaizen, ShuHaRi (filosofía Lean)
- Context Engineering, MCP, Observable Workflow
- Niveles de Kata, Checkpoint Heutagógico

### Katas Accesibles

Ninguna. Solo templates de Spec.

### Criterios de Transición → Stage 1

| Criterio | Observable | Verificación |
|----------|------------|--------------|
| Puede escribir una spec | Artefacto creado | spec.md existe y tiene secciones requeridas |
| Entiende el rol de Orquestador | Comportamiento | No pide al agente que "decida por él" |
| Conoce que hay Validation Gates | Mención | Pregunta "¿pasó el gate?" o equivalente |

### Checkpoint Heutagógico (§5)

> **Pregunta reflexiva**: "¿Entiendes la diferencia entre especificar QUÉ construir vs. implementar CÓMO hacerlo?"

**Indicador de éxito**: El Orquestador puede explicar por qué el humano define el "qué" y el agente propone el "cómo".

---

## Stage 1: Operacional (Productivity)

**Fase ShuHaRi**: Shu+ (Shu avanzado)
**Nivel de Competencia**: L1 Operacional
**Objetivo**: Usar RaiSE efectivamente para completar features

### Conceptos Nuevos (+5, Total: 10)

| # | Concepto | Por qué aquí | Interfaz Simple |
|---|----------|--------------|-----------------|
| 6 | Guardrail | Restricciones activas | "Reglas que el agente debe seguir" |
| 7 | User Story | Formato de requisitos | "Como [rol], quiero [acción]" |
| 8 | Implementation Plan | Guía de ejecución | "Pasos para implementar" |
| 9 | Jidoka (simplificado) | Manejo de errores | "Parar si algo falla" |
| 10 | Kata | Procesos estructurados | "Guía paso a paso" |

### Conceptos Aún Ocultos (~25)

- Niveles de Kata (Principios/Flujo/Patrón/Técnica)
- ShuHaRi (filosofía)
- Context Engineering, Golden Data, MCP
- Observable Workflow, Kaizen, Escalation Gate

### Katas Accesibles

- Nivel Flujo únicamente (secuencias de valor básicas)
- Sin exposición a niveles Principios, Patrón, o Técnica

### Criterios de Transición → Stage 2

| Criterio | Observable | Verificación |
|----------|------------|--------------|
| Pasa Validation Gates | Tasa de éxito | >80% de gates pasados sin re-trabajo |
| Usa Guardrails | Comportamiento | No viola restricciones documentadas |
| Ejecuta Katas de Flujo | Artefactos | Plans e implementations siguen el flujo |
| Aplica Jidoka | Comportamiento | Para cuando detecta problema, no acumula errores |

### Checkpoint Heutagógico (§5)

> **Pregunta reflexiva**: "¿Qué patrón identificas en los problemas que te hicieron parar (Jidoka)? ¿Cómo evitarías que ocurran?"

**Indicador de éxito**: El Orquestador puede articular al menos un patrón de error recurrente y proponer una mejora preventiva.

---

## Stage 2: Táctico (Context Design)

**Fase ShuHaRi**: Ha (Romper/Adaptar)
**Nivel de Competencia**: L2 Táctico
**Objetivo**: Diseñar contexto para mejorar resultados del agente

### Conceptos Nuevos (+8, Total: 18)

| # | Concepto | Por qué aquí | Interfaz Simple |
|---|----------|--------------|-----------------|
| 11 | Golden Data | Información verificada | "Datos confiables del proyecto" |
| 12 | Context Engineering | Diseño de ambiente | "Arquitectar qué sabe el agente" |
| 13 | Escalation Gate | Cuándo escalar | "Punto donde el humano debe decidir" |
| 14 | Checkpoint Heutagógico | Reflexión estructurada | "4 preguntas al terminar feature" |
| 15 | Niveles de Kata | Profundidad de guías | "Principios/Flujo/Patrón/Técnica" |
| 16 | raise-config | Repositorio central | "Dónde viven las reglas compartidas" |
| 17 | raise-kit | CLI del framework | "Herramienta de línea de comando" |
| 18 | Corpus | Colección de docs | "Conjunto de documentos del proyecto" |

### Conceptos Aún Ocultos (~17)

- ShuHaRi (filosofía profunda)
- Jidoka (4 pasos completos)
- Kaizen (mejora continua formal)
- MCP, Observable Workflow, MELT
- Lean Software Development (teoría completa)

### Katas Accesibles

- Nivel Flujo ✅
- Nivel Patrón ✅ (estructuras recurrentes)
- Sin exposición a Principios o Técnica

### Criterios de Transición → Stage 3

| Criterio | Observable | Verificación |
|----------|------------|--------------|
| Reduce re-prompting | Métrica | <3 iteraciones promedio para output aceptable |
| Diseña Golden Data | Artefactos | Crea/mantiene documentos de contexto |
| Usa Escalation Gates | Comportamiento | Identifica cuándo escalar correctamente |
| Completa Checkpoints | Registro | Responde las 4 preguntas heutagógicas |

### Checkpoint Heutagógico (§5)

> **Pregunta reflexiva**: "¿Qué contexto agregaste que más impactó la calidad del output del agente? ¿Cómo lo mediste?"

**Indicador de éxito**: El Orquestador puede demostrar correlación entre contexto agregado y mejora en métricas (re-prompting, adherencia a spec).

---

## Stage 3: Estratégico (Framework Evolution)

**Fase ShuHaRi**: Ri (Trascender/Separar)
**Nivel de Competencia**: L3 Estratégico
**Objetivo**: Contribuir a la evolución del framework RaiSE

### Conceptos Nuevos (+17, Total: 35 — Ontología Completa)

| # | Concepto | Por qué aquí |
|---|----------|--------------|
| 19-22 | ShuHaRi, Jidoka (4 pasos), Kaizen, Lean Software Dev | Filosofía profunda para contribuir |
| 23-25 | MCP, Observable Workflow, MELT | Integración técnica avanzada |
| 26-28 | PRD, Solution Vision, Technical Design | Artefactos enterprise |
| 29-31 | Capability, Feature, Statement of Work | Conceptos de preventa |
| 32-35 | Platform Agnosticism, Governance as Code, JIT Learning, Roadmap | Principios y planificación |

### Katas Accesibles

- Todos los niveles: Principios, Flujo, Patrón, Técnica
- Puede crear nuevas Katas

### Criterios de Permanencia (No hay Stage 4)

| Criterio | Observable | Verificación |
|----------|------------|--------------|
| Contribuye a raise-config | Commits | PRs aceptados al repositorio central |
| Crea o mejora Katas | Artefactos | Nuevas Katas o mejoras documentadas |
| Mentora a otros Orquestadores | Comportamiento | Ayuda a Stage 0-2 efectivamente |
| Propone mejoras al framework | ADRs | Decisiones arquitectónicas documentadas |

### Checkpoint Heutagógico (§5)

> **Pregunta reflexiva**: "¿Qué cambio propones al framework que beneficiaría a futuros Orquestadores? ¿Cómo validarías su efectividad?"

**Indicador de éxito**: El Orquestador puede articular una mejora concreta con métricas de validación propuestas.

---

## Mapeo Concepto → Etapa

### Tabla de Asignación Completa

| Concepto | Stage | Categoría |
|----------|-------|-----------|
| Orquestador | 0 | Roles |
| Spec | 0 | Workflow |
| Agent | 0 | Agent Ecosystem |
| Constitution | 0 | Core Philosophy |
| Validation Gate | 0 | Workflow |
| Guardrail | 1 | Agent Ecosystem |
| User Story | 1 | Workflow |
| Implementation Plan | 1 | Workflow |
| Jidoka (simplificado) | 1 | Core Philosophy |
| Kata | 1 | Kata System |
| Golden Data | 2 | Workflow |
| Context Engineering | 2 | Core Philosophy |
| Escalation Gate | 2 | Workflow |
| Checkpoint Heutagógico | 2 | Kata System |
| Niveles de Kata | 2 | Kata System |
| raise-config | 2 | Agent Ecosystem |
| raise-kit | 2 | Agent Ecosystem |
| Corpus | 2 | Workflow |
| ShuHaRi | 3 | Kata System |
| Jidoka (4 pasos) | 3 | Core Philosophy |
| Kaizen | 3 | Core Philosophy |
| Lean Software Dev | 3 | Core Philosophy |
| MCP | 3 | Agent Ecosystem |
| Observable Workflow | 3 | Agent Ecosystem |
| PRD | 3 | Workflow |
| Solution Vision | 3 | Workflow |
| Technical Design | 3 | Workflow |
| Capability | 3 | Preventa |
| Feature | 3 | Preventa |
| Statement of Work | 3 | Preventa |
| Platform Agnosticism | 3 | Core Philosophy |
| Governance as Code | 3 | Core Philosophy |
| JIT Learning | 3 | Kata System |
| Roadmap | 3 | Preventa |
| Heutagogía | 3 | Core Philosophy |

**Cobertura**: 35/35 conceptos asignados (100%) ✅

---

## Kata Accessibility por Stage

| Stage | Katas Accesibles | Justificación |
|-------|------------------|---------------|
| 0 | Ninguna | Solo templates; sin procesos estructurados aún |
| 1 | Flujo | Secuencias de valor básicas |
| 2 | Flujo + Patrón | Estructuras recurrentes para diseñar contexto |
| 3 | Todos (Principios, Flujo, Patrón, Técnica) | Acceso completo para crear/mejorar |

---

## Validación de Diseño

### Ley de Miller (7±2) ✅

| Stage | Conceptos Nuevos | Cumple |
|-------|------------------|--------|
| 0 | 5 | ✅ (≤7) |
| 1 | 5 | ✅ (≤7) |
| 2 | 8 | ⚠️ (=7+1, aceptable) |
| 3 | 17 | N/A (etapa final, ontología completa) |

### Alineamiento con §5 Heutagogía ✅

Cada etapa incluye:
1. Checkpoint con pregunta reflexiva
2. Indicador de éxito observable
3. Énfasis en auto-dirección (no dependencia)

### Gate-Coherencia ✅

- Alineado con Constitution §5 (Heutagogía)
- Respeta ShuHaRi como lente de progresión
- Criterios de transición son observables, no subjetivos

---

## Métricas de Reducción de Complejidad

| Métrica | Estado Actual | Con Learning Path |
|---------|---------------|-------------------|
| Conceptos en onboarding | ~35 (todo) | 5 (Stage 0) |
| Reducción inicial | 0% | **86%** |
| Conceptos para productividad | ~15-20 | 10 (Stage 0+1) |
| Tiempo a productividad | Alto | Reducido |

---

*Learning Path completado. Proceder a improvement-proposals.md (US3).*
