# Architecture Decision Records - RaiSE Framework v2.0

> Decisiones arquitectónicas para el framework RaiSE

## Índice de ADRs

| ADR | Título | Status | Capa |
|-----|--------|--------|------|
| [ADR-001](./adr-001-sar-pipeline-phases.md) | Pipeline SAR de 4 Fases | Accepted | Layer 2 (SAR) |
| [ADR-002](./adr-002-deterministic-context-delivery.md) | CTX Siempre Determinista | Accepted | Layer 2 (CTX) |
| [ADR-003](./adr-003-yaml-rule-format.md) | YAML para Formato de Reglas | Accepted | Layer 1 (Data) |
| [ADR-004](./adr-004-separate-graph.md) | Grafo de Relaciones Separado | Accepted | Layer 1 (Data) |
| [ADR-005](./adr-005-confidence-adoption-rate.md) | Confidence Basado en Adoption Rate | Accepted | Layer 2 (SAR) |
| [ADR-006](./adr-006-mvc-summaries.md) | MVC con Summaries para Context Rules | Accepted | Layer 2 (CTX) |
| [ADR-007](./adr-007-terminology-simplification.md) | Simplificación Terminológica | Accepted | Ontology |
| [ADR-008](./adr-008-kata-skill-context-simplification.md) | Context/Kata/Skill Simplification | Accepted | Ontology |
| [ADR-009](./adr-009-continuous-governance-model.md) | Modelo de Gobernanza Continua | Proposed | Governance |

## Grafo de Dependencias

```
Layer 2 (Components)
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  ADR-001 (4 fases SAR)      ADR-002 (CTX determinista)  │
│      │                           │                       │
│      ├───────────────┐           │                       │
│      │               │           │                       │
│      ▼               ▼           │                       │
│  ADR-005           ADR-003       │                       │
│  (confidence)      (YAML)        │                       │
│                      │           │                       │
└──────────────────────┼───────────┼───────────────────────┘
                       │           │
Layer 1 (Data)         │           │
┌──────────────────────┼───────────┼───────────────────────┐
│                      ▼           ▼                       │
│                  ADR-004 ──────► ADR-006                 │
│                  (grafo)        (MVC summaries)          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Convenciones

- **Naming**: `adr-NNN-slug-descriptivo.md`
- **Status**: Proposed → Accepted → [Deprecated|Superseded]
- **Template**: Ver `.raise/templates/architecture/adr.md`

---

*Parte de [RaiSE Framework v2.0](../vision.md)*
