# Epic RAISE-609: CuryGage RaiSE Onboarding — Scope

> **Status:** IN PROGRESS
> **Created:** 2026-03-20
> **Target:** Semana del 2026-03-24
> **Brief:** `brief.md`

## Objetivo

Habilitar a un equipo de CuryGage para correr una historia de usuario completa
(requerimiento → producción) usando RaiSE, con su propio stack (Jira, Confluence, Bitbucket)
y un skillset tuneado a sus convenciones, en 5 sesiones facilitadas.

**Valor desbloqueado:** CuryGage ve RaiSE como metodología end-to-end, no solo como herramienta de
coding. Jorge (stakeholder) puede evidenciar mejora en todo el proceso, desde cómo llega un
requerimiento hasta cómo se entrega.

## Stories

| ID | Historia | Tamaño | Estado | Descripción |
|----|----------|:------:|:------:|-------------|
| S609.1 | Session Plan | S | Pending | Plan de 5 sesiones: objetivos, agenda y outputs por sesión |
| S609.2 | Repo Bootstrap | S | Pending | `rai init --detect` + bootstrap de governance en su repo |
| S609.3 | Adapter Validation | S | Pending | Jira (ACLI) + Confluence funcionando en su entorno |
| S609.4 | Custom Skillset | M | Pending | Skillset CuryGage: skills genéricos tuneados a sus convenciones |
| S609.5 | Demo Story + Facilitation Guide | S | Pending | Historia demo real + guía de facilitación para Fer |

**Total:** 5 stories

## Dependencias

```
S609.1 (session plan — paralelo, es solo un doc)

S609.2 (repo bootstrap — fundación técnica)
    ↓
S609.3 (adapters)   S609.4 (skillset)   ← ambas dependen de S609.2
         ↓                ↓
              S609.5 (demo + guía)
```

**Externos:**
- Emilio entrega: ACLI backlog adapter (RAISE-594 ✓) + Confluence adapter (en progreso)
- CuryGage facilita: acceso a su repo + instancias de Jira/Confluence

## Scope

**In scope (MUST):**
- Plan de 5 sesiones con objetivos medibles por sesión
- `rai init --detect` funcionando en su repo
- Jira y Confluence conectados vía adapters
- Skillset base CuryGage en su repo
- Una historia corrida de punta a punta como demostración en sesión 5
- Guía de facilitación para que Fer pueda correr las sesiones solo

**In scope (SHOULD):**
- Awareness de Bitbucket como delivery pipeline (no integración profunda)
- Handoff doc para autonomía post-programa

**Out of scope:**
- Nuevas features en el CLI — usar 2.2.4 existente
- Onboarding de múltiples equipos — piloto primero, luego escalar
- Adaptadores más allá de Jira/Confluence — fuera del v1
- Integración CI/CD con Bitbucket — es el delivery pipeline de ellos, no RaiSE

## Done Criteria

**Epic completo:**
- [ ] Plan de sesiones revisado y aprobado por Emilio
- [ ] `rai init` corre sin errores en el repo de CuryGage
- [ ] `rai backlog search` retorna issues de su Jira
- [ ] `rai docs publish` sube a su Confluence
- [ ] Skillset CuryGage commiteado en su repo
- [ ] Sesión 5 completada: equipo corre historia autónomamente
- [ ] Retrospectiva del epic completada

## Riesgos

| Riesgo | L/I | Mitigación |
|--------|:---:|------------|
| Confluence adapter no listo a tiempo (Emilio lo está haciendo) | M/H | Sesión 3 puede hacer read-only; publicar a Confluence en sesión 4-5 |
| Acceso al entorno de CuryGage lento de conseguir | M/H | Hacer S609.2-3 en entorno staging/sandbox primero |
| Equipo CuryGage resiste el proceso ("muy ceremonioso") | L/H | Enfatizar: el proceso es lo que hace predecible la IA, no burocracia |

## Parking Lot

- Bitbucket adapter (integración con su pipeline) → RAISE-610 si hay demanda post-piloto
- Onboarding de segundo equipo → después de validar el piloto
- Ontology extractor para el método de CuryGage → fuera de scope, es iniciativa de Emilio
