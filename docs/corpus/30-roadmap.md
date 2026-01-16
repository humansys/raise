# RaiSE Roadmap
## Plan de Desarrollo

**Versión:** 1.0.0  
**Última Actualización:** 27 de Diciembre, 2025  
**Propósito:** Roadmap de desarrollo del proyecto RaiSE.

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

**Definition of Done:**
- CLI instalable via pip
- Proyecto inicializable con `raise init`
- Reglas sincronizables con `raise hydrate`
- Docs publicados en GitHub Pages

---

### v0.2.0 - Quality Gates (Target: Q2 2025)
**Tema:** "Quality Gates"

- [ ] DoD fractales completos (por fase)
- [ ] Katas de validación (L2, L3)
- [ ] raise-config centralizado (template repo)
- [ ] `raise validate` command
- [ ] Analytics básico (local)

**Definition of Done:**
- Cada fase tiene DoD validable
- Katas ejecutables via CLI
- Template de raise-config publicado

---

### v0.3.0 - Enterprise Preview (Target: Q3 2025)
**Tema:** "Scale"

- [ ] raise-mcp (MCP Server)
- [ ] Multi-agent context support
- [ ] SSO integration (planning)
- [ ] Audit logging (local)
- [ ] On-premise deployment guide

**Definition of Done:**
- MCP server funcional con Claude
- Documentación enterprise disponible

---

### v1.0.0 - Production (Target: Q4 2025)
**Tema:** "Stability"

- [ ] API estable (semver commitment)
- [ ] SOC2 Type I preparation
- [ ] Integraciones Jira/Linear
- [ ] Marketplace de katas community
- [ ] Enterprise tier launch

**Definition of Done:**
- Breaking changes require major version
- Enterprise customers piloting

---

## Milestones Actuales

| Milestone | Status | Target | Progress |
|-----------|--------|--------|----------|
| Corpus base completo | ✅ En Progreso | 2025-01-05 | 80% |
| Fork spec-kit evaluación | ✅ Done | 2025-12-26 | 100% |
| CLI v0.1 alpha | 📋 Pending | 2025-01-31 | 0% |
| Docs site live | 📋 Pending | 2025-02-15 | 0% |

---

## Backlog Priorizado

### P0 (Must Have)

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| Finalizar corpus base | Emilio | 2025-01-05 | En progreso |
| CLI scaffold (click) | TBD | 2025-01-15 | Pending |
| `raise init` command | TBD | 2025-01-20 | Pending |
| `raise hydrate` command | TBD | 2025-01-25 | Pending |
| `raise check` command | TBD | 2025-01-31 | Pending |

### P1 (Should Have)

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| Templates packaging | TBD | 2025-02-15 | Pending |
| Katas L1 completas | TBD | 2025-02-28 | Pending |
| Docusaurus site | TBD | 2025-02-15 | Pending |
| GitHub Actions workflow | TBD | 2025-02-20 | Pending |

### P2 (Nice to Have)

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| raise-mcp prototype | TBD | 2025-03 | Pending |
| VS Code extension | TBD | 2025-Q2 | Pending |
| Analytics dashboard | TBD | 2025-Q2 | Pending |

---

## Changelog

### 2025-12-27
- Roadmap inicial creado como parte del corpus base
- Definidos 4 releases principales (v0.1 → v1.0)

---

*Este roadmap se revisa mensualmente. Cambios documentados en changelog.*
