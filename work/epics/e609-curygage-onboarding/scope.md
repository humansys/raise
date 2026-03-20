# Epic RAISE-609: CuryGage RaiSE Integration — Scope

> **Status:** IN PROGRESS
> **Created:** 2026-03-20
> **Target:** Semana del 2026-03-24 (5 sesiones, ~½ día cada una)
> **Brief:** `brief.md`

## Objetivo

Conectar el entorno de trabajo de CuryGage (Jira + Confluence) a RaiSE vía adapters,
y entregarles un skillset scaffold propio que sean capaces de ajustar y evolucionar
sin depender de HumanSys.

**Contexto clave:** CuryGage ya lleva ~1 mes con RaiSE. Conocen el flujo y los skills genéricos.
No necesitan intro a la metodología. Lo que falta es sus herramientas reales integradas
y skills que reflejen sus propias convenciones.

**Valor desbloqueado:** El equipo trabaja con Jira y Confluence desde dentro del flujo de RaiSE,
y puede agregar o modificar sus propios skills de forma autónoma.

## Plan de Sesiones

5 sesiones de ~½ día. El tiempo extra es intencional — las integraciones siempre
tardan más de lo esperado, y la sesión 5 es deliberadamente para que *ellos* tomen el control.

| Sesión | Objetivo | Output concreto |
|--------|----------|-----------------|
| **S1** — Jira | `rai init` en su repo + Jira adapter validado en Windows | `rai backlog search` retorna sus issues |
| **S2** — Confluence | Confluence adapter + flujo de documentación | `rai docs publish` sube a su Confluence |
| **S3** — Skillset I | Skillset scaffold: presentación + primer override guiado | Skill customizado commiteado con ayuda de Fer |
| **S4** — Skillset II | El equipo ajusta skills adicionales autónomamente | 2+ skills propios, sin instrucciones de Fer |
| **S5** — Historia completa | Historia real de su backlog, end-to-end | Historia cerrada con sus adapters + skills |

**Lógica del orden:**
- S1-S2: Integrar herramientas primero — sin Jira y Confluence conectados, el skillset no tiene contexto real
- S3-S4: Dos sesiones completas de skillset — la primera guiada, la segunda autónoma. Así el aprendizaje queda
- S5: Historia real como prueba. Si algo de S1-S4 quedó pendiente, esta sesión lo absorbe

**Prep para el lunes (antes de S1):**
- Instalar y configurar raise-cli 2.2.4 en Windows en el entorno de CuryGage
- Configurar ACLI apuntando a su instancia de Jira
- Tener `.raise/jira.yaml` o variables de entorno listas para validar en sesión

## Stories

| ID | Historia | Tamaño | Estado | Descripción |
|----|----------|:------:|:------:|-------------|
| S609.1 | Jira Adapter | S | Pending | ACLI adapter configurado y validado en su entorno (cubre S1-S2) |
| S609.2 | Confluence Adapter | S | Pending | Adapter de docs validado (cubre S3) |
| S609.3 | Skillset Scaffold | M | Pending | Fork del skillset base + guía de cómo modificarlo (cubre S4) |
| S609.4 | Integration Run | S | Pending | Historia real end-to-end con sus adapters + skillset (cubre S5) |

**Total:** 4 stories

## Dependencias

```
S609.1 (Jira)
    ↓
S609.2 (Confluence)  ← puede ir en paralelo con S609.1 si hay acceso
    ↓
S609.3 (Skillset)   ← puede avanzar antes de que S609.2 esté listo
    ↓
S609.4 (Integration run)  ← requiere S609.1 + S609.2 + S609.3
```

**Externos:**
- Emilio: Confluence adapter (en progreso) — si no está para S3, S3 se mueve, no se cancela
- CuryGage: acceso admin a Jira + Confluence + su repo

## Scope

**In scope (MUST):**
- `rai backlog` operativo con su Jira: search, get, transition, comment
- `rai docs publish` operativo con su Confluence
- Skillset scaffold en su repo con al menos 2 overrides (story-start, story-close)
- Guía corta: cómo agregar/modificar un skill en su propio repo
- Historia end-to-end como prueba de integración

**In scope (SHOULD):**
- El equipo hace un ajuste de skill autónomamente en sesión 4 (sin instrucciones de Fer)
- Documentación de la configuración de adapters para que puedan replicarlo

**Out of scope:**
- Intro a RaiSE — ya la saben
- Nuevas features en el CLI — usar 2.2.4
- Bitbucket adapter — post-piloto si hay demanda
- Onboarding de otros equipos de CuryGage — este es el piloto

## Done Criteria

