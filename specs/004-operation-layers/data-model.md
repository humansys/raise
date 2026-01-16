# Data Model: Work Cycle

**Feature**: 004-operation-layers
**Date**: 2026-01-11
**Purpose**: Schema de entidades para el documento de Ciclos de Trabajo

---

## Entidad Principal: Work Cycle

Un **Work Cycle** (Ciclo de Trabajo) es un contexto operacional del Orquestador con recursos y herramientas específicas.

### Atributos

| Atributo | Tipo | Requerido | Descripción |
|----------|------|-----------|-------------|
| `id` | string | ✅ | Identificador único (onboarding, proyecto, feature, mejora) |
| `name` | string | ✅ | Nombre canónico en español |
| `name_en` | string | ✅ | Nombre canónico en inglés |
| `trigger` | string | ✅ | Qué evento inicia este ciclo |
| `work_unit` | string | ✅ | Unidad de trabajo principal |
| `raise_phases` | array[string] | ✅ | Fases de la metodología que cubre |
| `katas` | array[string] | ❌ | Referencias a katas que implementan el ciclo |
| `speckit_coverage` | enum | ✅ | none, partial, full |
| `speckit_commands` | array[string] | ❌ | Comandos de spec-kit que aplican |
| `description` | string | ✅ | Descripción breve del propósito |

### Enum: speckit_coverage

| Valor | Significado |
|-------|-------------|
| `none` | spec-kit no cubre este ciclo |
| `partial` | spec-kit cubre parcialmente |
| `full` | spec-kit cubre completamente |

---

## Instancias Definidas

### Ciclo de Onboarding

```yaml
id: onboarding
name: Ciclo de Onboarding
name_en: Onboarding Cycle
trigger: Nuevo repositorio o proyecto brownfield
work_unit: Repositorio
raise_phases: ["Fase 0 (parcial)"]
katas:
  - L0-01-gestion-integral-reglas-cursor
  - L2-01-analisis-exploratorio-repositorio
  - L2-02-inicializacion-gobernanza-reglas
  - L2-04-establecimiento-reglas-estandares-generales
  - L2-05-establecimiento-reglas-metodologia-raise
  - L2-06-establecimiento-meta-reglas-fundamentales
speckit_coverage: none
speckit_commands: []
description: >
  Preparación inicial de un repositorio para trabajar con RaiSE.
  Incluye análisis de arquitectura existente (software architecture reconstruction),
  establecimiento de gobernanza y reglas fundacionales.
```

### Ciclo de Proyecto

```yaml
id: proyecto
name: Ciclo de Proyecto
name_en: Project Cycle
trigger: Nueva épica o iniciativa multi-feature
work_unit: Épica / Iniciativa
raise_phases: ["Fase 1: Discovery", "Fase 2: Vision", "Fase 3: Design"]
katas: []  # No hay katas formales aún
speckit_coverage: none
speckit_commands: []
description: >
  Trabajo a nivel de épica o iniciativa que agrupa múltiples features.
  Incluye PRD, Solution Vision, y Technical Design de alto nivel.
```

### Ciclo de Feature

```yaml
id: feature
name: Ciclo de Feature
name_en: Feature Cycle
trigger: Feature priorizado del backlog
work_unit: Feature / User Story
raise_phases: ["Fase 4: Backlog", "Fase 5: Plan", "Fase 6: Development"]
katas:
  - flujo/04-generacion-plan
speckit_coverage: full
speckit_commands:
  - /speckit.specify
  - /speckit.clarify
  - /speckit.plan
  - /speckit.tasks
  - /speckit.implement
description: >
  Desarrollo de un feature individual desde especificación hasta código.
  Este es el ciclo donde spec-kit opera completamente.
```

### Ciclo de Mejora

```yaml
id: mejora
name: Ciclo de Mejora
name_en: Improvement Cycle
trigger: Post-feature, post-sprint, o periódico
work_unit: Aprendizaje / Refinamiento
raise_phases: ["Fase 7: UAT & Deploy", "Retrospectiva", "Kaizen"]
katas:
  - L0-01 Fase 7 (mantenimiento)
speckit_coverage: partial
speckit_commands:
  - /speckit.analyze
  - /speckit.constitution
description: >
  Reflexión y mejora continua después de completar trabajo.
  Incluye retrospectivas, actualización de guardrails/katas, y checkpoint heutagógico.
```

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
- Proyectos pequeños pueden saltar de Onboarding directo a Feature
- El Ciclo de Mejora retroalimenta todos los demás ciclos

---

## Entrada de Glosario Propuesta

### Work Cycle (Ciclo de Trabajo)

**[NUEVO v2.1]** Contexto operacional del Orquestador que agrupa fases de la metodología, katas aplicables, y herramientas disponibles. Los ciclos son ortogonales—el Orquestador transita entre ellos según la naturaleza del trabajo.

**Ciclos definidos:**

| Ciclo | Trigger | spec-kit |
|-------|---------|----------|
| **Onboarding** | Nuevo repo | ❌ |
| **Proyecto** | Nueva épica | ❌ |
| **Feature** | Feature priorizado | ✅ |
| **Mejora** | Post-trabajo | ⚠️ Parcial |

> **Relación con Fases**: Los ciclos agrupan fases (0-7) por contexto operacional, no por secuencia temporal.
