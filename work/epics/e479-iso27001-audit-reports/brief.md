---
epic_id: "E479"
title: "ISO 27001 Audit Report Generator"
status: "draft"
created: "2026-03-13"
stakeholders: ["Emilio", "Vic (Konesh)"]
problem_brief: "work/problem-briefs/iso27001-audit-reports-2026-03-13.md"
---

# Epic Brief: ISO 27001 Audit Report Generator

## Hypothesis
For development teams preparing for ISO 27001 audits,
evidence is currently scattered across git, Jira, and loose documents,
making audit preparation a manual, time-consuming process.
Unlike the current state, an automated report generator that extracts evidence
from existing RaiSE artifacts (git history, gates, sessions, backlog)
will eliminate manual audit preparation.

## Success Metrics
- **Leading:** Time to generate evidence report < 5 minutes (vs days of manual collection)
- **Lagging:** Audit preparation effort reduced >80% within 4 weeks of adoption

## Appetite
M — 5-8 stories

## Scope Boundaries
### In (MUST)
- Map ISO 27001:2022 Annex A controls to RaiSE evidence sources
- Generate evidence reports from git history (commits, reviews, approvals)
- Generate evidence reports from gate results (tests, types, lint)
- Generate evidence reports from session journals and decisions
- Output in auditor-friendly format (PDF or structured Markdown)

### In (SHOULD)
- Coverage dashboard: which controls have evidence, which have gaps
- Integration with backlog adapter for change management evidence
- Configurable control subset (not all 93 controls apply to every org)

### No-Gos
- Full SGSI implementation (risk management, incident response, etc.)
- Controls-as-code enforcement (future epic)
- Certification consulting or compliance advice
- Real-time continuous monitoring

### Rabbit Holes
- Trying to cover all 93 Annex A controls — start with the ~20 most relevant to software development
- Building a custom PDF engine — use existing libraries
- Over-engineering the control-to-evidence mapping — start with a simple YAML config
