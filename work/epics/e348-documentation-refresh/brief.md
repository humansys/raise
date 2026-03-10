---
epic_id: "E348"
title: "Documentation Refresh — user guides and developer extension docs through v2.2"
status: "draft"
created: "2026-03-05"
---

# Epic Brief: Documentation Refresh

## Hypothesis
For RaiSE users and developers/extensors who need current documentation to adopt and extend the framework,
the Documentation Refresh is a shipping pre-requisite
that brings all user guides and developer docs up to date through v2.2.
Unlike the current state (12 epics shipped with zero doc updates since v2.1), our solution ensures every audience has accurate, discoverable documentation.

## Success Metrics
- **Leading:** Documentation audit identifies all drift areas; first guide updated within S348.2
- **Lagging:** Users can install, configure, and extend RaiSE using only published docs (no tribal knowledge required)

## Appetite
M — 5-7 stories (audit + user guides + developer guides + CLI reference + validation)

## Scope Boundaries
### In (MUST)
- Audit documentation drift since v2.1
- User guides: installation, CLI usage, skills, .raise/ configuration
- Developer guides: adapters, MCP servers, skills, hooks
- CLI reference update (new commands since v2.1)

### In (SHOULD)
- Architecture overview for new contributors
- Migration guide from v2.1 to v2.2

### No-Gos
- API reference auto-generation tooling (separate epic)
- Video tutorials or interactive content
- Confluence/external publishing automation (E433 covers this)

### Rabbit Holes
- Trying to document every internal module — focus on public interfaces and extension points
- Building a docs site framework — use existing markdown in repo, publish later
- Perfectionism on prose — good enough and accurate beats polished and stale
