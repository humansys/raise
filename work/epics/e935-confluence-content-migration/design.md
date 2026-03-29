---
epic_id: "E935"
jira_key: "RAISE-935"
title: "Confluence Content Migration — Design"
status: "designed"
created: "2026-03-27"
---

# E935 Design: Confluence Content Migration

## Approach: Normalize-then-Script

Two-phase strategy that separates judgment from execution:

1. **Normalize (inference)** — Read each doc, classify destination (STRAT vs RaiSE1), assign target section, rename/reorganize in filesystem
2. **Upload (script)** — Read normalized filesystem, publish to Confluence API, register mapping

This avoids using inference for 1,800 individual uploads while ensuring content lands in the right place.

## Target Confluence Structure

### STRAT (expanded from 9 → 16 sections)

| # | Section | New? | Content |
|---|---------|------|---------|
| 1 | Visión e Identidad | Existing | Vision, strategy briefs |
| 2 | Modelo de Producto | Existing | Product specs, ADRs |
| 3 | Mercado y Competencia | Existing | Competitive analysis |
| 4 | Posicionamiento y Marca | Existing | Brand, messaging |
| 5 | GTM Metodología | Existing | Lean GTM framework |
| 6 | Partnerships e Integraciones | Existing | Atlassian, Anthropic |
| 7 | Clientes y Evidencia | Existing | Coppel, evidence catalogs |
| 8 | Roadmap y Futuro | Existing | Problem briefs, roadmap |
| 9 | Launch y Campañas | Existing | Launch strategy, pitches |
| 10 | Research | **New** | All strategic research (raise-commons + raise-gtm) |
| 11 | GTM Operations | **New** | RGTM content: epics, ADRs, content pipeline, partnerships |
| 12 | GTM Content | **New** | Blog posts, landing pages, campaigns from raise-gtm |
| 13 | Sources & Transcripts | **New** | Raw materials, demo transcripts, meeting notes |

### RaiSE1 (expanded)

| Section | New? | Content |
|---------|------|---------|
| Architecture | Existing | ADRs, system design |
| Developer Docs | Existing | Epic docs, guides |
| Product | Existing | Product vision, briefs |
| Epic Archives | **New** | Completed epic artifacts (brief, scope, design, retro) |
| Story Archives | **New** | Completed story artifacts |
| Bug Archives | **New** | Bug lifecycle artifacts |
| Analysis | **New** | Architecture specs, design pattern synthesis |

## Migration Script Design

Based on existing `build-dossier.py` (reads Confluence → assembles markdown). Migration script is its inverse.

### Input
- Normalized filesystem with directory structure mapping to Confluence sections
- Manifest file defining: source path → target space + section + title

### Output
- Pages created in Confluence with correct parent
- Labels applied (section label + source label)
- confluence-pages.yaml updated with page ID mapping

### Key Decisions
- **Parent assignment:** Each section header page is the parent for its children
- **Naming:** Page title = cleaned filename or H1 from markdown
- **Labels:** `migrated`, `source:{repo}`, section label (e.g., `epic-archive`)
- **Idempotency:** Check if page title exists before creating (skip duplicates)
- **Rate limiting:** 1 request/second with exponential backoff

## RGTM → STRAT Migration

Confluence-to-Confluence. For each RGTM page:
1. Read content via API
2. Classify target section in STRAT
3. Create page in STRAT with same content
4. Add redirect notice to original RGTM page
5. After verification, archive RGTM space

## Filesystem Normalization Rules

### Classification Heuristic
- Contains "ADR", architecture, module docs → **RaiSE1**
- Contains epic/story/bug artifacts from raise-commons → **RaiSE1**
- Contains strategy, GTM, market, brand, evidence, research → **STRAT**
- Contains raise-gtm governance, content → **STRAT**
- Ambiguous → flag for human review

### Directory Reorganization
After classification, reorganize into staging directories:
```
work/epics/e935-confluence-content-migration/staging/
  strat/
    10-research/
    11-gtm-operations/
    12-gtm-content/
    13-sources-transcripts/
  raise1/
    epic-archives/
    story-archives/
    bug-archives/
    analysis/
```

## No ADRs Needed
No new architectural decisions — using existing Confluence API, extending established patterns from Phase 1.
