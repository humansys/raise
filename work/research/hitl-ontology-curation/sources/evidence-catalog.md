# Evidence Catalog: HITL Ontology Curation

> Research Question: Where is the domain expert irreplaceable in the ontology construction pipeline, and what human-in-the-loop patterns maximize quality while minimizing cognitive load?

---

## Source Index

| # | Short ID | Type | Evidence | Key Finding |
|---|----------|------|----------|-------------|
| 1 | DRAGON-AI | Primary | High | LLM-generated definitions score acceptably but significantly below human-curated ones; expert confidence correlates with ability to detect LLM flaws |
| 2 | OntoChat-ESWC | Primary | High | Conversational ontology elicitation achieves 87.5% accuracy on requirement classification with non-expert users |
| 3 | Kommineni-2024 | Primary | Medium | Full LLM pipeline for ontology+KG construction feasible but 21% disagreement rate with human annotator on CQ evaluation |
| 4 | KG-Validation-LLM-HITL | Primary | High | LLM-based KG validation achieves 88% precision but only 44% recall; human oversight essential for completeness |
| 5 | OntoGPT-SPIRES | Primary | High | Zero-shot ontology extraction achieves 65% agreement with humans; varies heavily by information type |
| 6 | Bio-Ontology-LLM-Review | Secondary | High | ChatGPT 90%+ accuracy for well-defined categories (diseases, drugs) but 50-60% for ambiguous ones (symptoms) |
| 7 | HyWay-NeOn-LLM | Primary | High | LLM-augmented NeOn framework accelerates ontology design without compromising accuracy when expert validation retained |
| 8 | SWJ-Systematic-Review | Secondary | Very High | LLM outputs approach quality of novice human modelers; not yet expert-level |
| 9 | Structural-Hallucination | Primary | High | LLMs produce structural hallucinations: fabricated concepts elevated to highest-centrality positions in generated graphs |
| 10 | Expert-Validation-Framework | Primary | Medium | Visual interfaces with drag-and-drop and simplified approval workflows enable broader non-technical expert participation |
| 11 | Annotation-Fatigue-Pareto | Secondary | Medium | Quality degrades after 90 minutes; 20-minute breaks optimal; batch similar decisions to reduce cognitive switching |
| 12 | Wikidata-Quality | Primary | High | Balanced bot+human contribution yields best quality; crowd assists experts on easy tasks, experts focus on hard ones |
| 13 | GO-Curation-MGI | Primary | High | Gene Ontology manual curation workflow: literature -> expert indexing -> evidence-coded annotation -> peer review |
| 14 | SNOMED-Crowd | Primary | High | Crowd accuracy similar to experts for verification; crowd best as assistant (easy tasks) not replacement |
| 15 | Confidence-Routing | Secondary | Medium | Tiered thresholds: >90% auto-process, 50-89% human review, <50% alert; calibration essential |
| 16 | WebProtege-Usability | Primary | Medium | Customizable UI with knowledge-acquisition forms lowers entry barrier for domain experts |
| 17 | KG-Curation-Framework | Secondary | High | KG curation = assessment + cleaning + enrichment; fully automatic construction not yet feasible |
| 18 | Accelerating-KG-OE | Secondary | Very High | Modular ontology approaches central to LLM-assisted engineering; LLMs accelerate but don't replace expert validation |
| 19 | OntoChat-Participatory | Primary | High | Participatory prompting improves requirement elicitation; 62.5% found interaction intuitive, 87.5% found clusters meaningful |
| 20 | Decision-Fatigue-Neuroscience | Secondary | Medium | Decision quality degrades predictably over sessions; strategic timing and batching conserve mental energy |

---

## Detailed Entries

### 1. DRAGON-AI (Dynamic Retrieval Augmented Generation of Ontologies using AI)

- **Citation**: Matentzoglu et al. (2024). "Dynamic Retrieval Augmented Generation of Ontologies using Artificial Intelligence." *Journal of Biomedical Semantics*.
- **URL**: https://jbiomedsem.biomedcentral.com/articles/10.1186/s13326-024-00320-3
- **Type**: Primary research
- **Evidence Level**: High
- **Key Finding**: LLM-generated ontology definitions are consistently acceptable (grade >3/5) but statistically significantly below human-curated definitions on all metrics. Evaluators with higher domain confidence were better at detecting LLM definition flaws. Less confident evaluators could not distinguish LLM from human definitions.
- **Relevance**: Directly shows WHERE experts are irreplaceable: evaluating quality of generated definitions. Also shows that domain depth matters -- Eduardo's deep Scaling Up knowledge is exactly what's needed.
- **Date**: 2024

### 2. OntoChat (ESWC 2024)

