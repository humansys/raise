# R2: Modular and Pluggable Ontologies

## Research Question

What prior work exists on modular, composable, or pluggable ontology systems? How do they handle schema composition, cross-domain references, versioning, and conflict resolution?

**Context:** We are building "Knowledge Cartridges" — self-contained, pluggable domain knowledge modules. Each cartridge declares its own schema (Pydantic models defining node types and relationships), corpus sources, validation rules (competency questions), and a domain adapter (query interpretation). Cartridges are discovered by convention (`.raise/domains/*/domain.yaml`) and loaded dynamically via Python's import system.

---

## Evidence Catalog

### Source 1: Modular Ontology Modeling (MOMo)
- **Authors/Org:** Cogan Shimizu, Karl Hammar, Pascal Hitzler (Wright State / Kansas State University)
- **Year:** 2023
- **URL:** https://journals.sagepub.com/doi/10.3233/SW-222886
- **Type:** paper (peer-reviewed, Semantic Web Journal)
- **Evidence Level:** Very High
- **Key Finding:** MOMo is a complete methodology for building ontologies as compositions of modular design patterns. It builds on eXtreme Design (XD) but adds graphical schema diagrams as the primary knowledge elicitation vehicle. Modules are self-contained ontology design patterns with explicit external interfaces. Modules connect through "hooks" — typed attachment points that define how one pattern links to another. The methodology addresses four core problems: representational granularity mismatches, lacking conceptual clarity, poor modeling principles adherence, and insufficient reuse emphasis in tooling.
- **Relevance to our work:** Direct architectural analog. MOMo's "modules as patterns with explicit interfaces" maps closely to our cartridge concept. Their schema diagrams parallel our Pydantic model declarations. The hook/interface mechanism informs how cartridges should declare cross-domain attachment points.

### Source 2: MODL — Modular Ontology Design Library
- **Authors/Org:** Cogan Shimizu, Quinn Hirt, Pascal Hitzler
- **Year:** 2019
- **URL:** https://arxiv.org/abs/1904.05405
- **Type:** paper (workshop, WOP 2019 at ISWC)
- **Evidence Level:** High
- **Key Finding:** MODL is a curated collection of well-documented ontology design patterns organized into five categories: metapatterns, organization of data, space/time/movement, agents and roles, description and details. Each pattern is specified in OWL with accompanying documentation. Pattern annotations maintain provenance so modules can be manipulated as units. The library makes patterns findable, accessible, interoperable, and reusable (FAIR). Patterns serve as composable building blocks for larger ontologies.
- **Relevance to our work:** MODL's categorization scheme and FAIR documentation approach is a model for our cartridge registry. Their five categories suggest a useful starting taxonomy for domain cartridges. The provenance annotation approach maps to our `domain.yaml` metadata.

### Source 3: Survey of Modular Ontology Techniques (Biomedical Domain)
- **Authors/Org:** Jyotishman Pathak, Thomas M. Johnson, Christopher G. Chute (Mayo Clinic)
- **Year:** 2009
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC3113511/
- **Type:** paper (peer-reviewed survey)
- **Evidence Level:** Very High
- **Key Finding:** Comprehensive taxonomy dividing modular ontology approaches into two camps: (1) Logic-based (DDL, E-Connections, P-DL, Conservative Extensions / locality-based) which guarantee semantic correctness but require non-standard semantics; (2) Graph-based (GALEN, ModTool, PATO) which are tractable and intuitive but sacrifice semantic guarantees. Key distinction: ontology decomposition (extracting modules from monoliths) vs. ontology composition (building from independent modules). Integrating modules must not induce new relationships between existing concepts in any module. Traditional reasoners were designed for single ontologies, not multiple.
- **Relevance to our work:** The decomposition vs. composition distinction is critical — our cartridges are a composition approach. The constraint that "integrating modules cannot induce new relationships between existing concepts" is a design principle we should adopt. The logic-based vs. graph-based trade-off maps to how strict our cartridge composition validation should be.

