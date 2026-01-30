---
id: "ADR-003"
title: "YAML para Formato de Reglas"
date: "2026-01-28"
status: "Accepted"
related_to: ["SAD-GOV-001", "TEC-SAR-001"]
depends_on: ["ADR-001"]
---

# ADR-003: YAML para Formato de Reglas

## Contexto

Las reglas extraídas por SAR necesitan un formato de serialización. Los candidatos principales son JSON y YAML. Ambos son ampliamente soportados, parseables, y git-friendly.

Las reglas serán:
1. Generadas por LLM (en fase GOVERN de SAR)
2. Leídas por raise.ctx (retrieval determinista)
3. Editadas manualmente por humanos (ajustes, correcciones)
4. Versionadas en Git (diff-friendly importante)

Research de semantic density indica que LLMs procesan mejor YAML que JSON para contenido semántico.

## Decisión

Usar **YAML** como formato para reglas individuales (`.raise/rules/*.yaml`) y para el grafo de relaciones (`.raise/graph.yaml`).

JSON Schema se usa para **validación** de los archivos YAML.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Mejor legibilidad humana: menos ruido sintáctico que JSON |
| ✅ Positivo | LLM-friendly: research indica mejor comprensión |
| ✅ Positivo | Soporta comentarios: útil para documentar inline |
| ✅ Positivo | Multiline strings naturales: ideal para ejemplos de código |
| ⚠️ Negativo | Indentation-sensitive: errores de whitespace posibles |
| ⚠️ Negativo | Parsing ligeramente más lento que JSON |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| JSON | Más verboso; no soporta comentarios; peor para multiline |
| TOML | Menos adopción; LLMs menos familiarizados |
| Markdown con frontmatter | No parseable estructuradamente el contenido |
| XML | Excesivamente verboso; poor developer experience |

---

<details>
<summary><strong>Referencias</strong></summary>

- [Tech Design](../tech-design.md) - Sección 3.1: Rule Schema
- [Semantic Density Research](../../research/sar-component/semantic-density/) - Comparación de formatos
- YAML 1.2 Specification

</details>
