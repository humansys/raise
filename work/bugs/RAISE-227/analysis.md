# RAISE-227 — Analysis

## 5 Whys

| Step | Why | Evidence |
|------|-----|----------|
| Symptom | `depends_on: []` for all C# components | Reported in BetterNet.Services.Profile |
| Why 1 | `build_hierarchy()` never populates `AnalyzedComponent.depends_on` | analyzer.py:518-535 — field not set |
| Why 2 | `Symbol` has no `depends_on` field — no data to pass through | scanner.py:63-93 — missing field |
| Why 3 | `_extract_csharp_symbols_from_tree` doesn't extract constructor params | scanner.py:1128-1216 — no `constructor_declaration` branch |
| Why 4 | C# walker only handles class/interface/method/property/enum | Same — container_types set is exhaustive |
| Root cause | Missing extraction + missing field — `constructor_declaration` nodes are silently skipped, and even if extracted there's nowhere to store them |

## Confirmed Root Cause

`_extract_csharp_symbols_from_tree` does not visit `constructor_declaration` nodes.
`Symbol` has no `depends_on` field to carry dependency data from scanner to analyzer.
`build_hierarchy` has no mechanism to populate `AnalyzedComponent.depends_on`.

## Fix Approach

1. Add `depends_on: list[str] = Field(default_factory=list)` to `Symbol`
2. In `_extract_csharp_symbols_from_tree`: when building a class symbol, pre-scan the body
   for `constructor_declaration` → collect parameter type names → set on Symbol
3. Add helper `_extract_constructor_deps(body, source) -> list[str]` for the pre-scan
4. In `build_hierarchy` (analyzer.py): pass `symbol.depends_on` to `AnalyzedComponent`
5. `using` directives: out of scope for this fix (file-level, less actionable for DI graph)

## Scope Decision

Scoped to **constructor parameter types only**. `using` statements are namespace imports,
not component-level dependencies — they would require a separate mapping strategy.
