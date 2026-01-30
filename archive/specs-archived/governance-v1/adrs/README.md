# Architecture Decision Records - RaiSE Governance

> Decisiones arquitectónicas para SAR + raise.ctx

## Índice de ADRs

| ADR | Título | Status | Dependencias |
|-----|--------|--------|--------------|
| [ADR-001](./adr-001-sar-pipeline-phases.md) | Pipeline SAR de 4 Fases | Accepted | - |
| [ADR-002](./adr-002-deterministic-context-delivery.md) | raise.ctx Siempre Determinista | Accepted | - |
| [ADR-003](./adr-003-yaml-rule-format.md) | YAML para Formato de Reglas | Accepted | ADR-001 |
| [ADR-004](./adr-004-separate-graph.md) | Grafo de Relaciones Separado | Accepted | ADR-003 |
| [ADR-005](./adr-005-confidence-adoption-rate.md) | Confidence Basado en Adoption Rate | Accepted | ADR-001, ADR-003 |
| [ADR-006](./adr-006-mvc-summaries.md) | MVC con Summaries para Context Rules | Accepted | ADR-002, ADR-004 |

## Grafo de Dependencias

```
ADR-001 (4 fases SAR)          ADR-002 (determinismo)
    │                               │
    ├───────────────┐               │
    │               │               │
    ▼               ▼               │
ADR-003 (YAML)    ADR-005          │
    │            (confidence)       │
    │                               │
    ▼                               ▼
ADR-004 (grafo) ──────────────► ADR-006 (MVC summaries)
```

## Convenciones

- **Naming**: `adr-NNN-slug-descriptivo.md`
- **Status**: Proposed → Accepted → [Deprecated|Superseded]
- **Template**: `.raise/templates/architecture/adr.md`

---

*Relacionado: [Architecture Overview](../architecture-overview.md)*
