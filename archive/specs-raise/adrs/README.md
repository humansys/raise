# Architecture Decision Records - RaiSE Framework v2.4

> Decisiones arquitectónicas para el framework RaiSE

## Índice de ADRs

| ADR | Título | Status | Capa |
|-----|--------|--------|------|
| [ADR-011](./adr-011-three-directory-model.md) | **Three-Directory Model** | Proposed | Structure |
| [ADR-010](./adr-010-three-level-artifact-hierarchy.md) | **Three-Level Artifact Hierarchy** | Accepted | Ontology |
| [ADR-009](./adr-009-continuous-governance-model.md) | Modelo de Gobernanza Continua | Accepted | Governance |
| [ADR-008](./adr-008-kata-skill-context-simplification.md) | Context/Kata/Skill Simplification | Accepted | Ontology |
| [ADR-007](./adr-007-terminology-simplification.md) | Simplificación Terminológica | Accepted | Ontology |
| [ADR-006](./adr-006-mvc-summaries.md) | MVC con Summaries para Context Rules | Accepted | Layer 2 (CTX) |
| [ADR-005](./adr-005-confidence-adoption-rate.md) | Confidence Basado en Adoption Rate | Accepted | Layer 2 (SAR) |
| [ADR-004](./adr-004-separate-graph.md) | Grafo de Relaciones Separado | Accepted | Layer 1 (Data) |
| [ADR-003](./adr-003-yaml-rule-format.md) | YAML para Formato de Reglas | Accepted | Layer 1 (Data) |
| [ADR-002](./adr-002-deterministic-context-delivery.md) | CTX Siempre Determinista | Accepted | Layer 2 (CTX) |
| [ADR-001](./adr-001-sar-pipeline-phases.md) | Pipeline SAR de 4 Fases | Accepted | Layer 2 (SAR) |

## ADRs por Versión

### v2.4 (Current)

| ADR | Decisión |
|-----|----------|
| **ADR-011** | Three-Directory Model: .raise/ (engine), governance/ (authority), work/ (activity) |
| **ADR-010** | Three-Level Artifact Hierarchy: Solution → Project → Codebase |

### v2.3

| ADR | Decisión |
|-----|----------|
| **ADR-009** | Continuous Governance Model: guardrails derived from Solution Vision |
| **ADR-008** | Context/Kata/Skill ontology (3-layer model) |

### v2.2 and earlier

| ADR | Decisión |
|-----|----------|
| ADR-007 | Terminology simplification (SAR/CTX → setup/context) |
| ADR-001..006 | Foundation decisions |

## Grafo de Dependencias

```
Structure Layer
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  ADR-011 (Three-Directory Model)                            │
│      │                                                       │
│      │ structures artifacts from                            │
│      ▼                                                       │
└──────┼──────────────────────────────────────────────────────┘
       │
Ontology Layer
┌──────┼──────────────────────────────────────────────────────┐
│      ▼                                                       │
│  ADR-010 (Three-Level Hierarchy)                            │
│      │                                                       │
│      │ derives governance from                              │
│      ▼                                                       │
│  ADR-009 (Continuous Governance)                            │
│      │                                                       │
│      │ uses                                                  │
│      ▼                                                       │
│  ADR-008 (Context/Kata/Skill)  ←── ADR-007 (Terminology)    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Component Layer (Legacy)
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  ADR-001 (4 fases SAR)      ADR-002 (CTX determinista)      │
│      │                           │                           │
│      ├───────────────┐           │                           │
│      │               │           │                           │
│      ▼               ▼           │                           │
│  ADR-005           ADR-003       │                           │
│  (confidence)      (YAML)        │                           │
│                      │           │                           │
└──────────────────────┼───────────┼───────────────────────────┘
                       │           │
Data Layer             │           │
┌──────────────────────┼───────────┼───────────────────────────┐
│                      ▼           ▼                           │
│                  ADR-004 ──────► ADR-006                     │
│                  (grafo)        (MVC summaries)              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Convenciones

- **Naming**: `adr-NNN-slug-descriptivo.md`
- **Status**: Proposed → Accepted → [Deprecated|Superseded]
- **Template**: Ver `.raise/templates/architecture/adr.md`

---

*Parte de [RaiSE Framework v2.4](../vision.md)*
