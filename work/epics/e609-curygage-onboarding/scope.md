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
| **S1** — Repo + Jira | `rai init` en su repo + Jira adapter validado | `rai backlog search` retorna sus issues |
| **S2** — Jira profundo | Flujo backlog completo: get, transition, comment | El equipo corre un ciclo de backlog sin ayuda |
| **S3** — Confluence | Confluence adapter + flujo de documentación | `rai docs publish` sube a su Confluence |
| **S4** — Skillset | Skillset scaffold: revisión conjunta + primer override | Skill customizado commiteado por ellos |
| **S5** — Historia completa | Historia real de su backlog, end-to-end | Historia cerrada con sus adapters + skills |

**Por qué 5 y no 3:**
- S1-S2: Jira tiene más superficie que "funciona/no funciona" — necesita un día completo
- S3: Confluence puede estar en progreso cuando empieza el epic; sesión dedicada da margen
- S4: El skillset lo hacen *ellos*, no Fer — eso tarda más de lo que parece
- S5: Buffer real + prueba de autonomía. Si S1-S4 salen perfecto, S5 es la historia limpia.
  Si algo quedó pendiente, S5 lo absorbe.

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
