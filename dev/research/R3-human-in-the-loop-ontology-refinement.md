# R3: Human-in-the-Loop Ontology Refinement and Continuous Improvement

## Research Question

What prior work exists on human-in-the-loop ontology construction and refinement? What are the best practices for expert feedback loops, quality metrics, and continuous ontology improvement?

**Context:** We have a system where an AI agent extracts knowledge from text into structured ontology nodes (Pydantic models), then a domain expert reviews and validates them through a conversational HITL interface. The system has "gates" — deterministic validation checks (schema conformance, competency question coverage, cross-reference consistency) that detect when the ontology degrades. The vision is continuous improvement: as the agent is used, query failures signal gaps, which trigger extraction-curation cycles.

---

## Evidence Catalog

### Source 1: OntoChat — A Framework for Conversational Ontology Engineering using Language Models

- **Authors/Org:** Bohui Zhang, Valentina Anita Carriero, Katrin Schreiberhuber, Stefani Tsaneva, Lucia Sanchez Gonzalez, Jongmo Kim, Jacopo de Berardinis (King's College London)
- **Year:** 2024
- **URL:** https://arxiv.org/abs/2403.05921
- **Type:** paper (ESWC 2024)
- **Evidence Level:** High
- **Key Finding:** A conversational framework with four modules: (1) user story creation via guided elicitation, (2) competency question extraction with hidden refinement steps, (3) CQ analysis via paraphrase detection and clustering, (4) ontology testing via verbalization + prompt-driven unit tests (87.5% accuracy). Survey of 23 practitioners found requirement collection (86.4%), CQ extraction (81.8%), and testing (81.8%) as most demanding activities needing computational support. LLM acts as knowledge elicitor reducing multi-party interaction complexity.
- **Relevance to our work:** Directly validates our conversational HITL approach. Their CQ extraction + testing pipeline mirrors our competency question coverage gate. The "hidden refinement steps" (splitting complex questions, abstracting named entities) are patterns we should adopt. Their finding that graphical/visual interfaces are preferred aligns with our need for a review UI.

### Source 2: CleanGraph — Human-in-the-Loop Knowledge Graph Refinement and Completion

- **Authors/Org:** Tyler Bikaun, Michael Stewart, Wei Liu (University of Western Australia)
- **Year:** 2024
- **URL:** https://arxiv.org/html/2405.03932v2
- **Type:** paper
- **Evidence Level:** Medium (no formal evaluation)
- **Key Finding:** Interactive web-based tool for KG refinement via human verification. Plugin architecture for integrating automated error-detection and completion models. Domain experts review flagged errors through a visual interface, making decisions about entity merging, relationship corrections, and deletion. Built on FARM stack (FastAPI + React + MongoDB). Emphasizes that maintaining graph reliability is essential for downstream applications.
- **Relevance to our work:** Architecture pattern is relevant — plugin-based error detection with human review UI. Their approach of flagging issues for human decision (not auto-correcting) aligns with our gate philosophy. MongoDB for flexible node/edge property storage is worth noting for our cartridge storage.

### Source 3: DILIGENT — Distributed, Loosely-controlled and evolving Engineering of oNTologies

- **Authors/Org:** H. Sofia Pinto, Christoph Tempich, Steffen Staab (multiple institutions)
- **Year:** 2004–2009
- **URL:** https://link.springer.com/chapter/10.1007/3-540-28347-1_16
- **Type:** paper (seminal methodology)
- **Evidence Level:** Very High (foundational, highly cited)
- **Key Finding:** Five-activity process for distributed ontology engineering: (1) build, (2) local adaptation, (3) analysis, (4) revision, (5) local update. Emphasizes argumentation tracking — organizes exchanged arguments into types (elaboration, justification, alternatives, examples, counterexamples). Validated in tourism domain (Balearic Islands). Key insight: ontology engineering in distributed settings requires different approaches than centralized methodologies.
- **Relevance to our work:** The local adaptation → analysis → revision cycle directly maps to our extraction → gate-check → curation cycle. The argumentation tracking concept (why a decision was made) is something our system should capture during expert review. The "loosely-controlled" principle validates our approach of agent autonomy within gate constraints.

### Source 4: Ontology Maturing — A Collaborative Web 2.0 Approach to Ontology Engineering

- **Authors/Org:** Simone Braun, Andreas Schmidt, et al. (FZI Research Center, Karlsruhe)
- **Year:** 2007
- **URL:** https://www.researchgate.net/publication/221022560_Ontology_Maturing_a_Collaborative_Web_20_Approach_to_Ontology_Engineering
- **Type:** paper
- **Evidence Level:** High (well-cited conceptual framework)
- **Key Finding:** Four-phase maturation model: (1) emergence of ideas, (2) consolidation in communities, (3) formalization, (4) axiomatization. Key insight: ontology engineering is a collaborative informal learning process. Supports incremental formalization — knowledge matures from tags/folksonomies through increasingly formal structures. Five principles: shared understanding, active participation, incremental formalization, work-integration, and usable evolving models.
- **Relevance to our work:** The maturation phases map directly to our cartridge lifecycle: agent extracts rough nodes (emergence) → expert consolidates (consolidation) → schema validation formalizes (formalization) → cross-reference consistency axiomatizes (axiomatization). The "work-integration" principle — embedding ontology work in daily tasks rather than making it a separate activity — is exactly what our conversational interface achieves.

### Source 5: OOPS! (OntOlogy Pitfall Scanner)

- **Authors/Org:** Maria Poveda-Villalon, Asuncion Gomez-Perez, Mari Carmen Suarez-Figueroa (UPM)
- **Year:** 2014
- **URL:** https://oops.linkeddata.es/
- **Type:** tool + paper
- **Evidence Level:** Very High (widely used, based on 693+ ontology analysis)
- **Key Finding:** Catalogue of ontology pitfalls classified by Structural, Functional, and Usability-Profiling dimensions. Each pitfall has an importance level (critical, important, minor). Empirical analysis of 693+ ontologies identified common pitfall patterns. Available as both web UI and RESTful API for integration into pipelines. Pitfalls are domain-independent design anti-patterns.
- **Relevance to our work:** Our gate system should incorporate OOPS-style pitfall detection. The three-level severity classification (critical/important/minor) maps to our gate pass/warn/fail model. The REST API pattern validates our approach of making validation programmatically accessible. The empirically-derived pitfall catalogue provides a starting point for our own gate rules.

### Source 6: Competency Questions in Ontology Engineering — A Survey

- **Authors/Org:** Reham Alharbi, Valentina Tamma, Floriana Grasso (University of Liverpool)
- **Year:** 2023
- **URL:** https://link.springer.com/chapter/10.1007/978-3-031-47262-6_3
- **Type:** paper (survey)
- **Evidence Level:** High
- **Key Finding:** Five CQ types identified: Scoping (SCQ), Validating (VCQ), Foundational (FCQ), Relationship (RCQ), and Metaproperty (MpCQ). CQs help define scope and evaluate conceptualization. Key challenge: very limited guidance exists for formulating CQs and assessing CQ quality, leading to ambiguity. CQs should be convertible to SPARQL queries for automated testing. Ontology engineers face difficulties writing, using, and managing CQs.
- **Relevance to our work:** Our competency question coverage gate should distinguish CQ types. VCQs (validating) are most relevant for our gates — they verify the ontology meets requirements. The gap in CQ quality guidance means our system should help users write good CQs (perhaps using LLM assistance, as OntoChat does). The SPARQL formalization requirement maps to our need for executable validation.

### Source 7: Enhancing Human-in-the-Loop Ontology Curation Results through Task Design

- **Authors/Org:** (JDIQ special issue on Human-in-the-Loop Data Curation)
- **Year:** 2023
- **URL:** https://dl.acm.org/doi/10.1145/3626960
- **Type:** paper
- **Evidence Level:** High
- **Key Finding:** Two controlled experiments with junior expert crowd on ontology restriction verification. Key findings: (1) representation format does not significantly influence results, but contributors prefer graphical representation; (2) objective qualification tests are better than subjective self-assessment for evaluating contributor competence; (3) prior modeling knowledge positively affects judgment quality. First HC-based approach for verifying ontology restrictions.
- **Relevance to our work:** Task design matters for expert review quality. Our conversational interface should present ontology nodes in a way experts find intuitive (graphical preferred). We should consider qualification mechanisms to calibrate expert feedback quality. The finding that representation format doesn't affect accuracy but affects preference means we can optimize for UX without sacrificing quality.

### Source 8: WebProtege — A Collaborative Ontology Editor and Knowledge Acquisition Tool for the Web

- **Authors/Org:** Tania Tudorache, Csongor Nyulas, Natalya Noy, Mark Musen (Stanford)
- **Year:** 2013 (evolved through 2019+)
- **URL:** https://protegewiki.stanford.edu/wiki/WebProtege
- **Type:** tool + paper
- **Evidence Level:** Very High (50K+ users, 68K+ projects)
- **Key Finding:** Collaboration features: discussion threads attached to ontology entities, change notification, revision-based change tracking via ChAO (Changes and Annotations Ontology). Custom knowledge-acquisition forms for domain experts. Client-server architecture with centralized collaboration framework. Key insight: discussions integrated with editing process (not separate) improve collaboration quality.
- **Relevance to our work:** The ChAO pattern — storing change annotations and discussions as a separate ontology linked to the domain ontology — is a powerful architectural pattern. Our system should capture review decisions (accept/reject/modify) with rationale, linked to the specific nodes reviewed. The custom forms approach validates our Pydantic-model-driven UI generation.

### Source 9: Collaborative Protege — Change Tracking and Annotation

- **Authors/Org:** Tania Tudorache, Natalya Noy, Mark Musen (Stanford)
- **Year:** 2008
- **URL:** https://protegewiki.stanford.edu/wiki/Collaborative_Protege
- **Type:** tool + paper
- **Evidence Level:** High
- **Key Finding:** Change tracking intercepts GUI actions and creates change annotations attached to modified components. Notes tree corresponds to discussion threads (like forums). Filtering by author, text, type, date. Uses Changes and Annotations Ontology (ChAO) to store all metadata separately from domain ontology. Works in client-server mode with shared ontology.
- **Relevance to our work:** The separation of change/annotation metadata from domain data is a pattern we should follow. Our review decisions, expert comments, and gate results should live in a separate but linked data structure — not mixed into the cartridge itself. The filtering capabilities (by author, date, type) are requirements for our review history.

### Source 10: Gene Ontology Manual Curation Workflow

- **Authors/Org:** Multiple (MGI Database team, GO Consortium)
- **Year:** 2012–2020
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC3483533/
- **Type:** paper (methodology description)
- **Evidence Level:** Very High (production system, decades of operation)
- **Key Finding:** Multi-layer QC: (1) built-in data entry controls — vocabulary refreshed daily, only current terms allowed, incorrect evidence codes rejected; (2) annotation triage reports identifying gaps; (3) Term Matrix system using mutually exclusive process rules to detect annotation errors; (4) text mining to support and accelerate curation. Evidence codes classify confidence level of each annotation. Collaborative development with diverse communities.
- **Relevance to our work:** The multi-layer QC model is exactly what our gate system implements. The "vocabulary refreshed daily, only current terms allowed" pattern maps to our schema conformance gate. Evidence codes for confidence levels should be part of our node metadata. The Term Matrix (detecting logically inconsistent annotations) is analogous to our cross-reference consistency gate.

### Source 11: Wikidata — Collaborative Ontology Creation and User Roles

- **Authors/Org:** Alessandro Piscopo, Christopher Phethean, Elena Simperl
- **Year:** 2018
- **URL:** https://dl.acm.org/doi/10.1145/3274410
- **Type:** paper (CSCW 2018)
- **Evidence Level:** Very High (empirical study of largest collaborative KG)
- **Key Finding:** Two user roles identified: contributors and leaders. Leader role positively associated with ontology depth. Ontology has uneven breadth and depth. Wikidata built without restrictions on entity/property creation order, relying on minimal predefined roles, community consensus, property proposals, and WikiProjects for governance. Evolution through Talk pages and collaborative decisions.
- **Relevance to our work:** The contributor/leader distinction maps to our agent/expert roles. The finding that leaders improve depth (not just breadth) validates expert oversight. Wikidata's experience shows that unconstrained growth leads to uneven quality — our gates prevent this. Their governance through proposals and discussion validates our review-before-merge approach.

### Source 12: SemaDrift — Measuring Semantic Drift in Ontologies

- **Authors/Org:** T.G. Stavropoulos, S. Andreadis, E. Kontopoulos, I. Kompatsiaris
- **Year:** 2018
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S1570826818300258
- **Type:** paper (Semantic Web journal)
- **Evidence Level:** High
- **Key Finding:** Hybrid method combining identity-based and morphing-based approaches to measure semantic drift. Introduces concept stability ranking and hybrid chains across ontology versions. Provides Protege plugin (for engineers) and SemaDriftFx visual tool (for broader audience). Demonstrates drift detection in digital preservation and Web Services domains. Open-source application suite.
- **Relevance to our work:** Concept stability ranking is a metric we should track — nodes that keep changing may indicate poor extraction or evolving domain understanding. Version-to-version drift measurement could be applied to our cartridge versions to detect degradation. The visual tools for non-engineers validate our need for accessible monitoring.

### Source 13: KGValidator — A Framework for Automatic Validation of Knowledge Graph Construction

- **Authors/Org:** Jack Boylan, Shashank Mangla, Dominic Thorn, Demian Gholipour Ghalandari, Parsa Ghaffari, Chris Hokamp
- **Year:** 2024
- **URL:** https://arxiv.org/html/2404.15923v1
- **Type:** paper
- **Evidence Level:** High
- **Key Finding:** Three-source validation: (1) LLM internal knowledge, (2) textual context from documents, (3) reference KG cross-checking (Wikidata). Uses Pydantic + Instructor for structured validation output (boolean validity + text explanation). GPT-4 achieves 0.95 accuracy on WN18RR, 0.89 on Wiki27K with combined context. Llama-2-70B showed poor performance (~0.50), demonstrating model choice matters critically.
- **Relevance to our work:** Directly validates our Pydantic-based validation approach. The three-source validation pattern (internal knowledge, source documents, reference KG) maps to our gate types. The structured output pattern (valid/invalid + explanation) is what our gates should produce. The model performance gap warns us to validate our LLM choice carefully.

### Source 14: LLM-Supported Collaborative Ontology Design (NeOn Extension)

- **Authors/Org:** Janis Kampars, Guntis Mosans, Tushar Jogi, Franz Roters, Napat Vajragupta
- **Year:** 2025
- **URL:** https://www.frontiersin.org/journals/big-data/articles/10.3389/fdata.2025.1676477/full
- **Type:** paper (Frontiers in Big Data)
- **Evidence Level:** High
- **Key Finding:** Extends NeOn iterative framework with LLM automation while retaining expert-in-the-loop validation. LLMs as "co-pilots" not autonomous agents. Quality metrics from MeLOn methodology: completeness, correctness, coherence, applicability, effectiveness, intuitiveness, computational soundness, reusability. FAIR compliance as cross-cutting concern. Supports both waterfall and iterative-incremental lifecycles.
- **Relevance to our work:** The MeLOn quality metrics provide a comprehensive evaluation framework for our cartridges. The "co-pilot" framing matches our agent architecture perfectly. The NeOn extension validates that established ontology engineering methodologies can be adapted for LLM-assisted workflows. FAIR compliance gives us concrete non-functional requirements.

### Source 15: Large Language Models for Ontology Engineering — A Systematic Literature Review

- **Authors/Org:** Jiayi Li, Maria Poveda, Daniel Garijo (UPM)
- **Year:** 2025
- **URL:** https://www.semantic-web-journal.net/content/large-language-models-ontology-engineering-systematic-literature-review
- **Type:** paper (Semantic Web Journal, systematic review)
- **Evidence Level:** Very High (systematic review, 30 papers analyzed)
- **Key Finding:** LLMs serve primarily as ontology engineers, domain experts, and evaluators. Only 4 of 30 studies involved human participants — critical gap. Pervasive inconsistencies in task definitions, dataset selection, evaluation metrics, and experimental workflows. Incomplete evaluation protocols undermine reproducibility. Key recommendation: develop standardized benchmarks and hybrid workflows integrating LLM automation with human expertise.
- **Relevance to our work:** Validates that our HITL approach addresses a critical gap — most LLM-ontology systems lack human involvement. The call for standardized benchmarks means our gate metrics could become a contribution. The inconsistency finding reinforces why we need deterministic gates (not just LLM-based evaluation).

### Source 16: Ontology Knowledge Inspection Methodology for Quality Assessment and Continuous Improvement

- **Authors/Org:** (Data & Knowledge Engineering journal)
- **Year:** 2021
- **URL:** https://www.sciencedirect.com/science/article/pii/S0169023X21000161
- **Type:** paper
- **Evidence Level:** High
- **Key Finding:** Methodology based on Deming PDCA cycle (Plan-Do-Check-Act) applied to ontology quality management. Quantitative and graphical quality assessment. Fixes ontology inconsistencies while minimizing design defects. Grounded in software engineering quality standards extended to knowledge engineering. Addresses the reality that auto-generated ontologies have errors, inconsistencies, and poor design quality that must be manually fixed.
- **Relevance to our work:** The PDCA mapping is powerful: Plan=define competency questions/schema, Do=agent extraction, Check=gate validation, Act=expert curation. This frames our entire system as a continuous improvement cycle, not just a pipeline. The software engineering quality standards grounding validates our approach of applying software engineering practices (TDD, gates) to ontology engineering.

### Source 17: SHACL — Shapes Constraint Language (W3C Standard)

- **Authors/Org:** W3C (Holger Knublauch, Dimitris Kontokostas, editors)
- **Year:** 2017
- **URL:** https://www.w3.org/TR/shacl/
- **Type:** standard specification
- **Evidence Level:** Very High (W3C standard)
- **Key Finding:** Language for validating RDF graphs against shapes (constraints). Supports property existence, value type, value range, cardinality, and complex conditions. Distinct from OWL: OWL for inference, SHACL for validation. Automated tools leverage SHACL shapes to validate data on ingest, update, or transformation — enabling continuous quality without manual intervention. Developing shapes manually is complex; tools like Astrea auto-generate shapes from ontologies.
- **Relevance to our work:** SHACL is the closest standard analogy to our Pydantic-based gate system. Our Pydantic models function as "shapes" that constrain what valid ontology nodes look like. The OWL/SHACL distinction (inference vs. validation) maps to our separation of LLM extraction (inference) from gate checking (validation). Auto-generation of shapes from ontologies parallels our schema-driven validation.

### Source 18: OntoEKG — LLM-Driven Ontology Construction for Enterprise Knowledge Graphs

- **Authors/Org:** Abdulsobur Oyewale, Tommaso Soru
- **Year:** 2026
- **URL:** https://arxiv.org/html/2602.01276v1
- **Type:** paper
- **Evidence Level:** Medium (recent, limited evaluation)
- **Key Finding:** Four-stage pipeline: data ingestion, ontological element extraction, hierarchy construction with entailment, RDF serialization. Uses Pydantic for strict data model enforcement — forces LLM to output valid JSON with metadata (classes, properties, descriptions, domain, range). Exact-match F1 is very low (0.00–0.10), but fuzzy-match F1 reaches 0.72 in best domain. Positions LLM as "copilot" for domain stakeholders. No active HITL mechanism implemented.
- **Relevance to our work:** The Pydantic enforcement pattern is exactly what we do. The dramatic gap between exact-match and fuzzy-match scores (0.10 vs 0.72) demonstrates why human review is essential — LLMs get the gist right but details wrong. This empirically justifies our expert curation step. The low exact-match scores across domains warn against trusting unvalidated LLM output.

### Source 19: Ontology Evolution — A Survey and Future Challenges

- **Authors/Org:** (Multiple, Springer)
- **Year:** 2010
- **URL:** https://link.springer.com/chapter/10.1007/978-3-642-10580-7_11
- **Type:** survey paper
- **Evidence Level:** High
- **Key Finding:** Ontology versioning defined as "the ability to manage ontology changes and their effects by creating and maintaining different variants." Core challenge: accommodating new changes while preserving consistency. Most versioning approaches do not keep records of changes, preventing tracking rationale. Change management is the core task of ontology versioning and evolution.
- **Relevance to our work:** Our system must track change history with rationale — not just current state. The consistency preservation challenge is what our gates address. The emphasis on change management validates our commit-after-task approach where each cartridge modification is versioned.

---

## Synthesized Claims

### Claim 1: Expert oversight is essential — LLMs alone produce ontologies with significant accuracy gaps
**Confidence:** Very High | **Sources:** S1, S13, S15, S18

LLMs get conceptual structure approximately right (fuzzy-match F1 ~0.72) but exact representations wrong (exact-match F1 ~0.10). Only 4 of 30 studies in the Li et al. systematic review involved human participants. KGValidator shows GPT-4 achieves 0.95 accuracy with combined context but open-source models can fail catastrophically (~0.50). The consensus is that LLMs are "co-pilots" requiring expert validation.

**Implication for us:** Our HITL design is not optional — it addresses a well-documented gap. The gate system provides the deterministic backbone that LLM-only approaches lack.

### Claim 2: Competency questions are the primary mechanism for ontology requirements and evaluation
**Confidence:** Very High | **Sources:** S1, S6, S14, S16

CQs define scope, drive development, and enable testing. Five CQ types exist (Scoping, Validating, Foundational, Relationship, Metaproperty). Automated testing via SPARQL formalization or prompt-driven unit tests achieves 87.5% accuracy. The main challenge is helping users write good CQs — limited guidance exists.

**Implication for us:** Our CQ coverage gate is well-grounded in established practice. We should classify CQs by type and assist users in formulating them. LLM-driven CQ extraction from user stories (OntoChat pattern) could bootstrap this.

### Claim 3: Multi-layer quality assurance with severity classification is the proven approach
**Confidence:** Very High | **Sources:** S5, S10, S14, S17

OOPS! classifies pitfalls as critical/important/minor across Structural/Functional/Usability dimensions. Gene Ontology uses built-in data entry controls + annotation triage + cross-annotation pattern detection. SHACL provides constraint validation on ingest/update/transform. MeLOn defines 8 quality dimensions (completeness, correctness, coherence, applicability, effectiveness, intuitiveness, computational soundness, reusability).

**Implication for us:** Our gate system should have: (1) severity levels (critical blocks merge, important warns, minor logs), (2) multiple dimensions (structural validity, semantic correctness, coverage completeness), (3) automated continuous checking (not just at review time).

### Claim 4: The PDCA cycle maps naturally to AI-assisted ontology refinement
**Confidence:** High | **Sources:** S3, S4, S16, S19

DILIGENT's build→adapt→analyze→revise→update maps to extraction→localization→gate-check→expert-curation→update. Ontology Maturing's four phases (emergence→consolidation→formalization→axiomatization) describe knowledge maturation. The PDCA-based inspection methodology explicitly bridges software engineering QA to knowledge engineering. Ontology evolution research emphasizes tracking change rationale.

**Implication for us:** Our system implements a PDCA cycle: Plan (define schema + CQs), Do (agent extracts), Check (gates validate), Act (expert curates). This is not just a pipeline — it's a continuous improvement loop where each cycle improves both the ontology and the extraction patterns.

### Claim 5: Drift detection and stability metrics are necessary for long-lived ontologies
**Confidence:** High | **Sources:** S10, S11, S12, S19

SemaDrift provides concept stability ranking and version-to-version drift measurement. Wikidata shows uneven quality growth without controls. Gene Ontology refreshes vocabulary daily to prevent drift. Ontology evolution literature emphasizes that most systems fail to track change rationale, making drift invisible.

**Implication for us:** We need: (1) node stability scores (how often a node changes), (2) version-to-version drift measurement, (3) gap detection from query failures, (4) change rationale capture. Query failures are a particularly valuable signal — they indicate where the ontology fails to serve its consumers.

### Claim 6: Separation of review metadata from domain data is an established pattern
**Confidence:** High | **Sources:** S8, S9, S10

WebProtege's ChAO (Changes and Annotations Ontology) stores all change tracking and discussion separately from the domain ontology. Collaborative Protege intercepts GUI actions to create change annotations. Gene Ontology uses evidence codes as separate metadata layer.

**Implication for us:** Review decisions, expert comments, gate results, and change history should live in a separate data structure linked to cartridge nodes — not embedded in the cartridge itself. This keeps the domain model clean while maintaining full auditability.

### Claim 7: Task design and representation format affect expert review quality
**Confidence:** High | **Sources:** S1, S7, S8

Representation format doesn't significantly affect accuracy but affects expert preference (graphical preferred). Objective qualification tests outperform self-assessment for evaluating contributor competence. Prior modeling knowledge improves judgment quality. Discussions integrated with editing (not separate) improve collaboration.

**Implication for us:** Our conversational review interface should present nodes visually when possible. We should track reviewer expertise over time. Review should be inline with the ontology, not a separate workflow.

---

## Gaps Identified

1. **No established framework for query-failure-driven ontology improvement.** While the concept appears in recent KG literature (TCR-QF, OntoLogX), there is no mature methodology for using downstream query failures as signals for ontology gap detection. This is novel territory for our system.

2. **Limited work on Pydantic-as-schema for ontology validation.** The Pydantic/Instructor pattern appears in recent papers (KGValidator, OntoEKG) but is not yet established as a standard approach. Our system may be among the first to use Pydantic models as the primary schema constraint mechanism (analogous to SHACL shapes but in Python).

3. **No studies on LLM-human feedback loops for iterative ontology improvement.** RLHF is discussed generally, but no paper studies how expert corrections on LLM-extracted ontology nodes improve subsequent extractions over time. Our system could contribute here.

4. **Sparse literature on gate architectures for ontology QA.** The concept of deterministic validation gates (as opposed to probabilistic LLM-based evaluation) for ontology quality is not well-studied. SHACL is the closest analogue but operates at a different abstraction level (RDF triples vs. Pydantic models).

5. **No established metrics for "ontology health" as a continuous signal.** Individual quality dimensions are well-defined (completeness, consistency, etc.) but composite health scores and temporal health monitoring are not standardized.

---

## Relevance to Knowledge Cartridge Architecture

### Direct Validations

| Our Design Choice | Validated By | Strength |
|---|---|---|
| Conversational HITL interface for expert review | OntoChat (S1), WebProtege (S8) | Strong |
| Pydantic models as schema constraints | KGValidator (S13), OntoEKG (S18), SHACL analogy (S17) | Moderate (emerging pattern) |
| Deterministic gates (not LLM-based evaluation) | OOPS! (S5), GO QC (S10), SHACL (S17) | Strong |
| Competency question coverage as quality metric | CQ Survey (S6), OntoChat (S1), NeOn (S14) | Very Strong |
| Expert review before merge | DILIGENT (S3), Wikidata governance (S11), Li SLR (S15) | Very Strong |
| Change tracking with rationale | ChAO (S8,S9), Ontology Evolution (S19), DILIGENT (S3) | Strong |

### Architectural Recommendations from Literature

1. **Adopt PDCA as the explicit improvement model.** Frame the system as Plan (CQs + schema) → Do (extraction) → Check (gates) → Act (curation). Each cycle improves both the ontology and the extraction quality.

2. **Implement multi-source validation.** Following KGValidator: validate against (a) schema/Pydantic conformance, (b) source document consistency, (c) existing cartridge cross-references.

3. **Separate review metadata from domain data.** Following ChAO pattern: store review decisions, expert comments, gate results in a linked but separate structure.

4. **Track concept stability.** Following SemaDrift: measure how often each node changes across versions. Unstable nodes may need expert attention or indicate poor extraction patterns.

5. **Use query failures as gap signals.** When downstream consumers fail to answer questions using the cartridge, log the failure, classify the gap type, and trigger an extraction→curation cycle.

6. **Classify CQs by type.** Distinguish Scoping, Validating, Foundational, Relationship, and Metaproperty questions. Use VCQs for gate automation.

7. **Design for incremental formalization.** Following Ontology Maturing: allow nodes to exist at different maturity levels (draft → reviewed → validated → axiomatized). Gates enforce minimum maturity for production use.

---

*Research conducted: 2026-03-24*
*Method: WebSearch (14 queries) + WebFetch (6 deep reads) + triangulation*
*Confidence in overall synthesis: High*
