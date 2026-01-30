# RaiSE Work Cycles

## Ciclos de Trabajo del Orquestador

**Versión:** 2.1.0
**Fecha:** 11 de Enero, 2026
**Propósito:** Definir los contextos operacionales (ciclos) en los que trabaja el Orquestador, clarificando qué herramientas y katas aplican en cada uno.

> **Nota de versión 2.1:** Formalización de los ciclos de trabajo implícitos en las katas existentes. Clarifica dónde opera spec-kit y qué requiere desarrollo futuro (raise-kit).

---

## Definición de Work Cycle

Un **Work Cycle** (Ciclo de Trabajo) es un contexto operacional del Orquestador que agrupa:

- **Trigger**: Qué evento inicia el ciclo
- **Unidad de trabajo**: Qué artefacto principal se produce
- **Fases RaiSE**: Qué fases de la metodología cubre
- **Katas**: Qué katas aplican
- **Herramientas**: Qué comandos de spec-kit/raise-kit están disponibles

Los ciclos son **ortogonales**—el Orquestador transita entre ellos según la naturaleza del trabajo, no en secuencia fija.

---

## Los Cuatro Ciclos

### Ciclo de Onboarding

**Preparación inicial de un repositorio para trabajar con RaiSE.**

| Atributo | Valor |
|----------|-------|
| **Trigger** | Nuevo repositorio o proyecto brownfield |
| **Unidad de trabajo** | Repositorio configurado |
| **Fases RaiSE** | Fase 0 (parcial) |
| **spec-kit** | ❌ No cubre |

**Actividades:**
- Análisis exploratorio del repositorio (software architecture reconstruction)
- Identificación de tecnologías, patrones, estructura
- Establecimiento de gobernanza (constitution, guardrails)
- Creación de reglas fundacionales y meta-reglas

**Katas aplicables:**

| Kata | Propósito |
|------|-----------|
| `L0-01-gestion-integral-reglas-cursor` | Orquestación completa del onboarding |
| `L2-01-analisis-exploratorio-repositorio` | Análisis de tecnologías y patrones |
| `L2-02-inicializacion-gobernanza-reglas` | Crear estructura de gobernanza |
| `L2-04-establecimiento-reglas-estandares-generales` | Estándares de codificación |
| `L2-05-establecimiento-reglas-metodologia-raise` | Reglas de metodología |
| `L2-06-establecimiento-meta-reglas-fundamentales` | Meta-reglas de gestión |

> **Ubicación:** `src/katas/cursor_rules/`

---

### Ciclo de Proyecto

**Trabajo a nivel de épica o iniciativa que agrupa múltiples features.**

| Atributo | Valor |
|----------|-------|
| **Trigger** | Nueva épica o iniciativa multi-feature |
| **Unidad de trabajo** | Épica / Iniciativa |
| **Fases RaiSE** | Fase 1 (Discovery), Fase 2 (Vision), Fase 3 (Design) |
| **spec-kit** | ❌ No cubre |

**Actividades:**
- PRD (Product Requirements Document)
- Solution Vision
- Technical Design de alto nivel
- Desglose en features

**Katas aplicables:**
- *(No hay katas formales aún—uso ad-hoc de plantillas)*

> **Gap identificado:** Este ciclo no tiene katas formales ni herramientas. Candidato para raise-kit futuro.

---

### Ciclo de Feature

**Desarrollo de un feature individual desde especificación hasta código.**

| Atributo | Valor |
|----------|-------|
| **Trigger** | Feature priorizado del backlog |
| **Unidad de trabajo** | Feature / User Story |
| **Fases RaiSE** | Fase 4 (Backlog), Fase 5 (Plan), Fase 6 (Development) |
| **spec-kit** | ✅ Cubre completamente |

**Actividades:**
- Especificación de feature
- Plan de implementación
- Generación de tareas
- Implementación con Jidoka

**Comandos spec-kit disponibles:**

| Comando | Propósito |
|---------|-----------|
| `/speckit.specify` | Crear especificación de feature |
| `/speckit.clarify` | Clarificar requisitos ambiguos |
| `/speckit.plan` | Generar plan de implementación |
| `/speckit.tasks` | Generar lista de tareas |
| `/speckit.implement` | Ejecutar implementación |

**Katas aplicables:**

| Kata | Propósito |
|------|-----------|
| `flujo/04-generacion-plan` | Generación de plan de implementación |

---

### Ciclo de Mejora

**Reflexión y mejora continua después de completar trabajo.**