### Source 4: OBO Foundry — Coordinated Evolution of Ontologies
- **Authors/Org:** Barry Smith, Michael Ashburner, et al. (16+ contributors)
- **Year:** 2007 (foundational paper), updated 2021
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC2814061/ and https://academic.oup.com/database/article/doi/10.1093/database/baab069/6410158
- **Type:** paper (peer-reviewed, Nature Biotechnology / Database)
- **Evidence Level:** Very High
- **Key Finding:** OBO Foundry coordinates 100+ biomedical ontologies via voluntary acceptance of shared principles: open, orthogonal (no term duplication across ontologies), well-specified syntax, shared identifier space. Orthogonality is enforced by consolidating overlapping ontologies (e.g., multiple cell-type ontologies merged into one Cell Ontology). Cross-ontology references use the Relation Ontology (RO) with standardized relations (is_a, part_of). Governance is consensus-based with coordinator-editors. Foundry principles have been encoded as automated validation checks with a compliance dashboard. Versioning requires procedures for identifying successive versions.
- **Relevance to our work:** OBO Foundry's orthogonality principle (each domain exactly once) directly maps to our cartridge design — each cartridge owns a non-overlapping domain. Their automated compliance dashboard is a model for our cartridge validation. The Relation Ontology pattern (shared cross-cutting relations) informs how we handle cross-cartridge references.

### Source 5: MIREOT — Minimum Information to Reference External Ontology Terms
- **Authors/Org:** Melanie Courtot, Frank Gibson, Allyson Lister, James Malone, Daniel Schober, Ryan Brinkman, Alan Ruttenberg
- **Year:** 2011
- **URL:** https://journals.sagepub.com/doi/10.3233/AO-2011-0087
- **Type:** paper (peer-reviewed, Applied Ontology)
- **Evidence Level:** Very High
- **Key Finding:** MIREOT defines the minimum information needed to reference a term from an external ontology: (1) source ontology URI, (2) source term URI, (3) target direct superclass URI. This enables selective import — taking only the terms you need rather than importing entire ontologies. OWL's owl:imports is all-or-nothing, which is impractical for large ontologies and can cause inconsistencies. MIREOT recommends also reusing labels and textual descriptions for human readability. Implemented in OntoFox (web tool) and a Protege plugin.
- **Relevance to our work:** MIREOT's selective import approach is essential for cartridge cross-references. A cartridge referencing concepts from another should use MIREOT-style minimal references (type URI + parent type) rather than importing the entire foreign schema. This keeps cartridges loosely coupled.

### Source 6: Distributed Ontology Language (DOL)
- **Authors/Org:** Christoph Lange, Oliver Kutz, Till Mossakowski, Michael Gruninger
- **Year:** 2012
- **URL:** https://arxiv.org/abs/1204.5093
- **Type:** paper (peer-reviewed, CICM 2012, OMG standard)
- **Evidence Level:** High
- **Key Finding:** DOL provides a unified metalanguage for heterogeneous ontology integration. Rather than creating one comprehensive language, DOL accepts diverse formalisms (OWL, Common Logic, etc.) and provides meta-level constructs for: imports, alignments, conservative extensions, and theory interpretations. A DOL library consists of modules in different base languages. The Heterogeneous Tool Set (Hets) enables checking coherence, consistency, conservativity, intended consequences, and compliance. DOL is an OMG specification (ISO/TC 37/SC 3).
- **Relevance to our work:** DOL's approach of a metalanguage over heterogeneous modules is philosophically aligned with our cartridge architecture — cartridges can use different internal representations but declare a common interface. The coherence checking constructs map to our validation rules.

