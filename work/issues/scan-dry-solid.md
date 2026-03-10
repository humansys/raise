# DRY/SOLID Scan Results

> Scan of `src/rai_cli/` against guardrails-stack.md section 5 (DRY/SOLID)
> Date: 2026-02-05

---

## Summary

| Finding Type | Count | High | Medium | Low |
|-------------|-------|------|--------|-----|
| Functions > 50 lines | 8 | 5 | 3 | 0 |
| Duplicated patterns (3+) | 3 | 1 | 2 | 0 |
| God classes | 0 | 0 | 0 | 0 |
| Deep nesting (>3 levels) | 2 | 0 | 2 | 0 |
| Long parameter lists (>5) | 0 | 0 | 0 | 0 |

**Total Findings: 13**

---

## 1. Functions Longer Than 50 Lines

### HIGH Severity

| File:Line | Function | Lines | Description |
|-----------|----------|-------|-------------|
| `cli/commands/discover.py:36` | `scan_command()` | 164 | CLI command with all output formatting inline |
| `cli/commands/discover.py:203` | `build_command()` | 149 | CLI command with all output formatting inline |
| `cli/commands/discover.py:353` | `drift_command()` | 188 | CLI command with all output formatting inline |
| `cli/commands/graph.py:157` | `build()` | 125 | Graph building with inline concept reconstruction |
| `cli/commands/telemetry.py:201` | `emit_work()` | 129 | Validation and output formatting inline |

**Suggested Fix:**
- Extract output formatting to separate functions (e.g., `_format_scan_human()`, `_format_scan_json()`)
- Extract validation logic to helper functions
- Follow guardrail 2.5 "Thin Commands": Commands should orchestrate, not contain logic

### MEDIUM Severity

| File:Line | Function | Lines | Lines |
|-----------|----------|-------|-------|
| `cli/commands/context.py:125` | `query()` | 107 | Branches for unified vs governance query |
| `memory/query.py:280` | `search()` | 69 | Multiple responsibilities in single method |
| `onboarding/conventions.py:270` | `detect_indentation()` | 75 | File reading + parsing + analysis combined |

**Suggested Fix:**
- Split into smaller focused functions
- Extract file reading, parsing, and analysis into separate steps

---

## 2. Duplicated Code Patterns (Rule of Three Candidates)

### HIGH Severity

#### Error Handling Pattern (24 occurrences)

The pattern `console.print(f"[red]Error:[/red] ...")` followed by `rai typer.Exit(1)` appears in:

| File | Occurrences |
|------|-------------|
| `cli/commands/telemetry.py` | 8 |
| `cli/commands/memory.py` | 10 |
| `cli/commands/context.py` | 4 |
| `cli/commands/graph.py` | 2 |

**Affected Files:**
- `/home/emilio/Code/raise-commons/src/rai_cli/cli/commands/telemetry.py:79,107,153,160,163,196,261,274,286,328`
- `/home/emilio/Code/raise-commons/src/rai_cli/cli/commands/memory.py:126,216,374,384,405,450,456,483,521,545`
- `/home/emilio/Code/raise-commons/src/rai_cli/cli/commands/context.py:249,268,320,339`
- `/home/emilio/Code/raise-commons/src/rai_cli/cli/commands/graph.py:60,307`

**Suggested Fix:**
Create a helper function in `cli/error_handler.py` or use the existing error handling pattern:

```python
def exit_with_error(message: str, hint: str | None = None) -> NoReturn:
    """Print error message and exit with code 1."""
    console.print(f"[red]Error:[/red] {message}")
    if hint:
        console.print(f"[dim]Hint: {hint}[/dim]")
    raise typer.Exit(1)
```

### MEDIUM Severity

#### Validation Pattern for Literal Types (6 occurrences)

Pattern of validating string against list of valid values:

| File:Line | Context |
|-----------|---------|
| `cli/commands/telemetry.py:72-81` | `outcome` validation |
| `cli/commands/telemetry.py:149-155` | `size` validation |
| `cli/commands/telemetry.py:257-263` | `work_type` validation |
| `cli/commands/telemetry.py:266-276` | `event_type` validation |
| `cli/commands/telemetry.py:279-288` | `phase` validation |
| `cli/commands/memory.py:453-458` | `size` validation |

**Suggested Fix:**
Create a reusable validator:

```python
def validate_literal(
    value: str,
    valid_values: list[str],
    param_name: str,
) -> None:
    """Validate value is in list of valid options."""
    if value not in valid_values:
        console.print(f"[red]Error:[/red] Invalid {param_name}: {value}")
        console.print(f"Valid {param_name}s: {', '.join(valid_values)}")
        raise typer.Exit(1)
```

#### Output Format Branching (5 occurrences)

Pattern of `if format == "json": ... elif format == "summary": ... else: ...`:

| File:Line | Command |
|-----------|---------|
| `cli/commands/discover.py:133-199` | `scan_command` |
| `cli/commands/discover.py:295-349` | `build_command` |
| `cli/commands/discover.py:483-537` | `drift_command` |
| `cli/commands/memory.py:151-163` | `query` |
| `cli/commands/memory.py:236-258` | `list_memory` |

**Suggested Fix:**
Consider a formatter abstraction or use existing `OutputFormat` enum with formatter dispatch:

```python
def format_output(data: Any, format: OutputFormat) -> str:
    """Format data according to output format."""
    formatters = {
        OutputFormat.json: format_json,
        OutputFormat.human: format_human,
        OutputFormat.table: format_table,
    }
    return formatters[format](data)
```

---

## 3. God Classes

**No god classes detected.**

All classes have focused responsibilities:
- Model classes (Pydantic BaseModel) are data containers
- Query engines have single purpose (MemoryQuery, UnifiedQueryEngine)
- Builders have single purpose (GraphBuilder, UnifiedGraphBuilder)

---

## 4. Deep Nesting (>3 levels)

### MEDIUM Severity

| File:Line | Function | Max Depth | Description |
|-----------|----------|-----------|-------------|
| `memory/writer.py:95-120` | `validate_session_index()` | 4 | Loop > try > if > if |
| `onboarding/conventions.py:246-259` | `collect_python_files._collect()` | 4 | Function > for > if > if |

**Example from `memory/writer.py:95-120`:**
```python
with file_path.open("r", encoding="utf-8") as f:      # Level 1
    for line in f:                                      # Level 2
        try:                                            # Level 3
            data = json.loads(line)
            if entry_id is None:                        # Level 4
                entries_without_id += 1
```

**Suggested Fix:**
Extract inner logic to helper function:

```python
def _parse_session_entry(line: str) -> ParsedEntry:
    """Parse a single session entry line."""
    data = json.loads(line)
    entry_id = data.get("id")
    ...
```

---

## 5. Long Parameter Lists (>5 params)

**No functions with >5 parameters detected.**

The codebase follows good practices using:
- Pydantic models for grouped parameters (e.g., `PatternInput`, `CalibrationInput`)
- Typer Options with defaults rather than long positional parameter lists
- Builder patterns where multiple configuration is needed

---

## Recommendations

### Priority 1 (Address Before Release)

1. **Create `exit_with_error()` helper** - Single location for error exit pattern
   - Reduces 24 duplicated patterns to 1
   - Improves consistency of error messages
   - Enables future enhancement (e.g., logging)

2. **Extract output formatters from discover.py commands**
   - `scan_command()`: 164 lines -> ~50 lines + formatters
   - `build_command()`: 149 lines -> ~50 lines + formatters
   - `drift_command()`: 188 lines -> ~50 lines + formatters

### Priority 2 (Post-Release Refactoring)

3. **Create `validate_literal()` helper** - Reduces 6 validation patterns
4. **Refactor `detect_indentation()` in conventions.py** - Separate file I/O from analysis
5. **Flatten deep nesting in `validate_session_index()`** - Extract entry parsing

### Not Recommended

- **Do NOT abstract output format branching yet** - Only 5 occurrences, each with different data types. Per guardrail 5.2 "Semantic Over Syntactic Duplication", these look similar but serve different purposes.

---

## Guardrail Compliance Summary

| Guardrail | Status | Notes |
|-----------|--------|-------|
| 5.1 Rule of Three | PARTIAL | Error handling pattern has 24 occurrences (extract) |
| 5.2 Semantic Duplication | GOOD | Validation patterns are true duplication |
| 5.3 Composition Over Inheritance | GOOD | No deep inheritance hierarchies found |
| 5.4 Protocols Over ABCs | N/A | No ABCs used |
| 5.5 Simple DI | GOOD | Constructor injection, no frameworks |
| 5.6 Functions Are Fine | GOOD | Functions used appropriately |
| 5.7 Wrong Abstraction Debt | GOOD | No if/elif chains for "type" branching |

---

*Scanned: 77 Python files in src/rai_cli/*
*Tool: Manual analysis with Grep/Read*
