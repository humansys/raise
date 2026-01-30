---
id: "ADR-010"
title: "Jerarquía de Artefactos de Tres Niveles: Solution → Project → Codebase"
date: "2026-01-30"
status: "Proposed"
related_to: ["ADR-009", "ADR-008", "glossary-v2.3"]
supersedes: []
---

# ADR-010: Jerarquía de Artefactos de Tres Niveles

## Contexto

### Problema Identificado

RaiSE v2.1 definía artefactos a nivel de **proyecto** (PRD → Solution Vision → Tech Design), pero carecía de artefactos a nivel de **solución/sistema**. Esto creaba varios problemas:

1. **Gap en Governance**: ADR-009 define Governance como "producto-wide", pero ¿qué alimenta la Governance? No había artefacto que definiera el sistema/solución.

2. **Confusión Brownfield**: En escenarios brownfield, los equipos trabajan con **sistemas** existentes, no "productos". La terminología "producto" no resonaba.

3. **Cadena Incompleta**:
   ```
   PROJECT LEVEL:
     PRD → Solution Vision → Tech Design → Backlog

   Pero... ¿qué define el SISTEMA antes de los proyectos?
   ¿De dónde viene la Governance?
   ```

4. **Naming Conflict**: Si introducíamos "Solution Vision" a nivel de sistema, ¿cómo llamar al artefacto de proyecto que actualmente se llama "Solution Vision"?

### Análisis

Siguiendo el patrón identificado en cada nivel:

| Nivel | Definición del Problema | Definición de la Solución | Constraints |
|-------|------------------------|---------------------------|-------------|
| **Sistema** | ??? | ??? | Governance |
| **Proyecto** | PRD | Solution Vision (actual) | Tech Design |

La cadena lógica debería ser:

```
NIVEL SOLUCIÓN (Sistema):
  "¿Por qué este sistema?"  →  "¿Qué ES este sistema?"  →  "¿Qué estándares?"

NIVEL PROYECTO (Iniciativa):
  "¿Qué construir?"  →  "¿Cómo abordarlo?"  →  "¿Cómo implementarlo?"
```

### Investigación de Industria

| Término Industria | Nivel | Propósito |
|-------------------|-------|-----------|
| **Business Case** | Sistema | Justificar inversión, definir oportunidad |
| **Solution Architecture** | Sistema | Definir el sistema/solución |
| **Project Charter** | Proyecto | Definir alcance de iniciativa |
| **Technical Design** | Proyecto | Definir implementación |

El término **"Solution"** se alinea mejor con escenarios brownfield/enterprise, donde se trabaja con **sistemas** más que con "productos".

## Decisión

### Adoptar Jerarquía de Tres Niveles

```
┌─────────────────────────────────────────────────────────────────────────┐
│  NIVEL SOLUCIÓN (Sistema - Perdura)                                      │
│  ═══════════════════════════════════                                    │
│                                                                          │
│  Business Case          Solution Vision           Governance             │
│  "¿Por qué?"            "¿Qué sistema?"           "¿Qué estándares?"    │
│       │                       │                         │                │
│       │                       │                         │                │
│       ▼                       ▼                         ▼                │
│  ┌──────────┐           ┌──────────┐             ┌──────────┐           │
│  │ Necesidad │           │ Identidad │             │ Guardrails│           │
│  │ de negocio│           │ del       │             │ del       │           │
│  │ Stakehldrs│           │ sistema   │             │ sistema   │           │
│  │ Métricas  │           │ Alcance   │             │           │           │
│  └──────────┘           │ Dirección │             └──────────┘           │
│                          │ técnica   │                   │                │
│                          └──────────┘                   │                │
│                                │                         │                │
│                                │ informa                 │ constrains     │
│                                ▼                         ▼                │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  NIVEL PROYECTO (Iniciativa - Tiempo-bound)                              │
│  ══════════════════════════════════════════                             │
│                                                                          │
│  PRD                    Project Vision          Tech Design              │
│  "¿Qué construir?"      "¿Cómo abordarlo?"      "¿Cómo implementar?"    │
│       │                       │                         │                │
│       ▼                       ▼                         ▼                │
│  ┌──────────┐           ┌──────────┐             ┌──────────┐           │
│  │ Requisitos│           │ Approach  │             │ Diseño    │           │
│  │ del       │           │ arquitect.│             │ detallado │           │
│  │ proyecto  │           │ Decisiones│             │ Componente│           │
│  │ Alcance   │           │ Tradeoffs │             │ Interfaces│           │
│  └──────────┘           └──────────┘             └──────────┘           │
│                                                         │                │
│                                                         │ implementa     │
│                                                         ▼                │
└─────────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  NIVEL CODEBASE (Repositorio)                                            │
│  ════════════════════════════                                           │
│                                                                          │
│  Governance (heredada)        Rules (específicas)       Código           │
│  .raise/governance/           .cursor/rules/            src/             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Renombrar Artefactos

| Nivel | Antes (v2.1) | Después (v2.4) | Propósito |
|-------|--------------|----------------|-----------|
| Solución | *(no existía)* | **Business Case** | Definir necesidad de negocio |
| Solución | *(no existía)* | **Solution Vision** | Definir el sistema/solución |
| Solución | Governance | **Governance** (sin cambio) | Estándares del sistema |
| Proyecto | PRD | **PRD** (sin cambio) | Requisitos del proyecto |
| Proyecto | Solution Vision | **Project Vision** | Approach del proyecto |
| Proyecto | Tech Design | **Tech Design** (sin cambio) | Diseño de implementación |

**Cambio clave**: "Solution Vision" sube a nivel de sistema; el artefacto de proyecto se renombra a "Project Vision".

### Estructura de Katas

```
.raise/katas/
├── solution/                    # NUEVO - Nivel Sistema
│   ├── discovery.md             # → Business Case
│   └── vision.md                # → Solution Vision
│
├── setup/                       # Configuración
│   ├── governance.md            # Deriva de Solution Vision
│   ├── rules.md                 # Patrones de codebase
│   └── ecosystem.md             # Mapa de integraciones
│
├── project/                     # Nivel Proyecto (renombrado interno)
│   ├── discovery.md             # → PRD
│   ├── vision.md                # → Project Vision (antes Solution Vision)
│   ├── design.md                # → Tech Design
│   └── backlog.md               # → Project Backlog
│
├── feature/                     # Nivel Feature
│   ├── plan.md
│   ├── implement.md
│   └── review.md
│
└── improve/                     # Mejora continua
    └── ...