- **Citation**: Zheng et al. (2024). "OntoChat: a Framework for Conversational Ontology Engineering using Language Models." *ESWC 2024*.
- **URL**: https://arxiv.org/abs/2403.05921
- **Type**: Primary research
- **Evidence Level**: High
- **Key Finding**: Conversational interface for ontology engineering achieves 87.5% accuracy on requirement classification. Domain experts (N=6) could create user stories through conversation without ontology engineering knowledge. 62.5% found interaction intuitive.
- **Relevance**: Directly validates the "agent proposes, expert validates via conversation" pattern. Non-technical users successfully contributed to ontology engineering through natural dialogue.
- **Date**: 2024

### 3. Kommineni et al. — From Human Experts to Machines

- **Citation**: Kommineni, König-Ries, Samuel (2024). "From human experts to machines: An LLM supported approach to ontology and knowledge graph construction." *arXiv:2403.08345*.
- **URL**: https://arxiv.org/abs/2403.08345
- **Type**: Primary research
- **Evidence Level**: Medium
- **Key Finding**: Full LLM pipeline produced ontology with 45 classes, 41 relationships, 365 axioms. 42 disagreements out of 200 CQ evaluations (21% disagreement rate). Human-in-the-loop recommended for evaluating auto-generated KGs.
- **Relevance**: Quantifies the disagreement rate between LLM and human judgment. The 21% error rate means roughly 1 in 5 items needs human correction.
- **Date**: 2024

### 4. KG Validation by Integrating LLMs and Human-in-the-Loop

- **Citation**: Tsaneva et al. (2025). "Knowledge graph validation by integrating LLMs and human-in-the-loop." *Information Processing and Management*.
- **URL**: https://www.sciencedirect.com/science/article/pii/S030645732500086X
- **Type**: Primary research
- **Evidence Level**: High
- **Key Finding**: LLM-based validation achieved 88% precision but only 44% recall. The precision-recall gap means LLMs are decent at confirming correct facts but miss many valid ones. Human review essential for completeness.
- **Relevance**: Quantifies the complementary strengths: LLMs good at precision (confirming what's right), humans essential for recall (catching what's missing). For Scaling Up ontology, Eduardo catches the gaps.
- **Date**: 2025

### 5. OntoGPT / SPIRES

- **Citation**: Caufield et al. (2024). "Structured Prompt Interrogation and Recursive Extraction of Semantics (SPIRES)." *Bioinformatics*.
- **URL**: https://academic.oup.com/bioinformatics/article/40/3/btae104/7612230
- **Type**: Primary research
- **Evidence Level**: High
- **Key Finding**: Zero-shot ontology extraction achieves 65% average agreement with human reviewers. Highest agreement for standardized information; lowest for interpretation-heavy content. No training data needed for new domains.
- **Relevance**: 65% agreement sets a baseline -- the system gets about 2/3 right on first pass. Interpretation-heavy content (like business methodology) will likely be in the lower range, increasing need for Eduardo's review.
- **Date**: 2024

### 6. LLMs in Bio-Ontology Research (Review)

- **Citation**: Various (2025). "Large Language Models in Bio-Ontology Research: A Review." *MDPI Bioengineering*.
- **URL**: https://pmc.ncbi.nlm.nih.gov/articles/PMC12649945/
- **Type**: Secondary (review)
- **Evidence Level**: High
- **Key Finding**: ChatGPT achieves 90%+ accuracy for well-defined categories (disease names, drug names) but drops to 50-60% for ambiguous categories (symptoms). Domain-specific accuracy varies dramatically by concept type.
- **Relevance**: Predicts that LLMs will handle well-defined Scaling Up concepts (BHAG, Hedgehog) accurately but struggle with nuanced relationships and contextual application guidance.
- **Date**: 2025

### 7. HyWay — LLM-Augmented NeOn Framework

- **Citation**: Sack et al. (2025). "LLM-supported collaborative ontology design for data and knowledge management platforms." *Frontiers in Big Data*.
- **URL**: https://www.frontiersin.org/journals/big-data/articles/10.3389/fdata.2025.1676477/full
- **Type**: Primary research
- **Evidence Level**: High
- **Key Finding**: LLM augmentation of established NeOn methodology accelerates ontology development without compromising semantic accuracy when expert validation is retained. Expert-led workflow with LLM assistance is the effective pattern.
- **Relevance**: Validates the "LLM drafts, expert validates" architecture. Acceleration comes from automating drafting, not from removing expert judgment.
- **Date**: 2025

### 8. Systematic Literature Review — LLMs for Ontology Engineering

- **Citation**: (2025). "Large Language Models for Ontology Engineering: A Systematic Literature Review." *Semantic Web Journal*.
- **URL**: https://www.semantic-web-journal.net/system/files/swj3864.pdf
- **Type**: Secondary (systematic review)
- **Evidence Level**: Very High
- **Key Finding**: LLM outputs approach quality of novice human modelers but not expert level. GPT-4 performance validated by multiple independent studies. Modular ontology approaches are central to effective LLM-assisted engineering.
- **Relevance**: Sets the quality ceiling: LLMs are junior ontology engineers, not senior ones. Eduardo's expert judgment is the quality differentiator.
- **Date**: 2025

