# RaiSE Framework v2.0

> **Reliable AI Software Engineering** — Gobernanza explícita para desarrollo AI-assisted

---

## What's New in v2.0

| Aspecto | v1.x (Legacy) | v2.0 |
|---------|---------------|------|
| **Scope** | SAR + CTX (infraestructura only) | Framework completo (3 capas) |
| **Architecture** | 2 componentes aislados | 3 capas integradas: Data → Components → Commands |
| **Commands** | raise.* + speckit.* (fragmentado) | 7 categorías unificadas: setup, context, project, feature, validate, improve, tools |
| **Specification** | Templates verbosos | **Lean Spec** (MVS - Minimum Viable Specification) |
| **Context Delivery** | Full dump de reglas | **MVC** (Minimum Viable Context) - determinista |
| **Workflows** | Ad-hoc | **Katas** con Jidoka inline (self-correcting) |

---

## Arquitectura de 3 Capas

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RAISE FRAMEWORK v2.0                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LAYER 3: COMMANDS                                                          │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  setup/    context/   project/   feature/   validate/  improve/  tools/ │ │
│  │  (SAR)          (CTX)           (workflows)      (workflows)           │ │
│  │                                                                         │ │
│  │  [Implementados con Spec-Kit: katas + gates + templates]               │ │
│  └─────────────────────────────────┬──────────────────────────────────────┘ │
│                                    │                                         │
│  LAYER 2: COMPONENTS               │                                         │
│  ┌─────────────────────────────────┴──────────────────────────────────────┐ │
│  │      SAR (Extracción)           │         CTX (Entrega MVC)            │ │
│  │      Batch · LLM synthesis      │         On-demand · Determinista     │ │
│  └─────────────────────────────────┬──────────────────────────────────────┘ │
│                                    │                                         │
│  LAYER 1: DATA STORE               │                                         │
│  ┌─────────────────────────────────┴──────────────────────────────────────┐ │
│  │  .raise/  →  rules/*.yaml  │  graph.yaml  │  conventions.md            │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Principios Core

### Lean Specification
- **MVS** (Minimum Viable Specification): 4 secciones requeridas, resto opcional
- **Progressive Discovery**: Documentar cuando se necesita, no antes
- **Target**: <1.5:1 ratio markdown:code (vs 3.7:1 tradicional)

### Minimum Viable Context (MVC)
- **Relevante**: Solo reglas que aplican al task/scope
- **Denso**: Summaries para context, full content para primary
- **Determinista**: Mismo input = mismo output (100%)

### Facts Not Gaps
- SAR describe "lo que ES", no evalúa contra estándares externos
- Confidence basado en adoption rate objetivo
- Sin juicios subjetivos ("buena práctica")

### Jidoka (Stop and Fix)
- Cada paso en katas tiene verificación + recovery
- Parar en defectos, no propagar errores
- Self-correcting workflows

---

## Documentos

| Documento | Propósito |
|-----------|-----------|
| [vision.md](./vision.md) | **Solution Vision** - Framework completo |
| [architecture.md](./architecture.md) | Arquitectura C4 (Context + Container) |
| [design.md](./design.md) | Tech Design (SAR + CTX) |
| [roadmap.md](./roadmap.md) | Roadmap táctico |

### Componentes

| Componente | Documento | Propósito |
|------------|-----------|-----------|
| **SAR** | [sar/vision.md](./sar/vision.md) | Software Architecture Reconstruction |
| **CTX** | [ctx/vision.md](./ctx/vision.md) | Context Delivery (MVC) |

### Commands

| Documento | Propósito |
|-----------|-----------|
| [commands/standardization.md](./commands/standardization.md) | Roadmap de estandarización |

### ADRs

| ADR | Decisión |
|-----|----------|
| [ADR-001](./adrs/adr-001-sar-pipeline-phases.md) | Pipeline SAR de 4 fases |
| [ADR-002](./adrs/adr-002-deterministic-context-delivery.md) | CTX siempre determinista |
| [ADR-003](./adrs/adr-003-yaml-rule-format.md) | YAML para reglas |
| [ADR-004](./adrs/adr-004-separate-graph.md) | Grafo separado de reglas |
| [ADR-005](./adrs/adr-005-confidence-adoption-rate.md) | Confidence por adoption rate |
| [ADR-006](./adrs/adr-006-mvc-summaries.md) | MVC con summaries |

---

## Quick Start

```bash
# 1. Setup: Extraer convenciones del codebase (brownfield)
/setup/analyze-codebase
/setup/generate-rules

# 2. Project: Crear documentación de proyecto
/project/create-prd
/project/define-vision
/project/design-architecture
/project/prioritize-features

# 3. Feature: Desarrollar features
/feature/design-feature "FID-001: Auth Module"
/feature/create-backlog
/feature/generate-stories "Item 1"
/feature/plan-implementation
/feature/implement

# 4. Validate: Validar artefactos on-demand
/validate/validate-prd
/validate/validate-plan

# 5. Context: Consultar reglas cuando necesites
/context/get --task "implement auth service"
/context/check --file "src/services/AuthService.ts"

# 6. Improve: Mejora continua
/improve/manage-kata
```

---

## Estructura de Directorio

```
specs/raise/
├── README.md              # Este archivo
├── vision.md              # Solution Vision v2.0
├── architecture.md        # Arquitectura C4
├── design.md              # Tech Design
├── roadmap.md             # Roadmap táctico
│
├── sar/                   # Componente SAR
│   └── vision.md          # SAR Solution Vision
│
├── ctx/                   # Componente CTX
│   └── vision.md          # CTX Solution Vision
│
├── commands/              # Command Layer (7 categorías)
│   ├── architecture.md    # Arquitectura de comandos v2.1
│   └── standardization.md # Migration roadmap
│
└── adrs/                  # Architecture Decision Records
    ├── README.md
    └── adr-001..006.md
```

---

## Status

| Fase | Estado |
|------|--------|
| A1: Foundation & Schemas | ⏳ En progreso |
| A2: SAR Command | Pendiente |
| A3: CTX Commands | Pendiente |
| A4: Documentation | Pendiente |

**Track activo**: Open Core (Track A)

---

*RaiSE Framework v2.0 — Gobernanza explícita para desarrollo AI-assisted*