```

### Flujo Completo

```
SOLUCIÓN (una vez por sistema):

  solution/discovery ──→ solution/vision ──→ setup/governance
        │                      │                    │
        ▼                      ▼                    ▼
   Business Case         Solution Vision       Governance
        │                      │                    │
        │                      │                    │
        └──────────────────────┴────────────────────┘
                               │
                    informa múltiples proyectos
                               │
                               ▼

PROYECTO (una vez por iniciativa):

  project/discovery ──→ project/vision ──→ project/design ──→ project/backlog
        │                     │                  │                   │
        ▼                     ▼                  ▼                   ▼
       PRD              Project Vision      Tech Design          Backlog
                              │
                              │ hereda constraints de
                              │ Governance + Solution Vision
                              ▼

FEATURE (múltiples por proyecto):

  feature/plan ──→ feature/implement ──→ feature/review
```

### Contenido de Artefactos

#### Business Case (solution/discovery)

```markdown
# Business Case: [Nombre del Sistema]

## Oportunidad de Negocio
- ¿Qué problema de negocio resuelve?
- ¿Qué oportunidad de mercado existe?

## Stakeholders
- ¿Quiénes son los stakeholders clave?
- ¿Quiénes son los usuarios/clientes?

## Justificación
- ¿Por qué ahora?
- ¿Cuál es el costo de no hacer nada?

## Métricas de Éxito
- ¿Cómo medimos el éxito del sistema?

## Constraints de Negocio
- Compliance, regulaciones
- Presupuesto, timeline
- Dependencias organizacionales
```

#### Solution Vision (solution/vision)

```markdown
# Solution Vision: [Nombre del Sistema]

## Identidad del Sistema
- ¿Qué ES este sistema?
- ¿Cuál es su propósito core?

## Alcance y Boundaries
- ¿Qué incluye?
- ¿Qué explícitamente NO incluye?

## Capacidades Core
- ¿Qué puede hacer el sistema?
- ¿Cuáles son las capacidades principales?

## Dirección Técnica
- Stack tecnológico
- Patrones arquitectónicos
- Decisiones técnicas fundamentales

## Integraciones
- ¿Con qué sistemas se integra?
- ¿Qué APIs expone/consume?

## Quality Attributes
- Performance expectations
- Security level
- Availability requirements
```

#### Project Vision (project/vision) — Antes "Solution Vision"

```markdown
# Project Vision: [Nombre del Proyecto]

## Objetivo del Proyecto
- ¿Qué logra este proyecto específicamente?
- ¿Cómo contribuye a la Solution Vision?

## Approach Arquitectónico
- ¿Qué approach técnico tomamos?
- ¿Qué patrones aplicamos?

## Decisiones Clave
- Decisiones de diseño y sus tradeoffs
- Referencias a ADRs

## Scope
- In scope / Out of scope
- Dependencias con otros proyectos

## Alineamiento
- ¿Cómo se alinea con Governance?
- ¿Qué guardrails aplican?
```

### Relación con Governance (ADR-009)

La Governance se **deriva** de Solution Vision:

```
Solution Vision                    Governance
═══════════════                    ══════════

