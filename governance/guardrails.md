---
type: guardrails
version: "2.0.0"
constraint_scopes:
  default: all_bounded_contexts
  overrides:
    must-arch: [bc-ontology, bc-skills]
    should-cli: [lyr-orchestration]
---

# Guardrails: RaiSE

> Governance rules for reliable production Python code

## Contexto del Sistema

RaiSE is a reliability framework for AI-assisted software engineering. These guardrails ensure the codebase exemplifies the quality standards it promotes.

**Philosophy:** RaiSE code must be exemplary — if we advocate for governance, our own code must pass the highest standards.

---

## Trazabilidad

| Fuente | Artefacto |
|--------|-----------|
| Business Case | `governance/business_case.md` |
| Solution Vision | `governance/vision.md` |

---

## Principios Rectores

Derived from Solution Vision:

1. **Type Safety First** — Pydantic AI requires strict typing; we embrace it everywhere
2. **Single Tool per Job** — Ruff for linting+formatting, not multiple tools
3. **Security by Default** — No secrets, no vulnerabilities, audit-ready
4. **Test What Matters** — >90% coverage, property-based tests for critical paths
5. **Modern Python** — pyproject.toml, uv, Python 3.12+ features
6. **Inference Economy** — Treat AI inference as scarce; offload gathering to deterministic tools

---

## Guardrails Activos

### Code Quality

| ID | Level | Guardrail | Verificación | Derivado de |
|----|-------|-----------|--------------|-------------|
| `MUST-CODE-001` | MUST | Type hints on all code | `pyright --strict` passes | Solution Vision §Stack |
| `MUST-CODE-002` | MUST | Ruff linting passes | `ruff check .` exits 0 | Best practices |
| `MUST-CODE-003` | MUST | No type errors | `pyright` reports 0 errors | Solution Vision §Stack |
| `SHOULD-CODE-001` | SHOULD | Google-style docstrings on public APIs | Manual review / pydocstyle | Best practices |
| `SHOULD-CODE-002` | SHOULD | Prefer clear names over acronyms | Manual review / naming patterns | F2.3 retro |

### Testing

| ID | Level | Guardrail | Verificación | Derivado de |
|----|-------|-----------|--------------|-------------|
| `MUST-TEST-001` | MUST | >90% test coverage | `pytest --cov` ≥ 90% | Solution Vision §Quality |
| `MUST-TEST-002` | MUST | All tests pass | `pytest` exits 0 | Best practices |
| `SHOULD-TEST-001` | SHOULD | Property-based tests for parsers/validators | hypothesis tests exist for Pydantic models | Best practices |

### Security

| ID | Level | Guardrail | Verificación | Derivado de |
|----|-------|-----------|--------------|-------------|
| `MUST-SEC-001` | MUST | No secrets in code | `detect-secrets` + `bandit` pass | Solution Vision §Security |
| `MUST-SEC-002` | MUST | Bandit security scan passes | `bandit -r src/` exits 0 | Solution Vision §Security |
| `SHOULD-SEC-001` | SHOULD | Dependency vulnerability scan | `pip-audit` or `uv audit` | Best practices |

### Architecture

| ID | Level | Guardrail | Verificación | Derivado de |
|----|-------|-----------|--------------|-------------|
| `MUST-ARCH-001` | MUST | Engine/content separation | Engines in `engines/`, content in `katas/`, `skills/` | Solution Vision §Architecture |
| `MUST-ARCH-002` | MUST | Pydantic models for all schemas | All config/data classes inherit from Pydantic BaseModel | Solution Vision §Stack |
| `SHOULD-ARCH-001` | SHOULD | No circular imports | Import analysis passes | Best practices |

### Development Workflow

| ID | Level | Guardrail | Verificación | Derivado de |
|----|-------|-----------|--------------|-------------|
| `MUST-DEV-001` | MUST | Pre-commit hooks configured | `.pre-commit-config.yaml` exists and runs | Best practices |
| `MUST-DEV-002` | MUST | pyproject.toml for config | All tool config in `pyproject.toml` | Best practices |
| `SHOULD-DEV-001` | SHOULD | uv for dependency management | `uv.lock` exists | Solution Vision §Stack |
| `SHOULD-DEV-002` | SHOULD | Run tests after ruff --fix | Tests pass after auto-fix | F7.1 retro |

### CLI Development

