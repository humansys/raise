# Research: Pydantic v2 Best Practices

> 15-minute overview for decision-makers

---

## Research Metadata

| Field | Value |
|-------|-------|
| **Research ID** | PYDANTIC-V2-BEST-PRACTICES-20260205 |
| **Primary Question** | What are the best practices and anti-patterns for Pydantic v2 in a CLI codebase? |
| **Decision Context** | raise-cli code standards and potential refactoring |
| **Depth** | Standard (~2 hours) |
| **Sources** | 22 (36% Very High, 41% High evidence) |
| **Tool** | WebSearch + Context7 |
| **Date** | 2026-02-05 |
| **Researcher** | Rai (Claude Opus 4.5) |

---

## Executive Summary

Pydantic v2 best practices converge on a **"validation at boundaries"** pattern: use BaseModel for external input/output (CLI args, config files, API responses) while avoiding the "Serdes debt" of using Pydantic for all internal data structures (6.5x slower, 2.5x more memory).

**Key findings:**
1. **BaseModel vs dataclass**: BaseModel for validation, dataclass for internal DTOs
2. **Validators**: Default to `mode='after'` (type-safe); use `mode='before'` only for preprocessing
3. **Performance**: TypeAdapter reuse, discriminated unions, model_validate_json() are critical
4. **Anti-patterns**: Pydantic everywhere, TypeAdapter in functions, abstract types in models

---

## Quick Reference

### Model Selection

| Context | Use |
|---------|-----|
| Config files | `BaseModel + ConfigDict(frozen=True)` |
| User input | `BaseModel` |
| Polymorphic types | `Discriminated Union` |
| Internal DTOs | `@dataclass` |

### Validator Selection

| Need | Mode |
|------|------|
| Type-safe validation | `mode='after'` (default) |
| Input normalization | `mode='before'` |
| Cross-field checks | `@model_validator(mode='after')` |

### Performance Checklist

- [ ] TypeAdapters at module level
- [ ] `model_validate_json()` not `json.loads()` + validate
- [ ] `list[T]` not `Sequence[T]` in models
- [ ] Discriminated unions for polymorphic types
- [ ] BaseModel only at system boundaries

---

## Contents

| File | Purpose |
|------|---------|
| [prompt.md](./prompt.md) | Research prompt used |
| [synthesis.md](./synthesis.md) | Triangulated claims with evidence |
| [recommendation.md](./recommendation.md) | Actionable recommendations with code patterns |
| [sources/evidence-catalog.md](./sources/evidence-catalog.md) | All 22 sources with ratings |

---

## Recommendation (TL;DR)

**Adopt validation-at-boundaries architecture:**

```python
# GOOD: BaseModel at boundary
class CliConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    project_root: Path

# GOOD: Discriminated union for polymorphism
NodeData = Annotated[Union[ConceptNode, PatternNode], Field(discriminator='node_type')]

# GOOD: TypeAdapter at module level
node_adapter = TypeAdapter(NodeData)

# AVOID: BaseModel for internal processing (Serdes debt)
```

**Confidence**: HIGH

---

## Next Steps

1. Update `governance/solution/guardrails.md` with Pydantic patterns
2. Audit existing schemas for boundary vs internal usage
3. Create `schemas/adapters.py` for TypeAdapter singletons

---

*Quality Checklist Passed:*
- [x] Research question is specific and falsifiable
- [x] 10+ sources consulted (22)
- [x] Evidence catalog created with levels
- [x] Major claims triangulated (3+ sources each)
- [x] Confidence level explicitly stated
- [x] Contrary evidence acknowledged
- [x] Recommendation is actionable
- [x] Governance linkage established

---

*Generated: 2026-02-05*