### 9. Structural Hallucination in LLMs

- **Citation**: (2025). "Structural Hallucination in Large Language Models: A Network-Based Evaluation." *arXiv*.
- **URL**: https://arxiv.org/html/2603.01341v1
- **Type**: Primary research
- **Evidence Level**: High
- **Key Finding**: LLMs produce structural hallucinations where fabricated concepts are elevated to the highest-centrality positions in generated knowledge graphs. This is not random error but systematic distortion of conceptual architecture.
- **Relevance**: Critical risk for Scaling Up ontology: LLM could invent plausible-sounding business concepts and place them centrally. Eduardo's review of the STRUCTURE (not just individual terms) is essential.
- **Date**: 2025

### 10. Expert Validation Framework (EVF)

- **Citation**: (2025). "The Expert Validation Framework: Enabling Domain Expert Control in AI Engineering." *arXiv*.
- **URL**: https://arxiv.org/html/2601.12327
- **Type**: Primary research
- **Evidence Level**: Medium
- **Key Finding**: Visual interfaces with drag-and-drop, simplified approval workflows, and structured specification enable non-technical expert participation. Card-sorting activities effective for categorizing concepts.
- **Relevance**: Design patterns for Eduardo's interface: card-sorting for concept categorization, visual approval workflows, no programming required.
- **Date**: 2025

### 11. Annotation Fatigue and Session Optimization

- **Citation**: Pareto.ai (2025). "Annotation fatigue: Why human data quality declines over time."
- **URL**: https://pareto.ai/blog/annotation-fatigue-why-human-data-quality-declines-over-time
- **Type**: Secondary (industry research)
- **Evidence Level**: Medium
- **Key Finding**: Brain optimal for 90 minutes before needing 20-minute break. Quality degrades sharply after sustained focus. Subjective judgment tasks cause faster burnout than mechanical tasks. Batching similar decisions reduces cognitive switching costs.
- **Relevance**: Direct design constraint: Eduardo's review sessions should be <90 minutes, ideally 20-30 minutes of focused review. Batch similar concept types together.
- **Date**: 2025

### 12. Wikidata Quality and Collaborative Curation

- **Citation**: Piscopo & Simperl (2019 / cited in 2024 quality studies). "What Makes a Good Collaborative Knowledge Graph."
- **URL**: https://king-s-knowledge-graph-lab.github.io/WikidataQualityToolkit/
- **Type**: Primary research
- **Evidence Level**: High
- **Key Finding**: Balanced contribution of bots and human editors yields best quality. Higher anonymous edits reduce quality. Tenure and interest diversity improve outcomes. Quality indicators based on community consensus and constraint violations.
- **Relevance**: Even at Wikidata scale, human curation remains essential. Bot-only curation degrades quality. The human-bot balance is the key design parameter.
- **Date**: 2019-2024

### 13. Gene Ontology Manual Curation (MGI)

- **Citation**: Baldarelli et al. (2012). "Manual Gene Ontology annotation workflow at the Mouse Genome Informatics Database." *Database*.
- **URL**: https://academic.oup.com/database/article/doi/10.1093/database/bas045/439709
- **Type**: Primary research
- **Evidence Level**: High
- **Key Finding**: GO curation follows: literature collection -> expert indexing -> evidence-coded annotation -> peer review. Each annotation carries an evidence code indicating the type of support. Expert discipline knowledge is prerequisite.
- **Relevance**: Evidence-code pattern applicable: each ontology assertion should carry a provenance tag (source: book, source: Eduardo, source: LLM-draft).
- **Date**: 2012 (established methodology, still current)

### 14. SNOMED CT Crowd Verification

- **Citation**: Mortensen et al. (2016). "Is the crowd better as an assistant or a replacement in ontology engineering?" *PubMed*.
- **URL**: https://pubmed.ncbi.nlm.nih.gov/26873781/
- **Type**: Primary research
- **Evidence Level**: High
- **Key Finding**: Crowd accuracy similar to experts for ontology verification tasks. Crowd is better as expert ASSISTANT (handling easy verifications) than expert REPLACEMENT. Experts should focus on difficult/ambiguous tasks.
- **Relevance**: The LLM plays the "crowd" role -- handling easy/obvious assertions. Eduardo focuses on hard/nuanced ones. This is the division of labor.
- **Date**: 2016

### 15. Confidence-Based Routing for HITL

