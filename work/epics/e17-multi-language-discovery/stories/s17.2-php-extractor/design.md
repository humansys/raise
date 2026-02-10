# Design: S17.2 — PHP Extractor

## What & Why

**Problem:** `raise discover scan` cannot extract symbols from PHP files. zambezi-concierge has 37 PHP files in admin/app/ (Laravel + Filament) that are invisible to discovery.

**Value:** Enables discovery on PHP codebases and the PHP portion of polyglot repos like zambezi-concierge.

## Architectural Context

- **Module:** mod-discovery (domain layer, leaf)
- **Pattern:** Same tree-sitter walker pattern as TS/JS (PAT-066)
- **Constraint:** All analysis is deterministic — no AI inference in scanner

## Approach

Add `extract_php_symbols()` following the same structure as `extract_typescript_symbols()`:

1. **`_get_php_parser()`** — Create parser with `tree_sitter_php.language_php()`
2. **`_extract_php_signature()`** — Build signatures from PHP AST nodes
3. **`_extract_php_symbols()`** — Walk AST, extract symbols with parent tracking
4. **`extract_php_symbols()`** — Public API, parse source and delegate to walker
5. **Wire into `extract_symbols()`** — Add `"php"` case to dispatcher

### PHP tree-sitter Node Types

From exploration of `tree-sitter-php` v0.24.1:

| PHP Construct | tree-sitter Node Type | SymbolKind |
|---------------|----------------------|------------|
| `class Foo extends Bar implements Baz` | `class_declaration` | `"class"` |
| `interface Foo` | `interface_declaration` | `"interface"` |
| `trait Foo` | `trait_declaration` | `"trait"` |
| `function foo()` | `function_definition` | `"function"` |
| `public function foo()` (in class/interface/trait) | `method_declaration` | `"method"` |
| `enum Status: string` | `enum_declaration` | `"enum"` |
| `namespace App\Models` | `namespace_definition` | (used for qualified names, not extracted as symbol) |

**IMPORTANT:** PHP API is `language_php()` not `language()`. Also has `language_php_only()` (same capsule). Use `language_php()`.

### Name Extraction

- Name child node type is `name` (not `identifier` like in TS)
- Namespace extracted from `namespace_definition` → `namespace_name` for qualified names
- Signature includes `extends`/`implements` for classes, `formal_parameters` + return type for functions/methods
- Visibility from `visibility_modifier` child on methods

### Namespace Handling

PHP namespaces (`namespace App\Models;`) set the qualified prefix for all subsequent declarations in that file. Track namespace as state while walking:

```python
namespace = ""  # Set from namespace_definition
# Then: symbol.name = f"{namespace}\\{local_name}" if namespace else local_name
```

## Examples

### Input
```php
<?php
namespace App\Models;

class User extends Model implements Configurable {
    use HasSlug;

    public function getName(): string {
        return $this->name;
    }
}

function helper(int $x): int {
    return $x * 2;
}

enum Status: string {
    case Active = 'active';
}
```

### Expected Output
```python
[
    Symbol(kind="class", name="App\\Models\\User", file="User.php", line=4,
           signature="class User extends Model implements Configurable"),
    Symbol(kind="method", name="getName", file="User.php", line=7,
           parent="App\\Models\\User", signature="public function getName(): string"),
    Symbol(kind="function", name="App\\Models\\helper", file="User.php", line=12,
           signature="function helper(int $x): int"),
    Symbol(kind="enum", name="App\\Models\\Status", file="User.php", line=16,
           signature="enum Status: string"),
]
```

## Acceptance Criteria

**MUST:**
- Extract classes, functions, methods, interfaces, traits, enums from PHP source
- Handle PHP namespaces for qualified symbol names
- Wire `extract_php_symbols` into `extract_symbols()` dispatcher
- `scan_directory(path, language="php")` finds and parses `.php` files
- Signature extraction for all PHP symbol kinds
- All tests pass, ruff clean, pyright clean

**SHOULD:**
- Handle visibility modifiers (public/private/protected) in method signatures
- Handle static methods in signatures
- Handle `extends` and `implements` in class signatures

**MUST NOT:**
- Parse Blade templates (`.blade.php`) — explicitly skip
- Add Laravel-specific category logic (that's S17.4)
