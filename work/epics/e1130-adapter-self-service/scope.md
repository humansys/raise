# E1130: Adapter Self-Service — Discovery, Doctor, Config Generator

## Objective

Unified self-service configuration for both Jira and Confluence adapters.
A new user runs `/rai-adapter-setup`, answers 3-4 questions, gets validated
YAML config. `rai adapter doctor` catches drift before it causes failures.

## Context

- ADR-015: scoped to 1 session, 1 worktree
- Absorbs deferred E1051 stories (S1051.4 discovery, S1051.5 doctor, S1051.6 generator)
- Jira stories depend on RAISE-1052 (transport must exist first)
- Confluence stories use existing ConfluenceClient from E1051

## Design Decisions

1. **Unified doctor** — `rai adapter doctor` checks both Jira and Confluence in one command
2. **Unified setup skill** — `/rai-adapter-setup` detects available backends, guides both
3. **Discovery is a service, not a CLI** — consumed by doctor and generator, not user-facing
4. **Config generated, not written** — humans never need to know transition IDs (Adapter Vision §3)

## Stories

| # | Story | Size | Description | Origin |
|---|-------|------|-------------|--------|
| S1130.1 | Confluence Discovery Service | S | Query spaces, page trees, labels. Structured space map. | ex-S1051.4 |
| S1130.2 | Jira Backend Discovery | M | Query projects, workflows, transitions, components, versions. | new |
| S1130.3 | Adapter Doctor — unified | M | Validate config vs live backend. Both Jira + Confluence. Integrate into `rai doctor`. | ex-S1051.5 (expanded) |
| S1130.4 | Config Generator — Confluence | M | Discovery → present → human selects → generate valid YAML. | ex-S1051.6 |
| S1130.5 | Config Generator — Jira | M | Same pattern for Jira: discover workflows, transitions → generate jira.yaml. | new |
| S1130.6 | Unified `/rai-adapter-setup` skill | S | Interactive skill orchestrating S1130.4 + S1130.5. Detects installed backends. | new |

## Dependencies

```
S1130.1 (Confluence Discovery) ──┐
                                 ├──→ S1130.3 (Doctor) ──→ S1130.6 (Unified Skill)
S1130.2 (Jira Discovery) ────────┘         │
                                           │
S1130.1 ──→ S1130.4 (Confluence Generator) ┘
S1130.2 ──→ S1130.5 (Jira Generator) ──────┘
```

S1130.1 and S1130.2 can run in parallel.
S1130.4 and S1130.5 can run in parallel after their respective discoveries.

**External:** RAISE-1052 must be merged before S1130.2, S1130.3 (Jira parts), S1130.5.

## Done Criteria

1. `/rai-adapter-setup` on a new repo → 3-4 questions → complete validated config
2. `rai adapter doctor` reports Jira + Confluence health with actionable suggestions
3. Generated config passes doctor validation without edits
4. Existing manually-written configs continue working (backwards compat)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Jira workflow discovery returns unexpected structures | Medium | Medium | E494 spike already validated ACLI JSON; new client validates same fields |
| Doctor false positives annoy users | Low | Medium | Warnings vs errors; only error on confirmed mismatches |
| Setup skill UX too complex | Medium | Low | Keep it to 3-4 questions; advanced options in YAML directly |