### Source 7: E-Connections and Distributed Description Logics
- **Authors/Org:** Bernardo Cuenca Grau, Bijan Parsia, Evren Sirin (U. Manchester / U. Maryland)
- **Year:** 2004-2009
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S1570826805000314 and https://link.springer.com/chapter/10.1007/978-3-642-01907-4_15
- **Type:** paper (peer-reviewed)
- **Evidence Level:** High
- **Key Finding:** Two formal approaches to modular ontologies: (a) E-Connections keep ontologies small and disjoint, connected via typed "link properties" between modules; modules must have strictly disjoint domains. (b) Distributed Description Logics (DDL) use "bridge rules" as inter-module connectives; each module preserves its identity and independence. P-DL (Package-based DL) adds selective importing with transitive knowledge reuse. Key distinction: mappings/linkings (DDL, E-Connections) vs. importing (P-DL). E-Connections require domain disjointness; DDL allows overlap via bridge rules.
- **Relevance to our work:** E-Connections' strict domain disjointness maps to our desired cartridge orthogonality. Bridge rules in DDL are a model for cross-cartridge reference declarations. P-DL's selective importing with transitive reuse is the most flexible — a cartridge importing from another can re-export those concepts to a third.

### Source 8: NeOn Methodology for Ontology Networks
- **Authors/Org:** Mari Carmen Suarez-Figueroa, Asuncion Gomez-Perez, Mariano Fernandez-Lopez (UPM)
- **Year:** 2009-2015
- **URL:** https://oeg.fi.upm.es/index.php/en/methodologies/59-neon-methodology/index.html
- **Type:** paper / methodology (peer-reviewed, multiple publications)
- **Evidence Level:** High
- **Key Finding:** NeOn provides a scenario-based methodology with 9 scenarios covering: re-engineering, alignment, modularization, localization, and integration with design patterns and non-ontological resources. It does not prescribe a rigid workflow but offers pathways. Key innovation: treating ontology networks (not single ontologies) as the unit of development. Supports reusing both ontological and non-ontological resources. Enables continuous evolution in collaborative, distributed environments.
- **Relevance to our work:** NeOn's concept of "ontology networks as the development unit" parallels our collection of cartridges as a knowledge network. The scenario-based approach (different paths for different situations) could inform our cartridge development workflows. The emphasis on reusing non-ontological resources (thesauri, folksonomies) maps to our corpus sources.

### Source 9: Schema.org Extension Mechanisms
- **Authors/Org:** Schema.org community (Google, Microsoft, Yahoo, Yandex founding)
- **Year:** 2011-present (extension mechanism revised 2019)
- **URL:** https://schema.org/docs/extension.html
- **Type:** docs / specification
- **Evidence Level:** High
- **Key Finding:** Schema.org uses three extension mechanisms: (1) Hosted extensions — subdomains (bib.schema.org, autos.schema.org) for community-vetted domain vocabulary; content was folded into core in 2019. (2) Pending terms — staging area for terms under discussion; eventually incorporated or dropped. (3) External extensions — third parties host their own (e.g., gs1.org/voc). Additional mechanisms include PropertyValue for arbitrary key-value pairs and the Role mechanism for annotation. JSON-LD and RDFa support mixing independent schemas.
- **Relevance to our work:** Schema.org's lifecycle (pending → hosted → core) is a model for cartridge maturity. The external extension pattern (third parties host their own) validates our cartridge-as-installable-package approach. The property value escape hatch (arbitrary key-value) warns against — we should enforce typed schemas.

### Source 10: Apollo Federation (GraphQL Schema Composition)
- **Authors/Org:** Apollo GraphQL
- **Year:** 2019-present
- **URL:** https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/composition
- **Type:** docs / industry practice
- **Evidence Level:** High
- **Key Finding:** Apollo Federation composes subgraph schemas into a supergraph schema. Each subgraph defines which types/fields it can resolve — teams define these manually. Composition is the process of merging subgraphs plus adding routing metadata. Conflicts fail composition intentionally (e.g., same field with different types). The `@shareable` directive enables shared type ownership. Composition rules are formally specified. Schema linting catches issues pre-publish. Incremental adoption is supported — monolith → federated, one service at a time.
- **Relevance to our work:** Apollo Federation is the closest industry analog to our cartridge composition. Their "composition fails on conflict" approach should be our default. The `@shareable` directive (explicit shared ownership) informs how cartridges declare re-exported types. Incremental adoption support is essential — our system must work with one cartridge and scale to many.