"Security level: High"      →      MUST-SEC-*: JWT, RBAC, encryption
"Stack: TypeScript"         →      MUST-CODE-*: strict mode, ESLint
"Quality: 99.9% uptime"     →      MUST-TEST-*: 90% coverage, integration tests
"API: REST, OpenAPI"        →      MUST-API-*: versionado, documentación
```

**Solution Vision define WHAT; Governance define HOW to enforce it.**

### Escenarios de Uso

#### Greenfield (Nuevo Sistema)

```
1. solution/discovery  → Crear Business Case
2. solution/vision     → Crear Solution Vision
3. setup/governance    → Derivar Governance de Solution Vision
4. project/discovery   → Crear PRD para primer proyecto
5. project/vision      → Crear Project Vision
6. ...continúa...
```

#### Brownfield (Sistema Existente)

```
1. setup/governance    → Extraer Governance del código existente
2. solution/vision     → Documentar Solution Vision (reverse engineer)
3. solution/discovery  → Documentar Business Case (si no existe)
4. project/discovery   → Crear PRD para nuevo proyecto
5. ...continúa...
```

**En brownfield, el orden puede invertirse** — se comienza por lo que existe (código → governance → vision).

## Consecuencias

### Positivas

| Aspecto | Beneficio |
|---------|-----------|
| **Completitud** | Cadena completa desde necesidad de negocio hasta código |
| **Claridad** | Separación clara entre sistema (perdura) y proyecto (temporal) |
| **Brownfield-friendly** | Terminología "Solution/Sistema" resuena con enterprise |
| **Governance grounded** | Governance tiene input claro (Solution Vision) |
| **Escalabilidad** | Un sistema puede tener múltiples proyectos |
| **Trazabilidad** | Decisiones de proyecto se trazan a Solution Vision |

### Negativas

| Aspecto | Impacto | Mitigación |
|---------|---------|------------|
| **Breaking change** | "Solution Vision" cambia de significado | Migración documentada, período de transición |
| **Más artefactos** | 2 artefactos nuevos a nivel solución | Son opcionales para equipos pequeños |
| **Complejidad percibida** | 3 niveles vs 1 nivel antes | Documentación clara, flujos por escenario |

### Impacto en Katas Existentes

| Kata Actual | Cambio |
|-------------|--------|
| `project/discovery` | Sin cambio (sigue produciendo PRD) |
| `project/vision` | **Renombrar output** de "Solution Vision" a "Project Vision" |
| `project/design` | Sin cambio |
| `setup/governance` | **Actualizar prerequisite**: Solution Vision (nivel solución) |
| `setup/analyze` → `setup/rules` | Ya planeado en ADR-009 |

### Nuevas Katas Requeridas

| Nueva Kata | Propósito | Output |
|------------|-----------|--------|
| `solution/discovery` | Crear Business Case | `specs/main/business_case.md` |
| `solution/vision` | Crear Solution Vision | `specs/main/solution_vision.md` |

**Nota**: El archivo `solution_vision.md` mantiene su nombre, pero ahora es nivel solución, no proyecto. El proyecto produce `project_vision.md`.

## Alternativas Consideradas

### A1: Mantener un solo nivel (Project)

**Rechazado**: No resuelve el problema de Governance sin input. Governance queda "flotando" sin contexto.

### A2: Usar "Product" en lugar de "Solution"

**Rechazado**: "Product" no resuena en brownfield enterprise donde se trabaja con "sistemas" legacy.

### A3: Combinar Business Case + Solution Vision en un solo artefacto

**Considerado viable**: Podría simplificarse a "Solution Charter" que combine ambos. Dejamos como decisión futura post-validación.

### A4: No renombrar "Solution Vision" a nivel proyecto

**Rechazado**: Crearía confusión tener "Solution Vision" en dos niveles con significados diferentes.

## Plan de Implementación

### Fase 1: Documentación

- [ ] Actualizar glossary v2.4 con nuevos términos
- [ ] Crear templates para Business Case y Solution Vision
- [ ] Actualizar template de Project Vision (rename)

### Fase 2: Katas

- [ ] Crear `solution/discovery.md`
- [ ] Crear `solution/vision.md`
- [ ] Actualizar `project/vision.md` (renombrar output)
- [ ] Actualizar `setup/governance.md` (prerequisite)

### Fase 3: Migración

- [ ] Documentar guía de migración para proyectos existentes
- [ ] Actualizar README y onboarding docs

## Glosario de Términos (Extensión v2.4)

| Término | Definición |
|---------|------------|
| **Solution Level** | Nivel de abstracción que define el sistema/solución completo. Artefactos perduran mientras el sistema exista. |
| **Project Level** | Nivel de abstracción que define una iniciativa específica. Artefactos son time-bound. |
| **Business Case** | Artefacto que define la necesidad de negocio, stakeholders, y justificación para un sistema. |
| **Solution Vision** | Artefacto que define la identidad, alcance, capacidades, y dirección técnica de un sistema. |
| **Project Vision** | Artefacto que define el approach arquitectónico y decisiones clave de un proyecto específico. (Antes: "Solution Vision" a nivel proyecto) |

---

<details>
<summary><strong>Referencias</strong></summary>

- **ADR-009**: Continuous Governance Model
- **ADR-008**: Kata/Skill/Context Simplification
- **Research**: Layered Grounding Analysis (RES-LAYERED-GROUNDING-001)
- **Industry**: SAFe Portfolio Level, TOGAF Architecture Vision, Lean Canvas

</details>

---

*Propuesto: 2026-01-30*
*Autor: Kata Harness Design Session*
