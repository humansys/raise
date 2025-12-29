# ADR-004: Markdown para Humanos, JSON para Máquinas

**Estado:** ✅ Accepted  
**Fecha:** 2025-12-26  
**Actualizado:** 2025-12-28 (añadido JSONL para traces)  
**Autores:** Emilio (HumanSys.ai)

---

## Contexto

Necesitamos formatos para guardrails, specs y configuración. Debate entre legibilidad humana y parseo por máquinas.

## Decisión

Adoptar formatos específicos por audiencia:

| Formato | Uso | Audiencia |
|---------|-----|-----------|
| **Markdown** | Specs, constitution, plans | Humanos leen/editan |
| **JSON** | guardrails.json, config runtime | Máquinas consumen |
| **YAML** | raise.yaml, agent specs | Config human-editable |
| **MDC** | Guardrails source | Markdown + frontmatter YAML |
| **JSONL** | Observable Workflow traces | Append-only logs [v2.0] |

## Consecuencias

### Positivas
- Mejor experiencia para cada audiencia
- Markdown es diff-friendly en PRs
- JSON es parse-fast para runtime
- JSONL es append-only, ideal para logs
- Conversión automática posible

### Negativas
- Múltiples formatos para aprender
- Necesidad de tooling de conversión

### Neutras
- Frontmatter YAML en Markdown es patrón establecido

## Alternativas Consideradas

1. **Solo YAML** - Un formato. Rechazado por: verboso para documentos largos, menos readable.
2. **Solo JSON** - Un formato. Rechazado por: ilegible para humanos, no soporta comentarios.

## Referencias

- [11-data-architecture-v2.md](../11-data-architecture-v2.md) — Formatos de datos

---

*Ver [README.md](./README.md) para índice completo de ADRs.*
