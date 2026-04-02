# RAISE-227 — Scope

WHAT:      `depends_on: []` for 100% of components in C# projects.
           Constructor parameter types (DI) and `using` directives are not extracted.
WHEN:      Any `rai discover scan` on a C# codebase using DI (constructor injection).
WHERE:     `src/raise_cli/discovery/scanner.py` — `_extract_csharp_symbols_from_tree()`
           `src/raise_cli/discovery/analyzer.py` — `build_hierarchy()`
           `src/raise_cli/discovery/scanner.py` — `Symbol` model
EXPECTED:  Class symbols produced from C# files include `depends_on` populated
           from constructor parameter types (and optionally `using` directives).
Done when: `extract_csharp_symbols()` returns class Symbols with `depends_on`
           containing the type names of constructor parameters.
           `build_hierarchy()` passes `depends_on` through to `AnalyzedComponent`.
           Regression tests green.

TRIAGE:
  Bug Type:    Functional
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing
