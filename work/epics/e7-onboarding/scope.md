---
id: E7
title: "Onboarding"
status: in-progress
branch: epic/e7/onboarding
base: v2
priority: P1 (F&F critical path)
estimated: M (single story)
---

# E7: Onboarding

## Objective

Take a new user from `pip install raise-cli` to a fully RaiSE-ready project — working graph, governance structure, and first `/session-start` — through a single guided conversation.

## Context

E7 was originally scoped as "Distribution & Onboarding." E14 (Rai Distribution) delivered the distribution half: base Rai bundling, bootstrap on `raise init`, MEMORY.md generation, skills scaffolding. What remains is the **onboarding experience** — the guided path that leaves a project ready for development.

`raise init` creates infrastructure (manifest, profile, Rai base, skills) but leaves the governance content layer empty. Without governance docs, the graph has no concepts to query and skills fly blind.

## Scope

### In Scope

| Story | Description | Size |
|-------|-------------|------|
| S7.1 | `/onboard` skill — guided conversation from init to RaiSE-ready | M |

### What S7.1 Delivers

- `/onboard` Claude Code skill handling greenfield and brownfield
- Governance scaffolding: PRD, vision, guardrails, architecture docs
- Discovery integration for brownfield (scan + analyze)
- Graph build + verification
- Distributable via `raise init` (in DISTRIBUTABLE_SKILLS)

### Out of Scope (deferred)

- `raise status` health check command (post-F&F)
- `raise doctor` coherence audit (post-F&F)
- Auto-progress Shu→Ha→Ri (manual for now)
- Multi-language convention detection (Python first)

## Dependencies

- `raise init` — exists, working
- `raise discover scan` + `raise discover analyze` — exists, working
- `raise memory build` — exists, working
- Graph parsers for governance docs — exist, format specs in S7.1 design

## Stories

- [S7.1 Design](stories/s7.1-onboard-skill/design.md)
