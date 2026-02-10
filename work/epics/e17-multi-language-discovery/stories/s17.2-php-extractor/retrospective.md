# Retrospective: S17.2 — PHP Extractor

## Summary
- **Story:** S17.2
- **Epic:** E17 Multi-Language Discovery
- **Started:** 2026-02-09
- **Completed:** 2026-02-09
- **Estimated:** 60 minutes (M-sized)
- **Actual:** ~25 minutes

## What Went Well
- Pattern established in S17.1 made this story much faster — parser factory, signature extractor, walker, public API, dispatcher is a repeatable template
- TDD caught the blade exclusion need with a precise assertion (files_scanned == 1 vs >= 1)
- Integration test on real zambezi-concierge data: 225 files, 157 symbols — namespaces working correctly
- Emilio's question about blade templates prompted a useful scope discussion (presentation layer topology vs structural code knowledge)

## What Could Improve
- CLI language validation was hardcoded to 3 languages — discovered only during integration test. Plan should have included a "wire CLI" task.
- Could have explored `language_php()` vs `language_php_only()` difference more — both return same capsule but naming suggests different grammars

## Heutagogical Checkpoint

### What did you learn?
- tree-sitter-php API is `language_php()` not `language()` — each grammar has its own naming convention
- PHP tree-sitter uses `name` for identifier nodes (TS uses `identifier`/`type_identifier`)
- PHP `namespace_definition` wraps child declarations in the AST, making namespace state tracking natural
- Blade templates parse without errors in tree-sitter-php but produce no symbols — explicit exclusion is cleaner

### What would you change about the process?
- Add "CLI wiring check" as a standard consideration when planning new scanner capabilities

### Are there improvements for the framework?
- Minor: story-plan for scanner stories could include CLI validation as a checklist item

### What are you more capable of now?
- Repeatable pattern for adding tree-sitter language extractors
- Understanding of PHP AST node types (class_declaration, interface_declaration, trait_declaration, etc.)
- Faster velocity on subsequent language stories (S17.3 Svelte should benefit)

## Improvements Applied
- PAT-232: tree-sitter grammar API naming conventions
- PAT-233: Wire both domain layer and CLI layer when extending scanner

## Action Items
- None — all learnings captured in patterns
