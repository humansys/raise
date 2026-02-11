# PRD: raise-cli

> The CLI interface for RaiSE — Reliable AI Software Engineering

---

## Problema de Negocio

### Contexto

RaiSE is a methodology + governance framework for reliable AI-assisted software development. The framework defines katas (process patterns), gates (validation criteria), commands (atomic operations), and governance artifacts. However, **the methodology has no executable interface** — engineers must manually navigate markdown files and execute processes mentally.

### Usuarios Afectados

| User | Pain Point |
|------|------------|
| **RaiSE Engineers** | Must manually track kata execution, no automation for validation gates |
| **Teams** | No standardized way to enforce governance across projects |
| **AI Assistants** | No programmatic way to access governance context or execute katas |

### Impacto

| Impact | Measurement |
|--------|-------------|
| **Time waste** | ~30 min/kata manually navigating and tracking progress |
| **Inconsistency** | Variable interpretation of kata steps across team members |
| **No observability** | Cannot measure gate pass rates or governance effectiveness |
| **Adoption friction** | High barrier to entry for new RaiSE Engineers |

### Por Qué Ahora

- **Foundation complete**: Solution/Project katas, gates, and templates are defined
- **Dogfooding opportunity**: Use RaiSE to build RaiSE CLI
- **Market timing**: AI governance becoming regulatory requirement (EU AI Act 2025)
- **Dependency ready**: Pydantic AI, Typer, ast-grep, ripgrep mature and available
- **Ecosystem momentum**: Agent Skills adopted by 25+ tools (Cursor, VS Code, GitHub, OpenAI Codex)

---

## Metas

| # | Goal | Description |
|---|------|-------------|
| 1 | **Executable governance** | Transform markdown-based methodology into executable CLI commands |
| 2 | **Deterministic validation** | Provide programmatic gate validation, not just documentation |
| 3 | **Observable workflows** | Track and report on governance metrics |
| 4 | **AI-ready context** | Feed structured governance context to AI assistants |
| 5 | **Brownfield support** | Analyze existing codebases via SAR (Structure Analysis Report) |
| 6 | **Ecosystem distribution** | Distribute via Agent Skills ecosystem for AI assistant discovery |

---

## Métricas de Éxito

| Metric | Baseline | Target | How Measured |
|--------|----------|--------|--------------|
| Kata execution time | ~30 min (manual) | <10 min (assisted) | CLI telemetry |
| Gate pass rate (1st attempt) | N/A | >80% | CLI telemetry |
| Onboarding time for new RaiSE Engineer | Unknown | <1 hour to first kata | User feedback |
| Test coverage | N/A | >90% | pytest --cov |
| CLI response time | N/A | <5 seconds | Performance tests |

---

## Ecosystem Positioning

### Agent Skills Integration

The Agent Skills ecosystem (Anthropic, adopted by 25+ tools) provides a distribution channel for AI assistant capabilities. RaiSE positions as follows:

```
┌─────────────────────────────────────────────────┐
│  Agent Skill: "raise"                           │
│  → Teaches agents how to use raise-cli          │
│  → Bootstrap/discovery mechanism                │
└─────────────────────────────────────────────────┘
                      │
                      │ invokes
                      ▼
┌─────────────────────────────────────────────────┐
│  raise-cli (the product)                        │
│  ├── raise kata run <kata-id>    (katas)        │
│  ├── raise gate check <gate-id>  (gates)        │
│  ├── raise analyze               (commands)     │
│  ├── raise context generate      (commands)     │
│  └── raise metrics               (commands)     │
└─────────────────────────────────────────────────┘
```

**Strategy**: Model F (Skill as Bootstrap)
- The `rai` Agent Skill is a lightweight bootstrap that teaches AI agents how to use raise-cli
- CLI is the product; skill is the discovery/distribution mechanism
- Skill rarely changes; CLI can evolve freely

### Terminology Alignment

| RaiSE Term | Agent Skills Term | Relationship |
|------------|-------------------|--------------|
| **Commands** | — | CLI atomic operations (internal) |
| **Katas** | — | Process patterns (RaiSE content) |
| **Gates** | — | Validation criteria (RaiSE content) |
| `rai` skill | Agent Skill | Bootstrap for ecosystem distribution |

**Note**: RaiSE uses "commands" for atomic CLI operations to avoid confusion with Agent Skills ecosystem.

### Evolution Path

| Version | Distribution Model | What's Added |
|---------|-------------------|--------------|
| **v2.0** | CLI + `rai` skill | Skill points to CLI (bootstrap) |
| **v2.x** | + MCP server | Structured tool access for agents |
| **v3.0** | + Governance layer | `rai skill audit` for ecosystem governance |

---

## Alcance del Proyecto

### In-Scope (v2.0)