- [ ] `rai backlog search` retorna issues del Jira de CuryGage
- [ ] `rai backlog transition` actualiza un issue en su Jira
- [ ] `rai docs publish` sube documento a su Confluence
- [ ] Skillset scaffold commiteado en su repo
- [ ] El equipo modifica un skill sin ayuda de Fer (sesión 4)
- [ ] Historia end-to-end completada con sus adapters + sus skills (sesión 5)
- [ ] Retrospectiva del epic completada

## Riesgos

| Riesgo | L/I | Mitigación |
|--------|:---:|------------|
| Confluence adapter no listo para S3 | M/H | Mover S3 al final de la semana; arrancar con Jira primero |
| Acceso al entorno de CuryGage tarda | M/M | Preparar scaffold sin acceso; adapters se validan cuando llegue el acceso |
| El equipo quiere customizar todo en S4 | L/M | Scope mínimo: 2 overrides. El resto lo agregan ellos después |

## Parking Lot

- Bitbucket adapter → RAISE-610 si hay demanda post-piloto
- Onboarding de segundo equipo → después de cerrar este
- Guía de facilitación completa → no necesaria; el equipo ya sabe RaiSE

---

## Implementation Plan

> Agregado por `/rai-epic-plan` — 2026-03-20

### Story Sequence

| Orden | Story | Tamaño | Dependencias | Milestone | Rationale |
|:-----:|-------|:------:|--------------|-----------|-----------|
| 1 | S609.1 Jira Adapter | S | Ninguna (RAISE-594 ✓) | M1 | Risk-first + Windows: si hay problemas de instalación/permisos en su entorno, queremos saberlo el lunes |
| 2 | S609.2 Confluence Adapter | S | Emilio (externo) | M1 | Va en S2 — integraciones juntas antes del skillset. Si Emilio no entrega, S2 se swapea con S609.3 |
| 3 | S609.3 Skillset Scaffold | M | Ninguna (se construye local) | M2 | S3-S4 dedicadas al skillset. Dos sesiones permiten guiada + autónoma |
| 4 | S609.4 Integration Run | S | S609.1 + S609.2 + S609.3 | M3 | Requiere todo. Sesión 5, prueba de autonomía real |

### Milestones

| Milestone | Stories | Target | Criterio de éxito |
|-----------|---------|--------|-------------------|
| **M1: Tools Connected** | S609.1 + S609.2 | 2026-03-25 (mar) | `rai backlog` y `rai docs` operativos en su entorno Windows |
| **M2: Skillset Ready** | +S609.3 | 2026-03-27 (jue) | Skillset scaffold en su repo + equipo modificó un skill autónomamente en S4 |
| **M3: Autonomy Proven** | +S609.4 | 2026-03-28 (vie) | Historia real cerrada end-to-end sin intervención de Fer |

### Streams de trabajo

```
Semana del 2026-03-24

Lun 03-24      Mar 03-25       Mié 03-26   Jue 03-27      Vie 03-28
──────────────────────────────────────────────────────────────────────
S609.1 (Jira) ──► S609.2 (Confluence) ──► M1
                                           ↓
                               S609.3 (Skillset I+II) ──────► M2
                                                               ↓
                                                          S609.4 ──► M3
                                                          (Historia)

Si S609.2 se retrasa (Emilio): swap S2↔S3 — skillset adelanta, Confluence va al final
```

**Punto de merge crítico:** antes de S609.4 (viernes), verificar que S609.1 + S609.2 + S609.3
están todos verdes. Si S609.2 no llegó, S609.4 se hace sin Confluence y se agenda una sesión
adicional cuando el adapter esté listo.

### Progress Tracking

| Story | Tamaño | Estado | Sesiones | Actual | Notas |
|-------|:------:|:------:|----------|:------:|-------|
| S609.1 Jira Adapter | S | Pending | S1 + S2 | — | |
| S609.2 Confluence Adapter | S | Pending | S3 | — | Depende de Emilio |
| S609.3 Skillset Scaffold | M | Pending | S4 | — | |
| S609.4 Integration Run | S | Pending | S5 | — | Requiere M2 completo |

### Sequencing Risks

| Riesgo | L/I | Mitigación |
|--------|:---:|------------|
| Confluence adapter no llega para S3 (lunes-martes) | M/H | S609.3 avanza igual; S609.2 se hace al final de la semana o semana siguiente |
| Problemas de acceso/permisos en el Jira de CuryGage en S1 | M/M | Tener sandbox environment listo como fallback para validar el flujo técnico |
| S609.3 tarda más (equipo indeciso sobre qué customizar) | L/M | Scope mínimo definido: 2 overrides (story-start, story-close). El resto es post-epic |
