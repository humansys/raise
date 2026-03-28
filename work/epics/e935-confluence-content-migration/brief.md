---
epic_id: "E935"
title: "Confluence Content Migration — Filesystem to Single Source of Truth"
status: "draft"
created: "2026-03-27"
---

# Epic Brief: Confluence Content Migration — Filesystem to Single Source of Truth

## Hypothesis
For the RaiSE team who maintains strategic, research, and operational docs scattered across two repos and Confluence,
the content migration is a consolidation effort
that makes Confluence the single source of truth for all non-code documentation.
Unlike the current state (docs in raise-commons/work, raise-gtm/content, and partially in Confluence STRAT), our solution eliminates duplication and drift.

## Success Metrics
- **Leading:** First batch of docs migrated and verified accessible in Confluence
- **Lagging:** Zero non-code docs remaining in filesystem (repos contain only code + framework-required files)

## Appetite
M — 5-7 stories (systematic migration in batches by source/section)

## Scope Boundaries
### In (MUST)
- Migrate all work/, dev/research/, dev/product/ docs from raise-commons to Confluence STRAT
- Migrate all content/, work/, governance/ docs from raise-gtm to Confluence STRAT
- Clean filesystem to code-only (+ framework-required docs like CLAUDE.md)
- Update build-dossier.py index with new pages
- Update CLAUDE.md and references to point to Confluence

### In (SHOULD)
- Evaluate raise-gtm repo for archival (mostly content, minimal code)
- Organize migrated content into STRAT section hierarchy

### No-Gos
- Migrating code or framework-required files (templates, manifests, skills)
- Restructuring Confluence STRAT sections (already organized in prior session)
- Automating future sync — this is a one-time migration

### Rabbit Holes
- Trying to auto-convert markdown formatting perfectly — good enough is fine
- Building tooling beyond what build-dossier.py already provides
- Migrating git history or authorship metadata
