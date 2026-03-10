## Feature Scope: S17.4 — Analyzer Adjustments

**Epic:** E17 (multi-language-discovery)
**Size:** S
**Branch:** epic/e17/multi-language-discovery (S-sized, no story branch)

**In Scope:**
- Category maps for non-Python conventions (Laravel: models/, controllers/, etc.)
- Module path logic for non-Python files (`_file_to_module` generalization)
- Formatter summary counts for new SymbolKinds (enum, type_alias, constant, trait, component)

**Out of Scope:**
- New extractors or scanner changes
- AI synthesis changes
- Cross-language dependency analysis

**Done Criteria:**
- [ ] `rai discover analyze` categorizes PHP/Svelte/TS symbols correctly
- [ ] Module paths work for non-Python files
- [ ] Formatter shows counts for all SymbolKinds
- [ ] Tests pass (>90% coverage on new code)
- [ ] Quality gates pass (ruff, pyright, bandit)
- [ ] Retrospective complete
