# Research: Python Project Structure Best Practices (2024-2025)

> **Research ID**: PYTHON-STRUCT-20260205
> **Status**: Complete
> **Confidence**: HIGH

---

## 15-Minute Overview

This research investigates current Python project structure best practices to validate and inform RaiSE's architecture.

### Key Findings

1. **src Layout is Standard** - Recommended for distributable packages; prevents accidental imports from working directory

2. **pyproject.toml is Universal** - PEP 621 metadata supported by all major tools; setup.py/setup.cfg are legacy

3. **pydantic-settings for Config** - Type-safe configuration with validation; load_dotenv() considered an anti-pattern

4. **uv Emerging as Standard** - 10-100x faster than pip; replaces pip+venv+pyenv in single tool

5. **Keep __init__.py Minimal** - Avoid initialization logic; use for exports (`__all__`) only

6. **Architectural Layers Prevent Cycles** - MVC/layered architecture naturally prevents circular imports

7. **Gradual Typing is Expected** - 67% use mypy; native generics (list[str]) preferred

### RaiSE Alignment

**Good news**: RaiSE already follows all major best practices:
- src layout
- pyproject.toml + uv
- pydantic-settings
- Strict pyright + Ruff

**Minor refinements identified**:
- Document import convention (absolute root, relative subpackages)
- Audit __init__.py files for bloat

---

## Contents

| File | Purpose |
|------|---------|
| [synthesis.md](./synthesis.md) | Triangulated claims with evidence |
| [recommendation.md](./recommendation.md) | Actionable recommendations |
| [sources/evidence-catalog.md](./sources/evidence-catalog.md) | All 28 sources with ratings |

---

## Research Metadata

| Field | Value |
|-------|-------|
| **Tool/Model** | WebSearch + manual synthesis |
| **Search Date** | 2026-02-05 |
| **Prompt Version** | research-prompt-v1 |
| **Researcher** | Rai (Claude Code Agent) |
| **Total Sources** | 28 |
| **Evidence Distribution** | Very High: 25%, High: 39%, Medium: 29%, Low: 7% |
| **Total Time** | ~45 minutes |

---

## Key Sources

### Official/Primary (Very High Evidence)
- [Python Packaging User Guide - src vs flat](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [PEP 621 - pyproject.toml metadata](https://peps.python.org/pep-0621/)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [pytest Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [uv Documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/)
- [Meta Engineering - Typed Python 2024 Survey](https://engineering.fb.com/2024/12/09/developer-tools/typed-python-2024-survey-meta/)

### Practitioner/High Evidence
- [pyOpenSci Package Guide](https://www.pyopensci.org/python-package-guide/package-structure-code/python-package-structure.html)
- [FastAPI Settings Guide](https://fastapi.tiangolo.com/advanced/settings/)
- [Hitchhiker's Guide - Project Structure](https://docs.python-guide.org/writing/structure/)
- [Real Python - Project Layout](https://realpython.com/ref/best-practices/project-layout/)

---

## Quality Checklist

- [x] Research question is specific and falsifiable
- [x] 10+ sources consulted (28 total)
- [x] Evidence catalog created with levels
- [x] Major claims triangulated (3+ sources)
- [x] Confidence level explicitly stated for each claim
- [x] Contrary evidence acknowledged (where present)
- [x] Recommendation is actionable
- [x] Governance linkage established (validation of existing architecture)

---

## Governance Linkage

- **Decision**: No ADR needed; existing architecture validated
- **Guardrails**: Consider adding import convention to `governance/solution/guardrails.md`
- **Impact**: Confirms RaiSE is aligned with industry best practices
