# R5: Multi-Domain Knowledge Composition and Cross-Domain Reasoning

## Research Question

What prior work exists on multi-domain knowledge representation, cross-domain querying, and knowledge composition? How do systems handle semantic overlap, conflict resolution, and unified querying across heterogeneous knowledge sources?

**Context:** We are building a system where an AI agent can have multiple "Knowledge Cartridges" loaded simultaneously — each representing a different domain (e.g., ScaleUp business methodology, GTD productivity, software architecture). Each cartridge has its own schema, adapter, and validation rules. We need to understand how to query across domains, handle overlapping concepts, and compose domain-specific results into coherent answers.

---

## Evidence Catalog

### Source 1: OBO Foundry — Coordinated Evolution of Ontologies to Support Biomedical Data Integration

- **Authors/Org:** Smith B, Ashburner M, Rosse C, et al.
- **Year:** 2007 (Nature Biotechnology), updated through 2021
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC2814061/
- **Type:** paper (journal, Nature Biotechnology)
- **Evidence Level:** Very High
- **Key Finding:** OBO Foundry achieves multi-domain interoperability through three mechanisms: (1) **orthogonality** — each concept exists in exactly one ontology, preventing duplication; (2) a shared **Relation Ontology (RO)** providing standardized relations (is_a, part_of) as cross-domain glue; (3) **cross-products** that compose compound terms from constituent terms across ontologies (e.g., PATO "increased concentration" + FMA "blood" + ChEBI "glucose"). The approach is *coordinated development* — domains are designed to interoperate from inception, unlike UMLS's post-hoc integration.
- **Relevance to our work:** The orthogonality principle maps directly to Knowledge Cartridges — each cartridge owns its domain exclusively. The cross-product pattern shows how to compose concepts across cartridges without merging them. The shared Relation Ontology is analogous to a shared meta-schema for inter-cartridge references.

### Source 2: Foundational Ontologies Meet Ontology Matching — A Survey

- **Authors/Org:** Trojahn C, Vieira R, Schmidt D, Pease A, Guizzardi G
- **Year:** 2022 (Semantic Web journal)
- **URL:** https://journals.sagepub.com/doi/10.3233/SW-210447
- **Type:** paper (survey)
- **Evidence Level:** High
- **Key Finding:** Upper/foundational ontologies (BFO, DOLCE, SUMO) serve as cross-domain bridges that improve ontology matching quality. 100% of BFO categories align to DOLCE, but only 81% of DOLCE aligns to BFO, showing that foundational ontologies are not interchangeable. Upper ontologies clarify semantics, avoid poor design, and facilitate interoperability — but they require commitment to a philosophical stance (realist BFO vs. cognitive DOLCE). The OAEI evaluation shows LLM-enhanced matchers (e.g., CANARD + LLM) improve precision by up to 45%.
- **Relevance to our work:** A lightweight "upper schema" for Knowledge Cartridges could serve as a bridging layer — defining shared meta-concepts (Entity, Process, Goal, Metric) that each cartridge maps to. The choice between realist and cognitive stances matters: business domains may prefer cognitive (DOLCE-style) modeling.

### Source 3: Wikidata — Multi-Domain Knowledge Graph at Scale

- **Authors/Org:** Wikimedia Foundation / Vrandecic D, Krotzsch M (original design)
- **Year:** 2012–present
- **URL:** https://en.wikipedia.org/wiki/Wikidata / https://pmc.ncbi.nlm.nih.gov/articles/PMC7077981/
- **Type:** docs + paper
- **Evidence Level:** Very High
- **Key Finding:** Wikidata handles 100M+ items across all domains using: (1) a universal item model (QID + property-value statements); (2) Shape Expressions (ShEx) for entity schemas that validate domain-specific structure; (3) SPARQL with federated queries (SERVICE keyword) for cross-source querying; (4) community-maintained ontological structure without a single enforced upper ontology. Provenance is attached at the statement level. Multi-language support is built into every item.
- **Relevance to our work:** Wikidata's approach — universal item format + domain-specific validation via ShEx — is a proven pattern for our cartridge architecture. Each cartridge could define its own ShEx-like schema while items share a common envelope. Statement-level provenance maps to tracking which cartridge contributed which knowledge.

### Source 4: FedX — Federated SPARQL Query Processing

