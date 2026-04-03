---
id: "ADR-035"
title: "raise-server como Knowledge Store canónico (no Forge Storage)"
date: "2026-03-27"
status: "Proposed"
---

# ADR-035: raise-server como Knowledge Store canónico (no Forge Storage)

## Contexto

El knowledge graph de RaiSE (1,589 nodos + 33K edges para un solo proyecto)
necesita un store accesible desde Forge. Opciones: Forge Custom Entity Store
(240KB/valor, 100 condiciones/query, per-installation) o raise-server PostgreSQL
(ya existente, GIN full-text search, sin límites prácticos de query).

## Decisión

raise-server PostgreSQL es el store canónico del knowledge graph. Forge KVS se
usa exclusivamente para estado de conversación y caché local.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | PostgreSQL + GIN escala a grafos grandes sin límites artificiales |
| ✅ Positivo | raise-server ya existe y está validado (E275, 90+ tests) |
| ✅ Positivo | Queries complejas sin límite de 100 condiciones |
| ⚠️ Negativo | Dependencia externa — raise-server debe estar disponible |
| ⚠️ Negativo | Latencia adicional (Forge → fetch() → raise-server) |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Forge Custom Entity Store como primario | Límites de 100 condiciones y 240KB por valor. Un proyecto ya tiene 33K edges. A escala org sería inviable. |
| Dual-write (Forge + raise-server) | Complejidad de sincronización sin valor claro. Forge Storage no tiene las queries que necesitamos. |

---

<details>
<summary><strong>Referencias</strong></summary>

- R4-RAISE-760: Storage Options, Sección 2
- E275: Shared Memory Backend — validó raise-server con datos reales
- R3-RAISE-760: Recommendation R3 — "Keep knowledge graph in rai-server, not Forge"

</details>
