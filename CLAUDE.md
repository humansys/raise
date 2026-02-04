# RaiSE - Reliable AI Software Engineering

> "Raise your craft, feature by feature."

## Project Identity

**RaiSE** helps professional developers ship reliable software at AI speed — with governance that works naturally, whether you're using the CLI or your AI assistant.

**Type:** Framework + Multi-Interface Tooling (CLI, MCP, SaaS)
**Philosophy:** Bring value, get out of the way. Natural. Organic.

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

---

## Development Principles (Constitution)

### Core Principles

1. **Humans Define, Machines Execute** — Specs are source of truth; code is expression
2. **Governance as Code** — Standards versioned in Git; what's not in repo doesn't exist
3. **Platform Agnosticism** — Works where Git works; no vendor lock-in
4. **Validation Gates** — Quality checked at each phase, not just at the end
5. **Heutagogía** — Teach to fish, don't just deliver fish
6. **Kaizen** — Continuous improvement; learn from failures
7. **Lean Software Development** — Eliminate waste, context-first, Jidoka
8. **Observable Workflow** — Every decision traceable and auditable

### Values

| Value | Over | Meaning |
|-------|------|---------|
| Simplicidad | Completitud | Simple solutions covering 80% of cases |
| Composabilidad | Monolitos | Small components that combine |
| Transparencia | Magia | Everything inspectable and explainable |
| Convención | Configuración | Sensible defaults, override when needed |
| Evolución | Revolución | Incremental changes over total rewrites |
| Observabilidad | Opacidad | Traceability by default |

### Restrictions

**NEVER:**
- Process code without structured context
- Store secrets, tokens, or PII in config files
- Create proprietary API dependencies when Git-native alternative exists
- Sacrifice traceability for speed
- Generate code without documented implementation plan
- Execute without Observable Workflow active
- Ignore Escalation Gates when confidence is low
- Spawn subagents without explicit permission (inference economy)
- Assume tool availability - ask first
- Re-check things user has already told you

**ALWAYS:**
- Validate specs against constitution before planning
- Document architectural decisions (ADRs)
- Maintain backward compatibility in schemas
- Provide escape hatches for advanced users
- Include attribution to upstream projects (MIT compliance)
- Register trace of each interaction
- Escalate to Orchestrator when ambiguous
- Ask before expensive operations (agents, broad searches)
- Listen to session context - don't repeat rejected assumptions

---

## Code Standards (Guardrails)

### Type Safety — REQUIRED

All Python code must have complete type annotations.

```python
# CORRECT
def execute_kata(kata_id: str, context: KataContext) -> KataResult:
    """Execute a kata and return the result."""
    ...

# INCORRECT
def execute_kata(kata_id, context):
    ...
```

- All function parameters must have type hints
- All return types must be annotated
- Use `from __future__ import annotations` for forward references
- Prefer Pydantic models over TypedDict for complex types
- Verify with: `pyright --strict src/`

### Linting & Formatting — REQUIRED

All code must pass Ruff checks.

- Follow PEP 8 style guidelines
- Maximum line length: 88 characters
- Use double quotes for strings
- Imports sorted: standard library, third-party, local
- No unused imports or variables
- Verify with: `ruff check . && ruff format --check .`
- Fix with: `ruff check --fix . && ruff format .`

### Testing — REQUIRED

- **>90% test coverage** on core codebase
- All tests must pass before commit
- Place tests in `tests/` mirroring `src/` structure
- Use pytest fixtures for setup/teardown
- Mock external dependencies (git, ast-grep, ripgrep)
- Test edge cases and error conditions
- Verify with: `pytest --cov=src --cov-fail-under=90`

**RECOMMENDED:** Property-based tests (hypothesis) for parsers and validators.

### Security — REQUIRED

- **No secrets in code** — Never hardcode API keys, passwords, credentials
- Use environment variables for sensitive configuration
- Reference secrets via `os.environ` or Pydantic Settings
- Verify with: `bandit -r src/ -ll` and `detect-secrets scan`

