# Story Scope: S-RELEASE-ONTOLOGY

> **Status:** IN PROGRESS
> **Branch:** `story/standalone/s-release-ontology`
> **Size:** S
> **Created:** 2026-02-13

## Objective

Add `release` as a first-class concept in the RaiSE ontology, enabling epics to be grouped under release targets (e.g., REL-V3.0). This is a prerequisite for all V3 release planning.

## In Scope

- Add `release` to `NodeType` (context/models.py)
- Add `RELEASE` to `ConceptType` (governance/models.py)
- Add `governance/roadmap.md` governance artifact template
- Write roadmap parser (follows backlog parser pattern)
- Wire parser into governance extractor
- `part_of` edges: epic → release in graph builder
- Tests for parser, extractor wiring, and graph edges
- Initial `governance/roadmap.md` with REL-V3.0 defined

## Out of Scope

- CLI commands for release management (future)
- Release-specific queries in query engine (future)
- V3 epic formal scoping (E19-E22 — happens after this)
- Jira Fix Version sync (E21 scope)
- Migration of existing epics to releases (manual for now)

## Done Criteria

- [ ] `release` exists in `NodeType` and `ConceptType`
- [ ] `governance/roadmap.md` exists with proper structure
- [ ] Roadmap parser extracts releases and epic associations
- [ ] Graph builder creates release nodes and part_of edges
- [ ] Tests pass (>90% coverage on new code)
- [ ] `pyright` and `ruff check` pass
- [ ] Graph rebuild includes release nodes
- [ ] Retrospective complete