| Capability | Description |
|------------|-------------|
| **Kata execution engine** | Execute solution/project/story katas via CLI |
| **Gate validation engine** | Deterministic validation of governance artifacts |
| **Commands library** | Reusable atomic operations (git, ast-grep, ripgrep wrappers) |
| **Template scaffolding** | Generate governance artifacts from templates |
| **Golden context generation** | Generate CLAUDE.md, .cursorrules from governance |
| **Brownfield analysis (SAR)** | Codebase structure analysis for existing projects |
| **Observable metrics (local)** | Track gate pass rates, kata execution |
| **`rai` Agent Skill** | Bootstrap skill for ecosystem distribution |

### Out-of-Scope

| Exclusion | Rationale | Future? |
|-----------|-----------|---------|
| **MCP server** | Separate interface, different architecture | v2.x |
| **SaaS dashboard** | Enterprise feature, requires backend | v3.0 |
| **IDE extensions** | Separate distribution, different tooling | v2.x |
| **Multi-repo coordination** | Enterprise feature | v3.0 |
| **Custom kata authoring UI** | CLI-based authoring sufficient for v2 | v2.x |
| **Code generation** | Delegated to AI assistants (Claude, Cursor) | N/A |
| **CI/CD execution** | Delegated to CI platforms (RaiSE triggers only) | N/A |
| **Skill governance/audit** | Future differentiator (26% vulnerability rate in ecosystem) | v3.0 |

### Resolved Ambiguities

| Question | Decision |
|----------|----------|
| Include interactive mode? | Yes, with `--interactive` flag for kata execution |
| Support Windows? | Yes, but Linux/macOS primary targets |
| Plugin architecture? | Not in v2.0, but design for future extensibility |
| State persistence format? | JSON/YAML files (git-friendly) |
| Internal "skills" terminology? | Renamed to "commands" to avoid Agent Skills confusion |
| Agent Skills integration? | Model F — lightweight bootstrap skill pointing to CLI |

---

## Requisitos Funcionales

### RF-01: Kata Execution Engine

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-01.1 | The system MUST execute solution-level katas (discovery, vision) | Must |
| RF-01.2 | The system MUST execute project-level katas (discovery, vision, design, backlog) | Must |
| RF-01.3 | The system MUST execute feature-level katas (plan, implement, review) | Must |
| RF-01.4 | The system MUST track kata execution state (not started, in progress, completed) | Must |
| RF-01.5 | The system SHOULD support `--interactive` mode for guided execution | Should |
| RF-01.6 | The system SHOULD display Jidoka inline prompts during execution | Should |

**Command:** `rai kata run <kata-id> [--project <name>] [--interactive]`

### RF-02: Gate Validation Engine

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-02.1 | The system MUST validate governance artifacts against gate criteria | Must |
| RF-02.2 | The system MUST return structured validation results (pass/fail + details) | Must |
| RF-02.3 | The system MUST support solution, project, and feature gates | Must |
| RF-02.4 | The system SHOULD provide `--fix` suggestions for failed validations | Should |
| RF-02.5 | The system COULD integrate with CI/CD via exit codes | Could |

**Command:** `rai gate check <gate-id> [--artifact <path>]`

### RF-03: Commands Library

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-03.1 | The system MUST provide git wrapper commands (status, diff, log) | Must |
| RF-03.2 | The system MUST provide ast-grep wrapper commands (pattern search) | Must |
| RF-03.3 | The system MUST provide ripgrep wrapper commands (content search) | Must |
| RF-03.4 | The system SHOULD provide file manipulation commands (read, write, template) | Should |
| RF-03.5 | The system SHOULD provide structured output (JSON) for AI consumption | Should |

**Command:** `rai <command> [args...] [--json]`

### RF-04: Template Scaffolding

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-04.1 | The system MUST scaffold governance artifacts from templates | Must |
| RF-04.2 | The system MUST support variable substitution in templates | Must |
| RF-04.3 | The system SHOULD validate scaffolded artifacts against schemas | Should |

**Command:** `rai template scaffold <template-id> [--output <path>]`

### RF-05: Golden Context Generation

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-05.1 | The system MUST generate CLAUDE.md from governance artifacts | Must |
| RF-05.2 | The system SHOULD generate .cursorrules from guardrails | Should |
| RF-05.3 | The system SHOULD support custom output formats | Could |

**Command:** `rai context generate [--format claude|cursor|both]`

### RF-06: Brownfield Analysis (SAR)

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-06.1 | The system MUST analyze codebase structure (files, directories) | Must |
| RF-06.2 | The system MUST identify code patterns via ast-grep | Must |
| RF-06.3 | The system MUST generate Structure Analysis Report (SAR) | Must |
| RF-06.4 | The system SHOULD detect technology stack automatically | Should |
| RF-06.5 | The system SHOULD identify architectural patterns | Should |

**Command:** `rai analyze [--path <dir>] [--output <path>]`

### RF-07: Observability

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-07.1 | The system MUST track kata execution history | Must |
| RF-07.2 | The system MUST track gate validation history | Must |
| RF-07.3 | The system SHOULD generate summary reports | Should |
| RF-07.4 | The system SHOULD export metrics in JSON format | Should |

