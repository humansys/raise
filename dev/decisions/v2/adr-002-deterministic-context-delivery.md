---
id: "ADR-002"
title: "raise.ctx Siempre Determinista"
date: "2026-01-28"
status: "Accepted"
related_to: ["SAD-GOV-001", "VIS-CTX-001"]
---

# ADR-002: raise.ctx Siempre Determinista

## Contexto

raise.ctx entrega Minimum-Viable Context (MVC) a agentes LLM. Para debugging y reproducibilidad, es crítico que dado el mismo input (task, scope, confidence threshold), el output sea idéntico.

Los agentes LLM ya introducen no-determinismo en la generación de código. Si el retrieval también es no-determinista, diagnosticar problemas se vuelve exponencialmente difícil.

Existe tensión entre determinismo estricto y "inteligencia" en el retrieval (ej: usar embeddings para semantic search).

## Decisión

**raise.ctx será 100% determinista**: mismo input produce exactamente el mismo output, siempre.

Esto implica:
- **Sin LLM** en el proceso de retrieval
- **Sin embeddings** ni búsqueda semántica
- Algoritmos de traversal y filtering **fijos y documentados**
- Ordenamiento de resultados **estable** (no random)

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Reproducibilidad total: debugging simplificado |
| ✅ Positivo | Testeable: unit tests pueden verificar outputs exactos |
| ✅ Positivo | Predecible: el usuario sabe qué esperar |
| ✅ Positivo | Sin costos de API: no hay llamadas a LLM |
| ⚠️ Negativo | Menos "inteligente": no infiere relevancia semántica |
| ⚠️ Negativo | Depende de buena categorización en SAR |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| RAG con embeddings | Introduce no-determinismo; overkill para <500 reglas |
| LLM para ranking de relevancia | Costo, latencia, no-determinismo |
| Híbrido (determinista + LLM opcional) | Complejidad; el modo "inteligente" sería el default de facto |

---

<details>
<summary><strong>Referencias</strong></summary>

- [Solution Vision raise.ctx](../solution-vision-context.md) - Constraint de determinismo
- [Tech Design](../tech-design.md) - Sección retrieval
- Principio: "Deterministic Rails, Non-Deterministic Engine" (SAR usa LLM, raise.ctx no)

</details>
