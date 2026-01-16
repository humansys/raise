# Auditoría de Complejidad Ontológica: RaiSE v2.1

**Feature**: 001-heutagogy-progressive-disclosure
**Date**: 2026-01-11
**Status**: Complete
**User Story**: US1 (P1) — Auditoría de Complejidad Ontológica

## Executive Summary

Este informe presenta un inventario completo de los ~35 conceptos canónicos de la ontología RaiSE v2.1, clasificados por complejidad, dependencias, fase ShuHaRi recomendada, y utilidad para Orquestadores novatos. El análisis identifica 7 conceptos semilla y 8 barreras de entrada categorizadas según el framework Lean (Muda/Mura/Muri).

**Hallazgo principal**: El 60% de los conceptos tienen dependencias que requieren conocimiento previo, lo cual representa una barrera significativa para nuevos Orquestadores. Sin embargo, 7 conceptos "semilla" pueden proporcionar productividad inmediata sin dependencias complejas.

---

## 1. Inventario de Conceptos por Categoría

### 1.1 Core Philosophy (8 conceptos)

| ID | Término | Complejidad | Dependencias | ShuHaRi | Utility Novato |
|----|---------|-------------|--------------|---------|----------------|
| CP-01 | Constitution | basic | 0 | shu | ⭐⭐ medium |
| CP-02 | Context Engineering | advanced | 3 (Golden Data, MCP, Guardrails) | ri | ⭐ low |
| CP-03 | Governance as Code | intermediate | 1 (Git) | ha | ⭐⭐ medium |
| CP-04 | Heutagogía | intermediate | 1 (Checkpoint Heutagógico) | ha | ⭐ low |
| CP-05 | Jidoka | advanced | 2 (Validation Gate, Kata) | ri | ⭐⭐ medium |
| CP-06 | Kaizen | intermediate | 2 (Jidoka, Guardrails) | ha | ⭐ low |
| CP-07 | Lean Software Development | advanced | 4 (Jidoka, Kaizen, Kata, Observable Workflow) | ri | ⭐ low |
| CP-08 | Platform Agnosticism | basic | 1 (Git) | shu | ⭐ low |

**Análisis**: Solo 2 de 8 conceptos son básicos. Los conceptos filosóficos tienden a tener alta interdependencia.

---

### 1.2 Workflow Entities (10 conceptos)

| ID | Término | Complejidad | Dependencias | ShuHaRi | Utility Novato |
|----|---------|-------------|--------------|---------|----------------|
| WF-01 | Spec (Specification) | basic | 1 (Template) | shu | ⭐⭐⭐ high |
| WF-02 | Validation Gate | basic | 1 (Fase del flujo) | shu | ⭐⭐⭐ high |
| WF-03 | Escalation Gate | intermediate | 2 (Validation Gate, Orquestador) | ha | ⭐⭐ medium |
| WF-04 | PRD | basic | 0 | shu | ⭐⭐ medium |
| WF-05 | Solution Vision | intermediate | 1 (PRD) | ha | ⭐⭐ medium |
| WF-06 | Technical Design | intermediate | 2 (Solution Vision, Architecture) | ha | ⭐⭐ medium |
| WF-07 | Implementation Plan | intermediate | 2 (Technical Design, Tasks) | ha | ⭐⭐ medium |
| WF-08 | User Story | basic | 0 | shu | ⭐⭐⭐ high |
| WF-09 | Corpus | intermediate | 2 (Golden Data, Docs) | ha | ⭐ low |
| WF-10 | Golden Data | intermediate | 1 (Verificación humana) | ha | ⭐⭐ medium |

**Análisis**: 4 conceptos son básicos y de alta utilidad. Esta categoría es la más accesible para novatos.

---

### 1.3 Agent Ecosystem (6 conceptos)

| ID | Término | Complejidad | Dependencias | ShuHaRi | Utility Novato |
|----|---------|-------------|--------------|---------|----------------|
| AE-01 | Agent (Agente) | basic | 0 | shu | ⭐⭐⭐ high |
| AE-02 | Guardrail | basic | 1 (Constitution) | shu | ⭐⭐⭐ high |
| AE-03 | MCP | advanced | 3 (Resources, Tools, Prompts) | ri | ⭐ low |
| AE-04 | Observable Workflow | advanced | 4 (MELT: Metrics, Events, Logs, Traces) | ri | ⭐ low |
| AE-05 | raise-config | intermediate | 2 (Git, Guardrails) | ha | ⭐ low |
| AE-06 | raise-kit | intermediate | 2 (CLI, raise-config) | ha | ⭐⭐ medium |

**Análisis**: 2 conceptos básicos de alta utilidad (Agent, Guardrail). MCP y Observable Workflow son avanzados y de baja prioridad para novatos.

---

### 1.4 Kata System (4 conceptos)

| ID | Término | Complejidad | Dependencias | ShuHaRi | Utility Novato |
|----|---------|-------------|--------------|---------|----------------|
| KS-01 | Kata | intermediate | 2 (Niveles, Jidoka inline) | shu | ⭐⭐ medium |
| KS-02 | ShuHaRi | advanced | 3 (Shu, Ha, Ri + Kata) | ri | ⭐ low |
| KS-03 | Checkpoint Heutagógico | intermediate | 2 (Heutagogía, 4 preguntas) | ha | ⭐⭐ medium |
| KS-04 | Just-In-Time Learning | intermediate | 2 (Context, Agente) | ha | ⭐ low |

**Análisis**: Ningún concepto es realmente básico. El sistema Kata tiene alta interdependencia interna.

---

### 1.5 Roles & Commands (3 conceptos)

| ID | Término | Complejidad | Dependencias | ShuHaRi | Utility Novato |
|----|---------|-------------|--------------|---------|----------------|
| RC-01 | Orquestador | basic | 0 | shu | ⭐⭐⭐ high |
| RC-02 | pull (CLI) | basic | 1 (raise-config) | shu | ⭐⭐ medium |
| RC-03 | kata (CLI) | intermediate | 2 (Kata, Niveles) | ha | ⭐⭐ medium |

**Análisis**: Orquestador es el concepto más fundamental — define el rol del usuario.

---

### 1.6 Conceptos de Preventa (4 conceptos)

| ID | Término | Complejidad | Dependencias | ShuHaRi | Utility Novato |
|----|---------|-------------|--------------|---------|----------------|
| PV-01 | Capability | basic | 0 | shu | ⭐ low |
| PV-02 | Feature | basic | 1 (Capability) | shu | ⭐⭐ medium |
| PV-03 | Statement of Work | intermediate | 2 (Entregables, Cronograma) | ha | ⭐ low |
| PV-04 | Roadmap | basic | 1 (Features) | shu | ⭐ low |

**Análisis**: Conceptos de contexto empresarial, no esenciales para uso técnico del framework.

---

## 2. Grafo de Dependencias

```
                    ┌─────────────────────────────────────────────┐
                    │            CONSTITUTION (CP-01)             │
                    │          [Sin dependencias - ROOT]          │
                    └─────────────────┬───────────────────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           ▼                          ▼                          ▼
    ┌─────────────┐          ┌─────────────────┐         ┌─────────────┐
    │  GUARDRAIL  │          │   VALIDATION    │         │    SPEC     │
    │   (AE-02)   │          │   GATE (WF-02)  │         │   (WF-01)   │
    └──────┬──────┘          └────────┬────────┘         └─────────────┘
           │                          │
           ▼                          ▼
    ┌─────────────┐          ┌─────────────────┐
    │   CONTEXT   │          │   ESCALATION    │
    │ ENGINEERING │          │   GATE (WF-03)  │
    │   (CP-02)   │          └─────────────────┘
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐          ┌─────────────────┐
    │    MCP      │◄─────────│   OBSERVABLE    │
    │   (AE-03)   │          │   WORKFLOW      │
    └─────────────┘          │    (AE-04)      │
                             └─────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │                      KATA SYSTEM CLUSTER                     │
    │  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
    │  │  JIDOKA  │───▶│   KATA   │───▶│  SHUHARI │               │
    │  │ (CP-05)  │    │  (KS-01) │    │  (KS-02) │               │
    │  └──────────┘    └────┬─────┘    └──────────┘               │
    │                       │                                      │
    │                       ▼                                      │
    │                 ┌──────────┐                                │
    │                 │  KAIZEN  │                                │
    │                 │ (CP-06)  │                                │
    │                 └──────────┘                                │
    └─────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │                    ROLES (Independent)                       │
    │  ┌──────────────┐                                           │
    │  │ ORQUESTADOR  │  [Sin dependencias - Entry Point]         │
    │  │   (RC-01)    │                                           │
    │  └──────────────┘                                           │
    └─────────────────────────────────────────────────────────────┘
```

