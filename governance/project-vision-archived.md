# Project Vision: raise-cli

> **Estado**: Draft
> **Fecha**: 2026-01-30
> **Autor**: Claude Opus 4.5 + Emilio Osorio
> **Versión**: 1.0.0
> **PRD Referencia**: `governance/prd.md`

---

## 1. Problem Statement

### 1.1 Problema de Negocio (del PRD)

RaiSE methodology exists as markdown files that engineers must manually navigate and interpret. There's no executable interface — katas are followed mentally, gates are checked manually, and governance context is copy-pasted to AI assistants. This results in ~30 min/kata overhead, inconsistent interpretation across team members, and no measurable governance metrics.

### 1.2 Perspectiva Técnica

The methodology is **static documentation** when it should be **executable infrastructure**. The katas describe processes but don't enforce them; gates define criteria but don't validate them; governance exists but can't be fed to AI assistants programmatically.

**Dolor técnico subyacente:**
- No parser for kata definitions → can't track execution state
- No validator for gate criteria → can't enforce governance deterministically
- No structured context output → AI assistants get inconsistent context
- No metrics collection → can't prove governance effectiveness

---

## 2. Visión de Alto Nivel

### 2.1 Value Proposition

raise-cli transforms RaiSE methodology from documentation into executable governance infrastructure. Engineers interact with governance through familiar CLI patterns (`rai kata run`, `rai gate check`) while AI assistants discover capabilities through the Agent Skills ecosystem. The CLI becomes the single interface for governance execution, validation, and observability.

The CLI is **the engine** that makes RaiSE governance deterministic and observable. It's not another AI coding tool — it's the governance layer that makes AI coding reliable.

### 2.2 Diferenciadores Clave

- **Deterministic validation**: Gates run code, not prompts — auditors can trust the output
- **AI-ready by design**: Structured JSON output + Agent Skill for ecosystem distribution
- **Brownfield-native**: SAR analysis for existing codebases (70-80% of real work)
- **Observable governance**: Metrics prove ROI, not just "it feels better"

### 2.3 Resultados Esperados

- Kata execution time reduced from ~30 min to <10 min (3x improvement)
- Gate pass rate measurable (target >80% first-attempt)
- AI assistants can discover and use RaiSE via Agent Skills ecosystem
- Brownfield projects can onboard with `rai analyze` in <30 seconds

---

## 3. Alineamiento Estratégico

### 3.1 Mapeo Goals → Mecanismos

| Business Goal (PRD) | Mecanismo Técnico | Métrica de Éxito |
|---------------------|-------------------|------------------|
| Executable governance | Kata engine parses/executes `.raise/katas/*.md` | Kata completion tracked |
| Deterministic validation | Gate engine runs validation code against artifacts | Pass/fail with structured output |
| Observable workflows | Metrics store (JSON) tracks all executions | Metrics exportable, >80% pass rate |
| AI-ready context | `rai context generate` produces CLAUDE.md | AI can invoke `rai` commands |
| Brownfield support | `rai analyze` runs ast-grep + ripgrep analysis | SAR generated in <30s |
| Ecosystem distribution | `raise/SKILL.md` follows Agent Skills spec | Publishable to Claude Code plugins |

### 3.2 Impacto por Stakeholder

| Stakeholder | Beneficio Esperado | Métrica |
|-------------|-------------------|---------|
| RaiSE Engineer | Execute katas 3x faster with guided workflow | Time to complete kata |
| Teams | Consistent governance interpretation via deterministic gates | Gate pass variance |
| AI Assistants | Programmatic access to governance context | Skill discovery rate |
| Tech Leads | Observable metrics prove governance effectiveness | Dashboard availability |
| Compliance | Audit trail of all governance decisions | Metrics export |

---

## 4. Scope

### 4.1 Must Have (MVP)

> Máximo 5 items. Sin estos, el proyecto no tiene sentido.

- [x] **Kata execution engine** — Parse and guide kata execution with state tracking
- [x] **Gate validation engine** — Deterministic artifact validation with structured output
- [x] **Context generation** — Produce CLAUDE.md from governance artifacts
- [x] **Brownfield analysis** — SAR generation via ast-grep + ripgrep
- [x] **`rai` Agent Skill** — Bootstrap skill for ecosystem distribution

### 4.2 Should Have

> Importante pero el MVP funciona sin ellos.

- [ ] Interactive mode (`--interactive`) for guided kata execution
- [ ] Shell completion (Bash/Zsh/Fish)
- [ ] `--fix` suggestions for failed gate validations
- [ ] Metrics dashboard (`rai metrics show`)

### 4.3 Could Have (Nice-to-Have)

> Mejoras post-MVP.

- [ ] .cursorrules generation (in addition to CLAUDE.md)
- [ ] CI/CD integration examples
- [ ] Custom kata authoring support

### 4.4 Out of Scope

> Explícitamente excluido de este proyecto.

- ❌ MCP server (deferred to v2.x)
- ❌ SaaS dashboard (deferred to v3.0)
- ❌ IDE extensions (separate project)
- ❌ Multi-repo coordination (enterprise feature)
- ❌ Skill governance/audit (`rai skill audit` deferred to v3.0)
- ❌ Code generation (delegated to AI assistants)

---

## 5. Métricas de Éxito

### 5.1 Métricas de Negocio (Lagging)

