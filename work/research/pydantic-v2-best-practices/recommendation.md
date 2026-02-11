# Recommendation: Pydantic v2 Best Practices for raise-cli

> Research ID: PYDANTIC-V2-BEST-PRACTICES-20260205
> Date: 2026-02-05

---

## Decision

**Adopt a "validation at boundaries" architecture with these specific patterns for raise-cli.**

**Confidence**: HIGH (based on 22 sources, 8 Very High evidence)

---

## Rationale

The evidence strongly converges on using Pydantic for system boundaries while avoiding "Serdes debt" internally. For a CLI tool like raise-cli that processes governance files, graphs, and user input, this translates to clear patterns.

---

## Actionable Recommendations

### 1. Model Design Patterns

| Use Case | Pattern | Why |
|----------|---------|-----|
| CLI config | `BaseModel + ConfigDict(frozen=True)` | Immutable, validated config |
| Governance files | `BaseModel + strict=False` | Accept flexible input |
| Graph nodes | `Discriminated Union` | Fast polymorphic validation |
| Internal DTOs | `@dataclass` or plain class | Avoid Serdes debt |
| Type adapters | Module-level singleton | Reuse schema compilation |

**Code Pattern - Config Model:**
```python
from pydantic import BaseModel, ConfigDict

class CliConfig(BaseModel):
    model_config = ConfigDict(
        frozen=True,          # Immutable after creation
        extra='forbid',       # Reject unknown fields
        str_strip_whitespace=True,
    )

    project_root: Path
    output_format: Literal['json', 'human', 'table'] = 'human'
```

**Code Pattern - Discriminated Union (Graph Nodes):**
```python
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field

class ConceptNode(BaseModel):
    node_type: Literal['concept'] = 'concept'
    name: str
    definition: str

class PatternNode(BaseModel):
    node_type: Literal['pattern'] = 'pattern'
    pattern_id: str
    description: str

NodeData = Annotated[
    Union[ConceptNode, PatternNode],
    Field(discriminator='node_type')
]
```

### 2. Validation Patterns

| Validator Type | When to Use |
|----------------|-------------|
| `@field_validator(mode='after')` | Default - type-safe field checks |
| `@field_validator(mode='before')` | Input normalization (str -> list) |
| `@model_validator(mode='after')` | Cross-field validation |
| `@model_validator(mode='before')` | Raw input transformation |

**Code Pattern - After Validator (Default):**
```python
from pydantic import BaseModel, field_validator

class GovernanceFile(BaseModel):
    path: Path

    @field_validator('path', mode='after')
    @classmethod
    def validate_exists(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"File not found: {v}")
        return v
```

**Code Pattern - Before Validator (Input Normalization):**
```python
from typing import Any
from pydantic import BaseModel, field_validator

class SearchConfig(BaseModel):
    patterns: list[str]

    @field_validator('patterns', mode='before')
    @classmethod
    def ensure_list(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [v]
        return v
```

### 3. Serialization Patterns

| Method | Use When |
|--------|----------|
| `model_dump()` | Python dict for internal use |
| `model_dump(mode='json')` | JSON-compatible dict |
| `model_dump_json()` | Direct JSON string |
| `model_dump(exclude_unset=True)` | Only explicitly set fields |

**Code Pattern - CLI Output:**
```python
def output_result(result: BaseModel, format: str) -> None:
    if format == 'json':
        print(result.model_dump_json(indent=2))
    elif format == 'human':
        # Custom formatting
        ...
```

### 4. Performance Patterns

| Pattern | Implementation |
|---------|----------------|
| TypeAdapter reuse | Module-level instantiation |
| JSON validation | `Model.model_validate_json()` |
| Specific types | `list[str]` not `Sequence[str]` |
| FailFast | `Annotated[list[T], FailFast]` |

**Code Pattern - TypeAdapter Reuse:**
```python
# In src/rai_cli/schemas/adapters.py
from pydantic import TypeAdapter
from .graph import NodeData, EdgeData

node_adapter = TypeAdapter(NodeData)
edge_adapter = TypeAdapter(EdgeData)
node_list_adapter = TypeAdapter(list[NodeData])

# Usage in other modules
from .adapters import node_adapter
node = node_adapter.validate_json(json_string)
```

**Code Pattern - JSON Validation:**
```python
# GOOD - Direct JSON validation
config = CliConfig.model_validate_json(path.read_text())

# AVOID - Double parsing
import json
config = CliConfig.model_validate(json.loads(path.read_text()))
```

### 5. Anti-Patterns to Avoid

| Anti-Pattern | Why Avoid | Alternative |
|--------------|-----------|-------------|
| BaseModel everywhere | 6.5x slower, 2.5x memory | Use at boundaries only |
| TypeAdapter in functions | Schema recompilation | Module-level singleton |
| `Sequence`/`Mapping` in models | Extra isinstance checks | Use `list`/`dict` |
| `model_construct()` by default | Diminished benefit in v2 | Use regular validation |
| Subclassing primitives | Bypasses optimizations | Use Field constraints |
| Union without discriminator | Tests all options | Add discriminator field |

---

## Trade-offs Accepted

1. **More code organization**: TypeAdapters need dedicated module
2. **Mixed types internally**: Some internal classes won't be BaseModel
3. **Learning curve**: Team needs to understand boundary patterns
4. **Third-party dependency**: pydantic-typer for deep Typer integration

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Inconsistent model usage | Add to guardrails, enforce in PR review |
| Performance regression | Profile before/after changes |
| Validator complexity | Default to after mode, document exceptions |
| Schema drift | Use model_json_schema() for documentation |

---

## Implementation Checklist

- [ ] Audit existing models for boundary vs internal usage
- [ ] Add ConfigDict to config models (frozen, extra='forbid')
- [ ] Convert polymorphic unions to discriminated unions
- [ ] Create `schemas/adapters.py` for TypeAdapter singletons
- [ ] Replace json.loads() + validate with model_validate_json()
- [ ] Update guardrails with Pydantic patterns
- [ ] Add examples to CLAUDE.md code standards

---

## Governance Linkage

- **Guardrails update**: Add Pydantic section to `governance/solution/guardrails.md`
- **ADR candidate**: If major refactoring needed, create ADR-023
- **Component catalog**: Document new schema organization in `dev/components.md`

---

*Generated: 2026-02-05*
*Confidence: HIGH*
*Based on: 22 sources (36% Very High, 41% High evidence)*
