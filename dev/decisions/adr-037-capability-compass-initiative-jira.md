---
id: "ADR-037"
title: "Capabilities en Compass, Initiatives en Jira"
date: "2026-03-27"
status: "Proposed"
---

# ADR-037: Capabilities en Compass, Initiatives en Jira

## Contexto

RaiSE tiene dos ejes de clasificación por encima de Epic:

- **Initiative**: objetivo estratégico de negocio que agrupa epics hacia un resultado ("PRO Launch", "OSS Product Excellence"). Es temporal — se cierra al lograr el objetivo.
- **Capability**: competencia técnica permanente del producto ("Skill Engine", "Adapter Layer", "Session & Workstream"). No se "completa" — persiste y evoluciona.

Hoy ambos existen como issue types en Jira (RAISE project). Initiative sin issues activos (creados y borrados dos veces). Capability con 12 items (C1-C12) sin epics vinculados.

El problema: Jira es una herramienta de **work tracking** — issues tienen status, se mueven por workflows, se completan. Capabilities no son work items. Son entidades permanentes del catálogo de software con ownership, health metrics, y dependencias.

Atlassian tiene un producto diseñado exactamente para esto: **Compass** — software component catalog con scorecards, dependency mapping, DORA metrics, y ownership. La integración Compass ↔ Jira es nativa.

## Decisión

1. **Capabilities migran a Compass** como componentes del software catalog. Cada C1-C12 se convierte en un Compass component con owner, description, scorecards, y links a epics/stories de Jira.

2. **Initiatives se quedan en Jira** como issue type nativo, parent de Epics. Son work items con lifecycle (Backlog → In Progress → Done).

3. **El issue type Capability se retira de Jira** una vez migrado a Compass. Los 12 issues actuales (RAISE-795 a RAISE-815) se archivan con link al Compass component equivalente.

4. **Epics tienen UN parent** (Initiative) y un **link a Compass component** (la capability que tocan). Esto da dos vistas: "¿qué avanzamos en PRO Launch?" (Jira) y "¿qué health tiene el Adapter Layer?" (Compass).

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Cada producto hace lo que fue diseñado — Jira trackea trabajo, Compass cataloga software |
| ✅ Positivo | Capabilities ganan scorecards, dependency mapping, DORA metrics gratis |
| ✅ Positivo | Elimina la ambigüedad de "Capability como work item" — no tienen workflow, no se completan |
| ✅ Positivo | Compass ↔ Jira integration es nativa — los epics se ven desde ambos productos |
| ✅ Positivo | Alineado con best practices de Atlassian como partners |
| ⚠️ Negativo | Compass es un producto adicional (puede requerir licencia según plan) |
| ⚠️ Negativo | Migración requiere setup de Compass y re-linking |
| ⚠️ Negativo | Compass es P2 en el MVP timeline — la migración completa no ocurre de inmediato |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Mantener Capability como issue type en Jira | Capabilities no son work items. No tienen workflow natural. Fuerza un modelo incorrecto. |
| Usar labels `capability:*` en vez de Compass | Funcional pero pierde scorecards, dependency mapping, DORA, ownership — todo lo que Compass da gratis. |
| Usar Jira Components para capabilities | Components en Jira son demasiado simples (solo nombre + lead). No tienen health, dependencies, ni metrics. Compass es la evolución de Components. |

## Plan de Migración

| Fase | Acción | Timing |
|------|--------|--------|
| 1 | Documentar mapping C1-C12 → Compass component definitions | Ahora (RAISE-760) |
| 2 | Setup Compass para RAISE project | Post-MVP (RAISE-819) |
| 3 | Crear 12 Compass components con scorecards | Post-MVP |
| 4 | Vincular epics existentes a Compass components | Post-MVP |
| 5 | Archivar RAISE-795 a RAISE-815 (Capability issues) | Después de paso 4 |
| 6 | Considerar retirar Capability como issue type | Después de validar Compass |

**Fase 1 es parte de RAISE-760. Fases 2-6 son post-MVP.**

---

<details>
<summary><strong>Referencias</strong></summary>

- R1-RAISE-760: Compass es P2, GraphQL API via Forge toolkit, scorecards GA
- R3-RAISE-760: Module/architecture docs → Compass component catalog
- Atlassian Compass: https://www.atlassian.com/software/compass
- Current Capabilities: RAISE-795 (C1) through RAISE-815 (C12)

</details>