**RECOMMENDED:** Run `pip-audit` or `uv audit` for dependency vulnerabilities.

### Documentation — REQUIRED

Documentation is part of Definition of Done for all features.

**Code-Level (Always):**
- Google-style docstrings on all public APIs
- Type hints on all functions and methods
- Docstrings explain: purpose, responsibilities, dependencies, usage example

**Component Catalog (Per Feature):**
- Update `dev/components.md` when adding new components
- Include: location, purpose, dependencies, public API, when added

**ADRs (When Architectural Decisions Made):**
- Create ADR in `dev/decisions/` for:
  - New architectural patterns
  - Technology choices
  - Significant trade-offs
- Follow template in `dev/decisions/README.md`

**Architecture Guide (Per Epic):**
- Update `dev/architecture-overview.md` at epic completion
- Ensure mental model reflects current state

**Why:** Prepares for future GraphRAG integration - structured docs enable AI context retrieval

### Inference Economy — RECOMMENDED

Treat AI inference as a scarce resource:

- **Gather with tools, think with inference** — Use CLI tools for information retrieval
- **Research tools:**
  - `ddgr "query"` — Free DuckDuckGo search, no API key
  - `llm -m perplexity "query"` — Research with citations (requires API key)
- **Cache results** — Store in evidence catalogs, don't re-query
- **Reserve inference** for synthesis, judgment, creation

**When researching:** Use `ddgr` or `llm` first, then synthesize findings with Claude.

---

## Architecture

### Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Core Framework | Pydantic AI |
| Validation | Pydantic v2 |
| CLI | Typer |
| Distribution | uv + pipx |
| AST Analysis | ast-grep (shell) |
| Search | ripgrep (shell) |
| Testing | pytest |

### Pattern: Skills + Toolkit (ADR-012)

**Architecture decision (E2):** Instead of monolithic engines, use:
- **Skills:** Process guides (markdown) for AI to execute
- **CLI Toolkit:** Deterministic operations for data extraction/validation

```
src/raise_cli/
├── governance/    # E2 Governance Toolkit
│   ├── extraction/    # Parse governance files → concepts
│   ├── graph/         # Build concept graph with relationships
│   └── query/         # MVC queries (97% token savings)
├── cli/           # Typer CLI commands
│   ├── commands/      # Command modules (context, graph, etc.)
│   └── main.py        # CLI app entry point
├── schemas/       # Pydantic models for ALL data structures
├── config/        # Settings with cascade (CLI → env → file → defaults)
├── output/        # Output formatters (human/json/table)
├── core/          # Shared utilities (git, file ops)
├── exceptions.py  # Exception hierarchy with exit codes
├── engines/       # Reserved for future engines (empty)
└── handlers/      # Reserved for orchestration (empty)
```

**Key Principle:** Build dumb tools + smart context, not smart engines.

**Rules:**
- Governance modules provide deterministic operations
- Skills (in `.claude/skills/`) orchestrate CLI toolkit
- All data structures use Pydantic BaseModel (not dict or TypedDict)
- CLI commands can call modules directly (no handlers needed for simple operations)

### Package

- **PyPI:** `raise-cli`
- **Command:** `raise`
- **Install:** `pip install raise-cli` or `uv install raise-cli`

---

## Directory Structure (Three-Directory Model)

```
raise-commons/
├── .raise/           # Framework engine
│   ├── katas/        # Process definitions
│   ├── gates/        # Validation criteria
│   ├── templates/    # Scaffolds
│   ├── skills/       # Atomic operations
│   └── agents/       # Agent prompts
│
├── framework/        # Framework textbook (PUBLIC)
│   ├── reference/    # Constitution, glossary
│   └── concepts/     # Core concepts
│
├── governance/       # Project governance
│   ├── solution/     # Solution-level (business case, vision, guardrails)
│   └── projects/     # Project-level artifacts
│
├── work/             # Active work
│   ├── features/     # Feature specs
│   ├── proposals/    # Draft ADRs
│   └── research/     # Research sessions
│
└── dev/              # Framework maintenance
    └── decisions/    # ADRs
```

