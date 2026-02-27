# Problem Brief: AI Agentic Governance

**Date:** 2026-02-26
**Session:** SES-294
**Stakeholder:** Emilio (CEO/Product), validado con contexto Kurigage
**Status:** Ready for `/rai-epic-design`

---

## 1. APUESTA — Dominio

**Calidad + Visibilidad/Control.** El AI slop (código generado por AI sin governance)
frena la adopción de agentes AI en organizaciones. El dolor principal es calidad —
el output de AI agents no es confiable y no hay mecanismo para hacerlo confiable.

## 2. PARA QUIÉN — Stakeholder Primario

**Liderazgo técnico** (arquitectos, CTOs, tech leads). Son quienes ven el output
agregado de los equipos y no tienen forma de garantizar que el código generado
por AI cumple con los estándares de la organización.

## 3. ESTADO ACTUAL — El Gap

> **La organización no puede garantizar que desarrolla código de calidad con AI
> porque no sabe cómo hacerlo y desconfía.**

Contexto observado:
- Hicieron pruebas con Copilot, se decepcionaron (autocomplete ≠ governance)
- No tienen tiempo de investigar y construir sus propios harneses
- Están produciendo/gestionando para cumplir demanda de negocio
- La presión es "con AI deberían ir 10x más rápido"

## 4. RAÍZ — 3 Whys

| Why | Respuesta |
|-----|-----------|
| ¿Por qué no saben garantizar calidad con AI? | Hicieron pruebas con Copilot, se decepcionaron. No tienen tiempo de investigar y construir harneses integrados a su proceso. |
| ¿Por qué no tienen tiempo? | Están produciendo o gestionando para estar al día con demanda de negocio, que espera que con AI vayan 10x más rápido. |
| ¿Por qué la presión de 10x no se traduce en inversión? | En Latam nunca se ha invertido en equipos de desarrollo. La capacitación es prohibitiva y no hay oferta adaptada. |

**Raíz identificada:** El liderazgo técnico en Latam enfrenta presión de ir 10x
más rápido con AI, pero no puede invertir en construir la infraestructura de
governance necesaria porque: (1) capacitación es prohibitiva, (2) no hay oferta
de soluciones adaptadas, y (3) históricamente no se invierte en enablement de
equipos de desarrollo. El resultado es adopción superficial, decepción, y
desconfianza.

## 5. EARLY SIGNAL — 4 semanas

**Comportamiento que cambia:**

Los tech leads vuelven a programar código (probablemente habían dejado de hacerlo
por estar gestionando). Resuelven su problema de documentación porque Rai documenta
directo a Jira/Odoo. Se sienten con el ancho de banda para atacar cosas que antes
no podían.

**Observable en 4 semanas:** Tech leads produciendo código y documentación con
AI agents activamente.

## 6. HIPÓTESIS (SAFe)

> **Si** el liderazgo técnico no puede garantizar calidad de código con AI porque
> no tiene infraestructura de governance, capacitación es prohibitiva y no hay
> oferta adaptada,
>
> **entonces** al proveer governance guardrails embebidos en el workflow de AI agents
> (guardrails declarativos + poka-yoke + compliance visible),
>
> **los tech leads** volverán a programar activamente, resolverán su deuda de
> documentación vía integración directa (Jira/Odoo), y tendrán ancho de banda
> para atacar trabajo que antes era imposible,
>
> **medido por:** tech leads produciendo código y documentación con AI agents en
> las primeras 4 semanas de adopción.

---

## Contexto Adicional: Research Base

Este problem brief está respaldado por 4 research docs completos (SES-294):

| Research | Key Finding | Confluence |
|----------|-------------|-----------|
| [L1: Cross-Repo Visibility](../research/cross-repo-visibility/) | Schema soporta cross-repo edges, gap es en population y traversal | [Page](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3084648458) |
| [L2: Pattern Propagation](../research/pattern-propagation/) | Scope hierarchy + Wilson score aggregation + SECI model | [Page](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3082715148) |
| [L3: Governance Intelligence](../research/governance-intelligence-multi-repo/) | Poka-yoke en skills, MUST/SHOULD/CAN, waivers, compliance | [Page](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3084451849) |
| [L4: Organizational Learning](../research/organizational-learning/) | Health scorecards, Goodhart safeguards, experiment tracking | [Page](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3084779523) |

