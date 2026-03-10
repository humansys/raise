# Retrospective: S17.3 — Svelte Extractor

## Summary
- **Story:** S17.3
- **Size:** S
- **Tasks:** 3 (M + S + XS)
- **Commits:** 3 (scope, core+tests, integration test)

## What Went Well
- Two-pass approach (Svelte parser → JS/TS parser) worked cleanly on first implementation
- S17.2 (PHP) established the pattern — S17.3 followed naturally with the added twist of two-pass parsing
- Line offset calculation was correct on first try (raw_text node's start_point gave exact offset)
- All 9 Svelte tests passed on first GREEN
- Infrastructure (Language type, EXTENSION_TO_LANGUAGE, DEFAULT_LANGUAGE_PATTERNS) was already wired from prior stories — zero friction for scan_directory

## What Could Improve
- Initial design included `_extract_svelte_script_info()` helper that was never called — pyright caught it. Could have designed more carefully before coding, but the cleanup was trivial.

## Heutagogical Checkpoint

### What did you learn?
- tree-sitter-svelte treats `<script>` content as opaque `raw_text` — it doesn't inject a JS/TS sublanguage. This means any embedded-language parser needs a two-pass approach.
- tree-sitter-svelte API is `language()` (not `language_svelte()` like PHP's `language_php()`). Each tree-sitter binding has its own naming convention.
- `raw_text` node's `start_point[0]` gives the exact 0-indexed line for offset correction.

### What would you change about the process?
- Nothing significant. Story was well-scoped, design was clear, implementation was fast.

### Are there improvements for the framework?
- No framework changes needed.

### What are you more capable of now?
- Two-pass tree-sitter extraction pattern — applicable to any embedded-language file format (Vue SFC, Astro, etc.)

## Improvements Applied
- None needed.

## Patterns
- Two-pass tree-sitter pattern for embedded languages is reusable (Vue, Astro, etc.)
