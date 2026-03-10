---
id: "ADR-006"
title: "MVC con Summaries para Context Rules"
date: "2026-01-28"
status: "Accepted"
related_to: ["SAD-GOV-001", "VIS-CTX-001", "TEC-SAR-001"]
depends_on: ["ADR-002", "ADR-004"]
---

# ADR-006: MVC con Summaries para Context Rules

## Contexto

raise.ctx entrega Minimum-Viable Context (MVC) al agente LLM. El MVC incluye:
- **Primary rules**: reglas directamente aplicables a la tarea
- **Context rules**: reglas relacionadas (vía graph traversal)

Los context windows de LLMs son limitados (4K-128K tokens). Incluir el contenido completo de todas las reglas relacionadas puede exceder el budget y diluir la información relevante.

Tensión entre: completitud (más info = más contexto) vs eficiencia (menos tokens = más espacio para código).

## Decisión

Estructura diferenciada en MVC:
- **Primary rules**: contenido **completo** (pattern, examples, intent)
- **Context rules**: solo **summaries** (id, title, relevance reason)

```yaml
primary_rules:
  - id: "naming-components"
    title: "PascalCase for React Components"
    intent: "Consistency in component naming"
    pattern: { ... }        # Full content
    examples: { ... }       # Full content

context_rules:
  - id: "naming-files"
    title: "kebab-case for file names"
    relevance: "Related naming convention"
    # NO pattern, NO examples - just summary
```

El agente puede solicitar el contenido completo de una context_rule si lo necesita.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Token efficiency: summaries usan ~10% de tokens vs full |
| ✅ Positivo | Más reglas en contexto: caben más summaries que full rules |
| ✅ Positivo | Señal clara: primary = accionable, context = awareness |
| ✅ Positivo | Respeta token budget: predecible y controlable |
| ⚠️ Negativo | Info incompleta en context: agente puede necesitar más |
| ⚠️ Negativo | Requiere buen relevance text: si es vago, no ayuda |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Todo completo (primary + context) | Excede token budget fácilmente |
| Todo summary (incluso primary) | Primary necesita details para ser accionable |
| Solo primary, sin context | Pierde información de relaciones |
| Truncar contenido por tokens | Corta información arbitrariamente |

---

<details>
<summary><strong>Referencias</strong></summary>

- [Tech Design](../tech-design.md) - Sección 3.3: MVC Output Schema
- [Solution Vision raise.ctx](../solution-vision-context.md) - Token efficiency como NFR
- Principio: "Minimum Viable Context" - lo necesario, no más

</details>