### Source 11: Backstage Software Catalog — Extending the Model
- **Authors/Org:** Spotify / Backstage open source project
- **Year:** 2020-present
- **URL:** https://backstage.io/docs/features/software-catalog/extending-the-model/
- **Type:** docs / industry practice
- **Evidence Level:** High
- **Key Finding:** Backstage allows extending the entity model with new kinds via: (1) TypeScript type + JSONSchema schema definition, (2) Organization-namespaced apiVersion (e.g., `my-company.net/v1`), (3) Processor-based validation pipeline, (4) Entity providers for discovery. Relations form directed graphs between entities. Custom processors handle validation, post-processing, and relation emission via `catalogProcessingExtensionPoint`. Warning: custom kinds can break existing plugins that hardcode type checks. Metadata and spec fields are open for extension without schema changes.
- **Relevance to our work:** Backstage's pattern of "schema (TypeScript type + JSONSchema) + processor + discovery" maps directly to our cartridge structure (Pydantic model + domain adapter + convention-based discovery). Their warning about custom kinds breaking plugins is relevant — our cartridge system must handle unknown types gracefully.

### Source 12: Wikidata — Property Constraints and Entity Schemas
- **Authors/Org:** Wikimedia Foundation / Wikidata community
- **Year:** 2012-present
- **URL:** https://www.wikidata.org/wiki/Wikidata:WikiProject_Schemas and https://www.wikidata.org/wiki/Help:Property_constraints_portal
- **Type:** docs / community practice
- **Evidence Level:** High
- **Key Finding:** Wikidata handles multi-domain knowledge through: (1) Property constraints as hints (not hard restrictions), including type constraints, single-value constraints, etc. — community-defined rules resembling RDFS axioms. (2) Entity Schemas using Shape Expressions (ShEx) to describe expected structure. (3) Constraints as guidance rather than enforcement, enabling broad community contribution while maintaining quality signals. This enables integrative queries spanning multiple domain areas without time-consuming data integration steps.
- **Relevance to our work:** Wikidata's "constraints as hints" approach may be too loose for our cartridge validation (we want hard schemas). However, their ShEx-based entity schemas demonstrate how to declare expected structure for entities — analogous to our Pydantic models. Their success with multi-domain integration validates the general approach.

### Source 13: Data Mesh Principles
- **Authors/Org:** Zhamak Dehghani
- **Year:** 2020
- **URL:** https://martinfowler.com/articles/data-mesh-principles.html
- **Type:** blog / architecture (foundational article)
- **Evidence Level:** High
- **Key Finding:** Four principles: domain-oriented decentralized ownership, data as a product, self-serve platform, federated computational governance. Polysemes (concepts crossing domain boundaries) are handled by global governance defining standardized identifiers. Cross-domain references use unified identification from upstream bounded contexts. Governance shifts from "responsible for global canonical data modeling" to "responsible for modeling polysemes." Domains retain local control but comply with global interoperability standards.
- **Relevance to our work:** Data mesh's federated governance model directly informs our cartridge governance. The polyseme concept (cross-boundary entities) is exactly our cross-cartridge reference problem. Their solution — global governance for boundary-crossing concepts, local ownership for domain internals — should be our approach.

