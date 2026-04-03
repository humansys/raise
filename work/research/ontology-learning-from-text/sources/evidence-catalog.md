# Evidence Catalog: Ontology Learning from Text with LLMs

> Research conducted: 2026-03-18
> Researcher: Rai (Claude Opus 4.6)
> Searches performed: 18 web searches across academic, production, and community sources

---

## Source Index

| # | Short Name | Type | Evidence Level | Date |
|---|-----------|------|---------------|------|
| S1 | LLMs4OL Challenge 2024 | Primary | High | 2024-09 |
| S2 | LLMs4OL Challenge 2025 | Primary | High | 2025-10 |
| S3 | SWJ Systematic Literature Review | Primary | Very High | 2025 |
| S4 | EDC Framework (EMNLP 2024) | Primary | Very High | 2024-04 |
| S5 | OntoGPT / SPIRES | Primary | Very High | 2024-03 |
| S6 | TnT-LLM (Microsoft, KDD 2024) | Primary | Very High | 2024-03 |
| S7 | LLooM Concept Induction | Primary | High | 2024-04 |
| S8 | KGGen (NeurIPS 2025) | Primary | Very High | 2025-02 |
| S9 | KARMA Multi-Agent (NeurIPS 2025) | Primary | Very High | 2025-02 |
| S10 | AutoSchemaKG (HKUST) | Primary | High | 2025-05 |
| S11 | Neo4j LLM Graph Builder | Secondary | High | 2024-2025 |
| S12 | LlamaIndex Property Graph Index | Secondary | High | 2024 |
| S13 | Strwythura (DerwenAI) | Secondary | Medium | 2024 |
| S14 | Microsoft GraphRAG | Secondary | Very High | 2024 |
| S15 | OntoEKG (LiberAI) | Primary | Medium | 2025-02 |
| S16 | CQbyCQ / Ontogenia | Primary | High | 2025-03 |
| S17 | GLiNER (NAACL 2024) | Primary | High | 2024 |
| S18 | Keet Blog — LLM Ontology Feasibility | Tertiary | High | 2025-03 |
| S19 | LLM-empowered KG Construction Survey | Primary | High | 2025-10 |
| S20 | Bio-Ontology LLM Review (PMC) | Primary | High | 2025 |
| S21 | Ontology Learning from Text Analysis | Primary | Medium | 2024 |
| S22 | DSPy Neo4j Knowledge Graph | Secondary | Medium | 2024 |
| S23 | OntoGenix | Primary | Medium | 2024 |
| S24 | Fine-tuning vs Prompting for KG (Frontiers) | Primary | High | 2025 |

---

## Detailed Source Entries

### S1 — LLMs4OL 2024: 1st Large Language Models for Ontology Learning Challenge

- **URL**: https://arxiv.org/html/2409.10146v1
- **Type**: Primary (peer-reviewed challenge proceedings)
- **Evidence Level**: High
- **Date**: September 2024
- **Key Finding**: Three OL tasks benchmarked (term typing, taxonomy discovery, non-taxonomic relation extraction). GPT-based LLMs excelled at context comprehension. RAG-augmented approaches improved accuracy.
- **Relevance**: Establishes that LLMs can perform core OL subtasks; taxonomy discovery and relation extraction are viable but require scaffolding.

### S2 — LLMs4OL 2025: 2nd Large Language Models for Ontology Learning Challenge

- **URL**: https://www.tib-op.org/ojs/index.php/ocp/article/view/2913
- **Type**: Primary (challenge proceedings)
- **Evidence Level**: High
- **Date**: October 2025
- **Key Finding**: Hybrid pipelines (commercial LLMs + domain-tuned embeddings + fine-tuning) achieved strongest overall performance. Specialized domain models improved biomedical/technical results.
- **Relevance**: Validates that hybrid approaches outperform pure LLM or pure traditional NLP. Direct evidence for pipeline design.

### S3 — Large Language Models for Ontology Engineering: A Systematic Literature Review

- **URL**: https://www.semantic-web-journal.net/system/files/swj3864.pdf
- **Type**: Primary (peer-reviewed SLR, Semantic Web Journal)
- **Evidence Level**: Very High
- **Date**: 2025
- **Key Finding**: Analyzed 34 peer-reviewed papers (2018-2025), extracted 46 distinct ontology engineering tasks where LLMs are applied. LLMs reduce manual effort but face hallucination, consistency, and bias challenges. Hybrid methods (MapperGPT, MILA, SPIREX) achieve measurable gains.
- **Relevance**: Comprehensive landscape view. Identifies which OE tasks LLMs help with and which remain hard.