- **Authors/Org:** Schwarte A, Haase P, Hose K, Schenkel R (original); Ontotext (GraphDB integration)
- **Year:** 2011 (original), maintained through 2024
- **URL:** https://graphdb.ontotext.com/documentation/11.2/fedx-federation.html
- **Type:** docs + paper
- **Evidence Level:** High
- **Key Finding:** FedX enables transparent querying across multiple heterogeneous SPARQL endpoints as if they were a single database. Key mechanisms: (1) automatic source selection — determines which endpoints can answer which parts of a query; (2) novel join processing that minimizes remote requests; (3) grouping techniques that batch related patterns to the same source. Federation relies on owl:sameAs links between entities across graphs. The SERVICE operator in SPARQL 1.1 is the standard mechanism.
- **Relevance to our work:** The source selection mechanism maps directly to our problem — given a cross-cartridge query, which cartridges need to participate? FedX's approach of analyzing triple patterns against source capabilities is analogous to analyzing query terms against cartridge schemas.

### Source 5: HeFQUIN — Heterogeneous Federation Query Engine

- **Authors/Org:** Hartig O et al., Linköping University Semantic Web Group
- **Year:** 2022–present (active development)
- **URL:** https://github.com/LiUSemWeb/HeFQUIN
- **Type:** repo + research prototype
- **Evidence Level:** Medium
- **Key Finding:** HeFQUIN extends federation beyond uniform SPARQL endpoints to heterogeneous data sources with different query interfaces (SPARQL endpoints, Triple Pattern Fragment servers, etc.). It adapts query decomposition, planning, and physical operators to the particularities of different source interfaces. This is a step beyond FedX's assumption of uniform endpoints.
- **Relevance to our work:** Knowledge Cartridges will have different query interfaces (some graph-based, some document-based, some structured). HeFQUIN's approach of adapting operators per source type is directly relevant — our federation layer needs heterogeneous adapter support, not just uniform endpoints.

### Source 6: Apollo Federation — GraphQL Schema Composition

- **Authors/Org:** Apollo GraphQL Inc.
- **Year:** 2019–present
- **URL:** https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/federation
- **Type:** docs
- **Evidence Level:** High
- **Key Finding:** Apollo Federation composes multiple GraphQL subgraphs into a unified supergraph via a router. Key patterns: (1) each subgraph owns its domain types; (2) the @key directive enables cross-service entity references (subgraph A defines User, subgraph B extends it with Orders); (3) the router decomposes client queries into subgraph queries and joins results; (4) schema composition detects incompatibilities at build time. Adopted by Netflix, Expedia, Volvo, Booking. Aligns naturally with Domain-Driven Design bounded contexts.
- **Relevance to our work:** Apollo Federation is the closest production analog to our Knowledge Cartridge composition problem — each cartridge is a subgraph, the agent's query layer is the router, and cross-cartridge references use something like @key. The build-time incompatibility detection maps to cartridge registration validation.

### Source 7: Knowledge Conflicts for LLMs — A Survey

- **Authors/Org:** Xu R, Qi Z, Guo C, Wang Y, Wang Y, Zhang Y, Xu Z (Tsinghua, Cambridge, Westlake, CUHK)
- **Year:** 2024 (EMNLP Main Conference)
- **URL:** https://arxiv.org/abs/2403.08319
- **Type:** paper (survey)
- **Evidence Level:** Very High
- **Key Finding:** Identifies three types of knowledge conflicts: (1) **Context-Memory** — retrieved context contradicts parametric knowledge; (2) **Inter-Context** — multiple retrieved sources contradict each other; (3) **Intra-Memory** — model's own parameters produce inconsistent outputs. LLMs exhibit confirmation bias toward parametric memory. Resolution strategies include: faithful-to-context fine-tuning (KAFT), discriminating misinformation via vigilant prompting, disentangling sources (presenting distinct answers per source), and factuality improvement (COMBO, DoLa).
- **Relevance to our work:** When cartridges contain overlapping or conflicting knowledge (e.g., GTD and ScaleUp both define "priority"), the agent faces inter-context conflict. The "disentangling sources" strategy — presenting domain-attributed answers rather than forcing resolution — is directly applicable. Cartridge provenance tracking enables this.

### Source 8: Detect-Then-Resolve — KG Conflict Resolution with LLM

