# Epic Retrospective: E17 Multi-Language Discovery

**Completed:** 2026-02-10
**Duration:** 2 days (started 2026-02-09)
**Stories:** 4 stories + 1 bugfix delivered

---

## Summary

Extended `raise discover scan` from Python-only to polyglot support (TypeScript/TSX, PHP, Svelte). The epic was driven by a zambezi-concierge demo need — a real customer repo with Python + Laravel PHP + Svelte. All three extractors use tree-sitter for consistent, deterministic parsing. The analyzer now categorizes and paths non-Python files correctly.

---

## Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Stories Delivered | 4 + BF-2 | BF-2 was intercalated (arch graph gap) |
| Tests Added | ~930 lines | 5 test files changed |
| Average Velocity | 2.1x | Faster than estimated across all stories |
| Calendar Days | 2 | Started evening of Feb 9, closed Feb 10 |
| Coverage | 93% | Above 90% gate |

### Story Breakdown

| Story | Size | Actual | Velocity | Key Learning |
|-------|:----:|:------:|:--------:|--------------|
| S17.1 Fix TS/TSX | M | 45 min | 1.33x | Extension-based parser dispatch is clean |
| S17.2 PHP extractor | M | 25 min | 2.4x | tree-sitter pattern reuse pays off fast |
| S17.3 Svelte extractor | S | 20 min | 2.25x | Script block extraction simpler than expected |
| BF-2 Arch graph gap | L | 45 min | 2.67x | Templates + completeness check = poka-yoke |
| S17.4 Analyzer adjustments | S | 15 min | 2.0x | Formatter was already done from S17.1 |

---

## What Went Well

- **tree-sitter consistency** — Same extraction pattern (parse → walk → match node types → extract) replicated across PHP and Svelte with minimal adaptation
- **Exclude-based hierarchy routing** — New SymbolKinds (enum, trait, component, etc.) automatically become standalone without code changes
- **Demo deadline focused scope** — M2 milestone achieved in one evening session; demo ran successfully
- **TDD velocity** — RED/GREEN cycles were fast because the extractor pattern was well-established by S17.2

## What Could Be Improved

- **Scanner lacks --exclude for vendor/node_modules** (PAT-247) — Full-repo PHP scans hit vendor directories, causing duplicate IDs and noise
- **discover-describe was invisible** — Missing YAML frontmatter meant Claude Code never registered it. Fixed during epic close session.
- **uv run prefix in skills** — All 39 skill files hardcoded `uv run raise` instead of `raise`. Fixed as standalone bugfix during this epic's session.

## Patterns Discovered

| ID | Pattern | Context |
|----|---------|---------|
| PAT-247 | Scanner needs exclude patterns for vendor/node_modules | PHP/JS projects with dependency dirs |
| (fix) | Skills without YAML frontmatter are invisible to Claude Code | Skill registration requires frontmatter |
| (fix) | `uv run` prefix is dev-env coupling leak | End users install via pip, get `raise` on PATH |

## Process Insights

- S-sized stories on epic branch (no story branch) works well — avoids branch proliferation for trivial changes
- Multi-language support was easier than expected because the architecture (tree-sitter, SymbolKind, exclude-based routing) was designed for extension in E12
- Intercalating BF-2 mid-epic worked cleanly — separate branch, merge back, no disruption

---

## Artifacts

- **Scope:** `work/epics/e17-multi-language-discovery/scope.md`
- **Stories:** `work/epics/e17-multi-language-discovery/stories/`
- **Tests:** ~930 lines added across 5 test files
- **Bugfixes:** `uv run` prefix removal (39 files), discover-describe frontmatter

---

## Next Steps

- Demo zambezi-concierge discovery (today)
- First RaiSE client kick-off (today)
- Future: `--exclude` flag for scanner (PAT-247)
- Future: Absorb discover-complete into discover-validate (parking lot)
- Future: `raise story` CLI subcommands to reduce inference overhead

---

*Epic retrospective — 2026-02-10*
