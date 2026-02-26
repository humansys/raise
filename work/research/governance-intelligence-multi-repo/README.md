# Research: Governance Intelligence for Multi-Repo Environments

**Date:** 2026-02-26
**Session:** SES-294
**Status:** Exploration Complete — Ready for Problem Shaping
**Builds on:** [governance-as-code-agents](../governance-as-code-agents/) (Jan 29), [shared-memory-architecture](../shared-memory-architecture/) (Feb 25), [atlassian-forge-integration](../atlassian-forge-integration/) (Feb 24)

## Research Question

How can RaiSE leverage the shared knowledge graph (rai-server) to provide
governance intelligence across multiple repositories in an organization,
with poka-yoke enforcement integrated into the developer workflow?

## TL;DR

Three capabilities emerge from having the knowledge graphs of multiple repos
in one server:

1. **Design Intelligence** — Cross-repo awareness at design time (dependency
   visibility, blast radius analysis)
2. **Portfolio Intelligence** — Capacity, workload, and velocity metrics
   aggregated across repos/teams
3. **Governance Intelligence** — Compliance validation at all levels with
   poka-yoke prevention during work

This research focuses on **Governance Intelligence** — the most differentiating
capability. Cross-repo visibility and portfolio metrics exist in other tools
(Backstage, Jira Portfolio). Governance-as-code with poka-yoke integrated into
the AI developer workflow does not exist anywhere.

**Core insight:** "Para ir rapido hay que ir seguro." Poka-yoke is not a brake —
it's a rail. It lets you go fast *because* you can't derail.

## Contents

- [This README](./README.md) — Overview, context, and key decisions
- [Governance Intelligence Report](./governance-intelligence-report.md) — Full analysis with Kurigage scenarios
- Related: [governance-as-code-agents](../governance-as-code-agents/) — Policy DSL research (local enforcement)
- Related: [shared-memory-architecture](../shared-memory-architecture/) — Server architecture decisions

## Relationship to Prior Research

| Research | Date | Scope | This doc extends it by... |
|----------|------|-------|---------------------------|
| governance-as-code-agents | Jan 29 | Local policy enforcement (single repo) | Adding multi-repo scope hierarchy, cross-repo compliance, server-based validation |
| shared-memory-architecture | Feb 25 | Server storage + multi-tenancy | Adding governance-specific query patterns, compliance state, poka-yoke integration |
| atlassian-forge-integration | Feb 24 | Forge app + Rovo agents | Adding governance validation endpoints, compliance reporting for Rovo |

## Key Decisions

| Dimension | Decision | Rationale |
|-----------|----------|-----------|
| Differentiator | Governance Intelligence (not cross-repo viz or portfolio) | Other tools do viz/portfolio; nobody does governance-as-code with poka-yoke in AI dev workflow |
| Enforcement model | Three levels: MUST / SHOULD / CAN | Inspired by RFC 2119; maps to poka-yoke types (contact/motion-step/informative) |
| Scope hierarchy | Enterprise → Org → Team → Repo | Higher levels cannot be relaxed; lower levels can be stricter |
| Integration point | Embedded in existing skills (not separate tool) | Skills ARE the workflow; governance checks go inside them, not beside them |
| Exception mechanism | Waivers with expiration + traceability | Governance without exceptions is tyranny; waivers are auditable graph nodes |
| Validation customer | Kurigage (3 repos, 3 tech leads, 1 architect) | Real constraints, real governance needs, demo deadline |

## Next Steps

1. `/rai-problem-shape` — Shape this into a formal problem brief for the product roadmap
2. Gap analysis — Compare graph schema (18 node types, 11 edge types) against required capabilities
3. Endpoint design — Define governance-specific API endpoints for rai-server
4. Kurigage pilot — Validate with Rodo (architect) that the model matches their governance needs
