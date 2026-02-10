---
type: module
name: discovery
purpose: "Scan codebases to extract structural knowledge — symbols, components, modules, and drift detection"
status: current
depends_on: []
depended_by: [cli]
entry_points:
  - "raise discover scan"
  - "raise discover analyze"
  - "raise discover drift"
  - "raise discover build"
public_api:
  - "DriftSeverity"
  - "DriftWarning"
  - "EXTENSION_TO_LANGUAGE"
  - "Language"
  - "ScanResult"
  - "Symbol"
  - "SymbolKind"
  - "detect_drift"
  - "detect_language"
  - "extract_javascript_symbols"
  - "extract_python_symbols"
  - "extract_symbols"
  - "extract_typescript_symbols"
  - "scan_directory"
components: 45
constraints:
  - "Independent of governance module — no cross-imports"
  - "All analysis is deterministic — no AI inference in CLI"
  - "Scanner uses Python AST for Python files, tree-sitter for TS/TSX/JS"
---

## Purpose

The discovery module answers "what exists in this codebase and how is it organized?" It scans source code to extract symbols (classes, functions, methods), groups them into components, assigns confidence scores, and detects structural drift over time. The output feeds into the unified context graph and the architecture documentation.

This is the **code understanding** layer — while governance extracts knowledge from documentation, discovery extracts knowledge from code itself.

## Architecture

The module follows a pipeline architecture where each stage refines the previous output:

```
Source code → Scanner → raw symbols (551 for raise-commons)
                ↓
           Analyzer → components with confidence + module grouping (309)
                ↓
         Drift Detector → warnings if structure changed since baseline
```

## Key Files

- **`scanner.py`** — Symbol extraction using Python's `ast` module (Python) and tree-sitter (TypeScript, TSX, JavaScript, PHP). Language detection via file extension. Returns `ScanResult` with typed `Symbol` objects including kind (class/function/method/enum/type_alias/constant/interface/trait), line numbers, and parent relationships. PHP extraction includes namespace-qualified names.
- **`analyzer.py`** — Groups symbols into components, assigns confidence tiers (high/medium/low), categorizes by module path. Produces `AnalysisResult` with module-level grouping. 99% test coverage, 79 tests.
- **`drift.py`** — Compares current scan against a saved baseline. Detects added, removed, and moved components. Returns `DriftWarning` objects with severity levels.

## Dependencies

Leaf module. Uses Python stdlib (`ast`, `pathlib`), `tree-sitter-typescript` for TS/TSX, and `tree-sitter-php` for PHP parsing.

## Conventions

- All public functions return Pydantic models, not raw dicts
- Scanner output is language-agnostic (the `Symbol` model works for all languages)
- Analyzer categories are path-based and configurable
- Drift detection requires a baseline file (`work/discovery/baseline.json`)
