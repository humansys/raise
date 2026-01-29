# RaiSE Framework v2.3

> **Reliable AI Software Engineering** — Gobernanza explícita para desarrollo AI-assisted

---

## What's New in v2.3

| Aspecto | v2.2 (Archived) | v2.3 |
|---------|-----------------|------|
| **Ontología** | 7 command categories + SAR/CTX | **Context/Kata/Skill** (3 capas) |
| **Organización** | Commands by function | **Work Cycles** (project/feature/setup/improve) |
| **Ejecución** | spec-kit harness | **Kata Harness** (platform capability) |
| **Terminología** | SAR, CTX, Regla, Command | setup/, context/, Guardrail, Kata/Skill |

---

## Modelo de 3 Capas

```
┌────────────────────────────────────────────────────────────────────────┐
│                      RAISE FRAMEWORK v2.3                               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CONTEXT (Sabiduría)     →  Informa pero no ejecuta                    │
│  constitution, guardrails, patterns, golden data, templates, gates     │
│                                  │                                      │
│                                  ▼                                      │
│  KATA (Práctica)         →  Procesos SDLC por Work Cycle               │
│  project/: discovery, vision, design, backlog                          │
│  feature/: stories, plan, implement, review                            │
│  setup/:   analyze, ecosystem                                          │
│  improve/: retrospective, evolve-kata                                  │
│                                  │                                      │
│                                  ▼                                      │
│  SKILL (Acción)          →  Operaciones atómicas                       │
│  retrieve-mvc, run-gate, check-compliance, explain-rule                │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Principios Core

- **Heutagogía**: Orquestador dirige su propio aprendizaje
- **Jidoka**: Parar en defectos, no propagar errores
- **Facts Not Gaps**: Describir "lo que ES", no evaluar contra externos
- **Governance as Code**: Todo versionado en Git
- **Lean**: 3 conceptos vs 10+ anteriores

---

## Documentos

| Documento | Propósito |
|-----------|-----------|
| [vision.md](./vision.md) | **Solution Vision v2.3** - Documento completo |
| [adrs/](./adrs/) | Architecture Decision Records |
| [schemas/](./schemas/) | JSON Schemas para rule, graph, MVC |

### Context (en .raise/)

| Documento | Propósito |
|-----------|-----------|
| [constitution.md](../../.raise/context/constitution.md) | Principios fundamentales |
| [glossary.md](../../.raise/context/glossary.md) | Terminología canónica v2.3 |
| [work-cycles.md](../../.raise/context/work-cycles.md) | Definición de ciclos de trabajo |
| [philosophy.md](../../.raise/context/philosophy.md) | Filosofía de aprendizaje |

### ADRs Clave

| ADR | Decisión |
|-----|----------|
| [ADR-008](./adrs/adr-008-kata-skill-context-simplification.md) | **Context/Kata/Skill ontology** |
| [ADR-007](./adrs/adr-007-terminology-simplification.md) | Simplificación terminológica |

---

## Quick Start

```bash
# Work Cycle: Setup (1x brownfield)
/setup/analyze
/setup/ecosystem

# Work Cycle: Project (1x por épica)
/project/discovery
/project/vision
/project/design
/project/backlog

# Work Cycle: Feature (Nx por feature)
/feature/stories
/feature/plan
/feature/implement
/feature/review

# Work Cycle: Improve (continuo)
/improve/retrospective

# Skills (on-demand)
/skill/retrieve-mvc --scope "src/services/"
/skill/check-compliance --file "AuthService.ts"
/skill/run-gate --gate "gate-vision"
```

---

## Estructura

```
specs/raise/
├── README.md              # Este archivo
├── vision.md              # Solution Vision v2.3
├── adrs/                  # Architecture Decision Records (inmutables)
│   ├── adr-001..008.md
│   └── README.md
└── schemas/               # JSON Schemas para validación
    ├── rule-schema.json
    ├── graph-schema.json
    └── mvc-schema.json

.raise/                    # Data Store (en raíz del proyecto)
├── context/               # Sabiduría
├── katas/                 # Procesos por Work Cycle
├── skills/                # Operaciones atómicas
├── gates/                 # Criterios de validación
├── templates/             # Scaffolds
└── harness/               # Configuración del Kata Harness
```

---

## Archived (v2.2)

Los documentos v2.2 que usaban terminología SAR/CTX y 7 command categories están archivados en:

```
.raise-v1-archive/specs-v2.2/
```

Ver [archive README](../../.raise-v1-archive/specs-v2.2/README.md) para detalles de migración.

---

*RaiSE Framework v2.3 — Context informa. Kata guía. Skill ejecuta.*