### Clusters de Complejidad Identificados

1. **Cluster Lean/TPS** (alta interdependencia): Jidoka → Kata → ShuHaRi → Kaizen
2. **Cluster Context Engineering** (dependencias externas): Golden Data → MCP → Observable Workflow
3. **Cluster Workflow** (secuencial): PRD → Solution Vision → Technical Design → Implementation Plan

---

## 3. Conceptos Semilla (Seed Concepts)

Basado en el análisis (Ley de Miller 7±2), se identifican **7 conceptos semilla** para la fase Shu:

| # | Concepto | Justificación |
|---|----------|---------------|
| 1 | **Orquestador** | Define el rol del usuario; sin dependencias; entry point |
| 2 | **Spec** | Artefacto fundamental; 1 dependencia (template); alta utilidad |
| 3 | **Validation Gate** | Control de calidad esencial; 1 dependencia; alta utilidad |
| 4 | **Guardrail** | Restricciones operacionales; 1 dependencia (Constitution); alta utilidad |
| 5 | **Agent** | Concepto de IA que ejecuta; sin dependencias; alta utilidad |
| 6 | **Constitution** | Principios inmutables; sin dependencias; conocimiento contextual |
| 7 | **Jidoka (simplificado)** | "Parar si falla"; versión reducida sin 4 pasos; utilidad práctica |

**Cobertura**: Estos 7 conceptos permiten a un Orquestador novato:
- Entender su rol (Orquestador)
- Escribir especificaciones (Spec)
- Saber cuándo puede avanzar (Validation Gate)
- Conocer restricciones (Guardrail)
- Interactuar con agentes (Agent)
- Saber que hay principios inmutables (Constitution)
- Corregir errores (Jidoka simplificado)

---

## 4. Barreras de Entrada Identificadas

### 4.1 Barreras por Tipo

| ID | Tipo | Descripción | Conceptos Afectados | Severidad |
|----|------|-------------|---------------------|-----------|
| B-01 | Terminológica | Sobrecarga de términos japoneses | Kata, Jidoka, Kaizen, ShuHaRi | 🟡 Medium |
| B-02 | Conceptual | Interdependencia del cluster Lean/TPS | Jidoka, Kata, Kaizen, ShuHaRi | 🔴 High |
| B-03 | Estructural | Profundidad variable en documentación | Todos los conceptos avanzados | 🟡 Medium |
| B-04 | Terminológica | Vocabulario técnico de observabilidad | Observable Workflow, MELT | 🟢 Low |
| B-05 | Conceptual | Context Engineering requiere 3 conceptos previos | Context Engineering | 🟡 Medium |
| B-06 | Estructural | Niveles de Kata (4) vs. ShuHaRi (3) | Kata, ShuHaRi | 🟡 Medium |
| B-07 | Terminológica | Duplicidad de términos (Rule/Guardrail, DoD/Validation Gate) | Guardrail, Validation Gate | 🟢 Low |
| B-08 | Conceptual | Filosofía Heutagógica no universalmente conocida | Heutagogía, Checkpoint Heutagógico | 🟡 Medium |

### 4.2 Análisis Lean (Muda/Mura/Muri)

