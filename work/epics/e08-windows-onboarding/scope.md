---
id: E8
title: "Windows Team Onboarding Guide"
status: in-progress
branch: dev
priority: P1
estimated: S (3-4 stories)
bugs_addressed: [E4, E7]
---

# E8: Windows Team Onboarding Guide

## Objective

Documentar el proceso completo de onboarding de un equipo en Windows, incluyendo prerequisites, workarounds de bugs activos, y guías paso a paso — de forma que el equipo llegue a su primer `/rai-session-start` exitoso sin fricción.

## Context

Durante el onboarding de Fer (2026-03-25) se identificaron dos bugs activos en Windows:
- **E4 (cp1252):** Múltiples comandos `rai` crashean con `UnicodeEncodeError` en la salida. Reproducido en `rai graph build` → crash en `✓ Saved to...`. Workaround: `setx PYTHONUTF8 1`.
- **E7 (flat state migration):** Si session start crashea (por E4) después de migrar el flat file, el `next_session_prompt` se pierde en la siguiente sesión. Workaround: `PYTHONUTF8=1` previene el crash raíz.

Ambos bugs NO estarán resueltos antes del onboarding del equipo.

## Stories

| ID | Story | Tamaño | Descripción |
|----|-------|:------:|-------------|
| S8.1 | Prerequisitos Windows | XS | Documentar `setx PYTHONUTF8 1`, por qué es necesario, cómo verificarlo, cómo quitarlo | ✓ Done |
| S8.2 | Backlog con filesystem adapter | S | Verificar manifest, crear Epic y Stories con `rai backlog`, linkear con --parent, registrar el epic E8 y sus historias | ✓ Done |
| S8.3 | Entendiendo los Skill Sets | S | Qué son, estructura interna (overlay/replaces), entrada/salida, cómo crearlos, activarlos y verificarlos — con prueba práctica | ✓ Done |
| S8.4 | Bugs conocidos en Windows | XS | Catálogo de E4/E7 con síntomas, causa raíz simplificada, workaround, estado | ✓ Done |
| S8.5 | Workshop Skillset Simulation | S | Guía del instructor: setup externo, 3 tipos de personalización (overlay parcial, reescritura total, skill nuevo), deploy y verificación | ✓ Done |

## In Scope

- Documentación de prerequisites Windows (PYTHONUTF8=1)
- Guía para verificar manifest y usar `rai backlog` con filesystem adapter
- Guía de skill sets: qué son, estructura, creación, activación, prueba
- Catálogo de bugs conocidos con workarounds verificados
- Todo en español (el equipo es hispanohablante)

## Out of Scope

- Fix de los bugs (E4, E7) — eso es trabajo del CLI
- Guías para Linux/Mac
- Automatización del setup
- Documentación de features avanzados (epics, stories, graph queries)

## Done Criteria

- [ ] Todos los stories completos
- [ ] Un developer nuevo puede seguir la guía sin ayuda y llegar a /session-start exitoso
- [ ] Bugs E4 y E7 documentados con workarounds verificados
- [ ] Epic retrospective completada

## Dependencies

- E4 (cp1252 bug) — documentado, workaround verificado ✓
- E7 (flat state migration) — documentado, workaround indirecto via E4 fix ✓

---

*Created: 2026-03-25*
