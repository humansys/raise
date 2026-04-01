# Epic E1132: Claude Code Architecture Reconstruction — Scope

> **Status:** IN PROGRESS
> **Release:** 3.0.0
> **Created:** 2026-04-01
> **Jira:** RAISE-1162

## Objective

Reconstruir la arquitectura de Claude Code desde su source code filtrado para extraer conocimiento que informe el diseño de RaiSE, identificar líneas de mejora priorizadas para el roadmap, y formalizar el método de Architecture Reconstruction como práctica reproducible.

**Value:** RaiSE es un harness sobre Claude Code. Entender la arquitectura interna — extension points, contratos implícitos, limitaciones y patrones — es nuestra ventaja competitiva. Cada asunción validada o corregida evita bugs futuros y decisiones mal informadas. Secundariamente, este epic es el caso de uso real que valida y refina rai-discover para repos externos.

## Stories

| ID | Jira | Story | Size | Status | Description |
|----|------|-------|:----:|:------:|-------------|
| S1132.1 | RAISE-1163 | Reconnaissance — Architecture Map | L | In Progress | Barrido completo de 35 módulos: catálogo, dependency graph, entry points, patrones dominantes |
| S1132.2 | RAISE-1164 | Wave 1 — Extension Points | M | Pending | Deep dive: skills/, hooks/, tools/, commands/, Tool.ts, commands.ts. Cómo se extiende CC |
| S1132.3 | RAISE-1165 | Wave 2 — Agent Infrastructure | M | Pending | Deep dive: coordinator/, tasks/, QueryEngine.ts, query.ts, context/. Orquestación de agentes |
| S1132.4 | RAISE-1166 | Wave 3 — Integration Layer | M | Pending | Deep dive: services/mcp/, bridge/, plugins/, services/. Conexión con el mundo exterior |
| S1132.5 | RAISE-1167 | Wave 4 — State & Persistence | S | Pending | Deep dive: memdir/, state/, services/compact/, migrations/. Persistencia y compactación |
| S1132.6 | RAISE-1168 | Wave 5 — UI & Rendering | S | Pending | Deep dive: components/, ink/, screens/, outputStyles/. Sistema de UI Ink/React |
| S1132.7 | RAISE-1169 | Synthesis & Roadmap | M | Pending | Consolidar hallazgos → backlog priorizado, playbook rai-discover, publicar en Confluence |

**Total:** 7 stories

## Scope

**In scope (MUST):**
- Reconnaissance completa de los 35 módulos top-level + archivos raíz
- Mapa arquitectónico con dependencias entre módulos
- Deep dives en waves priorizadas por valor para RaiSE
- Catálogo de hallazgos con implicaciones accionables
- Backlog items creados en Jira para mejoras identificadas

**In scope (SHOULD):**
- Playbook documentado para futura integración en rai-discover
- Publicación en Confluence de hallazgos clave
- Patrones descubiertos candidatos para adopción en RaiSE

**Out of scope:**
- Fork o derivados del código de Claude Code → nunca, no somos competidores
- Reimplementación de componentes internos de CC → extraemos conocimiento, no código
- Análisis de seguridad ofensivo → no buscamos vulnerabilidades
- buddy/ (easter egg), vim/, voice/ → periféricos, valor marginal → diferir

## Done Criteria

**Per story:**
- [ ] Hallazgos documentados en `work/epics/e1132-claude-code-reconstruction/`
- [ ] Cada hallazgo conectado a implicación para RaiSE
- [ ] Review por Emilio antes de cerrar

**Epic complete:**
- [ ] Todas las stories completas (S1132.1–S1132.7)
- [ ] Mapa arquitectónico completo y revisado
- [ ] Backlog items creados en Jira para mejoras identificadas
- [ ] ADR-016 refinado con lecciones del proceso
- [ ] Playbook de reconstruction documentado
- [ ] Epic retrospective done
- [ ] Publicado en Confluence

## Dependencies

```
ADR-016 (accepted — guía de proceso)
  ↓
S1132.1 (reconnaissance — prerequisito de todas las waves)
  ↓
S1132.2 (extension points — prioridad 1)
  ↓
S1132.3 (agent infrastructure — prioridad 2)
  ↓
S1132.4 (integration layer — prioridad 3)
  ↓
S1132.5 (state & persistence — prioridad 4)
  ↓
S1132.6 (UI & rendering — prioridad 5)
  ↓
S1132.7 (synthesis — necesita al menos waves 1-4)
```

Waves son secuenciales por prioridad de valor pero técnicamente independientes.

**External:** Source code en ~/Code/claude-code-leak-main/ (snapshot, no se actualiza)

## Architecture

| Decision | ADR | Summary |
|----------|-----|---------|
| Architecture Reconstruction como práctica | ADR-016 | Método en 4 fases: reconnaissance → hypothesis → deep dives → synthesis |

## Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| Scope creep — 512K LOC invita a rabbit holes | H/M | Waves priorizadas, hallazgos siempre conectados a "¿qué significa para RaiSE?" |
| Staleness — código leaked es snapshot, CC evoluciona | L/M | Documentar versión, enfocarse en patrones arquitectónicos (estables) vs detalles (volátiles) |
| Takedown request — Anthropic puede pedir eliminación | M/L | Artifacts son propios (mapas, hallazgos). No copiamos código, extraemos conocimiento |

## Parking Lot

- Integración de hallazgos en rai-discover como feature → post-epic, depende de playbook
- Análisis comparativo con otros CLI AI (Cursor, Windsurf, Aider) → epic separado si hay valor
- buddy/ (companion sprite) → curiosidad, no valor de negocio
