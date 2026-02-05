# ISSUE-006: Deep Guardrails Audit

> Comprehensive file-by-file review of `src/raise_cli/` against `guardrails-stack.md`
> Date: 2026-02-05
> Methodology: 8 parallel agents reviewing each module

---

## Executive Summary

| Module | Violations | High | Medium | Low |
|--------|------------|------|--------|-----|
| cli/ | 23 | 2 | 9 | 12 |
| core/ | 4 | 0 | 0 | 4 |
| governance/ | 7 | 0 | 4 | 3 |
| context/ | 2 | 0 | 1 | 1 |
| memory/ | 4 | 0 | 2 | 2 |
| onboarding/ | 21 | 0 | 3 | 18 |
| telemetry/ | 2 | 0 | 1 | 1 |
| discovery/ | 6 | 0 | 4 | 2 |
| **TOTAL** | **69** | **2** | **24** | **43** |

**Quality Assessment:** The codebase is fundamentally sound. No critical security vulnerabilities. The 2 High-severity issues are architectural (exit codes, error handling DRY) not functional bugs.

---

## High Priority Fixes (Block F&F if not addressed)

### H1. [CLI 2.3] Generic Exit Code 1 Everywhere (36 occurrences)

**Problem:** All CLI commands use `typer.Exit(1)` regardless of error type. The exception hierarchy with distinct exit codes exists (`exceptions.py`) but is not used.

**Impact:** Scripts and CI/CD pipelines cannot distinguish error types.

**Files affected:**
- `cli/commands/context.py`: 4 occurrences (lines 253, 272, 322, 344)
- `cli/commands/graph.py`: 2 occurrences (lines 61, 309)
- `cli/commands/discover.py`: 2 occurrences (lines 108, 261)
- `cli/commands/memory.py`: 10 occurrences
- `cli/commands/telemetry.py`: 8 occurrences
- `cli/commands/profile.py`: multiple

**Introduced:** Various commits across E2, E9, E11, E13

**Fix:** Create centralized `cli_error()` helper that maps to exception hierarchy exit codes.

```python
# cli/error_handler.py
def cli_error(message: str, error_type: type[RaiseError] = RaiseError, hint: str | None = None) -> NoReturn:
    console.print(f"[red]Error:[/red] {message}")
    if hint:
        console.print(f"[dim]Hint: {hint}[/dim]")
    raise typer.Exit(error_type.exit_code)
```

---

### H2. [CLI 5.1] DRY - Error Pattern Duplicated 30+ Times

**Problem:** Pattern `console.print(f"[red]Error:[/red] ...") + raise typer.Exit(1)` repeated across all command files.

**Files affected:** memory.py (10), telemetry.py (8), context.py (4), graph.py (2), discover.py (6+)

**Fix:** Same as H1 - extract to shared helper.

---

## Medium Priority Fixes (Address before F&F if time permits)

### M1. [CLI 2.5] Fat Commands - Business Logic in Commands

| File | Function | Lines | Issue |
|------|----------|-------|-------|
| `discover.py` | `scan_command` | 165 | Output formatting inline |
| `discover.py` | `drift_command` | 189 | Output formatting inline |
| `graph.py` | `build` | 123 | Caching/serialization inline |
| `context.py` | `query` | 107 | Branch logic for unified vs governance |

**Introduced:** F13.2 (discover), F2.2/F2.3 (graph), F11.3 (context)

**Fix:** Extract formatting to `raise_cli/output/` module. Commands should orchestrate only.

---

### M2. [CLI 2.1] Multiple Positional Arguments

| File | Command | Positionals | Should Be |
|------|---------|-------------|-----------|
| `memory.py:411` | `add-calibration` | 4 (feature, name, size, actual) | 1 + 3 flags |
| `telemetry.py:204` | `emit` | 2 (work_type, work_id) | 1 + 1 flag |

**Introduced:** E9 (F9.4 Session Emitters)

---

