---
story: S17.4
title: Analyzer Adjustments for Multi-Language
size: S
complexity: simple
---

# S17.4: Analyzer Adjustments for Multi-Language

## Problem

The analyzer's `DEFAULT_CATEGORY_MAP` and `_file_to_module()` are Python-centric.
Non-Python files get category "other" and broken module paths (e.g., `.py` stripping
doesn't apply to `.php` files).

## Value

Correct categories and module paths for PHP/Svelte/TS symbols enable meaningful
grouping in the analysis output — important for AI synthesis batches and human review.

## Approach

Two changes in `analyzer.py`, no new files:

### 1. Extend `DEFAULT_CATEGORY_MAP` with multi-language conventions

Add Laravel and Svelte/TS path patterns:

```python
DEFAULT_CATEGORY_MAP: dict[str, str] = {
    # Python (existing)
    "cli/commands/": "command",
    "cli/": "utility",
    "schemas/": "schema",
    "models/": "model",
    "output/": "formatter",
    "governance/": "parser",
    "context/": "builder",
    "discovery/": "service",
    "memory/": "service",
    "onboarding/": "service",
    "config/": "utility",
    "core/": "utility",
    "telemetry/": "service",
    # Laravel/PHP
    "Controllers/": "controller",
    "Models/": "model",
    "Middleware/": "middleware",
    "Providers/": "provider",
    "Services/": "service",
    "Requests/": "schema",
    "Resources/": "formatter",
    "routes/": "route",
    "Migrations/": "migration",
    # Svelte/TS/JS
    "components/": "component",
    "stores/": "store",
    "routes/": "route",
    "lib/": "utility",
    "utils/": "utility",
    "types/": "schema",
    "hooks/": "utility",
    "api/": "service",
}
```

Note: `routes/` appears in both Laravel and Svelte — same category "route", no conflict.
Longest-prefix matching ensures `Controllers/` wins over other patterns.

### 2. Generalize `_file_to_module()` for non-Python extensions

Current: strips `src/` and `.py` only.
Fix: strip common source prefixes and any known extension.

```python
_SOURCE_PREFIXES = ("src/", "app/", "lib/")
_CODE_EXTENSIONS = {".py", ".php", ".ts", ".tsx", ".js", ".jsx", ".svelte"}

def _file_to_module(file_path: str) -> str:
    p = PurePosixPath(file_path)
    parts = list(p.parts)
    # Strip common source prefixes
    if parts and parts[0] in ("src", "app", "lib"):
        parts = parts[1:]
    # Remove known extension from last part
    if parts:
        last = PurePosixPath(parts[-1])
        if last.suffix in _CODE_EXTENSIONS:
            parts[-1] = last.stem
    return ".".join(parts)
```

### 3. Formatter — already done

`_format_scan_summary` already counts all SymbolKinds (enum, type_alias, constant,
trait, component) as of S17.1. No changes needed.

## Acceptance Criteria

**MUST:**
- PHP files under `Controllers/` get category "controller", not "other"
- PHP files under `Models/` get category "model"
- Svelte files under `components/` get category "component"
- `_file_to_module("app/Http/Controllers/UserController.php")` → `"Http.Controllers.UserController"`
- `_file_to_module("src/lib/stores/auth.ts")` → `"lib.stores.auth"`
- Existing Python module paths unchanged (regression)

**MUST NOT:**
- Break existing Python analysis
- Change confidence scoring logic
- Modify SymbolKind or scanner code

## Files Affected

| File | Change |
|------|--------|
| `src/raise_cli/discovery/analyzer.py` | Extend category map, generalize `_file_to_module` |
| `tests/test_analyzer.py` | Add tests for new categories and module paths |