| Directory | Purpose | Audience |
|-----------|---------|----------|
| `.raise/` | How to govern (the engine) | All users |
| `framework/` | What governs the framework (PUBLIC) | Framework maintainers |
| `governance/` | What governs this project | Project teams |
| `work/` | Active work in progress | Contributors |
| `dev/` | Governance maintenance tools | Framework maintainers |

---

## Golden Data (Sources of Truth)

| Priority | Document | Purpose |
|----------|----------|---------|
| 1 | `framework/reference/constitution.md` | Immutable principles |
| 2 | `governance/solution/vision.md` | System identity and direction |
| 3 | `governance/solution/guardrails.md` | Code standards |
| 4 | `framework/reference/glossary.md` | Canonical terminology |
| 5 | `dev/decisions/framework/*.md` | Architecture decisions (ADRs) |

---

## Terminology

| Deprecated | Canonical |
|------------|-----------|
| DoD | Validation Gate |
| Rule | Guardrail |
| Developer | Orchestrator / RaiSE Engineer |
| Kata levels L0-L3 | Principio/Flujo/Patrón/Técnica |

Use canonical terms. Correct deprecated usage.

---

## Git Practices

- **Platform:** GitLab (`glab` CLI, not `gh`)
- **Development Branch:** `v2`
- **Branching:** Feature branches from `v2` (see Branch Management SOP below)
- **Commits:** Conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- **Co-authorship:**
  - Rai (AI): `Co-Authored-By: Rai <rai@humansys.ai>`
  - Emilio: `Co-Authored-By: Emilio Osorio <emilio@humansys.ai>`

### Branch Management (REQUIRED)

**Follow SOP:** `dev/sops/branch-management.md`

**Branch naming:** `<type>/<scope>/<description>`
- `feature/` - Single feature implementation (2-5 days)
- `framework/` - Framework-only changes (2-5 days)
- `experiment/` - Research, discovery, multi-concern work (expect to rename)
- `bugfix/` - Bug fixes (1-2 days)
- `docs/` - Documentation only (1-2 days)

**Scope control:**
- Define scope in first commit (what's in/out, done criteria)
- Daily check: Does `git diff v2 --name-only` match branch name?
- Rename early (<3 days) if scope evolves
- Weekly review: Branches >5 days old should merge or justify
- Use parking lot (`dev/parking-lot.md`) to capture scope creep

**Key principle:** One concern per branch, or document multi-concern in `experiment/` type

---

## Toolchain

### Pre-commit Hooks (REQUIRED)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: pyright
        name: pyright
        entry: pyright
        language: system
        types: [python]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        args: ["-r", "src/", "-ll"]

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
```

### Quality Checks

| Check | Command | Blocking |
|-------|---------|----------|
| Linting | `ruff check .` | Yes |
| Formatting | `ruff format --check .` | Yes |
| Type checking | `pyright --strict src/` | Yes |
| Tests | `pytest` | Yes |
| Coverage | `pytest --cov=src --cov-fail-under=90` | Yes |
| Security | `bandit -r src/ -ll` | Yes |
| Secrets | `detect-secrets scan` | Yes |

---

## Jidoka (Stop on Defects)

If you detect:
- Incoherence with governance artifacts
- Violation of guardrails
- Security vulnerability
- Ambiguous requirements

**STOP.** Do not continue accumulating errors.

Cycle: **Detect → Stop → Correct → Continue**

---

## Versioning

- **Schema:** SemVer (relaxed pre-2.0)
- **Breaking changes:** OK until v2.0, strict after
- **Current:** Pre-release development

---

## References

| Artifact | Location |
|----------|----------|
| Constitution | `framework/reference/constitution.md` |
| Solution Vision | `governance/solution/vision.md` |
| Guardrails | `governance/solution/guardrails.md` |
| Business Case | `governance/solution/business_case.md` |
| Glossary | `framework/reference/glossary.md` |
| Rai's Perspective | `.claude/RAI.md` |

---

*Generated from governance artifacts via setup/rules kata*
*Version: 2.1.0*
*Date: 2026-01-31*