### Source 14: dbt Model Contracts and Packages
- **Authors/Org:** dbt Labs
- **Year:** 2023-present
- **URL:** https://docs.getdbt.com/docs/collaborate/govern/model-contracts
- **Type:** docs / industry practice
- **Evidence Level:** Medium
- **Key Finding:** dbt model contracts guarantee shape (column names, types, constraints) before building — proactive schema enforcement. Models reference each other via `ref()` function. Cross-project references use packages. Governance features: public/private model visibility, model versioning for breaking changes, group-based ownership boundaries. Contracts check schema before data is written, failing the build on mismatch.
- **Relevance to our work:** dbt's contract system (shape guarantee before build) directly maps to our cartridge validation gates. Their `ref()` function for cross-model references is analogous to cross-cartridge type references. Model versioning for breaking changes is essential for cartridge evolution. Public/private visibility maps to cartridge export declarations.

### Source 15: LinkML — Linked Data Modeling Language
- **Authors/Org:** Chris Mungall, Harold Solbrig, et al. (Lawrence Berkeley National Lab)
- **Year:** 2022-2025
- **URL:** https://linkml.io/ and https://academic.oup.com/gigascience/article/doi/10.1093/gigascience/giaf152/8378082
- **Type:** docs / paper (GigaScience 2025)
- **Evidence Level:** High
- **Key Finding:** LinkML provides a polyglot schema language with: schema imports for modular composition, first-class slots (fields) defined independently and usable across classes, class inheritance via `is_a` and `mixins`, prefix/namespace management for semantic disambiguation. LinkML-Map provides declarative syntax for schema transformations across versions (subsetting, renaming, restructuring). The Biolink Model demonstrates LinkML at scale for cross-domain biological data integration.
- **Relevance to our work:** LinkML's approach is very close to our needs — schemas defined in YAML, importable across modules, with independent slot definitions. Their prefix management maps to our namespace handling. LinkML-Map for version transformations is a feature we will eventually need for cartridge evolution.

### Source 16: Ontology Conflict Resolution Framework
- **Authors/Org:** C. Maria Keet, Rolf Grutter (U. Cape Town / Swiss Federal Research Institute)
- **Year:** 2021
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC8352153/
- **Type:** paper (peer-reviewed, J. Biomedical Semantics)
- **Evidence Level:** High
- **Key Finding:** Identifies 10 conflict categories in three groups: (1) Top-level theory conflicts (foundational ontology choice, mereology, topology, embedded language commitments), (2) Domain-level conflicts (competing scientific views), (3) Axiom/language conflicts (profile violations, undecidability, incoherence, modeling style, linguistic variations). Distinguishes meaning negotiation (figuring out what to represent) from conflict resolution (choosing among incompatible options). Proposes a conflict set data structure in BNF. Resolution principles: prefer least expressive suitable language, capture maximum domain semantics, maintain decidability.
- **Relevance to our work:** This taxonomy of conflicts directly informs what our cartridge composition validator must check. Modeling style conflicts (class vs. property representation) will arise between cartridges. The meaning negotiation vs. conflict resolution distinction is important — some cross-cartridge disagreements are design choices (negotiation), others are hard errors (resolution).

### Source 17: Competency Questions for Ontology Validation
- **Authors/Org:** Dawid Wisniewski, Jedrzej Potoniec, Agnieszka Lawrynowicz, C. Maria Keet
- **Year:** 2019
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S1570826819300617
- **Type:** paper (peer-reviewed, J. Web Semantics)
- **Evidence Level:** High
- **Key Finding:** Competency questions (CQs) are natural language questions constraining ontology scope. 234 CQs were formalized into 131 SPARQL-OWL queries across diverse ontologies, identifying 106 distinct CQ patterns. One CQ pattern may map to multiple query signatures and vice versa. CQs serve as ontology test cases — analogous to unit tests. Five CQ types: Scoping, Validating, Foundational, Relationship, and Metaproperty questions. CQ-driven Ontology Authoring (CQOA) provides continuous validation during development.
- **Relevance to our work:** Our cartridge "validation rules (competency questions)" design is directly supported by this research. CQs-as-tests is an established pattern. We should support both natural language CQs and their formalized query equivalents. The five CQ types can structure our validation rule categories.

