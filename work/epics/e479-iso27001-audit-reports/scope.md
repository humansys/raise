# E479 Scope: ISO 27001 Audit Report Generator

## Objective

Automate generation of ISO 27001 compliance evidence reports from existing RaiSE artifacts, eliminating manual audit preparation for development teams.

## In Scope
- ISO 27001:2022 Annex A control mapping (software development subset ~20 controls)
- Evidence extraction from git, gates, sessions, backlog
- Report generation in auditor-friendly format
- Coverage gap analysis

## Out of Scope
- Full SGSI implementation
- Controls-as-code enforcement
- Non-development controls (physical security, HR, etc.)
- Certification process

## Planned Stories
- TBD — to be defined in `/rai-epic-design`

## Done Criteria
- [ ] Control mapping covers top 20 development-relevant Annex A controls
- [ ] Report generates from real project data in < 5 minutes
- [ ] Output readable by non-technical auditor
- [ ] Validated with Konesh (Vic) on real audit scenario
