---
story_id: RAISE-158
title: "C#/.NET Discovery Scanner"
size: S
module: mod-discovery
domain: bc-discovery
layer: lyr-domain
---

## What & Why

**Problem:** Sofi's team at Kurigage uses .NET/C# for APIs and Windows Forms desktop apps. Discovery can't scan their codebase — blocks Track 1 brownfield onboarding.

**Value:** Enables `rai discover scan` on C#/.NET projects, completing multi-language coverage for Kurigage's tech stack.

## Approach

Add C# scanner following the established tree-sitter pattern (identical to PHP scanner). The `tree-sitter-c-sharp` package (v0.23.1, PyPI) provides the grammar.

**Components affected:**

| File | Change | What |
|------|--------|------|
| `src/rai_cli/discovery/scanner.py` | Modify | Add C# parser, extractor, wire into dispatcher |
| `src/rai_cli/cli/commands/discover.py` | Modify | Add "csharp" to language validation (L109) |
| `tests/discovery/test_scanner.py` | Modify | Add `TestExtractCsharpSymbols` class |
| `pyproject.toml` | Modify | Add `tree-sitter-c-sharp` optional dependency |

**Wiring points (PAT-E-233):**
1. `Language` literal — add `"csharp"`
2. `EXTENSION_TO_LANGUAGE` — `.cs` → `"csharp"`
3. `DEFAULT_LANGUAGE_PATTERNS` — `"csharp": ["**/*.cs"]`
4. `DEFAULT_EXCLUDE_PATTERNS` — add `"**/*.Designer.cs"`
5. `extract_symbols()` dispatcher — add `elif language == "csharp"`
6. `discover.py` CLI validation — add `"csharp"` to valid languages + help text

## C# Symbol Types to Extract

| C# Construct | SymbolKind | tree-sitter node type |
|--------------|------------|----------------------|
| `class` | `"class"` | `class_declaration` |
| `interface` | `"interface"` | `interface_declaration` |
| `struct` | `"class"` | `struct_declaration` |
| `record` | `"class"` | `record_declaration` |
| `enum` | `"enum"` | `enum_declaration` |
| `method` | `"method"` | `method_declaration` |
| `function` (top-level) | `"function"` | `local_function_statement` (C# 9+) |
| `property` | `"method"` | `property_declaration` |

**Notes:**
- Structs and records map to `"class"` kind (same semantic role for discovery)
- Properties map to `"method"` kind (they have accessors, relevant for API surface)
- Namespace tracking follows PHP pattern (`_qualify()` helper)

## Examples

### Input
```csharp
using System;

namespace MyApp.Services
{
    public interface IUserService
    {
        Task<User> GetUserAsync(int id);
    }

    public class UserService : IUserService
    {
        public string ConnectionString { get; set; }

        public async Task<User> GetUserAsync(int id)
        {
            return await _repo.FindAsync(id);
        }

        private void ValidateId(int id) { }
    }

    public enum UserRole
    {
        Admin,
        User,
        Guest
    }

    public record UserDto(string Name, string Email);

    public struct Point
    {
        public int X { get; set; }
        public int Y { get; set; }
    }
}
```

### Expected Output
```python
[
    Symbol(name="MyApp.Services.IUserService", kind="interface", file="UserService.cs", line=5, signature="interface IUserService"),
    Symbol(name="GetUserAsync", kind="method", file="UserService.cs", line=7, parent="MyApp.Services.IUserService"),
    Symbol(name="MyApp.Services.UserService", kind="class", file="UserService.cs", line=10, signature="class UserService : IUserService"),
    Symbol(name="ConnectionString", kind="method", file="UserService.cs", line=12, parent="MyApp.Services.UserService"),
    Symbol(name="GetUserAsync", kind="method", file="UserService.cs", line=14, parent="MyApp.Services.UserService"),
    Symbol(name="ValidateId", kind="method", file="UserService.cs", line=19, parent="MyApp.Services.UserService"),
    Symbol(name="MyApp.Services.UserRole", kind="enum", file="UserService.cs", line=22, signature="enum UserRole"),
    Symbol(name="MyApp.Services.UserDto", kind="class", file="UserService.cs", line=29, signature="record UserDto"),
    Symbol(name="MyApp.Services.Point", kind="class", file="UserService.cs", line=31, signature="struct Point"),
]
```

### CLI Usage
```bash
rai discover scan ./src --language csharp
rai discover scan ./src --language csharp --output json
```

### Designer.cs Exclusion
```bash
# This should NOT be scanned
# Form1.Designer.cs — auto-generated WinForms boilerplate
rai discover scan . --language csharp
# → Form1.Designer.cs excluded by DEFAULT_EXCLUDE_PATTERNS
```

## Acceptance Criteria

**MUST:**
- [ ] `extract_csharp_symbols()` extracts classes, interfaces, structs, records, enums, methods, properties
- [ ] Namespace-qualified names (e.g., `MyApp.Services.UserService`)
- [ ] `detect_language("foo.cs")` returns `"csharp"`
- [ ] `scan_directory(path, language="csharp")` works end-to-end
- [ ] `*.Designer.cs` excluded from default scan
- [ ] CLI `--language csharp` works

**SHOULD:**
- [ ] Visibility modifiers in method signatures (`public`, `private`, etc.)
- [ ] Inheritance info in class signatures (`class Foo : Bar, IBaz`)

**MUST NOT:**
- [ ] Break existing scanner tests
- [ ] Add C# as a required dependency (keep as optional, like other tree-sitter grammars)
