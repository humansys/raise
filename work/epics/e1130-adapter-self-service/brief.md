---
epic_id: "RAISE-1130"
title: "Adapter Self-Service — Discovery, Doctor, Config Generator"
status: "draft"
created: "2026-04-01"
---

# Epic Brief: Adapter Self-Service

## Hypothesis
For RaiSE users who struggle to configure Jira and Confluence adapters,
a self-service setup skill (`/rai-adapter-setup`) with automated discovery
eliminates manual YAML authoring and misconfiguration.
Unlike the current approach (copy config from another dev, guess transition IDs),
our solution discovers backends, presents options, and generates validated config.

## Success Metrics
- **Leading:** New dev runs `/rai-adapter-setup` → validated config in <2 minutes, zero manual YAML edits
- **Lagging:** Zero support requests for adapter configuration issues

## Appetite
M — 6 stories, ~2-3 sessions

## Scope Boundaries
### In (MUST)
- Confluence discovery service (spaces, page trees, labels)
- Jira discovery service (projects, workflows, transitions, components)
- Unified `rai adapter doctor` — validates config vs live backend for both adapters
- Config generator for Confluence (discovery → human selects → valid YAML)
- Config generator for Jira (discovery → human selects → valid YAML)
- Unified `/rai-adapter-setup` skill orchestrating both generators

### Out (WON'T)
- MCP adapter support (legacy, removed in E1052)
- Multi-instance config generator (v1 generates single-instance; multi-instance is manual)
- Adapter telemetry, degradation, error messages (→ E1131)
- Auto-detection of existing config for migration (manual is fine for now)

## Rabbit Holes
- Jira workflow discovery can return complex structures (custom workflows, conditional transitions) — keep it simple, surface only the common states
- Confluence space permissions may hide spaces from discovery — document the limitation, don't try to escalate permissions
- Doctor validation may produce false positives on edge cases — use warnings (not errors) for ambiguous checks

## Prior Art
- E1051 (Confluence Adapter v2): `ConfluenceClient` with discovery methods exists
- E1052 (Jira Adapter v2): `JiraClient` with project/workflow queries exists
- E494 (ACLI Jira Adapter): original workflow discovery spike, validated the approach
- Stories S1051.4, S1051.5, S1051.6 were deferred from E1051 and absorbed here