### M3. [Governance 5.1] Duplicated `extract_keywords` Function

**Files:**
- `governance/graph/relationships.py:228-276`
- `governance/query/strategies.py:63-100`

**Introduced:** 007cd664 (2026-02-01, F2.2/F2.3)

**Fix:** Extract to `core/text.py` alongside existing `sanitize_id()`.

---

### M4. [Governance 5.1] Duplicated Extract Logic (100+ lines)

**Files:** `governance/extractor.py`
- `extract_all()`: lines 92-194
- `extract_with_result()`: lines 196-297

Nearly identical logic. Only difference is result wrapper.

**Introduced:** 140e6368 (2026-01-31, F2.1)

**Fix:** `extract_all()` should call `extract_with_result().concepts`.

---

### M5. [Governance 5.7] Long Function - query_work_context

**File:** `governance/query/strategies.py:293-406` (113 lines)

Multiple if/elif branches for query patterns.

**Introduced:** 429fb233 (2026-02-02)

**Fix:** Extract helpers: `_query_current_work()`, `_query_epic_features()`, etc.

---

### M6. [Context 5.1] Stopwords Inline in 126-line Function

**File:** `context/builder.py:575-700`

`_extract_keywords()` is 126 lines, with 95 lines being inline stopwords set recreated on every call.

**Introduced:** 1c0fb3f9 (2026-02-03)

**Fix:** Extract `STOPWORDS: frozenset[str]` as module-level constant.

---

### M7. [Memory 5.1] Long Function - validate_session_index

**File:** `memory/writer.py:63-151` (89 lines)

Recent code (2026-02-05), not deprecated.

**Introduced:** 3ff60c6b (2026-02-05, session index validation)

**Fix:** Extract `_parse_jsonl_entries()`, `_find_gaps()`, `_collect_validation_result()`.

---

### M8. [Onboarding 5.1] Duplicated _should_exclude_dir

**Files:**
- `onboarding/detection.py:122-136`
- `onboarding/conventions.py:223-228`

**Introduced:** 48d12e3f, 8a26989e (2026-02-05, F7.1/F7.2)

**Fix:** Extract to `core/files.py`.

---

### M9. [Onboarding 5.1] Long Function - GuardrailGenerator.generate

**File:** `onboarding/governance.py:77-210` (134 lines)

**Introduced:** 261335e0 (2026-02-05, F7.3)

**Fix:** Extract helpers for each guardrail type.

---

### M10. [Onboarding 5.7] Deep Nesting - detect_indentation

**File:** `onboarding/conventions.py:270` - 6 levels deep

**Introduced:** 8a26989e (2026-02-05, F7.2)

**Fix:** Use early returns, extract helpers.

---

### M11. [Telemetry] Type Ignore Suppresses Type Safety

**File:** `telemetry/writer.py:159`

```python
signal = SkillEvent(
    ...
    event=event,  # type: ignore[arg-type]
)
```

**Introduced:** acc99c72 (2026-02-03)

**Fix:** Change `emit_skill_event()` parameter from `str` to `Literal["start", "complete", "abandon"]`.

---

### M12. [Discovery 1.6] Untyped baseline dict

**File:** `discovery/drift.py` - uses `list[dict[str, Any]]` for baseline

**Introduced:** f5d59211 (2026-02-04, F13.5)

**Fix:** Define `BaselineComponent` Pydantic model.

---

### M13. [Discovery 5.1] Long Functions

| File | Function | Lines |
|------|----------|-------|
| `scanner.py:121` | `extract_python_symbols` | 103 |
| `scanner.py:519` | `scan_directory` | 88 |
| `scanner.py:369` | `_extract_ts_js_symbols` | 100 |

**Introduced:** 0bfda5f7 (2026-02-04, F13.2)

---

## Low Priority (Tech Debt - Post F&F)

### L1. [CLI 2.2] Missing --format Option

