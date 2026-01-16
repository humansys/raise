# ADR-007: Guardrails over Rules

**Estado:** ✅ Accepted  
**Fecha:** 2025-12-28  
**Autores:** Emilio (HumanSys.ai), Claude (RaiSE Ontology Architect)

---

## Contexto

El término "Rule" (usado en v1.x) es semánticamente correcto pero:
- Es genérico y ambiguo (¿business rule? ¿lint rule? ¿coding rule?)
- No connota protección activa
- La industria enterprise AI converge en "Guardrail" (DSPy, LangChain, NVIDIA NeMo)

## Decisión

Renombrar **Rule** a **Guardrail** como término principal para directivas operacionales que gobiernan comportamiento de agentes y calidad de código.

### Jerarquía de Governance Actualizada

```
Constitution (Principios inmutables)
    ↓
Guardrails (Directivas operacionales)
    ↓
Specs (Contratos de implementación)
    ↓
Validation Gates (Puntos de control)
```

### Diferenciación Clave

| Aspecto | Constitution | Guardrail |
|---------|--------------|-----------|
| Mutabilidad | Casi nunca cambia | Cambia por proyecto/fase |
| Nivel | Filosófico | Operacional |
| Enforcement | Cultural | Automatizable |
| Ejemplo | "Humanos definen, máquinas ejecutan" | "Máximo 500 líneas por archivo" |

### Mapeo MCP

```json
{
  "resource": "raise://guardrails",
  "content": {
    "guardrails": [
      {"id": "GR-001", "scope": "code", "rule": "..."}
    ]
  }
}
```

## Consecuencias

### Positivas
- Alineamiento con terminología enterprise AI
- Connota protección activa (vs. "rule" pasivo)
- Diferenciación clara con Constitution
- Compatible con DSPy Assertions pattern

### Negativas
- Migración de archivos `raise-rules.json` → `guardrails.json`
- Actualización de documentación

### Neutras
- "Rule" permanece como alias válido en CLI (`raise rule` = `raise guardrail`)

## Alternativas Consideradas

1. **Mantener "Rule"** - Simple. Rechazado por: ambigüedad, no connota protección.
2. **"Constraint"** - Técnicamente preciso. Rechazado por: menos intuitivo, suena restrictivo.
3. **"Policy"** - Enterprise-friendly. Rechazado por: conflicto potencial con security policies.

## Migración

| Antes | Después |
|-------|---------|
| `raise-rules.json` | `guardrails.json` |
| `.raise/rules/` | `.raise/guardrails/` |
| `raise rule check` | `raise guardrail check` |

**Compatibilidad:** CLI mantiene `raise rule` como alias durante v2.x.

## Referencias

- [20-glossary-v2.md](../20-glossary-v2.md) — Definición formal
- [10-system-architecture-v2.md](../10-system-architecture-v2.md) — Recursos MCP

---

*Ver [README.md](./README.md) para índice completo de ADRs.*
