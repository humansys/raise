# Evidence Catalog: Domain Cartridge Architecture

> Research date: 2026-03-22
> Sources: 30+ across 3 research tracks
> Methodology: 3 parallel agents, triangulated findings

---

## Track 1: Schema-Driven Consistency Patterns

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| 1 | [Data Contract Specification](https://datacontract-specification.com/) | Primary | **Very High** | YAML-based open standard defining schema + servers + quality rules. CLI validates against 20+ backends. Most aligned with our needs |
| 2 | [dbt Model Contracts](https://docs.getdbt.com/docs/mesh/govern/model-contracts) | Primary | **Very High** | Build-time schema enforcement via YAML. When `contract.enforced: true`, breaking changes cause failures. Warehouse-specific |
| 3 | [Apicurio Registry](https://www.apicur.io/registry/) | Primary | **High** | Multi-format schema registry (Avro, JSON Schema, OpenAPI, GraphQL). Pluggable storage. Rule-based evolution governance. CNCF Sandbox |
| 4 | [Specmatic](https://specmatic.io/) | Primary | **High** | OpenAPI spec as executable contract. Schema IS the test. No code needed. Aligns with "schema-as-enforcement" |
| 5 | [Pydantic TypeAdapter](https://docs.pydantic.dev/latest/concepts/type_adapter/) | Primary | **High** | Runtime contract enforcement at adapter boundary. Already in our stack. Protocol support still missing |
| 6 | [Palantir Foundry Ontology](https://www.palantir.com/docs/foundry/ontology/overview) | Primary | **Medium** | Semantic abstraction over heterogeneous data. Ontology IS the schema at business-meaning level. Proprietary but pattern transferable |
| 7 | [Great Expectations](https://docs.greatexpectations.io/) | Primary | **High** | Python-native data validation. Expectation suites across heterogeneous sources. Complements schema enforcement |
| 8 | [Pact Consumer-Driven Contracts](https://docs.pact.io/) | Primary | **High** | Contract-by-example approach. Less aligned than schema-driven (Specmatic) for our use case |

## Track 2: Pluggable Knowledge Architectures

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| 9 | [Apache Jena Ontology API](https://jena.apache.org/documentation/ontology/) | Primary | **Very High** | Three-axis pluggable config (language x storage x reasoning). Union graph for modular imports. Load/unload independently |
| 10 | [Apollo Federation](https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/composition) | Primary | **Very High** | Independent schema modules + static composition with conflict detection. `@key` for cross-module entity linking. Build-time validation |
| 11 | [Backstage Software Catalog](https://backstage.io/docs/features/software-catalog/) | Primary | **Very High** | EntityProvider owns bucket of entities. Processors enrich unconditionally. Extension Points for pluggability. Closest prior art |
| 12 | [Haystack 2.0 Pipelines](https://docs.haystack.deepset.ai/docs/pipelines) | Primary | **High** | Typed input/output contract + assembly-time validation + YAML serialization. Composable pipeline graphs |
| 13 | [LlamaIndex Llama Packs](https://developers.llamaindex.ai/python/framework/community/llama_packs/) | Primary | **High** | Self-contained template modules with introspectable internals. Dual-mode: run-as-is or decompose-and-recombine |
| 14 | [KGTK](https://github.com/usc-isi-i2/kgtk) | Academic | **High** | Universal flat interchange format (4-col TSV). Zero-ceremony pipeline composition. Peer-reviewed (ISWC 2020) |
| 15 | [Ontology Design Patterns (ODPs)](http://www.ontologydesignpatterns.org/) | Academic | **High** | Reusable ontology modules. Template instantiation + alignment mappings. W3C community |
| 16 | [Amazon Neptune Data Lens](https://aws.amazon.com/blogs/database/build-a-knowledge-graph-in-amazon-neptune-using-data-lens/) | Secondary | **Medium-High** | Containerized pluggable transformers orchestrated by workflow engine. Visual schema-first design |

## Track 3: Work-as-Knowledge Patterns

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| 17 | [Backstage System Model](https://backstage.io/docs/features/software-catalog/system-model/) | Primary | **Very High** | Domain→System→Component hierarchy. Typed directional relations. Extensible kinds. K8s-inspired descriptor format |
| 18 | [GitLab Work Items](https://docs.gitlab.com/development/work_items/) | Primary | **Very High** | Unified work item framework. Type = composition of widgets. Up to 7 levels nesting. Value Stream Analytics treats items as flow units |
| 19 | [Linear GraphQL API](https://linear.app/developers/graphql) | Primary | **High** | All work items are graph nodes with typed relationships. Team-scoped (not project-scoped). Two-axis model |
| 20 | [Notion Data Model](https://www.notion.com/blog/data-model-behind-notion) | Primary | **High** | Everything is a block. Databases = containers with typed properties. Relations + rollups. Federated data sources (2025) |
| 21 | [Atlassian Rovo / Teamwork Graph](https://www.atlassian.com/software/rovo) | Primary | **High** | Overlay graph across Jira/Confluence/50+ apps. Search, Chat, Agents grounded in graph. Included in Cloud subscriptions 2025 |
| 22 | [DDD Bounded Contexts](https://martinfowler.com/bliki/BoundedContext.html) | Foundational | **Very High** | Same entity, different schema per context. Anti-Corruption Layer for translation. Published Language for shared contracts |
| 23 | [Dublin Core + SKOS](https://www.dublincore.org/resources/metadata-basics/) | Standard | **Very High** | W3C standards for metadata vocabularies. 25+ years of adoption. Compose from standardized vocabularies with URIs |
| 24 | [Obsidian Dataview](https://github.com/blacksmithgu/obsidian-dataview) | Primary | **High** | Annotation-based metadata on plain text creates queryable graph. No separate database. Content + data coexist |

---

## Triangulation Matrix

Claims validated by 3+ independent sources:

| Claim | Sources | Confidence |
|-------|---------|------------|
| **Typed entities + typed relations = queryable graph** is the universal pattern | Backstage, Linear, Notion, GitLab, Rovo, Jena | **HIGH** |
| **Schema-as-contract** enforced at adapter boundary is SOTA for consistency | Data Contract Spec, dbt, Specmatic, Pydantic, Apicurio | **HIGH** |
| **Composition over rigid schema** — entity type defined by capabilities, not fixed fields | GitLab widgets, Notion properties, Backstage extensible kinds, DDD | **HIGH** |
| **Overlay graph** over existing data (no migration) is preferred over data consolidation | Rovo Teamwork Graph, Obsidian Dataview, SKOS/Dublin Core | **HIGH** |
| **Provider-owns-bucket isolation** prevents cross-source contamination | Backstage EntityProvider, Apollo Federation subgraphs, Jena sub-graphs | **HIGH** |
| **Build-time/assembly-time validation** catches conflicts before runtime | Apollo composition, Haystack assembly, dbt contracts, Specmatic | **HIGH** |
| **Anti-corruption layers** needed when same concept has different schema per context | DDD ACL, Backstage processors, Apollo `@key` entity resolution | **HIGH** |

## Contrary Evidence / Tensions

| Tension | Sources | Implication |
|---------|---------|-------------|
| Pydantic lacks native Protocol support | Pydantic issues #8007, #10161 | Can't use `typing.Protocol` as Pydantic field type — use abstract base classes or structural subtyping instead |
| Schema enforcement varies by platform | dbt docs (Snowflake only enforces `not_null`) | Backend-specific constraints may not be fully enforceable — validation must be at adapter level, not delegated to backend |
| ODP composition requires manual alignment | ODPs literature | Fully automatic ontology composition remains unsolved — domain cartridge schema alignment may need human curation step |
| DDD suggests different schemas per context, NOT unified | Fowler, Evans | A single canonical schema may be an anti-pattern — consider per-cartridge schemas with explicit translation at boundaries |
