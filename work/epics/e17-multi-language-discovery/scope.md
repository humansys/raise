# Epic E17: Multi-Language Discovery - Scope

> **Status:** IN PROGRESS
> Branch: `epic/e17/multi-language-discovery`
> Created: 2026-02-09
> Target: 2026-02-10 (demo on zambezi-concierge)

---

## Objective

Extend `raise discover scan` to extract symbols from TypeScript/TSX, PHP, and Svelte codebases, enabling discovery on polyglot repositories.

**Value proposition:** Unlocks discovery for real customer projects (zambezi-concierge: Python + Laravel PHP + Svelte) that aren't Python-only. Without this, discovery covers ~30% of codebases we need to support. The TypeScript scanner currently misses 84% of files in real Next.js projects (bug report 2026-02-08).

**Success criteria:** `raise discover scan` produces a complete component catalog when run on zambezi-concierge (Python backend + PHP admin + Svelte frontend).

---

## Stories

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S17.1 | Fix TS/TSX scanner | M | ✅ Done | Fix .tsx glob, TSX parser, add enum/const/type_alias extraction, new SymbolKinds, exclude-based hierarchy |
| S17.2 | PHP extractor | M | ✅ Done | tree-sitter-php: classes, functions, interfaces, traits, methods |
| S17.3 | Svelte extractor | S | ✅ Done | tree-sitter-svelte: script block symbols + component registration |
| S17.4 | Analyzer adjustments | S | Pending | Category maps for non-Python, module path logic, formatter counts |

**Total:** 4 stories

---

## In Scope

**MUST:**
- Fix TS scanner: `.tsx` glob, `language_tsx()` parser dispatch by extension
- Extract enum, const, type_alias symbols from TS/TSX
- PHP extractor: classes, functions, interfaces, traits, methods
- Svelte extractor: script block symbols + component kind
- New SymbolKinds: "enum", "type_alias", "constant", "trait", "component"
- Exclude-based hierarchy routing in `build_hierarchy()`
- Extension registration for .php, .svelte in EXTENSION_TO_LANGUAGE
- Language-specific glob patterns for PHP and Svelte

**SHOULD:**
- Analyzer category maps for Laravel conventions (models/, controllers/, etc.)
- Module path logic for non-Python files (`_file_to_module` generalization)
- Formatter summary counts for new symbol kinds

---

## Out of Scope (defer to parking lot)

- Blade templates (`.blade.php`) — template markup, not structured code
- Vue SFC support — no current customer need
- Cross-language dependency analysis — future scope
- AI synthesis changes — downstream of scanner, separate concern
- Svelte template/markup extraction — only script block symbols

---

## Done Criteria

### Per Story
- [ ] Code implemented with type annotations
- [ ] Unit tests passing (>90% coverage on new code)
- [ ] All quality checks pass (ruff, pyright, bandit)
- [ ] TDD: red-green-refactor

### Epic Complete
- [ ] All 4 stories complete (S17.1-S17.4)
- [ ] `raise discover scan` works on zambezi-concierge repo
- [ ] Existing Python discovery unchanged (regression tests pass)
- [ ] Epic retrospective completed
- [ ] Merged to v2

---

## Dependencies

```
S17.1 (foundation: SymbolKinds, hierarchy, TS/TSX fix)
  ├──→ S17.2 (PHP extractor)
  └──→ S17.3 (Svelte extractor)
         │
         ▼
       S17.4 (analyzer adjustments)
```

S17.2 and S17.3 can run in parallel after S17.1.
S17.4 depends on all extractors being in place.

**External blockers:** None — tree-sitter-php and tree-sitter-svelte available on PyPI.

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| TSX parsing | Detect by extension (.ts→TS parser, .tsx→TSX parser) | Clean, deterministic, explicit |
| SymbolKind granularity | Granular kinds (enum, type_alias, constant, trait, component) | 1:1 to language constructs, downstream decides grouping |
| Hierarchy routing | Exclude-based (class/method are special, everything else standalone) | Future-proof, prevents silent data loss |
| Svelte extraction | tree-sitter-svelte | Consistent with TS/JS/PHP approach |
| PHP extraction | tree-sitter-php | Consistent pattern, Laravel is class-heavy |
| Multi-language detection | Fix globs + register extensions, auto-detect already works | Minimal plumbing, existing architecture handles it |

---

## Notes

### Why This Epic
- Bug report: TS scanner misses 84% of files in real Next.js project
- Customer demo: zambezi-concierge needs multi-language discovery by 2026-02-10
- Discovery is blocked for any non-Python-only project

### Key Risks
- tree-sitter-svelte grammar coverage: may miss edge cases in complex Svelte files → Mitigation: test against real zambezi-concierge files
- PHP namespace complexity: Laravel uses deep namespaces → Mitigation: class extraction covers the core need

### Trigger
Bug report from portal-pmo-v2 discovery (2026-02-08) + zambezi-concierge demo need.

---

## Implementation Plan

> Added by `/epic-plan` - 2026-02-09

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|:------------:|:---------:|-----------|
| 1 | S17.1: Fix TS/TSX scanner | M | None | M1 | Foundation — SymbolKinds + hierarchy used by all others |
| 2 | S17.2: PHP extractor | M | S17.1 | M2 | Largest zambezi sub-project (37 files), higher demo impact |
| 3 | S17.3: Svelte extractor | S | S17.1 | M2 | Smaller, same tree-sitter pattern as S17.2 |
| 4 | S17.4: Analyzer adjustments | S | S17.1-3 | M3 | Polish — demo works without it |

### Milestones

| Milestone | Stories | Target | Success Criteria |
|-----------|---------|--------|------------------|
| **M1: TS/TSX Fixed** | S17.1 | Tonight | .tsx scanned, enum/const/type extracted, Python regression pass |
| **M2: Demo Ready** | S17.1-3 | Tonight/tomorrow AM | `raise discover scan` on zambezi-concierge produces symbols from all 3 stacks |
| **M3: Epic Complete** | All 4 | Post-demo | Analyzer polished, retro done, merged to v2 |

### Parallel Opportunities

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1: S17.1 ──► S17.2 ──► S17.4
                      ↓
Stream 2:           S17.3 ──► merge
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

S17.2/S17.3 are independent but sequential in single-session work.

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| S17.1 takes longer than expected | Medium | High (cascading) | First in sequence — max recovery time |
| tree-sitter-svelte grammar gaps | Low | Medium | Test against real zambezi files early |
| PHP trait/namespace complexity | Low | Low | Class extraction covers Laravel core |

### Progress Tracking

| Story | Size | Status | Actual | Notes |
|-------|:----:|:------:|:------:|-------|
| S17.1 | M | ✅ Done | 45 min | 1.33x velocity |
| S17.2 | M | ✅ Done | 25 min | 2.4x velocity |
| S17.3 | S | ✅ Done | 20 min | 2.25x velocity |
| BF-2 | L | ✅ Done | 45 min | 2.67x velocity, templates + completeness check |
| S17.4 | S | Pending | - | |

**Milestones:**
- [x] M1: TS/TSX Fixed (2026-02-09)
- [x] M2: Demo Ready (2026-02-09)
- [ ] M3: Epic Complete

---

*Created: 2026-02-09*
*Plan added: 2026-02-09*
