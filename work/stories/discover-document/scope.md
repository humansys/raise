# Story Scope: discover-document

**Branch:** `story/discover-document`
**Parent:** `v2` (standalone — no active epic)
**Sizing:** M (skill + CLI infrastructure + template)
**Priority:** F&F critical path — architecture doc generation

---

## In Scope

1. **`/discover-document` skill** — Orchestrates documentation generation from discovery data
2. **`rai discover document` CLI command** — Deterministic generation of architecture docs
3. **Jinja2 template** for architecture overview (Mermaid diagrams, module catalog, dependency flow)
4. **Output:** `dev/architecture-overview.md` — human-readable, onboarding-ready

## Out of Scope

- Auto-refresh cycle (future: `rai discover refresh` wrapper)
- Non-Python language support
- Integration with external doc systems (Confluence, etc.)
- Interactive/web-based documentation viewer

## Inputs (Already Available)

- `work/discovery/components-validated.json` — 309 validated components
- `work/discovery/analysis.json` — module groups, hierarchy, confidence tiers
- `work/discovery/context.yaml` — project type, languages, directories
- `.raise/rai/memory/index.json` — 787 graph concepts, 4739 relationships

## Done Criteria

- [ ] `rai discover document` generates `dev/architecture-overview.md`
- [ ] Output includes: module overview, component catalog by concern, dependency flow, entry points, Mermaid diagrams
- [ ] Skill `/discover-document` works end-to-end
- [ ] Tests pass (>90% coverage on new code)
- [ ] Dogfood: generated doc for raise-commons is useful and accurate
- [ ] Retrospective complete