- **Authors/Org:** (Mathematics journal authors, 2024)
- **Year:** 2024
- **URL:** https://www.mdpi.com/2227-7390/12/15/2318
- **Type:** paper
- **Evidence Level:** Medium
- **Key Finding:** CRDL introduces a two-phase approach: (1) **detect** conflicts using relation/attribute-specific filtering strategies; (2) **resolve** using LLM prompts with injected relevant context. Conflict types include Specificity deltas (fuzziness, incompleteness, vagueness) and Contradictory deltas (invalidity, ambiguity, timeliness). Significantly improves precision and recall over state-of-the-art methods.
- **Relevance to our work:** The detect-then-resolve pattern is directly applicable. When composing results from multiple cartridges, first detect whether concepts overlap (same entity, different attributes) or conflict (same attribute, different values), then resolve using domain priority rules or LLM-mediated reasoning.

### Source 9: Combining Knowledge Graphs Quickly and Accurately (Amazon)

- **Authors/Org:** Wei H et al. (Amazon)
- **Year:** 2020 (The Web Conference)
- **URL:** https://www.amazon.science/blog/combining-knowledge-graphs-quickly-and-accurately
- **Type:** paper + blog
- **Evidence Level:** High
- **Key Finding:** Graph neural network approach for entity alignment across KGs with cross-graph attention and self-attention mechanisms. Cross-graph attention emphasizes correspondences and de-emphasizes differences between graphs. Handles multi-type knowledge graphs (nodes representing different entity types). 10% improvement on PRAUC over baselines, with 95% training time reduction vs. DeepMatcher.
- **Relevance to our work:** When cartridges reference overlapping entities (e.g., "team" in ScaleUp vs. "context" in GTD), entity alignment is needed. The neighborhood-based approach — looking at what surrounds a concept, not just its name — is relevant for detecting semantic overlap between cartridge concepts.

### Source 10: Modular Ontology Modeling (MOMo)

- **Authors/Org:** Shimizu C, Hammar K, Hitzler P et al.
- **Year:** 2023 (Semantic Web journal, vol. 14, issue 3)
- **URL:** https://journals.sagepub.com/doi/10.3233/SW-222886
- **Type:** paper
- **Evidence Level:** High
- **Key Finding:** MOMo methodology builds ontologies as compositions of reusable modules using Ontology Design Patterns (ODPs). Each module has its own schema diagram, axioms, examples. The overall ontology is "essentially a composition of the modules." MODL (Modular Ontology Design Library) provides a curated collection of cross-domain patterns. CoModIDE tooling supports graphical composition. Key principle: modules are self-contained building blocks that minimize ontological commitments, making them easier to integrate than monolithic ontologies.
- **Relevance to our work:** Knowledge Cartridges ARE ontology modules in this framework. MOMo's approach of minimal ontological commitment per module, with explicit composition rules, is the right philosophy. MODL's cross-domain pattern library could inspire a library of cross-cartridge bridging patterns.

### Source 11: Multi-View Knowledge Graphs (MVKG) Survey

- **Authors/Org:** Yang Z, Tao X, Cai J, Tang Y, Xie H, Li Q, Li Q, Li Y
- **Year:** 2025 (IJCAI-25)
- **URL:** https://www.ijcai.org/proceedings/2025/1197
- **Type:** paper (survey, top-tier conference)
- **Evidence Level:** High
- **Key Finding:** MVKGs address KG limitations through multi-view learning. Four view types: (1) Structure — graph topology perspectives; (2) Semantic — textual/linguistic meaning; (3) Representation — embedding spaces; (4) Knowledge & Modality — cross-modal information. Three fusion strategies: feature fusion (combine representations), decision fusion (aggregate outputs), hybrid fusion. The survey provides the first unified taxonomy for view generation and fusion.
- **Relevance to our work:** Each Knowledge Cartridge can be seen as providing a "view" of the knowledge space. MVKG fusion strategies (especially decision fusion — aggregating domain-specific answers) map to our composition problem. The taxonomy of views helps formalize what each cartridge contributes.

### Source 12: Construction of Knowledge Graphs — State and Challenges

- **Authors/Org:** Hofer M, Hellmann S, Dojchinovski M et al.
- **Year:** 2023 (arXiv)
- **URL:** https://arxiv.org/abs/2302.11509
- **Type:** paper (survey)
- **Evidence Level:** High
- **Key Finding:** KGs are "schema-flexible and can thus easily accommodate and interlink heterogeneously structured entities." Key challenge: individual construction steps are well-researched for one-shot execution, but their adoption for incremental updates and the interplay between steps has hardly been investigated. Evaluates 23 KG construction approaches against requirements. Covers both RDF and property graph models.
- **Relevance to our work:** Knowledge Cartridges need incremental updates (new domain knowledge added over time). The gap identified — poor support for incremental construction and inter-step coordination — is exactly the challenge of maintaining cartridge consistency as they evolve independently.

