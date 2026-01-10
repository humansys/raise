# ADR-006a: Validation Gates por Fase

**Estado:** ✅ Accepted  
**Fecha:** 2025-12-28  
**Supersede:** [ADR-006](./adr-006-dod-fractales.md)  
**Autores:** Emilio (HumanSys.ai), Claude (RaiSE Ontology Architect)

---

## Contexto

El concepto de "DoD Fractal" (ADR-006) era semánticamente correcto pero terminológicamente aislado. La investigación de ontologías Agentic AI (diciembre 2025) reveló que:

- La industria usa "Quality Gates", "Approval Gates", "Checkpoints"
- El patrón HITL (Human-in-the-Loop) es el estándar para puntos de control humano
- LangGraph usa "Conditional Edges" y "Checkpoints"
- Lean Manufacturing usa "Quality Gates" y "Pull boundaries"

## Decisión

Renombrar **DoD Fractal** a **Validation Gate**. Cada fase del flujo de valor tiene su propio Validation Gate con criterios específicos que deben pasarse antes de avanzar.

### Estructura de Validation Gates

| Gate | Criterio de Paso | Fase |
|------|------------------|------|
| Gate-Context | Stakeholders y restricciones claras | Discovery |
| Gate-Discovery | PRD validado | Discovery |
| Gate-Vision | Solution Vision aprobada | Vision |
| Gate-Design | Tech Design completo | Design |
| Gate-Backlog | HUs priorizadas | Planning |
| Gate-Plan | Implementation Plan verificado | Planning |
| Gate-Code | Código que pasa validaciones | Implementation |
| Gate-Deploy | Feature en producción | Deployment |

### Implementación MCP

```json
{
  "tool": "validate_gate",
  "parameters": {
    "gate": "Gate-Design",
    "artifact": "spec.md"
  }
}
```

### Escalation Gates (HITL)

Un subtipo especial de Validation Gate que **siempre** requiere intervención humana:

```json
{
  "tool": "escalate",
  "parameters": {
    "gate": "Gate-Vision",
    "reason": "Cambio de alcance significativo",
    "options": ["aprobar", "rechazar", "modificar"]
  }
}
```

## Consecuencias

### Positivas
- Terminología alineada con industria (HITL patterns)
- Interoperabilidad conceptual con LangGraph, CrewAI
- Onboarding más rápido (devs reconocen "gates")
- Mantiene semántica fractal (gates a múltiples niveles)
- Escalation Gates como subtipo natural

### Negativas
- Migración de documentación existente
- Posible confusión temporal con terminología legacy

### Neutras
- El concepto subyacente no cambia

## Alternativas Consideradas

1. **Mantener "DoD Fractal"** - Diferenciador único. Rechazado por: aislamiento terminológico, fricción de adopción.
2. **"Quality Gate"** - Más genérico. Rechazado por: menos específico que "Validation Gate" para contexto AI.
3. **"Checkpoint"** - LangGraph terminology. Rechazado por: conflicto potencial con Git checkpoints.

## Migración

| Archivo | Cambio |
|---------|--------|
| Documentación | "DoD" → "Validation Gate" |
| CLI | `raise dod` → `raise gate` (alias mantenido) |
| MCP Tools | `validate_dod` → `validate_gate` |

## Referencias

- [ADR-006](./adr-006-dod-fractales.md) — ADR supersedido
- [10-system-architecture-v2.md](../10-system-architecture-v2.md) — Implementación MCP
- [21-methodology-v2.md](../21-methodology-v2.md) — Flujo de valor

---

*Ver [README.md](./README.md) para índice completo de ADRs.*
