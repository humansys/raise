# RaiSE Roadmap
## Plan de Desarrollo

**Versión:** 2.0.0  
**Última Actualización:** 28 de Diciembre, 2025  
**Propósito:** Roadmap de desarrollo del proyecto RaiSE.

> **Nota de versión 2.0:** Roadmap actualizado con raise-mcp como componente CORE (promovido de v0.3 a v0.2), Observable Workflow, y terminologí­a v2.0.

---

## Visión de Releases

### v0.1.0 - Foundation (Target: Q1 2025)
**Tema:** "Foundation"

- [ ] CLI básico (init, check, hydrate)
- [ ] Soporte 5 agentes principales (Cursor, Copilot, Claude, GPT, Gemini)
- [ ] Templates core (PRD, spec, design, story)
- [ ] Katas base (L0, L1)
- [ ] Documentación inicial
- [ ] Corpus base completo

**Release Criteria:**
- CLI instalable via pip
- Proyecto inicializable con `raise init`
- Guardrails sincronizables con `raise hydrate`
- Docs publicados en GitHub Pages

---

### v0.2.0 - MCP-Native & Validation Gates (Target: Q2 2025) [ACTUALIZADO v2.0]
**Tema:** "MCP-Native Quality"

> **Cambio significativo:** raise-mcp promovido de v0.3 a v0.2. MCP es ahora componente CORE.

- [ ] **raise-mcp server (CORE)** [PROMOVIDO]
- [ ] Validation Gates completos (8 gates estándar)
- [ ] Guardrails system (renombrado de rules)
- [ ] `raise gate` command
- [ ] `raise guardrail` command
- [ ] Katas de validación (L2, L3)
- [ ] raise-config centralizado (template repo)

**MCP Primitivos Implementados:**
| Primitivo | Implementación | Status |
|-----------|----------------|--------|
| Resources | Constitution, Guardrails, Specs | ðŸ”„ En desarrollo |
| Tools | validate_gate, check_guardrail, escalate | ðŸ”„ En desarrollo |
| Prompts | Katas como templates | ðŸ“‹ Planificado |
| Sampling | Delegación razonamiento | ðŸ“‹ Planificado |

**Release Criteria:**
- MCP server funcional con Claude, Cursor, Windsurf
- 8 Validation Gates implementados y validables
- `raise mcp start` inicia servidor
- `raise gate check` valida gates
- Guardrails migrables desde rules legacy

---

### v0.3.0 - Observable Workflow (Target: Q3 2025) [NUEVO v2.0]
**Tema:** "Observability & HITL"

- [ ] Observable Workflow completo
- [ ] `raise audit` command
- [ ] JSONL trace storage
- [ ] Escalation Gates (HITL)
- [ ] Mí©tricas derivadas (re-prompting rate, escalation rate)
- [ ] Export OpenTelemetry (opcional)
- [ ] EU AI Act compliance documentation

**Observable Workflow Components:**
| Component | Status |
|-----------|--------|
| Trace logging automático | ðŸ”„ En desarrollo |
| Audit reports (CLI) | ðŸ“‹ Planificado |
| Metrics aggregation | ðŸ“‹ Planificado |
| CSV/JSON export | ðŸ“‹ Planificado |

**Release Criteria:**
- Cada acción MCP genera trace
- `raise audit` produce reportes íºtiles
- Escalation rate calculable
- Documentación EU AI Act disponible

---

### v0.4.0 - Enterprise Preview (Target: Q4 2025)
**Tema:** "Scale"

- [ ] Multi-agent context support avanzado
- [ ] SSO integration (planning)
- [ ] On-premise deployment guide
- [ ] Team analytics dashboard (local)
- [ ] Guardrail marketplace preparation

**Release Criteria:**
- Guí­a enterprise publicada
- Demo con 3+ agentes simultáneos

---

### v1.0.0 - Production (Target: Q1 2026)
**Tema:** "Stability"

