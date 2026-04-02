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
| **Tooling (release/2.4.0)** | | | | | |
| S1132.0a | RAISE-1170 | TS import/export extraction (tree-sitter) | S | Pending | Extender scanner.py con TypeScriptAnalyzer para imports/exports |
| S1132.0b | RAISE-1171 | Module-level dependency aggregation | S | Pending | Agrupar dependencias archivo→archivo en módulo→módulo |
| S1132.0c | RAISE-1172 | Signal scanner | S | Pending | TODOs, HACKs, feature flags, dead code markers |
| S1132.0d | RAISE-1173 | Entry point detection | XS | Pending | Detectar entry points desde package.json, pyproject.toml |
| **Analysis (release/3.0.0)** | | | | | |
| S1132.1 | RAISE-1163 | Reconnaissance — Architecture Map | L | In Progress | Barrido completo de 35 módulos usando tooling mejorado |
| S1132.2 | RAISE-1164 | Wave 1 — Extension Points | M | Pending | Deep dive: skills/, hooks/, tools/, commands/, Tool.ts, commands.ts |
| S1132.3 | RAISE-1165 | Wave 2 — Agent Infrastructure | M | Pending | Deep dive: coordinator/, tasks/, QueryEngine.ts, query.ts, context/ |
| S1132.4 | RAISE-1166 | Wave 3 — Integration Layer | M | Pending | Deep dive: services/mcp/, bridge/, plugins/, services/ |
| S1132.5 | RAISE-1167 | Wave 4 — State & Persistence | S | Pending | Deep dive: memdir/, state/, services/compact/, migrations/ |
| S1132.6 | RAISE-1168 | Wave 5 — UI & Rendering | S | Pending | Deep dive: components/, ink/, screens/, outputStyles/ |
| S1132.7 | RAISE-1169 | Synthesis & Roadmap | M | Pending | Consolidar hallazgos → backlog priorizado, playbook rai-discover |

**Total:** 11 stories (4 tooling + 7 analysis)

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
S1132.0a (TS imports) ──┐
S1132.0c (signals)      │ tooling — release/2.4.0, paralelas excepto 0b
S1132.0d (entry points) │
  ↓                     │
S1132.0b (module aggregation) ← depende de 0a
  ↓
S1132.1 (reconnaissance — consume tooling, prerequisito de waves)
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

Tooling stories (0a-0d) branch from release/2.4.0 (código productivo).
Analysis stories (1-7) branch from release/3.0.0 (documentación).
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
