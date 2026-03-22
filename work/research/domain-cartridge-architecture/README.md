# Research: Domain Cartridge Architecture

> **Date:** 2026-03-22
> **Researcher:** Emilio + Rai
> **Decision:** ADR for unified cartridge runtime in raise-core
> **Depth:** Standard
> **Status:** In Progress

## Research Question

Is there prior art for a unified "cartridge" pattern that treats knowledge domains, work management, and governance artifacts as pluggable, schema-validated modules with interchangeable backends?

## Secondary Questions

1. What are the SOTA patterns for schema-driven consistency enforcement across heterogeneous data sources?
2. How do existing KG construction pipelines handle pluggable ontologies with validation gates?
3. Is there precedent for treating project management data as a queryable knowledge domain?
4. What adapter patterns enforce data contracts regardless of backend type?

## Genesis

During a backlog management session (2026-03-22), we realized that:
- RAISE-650 (Domain Cartridges) and RAISE-651 (Graph Data Abstraction) share the same underlying pattern
- Work items (Jira), governance docs (Confluence), and knowledge (ontology nodes) all need: schema, adapter, gates, consistency enforcement
- The "managers" in the graph builder are really cartridge runtimes
- The metadata standards for Jira/Confluence are actually machine-readable schemas for the Work and Governance cartridges

## Artifacts

- [Evidence Catalog](sources/evidence-catalog.md)
- [Research Report](domain-cartridge-architecture-report.md) (pending)

## Feeds Into

- ADR: Domain Cartridge Architecture (to be created)
- RAISE-650: Domain Cartridges
- RAISE-651: Graph Data Abstraction
- `governance/jira-confluence-standards.md` → evolves to `work-schema.yaml`
