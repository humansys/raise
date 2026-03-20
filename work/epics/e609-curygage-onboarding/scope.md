# Epic RAISE-609: CuryGage RaiSE Integration — Scope

> **Status:** IN PROGRESS
> **Created:** 2026-03-20
> **Target:** Semana del 2026-03-24
> **Brief:** `brief.md`

## Objetivo

Conectar el entorno de trabajo de CuryGage (Jira + Confluence) a RaiSE vía adapters,
y entregarles un skillset scaffold propio que puedan evolucionar de forma autónoma.

**Contexto clave:** CuryGage ya lleva ~1 mes con RaiSE. Saben el flujo. No necesitan intro.
Lo que necesitan es dejar de usar workarounds para Jira/Confluence y tener skills que
reflejen sus propias convenciones.

**Valor desbloqueado:** El equipo trabaja con sus herramientas reales desde `rai backlog` y
`rai docs`, y puede agregar o modificar sus propios skills sin depender de HumanSys.

## Stories

| ID | Historia | Tamaño | Estado | Descripción |
|----|----------|:------:|:------:|-------------|
| S609.1 | Adapter Setup | S | Pending | Jira (ACLI) + Confluence validados en su entorno |
| S609.2 | Skillset Scaffold | M | Pending | Fork del skillset base con estructura para que ellos customicen |
| S609.3 | Integration Validation | S | Pending | Historia corrida end-to-end con sus adapters + su skillset |

**Total:** 3 stories

## Dependencias

```
S609.1 (adapters — fundación técnica)
    ↓
S609.2 (skillset — puede avanzar en paralelo)
    ↓
S609.3 (validación — requiere S609.1 + S609.2)
```

**Externos:**
- Emilio: Confluence adapter (en progreso, RAISE-594 ya tiene ACLI/Jira ✓)
- CuryGage: acceso a su Jira, Confluence, y al menos un repo donde hacer el init

## Scope

**In scope (MUST):**
- `rai backlog search/get/transition` funcionando con su Jira
- `rai docs publish` funcionando con su Confluence
- Skillset scaffold en su repo: estructura de directorios + 2-3 skills base overrideados
- Guía corta: cómo agregar/modificar un skill en su repo

**In scope (SHOULD):**
- Sesión de trabajo conjunto para validar adapters en vivo
- Historia end-to-end con sus herramientas como prueba de integración

**Out of scope:**
- Introducción a RaiSE — ya la saben
- Nuevas features en el CLI — usar 2.2.4
- Adapters adicionales (Bitbucket, Slack, etc.) — post-piloto si hay demanda

## Done Criteria

- [ ] `rai backlog search` retorna issues del Jira de CuryGage
- [ ] `rai docs publish` sube documento al Confluence de CuryGage
- [ ] Skillset scaffold commiteado en su repo con al menos un skill customizado
- [ ] Guía de "cómo modificar un skill" entregada
- [ ] Una historia corrida end-to-end con sus adapters + skillset (S609.3)
- [ ] Retrospectiva del epic completada

## Riesgos

| Riesgo | L/I | Mitigación |
|--------|:---:|------------|
| Confluence adapter no listo para la fecha | M/H | Arrancar con Jira solo; Confluence se agrega cuando esté |
| Acceso al entorno de CuryGage tarda en gestionarse | M/M | Preparar skillset scaffold sin acceso; adapters se validan cuando llegue el acceso |
| Equipo quiere customizar todo de golpe | L/M | Dar el scaffold mínimo; dejar que sus propias necesidades guíen la evolución |

## Parking Lot

- Bitbucket adapter → RAISE-610 si hay demanda post-piloto
- Onboarding de segundo equipo de CuryGage → después de validar este
- Guía de facilitación para sesiones → no necesaria si el equipo ya sabe RaiSE
