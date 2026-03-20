# RAISE-594: Plan — CLI Extension Mechanism

**Story:** RAISE-594 | **Size:** XS | **Date:** 2026-03-20
**Design:** `work/stories/raise-594-design.md`

## Tasks

### T1: ExtensionInfo dataclass + discover function skeleton (S)

**Files:** `src/raise_cli/cli/extensions.py` (create), `tests/cli/test_extensions.py` (create)

**TDD cycle:**
- RED: Test that `discover_cli_extensions(app)` with a valid entry point registers it and returns `ExtensionInfo(status="loaded")`
- RED: Test that a broken entry point (ImportError) is skipped and returns `ExtensionInfo(status="error")` with reason
- GREEN: Implement `ExtensionInfo` dataclass, `_dist_name` helper, `discover_cli_extensions` with load + `isinstance(Typer)` check
- REFACTOR: Ensure logging matches project idiom (warning on skip, debug on success)

**Verification:**
```bash
uv run pytest --tb=short
uv run pyright
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/
```

**AC:** AC1, AC3, AC6, AC7
**Dependencies:** None

---

### T2: Collision and duplicate protection (S)

**Files:** `src/raise_cli/cli/extensions.py` (modify), `tests/cli/test_extensions.py` (modify)

**TDD cycle:**
- RED: Test that extension named `"session"` (built-in) is rejected with `status="skipped"` and reason mentions "built-in"
- RED: Test that second extension with same name is rejected with `status="skipped"` and reason mentions "duplicate"
- GREEN: Add `BUILTIN_COMMANDS` frozenset + collision check, add `registered` dict + duplicate check
- REFACTOR: Verify warning messages are informative (include dist name)

**Verification:**
```bash
uv run pytest --tb=short
uv run pyright
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/
```

**AC:** AC4, AC5
**Dependencies:** T1

---

### T3: Wire into main.py + integration test (XS)

**Files:** `src/raise_cli/cli/main.py` (modify), `tests/cli/test_extensions.py` (modify)

**TDD cycle:**
- RED: Test that `rai --help` works with no extensions installed (no-op, existing commands intact)
- GREEN: Add import + `discover_cli_extensions(app)` call after standalone commands in `main.py`
- REFACTOR: Verify placement is clean (after line 77, before `console = Console()`)

**Manual integration test:**
```bash
uv run rai --help  # All built-in commands present, no errors
uv run rai info    # Existing command still works
```

**Verification:**
```bash
uv run pytest --tb=short
uv run pyright
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/
```

**AC:** AC1, AC2 (partial — full verification needs installed extension)
**Dependencies:** T1, T2

---

## Execution Order

```
T1 (skeleton + core tests) → T2 (protections) → T3 (wire + integration)
```

**Rationale:** Risk-first — T1 validates the core mechanism works. T2 adds safety. T3 is the low-risk wiring that activates everything.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `entry_points()` behaves differently across Python versions | Tests pass locally but fail in CI | Test with mocked `entry_points` — no real package needed |
| `BUILTIN_COMMANDS` drifts as new commands are added | New built-in could be shadowed | Accept: low frequency, easy to update. Future: derive from `app.registered_groups` |
| `from __future__ import annotations` masking NameError (PAT-E-597) | Silent failures | Verify runtime imports in T1 tests |

## Duration Tracking

| Task | Estimated | Actual | Status |
|---|---|---|---|
| T1 | 10 min | — | pending |
| T2 | 8 min | — | pending |
| T3 | 5 min | — | pending |
| **Total** | **23 min** | — | — |