### S4 — Extract, Define, Canonicalize (EDC) — EMNLP 2024

- **URL**: https://aclanthology.org/2024.emnlp-main.548/
- **Code**: https://github.com/clear-nus/edc
- **Type**: Primary (top-tier NLP venue)
- **Evidence Level**: Very High
- **Date**: April 2024
- **Key Finding**: Three-phase pipeline: (1) open information extraction, (2) schema definition, (3) post-hoc canonicalization. Works with or without predefined schema. Trained retrieval component fetches relevant schema elements (RAG-like). Handles large schemas beyond context window.
- **Relevance**: Directly applicable architecture. The "extract first, define schema second, canonicalize third" pattern is exactly what we need for corpus-first ontology learning.

### S5 — OntoGPT / SPIRES (Monarch Initiative)

- **URL**: https://github.com/monarch-initiative/ontogpt
- **Paper**: https://pmc.ncbi.nlm.nih.gov/articles/PMC10924283/
- **Type**: Primary (peer-reviewed, Bioinformatics journal + active OSS)
- **Evidence Level**: Very High
- **Date**: 2024 (published in Bioinformatics, March 2024)
- **Key Finding**: SPIRES uses structured prompting with knowledge schemas (LinkML) to extract typed entities and relations. Zero-shot learning. Grounds extracted entities against existing ontologies. Applied across food recipes, drug mechanisms, disease treatments.
- **Relevance**: Most mature schema-driven extraction tool. The knowledge schema concept (define shape, let LLM fill it) is a validated pattern. Python package, actively maintained.

### S6 — TnT-LLM: Text Mining at Scale with Large Language Models (Microsoft, KDD 2024)

- **URL**: https://arxiv.org/html/2403.12173v1
- **Type**: Primary (KDD 2024, top-tier venue)
- **Evidence Level**: Very High
- **Date**: March 2024
- **Key Finding**: Two-step pipeline: (1) LLM-generated taxonomy from sampled data, (2) LLM-based text classification using generated taxonomy. GPT-4 produces label names and descriptions from conversation summaries. Outperforms other methods in most cases.
- **Relevance**: Demonstrates practical taxonomy induction from unstructured corpus at scale. The "sample-summarize-induce" pattern is directly applicable to our transcript corpus.

### S7 — LLooM: Concept Induction from Unstructured Text

- **URL**: https://arxiv.org/html/2404.12259v1
- **Type**: Primary (peer-reviewed)
- **Evidence Level**: High
- **Date**: April 2024
- **Key Finding**: Three-operator pipeline: Distill (condense with LLM), Cluster (group distilled content), Synthesize (propose high-level concepts via LLM). Iteratively produces concepts of increasing generality.
- **Relevance**: The distill-cluster-synthesize pattern is useful for bottom-up concept discovery from transcripts.

### S8 — KGGen: Extracting Knowledge Graphs from Plain Text (NeurIPS 2025)

- **URL**: https://arxiv.org/abs/2502.09956
- **Code**: https://github.com/stair-lab/kg-gen
- **Type**: Primary (NeurIPS 2025)
- **Evidence Level**: Very High
- **Date**: February 2025
- **Key Finding**: LM-based extractor predicts subject-predicate-object triples, then iterative LM-based clustering refines the graph (normalizes tense, plurality, capitalization). Released MINE benchmark. Available as `pip install kg-gen`. Supports multiple LLM providers via LiteLLM.
- **Relevance**: Most accessible tool for quick KG extraction from text. The clustering step for entity normalization is a key insight for handling inconsistent terminology in transcripts.

### S9 — KARMA: Multi-Agent LLMs for Knowledge Graph Enrichment (NeurIPS 2025)

- **URL**: https://arxiv.org/abs/2502.06472
- **Code**: https://github.com/YuxingLu613/KARMA
- **Type**: Primary (NeurIPS 2025)
- **Evidence Level**: Very High
- **Date**: February 2025
- **Key Finding**: Nine collaborative agents (entity discovery, relation extraction, schema alignment, conflict resolution, etc.). Cross-agent verification. 83.1% LLM-verified correctness on 1,200 PubMed articles. 38,230 new entities extracted. Conflict edges reduced 18.6%.
- **Relevance**: Multi-agent architecture as reference for complex extraction. The conflict resolution agent pattern is valuable for handling contradictory information across corpus sources.

### S10 — AutoSchemaKG: Autonomous KG Construction (HKUST)

