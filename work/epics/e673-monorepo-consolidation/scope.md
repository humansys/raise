# E11: Monorepo Consolidation — Scope

## Objective
Consolidate rai-agent product code into raise-commons monorepo using uv workspaces,
with selective publishing for OSS vs proprietary packages and a single RAISE Jira project.

## Context Change
Originally "Product Separation" (multi-repo). Revised to monorepo after evaluating
team size (5 devs), cross-project Jira friction, and industry patterns (AutoGen, LangChain).
See brief.md for hypothesis.

## Phases

### Phase 1: Portfolio & Backlog Organization ✅
- Portfolio kanban conventions (SAFe 6 mapping)
- STRAT Initiatives with OKR links (STRAT-24..28)
- RAISE Epics with component `rai-agent` linked to Initiatives
- Easy Agile TeamRhythm for cross-project visualization
- Monorepo decision (revised from multi-repo)

### Phase 2: Monorepo Restructure (raise-commons)
- Convert raise-commons to uv workspace root
- Move raise-cli to packages/raise-cli/
- Add packages/rai-agent/ with code from this repo
- Setup workspace-level pyproject.toml
- Ensure existing raise-cli tests/CI still pass

### Phase 3: Distribution & CI
- rai-agent pyproject.toml with extras ([telegram], [gchat], [scheduling])
- CI/CD pipeline aware of workspace packages (selective publish)
- Docker Compose template for rai-agent self-hosting
- Apache 2.0 + CONTRIBUTING.md + AGENTS.md + README

### Phase 4: Personal Instance Cleanup
- Remove product code from this repo (daemon/, knowledge/, inference.py)
- Update this repo to depend on rai-agent package
- Migrate product Confluence docs to humansys
- Verify personal instance works with installed rai-agent

## Stories

| ID | Jira | Story | Size | Phase | Status | Blocked By |
|---|---|---|---|---|---|---|
| S11.1 | ✅ | Jira Migration & Portfolio Organization | M | 1 | ✅ Done | — |
| S11.2 | [RAISE-679](https://humansys.atlassian.net/browse/RAISE-679) | rai-agent Package Manifest | S | 2 | ✅ Done | — |
| S11.3 | [RAISE-674](https://humansys.atlassian.net/browse/RAISE-674) | uv Workspace Setup | M | 2 | ✅ Done | — |
| S11.4 | [RAISE-675](https://humansys.atlassian.net/browse/RAISE-675) | rai-agent Integration | M | 3 | ✅ Done | S11.2, S11.3 |
| S11.5 | [RAISE-676](https://humansys.atlassian.net/browse/RAISE-676) | CI/CD Workspace | S | 4 | ✅ Done | S11.4 |
| S11.6 | [RAISE-677](https://humansys.atlassian.net/browse/RAISE-677) | Distribution Packaging | S | 4 | 🔄 In Progress | S11.4 |
| S11.9 | [RAISE-704](https://humansys.atlassian.net/browse/RAISE-704) | Knowledge Refactor — protocols→raise-core, impl→raise-cli | M | 5 | Backlog | — |
| S11.8 | [RAISE-703](https://humansys.atlassian.net/browse/RAISE-703) | ScaleUp Migration → scaleupagent repo | M | 6 | Backlog | S11.9 |
| S11.7 | [RAISE-678](https://humansys.atlassian.net/browse/RAISE-678) | Personal Instance Cleanup | S | 7 | 🔄 In Progress | S11.8, S11.9 |

### Epic Reopened (2026-03-24)

RAISE-673 was reopened after analysis revealed knowledge/ is framework infrastructure
(raise-core protocols + raise-cli implementation), not agent-specific code. This adds
3 new stories:

- **S11.9 (RAISE-704):** Move knowledge/ protocols (DomainAdapter, DomainHints, GateResult)
  to raise-core and implementation (retrieval engine, gates, discovery, curation) to raise-cli.
  Follows BASE-049: protocols in core, implementations in consumer.
- **S11.8 (RAISE-703):** Extract scaleup/ domain plugin to its own repo
  (https://github.com/lunitomx/scaleupagent) as rai-scaleup package.
- **S11.7 (RAISE-678):** Redefined — now removes ALL code (daemon + knowledge + scaleup)
  from personal repo. Reduced from M to S since it becomes trivial after S11.8 + S11.9.

Also fixed RAISE-698 (bug): rai-agent pyproject.toml was missing entry points,
raise-cli dependency, and had telegram/scheduling as optional instead of core deps.

### Background: E3 Knowledge Infrastructure (RAISE-707)

The knowledge/ and scaleup/ modules were built in E3 (originally LIFE-90, now RAISE-707).
Epic artifacts and research (128 sources, 5 axes) are at:
- `work/epics/e3-scaleup-agent/` — 51 files (brief, design, 9 story lifecycles)
- `work/research/ontology-learning-from-text/` — R0
- `work/research/agentic-kg-construction/` — R1 (personal KGs, 56 sources)
- `work/research/hitl-ontology-curation/` — R2
- `work/research/kg-retrieval-architectures/` — R3
- `work/research/symbolic-graph-retrieval-scoring.md` — R4

### Removed from scope
- RAISE-701 (GHCR publishing) → promoted to separate Epic
- RAISE-702 (One-click deploy) → promoted to separate Epic

### Dependency Graph
```
S11.1 ✅

Phase 2 (parallel):
  S11.2 (rai-personal: manifest) ✅ ──┐
  S11.3 (rai-commons: workspace) ✅ ──┤
                                       ▼
Phase 3:              S11.4 (rai-commons: integration) ✅
                                       │
Phase 4 (parallel):   ┌── S11.5 (CI/CD) ✅
                      └── S11.6 (distro) 🔄
                                       │
Phase 5:              S11.9 (knowledge/ → raise-core + raise-cli)
                                       │
Phase 6:              S11.8 (scaleup/ → scaleupagent)
                                       │
Phase 7:              S11.7 (personal cleanup — trivial after 5+6)
```

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| uv workspace breaks existing raise-cli installs | Medium | High | Test editable install before and after restructure |
| CI pipeline complexity for selective publish | Medium | Medium | Start with manual publish, automate later |
| Import tangling between rai-agent and raise-cli | Low | Medium | Same package structure, clear dependency direction |
| knowledge/ refactor breaks existing knowledge CLI users | Medium | Medium | Maintain `rai knowledge` command surface unchanged |
| scaleup/ import paths change | Low | Low | scaleupagent is single-consumer (personal instance) |

## Done Criteria
- [x] raise-commons is a uv workspace monorepo
- [x] packages/rai-agent/ exists with daemon
- [ ] knowledge/ protocols in raise-core, implementation in raise-cli
- [ ] `pip install rai-agent` works from monorepo
- [x] CI/CD passes for all packages
- [ ] scaleup/ in scaleupagent repo as rai-scaleup package
- [ ] Personal repo has no product or domain code
- [x] RAISE Epics (component rai-agent) linked to STRAT Initiatives
