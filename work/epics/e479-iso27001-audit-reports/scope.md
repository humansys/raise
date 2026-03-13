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

## Implementation Plan

### Sequencing Strategy: Walking Skeleton

Prove the extract→render pipeline E2E with the shortest path (mapping→git→markdown), then broaden.

### Sequence

| Order | Story | Jira | Size | Rationale | Enables |
|-------|-------|------|------|-----------|---------|
| 1 | S479.1 Control mapping | RAISE-558 | S | Foundation — all extractors depend on this | S479.2-4, S479.8 |
| 2 | S479.2 Git extractor | RAISE-559 | M | Highest-value evidence source, proves pipeline | S479.5 |
| 3 | S479.5 Report — Markdown | RAISE-562 | M | Walking skeleton complete: real report for Vic | S479.6, S479.7 |
| 4 | S479.3 Gate extractor | RAISE-560 | S | Parallel with S479.4 after skeleton validated | S479.5 (enriches) |
| 4 | S479.4 Session extractor | RAISE-561 | S | Parallel with S479.3 | S479.5 (enriches) |
| 5 | S479.6 Report — PDF | RAISE-563 | S | Parallel with S479.7, S479.8 |  |
| 5 | S479.7 Report — CSV | RAISE-564 | XS | Parallel with S479.6, S479.8 |  |
| 5 | S479.8 Coverage dashboard | RAISE-565 | S | Parallel with S479.6, S479.7 |  |

### Milestones

#### M1: Walking Skeleton
- **Stories:** S479.1, S479.2, S479.5
- **Criteria:** One Markdown report with real git evidence for at least 1 control
- **Demo:** Show Vic a real report from raise-commons data

#### M2: Full Extraction
- **Stories:** + S479.3, S479.4
- **Criteria:** All 8 controls with evidence from 3 sources (git, gates, sessions)
- **Demo:** Complete evidence collection, gap analysis visible

#### M3: All Formats + Dashboard (Epic Complete)
- **Stories:** + S479.6, S479.7, S479.8
- **Criteria:** PDF, CSV, dashboard working. Vic validates against auditor expectations
- **Demo:** Full audit report package ready for auditor

### Progress Tracking

| Story | Jira | Status | Branch | Notes |
|-------|------|--------|--------|-------|
| S479.1 | RAISE-558 | done | — | Merged to dev |
| S479.2 | RAISE-559 | pending | — | — |
| S479.3 | RAISE-560 | pending | — | — |
| S479.4 | RAISE-561 | pending | — | — |
| S479.5 | RAISE-562 | pending | — | — |
| S479.6 | RAISE-563 | pending | — | — |
| S479.7 | RAISE-564 | pending | — | — |
| S479.8 | RAISE-565 | pending | — | — |
