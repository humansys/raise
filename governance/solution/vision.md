# Solution Vision: RaiSE

> Reliable AI Software Engineering

## Identidad

### Descripción

**RaiSE helps professional developers ship reliable software at AI speed — with governance that works naturally, whether you're using the CLI or your AI assistant.**

### Tipo de Sistema

**Framework + Multi-Interface Tooling**

```
┌──────────────────────────────────────────────────────────────────┐
│                         RaiSE                                    │
│         "Bring value, get out of the way"                        │
├──────────────────────────────────────────────────────────────────┤
│                    ┌─────────────────┐                           │
│                    │   RaiSE Core    │                           │
│                    │  (Methodology)  │                           │
│                    │  Katas + Skills │                           │
│                    └────────┬────────┘                           │
│           ┌─────────────────┼─────────────────┐                  │
│           ▼                 ▼                 ▼                  │
│    ┌────────────┐    ┌────────────┐    ┌────────────┐           │
│    │  CLI       │    │  MCP       │    │  SaaS      │           │
│    │  (v2)      │    │  (future)  │    │  (future)  │           │
│    │  Humans    │    │  Agents    │    │  Teams     │           │
│    └────────────┘    └────────────┘    └────────────┘           │
│        Open Core         Open Core        Enterprise             │
└──────────────────────────────────────────────────────────────────┘
```

### Misión

> **"Raise your craft, feature by feature."**

### Filosofía de Diseño

> **"Bring value, get out of the way."**

- **Natural** — Feels like how you already work
- **Organic** — Grows with your workflow, not imposed
- **Present where users are** — CLI, MCP, IDE — meet them there
- **Invisible when working** — Only visible when it adds value

### The RaiSE Triad

```
        RaiSE Engineer
        (Human - Strategy, Judgment, Ownership)
              │
              │ orchestrates
              ▼
┌─────────────────────────────────────┐
│             RaiSE                   │
│   (Methodology + Governance)        │
│   Deterministic, Observable         │
└─────────────────────────────────────┘
              │
              │ constrains + enables
              ▼
           Claude
    (AI Partner - Execution)
```

- **RaiSE Engineer** = Professional who orchestrates AI-assisted evolution of production systems
- **RaiSE** = The governance/methodology that makes AI development trustworthy
- **"You"** = Claude (or capable LLM) — AI as partner, not replacement

---

## Alcance

### In Scope (v2)

| Capability | Description |
|------------|-------------|
| **Kata execution engine** | Execute solution/project katas via CLI |
| **Governance gates** | Deterministic validation against guardrails |
| **Skills library** | Reusable atomic operations |
| **Observable metrics** | Track gate pass rates, quality trends |
| **Golden context management** | Feed governance context to AI assistants |
| **Brownfield analysis (SAR)** | Codebase structure analysis for existing projects |
| **Template scaffolding** | Generate governance artifacts from templates |
| **CLI interface** | Primary interface for v2 |
| **Greenfield + Brownfield** | Both project modes supported |

### Out of Scope

| Exclusion | Responsibility |
|-----------|---------------|
| **Code generation** | Claude, Cursor, Copilot |
| **Project management** | Jira, Linear (optional integration only) |
| **CI/CD execution** | GitHub Actions, GitLab CI (RaiSE can trigger) |

### Boundaries

| System | Boundary |
|--------|----------|
| **AI Assistants** | v2: RaiSE provides context, AI executes. Future: RaiSE orchestrates via MCP. |
| **CI/CD** | Bidirectional: CI calls RaiSE gates, gates can trigger CI |
| **PM Tools** | Optional sync; not required for RaiSE to function |

---

## Capacidades Core

### MUST (v2 Launch Requirements)

| # | Capability | Description | Users |
|---|------------|-------------|-------|
| 1 | **Kata Execution Engine** | Execute solution/project katas via CLI | RaiSE Engineer, Agents |
| 2 | **Governance Gates** | Deterministic validation against guardrails | RaiSE Engineer |
| 3 | **Skills Library** | Reusable atomic operations | RaiSE Engineer, Agents |
| 4 | **Observable Metrics** | Track gate pass rates, quality trends | RaiSE Engineer, Managers |
| 5 | **Golden Context Management** | Feed governance context to AI assistants | Agents (Claude, Cursor) |
| 6 | **Brownfield Analysis (SAR)** | Codebase structure analysis for existing projects | RaiSE Engineer |
| 7 | **Template Scaffolding** | Generate governance artifacts from templates | RaiSE Engineer |

### SHOULD (Important, Not Blocking)

| Capability | Description | Rationale |
|------------|-------------|-----------|
| **Custom Kata Authoring** | Users create their own katas | Extensibility, community growth |

### COULD (Future / SaaS)

| Capability | Tier |
|------------|------|
| Multi-repo coordination | Enterprise |
| IDE extensions | Future |
| MCP interface | Future |
| SaaS dashboard | Enterprise |

---

## Dirección Técnica

### Stack Tecnológico

| Layer | Technology | Justificación |
|-------|------------|---------------|
| **Language** | Python 3.12+ | Type hints, performance, AI ecosystem |
| **Core Framework** | Pydantic AI | Agentic orchestration, structured outputs |
| **Validation/Schemas** | Pydantic v2 | Governance rules, configs, gates |
| **CLI** | Typer | Modern, type-safe, excellent DX |
| **Distribution** | uv + pipx | Fast, reliable Python distribution |
| **AST Analysis** | ast-grep (shell) | Rust performance for SAR |
| **Search** | ripgrep (shell) | Rust performance for scanning |
| **Testing** | pytest | Standard, mature |
| **Async** | asyncio | Native, Pydantic AI compatible |

