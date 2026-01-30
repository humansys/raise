# RaiSE Framework v2.4

> **Reliable AI Software Engineering** — Gobernanza explícita para desarrollo AI-assisted

---

## What's New in v2.4

| Aspecto | v2.3 | v2.4 |
|---------|------|------|
| **Jerarquía** | Plana (project → feature) | **3 Niveles** (Solution → Project → Codebase) |
| **Work Cycles** | 4 ciclos | **5 ciclos** (+solution/) |
| **Governance** | Standalone | **Derivada de Solution Vision** |
| **Artefactos** | Solution Vision (proyecto) | **Project Vision** (proyecto) + **Solution Vision** (sistema) |
| **Business Case** | No existía | **Nuevo artefacto** nivel solución |

---

## Jerarquía de Tres Niveles (ADR-010)

```
SOLUTION LEVEL (Sistema - perdura)
├── solution/discovery    → Business Case
├── solution/vision       → Solution Vision
└── setup/governance      → Governance (guardrails)
        │
        │ constrains all projects
        ▼
PROJECT LEVEL (Iniciativa - time-bound)
├── project/discovery     → PRD
├── project/vision        → Project Vision (renamed from Solution Vision)
├── project/design        → Tech Design
└── project/backlog       → Backlog
        │
        │ implements via features
        ▼
CODEBASE LEVEL (Implementación)
├── feature/plan          → Implementation plan
├── feature/implement     → Working code
└── feature/review        → Retrospective
```

---

## Modelo de 3 Capas

```
┌────────────────────────────────────────────────────────────────────────┐
│                      RAISE FRAMEWORK v2.4                               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CONTEXT (Sabiduría)     →  Informa pero no ejecuta                    │
│  constitution, guardrails, patterns, golden data, templates, gates     │
│                                  │                                      │
│                                  ▼                                      │
│  KATA (Práctica)         →  Procesos SDLC por Work Cycle               │
│  solution/: discovery, vision                                          │
│  project/:  discovery, vision, design, backlog                         │
│  feature/:  stories, plan, implement, review                           │
│  setup/:    governance, rules, ecosystem                               │
│  improve/:  retrospective, evolve-kata                                 │
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
| [vision.md](./vision.md) | **Solution Vision v2.4** - Documento completo |
| [adrs/](./adrs/) | Architecture Decision Records |
| [schemas/](./schemas/) | JSON Schemas para rule, graph, MVC |

### Context (en .raise/)

| Documento | Propósito |
|-----------|-----------|
| [constitution.md](../../.raise/context/constitution.md) | Principios fundamentales |
| [glossary.md](../../.raise/context/glossary.md) | Terminología canónica v2.4 |
| [work-cycles.md](../../.raise/context/work-cycles.md) | Definición de ciclos de trabajo |
| [philosophy.md](../../.raise/context/philosophy.md) | Filosofía de aprendizaje |

### ADRs Clave

| ADR | Decisión |
|-----|----------|
| [ADR-010](./adrs/adr-010-three-level-artifact-hierarchy.md) | **Three-Level Artifact Hierarchy** |
| [ADR-009](./adrs/adr-009-continuous-governance-model.md) | **Continuous Governance Model** |
| [ADR-008](./adrs/adr-008-kata-skill-context-simplification.md) | Context/Kata/Skill ontology |
| [ADR-007](./adrs/adr-007-terminology-simplification.md) | Simplificación terminológica |

---

## Quick Start

```bash
# Work Cycle: Solution (1x por sistema - greenfield)
/solution/discovery        # → Business Case
/solution/vision           # → Solution Vision

# Work Cycle: Setup (1x por sistema)
/setup/governance          # → Guardrails (derivado de Solution Vision)
/setup/rules               # → Codebase rules
/setup/ecosystem           # → Ecosystem map

# Work Cycle: Project (1x por épica)
/project/discovery         # → PRD
/project/vision            # → Project Vision
/project/design            # → Tech Design
/project/backlog           # → Backlog

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
├── vision.md              # Solution Vision v2.4
├── adrs/                  # Architecture Decision Records (inmutables)
│   ├── adr-001..010.md
│   └── README.md
└── schemas/               # JSON Schemas para validación
    ├── rule-schema.json
    ├── graph-schema.json
    └── mvc-schema.json

.raise/                    # Data Store (en raíz del proyecto)
├── context/               # Sabiduría
├── katas/                 # Procesos por Work Cycle
│   ├── solution/          # NEW v2.4
│   ├── project/
│   ├── feature/
│   ├── setup/
│   └── improve/
├── skills/                # Operaciones atómicas
├── gates/                 # Criterios de validación
├── templates/             # Scaffolds
│   ├── solution/          # NEW v2.4
│   ├── project/           # NEW v2.4
│   └── ...
└── harness/               # Configuración del Kata Harness
```

---

## Migration from v2.3

See [Migration Guide](../../docs/migration/v2.3-to-v2.4-migration.md) for details on:
- Renaming `solution_vision.md` to `project_vision.md` at project level
- Creating solution-level artifacts (Business Case, Solution Vision)
- Updating kata and gate references

---

## Archived (v2.2 and earlier)

Los documentos v2.2 que usaban terminología SAR/CTX y 7 command categories están archivados en:

```
.raise-v1-archive/specs-v2.2/
```

---

*RaiSE Framework v2.4 — Solution define. Project planea. Feature implementa.*
*Context informa. Kata guía. Skill ejecuta.*