## Contexto Adicional: Mercado y Posicionamiento

**Categoría propuesta:** AI Agentic Governance

| Competidor | Qué hace | Limitación |
|-----------|----------|-----------|
| GitHub Copilot | Productivity (escribe código más rápido) | Sin governance |
| Cursor/Windsurf | Context (entiende tu repo) | Sin governance multi-repo |
| Devin/Codex | Autonomy (ejecuta tareas solo) | Sin governance organizacional |
| SonarQube | Code quality (detecta después) | Speed camera, no lane assist |
| OPA/Rego | Policy as code (infra) | No developer workflow |
| Backstage | Service catalog (observa) | No previene, solo reporta |

**RaiSE:** Governance guardrails. No hace al agente más capaz — lo hace **confiable**.

> Speed camera (SonarQube) catches you after the violation.
> Lane assist (RaiSE) keeps you in the lane while you drive.

## Contexto Adicional: Cliente Piloto (Kurigage)

| Rol | Persona | Necesita |
|-----|---------|----------|
| Arquitecto | Rodo | Declarar guardrails, ver compliance cross-repo |
| Tech Lead | Adan | Governance durante workflow (contabilidad, PHP) |
| Tech Lead | Arnulfo | Governance durante workflow (ERP, PHP) |
| Tech Lead | Sofi | Cross-repo awareness (APIs, .NET) |
| Business Owner | Jorge | "¿Estamos haciendo las cosas bien?" → 🟢🟡🔴 |

## Propuesta de Scope para Epic(s)

### 🎯 MVP Launch: March 15, 2026 — Atlassian Webinar

**Audiencia:** Clientes Jira. La demo debe mostrar Jira + Confluence + Governance
funcionando juntos. 3 semanas de runway.

El MVP agrupa 3 workstreams + lo que ya existe:

### Epic 1: Platform Integration (E-JIRA, 🚀 YA EN PROGRESO)
- Jira backlog integration (`rai backlog` — create, read, update, transition)
- Confluence docs publishing (`rai docs publish`)
- Jira → knowledge graph parser
- **Status:** Ya se está implementando

### Epic 2: Skill Ecosystem (E-SKILLS, 🚀 YA EN PROGRESO)
- Skill builder tooling
- Jira connector skill
- Confluence connector skill
- **Status:** Ya se está implementando

### Epic 3: Governance Foundation (E-GOV-FOUNDATION, 📋 por diseñar)
- L1 parcial: cross-repo edges + impact query
- L3 Phase 1: guardrail nodes + enforcement levels + scope hierarchy + scope resolution query
- Deliverable: "Rodo declara guardrails, el grafo los almacena, query devuelve guardrails aplicables"

### Ya completado:
- E275: Shared Memory Backend ✅ (graph sync, patterns, telemetry, query)

### Demo scenario:
1. Rodo define guardrails → sync al server
2. Tech lead crea story en Jira → RaiSE sincroniza
3. Agent diseña story → muestra guardrails aplicables + blast radius cross-repo
4. Compliance check pasa → docs publicados a Confluence automáticamente
5. Rodo ve compliance report

### Post-MVP (Q2):
- **P1.1: Governance Guardrails** — Poka-yoke en 3 skills + waivers + compliance report
- **P1.2: Portfolio Health** — Health score composite + 🟢🟡🔴

### Fast-follow (Q3+):
- P2.0: Pattern Propagation (scope hierarchy, promotion, cross-repo reinforcement)
- P2.1: Organizational Intelligence (experiments, DORA, recommendations)
- P2.2: Forge Integration (Rovo agents)

---

**Next:** `/rai-epic-design` for Epic 3 (Governance Foundation) — Epics 1 y 2 ya están en progreso