- [ ] API estable (semver commitment)
- [ ] SOC2 Type I preparation
- [ ] Integraciones Jira/Linear
- [ ] Marketplace de katas community
- [ ] Enterprise tier launch

**Release Criteria:**
- Breaking changes require major version
- Enterprise customers piloting
- Full MCP 1.0 compliance

---

## Milestones Actuales

| Milestone | Status | Target | Progress |
|-----------|--------|--------|----------|
| Corpus v2.0 completo | âœ… En Progreso | 2025-12-28 | 90% |
| Ontologí­a v2.0 validada | âœ… En Progreso | 2025-12-28 | 85% |
| Fork spec-kit evaluación | âœ… Done | 2025-12-26 | 100% |
| Investigación Agentic AI | âœ… Done | 2025-12-27 | 100% |
| ADRs v2.0 actualizados | âœ… En Progreso | 2025-12-28 | 80% |
| CLI v0.1 alpha | ðŸ“‹ Pending | 2025-01-31 | 0% |
| Docs site live | ðŸ“‹ Pending | 2025-02-15 | 0% |

---

## Backlog Priorizado

### P0 (Must Have)

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| Finalizar corpus v2.0 | Emilio | 2025-12-28 | En progreso |
| CLI scaffold (click) | TBD | 2025-01-15 | Pending |
| `raise init` command | TBD | 2025-01-20 | Pending |
| `raise hydrate` command | TBD | 2025-01-25 | Pending |
| `raise check` command | TBD | 2025-01-31 | Pending |
| **`raise mcp` command** | TBD | 2025-02-15 | Pending |
| **`raise gate` command** | TBD | 2025-02-20 | Pending |

### P1 (Should Have)

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| Templates packaging | TBD | 2025-02-15 | Pending |
| Katas L1 completas | TBD | 2025-02-28 | Pending |
| Docusaurus site | TBD | 2025-02-15 | Pending |
| GitHub Actions workflow | TBD | 2025-02-20 | Pending |
| **`raise guardrail` command** | TBD | 2025-02-25 | Pending |
| **`raise audit` command** | TBD | 2025-03-15 | Pending |

### P2 (Nice to Have)

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| VS Code extension | TBD | 2025-Q2 | Pending |
| Analytics dashboard | TBD | 2025-Q2 | Pending |
| OpenTelemetry export | TBD | 2025-Q3 | Pending |

---

## Dependencias de Ontologí­a v2.0

| Cambio | Impacto en Roadmap | Status |
|--------|-------------------|--------|
| Rule â†’ Guardrail | CLI commands, file formats | âœ… Diseí±ado |
| DoD â†’ Validation Gate | CLI commands, katas | âœ… Diseí±ado |
| raise-mcp CORE | v0.2 scope aumentado | âœ… Decidido |
| Observable Workflow | v0.3 nuevo | âœ… Diseí±ado |
| Escalation Gate | v0.3 scope | âœ… Diseí±ado |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| MCP protocol changes | Medium | High | Version pinning, abstraction layer |
| Scope creep v0.2 | Medium | Medium | Strict gate validation, MVP first |
| Single contributor | High | High | Document everything, attract contributors |
| Enterprise adoption slow | Medium | Medium | Focus on developer experience first |

---

## Changelog

### 2025-12-28
- **FIX**: "Definition of Done" → "Release Criteria" (consistencia terminológica v2.0)
- **MAJOR**: raise-mcp promovido de v0.3 a v0.2 (CORE)
- **NUEVO**: v0.3 ahora es Observable Workflow
- **NUEVO**: v0.4 es Enterprise Preview (antes v0.3)
- Terminologí­a actualizada: guardrails, Validation Gates
- Milestones actualizados con corpus v2.0
- Risk register aí±adido

### 2025-12-27
- Roadmap inicial creado como parte del corpus base
- Definidos 4 releases principales (v0.1 â†’ v1.0)

---

*Este roadmap se revisa mensualmente. Cambios documentados en changelog. Ver [14-adr-index-v2.md](./14-adr-index-v2.md) para decisiones arquitectónicas.*
