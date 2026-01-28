---
id: "VIS-RAISE-001"
title: "RaiSE Framework - Solution Vision"
version: "2.0.0"
date: "2026-01-28"
status: "Draft"
author: "Emilio + Claude Opus 4.5"
related_docs:
  - "[SAR Component Vision](./solution-vision-sar.md)"
  - "[Context Component Vision](./solution-vision-context.md)"
  - "[Architecture Overview](./architecture-overview.md)"
  - "[Tech Design](./tech-design.md)"
template: "lean-spec-v1"
---

# RaiSE Framework - Solution Vision

## Resumen Ejecutivo

**RaiSE** (Reliable AI Software Engineering) es un framework de gobernanza para desarrollo asistido por IA. Permite que agentes LLM generen código consistente con las convenciones y arquitectura de codebases existentes.

**Componentes principales:**
- **SAR**: Extrae convenciones de codebases brownfield
- **CTX**: Entrega contexto mínimo viable a agentes
- **Commands**: Workflows ejecutables para procesos de desarrollo

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

### 5 Categorías

```
COMMANDS (16 totales):

setup/                          (Preparación - 1x por proyecto)
├── init-project         # Inicializar proyecto con constitution
├── analyze-codebase     # SAR: analizar codebase brownfield
├── generate-rules       # SAR: generar reglas desde análisis
└── edit-rule            # SAR: editar regla existente

context/                        (Entrega de contexto - on-demand)
├── get                  # CTX: obtener MVC para tarea
├── check                # CTX: verificar compliance de código
└── explain              # CTX: explicar regla específica

project/                        (Nivel proyecto - 1x por proyecto)
├── create-prd           # Discovery → PRD
├── define-vision        # PRD → Solution Vision
├── map-ecosystem        # Mapear ecosistema técnico
├── design-architecture  # Tech Design
├── create-backlog       # Backlog de features
└── estimate-effort      # Estimación

feature/                        (Nivel feature - Nx por feature)
├── create-spec          # Especificación de feature
├── plan-implementation  # Plan de implementación
├── generate-tasks       # Generar tasks granulares
└── implement            # Guía de implementación

tools/                          (Utilidades)
└── export-issues        # Exportar a issue tracker
```

### Modelo Mental

```
"Setup once, Plan the project, Feature by feature, Context when needed"

     SETUP ──────▶ PROJECT ──────▶ FEATURE ◀──────── CONTEXT
   (1x inicial)   (1x planning)   (Nx iterativo)   (on-demand)
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

**Detalle**: [solution-vision-sar.md](./solution-vision-sar.md)

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

**Detalle**: [solution-vision-context.md](./solution-vision-context.md)

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

**Detalle**: [solution-roadmap.md](./solution-roadmap.md)

---

## 10. Documentos Relacionados

| Documento | Propósito |
|-----------|-----------|
| [solution-vision-sar.md](./solution-vision-sar.md) | Detalle componente SAR |
| [solution-vision-context.md](./solution-vision-context.md) | Detalle componente CTX |
| [architecture-overview.md](./architecture-overview.md) | Arquitectura C4 |
| [tech-design.md](./tech-design.md) | Diseño técnico |
| [solution-roadmap.md](./solution-roadmap.md) | Roadmap táctico |
| [adrs/](./adrs/) | Decisiones arquitectónicas |

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-01-28 | Visión inicial (solo SAR + CTX) |
| 2.0.0 | 2026-01-28 | Visión unificada incluyendo Layer 3 (Commands) |

---

*RaiSE Framework: Gobernanza explícita para desarrollo AI-assisted.*
