---
epic_id: "RAISE-1021"
title: "Adapter Configuration Foundation"
status: "draft"
created: "2026-03-28"
---

# Epic Brief: Adapter Configuration Foundation

## Hypothesis
For RaiSE developers who need reliable adapter integration,
the generated config + doctor system is a configuration layer
that eliminates hand-written YAML with hard-coded IDs.
Unlike the current manual approach (look up transition IDs, paste into YAML),
our solution discovers the backend and generates correct config automatically.

## Success Metrics
- **Leading:** `/rai-adapter-setup` generates valid jira.yaml from live Jira in < 2 minutes
- **Lagging:** Zero config-related adapter failures after generated config is in use

## Appetite
M — 5-7 stories

## Scope Boundaries
### In (MUST)
- Jira backend discovery (projects, workflows, transitions, issue types)
- Confluence backend discovery (spaces, page trees)
- Config generator skill (`/rai-adapter-setup`)
- Adapter doctor (`rai adapter doctor`)
- Confluence config schema (artifact-type routing, parent pages, labels)

### In (SHOULD)
- Jira multi-project routing (per-project config resolved from issue key prefix)

### No-Gos
- Adapter Protocol changes (that's RAISE-1022)
- Telemetry/degradation handling (that's RAISE-1023)
- Local persistence adapters (that's RAISE-1040)
- Webhook or automation config
- Migration of existing jira.yaml — new format coexists

### Rabbit Holes
- Over-engineering the discovery to handle every Jira workflow plugin — stick to standard workflows
- Building a full Confluence IA planner — just discover what exists and map artifact types
- Multi-instance Jira support — one instance per repo is sufficient for v2.4
