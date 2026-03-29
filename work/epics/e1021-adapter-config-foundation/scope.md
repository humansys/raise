# E1021: Adapter Configuration Foundation

## Objective

Make adapter configuration reliable by generating it from live backend discovery
instead of requiring manual hand-written YAML with transition IDs, component names,
and page hierarchies.

## In Scope

1. **Jira Backend Discovery** — query Jira API to produce a complete backend map
   (projects, workflows, transition IDs, issue types, components, versions)
2. **Confluence Backend Discovery** — query Confluence for spaces, page trees, templates
3. **Config Generator (`/rai-adapter-setup`)** — interactive skill that generates correct YAML
4. **Adapter Doctor (`rai adapter doctor`)** — validate config against live backend, report mismatches
5. **Confluence Config Schema** — artifact-type routing, parent pages, templates, labels
6. **Jira Multi-Project Routing** — per-project config, resolved from issue key prefix

## Out of Scope

- Adapter Protocol changes (RAISE-1022)
- Telemetry and degradation handling (RAISE-1023)
- Local persistence adapters (RAISE-1040)
- Webhook/automation configuration
- Multi-instance Jira support

## Planned Stories (draft — refined in /rai-epic-design)

1. S1021.1: Jira backend discovery service
2. S1021.2: Confluence backend discovery service
3. S1021.3: Config generator skill (`/rai-adapter-setup`)
4. S1021.4: Adapter doctor command (`rai adapter doctor`)
5. S1021.5: Confluence config schema + artifact-type routing
6. S1021.6: Jira multi-project routing

## Done Criteria

- `/rai-adapter-setup` generates valid `.raise/jira.yaml` from live Jira discovery
- `/rai-adapter-setup` generates valid `.raise/confluence.yaml` with routing rules
- `rai adapter doctor` detects and reports config-vs-backend mismatches
- Multi-project routing resolves project from issue key prefix
- All existing adapter tests continue passing

## Design References

- `governance/product/adapter-vision.md` §3 (Configuration Model)
- `governance/product/adapter-backlog-v2.md` Epic 1
