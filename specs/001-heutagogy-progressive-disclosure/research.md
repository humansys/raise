# Research: Disclosure Progresivo Heutagógico

**Feature**: 001-heutagogy-progressive-disclosure
**Date**: 2026-01-11
**Status**: Complete

## Executive Summary

Este research analiza la ontología RaiSE v2.1 para identificar patrones de disclosure progresivo existentes y proponer una estrategia coherente para reducir la curva de aprendizaje de nuevos Orquestadores.

**Hallazgo principal**: Ya existe un patrón de disclosure progresivo en ADR-009 (ShuHaRi Hybrid). Este patrón puede extenderse sistemáticamente a toda la ontología.

---

## 1. Análisis de Complejidad Ontológica

### 1.1 Inventario de Conceptos

Basado en el análisis del glosario v2.1 y ontology-bundle, se identifican **~35 términos canónicos** organizados en 5 categorías:

| Categoría | # Términos | Ejemplos |
|-----------|------------|----------|
| **Core Philosophy** | 8 | Constitution, Heutagogía, Jidoka, Kaizen, Context Engineering |
| **Workflow Entities** | 10 | Spec, Plan, Task, User Story, Validation Gate, Escalation Gate |
| **Agent Ecosystem** | 6 | Agent, Guardrail, MCP, Golden Data, Corpus, Observable Workflow |
| **Kata System** | 5 | Kata, ShuHaRi, Principios/Flujo/Patrón/Técnica |
| **Roles & Actions** | 6 | Orquestador, Checkpoint Heutagógico, JIT Learning |

### 1.2 Matriz de Complejidad

Cada concepto evaluado en 3 dimensiones:

| Concepto | Complejidad Intrínseca | Dependencias | Utilidad Novato |
|----------|------------------------|--------------|-----------------|
| Orquestador | Baja | 0 | ⭐⭐⭐ Alta |
| Spec | Baja | 1 (Template) | ⭐⭐⭐ Alta |
| Validation Gate | Media | 2 (Fase, Criterios) | ⭐⭐⭐ Alta |
| Constitution | Media | 0 | ⭐⭐ Media |
| Guardrail | Media | 2 (Scope, Enforcement) | ⭐⭐ Media |
| Kata | Alta | 4 (Level, Audience, Jidoka, ShuHaRi) | ⭐ Baja |
| Context Engineering | Alta | 3 (Golden Data, MCP, Guardrails) | ⭐ Baja |
| Observable Workflow | Alta | 4 (MELT, Traces, Metrics) | ⭐ Baja |
| ShuHaRi | Alta | 3 (Shu, Ha, Ri + Kata) | ⭐ Baja |
| Jidoka | Alta | 2 (Detectar→Parar→Corregir→Continuar) | ⭐ Baja |

### 1.3 Grafo de Dependencias

```
Constitution
    ├── Guardrail ← Agent
    ├── Validation Gate
    │       └── Escalation Gate
    └── Heutagogía
            └── Checkpoint Heutagógico

Kata
    ├── Niveles (Principios/Flujo/Patrón/Técnica)
    ├── Audience (beginner/intermediate/advanced)
    ├── ShuHaRi (filosofía interna)
    └── Jidoka (inline en pasos)

Context Engineering
    ├── Golden Data
    ├── Corpus
    ├── MCP
    └── Observable Workflow
            └── MELT (Metrics, Events, Logs, Traces)
```

---

## 2. Patrones de Disclosure Existentes

### 2.1 ADR-009: ShuHaRi Hybrid (Patrón de Referencia)

**Decisión**: ShuHaRi es filosofía de diseño interno; el usuario ve `audience: beginner/intermediate/advanced`.

**Principios aplicados**:
1. **Progressive Disclosure**: Filosofía disponible en docs avanzados, no requerida para uso
2. **Familiar Interface**: Términos universales en software
3. **Rich Foundation**: Diseño sigue progresión ShuHaRi internamente
4. **Marketing Differentiation**: ShuHaRi para talks/blogs externos

**Implicación**: Este patrón puede replicarse para otros conceptos complejos.

### 2.2 Ontology Bundle (Simplificación Existente)

El documento `25-ontology-bundle-v2_1.md` ya representa un intento de disclosure progresivo:
- ~45KB vs. corpus completo (~200KB+)
- Consolidación de Constitution, Glossary, Data Architecture
- Diseñado para transferencia cross-project

**Limitación identificada**: Es un "snapshot" estático, no un camino de aprendizaje gradual.

### 2.3 Niveles de Competencia del Orquestador

La learning-philosophy-v2.md define 3 niveles:

| Nivel | Competencia | Indicador |
|-------|-------------|-----------|
| L1: Operacional | Usa RaiSE efectivamente | Pasa Validation Gates |
| L2: Táctico | Diseña contexto | Reduce re-prompting |
| L3: Estratégico | Mejora el framework | Contribuye a raise-config |

**Oportunidad**: Mapear conceptos a estos niveles de competencia.

---

## 3. Frameworks de Análisis Aplicados

