---
epic_id: "E935"
jira_key: "RAISE-935"
title: "Confluence Content Migration — Filesystem to Single Source of Truth"
status: "in-progress"
created: "2026-03-27"
---

# E935 Scope: Confluence Content Migration

## Objective
Migrate all non-code documentation from raise-commons and raise-gtm filesystems to Confluence STRAT space, making Confluence the single source of truth. After migration, repos contain only code and framework-required files.

## Prior Art
Session 2026-03-27 completed Phase 1:
- 59 strategic pages published to STRAT (9 sections)
- Dossier index created
- build-dossier.py extraction script working (~95k tokens)
- ~170 docs remaining to migrate

## In Scope
- raise-commons: work/, dev/research/, dev/product/ docs
- raise-gtm: content/, work/, governance/ docs
- Filesystem cleanup (remove migrated files)
- build-dossier.py index update
- CLAUDE.md and reference updates
- raise-gtm archival evaluation

## Out of Scope
- Code files, templates, skills, manifests
- Confluence section restructuring
- Automated sync tooling
- Git history migration

## Planned Stories
_(To be defined in /rai-epic-design)_

## Done Criteria
- All non-code docs migrated to Confluence STRAT
- Filesystem contains only code + framework-required files
- build-dossier.py index reflects all migrated pages
- References in CLAUDE.md point to Confluence
- raise-gtm evaluated for archival
