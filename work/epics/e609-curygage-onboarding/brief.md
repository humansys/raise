---
epic_id: "RAISE-609"
title: "CuryGage RaiSE Integration — Jira, Confluence y custom skillset"
status: "active"
created: "2026-03-20"
---

# Epic Brief: CuryGage RaiSE Onboarding

## Contexto
CuryGage lleva ~1 mes usando RaiSE. Ya conocen el flujo, ya han desarrollado con los skills
genéricos. No necesitan intro a la metodología. Lo que falta es conectar sus herramientas
corporativas y darles un skillset propio que puedan mantener ellos mismos.

## Hypothesis
Para un equipo de CuryGage que ya usa RaiSE con skills genéricos,
integrar Jira y Confluence como adapters y entregarles un skillset scaffold propio
les permite trabajar con sus herramientas reales en lugar de workarounds,
y evolucionar sus skills sin depender de HumanSys.

## Success Metrics
- **Leading:** `rai backlog search` retorna issues de su Jira; `rai docs publish` sube a su Confluence
- **Lagging:** Equipo ajusta y hace commit de un skill propio sin ayuda de Fer en los 7 días siguientes

## Appetite
S — prep + 2-3 sesiones de trabajo conjunto. El equipo ya sabe usar RaiSE.

## Scope Boundaries
### In (MUST)
- Jira adapter validado en su entorno (ACLI-based, ya disponible en 2.2.4)
- Confluence adapter validado en su entorno (Emilio lo está terminando)
- Custom skillset scaffold: fork del skillset base, listo para que ellos lo ajusten
- Guía de cómo agregar/modificar skills en su propio repo

### In (SHOULD)
- Una sesión de trabajo conjunto para validar que los adapters funcionen en su env
- Una historia corrida con sus adapters + su skillset para confirmar integración end-to-end

### No-Gos
- Introducir RaiSE desde cero — ya lo saben, no repetir
- Nuevas features en el CLI — usar 2.2.4 existente
- Adapters más allá de Jira/Confluence en esta fase

### Rabbit Holes
- Customizar demasiado el skillset antes de que ellos mismos identifiquen sus necesidades
- Esperar a que el Confluence adapter esté perfecto — se puede arrancar con Jira solo
