## Story Scope: S17.3 — Svelte Extractor

**Size:** S
**Epic:** E17 (Multi-Language Discovery)
**Branch:** epic/e17/multi-language-discovery (S-sized, no story branch)

**In Scope:**
- tree-sitter-svelte extractor for `<script>` block symbols
- Component registration in extractor registry
- CLI accepts `svelte` as language argument
- Integration test with real `.svelte` file

**Out of Scope:**
- Template block analysis (HTML/expressions)
- Style block analysis
- S17.4 analyzer adjustments

**Done Criteria:**
- [ ] Svelte extractor extracts functions, classes, imports from `<script>` blocks
- [ ] Component file registered as module-level symbol
- [ ] CLI `--languages svelte` works end-to-end
- [ ] Tests pass
- [ ] Retrospective complete
