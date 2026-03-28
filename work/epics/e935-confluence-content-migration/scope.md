---
epic_id: "E935"
jira_key: "RAISE-935"
title: "Confluence Content Migration — Filesystem to Single Source of Truth"
status: "planned"
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

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-03-27

### Sequencing Strategy

**Quick-wins + Dependency-driven.** No architectural uncertainty — Confluence API and build-dossier.py patterns are proven from Phase 1. The risk is volume, not technology. S935.4 (RGTM→STRAT) is the quick win: 18 pages, Confluence-to-Confluence, validates migration flow without touching filesystem.

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S935.1 — Target structure | S | None | M1 | Foundation: sections and taxonomy must exist before any classification |
| 2 | S935.4 — Migrate RGTM → STRAT | S | S935.1 | M1 | Quick win: 18 pages, validates Confluence-to-Confluence flow, no filesystem risk |
| 3 | S935.2 — Classify raise-commons | M | S935.1 | M2 | Parallel with S935.3: largest batch (~1,800 files), inference-heavy |
| 3 | S935.3 — Classify raise-gtm | M | S935.1 | M2 | Parallel with S935.2: smaller batch (~560 files), all→STRAT simplifies classification |
| 4 | S935.5 — Migration script | M | S935.2, S935.3 | M3 | Needs normalized filesystem as input; based on build-dossier.py patterns |
| 5 | S935.6 — Execute migration | S | S935.5 | M3 | Run script, verify sample, then bulk. HITL gate before bulk upload |
| 6 | S935.7 — Cleanup & references | S | S935.6 | M4 | Final: delete migrated files, update refs. Only after migration verified |

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|------------------|
| **M1: Structure + Quick Win** | S935.1, S935.4 | New sections exist in STRAT + RaiSE1. RGTM 18 pages migrated and verified in STRAT |
| **M2: Content Classified** | +S935.2, S935.3 | All docs classified (STRAT vs RaiSE1), filesystem reorganized into staging dirs. HITL review of classification |
| **M3: Migration Complete** | +S935.5, S935.6 | Script built and executed. All ~1,800 docs published to Confluence. confluence-pages.yaml populated |
| **M4: Epic Complete** | +S935.7 | Filesystem clean. References updated. raise-gtm evaluated for archival. Done criteria met. Retro done |

### Parallel Work Streams

```
Time →
Stream A (Critical): S935.1 ─► S935.4 ─► ··wait·· ─► S935.5 ─► S935.6 ─► S935.7
                         │                     ▲
                         ├── S935.2 (commons) ─┤
                         │                     │
Stream B (Parallel):     └── S935.3 (gtm) ────┘
```

**Merge points:**
- After S935.1: split — S935.4 runs sequentially (quick win), S935.2+S935.3 run in parallel
- Before S935.5: merge — script needs both classification outputs + RGTM migration done

### Progress Tracking

| Story | Size | Status | Actual | Notes |
|-------|:----:|:------:|:------:|-------|
| S935.1 — Target structure | S | **Done** | 2026-03-27 | 8 sections, labels, index updated |
| S935.4 — Migrate RGTM → STRAT | S | Pending | — | |
| S935.2 — Classify raise-commons | M | Pending | — | |
| S935.3 — Classify raise-gtm | M | Pending | — | |
| S935.5 — Migration script | M | Pending | — | |
| S935.6 — Execute migration | S | Pending | — | |
| S935.7 — Cleanup & references | S | Pending | — | |

### Sequencing Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| Classification takes longer than expected (1,800 files × inference) | M/M | Batch by directory, classify by heuristic first, inference only for ambiguous |
| RGTM pages have Confluence-specific formatting that doesn't copy cleanly | L/L | Manual fix for 18 pages is acceptable |
| Script assumes uniform markdown but some docs are non-standard | M/M | Validate with 10-doc sample per directory before bulk run |