### Source 13: R1-Router — Learning to Route Queries Across Knowledge Bases

- **Authors/Org:** Peng C, Xu Z, Liu Z et al. (Northeastern University, Tsinghua University)
- **Year:** 2025 (arXiv)
- **URL:** https://arxiv.org/abs/2505.22095
- **Type:** paper
- **Evidence Level:** High
- **Key Finding:** R1-Router dynamically decides when and where to retrieve information during multi-step reasoning. At each step, the model: (1) assesses whether collected information suffices; (2) generates targeted sub-queries for specific knowledge sources; (3) routes sub-queries to appropriate retrievers (text, image, table). Uses Step-GRPO (step-wise rewards for intermediate decisions). 7% average improvement over baseline RAG, 95% improvement on Table QA.
- **Relevance to our work:** R1-Router's step-wise routing is the most directly analogous system to our cross-cartridge query problem. The agent needs to decide which cartridge(s) to query, generate domain-appropriate sub-queries, and compose results. The learned routing policy (vs. rule-based) is an interesting architectural option.

### Source 14: Schema.org — Multi-Domain Vocabulary at Web Scale

- **Authors/Org:** Google, Microsoft, Yahoo, Yandex (original consortium)
- **Year:** 2011–present
- **URL:** https://schema.org/
- **Type:** standard/specification
- **Evidence Level:** Very High
- **Key Finding:** Schema.org provides 823 types and 1,529 properties across all web domains using a single extensible hierarchy. Top-level types (Person, Organization, Place, Event, CreativeWork) are abstract enough to span domains. Domain-specific extensions (automotive, health, bibliographic) add specialized types without breaking the core. Adopted by 45M+ web domains with 450B+ objects. Uses JSON-LD, RDFa, Microdata encodings.
- **Relevance to our work:** Schema.org proves that a small set of abstract top-level types can organize knowledge across arbitrary domains. Our cartridge system could use a similar approach: a small shared type hierarchy (Entity, Process, Goal, Metric, Role) with cartridge-specific extensions.

### Source 15: Semantic Layers and Data Mesh — Enterprise Knowledge Integration

- **Authors/Org:** Multiple enterprise vendors (Databricks, EPAM, Enterprise Knowledge)
- **Year:** 2024–2025
- **URL:** https://www.epam.com/insights/blogs/scaling-data-mesh-with-universal-semantic-layers-from-proof-of-concept-to-enterprise-reality
- **Type:** blog / industry practice
- **Evidence Level:** Medium
- **Key Finding:** The "core + edge" pattern distinguishes between authoritative enterprise metric definitions (core) and team-specific knowledge (edge). Edge knowledge can be reviewed and promoted to core. In Data Mesh, each domain manages its own semantics while adhering to enterprise-wide interoperability standards. The universal semantic layer provides consistent access patterns while maintaining domain autonomy. Federated governance distributes ownership to domain teams.
- **Relevance to our work:** The core+edge pattern maps well to cartridges. A "core cartridge" defines shared concepts (Entity, Goal, Metric), while domain cartridges extend with specialized knowledge. The promotion mechanism (edge -> core) handles concept graduation as patterns stabilize across domains.

### Source 16: EARAG — Entity Alignment via Retrieval-Augmented Generation

- **Authors/Org:** (Multiple authors, 2025)
- **Year:** 2025
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S1566253525006591
- **Type:** paper
- **Evidence Level:** Medium
- **Key Finding:** EARAG integrates structured knowledge from KGs with LLM semantic reasoning for entity alignment. Uses CNN-based retriever with multiple similarity metrics to find candidate entities, then constructs prompts guiding the LLM to determine equivalence and generate explanations. Achieves state-of-the-art accuracy with superior interpretability.
- **Relevance to our work:** When the agent encounters concepts from different cartridges that might refer to the same thing (e.g., "sprint" in ScaleUp vs. "project" in GTD), an EARAG-like approach could determine equivalence with explainable reasoning.

### Source 17: Agentic RAG — Multi-Source Query Routing Patterns