### Source 18: OWL Module Interface Proposals
- **Authors/Org:** Jie Bao, George Voutsadakis, Vasant Honavar (Iowa State University)
- **Year:** 2006-2009
- **URL:** https://ceur-ws.org/Vol-216/submission_28.pdf and http://webont.org/owled/2009/papers/owled2009_submission_10.pdf
- **Type:** paper (workshop)
- **Evidence Level:** Medium
- **Key Finding:** OWL's `owl:imports` is all-or-nothing — no granular control over which axioms are imported. Proposals for adapting OWL as a modular language introduce: selective module boundaries with explicit interfaces, specification of which components are for external use vs. internal, semantic importing (`owlx:semanticImports`) alongside syntactic importing. Nested locality-based modules (bottom-star modules) implemented in OWL API provide approximations of minimal coverage modules.
- **Relevance to our work:** The all-or-nothing limitation of `owl:imports` validates our cartridge design decision to declare explicit exports. Cartridges should have a clear public interface (exported types/relations) vs. internal implementation. The semantic vs. syntactic import distinction is relevant for our cross-cartridge reference mechanism.

### Source 19: Ontology Alignment Evaluation Initiative (OAEI)
- **Authors/Org:** OAEI community (INRIA, various universities)
- **Year:** 2004-2025 (annual campaign)
- **URL:** http://www.ontologymatching.org/publications.html
- **Type:** paper / benchmark (annual evaluation)
- **Evidence Level:** High
- **Key Finding:** OAEI provides standardized benchmarks for comparing ontology matching systems. The 2023 campaign offered 15 tracks with 16 participating systems. Ontology alignment generates correspondences (mappings) between entities of different ontologies. Recent advances use LLMs and semantic embeddings for matching. Holistic cross-domain alignment approaches remain scarce — most work focuses on individual ontology pairs.
- **Relevance to our work:** If cartridges overlap (violating orthogonality), we need alignment mechanisms. OAEI's benchmark approach could inform our cross-cartridge compatibility testing. The scarcity of holistic cross-domain approaches confirms that our cartridge system should enforce orthogonality rather than relying on alignment.

### Source 20: Protege Plugin Architecture
- **Authors/Org:** Mark Musen, Stanford University
- **Year:** 1987-present
- **URL:** https://protege.stanford.edu/
- **Type:** docs / software
- **Evidence Level:** Medium
- **Key Finding:** Protege uses a tiered architecture: knowledge model (object-oriented ontology model) → persistence layer → API → GUI/plugins/applications. All access goes through the same API. Plugins add visualization, multi-ontology management (merging, versioning), inference engines, and other functionality. Ontology inclusion allows building large knowledge bases by "gluing" smaller modular ontologies. The plugin ecosystem (dozens of plugins) demonstrates that modular extensibility works in practice for ontology tools.
- **Relevance to our work:** Protege's plugin architecture (unified API, pluggable functionality) validates our cartridge approach. Their experience with ontology inclusion ("gluing" smaller ontologies) is directly relevant. The plugin ecosystem's success over 35+ years shows that modular extensibility sustains long-term.

---

## Synthesized Claims

### Claim 1: Modular ontology composition requires explicit module interfaces — full import is insufficient
- **Confidence:** HIGH
- **Supporting sources:** 3 (owl:imports limitations), 5 (MIREOT selective import), 7 (E-Connections typed links, P-DL selective import), 18 (OWL module interface proposals)
- **Contrary evidence:** None found. All sources agree that full import (owl:imports style) is problematic at scale.
- **Implication:** Cartridges must declare explicit public interfaces (exported types, relations, attachment points) rather than exposing everything.

