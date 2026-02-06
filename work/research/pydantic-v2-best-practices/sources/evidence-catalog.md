# Evidence Catalog: Pydantic v2 Best Practices

> Research ID: PYDANTIC-V2-BEST-PRACTICES-20260205
> Date: 2026-02-05
> Depth: Standard (~2 hours)

---

## Summary Statistics

- **Total Sources**: 22
- **Evidence Distribution**:
  - Very High: 8 (36%)
  - High: 9 (41%)
  - Medium: 5 (23%)
  - Low: 0 (0%)
- **Temporal Coverage**: 2023-2025 (Pydantic v2 era)

---

## Sources

### Official Documentation (Very High Evidence)

**Source 1**: [Pydantic Performance Documentation](https://docs.pydantic.dev/latest/concepts/performance/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025 (latest)
- **Key Finding**: TypeAdapter reuse, model_validate_json(), discriminated unions, and FailFast are key performance optimizations
- **Relevance**: Direct guidance on performance patterns for CLI tool development

**Source 2**: [Pydantic Validators Documentation](https://docs.pydantic.dev/latest/concepts/validators/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025 (latest)
- **Key Finding**: Four validator modes (before, after, plain, wrap) with specific use cases; after mode is "generally more type safe"
- **Relevance**: Core validation patterns for data models

**Source 3**: [Pydantic Dataclasses Documentation](https://docs.pydantic.dev/latest/concepts/dataclasses/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025 (latest)
- **Key Finding**: "Pydantic dataclasses are NOT a replacement for Pydantic models" - they serve different purposes
- **Relevance**: Critical distinction for model design decisions

**Source 4**: [Pydantic Serialization Documentation](https://docs.pydantic.dev/latest/concepts/serialization/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025 (latest)
- **Key Finding**: Three methods - model_dump(), model_dump(mode='json'), model_dump_json() with different use cases
- **Relevance**: Serialization patterns for CLI output

**Source 5**: [Pydantic JSON Schema Documentation](https://docs.pydantic.dev/latest/concepts/json_schema/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025 (latest)
- **Key Finding**: model_json_schema() returns schema definition, not serialized data; supports by_alias parameter
- **Relevance**: Schema generation for configuration validation

**Source 6**: [Pydantic Unions Documentation](https://docs.pydantic.dev/latest/concepts/unions/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025 (latest)
- **Key Finding**: Discriminated unions use Rust-implemented logic for fast type selection
- **Relevance**: Pattern for polymorphic CLI models

**Source 7**: [Pydantic v2.8 Release](https://pydantic.dev/articles/pydantic-v2-8-release)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2024
- **Key Finding**: FailFast annotation for sequence types stops validation on first error
- **Relevance**: Performance optimization for list validation

**Source 8**: [Pydantic v2.11 Release](https://pydantic.dev/articles/pydantic-v2-11-release)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025
- **Key Finding**: 7x reduction in allocations, 2-4x reduction in memory via schema reuse
- **Relevance**: Memory optimization for CLI tools

### Expert Practitioner Sources (High Evidence)

**Source 9**: [Pydantic v2 at Scale: 7 Tricks for 2x Faster Validation](https://medium.com/@connect.hashblock/pydantic-v2-at-scale-7-tricks-for-2-faster-validation-9bd95bf27232)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: TypeAdapter reuse, strict unions, discriminators, JSON parsing, trusted construction double validation throughput
- **Relevance**: Battle-tested performance patterns

**Source 10**: [Working With Pydantic v2: Best Practices](https://medium.com/algomart/working-with-pydantic-v2-the-best-practices-i-wish-i-had-known-earlier-83da3aa4d17a)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025-12
- **Key Finding**: Strict mode prevents magic coercion; model_config replaces metaclass config
- **Relevance**: Configuration best practices

**Source 11**: [12 Pydantic v2 Model Patterns You'll Reuse Forever](https://medium.com/@ThinkingLoop/12-pydantic-v2-model-patterns-youll-reuse-forever-543426b3c003)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Module-level TypeAdapter instantiation pattern for reuse
- **Relevance**: Code organization patterns

**Source 12**: [Why Too Much Pydantic Can Be a Bad Thing](https://medium.com/@whimox/why-too-much-pydantic-can-be-a-bad-thing-3b9e89d28210)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024-12
- **Key Finding**: Over-inheriting from BaseModel causes problems; use within intended scope
- **Relevance**: Critical anti-pattern identification

**Source 13**: [Software Engineering for Data Scientists: Pydantic Performance](https://leehanchung.github.io/blogs/2025/07/03/pydantic-is-all-you-need-for-performance-spaghetti/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: "Serdes debt" - using Pydantic everywhere causes 6.5x slower performance, 2.5x more memory
- **Relevance**: Critical anti-pattern with quantitative data

**Source 14**: [Pydantic for Experts: Discriminated Unions](https://blog.dataengineerthings.org/pydantic-for-experts-discriminated-unions-in-pydantic-v2-2d9ca965b22f)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Discriminated unions enable immediate type identification vs testing multiple possibilities
- **Relevance**: Union pattern optimization

**Source 15**: [pydantic-typer GitHub](https://github.com/pypae/pydantic-typer)
- **Type**: Primary
- **Evidence Level**: High
- **Date**: 2024 (active)
- **Key Finding**: Library for nested Pydantic models in Typer commands
- **Relevance**: Direct integration pattern for CLI

**Source 16**: [Speakeasy: Pydantic vs Dataclasses](https://www.speakeasy.com/blog/pydantic-vs-dataclasses)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: BaseModel for validation/APIs, dataclass for lightweight containers
- **Relevance**: Model selection criteria

**Source 17**: [DataCamp: Pydantic Guide](https://www.datacamp.com/tutorial/pydantic)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Comprehensive patterns including computed_field, Field constraints
- **Relevance**: Practical implementation patterns

### Community Sources (Medium Evidence)

**Source 18**: [DEV.to: Best Practices for Pydantic](https://dev.to/devasservice/best-practices-for-using-pydantic-in-python-2021)
- **Type**: Tertiary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Type annotation mistakes with Union are common pitfall
- **Relevance**: Common error patterns

**Source 19**: [Leapcell: Slots Benchmark Study](https://leapcell.io/blog/does-using-slots-actually-boost-pydantic-and-orm-performance-a-benchmark-study)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: slots=True reduces memory but Pydantic v2 handles it automatically
- **Relevance**: Memory optimization context

**Source 20**: [GitHub Issue #710: BaseModel vs Dataclass](https://github.com/pydantic/pydantic/issues/710)
- **Type**: Primary
- **Evidence Level**: Medium
- **Date**: 2023-ongoing
- **Key Finding**: BaseModel has more overhead but more features; benchmark shows attribute access differences
- **Relevance**: Performance comparison data

**Source 21**: [Mastering Pydantic Part 2: Validation Techniques](https://aiechoes.substack.com/p/mastering-pydantic-part-2-advanced)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Four validator modes with execution order details
- **Relevance**: Validator implementation guidance

**Source 22**: [Context7 Pydantic Documentation](https://docs.pydantic.dev/latest/llms-full.txt)
- **Type**: Primary
- **Evidence Level**: Medium (aggregated)
- **Date**: 2025
- **Key Finding**: Code examples for frozen fields, model validators, dataclass integration
- **Relevance**: Implementation examples

---

## Evidence Gaps Identified

1. **Pydantic + Typer native integration**: Limited official guidance; relies on third-party libraries
2. **CLI-specific patterns**: Most sources focus on API/web contexts
3. **Long-running CLI performance**: No specific guidance for CLI tools that run continuously
4. **Lazy initialization**: Feature not yet available in Pydantic v2 (deferred)

---

*Generated: 2026-02-05*
*Researcher: Rai (Claude Opus 4.5)*
*Tool: WebSearch + Context7*
