---
story: RAISE-160
title: Flutter/Dart discovery scanner
size: S
module: mod-discovery
layer: lyr-domain
---

## What & Why

**Problem:** `rai discover scan` cannot parse `.dart` files. Kurigage Track 2 is a Flutter mobile app — without Dart support, the knowledge graph misses the entire codebase.

**Value:** Dart symbols (classes, mixins, extensions, enums, functions) appear in the graph, enabling governance and context queries for Flutter projects.

## Approach

Follow the exact C#/PHP scanner pattern: tree-sitter parser → AST walk → Symbol extraction.

**Dependency decision:** No standalone `tree-sitter-dart` exists on PyPI. Use `tree-sitter-language-pack` which bundles 160+ grammars including Dart. API: `get_parser("dart")` returns a `tree_sitter.Parser`.

**Components affected:**

| Component | Change | Detail |
|-----------|--------|--------|
| `pyproject.toml` | modify | Add `tree-sitter-language-pack` dependency |
| `scanner.py` — types | modify | Add `"dart"` to `Language`, `EXTENSION_TO_LANGUAGE`, `DEFAULT_LANGUAGE_PATTERNS` |
| `scanner.py` — parser | create | `_get_dart_parser()`, `_extract_dart_signature()`, `_extract_dart_symbols_from_tree()`, `extract_dart_symbols()` |
| `scanner.py` — dispatch | modify | Add `"dart"` case in `extract_symbols()` |
| `tests/discovery/test_scanner_dart.py` | create | Tests for all Dart symbol types |

## Dart Symbol Mapping

| Dart Construct | tree-sitter node type | SymbolKind |
|---------------|----------------------|------------|
| class | `class_definition` | `"class"` |
| mixin | `mixin_declaration` | `"trait"` |
| extension | `extension_declaration` | `"class"` |
| enum | `enum_declaration` | `"enum"` |
| top-level function | `function_signature` in `program` | `"function"` |
| method | `method_signature` inside class/mixin | `"method"` |

**IMPORTANT:** Dart `mixin` maps to `"trait"` (already in SymbolKind). Extensions map to `"class"` since SymbolKind has no `"extension"` variant and adding one is out of scope.

## Examples

### Parser function
```python
def _get_dart_parser() -> Parser:
    from tree_sitter_language_pack import get_parser
    return get_parser("dart")
```

### Extract usage
```python
>>> source = '''
... class UserService {
...   void process() {}
... }
... mixin Loggable {
...   void log(String msg) {}
... }
... enum Status { active, inactive }
... void main() {}
... '''
>>> symbols = extract_dart_symbols(source, "lib/user_service.dart")
>>> [(s.name, s.kind) for s in symbols]
[('UserService', 'class'), ('process', 'method'), ('Loggable', 'trait'), ('log', 'method'), ('Status', 'enum'), ('main', 'function')]
```

### Language detection
```python
>>> detect_language("lib/main.dart")
'dart'
```

## Acceptance Criteria

**MUST:**
- `"dart"` in `Language` type, extension map, and glob patterns
- `extract_dart_symbols()` extracts classes, mixins, extensions, enums, top-level functions, methods
- Methods have `parent` set to containing class/mixin
- `extract_symbols(source, path, "dart")` dispatches correctly
- Tests cover each symbol type with representative Flutter code

**SHOULD:**
- Handle `abstract class`, `sealed class` modifiers
- Handle `extension type` declarations (Dart 3)

**MUST NOT:**
- Add `"extension"` to SymbolKind (use `"class"`)
- Pull in grammar-specific dependencies beyond `tree-sitter-language-pack`

## Notes

- The `tree-sitter-language-pack` uses `get_parser("dart")` instead of the manual `Language(grammar.language())` pattern used by other scanners. The `_get_dart_parser()` function encapsulates this difference.
- Dart AST node types need verification against the actual grammar at implementation time. The tree-sitter-dart grammar is from `UserNobody14/tree-sitter-dart`.