| Atributo | Valor |
|----------|-------|
| **Trigger** | Post-feature, post-sprint, o periódico |
| **Unidad de trabajo** | Aprendizaje / Refinamiento |
| **Fases RaiSE** | Fase 7 (UAT & Deploy), Retrospectiva, Kaizen |
| **spec-kit** | ⚠️ Parcial |

**Actividades:**
- Checkpoint Heutagógico
- Retrospectivas
- Actualización de guardrails/katas
- Análisis de coherencia ontológica

**Comandos spec-kit disponibles:**

| Comando | Propósito |
|---------|-----------|
| `/speckit.analyze` | Validar coherencia entre artefactos |
| `/speckit.constitution` | Actualizar constitution |

**Katas aplicables:**

| Kata | Propósito |
|------|-----------|
| `L0-01` Fase 7 | Mantenimiento y evolución |

> **Gap identificado:** No hay comandos para retrospectivas estructuradas ni checkpoint heutagógico formal.

---

## Tabla Resumen de Ciclos

| Ciclo | Trigger | Unidad | Fases RaiSE | Katas | spec-kit |
|-------|---------|--------|-------------|-------|----------|
| **Onboarding** | Nuevo repo | Repositorio | Fase 0 (parcial) | L0-01, L2-01 a L2-06 | ❌ |
| **Proyecto** | Nueva épica | Épica | Fases 1-3 | *(ninguna formal)* | ❌ |
| **Feature** | Feature priorizado | Feature | Fases 4-6 | flujo/04 | ✅ |
| **Mejora** | Post-trabajo | Aprendizaje | Fase 7+ | L0-01 Fase 7 | ⚠️ Parcial |

---

## Relaciones entre Ciclos

```
┌──────────────┐
│  Onboarding  │ ─────────────────────────────────────┐
└──────┬───────┘                                      │
       │ (habilita)                                   │
       ▼                                              │
┌──────────────┐                                      │
│   Proyecto   │                                      │
└──────┬───────┘                                      │
       │ (genera features)                            │
       ▼                                              │
┌──────────────┐                                      │
│   Feature    │ ◄─── spec-kit opera aquí            │
└──────┬───────┘                                      │
       │ (alimenta)                                   │
       ▼                                              │
┌──────────────┐                                      │
│    Mejora    │ ─────── (refina) ────────────────────┘
└──────────────┘
```

**Notas:**
- Los ciclos son ortogonales: un Orquestador puede estar en cualquiera según el momento
- El Ciclo de Mejora retroalimenta todos los demás ciclos
- Proyectos pequeños pueden saltar de Onboarding directo a Feature

---

## Adaptación por Contexto

### Proyectos Pequeños

Pueden omitir el Ciclo de Proyecto y transitar directamente:

```
Onboarding → Feature → Mejora
```

Se pierde la documentación de alto nivel (PRD, Vision), pero es válido para cambios menores.

### Repos sin Onboarding Previo

Si se usa spec-kit directamente sin haber completado el Ciclo de Onboarding:

- ⚠️ No hay constitution específica del proyecto
- ⚠️ No hay guardrails de arquitectura
- ⚠️ El agente opera sin contexto del repositorio

**Recomendación:** Ejecutar al menos `L2-01` (análisis exploratorio) antes de usar spec-kit.

---

## Implicaciones para raise-kit (Futuro)

Este documento establece el blueprint para raise-kit como fork de spec-kit:

| Ciclo | Comandos spec-kit | Comandos raise-kit (propuestos) |
|-------|-------------------|--------------------------------|
| **Onboarding** | *(ninguno)* | `/raise.init`, `/raise.discover`, `/raise.bootstrap` |
| **Proyecto** | *(ninguno)* | `/raise.epic`, `/raise.vision`, `/raise.design` |
| **Feature** | specify, plan, tasks, implement | *(heredados de spec-kit)* |
| **Mejora** | analyze, constitution | `/raise.retrospect`, `/raise.checkpoint` |

> **YAGNI:** Esta tabla es descriptiva, no prescriptiva. Los comandos se diseñarán cuando se implemente raise-kit.

---

## Referencias

- [20-glossary-v2.1.md](./20-glossary-v2.1.md) — Entrada "Work Cycle"
- [21-methodology-v2.md](./21-methodology-v2.md) — Fases 0-7 del flujo de valor
- `src/katas/cursor_rules/` — Katas del Ciclo de Onboarding

---

## Changelog

### v2.1.0 (2026-01-11)

- **NUEVO**: Documento inicial formalizando los 4 ciclos de trabajo
- **NUEVO**: Tabla resumen de ciclos con cobertura spec-kit
- **NUEVO**: Sección de implicaciones para raise-kit
- **NUEVO**: Diagrama de relaciones entre ciclos
