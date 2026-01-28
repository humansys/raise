---
id: "VIS-RAISE-002"
title: "RaiSE Framework v2.0 - Solution Vision"
version: "2.1.0"
date: "2026-01-28"
status: "Draft"
author: "Emilio + Claude Opus 4.5"
supersedes: "VIS-RAISE-001 (governance-only, pre-v2)"
related_docs:
  - "[SAR Component Vision](./sar/vision.md)"
  - "[CTX Component Vision](./ctx/vision.md)"
  - "[Architecture](./architecture.md)"
  - "[Tech Design](./design.md)"
  - "[Roadmap](./roadmap.md)"
template: "lean-spec-v1"
---

# RaiSE Framework v2.0 - Solution Vision

## Resumen Ejecutivo

**RaiSE v2.0** (Reliable AI Software Engineering) es un framework de gobernanza para desarrollo AI-assisted. Transforma conocimiento tribal implícito en **gobernanza explícita, versionada, y ejecutable**.

**Evolución desde v1.x:**

| Aspecto | v1.x | v2.0 |
|---------|------|------|
| Scope | Infraestructura (SAR + CTX) | Framework completo (3 capas) |
| Specification | Templates verbosos | **Lean Spec** (MVS) |
| Context | Full dump | **MVC** (Minimum Viable Context) |
| Commands | Fragmentados (raise.*, speckit.*) | 7 categorías unificadas |
| Workflows | Ad-hoc | **Katas** con Jidoka inline |

**Componentes principales:**
- **SAR**: Extrae convenciones de codebases brownfield (Layer 2)
- **CTX**: Entrega contexto mínimo viable a agentes (Layer 2)
- **Commands**: Workflows ejecutables en 5 categorías (Layer 3)
- **Data Store**: Reglas y grafo versionados (Layer 1)

---