- **URL**: https://arxiv.org/abs/2505.23628
- **Code**: https://github.com/HKUST-KnowComp/AutoSchemaKG
- **Type**: Primary (arXiv, HKUST)
- **Evidence Level**: High
- **Date**: May 2025
- **Key Finding**: No predefined schema needed. Processes 50M+ documents, 900M+ nodes, 5.9B edges. Schema induction achieves 92% semantic alignment with human-crafted schemas. Models events alongside entities (temporal, causal, procedural knowledge).
- **Relevance**: Demonstrates schema-free extraction at massive scale. The event modeling capability is relevant for process-oriented methodology like Scaling Up.

### S11 — Neo4j LLM Knowledge Graph Builder

- **URL**: https://neo4j.com/labs/genai-ecosystem/llm-graph-builder/
- **Code**: https://github.com/neo4j-labs/llm-graph-builder
- **Type**: Secondary (production tool from major vendor)
- **Evidence Level**: High
- **Date**: 2024-2025 (continuously updated)
- **Key Finding**: Supports multiple LLMs (OpenAI, Gemini, Claude, Llama3, Qwen). Handles PDFs, documents, images, YouTube transcripts. Includes entity resolver for deduplication. Custom extraction prompts supported. React + FastAPI, deployable via Docker.
- **Relevance**: Most production-ready tool for our use case. Directly handles transcripts. Entity resolution built-in. Customizable extraction guidance.

### S12 — LlamaIndex Property Graph Index

- **URL**: https://www.llamaindex.ai/blog/introducing-the-property-graph-index-a-powerful-new-way-to-build-knowledge-graphs-with-llms
- **Docs**: https://docs.llamaindex.ai/en/stable/module_guides/indexing/lpg_index_guide/
- **Type**: Secondary (major framework documentation)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Three extraction modes: schema-guided (constrained), free-form (LLM infers), dynamic (LLM defines ontology on-the-fly). Modular architecture allows multiple extractors. Schema hints guide but don't enforce.
- **Relevance**: Programmable extraction with schema flexibility. Good for iterative refinement where schema evolves.

### S13 — Strwythura (DerwenAI)

- **URL**: https://github.com/DerwenAI/strwythura
- **Type**: Secondary (reference implementation)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Full ontology pipeline: structured + unstructured sources, entity resolution, knowledge graph, enhanced GraphRAG. Uses DSPy, spaCy, GLiNER, RDFlib, NetworkX. Includes human-in-the-loop curation stage. Produces Streamlit app with MLOps instrumentation.
- **Relevance**: Complete reference architecture combining multiple tools. The explicit HITL curation stage validates that human review is part of production pipelines.

### S14 — Microsoft GraphRAG

- **URL**: https://microsoft.github.io/graphrag/
- **Type**: Secondary (major vendor, production system)
- **Evidence Level**: Very High
- **Date**: 2024
- **Key Finding**: Slices corpus into TextUnits, extracts entities/relationships/claims, builds community hierarchy, generates summaries. Two approaches: top-down (define ontology first) or bottom-up (extract schema from data). Community detection for hierarchical summarization.
- **Relevance**: The community hierarchy pattern is useful for organizing extracted knowledge at multiple levels of abstraction.

### S15 — OntoEKG: LLM-Driven Ontology for Enterprise KGs

- **URL**: https://arxiv.org/abs/2602.01276
- **Code**: https://github.com/LiberAI/OntoEKG
- **Type**: Primary (arXiv)
- **Evidence Level**: Medium
- **Date**: February 2025
- **Key Finding**: Two-phase pipeline: extraction module (identifies classes/properties) + entailment module (infers class hierarchy, serializes to RDF). F1=0.724 with fuzzy matching, F1=0.102 with exact matching on enterprise policy texts.
- **Relevance**: The large gap between fuzzy and exact F1 demonstrates that LLM extraction is "approximately right" — good for initial draft, requires human refinement.

### S16 — CQbyCQ / Ontogenia: Competency Questions to OWL

- **URL**: https://arxiv.org/abs/2503.05388
- **Type**: Primary (peer-reviewed)
- **Evidence Level**: High
- **Date**: March 2025
- **Key Finding**: Two prompting techniques for OWL generation from competency questions. Ontogenia with o1-preview produces ontologies that significantly outperform novice ontology engineers. Tested on 100 CQs across 10 ontologies.
- **Relevance**: Validates that well-structured prompts can produce engineer-quality ontologies. CQs as specification mechanism is applicable (we can formulate CQs about Scaling Up domain).

