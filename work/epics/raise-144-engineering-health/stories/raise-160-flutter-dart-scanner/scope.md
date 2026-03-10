## Feature Scope: RAISE-160

**Story:** Flutter/Dart discovery scanner
**Epic:** RAISE-144 (Engineering Health)
**Size:** S
**Branch:** v2 (branchless, S-sized rolling epic story)

**In Scope:**
- Add tree-sitter-dart dependency
- Implement `extract_dart_symbols()` following existing parser pattern (PHP, C#)
- Extract: classes, mixins, extensions, enums, top-level functions
- Add `"dart"` to `Language` Literal type
- Wire `.dart` extension in scanner file mapping
- Tests with representative Flutter code samples

**Out of Scope:**
- Flutter widget analysis / build method parsing
- Dart package resolution
- Dart-specific governance rules
- tree-sitter-dart grammar authoring (use existing)

**Done Criteria:**
- [ ] `rai discover scan` extracts Dart symbols from .dart files
- [ ] Language type includes "dart"
- [ ] Tests cover classes, mixins, extensions, enums, top-level functions
- [ ] All tests pass (2021+)
- [ ] Retrospective complete
