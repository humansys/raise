# Synthesis: Pydantic v2 Best Practices

> Research ID: PYDANTIC-V2-BEST-PRACTICES-20260205
> Date: 2026-02-05

---

## Major Claims (Triangulated)

### Claim 1: BaseModel vs Dataclass Selection

**Claim**: Use BaseModel for data validation at system boundaries; use dataclass for internal data containers where validation is not needed.

**Confidence**: HIGH

**Evidence**:
1. [Pydantic Dataclasses Docs](https://docs.pydantic.dev/latest/concepts/dataclasses/) - "Pydantic dataclasses are NOT a replacement for Pydantic models"
2. [Speakeasy Blog](https://www.speakeasy.com/blog/pydantic-vs-dataclasses) - "Choose BaseModel when data validation and automatic serialization are crucial"
3. [GitHub Issue #710](https://github.com/pydantic/pydantic/issues/710) - Benchmark shows dataclass attribute access is faster than BaseModel

**Disagreement**: Some sources suggest Pydantic dataclasses as a "middle ground" but official docs warn against this.

**Implication for raise-cli**: Use BaseModel for all CLI input/output models (governance files, config, commands). Reserve dataclass for internal data transfer objects where validation overhead matters.

---

### Claim 2: Use `mode='after'` Validators by Default

**Claim**: Field and model validators should use `mode='after'` unless preprocessing raw input is explicitly needed.

**Confidence**: HIGH

**Evidence**:
1. [Pydantic Validators Docs](https://docs.pydantic.dev/latest/concepts/validators/) - "After validators are generally more type safe and thus easier to implement"
2. [Mastering Pydantic Part 2](https://aiechoes.substack.com/p/mastering-pydantic-part-2-advanced) - After mode receives already-coerced values
3. [Context7 Documentation](https://docs.pydantic.dev/latest/llms-full.txt) - After validators run post-initialization, return validated instance

**Disagreement**: None found.

**Implication for raise-cli**: Default to `@field_validator('field', mode='after')` and `@model_validator(mode='after')`. Only use `mode='before'` for input normalization (e.g., accepting both string and list for a field).

---

### Claim 3: TypeAdapter Must Be Instantiated Once at Module Level

**Claim**: TypeAdapter instances should be created at module level and reused; creating them inside functions causes significant performance overhead.

**Confidence**: HIGH

**Evidence**:
1. [Pydantic Performance Docs](https://docs.pydantic.dev/latest/concepts/performance/) - "Each time a TypeAdapter is instantiated, it will construct a new validator and serializer"
2. [Pydantic v2 at Scale](https://medium.com/@connect.hashblock/pydantic-v2-at-scale-7-tricks-for-2-faster-validation-9bd95bf27232) - "Creating a TypeAdapter triggers schema construction - reuse them at module level"
3. [12 Pydantic Patterns](https://medium.com/@ThinkingLoop/12-pydantic-v2-model-patterns-youll-reuse-forever-543426b3c003) - Shows `user_id_adapter = TypeAdapter(UserId)` at module level

**Disagreement**: None found.

**Implication for raise-cli**: Define TypeAdapters in dedicated modules (e.g., `src/rai_cli/schemas/adapters.py`) and import them where needed.

---

### Claim 4: Use Discriminated Unions for Polymorphic Models

**Claim**: When validating unions of multiple model types, use discriminated unions with a literal discriminator field for performance.

**Confidence**: HIGH

**Evidence**:
1. [Pydantic Unions Docs](https://docs.pydantic.dev/latest/concepts/unions/) - "Logic for discriminated unions in Pydantic V2 is implemented in Rust - which means that they're very fast"
2. [Pydantic for Experts](https://blog.dataengineerthings.org/pydantic-for-experts-discriminated-unions-in-pydantic-v2-2d9ca965b22f) - "Instead of trying each union choice until one succeeds, Pydantic uses the discriminator field's value"
3. [Pydantic Performance Docs](https://docs.pydantic.dev/latest/concepts/performance/) - Lists discriminated unions as key optimization

**Disagreement**: None found.

**Implication for raise-cli**: For node types in the graph, use discriminated unions:
```python
NodeData = Annotated[
    Union[ConceptNode, PatternNode, SessionNode],
    Field(discriminator='node_type')
]
```

---

### Claim 5: Avoid Using Pydantic Beyond System Boundaries (Serdes Debt)

**Claim**: Using Pydantic models for all internal data structures causes significant performance and memory overhead ("Serdes debt").

**Confidence**: HIGH

**Evidence**:
1. [Serdes Debt Article](https://leehanchung.github.io/blogs/2025/07/03/pydantic-is-all-you-need-for-performance-spaghetti/) - "6.5x slower performance and 2.5x more memory usage" when using Pydantic everywhere
2. [Why Too Much Pydantic](https://medium.com/@whimox/why-too-much-pydantic-can-be-a-bad-thing-3b9e89d28210) - "Over-inheriting from BaseModel causes problems"
3. [Pydantic Performance Docs](https://docs.pydantic.dev/latest/concepts/performance/) - "avoid subclassing primitives for metadata; use dedicated model fields"

**Disagreement**: None found.

**Implication for raise-cli**:
- **DO**: Use BaseModel for CLI inputs (config files, governance files, user input)
- **DON'T**: Convert every internal class to BaseModel. Use plain classes, dataclasses, or TypedDict for internal processing.

---

### Claim 6: Prefer `model_validate_json()` Over `model_validate(json.loads())`

**Claim**: For JSON input, use the native `model_validate_json()` method instead of parsing JSON first, then validating.

**Confidence**: HIGH

**Evidence**:
1. [Pydantic Performance Docs](https://docs.pydantic.dev/latest/concepts/performance/) - "performs validation directly on JSON streams without intermediate Python dict conversion"
2. [Pydantic v2 at Scale](https://medium.com/@connect.hashblock/pydantic-v2-at-scale-7-tricks-for-2-faster-validation-9bd95bf27232) - Lists JSON parsing as one of 7 performance tricks
3. [Pydantic Serialization Docs](https://docs.pydantic.dev/latest/concepts/serialization/) - Documents the method as primary JSON loading approach

**Disagreement**: None found.

**Implication for raise-cli**: When loading governance files (JSONL, JSON), use `Model.model_validate_json(json_string)` directly.

---

### Claim 7: Use Specific Types Over Abstractions

**Claim**: Prefer `list`, `dict` over `Sequence`, `Mapping` for better validation performance.

**Confidence**: MEDIUM

**Evidence**:
1. [Pydantic Performance Docs](https://docs.pydantic.dev/latest/concepts/performance/) - "Abstract types require additional isinstance checks and multiple validation attempts"
2. [Pydantic v2 at Scale](https://medium.com/@connect.hashblock/pydantic-v2-at-scale-7-tricks-for-2-faster-validation-9bd95bf27232) - Recommends strict unions and specific types

**Disagreement**: Some code style guides prefer abstractions for flexibility.

**Implication for raise-cli**: Use `list[str]` not `Sequence[str]` in model field annotations. Reserve abstractions for function signatures where flexibility matters.

---

### Claim 8: model_construct() Performance Benefit is Diminished in v2

**Claim**: The performance gap between validation and `model_construct()` has narrowed in v2; validation may be faster for simple models.

**Confidence**: MEDIUM

**Evidence**:
1. [Pydantic Models Docs](https://docs.pydantic.dev/latest/concepts/models/) - "For simple models, going with validation may even be faster"
2. [GitHub Discussion #6748](https://github.com/pydantic/pydantic/discussions/6748) - Performance comparison discussions

**Disagreement**: Some sources still recommend model_construct() for trusted data without caveats.

**Implication for raise-cli**: Profile before using `model_construct()`. For most CLI use cases, regular validation is fine.

---

### Claim 9: Use `computed_field` with Explicit `@property` Decorator

**Claim**: When using computed_field, explicitly add @property decorator for better type checking.

**Confidence**: MEDIUM

**Evidence**:
1. [Pydantic Fields Docs](https://docs.pydantic.dev/latest/concepts/fields/) - "it is preferable to explicitly use the @property decorator for type checking purposes"
2. [DataCamp Tutorial](https://www.datacamp.com/tutorial/pydantic) - Shows pattern with both decorators

**Disagreement**: None found.

**Implication for raise-cli**:
```python
@computed_field
@property
def full_path(self) -> str:
    return f"{self.directory}/{self.filename}"
```

---

### Claim 10: Frozen Models Require ConfigDict, Not Class Attribute

**Claim**: In v2, use `model_config = ConfigDict(frozen=True)` not the removed `allow_mutation` attribute.

**Confidence**: HIGH

**Evidence**:
1. [Pydantic v2 Release](https://pydantic.dev/articles/pydantic-v2) - "allow_mutation configuration was removed... use frozen equivalently"
2. [Migration Guide](https://docs.pydantic.dev/latest/migration/) - Documents ConfigDict as the v2 approach
3. [Context7 Examples](https://docs.pydantic.dev/latest/llms-full.txt) - Shows Field(frozen=True) for individual fields

**Disagreement**: None found.

**Implication for raise-cli**: For immutable config models:
```python
class Config(BaseModel):
    model_config = ConfigDict(frozen=True)
```

---

## Patterns & Paradigm Shifts

### Pattern 1: Validation at the Edge

The dominant pattern across sources is "validate at system boundaries, trust internally":
- Parse external input with BaseModel
- Process with plain Python types
- Serialize output with model_dump()

### Pattern 2: Configuration via ConfigDict

Pydantic v2 consolidated configuration into `model_config = ConfigDict(...)`. Key options:
- `frozen=True` - immutability
- `extra='forbid'` - reject unknown fields
- `strict=True` - no type coercion
- `revalidate_instances='always'` - re-validate nested models

### Pattern 3: Annotated Type Pattern

Reusable validators via Annotated types:
```python
PositiveInt = Annotated[int, Field(gt=0)]
Email = Annotated[str, AfterValidator(validate_email)]
```

### Paradigm Shift: Rust Core Performance

Pydantic v2's Rust core (pydantic-core) changes optimization strategies:
- Python-level validators are now the bottleneck
- Declarative constraints (Field, Annotated) are preferred
- model_construct() advantage is reduced

---

## Gaps & Unknowns

1. **Lazy initialization**: Mentioned in v2 roadmap but not yet available
2. **CLI-specific patterns**: Most guidance targets API/web contexts
3. **Typer native integration**: Relies on third-party pydantic-typer
4. **Memory profiling for CLI**: No specific guidance for CLI memory optimization
5. **Async validators**: Limited guidance on async validation patterns

---

*Generated: 2026-02-05*
