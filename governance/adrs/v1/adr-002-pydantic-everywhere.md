# ADR-002: Pydantic for All Data Models

**Date:** 2026-01-30
**Status:** Accepted
**Deciders:** Emilio Osorio, Rai

---

## Context

raise-cli needs to:
- Parse YAML frontmatter from kata/gate definitions
- Validate configuration from multiple sources (CLI, env, files)
- Serialize state and metrics to JSON
- Provide type-safe data structures throughout the codebase
- Generate documentation/schemas automatically

Python offers multiple options for data structures: dict, TypedDict, dataclasses, attrs, Pydantic.

---

## Decision

Use **Pydantic v2** for all data models throughout the codebase.

**Scope:**
- All schemas (KataDefinition, GateDefinition, KataState, etc.)
- Configuration (RaiseSettings with Pydantic Settings)
- API responses (KataResult, GateResult, etc.)
- State persistence (JSON serialization)

**Pattern:**
```python
from pydantic import BaseModel

class KataDefinition(BaseModel):
    id: str
    titulo: str
    work_cycle: str
    prerequisites: list[str] = []
```

---

## Alternatives Considered

### Alternative 1: dict
**Rejected because:**
- No type safety
- No validation (can pass invalid data)
- Manual serialization/deserialization
- No schema generation
- Prone to typos (string keys)

### Alternative 2: TypedDict
**Rejected because:**
- Type checking only (no runtime validation)
- No methods or property validation
- Can't use for configuration cascade
- No JSON serialization helpers

### Alternative 3: dataclasses
**Rejected because:**
- No validation (need to add manually)
- No JSON serialization (need to add manually)
- No nested model validation
- Can't handle configuration cascade

### Alternative 4: attrs
**Rejected because:**
- Less widespread than Pydantic in Python ecosystem
- No built-in settings management
- Would need additional validation library
- Pydantic more actively maintained for our use case

---

## Consequences

### Positive
- **Runtime validation:** Catch bad data early (parse time, not execution time)
- **Type safety:** Full pyright/mypy support
- **JSON serialization:** Built-in `.model_dump_json()`, `.model_validate_json()`
- **Configuration cascade:** Pydantic Settings handles CLI → env → file → defaults
- **Documentation:** Auto-generate JSON schemas for API docs
- **Validation rules:** Built-in validators (email, URL, range, regex)
- **IDE support:** Excellent autocomplete and type inference

### Negative
- **Dependency:** Adds Pydantic as core dependency (~2MB)
- **Learning curve:** Team needs to learn Pydantic patterns
- **Performance:** Validation adds overhead (negligible for CLI use case)
- **Version lock-in:** Pydantic v2 made breaking changes from v1

### Mitigations
- **Dependency size:** Accept as reasonable (2MB is small)
- **Learning curve:** Pydantic v2 docs are excellent, patterns are intuitive
- **Performance:** Irrelevant for CLI (not high-throughput API)
- **Version lock-in:** Pin to Pydantic >=2.6.0, follow their migration guides

---

## Examples

### Configuration Cascade
```python
from pydantic_settings import BaseSettings

class RaiseSettings(BaseSettings):
    output_format: str = "human"
    raise_dir: Path = Path(".raise")

    model_config = SettingsConfigDict(
        env_prefix="RAISE_",
        toml_file="pyproject.toml"
    )

# Auto-loads: CLI > ENV > pyproject.toml > defaults
settings = RaiseSettings()
```

### Validation
```python
class KataDefinition(BaseModel):
    id: str
    prerequisites: list[str] = []

    @field_validator("id")
    def validate_id_format(cls, v: str) -> str:
        if "/" not in v:
            raise ValueError("Kata ID must be 'category/name'")
        return v

# This fails at parse time
kata = KataDefinition(id="invalid")  # ValueError
```

---

## References

- Pydantic docs: https://docs.pydantic.dev/latest/
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- Design: `governance/projects/raise-cli/design.md` (Section 3)

---

*ADR-002 - Pydantic everywhere*
