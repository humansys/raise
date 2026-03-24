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

## Stories (to be redefined)

Previous stories (RAI-67..73) are obsolete — they assumed multi-repo.
New stories needed for monorepo approach:

| ID | Jira | Story | Size | Phase | Blocked By |
|---|---|---|---|---|---|
| S11.1 | ✅ | Jira Migration & Portfolio Organization | M | 1 | — |
| S11.2 | ✅ RAISE-674 | uv Workspace Setup — convert raise-commons to monorepo | M | 2 | — |
| S11.3 | ✅ RAISE-675 | rai-agent Package — move code to packages/rai-agent/ | M | 2 | S11.2 |
| S11.4 | RAISE-676 | CI/CD Workspace — selective pipeline per package | S | 3 | S11.3 |
| S11.5 | RAISE-677 | Distribution Packaging — Docker, license, docs | S | 3 | S11.3 |
| S11.6 | RAISE-678 | Personal Instance Cleanup — remove product code, verify | M | 4 | S11.3, S11.4 |

### Dependency Graph
```
S11.1 ✅
S11.2 ✅── S11.3 ✅──┬── S11.4 ──┬── S11.6
                       └── S11.5   │
```

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| uv workspace breaks existing raise-cli installs | Medium | High | Test editable install before and after restructure |
| CI pipeline complexity for selective publish | Medium | Medium | Start with manual publish, automate later |
| Import tangling between rai-agent and raise-cli | Low | Medium | Same package structure, clear dependency direction |

## Done Criteria
- [ ] raise-commons is a uv workspace monorepo
- [ ] packages/rai-agent/ exists with daemon, knowledge, channels
- [ ] `pip install rai-agent` works from monorepo
- [ ] CI/CD passes for all packages
- [ ] Personal repo has no product code
- [ ] Confluence product docs in humansys
- [ ] RAISE Epics (component rai-agent) linked to STRAT Initiatives ✅