### Claim 2: Orthogonality (non-overlapping domains) is the most practical strategy for modular knowledge systems
- **Confidence:** HIGH
- **Supporting sources:** 4 (OBO Foundry orthogonality principle), 7 (E-Connections strict domain disjointness), 3 (composition constraint — no new relationships between existing concepts), 19 (cross-domain alignment remains scarce)
- **Contrary evidence:** DDL bridge rules allow overlap (Source 7). Wikidata succeeds without strict orthogonality (Source 12), but at the cost of complex constraint systems.
- **Implication:** Cartridges should own non-overlapping domains. Cross-domain concepts (polysemes) should be handled by a shared reference cartridge or explicit bridge declarations, not domain overlap.

### Claim 3: Cross-module references should use minimal, typed declarations — not full imports
- **Confidence:** HIGH
- **Supporting sources:** 5 (MIREOT: URI + parent type is sufficient), 7 (P-DL selective importing), 10 (Apollo @shareable for explicit sharing), 13 (data mesh polysemes with unified identifiers), 14 (dbt ref() function)
- **Contrary evidence:** None found.
- **Implication:** A cartridge referencing a concept from another cartridge should declare: source cartridge ID, source type URI, local parent type. This is sufficient for composition without tight coupling.

### Claim 4: Competency questions are an established, well-studied mechanism for ontology validation
- **Confidence:** HIGH
- **Supporting sources:** 17 (234 CQs formalized to SPARQL), 8 (NeOn includes CQs in methodology), 1 (MOMo uses CQs for validation)
- **Contrary evidence:** CQ formulation remains difficult in practice (Source 17 notes practitioners struggle). Limited tooling for automated CQ-to-query translation.
- **Implication:** Our cartridge validation rules as competency questions are well-supported by prior work. We should expect manual effort in CQ formulation and invest in tooling.

### Claim 5: Schema composition should fail on conflict rather than silently merge
- **Confidence:** HIGH
- **Supporting sources:** 10 (Apollo Federation fails composition on type conflicts), 14 (dbt contracts fail build on mismatch), 16 (conflict resolution framework identifies 10 conflict categories)
- **Contrary evidence:** Wikidata uses constraints-as-hints (Source 12), tolerating violations. Schema.org's pending mechanism allows ambiguity during development.
- **Implication:** Cartridge composition should be strict by default — conflicting type definitions fail validation. A "pending" or "draft" status could allow softer validation during development.

### Claim 6: Successful modular knowledge systems require federated governance — local autonomy with global standards
- **Confidence:** HIGH
- **Supporting sources:** 4 (OBO Foundry voluntary principles + compliance dashboard), 13 (data mesh federated computational governance), 9 (Schema.org community process), 10 (Apollo composition rules)
- **Contrary evidence:** None found. All successful systems combine local ownership with some form of global coordination.
- **Implication:** The cartridge system needs: (1) a cartridge specification (the global standard), (2) automated validation (compliance dashboard), (3) local ownership of cartridge internals, (4) governance for cross-cartridge concepts.

### Claim 7: Versioning and evolution of modular ontologies remain under-solved
- **Confidence:** MEDIUM
- **Supporting sources:** 14 (dbt model versions for breaking changes), 15 (LinkML-Map for version transformations), 4 (OBO Foundry requires version identification but no detailed mechanism), 16 (conflict resolution framework addresses evolution conflicts)
- **Contrary evidence:** DOL (Source 6) provides conservative extension checking. Some formal mechanisms exist but are not widely adopted in practice.
- **Implication:** Cartridge versioning is a known hard problem. We should start simple (semver on cartridges) and plan for version transformation tooling (a la LinkML-Map) as a future capability.

### Claim 8: Convention-based discovery and dynamic loading of modular schemas is industry-proven
- **Confidence:** HIGH
- **Supporting sources:** 11 (Backstage entity discovery via processors and conventions), 14 (dbt package discovery), 10 (Apollo subgraph registration), 20 (Protege plugin discovery)
- **Contrary evidence:** None found.
- **Implication:** Our `.raise/domains/*/domain.yaml` convention-based discovery is a well-established pattern. Python entry points or importlib-based loading is appropriate.

