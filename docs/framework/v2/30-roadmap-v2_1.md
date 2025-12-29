# RaiSE Roadmap
## Plan de Desarrollo

**VersiÃƒÂ³n:** 2.1.0  
**ÃƒÅ¡ltima ActualizaciÃƒÂ³n:** 29 de Diciembre, 2025  
**PropÃƒÂ³sito:** Roadmap de desarrollo del proyecto RaiSE.

> **Nota de versiÃƒÂ³n 2.0:** Roadmap actualizado con raise-mcp como componente CORE (promovido de v0.3 a v0.2), Observable Workflow, y terminologÃƒÂ­a v2.0.

---

## VisiÃƒÂ³n de Releases

### v0.1.0 - Foundation (Target: Q1 2025)
**Tema:** "Foundation"

- [ ] CLI bÃƒÂ¡sico (init, pull, check, kata)
- [ ] Soporte 5 agentes principales (Cursor, Copilot, Claude, GPT, Gemini)
- [ ] Templates core (PRD, spec, design, story)
- [ ] Katas base (L0, L1)
- [ ] DocumentaciÃƒÂ³n inicial
- [ ] Corpus base completo

**Release Criteria:**
- CLI instalable via pip
- Proyecto inicializable con `raise init`
- Guardrails sincronizables con `raise pull`
- Docs publicados en GitHub Pages

---

### v0.2.0 - MCP-Native & Validation Gates (Target: Q2 2025) [ACTUALIZADO v2.0]
**Tema:** "MCP-Native Quality"

> **Cambio significativo:** raise-mcp promovido de v0.3 a v0.2. MCP es ahora componente CORE.

- [ ] **raise-mcp server (CORE)** [PROMOVIDO]
- [ ] Validation Gates completos (8 gates estÃƒÂ¡ndar)
- [ ] Guardrails system (renombrado de rules)
- [ ] `raise gate` command
- [ ] `raise guardrail` command
- [ ] Katas de validaciÃƒÂ³n (L2, L3)
- [ ] raise-config centralizado (template repo)

**MCP Primitivos Implementados:**
| Primitivo | ImplementaciÃƒÂ³n | Status |
|-----------|----------------|--------|
| Resources | Constitution, Guardrails, Specs | Ã°Å¸â€â€ž En desarrollo |
| Tools | validate_gate, check_guardrail, escalate | Ã°Å¸â€â€ž En desarrollo |
| Prompts | Katas como templates | Ã°Å¸â€œâ€¹ Planificado |
| Sampling | DelegaciÃƒÂ³n razonamiento | Ã°Å¸â€œâ€¹ Planificado |

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
- [ ] MÃƒÂ©tricas derivadas (re-prompting rate, escalation rate)
- [ ] Export OpenTelemetry (opcional)
- [ ] EU AI Act compliance documentation

**Observable Workflow Components:**
| Component | Status |
|-----------|--------|
| Trace logging automÃƒÂ¡tico | Ã°Å¸â€â€ž En desarrollo |
| Audit reports (CLI) | Ã°Å¸â€œâ€¹ Planificado |
| Metrics aggregation | Ã°Å¸â€œâ€¹ Planificado |
| CSV/JSON export | Ã°Å¸â€œâ€¹ Planificado |

**Release Criteria:**
- Cada acciÃƒÂ³n MCP genera trace
- `raise audit` produce reportes ÃƒÂºtiles
- Escalation rate calculable
- DocumentaciÃƒÂ³n EU AI Act disponible

---

### v0.4.0 - Enterprise Preview (Target: Q4 2025)
**Tema:** "Scale"

- [ ] Multi-agent context support avanzado
- [ ] SSO integration (planning)
- [ ] On-premise deployment guide
- [ ] Team analytics dashboard (local)
- [ ] Guardrail marketplace preparation