### Patrones Arquitectónicos

**Pattern:** Modular Monolith → Plugin-ready when needed

```
PHASE 1: MVP (Modular Monolith)
════════════════════════════════
raise/
├── cli/           # Typer commands
├── engines/       # Core logic
│   ├── kata.py
│   ├── gate.py
│   └── skill.py
├── katas/         # Built-in katas
├── skills/        # Built-in skills
├── schemas/       # Pydantic models
└── core/          # Shared utilities

PHASE 2: Plugin-Ready (When Needed)
═══════════════════════════════════
- Katas loadable from external packages
- Skills loadable from external packages
- Community can contribute without PRs to core
```

**Key Principle:** Engines are stable. Interfaces come and go. Content grows organically.

### Decisiones Fundamentales

| Decisión | Opciones Consideradas | Elección | Razón |
|----------|----------------------|----------|-------|
| Primary Language | TypeScript, Python, Rust, Go | **Python** | Pydantic AI alignment, AI ecosystem, single stack |
| Guardrails Format | YAML+MD, Pure Python, Hybrid | **YAML + Markdown (.mdc)** | Human-readable, git-friendly |
| State Storage | SQLite, JSON/YAML, None | **JSON/YAML files** | Simple, human-readable, git-friendly |
| Architecture | Microservices, Modular Monolith, Plugin | **Modular Monolith → Plugin-ready** | YAGNI now, extensible later |
| Package Name | raise, raise-dev, raiseframework | **raise-cli** | Clear, available, `raise` command |

---

## Quality Attributes

| Attribute | Target | Métrica |
|-----------|--------|---------|
| **Performance** | < 5 seconds | Common CLI operations |
| **Security (CLI)** | Medium | Protects source code, filters secrets |
| **Security (SaaS)** | High | SOC2 compliance (future) |
| **Test Coverage** | >90% | Core codebase |
| **Documentation** | Docstrings + inline | Python standard |
| **Versioning** | SemVer relaxed pre-2.0 | Breaking changes OK until v2.0 |

### Security Level

**CLI (Open Core): Medium**

| Concern | Mitigation |
|---------|------------|
| Source code access | Respect .gitignore, don't index secrets |
| Credentials in context | Filter .env, credentials files |
| Local state storage | No sensitive data in state files |

**SaaS (Enterprise): High** — SOC2, encryption, audit trails (future scope)

---

## Integraciones

### Upstream (RaiSE Consumes)

| Sistema | Tipo | Datos | Criticidad |
|---------|------|-------|------------|
| **Git** | Local CLI | Repo history, branches, commits | Core |
| **ast-grep** | Local CLI | AST patterns, code structure | Core (SAR) |
| **ripgrep** | Local CLI | File content search | Core (SAR) |
| **Additional SAR tools** | TBD | Code analysis | Supporting |

### Downstream (Consumes RaiSE)

| Consumer | Tipo | Datos | SLA |
|----------|------|-------|-----|
| **AI Assistants** | Files (CLAUDE.md, .cursorrules) | Governance context | N/A |
| **AI Assistants** | CLI output | On-demand context | N/A |
| **CI/CD** | CLI (`raise gate check`) | Validation results | < 5s |
| **SaaS** (future) | API | Metrics, audit data | TBD |
| **MCP** (future) | Protocol | Real-time governance | TBD |

### Contratos

| Contract | Format | Status |
|----------|--------|--------|
| Guardrail Schema | Pydantic model + YAML spec | To be defined |
| Kata Schema | Pydantic model + YAML spec | To be defined |
| CLI Output | JSON (structured) | To be defined |
| Context Files | CLAUDE.md, .cursorrules conventions | Follows platform standards |

---

## Evolución

### Roadmap de Alto Nivel

```
v2.0 (MVP)
├── CLI interface (raise command)
├── Kata execution engine
├── Governance gates
├── Skills library
├── Observable metrics (local)
├── Golden context (files)
├── Brownfield analysis (SAR)
└── Template scaffolding

v2.x (Iteration)
├── Custom kata authoring
├── MCP interface
├── Enhanced SAR tools
└── Community contributions

v3.0 (Enterprise)
├── SaaS dashboard
├── Centralized governance
├── Multi-repo coordination
├── Audit trails
└── SOC2 compliance
```

### Principios de Evolución

1. **Ship fast, iterate** — Lean approach to market timing
2. **Dogfood first** — humansys.ai uses RaiSE to build for clients
3. **Community informs** — Let adoption patterns guide plugin architecture
4. **Interfaces evolve, engines stay** — Core stability enables interface flexibility

---

## Trazabilidad

| Fuente | Artefacto |
|--------|-----------|
| Business Case | `governance/solution/business_case.md` |
| Research | `work/research/` |
| Session Log | `work/research/sessions/2026-01-30-solution-discovery-kata.md` |

---

## Aprobaciones

| Rol | Nombre | Fecha | Decisión |
|-----|--------|-------|----------|
| Founder/CEO | Emilio Osorio | 2026-01-30 | **APPROVED** |

---

*Document created: 2026-01-30*
*Kata: solution/vision*
*Version: 1.0.0*