### S17 — GLiNER: Generalist NER Model (NAACL 2024)

- **URL**: https://github.com/urchade/GLiNER
- **Type**: Primary (NAACL 2024)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Lightweight NER model competitive with ChatGPT in zero-shot. Runs on CPUs. Supports joint entity and relation extraction. Fine-tunable. Apache 2.0 license.
- **Relevance**: Cost-effective alternative to LLM-based NER for high-volume entity extraction. Can be part of hybrid pipeline.

### S18 — Keet Blog: Is Developing an Ontology from an LLM Feasible?

- **URL**: https://keet.wordpress.com/2025/03/26/is-developing-an-ontology-from-an-llm-really-feasible/
- **Type**: Tertiary (expert blog, Prof. C. Maria Keet — ontology engineering textbook author)
- **Evidence Level**: High (domain expert opinion)
- **Date**: March 2025
- **Key Finding**: LLMs don't store structured facts/axioms needed for reliable inference. Different runs produce different ontologies. However, the traditional pipeline is laborious enough that LLM shortcuts are worth exploring. LLMs can provide a "first version" but not a finished ontology.
- **Relevance**: Important counterweight. Sets realistic expectations: LLMs generate drafts, not finished ontologies. Human expertise remains central.

### S19 — LLM-empowered Knowledge Graph Construction: A Survey

- **URL**: https://arxiv.org/abs/2510.20345
- **Type**: Primary (comprehensive survey)
- **Evidence Level**: High
- **Date**: October 2025
- **Key Finding**: Covers NER, RE, event extraction, entity linking. Prompt engineering, RAG, and ensemble learning are key technical approaches. Hallucinated triples remain a critical issue in domain-specific corpora.
- **Relevance**: Broad landscape confirmation. RAG + ensemble as key patterns.

### S20 — Large Language Models in Bio-Ontology Research: A Review

- **URL**: https://pmc.ncbi.nlm.nih.gov/articles/PMC12649945/
- **Type**: Primary (PMC peer-reviewed)
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: MILA achieved F1 0.83-0.95 in biomedical alignment by invoking LLMs only for uncertain mappings, reducing LLM queries by 90%+. Hybrid methods (SPIRES, DRAGON-AI, SPIREX) show measurable gains with selective prompting + HITL validation.
- **Relevance**: The "LLM only for uncertain cases" pattern is a key efficiency insight. 90% query reduction means hybrid approaches are far more cost-effective.

### S21 — Exploring Large Language Models for Ontology Learning

- **URL**: https://iacis.org/iis/2024/4_iis_2024_299-310.pdf
- **Type**: Primary (conference paper)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: LLMs identify classes and individuals well but often miss inter-class properties. Inconsistent/incorrect properties between individuals are common.
- **Relevance**: Confirms that relationship extraction is harder than entity extraction for LLMs.

### S22 — DSPy Neo4j Knowledge Graph

- **URL**: https://github.com/chrisammon3000/dspy-neo4j-knowledge-graph
- **Type**: Secondary (open-source implementation)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: DSPy signatures for entity/relation extraction. Cypher generation for Neo4j. Demonstrates programmatic LLM pipeline for KG construction.
- **Relevance**: Shows DSPy as viable scaffolding framework for our pipeline.

### S23 — OntoGenix: LLM Ontology Engineering from Datasets

- **URL**: https://www.sciencedirect.com/science/article/pii/S0306457324004011
- **Type**: Primary (ScienceDirect)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: LLM-powered pipeline for automating ontology development from datasets.
- **Relevance**: Complementary approach (from structured data rather than text).

### S24 — Fine-tuning vs Prompting for KG Construction

- **URL**: https://www.frontiersin.org/journals/big-data/articles/10.3389/fdata.2025.1505877/full
- **Type**: Primary (Frontiers, peer-reviewed)
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: Fine-tuned Mistral with 7-shot examples performs exceptionally well on Triple Match F1. Fine-tuning outperforms zero-shot prompting for domain-specific extraction.
- **Relevance**: For production quality, fine-tuning a smaller model on domain examples may outperform zero-shot GPT-4.

---

## Sources Not Included (Reviewed and Excluded)

- Generic NLP vs LLM comparison articles (no ontology-specific content)
- Hallucination survey papers without KG/ontology focus
- RDF/OWL standard documentation (well-known, no novel findings)
- Marketing/vendor content without technical depth

---

*Catalog contains 24 sources: 16 primary, 6 secondary, 2 tertiary*
*Evidence levels: 7 Very High, 11 High, 6 Medium, 0 Low*