- **Authors/Org:** Various (AWS, Microsoft, industry practitioners)
- **Year:** 2024–2025
- **URL:** https://aws.amazon.com/what-is/retrieval-augmented-generation/
- **Type:** docs + blog
- **Evidence Level:** Medium
- **Key Finding:** Agentic RAG introduces strategic query routing where an LLM agent: (1) decides if retrieval is needed; (2) selects which data source to query; (3) decomposes complex questions into sub-queries per source; (4) determines if results are sufficient or if additional rounds are needed. Domain-specific routing examples: healthcare routes clinical questions to medical KB, billing to financial index. MA-RAG coordinates specialized agents for different retrieval domains.
- **Relevance to our work:** This is the operational pattern for our cartridge query layer. The agent analyzes the query, determines which cartridges are relevant, generates cartridge-specific sub-queries, and composes results. The "sufficiency check" after each retrieval round prevents over-querying.

---

## Synthesized Claims

### Claim 1: Orthogonality (one concept, one owner) is the primary mechanism for avoiding cross-domain conflict
**Confidence:** Very High | **Sources:** S1 (OBO Foundry), S6 (Apollo Federation), S10 (MOMo), S14 (Schema.org)

All successful multi-domain systems enforce that each concept is owned by exactly one domain. OBO Foundry requires each concept to have a single URI. Apollo Federation has each type owned by one subgraph. MOMo modules minimize ontological commitment. Schema.org extensions don't override core types. This is the single most validated design principle.

**Implication for cartridges:** Each cartridge must declare exclusive ownership of its concepts. Cross-cartridge references use linking, not duplication.

### Claim 2: A shared "upper" layer of abstract types provides the bridging mechanism for cross-domain composition
**Confidence:** High | **Sources:** S2 (foundational ontologies), S14 (Schema.org), S10 (MOMo), S15 (semantic layers)

Upper ontologies (BFO, DOLCE), Schema.org's top-level types, and enterprise semantic layers all use a small set of domain-independent abstractions as the meeting point. The upper layer need not be large — Schema.org has ~10 top-level types spanning 45M domains. However, choosing the right abstractions matters (BFO realist vs. DOLCE cognitive).

**Implication for cartridges:** Define 5-10 shared meta-types (Entity, Process, Goal, Metric, Role, Artifact, Constraint) that all cartridges map to. Keep this layer minimal and stable.

### Claim 3: Cross-domain queries require source-aware decomposition and routing, not monolithic search
**Confidence:** Very High | **Sources:** S4 (FedX), S5 (HeFQUIN), S6 (Apollo Federation), S13 (R1-Router), S17 (Agentic RAG)

Every successful federated system decomposes queries into source-specific sub-queries. FedX analyzes triple patterns against source capabilities. Apollo's router plans subgraph queries. R1-Router learns routing policies. Agentic RAG uses LLM-based routing. No system attempts a "query everything at once" approach.

**Implication for cartridges:** The query layer must: (1) analyze the query to identify relevant cartridges; (2) generate cartridge-specific sub-queries; (3) execute against selected cartridges; (4) compose results. This is a federation pattern, not a search pattern.

### Claim 4: Conflict resolution requires explicit detection before resolution, and multiple strategies exist
**Confidence:** High | **Sources:** S7 (Knowledge Conflicts survey), S8 (CRDL), S9 (Amazon entity alignment)

Conflicts fall into two categories: Specificity (different levels of detail) and Contradictory (actually incompatible claims). Detection must precede resolution. Resolution strategies include: (a) source priority (trust one cartridge over another); (b) recency (newer wins); (c) disentangling (present both with attribution); (d) LLM-mediated reasoning. The "disentangling" strategy is often preferable to forced resolution.

**Implication for cartridges:** When ScaleUp says "velocity is story points per sprint" and an Agile cartridge says "velocity is throughput per unit time," don't force resolution. Present both with cartridge attribution and let the user decide. Add cartridge priority metadata for cases where automatic resolution is needed.

### Claim 5: Entity alignment across domains can leverage neighborhood structure, not just name matching
**Confidence:** High | **Sources:** S9 (Amazon), S16 (EARAG), S2 (foundational ontologies)

Name matching alone is insufficient (CustomerID vs. ClientID). Graph-based approaches look at the semantic neighborhood — entities that share similar surroundings are likely equivalent. LLM-enhanced approaches (EARAG) add explainability. Cross-graph attention mechanisms de-emphasize domain-specific differences.

