# E479 Scope: ISO 27001 Audit Report Generator

## Objective

Automate generation of ISO 27001 compliance evidence reports from existing RaiSE artifacts, eliminating manual audit preparation for development teams already certified.

## Value

Development teams spend days collecting evidence for ISO 27001 recertification audits. This epic automates that collection from artifacts they already produce (git, gates, sessions), reducing preparation time >80%.

## In Scope

### MUST
- ISO 27001:2022 Annex A.8 control mapping (8 technological controls)
- Git evidence extractor (commits, PRs, tags, branches)
- Gate evidence extractor (tests, types, lint results)
- Session evidence extractor (journals, decisions, ADRs)
- Report generation in Markdown, PDF, and CSV formats
- Coverage gap analysis dashboard

### SHOULD
- Configurable audit period (date range filter)
- Control subset selection (not all 8 may apply to every project)

## Out of Scope
- Non-A.8 domains (organizational, people, physical) — future epic
- Full SGSI implementation
- Controls-as-code enforcement — future epic
- Jira/Confluence evidence extraction — only Git for v1
- Certification consulting or compliance advice

## Controls Covered (A.8 Technological)

| Control | Description | Evidence Source |
|---------|-------------|----------------|
| A.8.4 | Access to source code | Git permissions |
| A.8.9 | Configuration management | Git history, branches, tags |
| A.8.15 | Logging | Session journals, audit trail |
| A.8.25 | Secure development lifecycle | Gates (tests, types, lint), TDD |
| A.8.26 | Application security requirements | Story designs, ADRs |
| A.8.27 | Secure system architecture | Design docs, architecture reviews |
| A.8.32 | Change management | Commits, PRs, approvals, backlog |
| A.8.33 | Test information | Test results, coverage |

## Stories

| ID | Story | Size | Description |
|----|-------|------|-------------|
| S479.1 | Control mapping config | S | YAML with 8 A.8 controls mapped to RaiSE evidence sources |
| S479.2 | Git evidence extractor | M | Extract commits, PRs, tags, branches as traceable evidence |
| S479.3 | Gate evidence extractor | S | Extract gate results (tests, types, lint) as evidence |
| S479.4 | Session evidence extractor | S | Extract journals, decisions, ADRs as evidence |
| S479.5 | Report engine — Markdown | M | Generate structured report per control in Markdown |
| S479.6 | Report engine — PDF | S | Convert Markdown to formal PDF with cover and index |
| S479.7 | Report engine — CSV | XS | Export control table with evidence to CSV/Excel |
| S479.8 | Coverage dashboard | S | Show which controls have evidence and which have gaps |

## Dependencies

```
S479.1 → S479.2, S479.3, S479.4
S479.2, S479.3, S479.4 → S479.5
S479.5 → S479.6, S479.7
S479.1 + extractors → S479.8
```

## Done Criteria
- [ ] 8 A.8 controls mapped with at least one working evidence source each
- [ ] Report generated from real RaiSE project data in < 5 minutes
- [ ] Three output formats working (Markdown, PDF, CSV)
- [ ] Vic (Konesh) validates report against auditor expectations
- [ ] Architecture docs updated
- [ ] Epic retrospective completed

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Git evidence insufficient for some controls (e.g. A.8.4) | High | Medium | Report as explicit gap, never fabricate evidence |
| PDF format doesn't meet auditor expectations | Medium | Medium | Validate template with Vic in S479.6 before polishing |
| Git history volume makes extraction slow | Low | High | Date range filter (audit period) |
