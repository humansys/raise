---
id: "ADR-001"
title: "Pipeline SAR de 4 Fases"
date: "2026-01-28"
status: "Accepted"
related_to: ["SAD-GOV-001", "TEC-SAR-001"]
---

# ADR-001: Pipeline SAR de 4 Fases

## Contexto

SAR necesita extraer convenciones de codebases brownfield de forma estructurada. Un proceso monolítico sería difícil de debuggear, validar y mantener. Diferentes partes del análisis tienen diferentes características: clasificación del proyecto es relativamente simple, mientras que la síntesis de reglas es compleja y requiere LLM.

Se requiere un balance entre granularidad (más fases = más control) y simplicidad (menos fases = menos overhead).

## Decisión

Implementar SAR como un pipeline de **4 fases secuenciales**:

1. **DETECT** (Phase 0): Clasificar tipo de proyecto, estructura, stack
2. **SCAN** (Phase 1): Analizar imports, naming patterns, estructura de archivos
3. **DESCRIBE** (Phase 2): Generar documentación de convenciones
4. **GOVERN** (Phase 3): Extraer reglas con confidence scores y construir grafo

Cada fase produce output validable y puede tener gates entre fases.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Separation of concerns: cada fase tiene responsabilidad única |
| ✅ Positivo | Debuggability: si falla, se sabe en qué fase |
| ✅ Positivo | Validación incremental: gates entre fases detectan errores temprano |
| ✅ Positivo | Extensibilidad: fases pueden evolucionar independientemente |
| ⚠️ Negativo | Overhead de coordinación entre fases |
| ⚠️ Negativo | Context management: cada fase necesita pasar info a la siguiente |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Proceso monolítico (1 fase) | Difícil debuggear; no permite validación incremental |
| 2 fases (análisis + síntesis) | Mezcla concerns; SCAN y DESCRIBE tienen outputs distintos |
| 6+ fases (más granular) | Overhead excesivo; complejidad sin beneficio proporcional |
| Fases paralelas | Dependencias secuenciales: GOVERN necesita output de DESCRIBE |

---

<details>
<summary><strong>Referencias</strong></summary>

- [Tech Design](../tech-design.md) - Sección 2: Arquitectura
- [Solution Vision SAR](../solution-vision.md) - Pipeline LLM-driven
- Patrón: Pipes and Filters (POSA)

</details>