| ID | Level | Guardrail | Verificación | Derivado de |
|----|-------|-----------|--------------|-------------|
| `SHOULD-CLI-001` | SHOULD | Explicit path parameters for testability | CLI commands use `--path` option, not `cwd()` | F7.1 retro |

### Inference Economy

| ID | Level | Guardrail | Verificación | Derivado de |
|----|-------|-----------|--------------|-------------|
| `SHOULD-INF-001` | SHOULD | Use CLI tools for information gathering | Research uses `ddgr`, `llm`, etc. before inference | Lean §7 |
| `SHOULD-INF-002` | SHOULD | Cache research results | Evidence catalogs prevent re-querying | Lean §7 |
| `SHOULD-INF-003` | SHOULD | Reserve inference for synthesis | Gathering is deterministic, thinking is inference | Lean §7 |

---

## Guardrail Details

### MUST-CODE-001: Type Hints on All Code

**Regla:** All Python code must have complete type annotations.

**Contexto (Golden Context para Agentes):**
```
When writing Python code for RaiSE:
- All function parameters must have type hints
- All function return types must be annotated
- Use `from __future__ import annotations` for forward references
- Prefer Pydantic models over TypedDict for complex types
- Use `typing.Protocol` for interfaces
```

**Verificación:**
```yaml
check: command
command: pyright --strict src/
threshold: 0 errors
blocking: true
on_failure:
  message: "Type errors found. All code must have complete type annotations."
  recovery: "Run pyright and fix reported errors."
```

**Ejemplos:**

✅ Correcto:
```python
def execute_kata(kata_id: str, context: KataContext) -> KataResult:
    """Execute a kata and return the result."""
    ...
```

❌ Incorrecto:
```python
def execute_kata(kata_id, context):
    """Execute a kata and return the result."""
    ...
```

**Pattern: Using `cast()` for `Any` in containers**

When pyright strict mode reports "partially unknown type" for values extracted from `dict[str, Any]` or `list[Any]`, use `typing.cast()` to assert the expected type:

```python
from typing import Any, cast

def process_nested(data: dict[str, Any]) -> None:
    for key, value in data.items():
        if isinstance(value, dict):
            # cast() tells pyright the exact type after isinstance check
            nested = cast(dict[str, Any], value)
            process_nested(nested)
        elif isinstance(value, list):
            items = cast(list[Any], value)
            for item in items:
                ...
```

Use `cast()` when:
- Processing recursive structures with `Any` values
- After `isinstance()` checks where pyright can't narrow the type
- Working with external data (JSON, TOML) where structure is validated elsewhere

**Do NOT** use `cast()` to silence legitimate type errors.

---

### MUST-CODE-002: Ruff Linting Passes

**Regla:** All code must pass Ruff linting and formatting checks.

**Contexto (Golden Context para Agentes):**
```
When writing Python code for RaiSE:
- Follow PEP 8 style guidelines
- Maximum line length: 88 characters (Ruff default)
- Use double quotes for strings
- Imports sorted: standard library, third-party, local
- No unused imports or variables
```

**Verificación:**
```yaml
check: command
command: ruff check . && ruff format --check .
threshold: 0 errors
blocking: true
on_failure:
  message: "Ruff linting or formatting errors found."
  recovery: "Run `ruff check --fix .` and `ruff format .`"
```

---

### SHOULD-CODE-002: Prefer Clear Names Over Acronyms

**Regla:** Use clear, descriptive names instead of acronyms unless the acronym is universally understood.

**Contexto (Golden Context para Agentes):**
```
When naming classes, functions, and variables in Python:
- Prefer semantic clarity over brevity
- Avoid acronyms that can be ambiguous or context-dependent
- Use acronyms only when universally understood (HTTP, JSON, API, etc.)
- Prioritize self-documenting code over clever abbreviations
```

**Verificación:**
```yaml
check: manual
criteria: Code review checks for clear, descriptive names
blocking: false
on_failure:
  message: "Consider using more descriptive names."
  recovery: "Rename ambiguous acronyms to clear semantic names."
```

**Ejemplos:**

✅ Correcto:
```python
# Clear semantic names
class ContextQuery(BaseModel):
    """Query for Minimum Viable Context (MVC)."""
    query: str
    strategy: QueryStrategy

class ContextResult(BaseModel):
    """Result of context query."""
    concepts: list[Concept]
```

❌ Incorrecto:
```python
# Ambiguous acronyms
class MVCQuery(BaseModel):
    """Query for context."""  # MVC = Model-View-Controller? Minimum Viable Context?
    query: str

class MVCResult(BaseModel):
    """Result."""  # Unclear what MVC means here
    concepts: list[Concept]
```

