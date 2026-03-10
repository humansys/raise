# Recommendation: Python Project Structure Best Practices

> Research ID: PYTHON-STRUCT-20260205
> Based on 28 sources with triangulated evidence

---

## Recommendation

**Decision**: Validate and maintain RaiSE's current structure with minor refinements.

**Confidence**: HIGH

**Rationale**: RaiSE already follows the 2024-2025 consensus on Python project structure. The research confirms our existing choices and identifies opportunities for refinement.

---

## Current RaiSE Alignment

| Practice | Standard (2024-2025) | RaiSE Status | Action |
|----------|---------------------|--------------|--------|
| src layout | Recommended for packages | Using `src/rai_cli/` | Aligned |
| pyproject.toml | Standard (PEP 621) | Using pyproject.toml | Aligned |
| pydantic-settings | Recommended | Using for config | Aligned |
| uv for deps | Emerging standard | Using uv | Aligned |
| Strict pyright | Industry practice | Configured | Aligned |
| Ruff linting | Modern standard | Configured | Aligned |
| Minimal __init__.py | Best practice | Mostly followed | Review needed |
| Import patterns | Absolute root/relative sub | Mixed usage | Standardize |
| Lock file | Required for reproducibility | Using uv.lock | Aligned |

---

## Actionable Refinements

### 1. Audit __init__.py Files (LOW PRIORITY)

**Current state**: Unknown complexity
**Standard**: Keep minimal (exports, version only)

**Action**: Review all __init__.py files in `src/rai_cli/`:
- Remove any initialization logic
- Keep only `__all__` exports and version constants
- Move any code to dedicated modules

### 2. Standardize Import Convention (LOW PRIORITY)

**Current state**: Mixed absolute/relative
**Standard**: Absolute at package root, relative within subpackages

**Action**: Document in CLAUDE.md or guardrails:
```python
# CORRECT - root level module importing another root module
from raise_cli.core import git_utils

# CORRECT - subpackage importing sibling
from .base import CommandBase

# INCORRECT - relative from root
from . import core  # should be: from raise_cli import core
```

### 3. Verify pytest Configuration (ALREADY DONE)

**Standard**: Use `--import-mode=importlib` with src layout
**Action**: Confirm in pyproject.toml:
```toml
[tool.pytest.ini_options]
addopts = ["--import-mode=importlib"]
```

### 4. Document Architectural Layers (CONTINUOUS)

**Purpose**: Prevent circular imports by design
**Action**: Maintain in `dev/architecture-overview.md`:
```
Dependency Direction (higher imports lower, never reverse):
  commands/ → handlers/ → engines/ → core/
                     ↘ schemas/ ↙
  exceptions.py (shared, imported by all)
```

---

## Trade-offs Acknowledged

| Choice | Benefit | Cost |
|--------|---------|------|
| src layout | Clean imports, test isolation | Extra directory level |
| uv over Poetry | Speed (10-100x), unified tooling | Less mature for library publishing |
| Strict pyright | Catches more bugs | Stricter than mypy, more annotation work |
| pydantic-settings | Type-safe config, validation | Runtime dependency |

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| uv breaking changes | Low | Medium | Lock uv version, test upgrades |
| Over-complexity in __init__.py | Medium | Low | Periodic audits, Ruff rules |
| Circular import creep | Medium | Medium | Architectural discipline, CI checks |
| Tool ecosystem fragmentation | Low | Low | Follow PyPA standards (PEP 621) |

---

## Alternatives Considered

### Flat Layout
**Why not**: Would require restructuring; src layout is better for distributable packages.

### Poetry Instead of uv
**Why not**: uv is faster and RaiSE already uses it. Poetry would add migration cost.

### mypy Instead of pyright
**Why not**: pyright is stricter and faster. Already configured in RaiSE.

---

## Implementation Priority

1. **No immediate changes needed** - RaiSE is well-aligned
2. **Low priority refinements** - Can be done during maintenance windows:
   - __init__.py audit
   - Import convention documentation
3. **Ongoing discipline** - Part of code review:
   - Maintain architectural layers
   - Enforce import patterns

---

## Governance Linkage

- **ADR Impact**: No new ADR needed; existing architecture is validated
- **Guardrails Update**: Consider adding import convention to `governance/solution/guardrails.md`
- **Parking Lot**: None; research is complete

---

## Conclusion

RaiSE's current structure is well-aligned with 2024-2025 Python best practices. The research validates our existing choices:
- src layout
- pyproject.toml with PEP 621
- uv for dependency management
- pydantic-settings for configuration
- Strict pyright for type checking
- Ruff for linting/formatting

No structural changes are required. Minor refinements (import convention documentation, __init__.py audit) can be scheduled as maintenance tasks.
