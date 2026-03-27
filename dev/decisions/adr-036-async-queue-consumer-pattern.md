---
id: "ADR-036"
title: "Patrón Async Queue Consumer para llamadas a backend"
date: "2026-03-27"
status: "Proposed"
---

# ADR-036: Patrón Async Queue Consumer para llamadas a backend

## Contexto

Las funciones sync de Forge tienen un timeout hard de 25 segundos. Las operaciones
de graph sync a raise-server pueden exceder ese tiempo (el grafo actual tiene
1,589 nodos + 33K edges). El Async Events API permite hasta 900s (15 min) con
hasta 50 eventos por request y 200KB de payload.

## Decisión

Usar Async Events API + queue consumer (900s timeout) para todas las llamadas a
raise-server que involucren sync de datos o procesamiento que pueda exceder 25s.
Queries simples (`graph/query`) se hacen en sync si son predeciblemente rápidas.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | 15 minutos de timeout acomoda syncs grandes |
| ✅ Positivo | Batch de hasta 50 eventos por request |
| ✅ Positivo | Patrón documentado por Atlassian para LLM calls |
| ⚠️ Negativo | Más complejo que llamadas sync directas |
| ⚠️ Negativo | Resultados no inmediatos — necesita KVS para estado intermedio |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Solo sync calls | Fallaría en graph sync > 25s |
| Forge Realtime para streaming | Preview status, agrega complejidad. Reservar para post-MVP. |
| Chunked sync (múltiples calls de 25s) | Frágil, requiere lógica de retry y state management manual |

---

<details>
<summary><strong>Referencias</strong></summary>

- R4-RAISE-760: Runtime & Constraints, Sección 1
- Forge Async Events API docs
- R4 Evidence E25: Async Events API — 50 events/request, 200KB payload

</details>