| Métrica | Baseline | Target | Timeframe |
|---------|----------|--------|-----------|
| Kata execution time | ~30 min | <10 min | v2.0 launch |
| Gate pass rate (1st attempt) | N/A | >80% | 3 months post-launch |
| Onboarding time | Unknown | <1 hour to first kata | v2.0 launch |

### 5.2 Métricas Técnicas (Leading)

| Métrica | Target | Cómo se Mide |
|---------|--------|--------------|
| CLI startup time | <1 second | pytest benchmark |
| Command response time | <5 seconds | pytest benchmark |
| SAR analysis time (medium repo) | <30 seconds | pytest benchmark |
| Test coverage | >90% | pytest --cov |
| Type coverage | 100% | pyright --strict |

---

## 6. Constraints y Assumptions

### 6.1 Constraints Técnicas

| Constraint | Fuente | Negociable |
|------------|--------|------------|
| Python 3.12+ | Solution Vision | No |
| Pydantic v2 for schemas | Solution Vision | No |
| Typer for CLI framework | Solution Vision | No |
| ast-grep/ripgrep optional | PRD (graceful degradation) | Yes |
| JSON/YAML state (no database) | PRD | Partial |

### 6.2 Constraints de Negocio

| Constraint | Fuente | Negociable |
|------------|--------|------------|
| Open Core model (MIT license) | Business Case | No |
| Dogfood with RaiSE | Business Case | No |
| v2.0 before external funding | Business Case | Partial |

### 6.3 Assumptions

> Supuestos que deben validarse durante la implementación.

1. Pydantic AI is stable enough for production use
2. Engineers will adopt CLI-based governance (vs GUI)
3. Agent Skills ecosystem will remain relevant for distribution
4. ast-grep/ripgrep are commonly available or easily installable
5. JSON/YAML files are sufficient for state management (no SQLite needed)

---

## 7. Componentes de Alto Nivel

### 7.1 Diagrama de Contexto

```
┌─────────────────────────────────────────────────────────────────┐
│                        raise-cli                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Kata Engine │  │ Gate Engine │  │ SAR Engine  │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│  ┌──────┴────────────────┴────────────────┴──────┐              │
│  │                   Core Layer                   │              │
│  │  (Schemas, Config, State, Metrics)            │              │
│  └───────────────────────────────────────────────┘              │
│         │                                                        │
│  ┌──────┴──────┐                                                │
│  │  CLI Layer  │  ← Typer commands                              │
│  └─────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌───────────┐        ┌───────────┐        ┌───────────┐
   │  .raise/  │        │ ast-grep  │        │  ripgrep  │
   │  (katas,  │        │ (optional)│        │ (optional)│
   │  gates)   │        └───────────┘        └───────────┘
   └───────────┘
         │
         ▼
   ┌───────────┐
   │ Agent     │  ← raise/SKILL.md (ecosystem distribution)
   │ Skills    │
   └───────────┘
```

### 7.2 Componentes Principales

| Componente | Responsabilidad | Tecnología |
|------------|-----------------|------------|
| **CLI Layer** | Parse commands, route to engines, format output | Typer |
| **Kata Engine** | Parse kata definitions, track state, guide execution | Pydantic + custom |
| **Gate Engine** | Load gate criteria, validate artifacts, return results | Pydantic + custom |
| **SAR Engine** | Analyze codebase structure, detect patterns | ast-grep, ripgrep |
| **Core Layer** | Schemas, configuration, state management, metrics | Pydantic v2 |
| **Context Generator** | Produce CLAUDE.md from governance artifacts | Jinja2 or custom |

### 7.3 Integraciones Externas

| Sistema | Tipo | Datos | Criticidad |
|---------|------|-------|------------|
| ast-grep | CLI subprocess | AST patterns | Supporting (optional) |
| ripgrep | CLI subprocess | File content | Supporting (optional) |
| Git | CLI subprocess | Repo state, history | Core |
| Agent Skills ecosystem | File output | SKILL.md | Distribution |

---

## 8. Trade-offs Documentados

| Decisión | Alternativas | Elección | Razón |
|----------|--------------|----------|-------|
| State storage | SQLite, JSON files, None | JSON/YAML files | Git-friendly, human-readable, simple |
| CLI framework | Click, argparse, Typer | Typer | Type-safe, modern, good DX |
| Agent Skills model | Full skill, MCP-only, Bootstrap | Bootstrap (Model F) | CLI is product, skill is discovery |
| Internal terminology | Skills, Operations, Commands | Commands | Natural CLI term, avoids Agent Skills confusion |
| ast-grep/ripgrep | Required, Optional, Bundled | Optional | Graceful degradation, easier adoption |

---

## 9. Trazabilidad

| Fuente | Artefacto | Relación |
|--------|-----------|----------|
| PRD | `governance/prd.md` | Input principal |
| Solution Vision | `governance/vision.md` | Contexto de sistema |
| Business Case | `governance/business_case.md` | Justificación de negocio |
| Skills Research | `work/research/outputs/skills-ecosystem-analysis.md` | Agent Skills strategy |
| Tech Design | `governance/design.md` | Output (siguiente) |

---

## 10. Aprobaciones

| Rol | Nombre | Fecha | Status |
|-----|--------|-------|--------|
| Product Owner | Emilio Osorio | 2026-01-30 | Pending |
| Technical Lead | Emilio Osorio | 2026-01-30 | Pending |

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0.0 | 2026-01-30 | Claude Opus 4.5 | Versión inicial |

---

*Generado por: `project/vision` kata*
*Template version: 1.0.0 (ADR-010)*
