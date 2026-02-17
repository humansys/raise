## Story Scope: RAISE-158

**Epic:** RAISE-144 (Engineering Health)
**Size:** S
**Priority:** P0
**Context:** Kurigage Track 1 — Sofi's team works with .NET/C# APIs

**In Scope:**
- Add C#/.NET scanner using tree-sitter-c-sharp
- Extract: classes, interfaces, structs, enums, methods, functions, records, properties
- Namespace-qualified names (same pattern as PHP)
- Wire into `extract_symbols` dispatcher, `Language` literal, extension map
- Tests following existing patterns (unit + scan_directory integration)

**Out of Scope:**
- Razor/Blazor template parsing (.cshtml, .razor)
- NuGet dependency analysis
- Cross-language reference tracking
- F# support

**Done Criteria:**
- [ ] `extract_csharp_symbols()` extracts all C# symbol types
- [ ] `detect_language("foo.cs")` returns "csharp"
- [ ] `scan_directory(path, language="csharp")` works end-to-end
- [ ] All tests pass (new + existing)
- [ ] Type checks pass (pyright)
- [ ] Linting passes (ruff)
- [ ] Retrospective complete
