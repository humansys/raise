# RAISE-227 — Plan

## Tasks

### T1 — Regression test [RED]
Write test: `extract_csharp_symbols()` on a class with constructor injection returns
`depends_on` populated with injected type names.
Verify: test fails (Symbol has no `depends_on` field).
Commit: `test(RAISE-227): regression — C# constructor deps not extracted [RED]`

### T2 — Add `depends_on` to Symbol [GREEN]
Add `depends_on: list[str] = Field(default_factory=list)` to `Symbol` model.
Verify: test still fails (field exists but not populated).
Commit: `feat(RAISE-227): add depends_on field to Symbol model`

### T3 — Extract constructor deps in C# walker [GREEN]
Add `_extract_constructor_deps(body: Node, source: bytes) -> list[str]` helper.
Modify class branch in `_extract_csharp_symbols_from_tree` to pre-scan body for
`constructor_declaration` → extract `parameter` type nodes → populate `depends_on`.
Verify: T1 regression test passes.
Commit: `fix(RAISE-227): extract constructor param types in C# scanner [GREEN]`

### T4 — Pass depends_on through build_hierarchy [GREEN]
In `build_hierarchy` (analyzer.py): set `depends_on=symbol.depends_on` when creating
class `AnalyzedComponent`.
Verify: all tests pass — uv run pytest --tb=short, ruff check, pyright.
Commit: `fix(RAISE-227): pass depends_on through build_hierarchy to AnalyzedComponent`

## Verification
- `uv run pytest --tb=short`
- `uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/`
- `uv run pyright`