**Release Criteria:**
- GuÃƒÂ­a enterprise publicada
- Demo con 3+ agentes simultÃƒÂ¡neos

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
| Corpus v2.0 completo | Ã¢Å“â€¦ En Progreso | 2025-12-28 | 90% |
| OntologÃƒÂ­a v2.0 validada | Ã¢Å“â€¦ En Progreso | 2025-12-28 | 85% |
| Fork spec-kit evaluaciÃƒÂ³n | Ã¢Å“â€¦ Done | 2025-12-26 | 100% |
| InvestigaciÃƒÂ³n Agentic AI | Ã¢Å“â€¦ Done | 2025-12-27 | 100% |
| ADRs v2.0 actualizados | Ã¢Å“â€¦ En Progreso | 2025-12-28 | 80% |
| CLI v0.1 alpha | Ã°Å¸â€œâ€¹ Pending | 2025-01-31 | 0% |
| Docs site live | Ã°Å¸â€œâ€¹ Pending | 2025-02-15 | 0% |

---

## Backlog Priorizado

### P0 (Must Have)

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| Finalizar corpus v2.1 | Emilio | 2025-12-29 | ✅ Completado |
| CLI scaffold (click) | TBD | 2025-01-15 | Pending |
| `raise init` command | TBD | 2025-01-20 | Pending |
| `raise pull` command | TBD | 2025-01-25 | Pending |
| `raise kata` command | TBD | 2025-01-28 | Pending |
| `raise check` command | TBD | 2025-01-31 | Pending |
| `raise gate` command | TBD | 2025-02-10 | Pending |
| `raise audit` command | TBD | 2025-02-15 | Pending |

### P1 (Should Have)

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| Templates packaging | TBD | 2025-02-15 | Pending |
| Katas L1 completas | TBD | 2025-02-28 | Pending |
| Docusaurus site | TBD | 2025-02-15 | Pending |
| GitHub Actions workflow | TBD | 2025-02-20 | Pending |
| **`raise mcp` command** | TBD | 2025-02-25 | Pending |
| **`raise guardrail` command** | TBD | 2025-03-01 | Pending |
| **`raise generate` command** | TBD | 2025-03-15 | Pending |

### P2 (Nice to Have)

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| VS Code extension | TBD | 2025-Q2 | Pending |
| Analytics dashboard | TBD | 2025-Q2 | Pending |
| OpenTelemetry export | TBD | 2025-Q3 | Pending |

---

## Dependencias de OntologÃƒÂ­a v2.0

| Cambio | Impacto en Roadmap | Status |
|--------|-------------------|--------|
| Rule Ã¢â€ â€™ Guardrail | CLI commands, file formats | Ã¢Å“â€¦ DiseÃƒÂ±ado |
| DoD Ã¢â€ â€™ Validation Gate | CLI commands, katas | Ã¢Å“â€¦ DiseÃƒÂ±ado |
| raise-mcp CORE | v0.2 scope aumentado | Ã¢Å“â€¦ Decidido |
| Observable Workflow | v0.3 nuevo | Ã¢Å“â€¦ DiseÃƒÂ±ado |
| Escalation Gate | v0.3 scope | Ã¢Å“â€¦ DiseÃƒÂ±ado |

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

### 2025-12-29
- **BREAKING**: Ontologia de comandos actualizada (ADR-010)
- `raise hydrate` -> `raise pull`
- `raise validate` -> `raise kata`
- **NUEVO**: `raise kata` anadido a P0
- **MOVIDO**: `raise mcp`, `raise guardrail`, `raise generate` a P1 (YAGNI)
- Corpus v2.1 marcado como completado

### 2025-12-28
- **FIX**: "Definition of Done" -> "Release Criteria"
- **MAJOR**: raise-mcp promovido de v0.3 a v0.2 (CORE)
- **NUEVO**: v0.3 ahora es Observable Workflow
- **NUEVO**: v0.4 es Enterprise Preview
- Terminologia actualizada: guardrails, Validation Gates

### 2025-12-27
- Roadmap inicial creado como parte del corpus base

---

*Este roadmap se revisa mensualmente. Ver [raise-adr/](./raise-adr/) para decisiones arquitectonicas.*
