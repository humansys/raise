---
epic_id: "E348"
title: "Documentation Refresh"
status: "in-progress"
created: "2026-03-05"
backlog_key: "RAISE-348"
---

# E348: Documentation Refresh

## Objective

Bring all user and developer documentation up to date through v2.2. Shipping pre-requisite — no release without current docs.

## In Scope
- Audit documentation drift since v2.1 (12 epics, zero doc updates)
- User documentation: installation, CLI usage, skills workflow, .raise/ configuration
- Developer documentation: adapters, MCP servers, skills, hooks, extension points
- CLI reference: new commands and flags since v2.1
- README refresh for repository root

## Out of Scope
- API reference auto-generation tooling
- Video tutorials or interactive content
- Confluence publishing automation (RAISE-433)
- Internal module documentation (covered by /rai-discover pipeline)

## Stories (from RAISE-348)
- S348.1: Audit documentation drift (RAISE-357)
- S348.2-N: User and developer guide stories (to be defined in /rai-epic-design)

## Done Criteria
- [ ] Documentation audit complete with gap analysis
- [ ] User guides cover install → configure → use workflow
- [ ] Developer guides cover adapter → MCP → skill → hook extension points
- [ ] CLI reference reflects all v2.2 commands
- [ ] README accurately describes current project state
- [ ] All docs validated against actual CLI behavior
