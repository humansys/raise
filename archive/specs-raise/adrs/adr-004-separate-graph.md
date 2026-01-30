---
id: "ADR-004"
title: "Grafo de Relaciones Separado de Reglas"
date: "2026-01-28"
status: "Accepted"
related_to: ["SAD-GOV-001", "TEC-SAR-001"]
depends_on: ["ADR-003"]
---

# ADR-004: Grafo de Relaciones Separado de Reglas

## Contexto

Las reglas tienen relaciones entre sí: una regla puede requerir otra, conflictuar con otra, o estar relacionada temáticamente. Estas relaciones son críticas para raise.ctx (graph traversal para MVC).

Dos opciones arquitectónicas:
1. **Embebido**: cada regla contiene sus relaciones (`requires: [rule-x, rule-y]`)
2. **Separado**: un archivo `graph.yaml` centraliza todas las relaciones

El trade-off es entre cohesión (regla auto-contenida) y eficiencia de traversal.

## Decisión

Mantener el grafo de relaciones en un **archivo separado** (`graph.yaml`), no embebido en cada regla.

```yaml
# .raise/graph.yaml
edges:
  - from: "rule-a"
    to: "rule-b"
    type: "requires"
    reason: "rule-a depends on naming convention from rule-b"
```

Las reglas individuales son **self-contained chunks** sin referencias a otras reglas.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Traversal eficiente: cargar solo el grafo, no todas las reglas |
| ✅ Positivo | Reglas portables: cada regla es un chunk independiente |
| ✅ Positivo | Evolución independiente: grafo y reglas pueden cambiar por separado |
| ✅ Positivo | Visualización: fácil generar visualización del grafo |
| ⚠️ Negativo | Sincronización: grafo puede quedar desactualizado si se borra regla |
| ⚠️ Negativo | Dos archivos que editar: regla + actualizar grafo |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Relaciones embebidas en cada regla | Traversal ineficiente: cargar todas las reglas para navegar |
| Doble: embebido + grafo derivado | Duplicación; riesgo de inconsistencia |
| Base de datos (SQLite) | Overhead; no diff-friendly; dependencia adicional |

---

<details>
<summary><strong>Referencias</strong></summary>

- [Tech Design](../tech-design.md) - Sección 3.2: Graph Schema
- [Architecture Overview](../architecture-overview.md) - Graph Engine component
- Patrón: Adjacency List representation

</details>
