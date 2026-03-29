# E1001: Bug-Driven Process Improvement

**Jira:** RAISE-1001
**Version:** 2.3.1
**Status:** Backlog

## Objective

Establish a formal bug classification and workflow system that treats every bug as a process sensor — extracting not just the fix, but a process improvement from each defect.

> **Principle:** "Never let a bug go without improvement."

## Research

Based on formal SOTA research with triangulated claims from 13 sources:
- [Research: SOTA Bug Classification Taxonomies](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3147269371)

## Classification System

4 orthogonal dimensions (IEEE 1044 + ODC + Chromium):

1. **Bug Type:** Functional, Interface, Data, Logic, Configuration, Regression
2. **Severity:** S0-Critical, S1-High, S2-Medium, S3-Low
3. **Origin:** Requirements, Design, Code, Integration, Environment
4. **Qualifier:** Missing, Incorrect, Extraneous

## Bug Workflow

```
Open → Triage → Diagnose → Fix → Verify → Retro → Done
```

## Organization

Bugs organized by **Component** (not Epic). Linked to Stories/Epics via Jira links.

## Stories

| ID | Story | Key | Size | Dep |
|----|-------|-----|------|-----|
| S1001.1 | Jira Infrastructure — Custom Fields & Bug Workflow | RAISE-1002 | M | — |
| S1001.2 | Skill `/rai-bug-triage` — Classify, Diagnose, Extract | RAISE-1003 | M | S1 |
| S1001.3 | Dogfood — Process All 2.3.x Bugs | RAISE-1004 | L | S1, S2 |
| S1001.4 | Dashboard — JQL Filters & Analysis | RAISE-1005 | S | S1, S3 |

## Done Criteria

- [ ] 4 custom fields in Jira with constrained values
- [ ] Bug workflow active (7 statuses)
- [ ] `/rai-bug-triage` skill operational
- [ ] All 2.3.x bugs classified + improvement extracted
- [ ] 3+ concrete process improvements identified
- [ ] Dashboard with cross-dimensional analysis

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Jira admin permissions for custom fields | Blocks S1 | Emilio has admin access |
| Too few 2.3.x bugs for meaningful patterns | Low value from S3 | Include 2.2.x bugs if needed |
| Custom fields add friction to bug creation | Adoption fails | Keep to 4 fields, all dropdowns, <2 min |