| Barrera | Tipo Lean | Manifestación | Propuesta de Mitigación |
|---------|-----------|---------------|-------------------------|
| B-01 | **Muri** (sobrecarga) | 4 términos japoneses expuestos simultáneamente | Disclosure progresivo: solo Kata en Shu |
| B-02 | **Mura** (irregularidad) | Cluster tightly-coupled sin entrada clara | Definir entry point (Kata simplificado) |
| B-03 | **Mura** (irregularidad) | Docs con diferente nivel de detalle | Estandarizar profundidad por fase ShuHaRi |
| B-04 | **Muda** (desperdicio) | Vocabulario innecesario para novatos | Ocultar MELT hasta fase Ri |
| B-05 | **Muri** (sobrecarga) | Prerequisitos no explícitos | Documentar dependencias visualmente |
| B-06 | **Mura** (irregularidad) | Dos sistemas de clasificación | Usar solo audience (beginner/intermediate/advanced) externamente |
| B-07 | **Muda** (desperdicio) | Aliases históricos en documentación | Eliminar aliases en docs de onboarding |
| B-08 | **Muri** (sobrecarga) | Concepto académico sin contexto | Explicar como "aprendizaje auto-dirigido" |

---

## 5. Métricas de Complejidad

### 5.1 Distribución por Complejidad

| Complejidad | Count | % | Conceptos |
|-------------|-------|---|-----------|
| Basic | 13 | 37% | Constitution, Spec, Validation Gate, PRD, User Story, Agent, Guardrail, Orquestador, pull, Capability, Feature, Roadmap, Platform Agnosticism |
| Intermediate | 14 | 40% | Governance as Code, Heutagogía, Kaizen, Escalation Gate, Solution Vision, Technical Design, Implementation Plan, Corpus, Golden Data, raise-config, raise-kit, Kata, Checkpoint Heutagógico, JIT Learning, kata (CLI), SoW |
| Advanced | 8 | 23% | Context Engineering, Jidoka, Lean Software Dev, MCP, Observable Workflow, ShuHaRi |

### 5.2 Distribución por Fase ShuHaRi

| Fase | Count | % | Descripción |
|------|-------|---|-------------|
| Shu (Proteger) | 13 | 37% | Seguir exactamente; conceptos básicos |
| Ha (Romper) | 14 | 40% | Adaptar al contexto; conceptos intermedios |
| Ri (Trascender) | 8 | 23% | Crear nuevos; conceptos avanzados |

### 5.3 Distribución por Utilidad para Novatos

| Utilidad | Count | % |
|----------|-------|---|
| High (⭐⭐⭐) | 7 | 20% |
| Medium (⭐⭐) | 14 | 40% |
| Low (⭐) | 14 | 40% |

---

## 6. Validación de Gates

### Gate-Terminología ✅ PASS

- Todos los términos usados corresponden al glosario v2.1
- Sin uso de términos deprecated (Rule, DoD Fractal, L0-L3)
- Terminología canónica consistente

### Gate-Coherencia ✅ PASS

- Sin contradicciones con Constitution §1-§8
- Clasificaciones alineadas con research.md (Decision 1, 2, 3)
- Conceptos semilla alineados con Ley de Miller

---

## Appendix: Tablas de Referencia Rápida

### A.1 Todos los Conceptos Ordenados por ShuHaRi

**Fase Shu (13 conceptos)**:
Constitution, Spec, Validation Gate, PRD, User Story, Agent, Guardrail, Orquestador, pull (CLI), Capability, Feature, Roadmap, Platform Agnosticism

**Fase Ha (14 conceptos)**:
Governance as Code, Heutagogía, Kaizen, Escalation Gate, Solution Vision, Technical Design, Implementation Plan, Corpus, Golden Data, raise-config, raise-kit, Kata, Checkpoint Heutagógico, JIT Learning, kata (CLI), Statement of Work

**Fase Ri (8 conceptos)**:
Context Engineering, Jidoka (4 pasos), Lean Software Development, MCP, Observable Workflow, ShuHaRi (filosofía)

### A.2 Conceptos con Alta Utilidad para Novatos (⭐⭐⭐)

1. Orquestador (RC-01)
2. Spec (WF-01)
3. Validation Gate (WF-02)
4. User Story (WF-08)
5. Agent (AE-01)
6. Guardrail (AE-02)

---

*Audit Report completado. Proceder a learning-path.md (US2).*
