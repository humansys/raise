# Research: Cross-Repo Visibility (Layer 1)

**Date:** 2026-02-26
**Session:** SES-294
**Status:** Exploration Complete — Ready for Epic Planning
**Builds on:** [shared-memory-architecture](../shared-memory-architecture/) (Feb 25), [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) (Feb 26)

## Research Question

How can RaiSE provide cross-repo dependency visibility, impact analysis, and
duplicate detection using the shared knowledge graph, and what are the schema
and endpoint gaps needed to enable this?

## TL;DR

The existing PostgreSQL schema (graph_nodes + graph_edges with org_id/repo_id
scoping) already supports cross-repo edges — they just have no mechanism to
get populated. The main gap is in the sync logic (`resolve_node_ids()` only
searches within one repo) and query logic (no traversal endpoints, only keyword
search).

Three capabilities unlock Layer 1:

1. **Dependency Graph Cross-Repo** — `depends_on` edges crossing repo boundaries,
   populated via contract declarations in `.raise/contracts.yaml`
2. **Impact Analysis** — BFS traversal from a changed node, crossing repo
   boundaries, integrated into `/rai-story-design` for design-time awareness
3. **Duplicate Detection** — Name + content similarity across repos to surface
   redundant components

**Core insight:** The hard part is not querying cross-repo data (BFS is trivial).
The hard part is populating cross-repo edges reliably. The hybrid approach
(auto-discover within repo, manually declare cross-repo contracts) is the
pragmatic starting point.

## Contents

- [This README](./README.md) — Overview, context, and key decisions
- [Cross-Repo Visibility Report](./cross-repo-visibility-report.md) — Full analysis with Kurigage scenarios
- Related: [shared-memory-architecture](../shared-memory-architecture/) — Server architecture, PostgreSQL schema
- Related: [governance-intelligence-multi-repo](../governance-intelligence-multi-repo/) — Layer 3 (Governance Intelligence)

## Relationship to Capability Layers

```
  4. Organizational Learning        (future)
  3. Governance Intelligence        (researched — Feb 26)
  2. Pattern Propagation            (future)
  1. Cross-Repo Visibility          ← THIS RESEARCH
  0. Shared Memory (EXISTS — E275)
```

## Key Decisions

| Dimension | Decision | Rationale |
|-----------|----------|-----------|
| Edge population | Hybrid: auto intra-repo + manual cross-repo contracts | Can't auto-scan other repos; manual YAML is low-effort for 5-10 deps |
| Contract format | `.raise/contracts.yaml` per repo | Fits existing `.raise/` convention; version-controlled, PR-reviewed |
| Impact algorithm | Server-side BFS traversal | Server has complete cross-repo graph; client only has its own repo |
| Duplicate detection | Name + content similarity (TF-IDF) | Simple, deterministic, catches obvious cases; defer semantic (embeddings) |
| Schema changes | None — extend JSONB properties + sync logic | Existing graph_nodes + graph_edges already support cross-repo edges |
| Skill integration | `/rai-story-design` queries impact | Design time is the optimal prevention point |
| New endpoints | 3: dependencies, impact, duplicates | Structural graph queries, not keyword search |

## Effort Estimate

| Phase | Scope | Effort |
|-------|-------|--------|
| Phase 1: Cross-repo edges | Edge sync + contract convention | S (1-2 days) |
| Phase 2: Dependency visibility | 3 endpoints + skill integration | M (1-2 weeks) |
| Phase 3: Intelligence | Duplicate detection + versioning | S-M (3-5 days) |
| **Total** | **5-7 stories** | **~3 weeks** |

## Next Steps

1. Phase 1 as a story within the next epic — enable `target_repo_id` in EdgeInput
2. Design `.raise/contracts.yaml` schema (provider + consumer declarations)
3. Implement `GET /visibility/dependencies` endpoint
4. Validate with Kurigage: Rodo syncs all 3 repos, sees cross-repo dependency matrix
5. Integrate impact analysis into `/rai-story-design` for design-time blast radius