**Rationale:** Python developers expect clear, readable code (PEP 8). Acronyms like "MVC" can be ambiguous (Model-View-Controller vs Minimum Viable Context). Domain terminology can stay in docstrings and documentation while code uses semantic names.

**Evidence:** F2.3 feature - renamed `MVCQuery` → `ContextQuery` for clarity. User feedback: "Python developers expect clear names over acronyms unless universally understood."

---

### MUST-TEST-001: >90% Test Coverage

**Regla:** Test coverage must be at least 90% for the core codebase.

**Contexto (Golden Context para Agentes):**
```
When writing code for RaiSE:
- Write tests for all new functionality
- Place tests in `tests/` mirroring `src/` structure
- Use pytest fixtures for setup/teardown
- Mock external dependencies (git, ast-grep, ripgrep)
- Test edge cases and error conditions
```

**Verificación:**
```yaml
check: coverage
command: pytest --cov=src --cov-report=term-missing --cov-fail-under=90
threshold: 90
blocking: true
on_failure:
  message: "Test coverage below 90%."
  recovery: "Add tests for uncovered code paths."
```

---

### MUST-SEC-001: No Secrets in Code

**Regla:** No secrets, API keys, passwords, or credentials in code.

**Contexto (Golden Context para Agentes):**
```
When writing code for RaiSE:
- Never hardcode secrets, API keys, or passwords
- Use environment variables for sensitive configuration
- Add secret patterns to .gitignore
- Reference secrets via `os.environ` or Pydantic Settings
```

**Verificación:**
```yaml
check: command
command: detect-secrets scan --baseline .secrets.baseline && bandit -r src/ -ll
threshold: 0 findings
blocking: true
on_failure:
  message: "Potential secrets or security issues found."
  recovery: "Remove secrets from code; use environment variables."
```

---

### MUST-ARCH-001: Engine/Content Separation

**Regla:** Engines (stable) must be separate from content (grows organically).

**Contexto (Golden Context para Agentes):**
```
RaiSE architecture separates concerns:

src/raise_cli/
├── engines/       # Stable core logic (kata, gate, skill engines)
│   ├── kata.py    # Kata execution engine
│   ├── gate.py    # Gate validation engine
│   └── skill.py   # Skill execution engine
├── katas/         # Built-in kata definitions (content)
├── skills/        # Built-in skill definitions (content)
├── schemas/       # Pydantic models for all data
├── cli/           # Typer CLI commands
└── core/          # Shared utilities

Rules:
- Engines import schemas, never content
- Content uses engines via well-defined interfaces
- New katas/skills don't require engine changes
```

**Verificación:**
```yaml
check: architecture
command: "import analysis: engines/ should not import from katas/ or skills/"
blocking: true
on_failure:
  message: "Architecture violation: engines should not import content."
  recovery: "Refactor to maintain engine/content separation."
```

---

### MUST-ARCH-002: Pydantic Models for All Schemas

**Regla:** All configuration and data structures must use Pydantic models.

**Contexto (Golden Context para Agentes):**
```
When defining data structures in RaiSE:
- Use Pydantic BaseModel for all schemas
- Use Pydantic Settings for configuration
- Define models in src/raise_cli/schemas/
- Use Field() for validation and documentation
- Export models from schemas/__init__.py
```

**Verificación:**
```yaml
check: grep
pattern: "^class.*\\(.*TypedDict\\)|^.*: dict\\[|^.*= \\{\\}"
path: "src/"
expect: 0 matches
blocking: true
on_failure:
  message: "Found dict or TypedDict instead of Pydantic model."
  recovery: "Convert to Pydantic BaseModel."
```

---

### MUST-DEV-001: Pre-commit Hooks Configured

**Regla:** Pre-commit hooks must be configured and all hooks must pass.

**Contexto (Golden Context para Agentes):**
```
RaiSE uses pre-commit for automated checks:

.pre-commit-config.yaml must include:
- ruff (linting + formatting)
- pyright (type checking)
- bandit (security)
- detect-secrets (secret scanning)
- pytest (optional, with --all flag)

Contributors must run: `pre-commit install`
```

**Verificación:**
```yaml
check: file_exists
path: ".pre-commit-config.yaml"
blocking: true
on_failure:
  message: "Pre-commit configuration not found."
  recovery: "Create .pre-commit-config.yaml with required hooks."
```

---