Commands without format support:
- `profile show` (YAML only)
- `profile session` (text only)
- `status` (text only)
- `telemetry emit-*` (text only)

### L2. [Core 3.4] Path Traversal Prevention

`core/tools.py` functions accept paths without validation. Low risk in CLI context.

### L3. [Governance 1.2] model_post_init vs @field_validator

`governance/models.py:89-101` uses `model_post_init` instead of `@field_validator(mode='after')`.

### L4. [Memory] Deprecated Code

Most memory/ violations are in deprecated code (`MemoryGraph`, `MemoryQuery`). Not worth fixing.

### L5. [Onboarding] Multiple 50-75 Line Functions

10 functions slightly exceed 50-line guideline. Marginal violations.

### L6. [Telemetry 5.1] Signal Union Redeclared

`writer.py:72-79` redeclares Signal union instead of importing from `schemas.py`.

---

## Compliant Areas (No Issues Found)

### Security (All Modules)
- No `eval()`, `exec()`, or `compile()` with user input
- All `subprocess.run()` uses `shell=False`
- All YAML uses `yaml.safe_load()`
- No hardcoded secrets
- No pickle usage

### Pydantic Best Practices
- Discriminated unions used correctly (telemetry `Signal`)
- `model_validate_json()` used where appropriate
- Specific types (`list`, `dict`) used over abstractions
- BaseModel at boundaries (with minor exceptions noted)

### Testing
- >90% coverage maintained
- AAA pattern followed
- Fixtures used appropriately

---

## Traceability Analysis

### When Were Violations Introduced?

| Feature | Date | Violations Introduced |
|---------|------|-----------------------|
| F2.1 Concept Extraction | 2026-01-31 | Exit codes (graph.py), extractor duplication |
| F2.2/F2.3 Graph Builder | 2026-02-01 | extract_keywords duplication, graph.py fat command |
| F9.4 Session Emitters | 2026-02-03 | telemetry positional args, type ignore |
| F11.3 Unified Query | 2026-02-03 | context.py exit codes, query_work_context length |
| F13.2 Extraction Toolkit | 2026-02-04 | discover.py fat commands, scanner.py long functions |
| F7.1-F7.3 Onboarding | 2026-02-05 | _should_exclude_dir duplication, deep nesting |

### Why Were They Introduced?

1. **Exit codes (H1):** Pattern established in F2.1 before exception hierarchy was designed. Copied forward.

2. **Fat commands (M1):** Pragmatic choice during rapid feature development. Formatting was done inline to ship features faster.

3. **Duplications (M3, M4, M8):** Features developed in parallel or by different sessions without cross-checking.

4. **Long functions (M5-M9):** Complex domain logic (parsing, conventions detection) naturally grew. No refactoring pause.

5. **Type ignore (M11):** Quick fix to unblock telemetry implementation.

---

## Recommended Fix Order

### Phase 1: F&F Blocking (Do Now)
1. **H1 + H2:** Create `cli_error()` helper (1-2 hours)
   - Single location for error pattern
   - Maps to exception hierarchy exit codes
   - Update all 36 occurrences

### Phase 2: F&F Polish (If Time)
2. **M11:** Fix type ignore in telemetry (15 min)
3. **M3, M8:** Extract duplicated functions to core/ (30 min each)
4. **M6:** Extract stopwords constant (15 min)

### Phase 3: Post-F&F Refactoring
5. Fat commands (M1) - 2-3 hours
6. Long functions (M5, M7, M9, M13) - 2-3 hours
7. Remaining medium items

---

## Metrics

- **Total files reviewed:** 77 Python files
- **Total violations found:** 69
- **High severity:** 2 (both related to exit code pattern)
- **Medium severity:** 24
- **Low severity:** 43
- **Security vulnerabilities:** 0
- **Review methodology:** Parallel agent review with git blame traceability

---

*Generated: 2026-02-05*
*Reviewed by: 8 parallel Explore agents*
*Guardrails version: 1.0.0*