**Command:** `rai metrics [show|export] [--format json]`

### RF-08: Agent Skill Distribution

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-08.1 | The system MUST include a `rai` Agent Skill for ecosystem distribution | Must |
| RF-08.2 | The skill MUST follow Anthropic Agent Skills specification (SKILL.md format) | Must |
| RF-08.3 | The skill SHOULD document core CLI commands and workflows | Should |
| RF-08.4 | The skill SHOULD be publishable to Claude Code plugins marketplace | Should |

**Artifact:** `raise/SKILL.md` (bootstrap skill)

---

## Requisitos No Funcionales

### Performance

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| CLI startup time | <1 second | Responsive UX |
| Common operations | <5 seconds | Per Solution Vision |
| SAR analysis (medium repo) | <30 seconds | Acceptable for brownfield |

### Reliability

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| Test coverage | >90% | Per Guardrails |
| Crash-free execution | 99.9% | Production-ready |
| Idempotent operations | All writes | Safe to retry |

### Security

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| No secrets in code | 100% | Per Guardrails |
| Respect .gitignore | Always | Don't leak sensitive files |
| Filter credentials in context | Always | Per Solution Vision |

### Usability

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| Zero-config for basic use | Required | Low barrier to adoption |
| Helpful error messages | Always | Developer experience |
| Shell completion | Bash/Zsh/Fish | Modern CLI standard |

### Compatibility

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| Python version | 3.12+ | Type hints, performance |
| OS support | Linux, macOS, Windows | Cross-platform |
| External dependencies | ast-grep, ripgrep (optional) | Graceful degradation if missing |
| Agent Skills spec | Compatible | Ecosystem distribution |

---

## Supuestos

| # | Assumption | Impact if Wrong |
|---|------------|-----------------|
| 1 | Engineers prefer CLI over GUI for governance tasks | May need IDE extension sooner |
| 2 | ast-grep and ripgrep are available or easily installable | Need to provide installation guidance or bundle |
| 3 | Pydantic AI is stable enough for production | May need fallback to plain Pydantic |
| 4 | JSON/YAML state files are sufficient (no database needed) | May need SQLite for complex queries |
| 5 | Single-repo governance is the primary use case | Multi-repo needs different architecture |
| 6 | Agent Skills ecosystem will remain relevant | May need to support alternative distribution |

---

## Riesgos Identificados

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| **Pydantic AI instability** | Medium | Medium | Abstract AI layer, allow plain Pydantic fallback | Tech Lead |
| **ast-grep/ripgrep not installed** | High | Low | Graceful degradation with helpful error messages | Dev Team |
| **Scope creep to MCP/SaaS** | Medium | High | Strict scope enforcement, defer to v2.x/v3.0 | Product Owner |
| **Performance issues with large repos** | Medium | Medium | Streaming output, incremental analysis, timeouts | Dev Team |
| **Breaking changes in dependencies** | Low | Medium | Pin versions, comprehensive tests | Dev Team |
| **Agent Skills spec evolution** | Low | Low | Minimal skill (bootstrap), easy to update | Dev Team |

---

## Dependencias

### Upstream (Required by raise-cli)

| Dependency | Type | Purpose | Status |
|------------|------|---------|--------|
| Python 3.12+ | Runtime | Language | Available |
| Pydantic v2 | Library | Validation, schemas | Stable |
| Pydantic AI | Library | Agent orchestration | Stable |
| Typer | Library | CLI framework | Stable |
| ast-grep | External CLI | AST analysis | Stable |
| ripgrep | External CLI | Content search | Stable |

### Downstream (Depends on raise-cli)

| Consumer | Type | Impact |
|----------|------|--------|
| `rai` Agent Skill | Distribution | Bootstrap for AI assistants |
| MCP server (future) | Code | Share engines |
| SaaS (future) | API | Expose via REST |
| CI/CD pipelines | CLI | Gate validation |

---

## Directory Structure

```
.raise/
├── katas/        # Process definitions
├── gates/        # Validation criteria
├── commands/     # Atomic CLI operations (was: skills/)
├── templates/    # Scaffolds
└── agents/       # Agent prompts

raise/
└── SKILL.md      # Agent Skill for ecosystem distribution
```

---

## Trazabilidad

| Source | Artifact |
|--------|----------|
| Solution Vision | `governance/vision.md` |
| Business Case | `governance/business_case.md` |
| Guardrails | `governance/guardrails.md` |
| CLAUDE.md | `CLAUDE.md` |
| Skills Ecosystem Research | `work/research/outputs/skills-ecosystem-analysis.md` |

---

## Aprobaciones

| Rol | Nombre | Fecha | Decisión |
|-----|--------|-------|----------|
| Product Owner | Emilio Osorio | 2026-01-30 | Pending |
| Tech Lead | [NEEDS CLARIFICATION] | Pending | Pending |

---

*Document created: 2026-01-30*
*Last updated: 2026-01-30*
*Kata: project/discovery*
*Version: 1.1.0*