### SHOULD-INF-001: Use CLI Tools for Information Gathering

**Regla:** Prefer deterministic CLI tools over inference for information gathering.

**Contexto (Golden Context para Agentes):**
```
When researching or gathering information:
- Use `ddgr "query"` for quick web searches (free, no API key)
- Use `llm -m perplexity "query"` for research with citations (API key required)
- Use `WebSearch` only when CLI tools unavailable
- Reserve inference (Claude) for synthesis, judgment, and creation
- Cache results in evidence catalogs to prevent re-querying
```

**Verificación:**
```yaml
check: process
criteria: Research sessions use CLI tools before inference
blocking: false
on_failure:
  message: "Consider using deterministic tools for gathering."
  recovery: "Install ddgr: apt install ddgr"
```

**Rationale:** Inference is expensive (tokens, latency, environmental cost). Gathering is deterministic work; synthesis is where inference adds value.

---

### SHOULD-DEV-002: Run Tests After Ruff --fix

**Regla:** Always run tests after using `ruff check --fix` to verify auto-fixes didn't break code.

**Contexto (Golden Context para Agentes):**
```
When using Ruff auto-fix:
- `ruff check --fix` can remove "unused" imports
- Those imports might be used in tests or dynamically
- Always verify: ruff check --fix . && pytest
- If tests fail after fix, investigate the removed imports
```

**Verificación:**
```yaml
check: process
criteria: Tests pass after ruff auto-fix
blocking: false
on_failure:
  message: "Auto-fix may have broken tests."
  recovery: "Restore removed imports if tests fail."
```

**Evidence:** F7.1 feature - `ruff --fix` removed `get_rai_home` import, breaking 8 tests that patched it.

---

### SHOULD-CLI-001: Explicit Path Parameters for Testability

**Regla:** CLI commands should use explicit `--path` parameters instead of relying on `cwd()`.

**Contexto (Golden Context para Agentes):**
```
When designing CLI commands with directory operations:
- Add `--path PATH` option defaulting to current directory
- Avoid mocking `Path.cwd()` in tests
- Tests can pass explicit paths without complex patching
- Also simplifies scripting: `raise init --path /some/dir`
```

**Verificación:**
```yaml
check: design_review
criteria: CLI commands with directory operations have --path option
blocking: false
on_failure:
  message: "Consider adding --path option for testability."
  recovery: "Add `--path` parameter defaulting to `Path.cwd()`."
```

**Ejemplos:**

✅ Correcto:
```python
@app.command()
def init(
    path: Annotated[Path | None, typer.Option("--path", "-p")] = None,
) -> None:
    project_path = path if path is not None else Path.cwd()
    # ... use project_path
```

❌ Incorrecto:
```python
@app.command()
def init() -> None:
    project_path = Path.cwd()  # Hard to test without mocking
    # ...
```

**Evidence:** F7.1 feature - using `--path` simplified test mocking from 3 patch points to 1.

---

## Proceso de Excepción

To request an exception to any guardrail:

1. **Create ADR** in `dev/decisions/` documenting:
   - Which guardrail(s) need exception
   - Why the exception is necessary
   - Scope and duration of exception
   - Mitigation for the bypassed protection

2. **Get approval** from project maintainer

3. **Document** the exception in this file under "Active Exceptions"

### Active Exceptions

*None*

---

## Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/RobertCraiwordie/pyright-python
    rev: v1.1.350
    hooks:
      - id: pyright

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

---

## Historial de Cambios

| Fecha | Versión | Cambio |
|-------|---------|--------|
| 2026-01-30 | 1.0.0 | Initial guardrails derived from Solution Vision |
| 2026-01-31 | 1.1.0 | Added Inference Economy principle and guardrails (SHOULD-INF-*) |
| 2026-01-31 | 1.2.0 | Added `cast()` pattern for pyright strict mode (F1.5 retro) |
| 2026-01-31 | 1.3.0 | Added Python naming best practices (SHOULD-CODE-002, F2.3 retro) |
| 2026-02-05 | 1.4.0 | Added SHOULD-DEV-002 (tests after ruff fix) and SHOULD-CLI-001 (path params), F7.1 retro |

---

## Aprobaciones

| Rol | Nombre | Fecha | Decisión |
|-----|--------|-------|----------|
| Founder/CEO | Emilio Osorio | 2026-01-30 | **APPROVED** |

---

*Document created: 2026-01-30*
*Kata: setup/governance*
*Version: 1.0.0*
