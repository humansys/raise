# Synthesis: Python Project Structure Best Practices (2024-2025)

> Research ID: PYTHON-STRUCT-20260205
> Based on 28 sources (25% Very High, 39% High evidence)

---

## Major Claims (Triangulated)

### Claim 1: src Layout is Recommended for Distributable Packages

**Confidence**: HIGH

**Evidence**:
1. [Python Packaging User Guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) - "src/ layout prevents accidental imports from working directory"
2. [pyOpenSci Package Guide](https://www.pyopensci.org/python-package-guide/package-structure-code/python-package-structure.html) - "src/ layout is semantically more clear"
3. [pytest Good Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) - "src layout + --import-mode=importlib recommended"
4. [Real Python](https://realpython.com/ref/best-practices/project-layout/) - "Recommends src layout for packages intended to be installed"

**Disagreement**:
- uv defaults to flat layout (Aug 2024)
- Scientific packages (NumPy, SciPy) use flat due to complex C builds
- Poetry defaults to src (Feb 2025)

**Implication**: Use src layout unless you have specific reasons (complex builds, quick scripts). For RaiSE CLI, src layout is correct.

---

### Claim 2: Keep __init__.py Minimal or Empty

**Confidence**: HIGH

**Evidence**:
1. [Hitchhiker's Guide](https://docs.python-guide.org/writing/structure/) - "leaving __init__.py empty is considered normal and even good practice"
2. [Python Packaging Guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) - "complex __init__.py causes import chain execution"
3. [ArjanCodes](https://arjancodes.com/blog/organizing-python-code-with-packages-and-modules/) - "use __init__.py for public API, not initialization"

**Disagreement**: None found - consensus is strong.

**Implication**: RaiSE should keep __init__.py files minimal. Use for:
- Public API exports (explicit `__all__`)
- Version constants
- Nothing else

---

### Claim 3: Absolute Imports at Package Root, Relative Within Subpackages

**Confidence**: HIGH

**Evidence**:
1. [PEP 328](https://peps.python.org/pep-0328/) - "Absolute imports are default since Python 2.5"
2. [Python For The Lab](https://pythonforthelab.com/blog/complete-guide-to-imports-in-python-absolute-relative-and-more/) - "absolute at root, relative within subpackages"
3. [DataCamp Tutorial](https://www.datacamp.com/tutorial/python-circular-import) - "strategic approach prevents circular dependency problems"

**Disagreement**: Some prefer all-absolute for clarity, but relative within subpackages is widely accepted.

**Implication**:
```python
# In src/rai_cli/commands/context.py
from raise_cli.core import git_utils      # Absolute from root
from .base import CommandBase              # Relative within subpackage
```

---

### Claim 4: pydantic-settings is the Standard for Configuration

**Confidence**: HIGH

**Evidence**:
1. [Pydantic Settings Docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Official, feature-rich configuration management
2. [FastAPI Docs](https://fastapi.tiangolo.com/advanced/settings/) - Recommends pydantic-settings as the pattern
3. [DEV.to Article](https://dev.to/proteusiq/trending-anti-pattern-loading-environments-j55) - "load_dotenv() is an anti-pattern"
4. [Meta Survey](https://engineering.fb.com/2024/12/09/developer-tools/typed-python-2024-survey-meta/) - "62% use Pydantic"

**Disagreement**: python-dotenv is simpler for small projects, but lacks validation.

**Implication**: Use pydantic-settings for:
- Type-safe configuration
- Validation at startup (fail fast)
- Support for multiple sources (.env, env vars, files)

---

### Claim 5: pyproject.toml is the Standard Configuration File

**Confidence**: VERY HIGH

**Evidence**:
1. [Python Packaging Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - Official specification
2. [PEP 621](https://peps.python.org/pep-0621/) - "Standardizes project metadata"
3. [uv Docs](https://docs.astral.sh/uv/concepts/projects/dependencies/) - Uses pyproject.toml
4. [State of Python Packaging 2026](https://learn.repoforge.io/posts/the-state-of-python-packaging-in-2026/) - "PEP 621 supported by all major tools"

**Disagreement**: None - setup.py/setup.cfg are legacy.

**Implication**: All configuration in pyproject.toml:
- `[project]` - PEP 621 metadata
- `[tool.ruff]` - Linting
- `[tool.pyright]` - Type checking
- `[tool.pytest.ini_options]` - Testing

---

### Claim 6: uv is Emerging as the Preferred Package Manager

**Confidence**: MEDIUM-HIGH

**Evidence**:
1. [uv Docs](https://docs.astral.sh/uv/concepts/projects/dependencies/) - 10-100x faster than pip
2. [DataCamp Tutorial](https://www.datacamp.com/tutorial/python-uv) - "replaces pip, venv, pyenv in single tool"
3. [Loopwerk Comparison](https://www.loopwerk.io/articles/2024/python-poetry-vs-uv/) - "Poetry more mature for libraries; uv faster"

**Disagreement**:
- Poetry still preferred for libraries with publishing needs
- Some teams stick with pip for simplicity
- pdm also viable alternative

**Implication**: For RaiSE:
- uv for development workflow (speed)
- Poetry compatibility for library publishing
- Lock file (uv.lock or poetry.lock) for reproducibility

---

### Claim 7: Architectural Patterns Prevent Circular Imports

**Confidence**: HIGH

**Evidence**:
1. [DataCamp Tutorial](https://www.datacamp.com/tutorial/python-circular-import) - "MVC naturally prevents cycles"
2. [Medium Article](https://medium.com/@denis.volokh/the-circular-import-trap-in-python-and-how-to-escape-it-9fb22925dab6) - "Service layer pattern effective"
3. [Dagster Blog](https://dagster.io/blog/python-project-best-practices) - "Use established patterns"

**Disagreement**: None - consensus on architectural approach.

**Implication**: Design dependency direction:
```
commands → handlers → engines → core
                  ↘ schemas ↙
```
Lower layers never import higher layers.

---

### Claim 8: Gradual Typing is Standard Practice

**Confidence**: HIGH

**Evidence**:
1. [Meta Survey](https://engineering.fb.com/2024/12/09/developer-tools/typed-python-2024-survey-meta/) - "67% use mypy, gradual adoption recommended"
2. [Python Typing Docs](https://docs.python.org/3/library/typing.html) - Native generics since 3.9
3. [Khaled's Guide](https://khaled-jallouli.medium.com/python-typing-in-2025-a-comprehensive-guide-d61b4f562b99) - "Use native generics (list[str])"

**Disagreement**: pyright vs mypy preference varies; both valid.

**Implication**:
- Use `from __future__ import annotations` for forward references
- Prefer native generics (`list[str]` not `List[str]`)
- Pyright for strict mode (faster, stricter)

---

## Patterns & Paradigm Shifts (2024-2025)

### 1. Tool Consolidation

**Pattern**: Single tools replacing multiple utilities
- uv = pip + venv + pyenv + pipx
- Ruff = flake8 + black + isort + dozens of plugins

**Shift**: From "best-of-breed toolkit" to "batteries-included toolchain"

### 2. Type Safety as Default

**Pattern**: Type hints expected, not optional
- IDE support is #1 reason (59%)
- Pydantic used by 62% of Python developers
- Runtime validation becoming standard (Pydantic, Beartype)

**Shift**: From "dynamic by default" to "typed by default"

### 3. Lock Files for Reproducibility

**Pattern**: All modern tools generate lock files
- uv.lock, poetry.lock, pdm.lock
- pyproject.toml for constraints, lock file for exact versions

**Shift**: From "requirements.txt" to "declarative + lock"

### 4. src Layout Standardization

**Pattern**: src/ becoming default for non-trivial projects
- pytest recommends it
- Prevents common import errors
- Only exception: scientific computing with complex builds

**Shift**: From "flat by default" to "src by default"

---

## Gaps & Unknowns

### 1. Monorepo Best Practices (Emerging)

- Multiple approaches: Pants, Poetry workspaces, uv workspaces
- No clear winner or standard pattern yet
- RaiSE is single-package, not immediately relevant

### 2. uv Maturity for Publishing

- uv is newer (Feb 2024)
- Publishing workflow less mature than Poetry
- May need Poetry for library publishing

### 3. Namespace Packages Usage

- PEP 420 implicit namespaces well-documented
- Practical guidance on when to use is sparse
- Most projects don't need namespace packages

---

## Key Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Bloated __init__.py | Import chain execution, slow startup | Keep minimal or empty |
| Wildcard imports (`from x import *`) | Namespace pollution, static analysis fails | Explicit imports |
| load_dotenv() without validation | Silent failures, type errors | Use pydantic-settings |
| Circular imports | ImportError at runtime | Architectural layers |
| Deep nesting (>4 levels) | Complex imports, hard to navigate | Flatten or refactor |
| requirements.txt as source of truth | No lock mechanism, drift | pyproject.toml + lock file |
| Mixing src and flat layout | Confusion, import errors | Pick one consistently |
| Static-only classes | Java pattern, not Pythonic | Use plain functions |

---

## Summary

The 2024-2025 Python ecosystem shows strong convergence:

1. **Structure**: src layout + minimal __init__.py
2. **Imports**: Absolute at root, relative in subpackages
3. **Config**: pydantic-settings for type-safe env handling
4. **Deps**: pyproject.toml (PEP 621) + lock file (uv.lock/poetry.lock)
5. **Types**: Gradual typing with pyright or mypy
6. **Tools**: Consolidation (uv, Ruff) replacing fragmented toolchains

RaiSE already follows most of these practices. Key validation points:
- src layout
- pydantic-settings for config
- pyproject.toml with uv
- Strict pyright
- Ruff for linting/formatting
