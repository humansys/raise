---
id: "ADR-005"
title: "Confidence Basado en Adoption Rate"
date: "2026-01-28"
status: "Accepted"
related_to: ["SAD-GOV-001", "TEC-SAR-001", "VIS-SAR-001"]
depends_on: ["ADR-001", "ADR-003"]
---

# ADR-005: Confidence Basado en Adoption Rate

## Contexto

SAR extrae reglas de convenciones observadas en el codebase. Necesitamos un score de "confidence" que indique qué tan establecida está una convención. Este score determina:
1. Si la regla se incluye en MVC (filtro por threshold)
2. El nivel de enforcement sugerido (hard, strong, moderate, advisory)

Dos enfoques posibles:
- **Subjetivo**: "esta es una buena práctica" (opinión del LLM)
- **Objetivo**: "el 95% del código sigue este patrón" (dato medible)

## Decisión

Calcular confidence basado en **adoption rate objetivo**: porcentaje de instancias que siguen el patrón vs total de instancias aplicables.

```python
confidence = pattern_matches / total_applicable
# Ejemplo: 95 archivos usan PascalCase para componentes / 100 archivos de componentes = 0.95
```

Mapping a enforcement level:
- 100% → `hard` (unanimous)
- 90-99% → `strong`
- 80-89% → `moderate`
- 60-79% → `advisory`
- <60% → `none` (inconsistent, no extraer como regla)

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Objetivo y verificable: basado en datos, no opiniones |
| ✅ Positivo | Respeta la realidad del codebase: "facts not gaps" |
| ✅ Positivo | Auditable: se puede verificar el cálculo |
| ✅ Positivo | Consistente: mismo codebase = mismo score |
| ⚠️ Negativo | No captura "debería ser así": solo "así es" |
| ⚠️ Negativo | Convenciones nuevas (100% pero N=3) pueden tener score alto artificial |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Score subjetivo del LLM | No reproducible; varía entre ejecuciones |
| Combinación objetivo + subjetivo | Introduce no-determinismo parcial |
| Sin confidence (todas iguales) | Pierde información valiosa para filtering |
| Confidence manual post-extracción | Overhead humano; no escala |

---

<details>
<summary><strong>Referencias</strong></summary>

- [Tech Design](../tech-design.md) - Sección algoritmo de confidence
- [Solution Vision SAR](../solution-vision.md) - Principio "Facts Not Gaps"
- Estadística: adoption rate como medida de consistencia

</details>
