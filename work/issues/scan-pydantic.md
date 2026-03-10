# Pydantic Anti-Pattern Scan Report

> Scanned: `src/rai_cli/` against `governance/solution/guardrails-stack.md` Section 1 (Pydantic v2)
> Date: 2026-02-05
> Files scanned: 72 Python files

---

## Summary

| Severity | Count |
|----------|-------|
| High     | 0     |
| Medium   | 3     |
| Low      | 1     |

**Overall Assessment:** The codebase follows Pydantic v2 best practices well. No TypeAdapter anti-patterns found (none used). No excessive `mode='before'` validators (none found). Telemetry schemas correctly use discriminated unions. A few minor `model_dump()` calls could be improved.

---

## Findings

### 1. model_dump() Without mode="json" (Medium)

**Issue:** When serializing to JSON (via `json.dumps()`), `model_dump()` should use `mode="json"` to ensure proper serialization of non-JSON-native types (datetime, Path, Enum, etc.).

#### Finding 1.1

**File:** `/home/emilio/Code/raise-commons/src/rai_cli/cli/commands/discover.py`
**Line:** 137

```python
"symbols": [s.model_dump() for s in result.symbols],
```

**Context:** Used within `json.dumps()` for JSON output format.

**Severity:** Medium

**Suggested Fix:**
```python
"symbols": [s.model_dump(mode="json") for s in result.symbols],
```

#### Finding 1.2

**File:** `/home/emilio/Code/raise-commons/src/rai_cli/cli/commands/discover.py`
**Line:** 487

```python
"warnings": [w.model_dump() for w in warnings],
```

**Context:** Used within `json.dumps()` for JSON output format.

**Severity:** Medium

**Suggested Fix:**
```python
"warnings": [w.model_dump(mode="json") for w in warnings],
```

#### Finding 1.3

**File:** `/home/emilio/Code/raise-commons/src/rai_cli/context/graph.py`
**Line:** 65

```python
self.graph.add_node(node.id, **node.model_dump())
```

**Context:** Unpacking into NetworkX graph node. This case is borderline acceptable since NetworkX can handle Python objects, but using `mode="json"` would ensure consistent serialization.

**Severity:** Low

**Suggested Fix (optional):**
```python
self.graph.add_node(node.id, **node.model_dump(mode="json"))
```

**Note:** Keep without `mode="json"` if NetworkX requires Python objects (e.g., `datetime` instances rather than ISO strings).

---

### 2. TypeAdapter Created Inside Functions (High Priority Pattern)

**Status:** NOT FOUND

No instances of `TypeAdapter` were found in the codebase. This is fine - TypeAdapter is used when you need to validate/serialize types that aren't BaseModel subclasses. The codebase correctly uses BaseModel everywhere.

---

### 3. Excessive mode='before' Validators (High Priority Pattern)

**Status:** NOT FOUND

No `@field_validator` or `@validator` decorators found in the codebase. Validation is handled through:
- Type annotations (implicit coercion)
- Field constraints (`ge=`, `le=`, etc.)
- Literal types for enums

This is actually good practice - simple validation through types rather than custom validators.

---

### 4. BaseModel for Internal-Only Classes (Medium Priority Pattern)

**Status:** PARTIAL CONCERN (Low Severity)

Some classes appear to be internal-only but use BaseModel. However, since most are used for:
- JSONL serialization (memory concepts)
- CLI JSON output
- Graph serialization

Using BaseModel is justified. The deprecated `MemoryGraph` in `memory/builder.py` is already marked for removal.

**Potential candidates for @dataclass conversion (future consideration):**

| File | Class | Justification |
|------|-------|---------------|
| `memory/builder.py` | `MemoryGraph` | Already deprecated, will be removed |

**Not recommended for conversion:** All other BaseModel classes are used at system boundaries (file I/O, CLI output, JSON serialization).

---

### 5. Plain Union Instead of Discriminated Unions (High Priority Pattern)

**Status:** WELL IMPLEMENTED

The telemetry module correctly implements discriminated unions:

**File:** `/home/emilio/Code/raise-commons/src/rai_cli/telemetry/schemas.py`
**Lines:** 278-286

```python
Signal = Annotated[
    SkillEvent
    | SessionEvent
    | CalibrationEvent
    | ErrorEvent
    | CommandUsage
    | WorkLifecycle,
    Field(discriminator="type"),
]
```

Each event type has a `Literal` type field acting as discriminator:
- `SkillEvent.type: Literal["skill_event"]`
- `SessionEvent.type: Literal["session_event"]`
- etc.

This follows the guardrails exactly.

---

## Best Practices Observed

1. **model_validate_json() used correctly:**
   - `MemoryGraph.from_json()` uses `cls.model_validate_json(json_str)`
   - `ContextResult.from_json()` uses `cls.model_validate_json(json_str)`

2. **Proper serialization methods:**
   - `model_dump_json(indent=2)` used for JSON output
   - `mode="json"` used in profile/manifest/memory commands

3. **Specific types over abstractions:**
   - Uses `list[str]`, `dict[str, Any]` consistently
   - No `Sequence`, `Mapping` found

4. **No Union[X, None] anti-pattern:**
   - Uses modern `X | None` syntax throughout

---

## Recommended Actions

### Immediate (Pre-Commit)

1. **Fix discover.py model_dump() calls** (2 instances)
   - Add `mode="json"` to lines 137 and 487

### Consider Later

2. **Review context/graph.py** line 65
   - Test if `mode="json"` is compatible with NetworkX usage

---

## Checklist (from guardrails-stack.md)

- [x] BaseModel only at system boundaries? **YES** (all models serialize/deserialize)
- [x] Validators use mode='after' by default? **N/A** (no custom validators)
- [x] TypeAdapters at module level? **N/A** (none used)
- [x] Discriminated unions for polymorphic types? **YES** (Signal union in telemetry)
- [ ] model_dump(mode="json") when serializing to JSON? **PARTIAL** (2 instances missing)

---

*Generated: 2026-02-05*
*Scanner: Manual grep + read analysis*
