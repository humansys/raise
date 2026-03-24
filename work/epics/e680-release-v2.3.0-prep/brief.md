---
epic_id: "E680"
title: "Release v2.3.0 Prep"
status: "draft"
created: "2026-03-23"
---

# Epic Brief: Release v2.3.0 Prep

## Hypothesis
For the RaiSE development team who need to ship v2.3.0 with proper documentation and quality assurance,
the release prep epic is a structured process
that ensures every release ships with complete documentation, changelog, and verification.
Unlike ad-hoc releases (v2.2.0-v2.2.3), our solution prevents documentation debt and establishes a repeatable pattern.

## Success Metrics
- **Leading:** All 3 completed epics have Confluence documentation before release
- **Lagging:** Retrospective produces actionable `/rai-release-prep` skill design

## Appetite
S — 5 stories, documentation + verification focus (no code features)

## Scope Boundaries
### In (MUST)
- Epic documentation for E478, E494, E654 via `/rai-epic-docs`
- CHANGELOG.md updated with full v2.3.0 scope
- Verification roundtrip of `rai session start/close`
- `/rai-publish` with minor bump

### In (SHOULD)
- Dev/user docs update in `/docs` for ACLI adapter, session identity, CLI extensions
- Release notes draft for Confluence/GitHub

### No-Gos
- Building the `/rai-release-prep` skill (that's retro output, not this epic's work)
- Fixing open bugs (RAISE-539, 634, 213) — those are Fernando's, we document their status
- Redesigning the docs site

### Rabbit Holes
- Over-documenting epics that already have good retrospectives
- Trying to automate the process before we've done it manually once