**Implication for cartridges:** When detecting overlap between cartridges, compare not just concept names but their relationships, properties, and usage patterns. A "team" in ScaleUp connected to "goals, metrics, roles" and a "team" in GTD connected to "projects, contexts, responsibilities" share enough neighborhood structure to warrant alignment.

### Claim 6: Modular composition with minimal coupling is preferred over deep integration
**Confidence:** Very High | **Sources:** S1 (OBO Foundry), S6 (Apollo Federation), S10 (MOMo), S15 (data mesh)

OBO's cross-products compose without merging. Apollo subgraphs extend without modifying. MOMo modules minimize ontological commitment. Data mesh maintains domain autonomy. Deep integration (UMLS-style post-hoc merging) is expensive, brittle, and loses domain-specific nuance.

**Implication for cartridges:** Cartridges should compose through references and bridging types, not through merging. A cross-cartridge query should feel like asking multiple experts and synthesizing, not like querying a single merged database.

---

## Gaps Identified

1. **No prior work on "Knowledge Cartridge" as a formal concept.** The closest analogs are ontology modules (MOMo), GraphQL subgraphs (Apollo), and data mesh domain products. Our concept of a self-contained, schema-validated, adapter-equipped knowledge unit with its own reasoning rules appears novel in its combination.

2. **Limited research on LLM-native cross-domain composition.** Most work assumes SPARQL or GraphQL as query languages. The pattern of an LLM agent reasoning across multiple knowledge domains simultaneously, deciding which to query and how to compose results, is only emerging (R1-Router, Agentic RAG).

3. **Validation rule composition is under-explored.** How do you validate a composed result that spans cartridges? If ScaleUp requires "every goal has a metric" and GTD requires "every project has a next action," what validation applies to a cross-domain entity that is both a ScaleUp goal and a GTD project?

4. **Dynamic cartridge loading/unloading patterns.** Most ontology work assumes a fixed set of sources. The ability to hot-load and hot-unload knowledge cartridges — changing the agent's domain expertise at runtime — lacks formal treatment.

5. **Conflict resolution for reasoning rules (not just data).** Existing work focuses on data conflicts (entity A has value X vs. Y). Our cartridges may have conflicting reasoning rules (ScaleUp: "prioritize by business impact" vs. GTD: "prioritize by context and energy"). No systematic treatment of meta-level conflict resolution exists.

---

## Relevance to Knowledge Cartridge Architecture

Based on this review, the recommended architectural patterns for Knowledge Cartridges are:

### 1. Orthogonality-First Design
Each cartridge exclusively owns its concepts. Cross-references use explicit linking (analogous to owl:sameAs or @key), never duplication. This is the single most validated principle across all sources.

### 2. Thin Upper Schema
Define a minimal shared type hierarchy (5-10 types: Entity, Process, Goal, Metric, Role, Artifact, Constraint, Relationship). Each cartridge maps its domain types to this schema. Inspired by Schema.org's success with ~10 top-level types spanning 45M domains.

### 3. Federated Query Decomposition
The agent's query layer should:
- Analyze queries to identify relevant cartridges (source selection, per FedX)
- Generate cartridge-specific sub-queries (decomposition, per Apollo router)
- Route sub-queries to appropriate cartridge adapters (routing, per R1-Router)
- Compose results with provenance tracking (attribution, per Wikidata)

### 4. Detect-Then-Resolve Conflict Handling
When cartridges return overlapping or conflicting information:
- **Detect** overlap via shared upper schema mapping + neighborhood similarity
- **Classify** as specificity delta or contradictory delta
- **Resolve** via: source priority > recency > disentangling (present both with attribution)
- Default to disentangling — let the user see domain-specific perspectives

### 5. Cartridge-as-Module Composition
Following MOMo and Apollo Federation:
- Each cartridge is self-contained with its own schema, validation, and adapter
- Composition happens through bridging types and cross-references
- Registration validates compatibility (schema composition check, per Apollo)
- No modification of cartridge internals during composition

### 6. Provenance-by-Default
Every piece of composed knowledge carries its source cartridge attribution (per Wikidata's statement-level provenance). This enables:
- Conflict detection (same concept, different cartridges)
- Trust calibration (which cartridge is authoritative for this claim?)
- Debugging (why did the agent answer this way?)

---

*Research conducted: 2026-03-24*
*Method: Systematic web search (12 search queries), source fetching (6 detailed reads), triangulation (3+ sources per claim)*
*Confidence in synthesis: High — core patterns are well-established across multiple mature systems*