---

## Gaps Identified

1. **No prior work combines all cartridge features in one system.** Academic modular ontology work focuses on formal semantics (OWL, DL). Industry systems focus on schema composition (GraphQL, dbt). None combine: self-contained schema + corpus + validation rules + domain adapter + convention-based discovery.

2. **Cross-module query routing is under-explored in ontology literature.** Apollo Federation solves this for GraphQL, but no ontology system provides pluggable query interpretation adapters that route based on domain detection.

3. **Dynamic loading of ontology modules at runtime is mostly absent from academic work.** The literature assumes compile-time/design-time module composition. Our Python import-based runtime loading is closer to software plugin systems than ontology engineering.

4. **Corpus attachment (linking ontology modules to their source documents) is not addressed.** Academic modular ontology work treats schemas in isolation from the corpora they describe. Our cartridge concept of bundling corpus sources with schema is novel.

5. **Validation-as-competency-questions attached to individual modules is uncommon.** CQs are typically defined for an entire ontology, not per-module. Our per-cartridge validation rules are a reasonable extension but lack direct precedent.

6. **LLM-era ontology modularity is nascent.** Recent work (2024-2025) explores LLMs for ontology matching and construction, but modular ontology methodology has not yet incorporated LLM capabilities for module discovery, composition, or query interpretation.

---

## Relevance to Knowledge Cartridge Architecture

### Direct Design Validations

| Cartridge Feature | Prior Art Support | Key Source |
|---|---|---|
| Self-contained domain modules | MOMo modules, OBO Foundry orthogonality | Sources 1, 4 |
| Pydantic schema declarations | Backstage TypeScript+JSONSchema, dbt contracts | Sources 11, 14 |
| Convention-based discovery | Backstage processors, dbt packages, Protege plugins | Sources 11, 14, 20 |
| Competency question validation | CQ-to-SPARQL research, CQOA | Source 17 |
| Cross-cartridge references | MIREOT selective import, P-DL, Apollo @shareable | Sources 5, 7, 10 |
| Composition fails on conflict | Apollo Federation, dbt contracts | Sources 10, 14 |

### Recommended Design Principles (from literature)

1. **Explicit public interface per cartridge** — declare exported types and relations; do not expose internals (Sources 1, 18)
2. **Orthogonal domains** — each concept owned by exactly one cartridge; polysemes handled by explicit bridge declarations (Sources 4, 7, 13)
3. **Minimal cross-references** — reference foreign types by (cartridge_id, type_uri, local_parent) — MIREOT-style (Source 5)
4. **Fail-fast composition** — conflicting type definitions are errors, not warnings (Sources 10, 14)
5. **Federated governance** — cartridge spec as global standard, automated compliance checks, local ownership of internals (Sources 4, 13)
6. **Maturity lifecycle** — draft → published → core progression for cartridges (Source 9 Schema.org pattern)
7. **Version with semver** — plan for future transformation tooling (Sources 14, 15)

### Architecture Risks Identified

1. **Over-formalization:** Academic approaches (DDL, E-Connections, DOL) provide formal guarantees but require specialized reasoners. Our Pydantic-based approach trades formal guarantees for developer accessibility — a deliberate choice that should be documented.
2. **Cross-cartridge query complexity:** As cartridge count grows, query routing becomes an O(n) problem. Apollo Federation solved this with a router; we may need similar infrastructure.
3. **Versioning debt:** Starting without version transformation tooling is acceptable but will accumulate technical debt as cartridges evolve.

---

*Research conducted: 2026-03-24*
*Session type: research*
*Searches performed: 15 web searches, 10 page fetches*
*Sources cataloged: 20*
*Evidence triangulation: All synthesized claims supported by 3+ sources*
