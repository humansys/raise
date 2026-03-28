---
epic_id: "E935"
jira_key: "RAISE-935"
title: "Confluence Content Migration — Filesystem to Single Source of Truth"
status: "designed"
created: "2026-03-27"
---

# E935 Scope: Confluence Content Migration

## Objective
Migrate all non-code documentation from raise-commons and raise-gtm filesystems, plus RGTM Confluence space, to STRAT and RaiSE1 spaces. After migration, repos contain only code and framework-required files. Confluence is the single source of truth.

## Prior Art
Session 2026-03-27 completed Phase 1:
- 58 strategic pages published to STRAT (9 sections)
- Dossier index created
- build-dossier.py extraction script working (~95k tokens)

## Confluence Space Map

| Space | Action |
|-------|--------|
| RaiSE1 | Stays — product docs (architecture, ADRs, epics, developer docs) |
| STRAT | Stays — absorbs strategy + GTM content |
| RGTM | Deprecated — useful content migrates to STRAT |
| CS | Stays — future use (customer success) |

## Source Inventory

### raise-commons (~1,800 files)
- dev/research/ (11 files, 284K) — strategic research
- dev/product/ (1 file, 32K) — PRO MVP spec
- dev/ root (10 files, 196K) — architecture, setup, onboarding
- work/research/ (377 files, 7.1M) — research by topic
- work/analysis/ (18 files, 352K) — architecture specs
- work/stories/ (94 files, 640K) — completed story artifacts
- work/bugs/ (127 files, 660K) — bug lifecycle artifacts
- work/epics/ completed (~1,000 files, ~9M) — epic archives
- work/problem-briefs/ (9 files, 44K) — problem statements
- work/issues/, hotfixes, other (~40 files, ~400K)

### raise-gtm (~560 files)
- governance/ (11 files, 80K) — vision, PRD, architecture
- dev/decisions/ (10 files, 52K) — ADRs
- content/strategy/ (8 files, 172K) — positioning
- content/research/ (16 files, 188K) — evidence catalogs
- content/sources/ (64 files, 4.2M) — transcripts, raw materials
- work/briefs/ (3 files, 40K) — strategic briefs
- work/content/ (45 files, 312K) — blog posts, landing pages
- work/epics/ (17 epics, 2.2M) — GTM feature tracking
- work/research/ (23 files, 328K) — GTM research

### RGTM Confluence (18 pages)
- ADRs (007-010), epics (E17, E18, E20), research catalogs, content pipeline, partnership leads, templates

## Destination Rules
- Product docs (architecture, ADRs, epics, stories, bugs, dev docs) → **RaiSE1**
- Strategy, GTM, market, brand, partnerships, evidence → **STRAT**
- raise-gtm governance, content, research → **STRAT**
- RGTM pages → **STRAT**

## Stories

| ID | Name | Size | Description |
|----|------|------|-------------|
| S935.1 | Target structure | S | Define new sections in STRAT + RaiSE1, naming conventions, label taxonomy |
| S935.2 | Classify & normalize raise-commons | M | Inference: read docs, classify STRAT vs RaiSE1, reorganize filesystem |
| S935.3 | Classify & normalize raise-gtm | M | Inference: read docs, classify to STRAT, reorganize filesystem |
| S935.4 | Migrate RGTM → STRAT | S | Move/recreate 18 RGTM pages to STRAT, deprecate space |
| S935.5 | Migration script | M | Script: read normalized filesystem, publish via API, register in confluence-pages.yaml |
| S935.6 | Execute migration | S | Run script, verify sample, bulk upload |
| S935.7 | Cleanup & references | S | Delete migrated docs, update CLAUDE.md, index, references |

**Dependencies:** S935.1 → S935.2 + S935.3 + S935.4 (parallel) → S935.5 → S935.6 → S935.7

## Exclusions
- Active/in-progress epics (stay in filesystem until closed)
- Code files, templates, skills, manifests
- Git history or authorship metadata
- Automated sync tooling (one-time migration)
- CS space (separate use)

## Done Criteria
- All non-code docs from both repos published in STRAT or RaiSE1
- RGTM space deprecated (content moved to STRAT)
- confluence-pages.yaml with complete mapping
- Filesystem clean (only code + framework-required files)
- build-dossier.py index updated
- CLAUDE.md and references point to Confluence
- raise-gtm repo evaluated for archival (code stays, docs gone)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Confluence API rate limiting on ~1,800 pages | Medium | Medium | Batch with delays, retry logic |
| Markdown conversion artifacts (tables, code blocks) | Medium | Low | Verify sample before bulk |
| Misclassification STRAT vs RaiSE1 | Low | Medium | Human review of classification before upload |
