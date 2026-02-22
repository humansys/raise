---
epic_id: "RAISE-211"
title: "Adapter Foundation"
status: "draft"
created: "2026-02-22"
---

# Epic Brief: Adapter Foundation

## Hypothesis
For raise-cli developers who need extensibility beyond local-only governance,
the Adapter Foundation is an infrastructure layer
that provides Protocol contracts, entry point discovery, and tier-aware capability detection.
Unlike the current monolithic architecture where all parsers and backends are hardcoded,
our solution enables raise-pro to plug in commercial adapters without modifying core code.

## Success Metrics
- **Leading:** S211.1 Protocol contracts importable and type-checked by pyright in strict mode
- **Lagging:** `rai memory build` produces byte-identical output via registry path vs current hardcoded path

## Appetite
M — 6 stories. Foundation infrastructure that three downstream epics depend on (RAISE-207, RAISE-208, RAISE-209).

## Scope Boundaries

### In (MUST)
- Protocol contracts for all adapter types (PM, Governance, Graph, Tier)
- Entry point registry with importlib.metadata discovery
- FilesystemGraphBackend as built-in (current behavior, refactored)
- TierContext with progressive enrichment (no feature gating)
- Zero regression on existing `rai memory build` output

### In (SHOULD)
- `rai adapters list/check` CLI commands
- Refactor governance parsers to register as entry points

### No-Gos
- No concrete PRO adapters — those live in raise-pro packages
- No network calls in core — all remote capability is in PRO adapters
- No breaking changes to existing CLI commands or output formats
- No feature gating that disables COMMUNITY functionality

### Rabbit Holes
- Over-engineering the registry with plugin lifecycle (load/unload/reload) — simple discovery is enough
- Building adapter validation framework before we have real adapters to validate
- Premature abstraction of config management (manifest.yaml is sufficient for tier detection)
- Trying to make entry points work without installing the package (editable installs are fine)

## ADR Foundation
| ADR | Concept | Status |
|-----|---------|--------|
| ADR-033 | Open-core adapter architecture | Accepted |
| ADR-034 | Governance extensibility | Accepted |
| ADR-035 | Backend deployment topology | Accepted |
| ADR-036 | KnowledgeGraphBackend | Accepted |
| ADR-037 | TierContext | Accepted |

## Dependencies
**This epic enables:**
- RAISE-207: Repo separation (code boundary is now in Protocol contracts)
- RAISE-208: Jira adapter in raise-pro (ProjectManagementAdapter Protocol exists)
- RAISE-209: Team memory (KnowledgeGraphBackend Protocol exists for SupabaseGraphBackend)

**Note on RAISE-141:** RAISE-141's "BacklogProvider" is subsumed by ProjectManagementAdapter in ADR-033. S211.1 captures that architectural decision.