### 3.1 Ley de Miller (7±2)

**Aplicación**: Identificar "conceptos semilla" que no excedan la carga cognitiva.

**Propuesta de conceptos semilla** (fase Shu, máximo 7):
1. Orquestador
2. Spec
3. Validation Gate
4. Guardrail
5. Kata (solo concepto, sin niveles)
6. Constitution (solo existencia)
7. Jidoka (solo "parar si algo falla")

### 3.2 Análisis Lean (Muda/Mura/Muri)

| Desperdicio | Manifestación en Ontología | Propuesta |
|-------------|---------------------------|-----------|
| **Muda** (desperdicio) | Términos redundantes: "Rule" aún aparece como alias | Eliminar aliases en docs primarios |
| **Mura** (irregularidad) | Inconsistencia en profundidad documental | Estandarizar profundidad por nivel |
| **Muri** (sobrecarga) | Exponer ShuHaRi/Jidoka/Kaizen juntos | Disclosure progresivo por etapa |

### 3.3 Modelo ShuHaRi como Lente de Progresión

| Fase | Qué exponer | Qué ocultar |
|------|-------------|-------------|
| **Shu** (Proteger) | 7 conceptos semilla, flujo básico | Filosofía Lean, Observable Workflow, MCP |
| **Ha** (Romper) | Context Engineering, niveles de Kata | Detalles de MELT, ADRs históricos |
| **Ri** (Trascender) | Ontología completa, creación de Katas | Nada — acceso total |

---

## 4. Decisiones de Research

### Decision 1: Modelo de Disclosure por Etapas

**Decision**: Adoptar 4 etapas de learning path alineadas con competencias del Orquestador + fase de awareness inicial.

**Rationale**: Los 3 niveles de competencia existentes (L1/L2/L3) más una "Etapa 0" de primer contacto dan cobertura completa.

**Alternativas consideradas**:
- 3 etapas (ShuHaRi puro) — Rechazado: no hay etapa de "primer contacto"
- 5 etapas — Rechazado: excede simplicidad necesaria

### Decision 2: Concepto Semilla como Puerta de Entrada

**Decision**: Definir 5-7 "conceptos semilla" que un Orquestador novato necesita para ser productivo.

**Rationale**: Ley de Miller (7±2) como límite cognitivo. Los 7 conceptos propuestos permiten:
- Entender el rol (Orquestador)
- Escribir especificaciones (Spec)
- Saber cuándo pasar a siguiente fase (Validation Gate)
- Conocer restricciones (Guardrail)
- Tener referencia de proceso (Kata)
- Saber que hay principios inmutables (Constitution)
- Tener mecanismo de corrección (Jidoka simplificado)

**Alternativas consideradas**:
- 3 conceptos (Orquestador, Spec, Validation Gate) — Rechazado: insuficiente para productividad
- 10 conceptos — Rechazado: excede carga cognitiva

### Decision 3: Patrón ADR-009 como Template

**Decision**: Aplicar el patrón de ADR-009 (interfaz simple + filosofía interna) a otros conceptos complejos.

**Rationale**: Ya probado y aceptado. Evita inventar nuevo patrón.

**Aplicación propuesta**:
| Concepto Complejo | Interfaz Simple | Filosofía Interna |
|-------------------|-----------------|-------------------|
| Jidoka | "Parar si falla" | 4 pasos: Detectar→Parar→Corregir→Prevenir |
| Context Engineering | "Dar contexto al agente" | Arquitectura MCP + Golden Data |
| Observable Workflow | "El sistema registra todo" | Framework MELT |
| Niveles de Kata | "Guías de proceso" | Principios/Flujo/Patrón/Técnica |

---

## 5. Artefactos de Referencia Consultados

| Documento | Relevancia | Hallazgo Clave |
|-----------|------------|----------------|
| `00-constitution-v2.md` | Alta | 8 principios, §5 Heutagogía es core |
| `20-glossary-v2.1.md` | Alta | ~35 términos, ya tiene anti-términos |
| `21-methodology-v2.md` | Alta | 8 fases, 8 Validation Gates |
| `05-learning-philosophy-v2.md` | Alta | 4 pilares, 3 niveles de Orquestador |
| `25-ontology-bundle-v2_1.md` | Alta | Simplificación existente (~45KB) |
| `adr-009-shuhari-hybrid.md` | Alta | Patrón de disclosure progresivo |
| `kata-shuhari-schema-v2.1.md` | Media | ShuHaRi como lente, no clasificación |
| ADRs (11 documentos) | Media | Decisiones arquitectónicas históricas |

---

## 6. Próximos Pasos

Este research informa la generación de:
1. **data-model.md**: Modelo de entidades (Concepto, Barrera, Etapa, Mejora)
2. **quickstart.md**: Guía de ejecución del análisis
3. **audit-report.md**: Inventario detallado con clasificaciones
4. **learning-path.md**: Camino de 4 etapas
5. **improvement-proposals.md**: Mejoras priorizadas

---

*Research completado. Proceder a Phase 1 (data-model.md, quickstart.md).*