## 1. Arquitectura de 3 Capas

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RAISE FRAMEWORK                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LAYER 3: COMMANDS (Workflows ejecutables)                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  setup/              context/           project/          feature/     │ │
│  │  ├─ init-project     ├─ get             ├─ create-prd     ├─ create-spec│
│  │  ├─ analyze-codebase ├─ check           ├─ define-vision  ├─ plan      │ │
│  │  ├─ generate-rules   └─ explain         ├─ design-arch    ├─ tasks     │ │
│  │  └─ edit-rule                           ├─ create-backlog └─ implement │ │
│  │                                          └─ estimate                    │ │
│  │  [Implementados con tecnología spec-kit: katas + gates + templates]    │ │
│  │                                                                         │ │
│  └─────────────────────────────┬──────────────────────────────────────────┘ │
│                                │ usa                                         │
│                                ▼                                             │
│  LAYER 2: COMPONENTS (Infraestructura de gobernanza)                        │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  ┌─────────────────────────┐       ┌─────────────────────────────────┐ │ │
│  │  │          SAR            │       │           CTX                   │ │ │
│  │  │    (Extracción)         │       │    (Entrega de MVC)             │ │ │
│  │  ├─────────────────────────┤       ├─────────────────────────────────┤ │ │
│  │  │ • Analiza codebase      │       │ • Lee rules + graph             │ │ │
│  │  │ • Extrae patrones       │       │ • Traversal determinista        │ │ │
│  │  │ • Genera reglas         │ ────▶ │ • Filtra por task/scope         │ │ │
│  │  │ • Construye grafo       │ genera│ • Entrega MVC al agente         │ │ │
│  │  ├─────────────────────────┤       ├─────────────────────────────────┤ │ │
│  │  │ Frecuencia: Batch       │       │ Frecuencia: On-demand           │ │ │
│  │  │ Método: LLM synthesis   │       │ Método: Determinista            │ │ │
│  │  └─────────────────────────┘       └─────────────────────────────────┘ │ │
│  │                                                                         │ │
│  │  Ver: solution-vision-sar.md        Ver: solution-vision-context.md    │ │
│  │                                                                         │ │
│  └─────────────────────────────┬──────────────────────────────────────────┘ │
│                                │ produce/consume                             │
│                                ▼                                             │
│  LAYER 1: DATA STORE (Artefactos de gobernanza)                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  .raise/                                                                │ │
│  │  ├── project-profile.yaml    # Clasificación del proyecto              │ │
│  │  ├── conventions.md          # Documentación human-readable            │ │
│  │  ├── rules/                  # Reglas unitarias                        │ │
│  │  │   ├── naming/*.yaml                                                 │ │
│  │  │   ├── architecture/*.yaml                                           │ │
│  │  │   └── patterns/*.yaml                                               │ │
│  │  └── graph.yaml              # Grafo de relaciones                     │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Problema y Solución

### Declaración del Problema

Los equipos de desarrollo tienen **conocimiento tribal implícito** sobre convenciones y patrones que no está documentado de forma consumible por agentes LLM.

| Aspecto | Descripción |
|---------|-------------|
| **Quién** | Desarrolladores (Orquestadores) y agentes LLM trabajando en codebases brownfield |
| **Impacto** | Agentes sin contexto generan código inconsistente con la arquitectura existente |
| **Cuándo** | Cada vez que un agente trabaja sin conocer las "reglas no escritas" |
| **Por qué importa** | Sin gobernanza explícita, la calidad del código AI-generated es impredecible |

### Visión de la Solución

RaiSE transforma conocimiento tribal implícito en **gobernanza explícita, versionada, y ejecutable**:

1. **SAR extrae** convenciones de codebases existentes (facts, not gaps)
2. **Data Store persiste** reglas en formato estructurado (YAML + Graph)
3. **CTX entrega** contexto mínimo viable a agentes cuando lo necesitan
4. **Commands orquestan** workflows de desarrollo con gobernanza integrada

**Resultado**: Código AI-generated que pasa code review en el primer intento.

---

## 3. Estructura de Comandos (Layer 3)

### 7 Categorías

```
COMMANDS (35 totales: 24 comandos + 11 gates):

setup/                          (SAR + Init - 1x brownfield)
├── init-project                # Inicializar proyecto con constitution
├── analyze-codebase            # SAR: analizar codebase brownfield
├── generate-rules              # SAR: generar reglas desde análisis
└── edit-rule                   # SAR: editar regla existente

context/                        (CTX - on-demand)
├── get                         # CTX: obtener MVC para tarea
├── check                       # CTX: verificar compliance de código
└── explain                     # CTX: explicar regla específica

project/                        (Project Flow - 1x proyecto)
├── create-prd                  # Discovery → PRD
├── define-vision               # PRD → Solution Vision
├── map-ecosystem               # Vision → Ecosystem Map
├── design-architecture         # Vision → Technical Design
├── prioritize-features         # Tech Design → Feature Prioritization
├── create-backlog              # Prioritization → Project Backlog
└── estimate-effort             # Backlog → Estimation Roadmap

feature/                        (Feature Flow - Nx feature)
├── design-feature              # Feature ID → Feature Design (incluye spec)
├── create-backlog              # Feature Design → Feature Backlog
├── generate-stories            # Backlog Item → User Story individual
├── plan-implementation         # Stories → Plan + Tasks (integrado)
└── implement                   # Plan → Code + Tests

validate/                       (Gates On-Demand - 11 comandos)
├── validate-prd                # Gate: PRD quality
├── validate-vision             # Gate: Vision alignment
├── validate-ecosystem          # Gate: Ecosystem completeness
├── validate-architecture       # Gate: Tech Design quality
├── validate-prioritization     # Gate: Prioritization matrix
├── validate-backlog            # Gate: Backlog quality
├── validate-estimation         # Gate: Estimation accuracy
├── validate-feature-design     # Gate: Feature Design completeness
├── validate-stories            # Gate: User Stories quality
├── validate-plan               # Gate: Plan consistency
└── validate-requirements       # Gate: Requirements quality

improve/                        (Mejora Continua)
├── manage-kata                 # Gestión de katas
├── run-retrospective           # (Planned) Ejecutar retrospectiva
└── audit-conventions           # (Planned) Auditar convenciones vs código

tools/                          (Utilidades)
├── export-issues               # Exportar a issue tracker
└── generate-contract           # Generar Statement of Work (SOW)
```

### Modelo Mental

```
"Setup once, Plan the project, Feature by feature, Validate always, Context when needed"

     SETUP ──────▶ PROJECT ──────▶ FEATURE ◀──────── CONTEXT
   (1x inicial)   (1x planning)   (Nx iterativo)   (on-demand)
        │              │              │
        └──────────────┴──────────────┴──────▶ VALIDATE (on-demand)
                                               IMPROVE (continuo)
```

### Tecnología: Spec-Kit Harness

Cada comando se implementa usando el patrón spec-kit:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPEC-KIT HARNESS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  COMMAND                        KATA                             │
│  (/feature/create-spec)  ────▶ (workflow paso a paso)           │
│         │                             │                          │
│         │                             ▼                          │
│         │                       TEMPLATE                         │
│         │                  (estructura del output)               │
│         │                             │                          │
│         │                             ▼                          │
│         └───────────────────▶   GATE                            │
│                            (validación de calidad)               │
│                                                                  │
│  Jidoka Inline: Cada paso tiene verificación + recovery         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Componentes de Infraestructura (Layer 2)

### SAR (Software Architecture Reconstruction)

**Responsabilidad**: Extraer convenciones de codebases brownfield.

| Aspecto | Descripción |
|---------|-------------|
| **Input** | Codebase brownfield |
| **Output** | rules/*.yaml, graph.yaml, conventions.md |
| **Método** | LLM synthesis (Open Core) / Determinista (Licensed) |
| **Frecuencia** | Batch (cuando codebase cambia significativamente) |
| **Principio** | "Facts Not Gaps" - describe lo que ES, no evalúa |

**Pipeline**: DETECT → SCAN → DESCRIBE → GOVERN

**Detalle**: [sar/vision.md](./sar/vision.md)

### CTX (Context Delivery)

**Responsabilidad**: Entregar Minimum-Viable Context a agentes.

| Aspecto | Descripción |
|---------|-------------|
| **Input** | Task + Scope + Confidence threshold |
| **Output** | MVC (primary_rules, context_rules, warnings) |
| **Método** | Determinista (graph traversal, pattern matching) |
| **Frecuencia** | On-demand (cada vez que agente necesita contexto) |
| **Principio** | Mismo input = mismo output (100% reproducible) |

**Pipeline**: SCOPE MATCH → GRAPH TRAVERSE → FILTER → ASSEMBLE MVC

**Detalle**: [ctx/vision.md](./ctx/vision.md)

---

## 5. Data Store (Layer 1)

### Estructura

```
.raise/
├── project-profile.yaml      # Metadata del proyecto
│   └── type, structure, stack, analysis_flags
│
├── conventions.md            # Documentación human-readable
│   └── Convenciones descritas en prosa
│
├── rules/                    # Reglas unitarias (1 archivo = 1 regla)
│   ├── naming/
│   │   ├── ts-service-suffix.yaml
│   │   └── ts-repository-suffix.yaml
│   ├── architecture/
│   │   └── ts-no-direct-db-access.yaml
│   └── patterns/
│       └── ts-async-error-handling.yaml
│
└── graph.yaml                # Grafo de relaciones
    ├── nodes: [rule references]
    └── edges: [requires, conflicts_with, supersedes, related_to]
```

### Principios de Diseño

| Principio | Implementación |
|-----------|----------------|
| **Portable** | YAML + Markdown, sin dependencias |
| **Git-friendly** | Diffable, mergeable, versionable |
| **Human-editable** | Formato legible, comentarios permitidos |
| **Machine-parseable** | JSON Schema para validación |

---

## 6. Estrategia de Producto: Open Core

### Modelo de Negocio

```
┌─────────────────────────────────────────────────────────────────┐
│                     OPEN CORE MODEL                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  OPEN CORE (Free)              LICENSED (Paid)                  │
│  ┌─────────────────────┐       ┌─────────────────────────────┐  │
│  │ • SAR LLM synthesis │       │ • SAR determinista          │  │
│  │ • CTX completo      │       │ • Observabilidad            │  │
│  │ • Todos los commands│       │ • CI/CD integrations        │  │
│  │ • Katas + Gates     │       │ • Multi-repo governance     │  │
│  │ • Templates         │       │ • Soporte enterprise        │  │
│  └─────────────────────┘       └─────────────────────────────┘  │
│                                                                  │
│  OUTPUT IDÉNTICO: Ambos producen mismo formato de datos         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Flywheel de Adopción

```
Developer usa RaiSE Open Core (free)
         ↓
Extrae reglas, usa commands
         ↓
Equipo ve valor en gobernanza
         ↓
Empresa necesita precisión + observabilidad
         ↓
Upgrade a Licensed
```

---

## 7. Principios Core

### Facts Not Gaps

SAR describe "lo que ES", no evalúa contra estándares externos.

| ✅ Lo que RaiSE hace | ❌ Lo que RaiSE NO hace |
|---------------------|------------------------|
| "95% usa camelCase" | "Viola principio SOLID" |
| Mide consistencia interna | Impone Clean Architecture |
| Identifica inconsistencias | Prescribe refactorizaciones |

### Deterministic Rails, Non-Deterministic Engine

- **Rails** (determinista): CTX retrieval, Gates, Templates
- **Engine** (no-determinista): SAR LLM synthesis

### Jidoka (Stop and Fix)

Cada paso en katas tiene:
- **Verificación**: Criterio observable de completitud
- **Recovery**: "Si no puedes continuar → acción correctiva"

---

## 8. Métricas de Éxito

### Métricas de Producto

| Métrica | Target | Descripción |
|---------|--------|-------------|
| Code review pass rate | >80% | Código con MVC pasa review |
| Rule precision | >85% | Reglas extraídas son correctas |
| CTX latency | <200ms | Tiempo de respuesta |
| Command adoption | 100% | Todos los workflows usan RaiSE |

### Métricas de Adopción

| Métrica | Target |
|---------|--------|
| Proyectos con SAR ejecutado | 10+ (Open Core) |
| Reglas extraídas total | 500+ |
| Upgrade rate a Licensed | 10% |

---

## 9. Roadmap de Alto Nivel

### Track A: Open Core

| Fase | Entregables | Estado |
|------|-------------|--------|
| A1: Foundation | Schemas, templates | ⏳ En progreso |
| A2: SAR Command | `setup/analyze-codebase` | Pendiente |
| A3: CTX Commands | `context/get`, `check`, `explain` | Pendiente |
| A4: Documentation | Guías, ejemplos | Pendiente |

### Track B: Licensed

| Fase | Entregables | Estado |
|------|-------------|--------|
| B1: SAR Determinista | ast-grep, ripgrep integration | Post-validación A |
| B2: Observabilidad | Dashboard, métricas | Post-validación A |
| B3: Enterprise | CI/CD, multi-repo | Post-validación A |

**Detalle**: [roadmap.md](./roadmap.md)

---

## 10. Documentos Relacionados

| Documento | Propósito |
|-----------|-----------|
| [sar/vision.md](./sar/vision.md) | Detalle componente SAR |
| [ctx/vision.md](./ctx/vision.md) | Detalle componente CTX |
| [architecture.md](./architecture.md) | Arquitectura C4 |
| [design.md](./design.md) | Diseño técnico |
| [roadmap.md](./roadmap.md) | Roadmap táctico |
| [commands/standardization.md](./commands/standardization.md) | Estandarización de comandos |
| [adrs/](./adrs/) | Decisiones arquitectónicas |

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-01-28 | Visión inicial (solo SAR + CTX como "governance") |
| 2.0.0 | 2026-01-28 | **Major refactor**: Framework completo con 3 capas, Lean Spec, MVC, 5 categorías de comandos |
| 2.0.0 | 2026-01-28 | Visión unificada incluyendo Layer 3 (Commands) |
| 2.1.0 | 2026-01-28 | **7 categorías**: setup, context, project, feature, validate, improve, tools |

---

*RaiSE Framework: Gobernanza explícita para desarrollo AI-assisted.*