- **Citation**: Multiple sources (2024-2025). Confidence scoring and tiered thresholds.
- **URL**: https://briq.com/blog/confidence-thresholds-reliable-ai-systems
- **Type**: Secondary (industry practice)
- **Evidence Level**: Medium
- **Key Finding**: Tiered confidence thresholds: >90% auto-accept, 50-89% flag for review, <50% alert. Calibration is essential -- many AI systems are overconfident. Confidence data drives continuous improvement.
- **Relevance**: Design pattern for Eduardo's queue: high-confidence items auto-accepted, medium items in his review queue, low-confidence items flagged for discussion.
- **Date**: 2024-2025

### 16. WebProtege Usability

- **Citation**: Tudorache et al. (2013). "WebProtege: A Collaborative Ontology Editor and Knowledge Acquisition Tool for the Web." *Semantic Web*.
- **URL**: https://pmc.ncbi.nlm.nih.gov/articles/PMC3691821/
- **Type**: Primary research
- **Evidence Level**: Medium
- **Key Finding**: Customizable UI with knowledge-acquisition forms lowers entry barrier for domain experts. Declarative form-based interfaces more accessible than tree-based ontology editors. Simple web-based tools covering frequent OWL constructs are sufficient for many users.
- **Relevance**: Form-based UIs are proven accessible. But even WebProtege requires ontology concepts -- conversational interface is one level simpler.
- **Date**: 2013

### 17. Knowledge Graph Curation Framework

- **Citation**: (2022). "Knowledge Graph Curation: A Practical Framework." *ACM*.
- **URL**: https://dl.acm.org/doi/fullHtml/10.1145/3502223.3502247
- **Type**: Secondary (framework)
- **Evidence Level**: High
- **Key Finding**: KG curation lifecycle: assessment (define metrics) -> cleaning (verify against constraints) -> enrichment (detect duplicates, add missing). Fully automatic construction not feasible. Human input needed at multiple steps.
- **Relevance**: Provides the lifecycle model. Assessment and cleaning can be partially automated; enrichment and edge-case resolution require Eduardo.
- **Date**: 2022

### 18. Accelerating KG and Ontology Engineering with LLMs

- **Citation**: Shimizu & Hitzler (2025). "Accelerating knowledge graph and ontology engineering with large language models." *Journal of Web Semantics*.
- **URL**: https://www.sciencedirect.com/science/article/pii/S1570826825000022
- **Type**: Secondary (survey/position)
- **Evidence Level**: Very High
- **Key Finding**: Modular ontology approaches are central to effective LLM-assisted engineering. LLMs accelerate drafting, alignment, and population but expert validation remains mandatory for quality. Ontology Design Patterns improve LLM output consistency.
- **Relevance**: Modular approach fits Scaling Up: each chapter/framework is a module. LLM drafts module, Eduardo validates.
- **Date**: 2025

### 19. OntoChat with Participatory Prompting

- **Citation**: Zheng et al. (2024). "Improving Ontology Requirements Engineering with OntoChat and Participatory Prompting." *AAAI Spring Symposium*.
- **URL**: https://ojs.aaai.org/index.php/AAAI-SS/article/download/31799/33966/35868
- **Type**: Primary research
- **Evidence Level**: High
- **Key Finding**: Participatory prompting (user guides the LLM through structured questions) improves elicitation quality. 87.5% of ontology engineers found resulting competency question clusters meaningful.
- **Relevance**: The "structured conversation" pattern works. Eduardo answers questions about Scaling Up; system organizes responses into ontology structure.
- **Date**: 2024

### 20. Decision Fatigue Neuroscience

- **Citation**: Global Council for Behavioral Science (2024). "The Neuroscience of Decision Fatigue."
- **URL**: https://gc-bs.org/articles/the-neuroscience-of-decision-fatigue/
- **Type**: Secondary (review)
- **Evidence Level**: Medium
- **Key Finding**: Decision quality degrades predictably over sessions. Strategic timing of complex decisions for high-energy periods, batching similar decisions, and reducing total decision count all conserve cognitive resources.
- **Relevance**: Eduardo should review complex/ambiguous items first in sessions, routine approvals later. Total decisions per session should be bounded.
- **Date**: 2024

---

## Sources Not Found / Gaps

1. **No direct study on ontology curation for business methodology domains** (all evidence from biomedical, music, academic domains)
2. **No quantitative study on minimum viable expert involvement threshold** for "good enough" ontology quality
3. **No published conversational ontology curation tool designed specifically for non-programmer business experts** (OntoChat closest but targets ontology engineers)
4. **Limited evidence on long-term sustainability** of expert curation commitment (most studies are short-term evaluations)

---

*Catalog compiled: 2026-03-18*
*Research conducted by: Rai (Claude Opus 4.6)*
*Total sources reviewed: 20 primary + numerous supporting*
*Search strategy: Academic (arxiv, PMC, ACM, Springer, Frontiers, SWJ), Industry (Pareto.ai, Briq), Tools (OntoGPT, WebProtege, PoolParty)*
