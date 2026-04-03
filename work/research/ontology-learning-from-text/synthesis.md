# Synthesis: Ontology Learning from Text with LLMs

> Triangulated claims, patterns, and gaps
> Based on 24 sources (see evidence-catalog.md)

---

## Triangulated Claims

### Claim 1: LLMs are effective at generating ontology DRAFTS, not finished ontologies

**Confidence: HIGH** (5+ convergent sources: S3, S5, S15, S16, S18, S21)

LLMs can produce a "first version" of an ontology that captures the majority of important classes and individuals. However:
- Different runs produce different ontologies (S18)
- Inter-class properties are frequently missed or incorrect (S21)
- Fuzzy-match F1 (0.72) vastly exceeds exact-match F1 (0.10) — LLMs get the gist right but details wrong (S15)
- Well-structured prompts (Ontogenia) produce quality matching novice ontology engineers (S16)

**Implication**: Plan for LLM as draft generator + human expert refinement loop. Budget 30-50% of effort for curation.

### Claim 2: Hybrid pipelines (LLM + deterministic scaffolding + traditional NLP) outperform pure LLM approaches

**Confidence: HIGH** (5+ convergent sources: S2, S3, S13, S17, S20)

The LLMs4OL 2025 challenge confirmed that hybrid pipelines integrating commercial LLMs with domain-tuned embeddings achieved the strongest results (S2). MILA achieved F1 0.83-0.95 by invoking LLMs only for uncertain mappings, reducing queries by 90%+ (S20). GLiNER provides NER competitive with ChatGPT at a fraction of the cost (S17). Strwythura combines DSPy + spaCy + GLiNER + RDFlib (S13).

**Implication**: Do not use LLMs for everything. Use lightweight models (GLiNER) for entity extraction, LLMs for relationship inference and disambiguation, deterministic tools for validation.

### Claim 3: The Extract-Schema-Canonicalize pattern is the emerging standard for corpus-first ontology learning

**Confidence: HIGH** (4 convergent sources: S4, S8, S10, S14)

Multiple independent groups converged on a three-phase pattern:
1. **Extract** entities and relations from text (open or guided)
2. **Define/Induce** schema from extracted data (bottom-up schema induction)
3. **Canonicalize** entities and relations (normalize, deduplicate, resolve)

EDC (S4) formalized this at EMNLP 2024. KGGen (S8) implements extract + cluster-canonicalize. AutoSchemaKG (S10) demonstrates dynamic schema induction at scale. GraphRAG (S14) uses extract + community hierarchy.

**Implication**: Adopt this three-phase pattern. It naturally separates LLM-dependent steps from deterministic post-processing.

### Claim 4: Entity resolution / canonicalization is the hardest unsolved step

**Confidence: HIGH** (4+ sources: S4, S8, S9, S11, S19)

Raw LLM extraction produces duplicate entities, inconsistent naming, and conflicting relations. KGGen addresses this with iterative LM-based clustering (S8). KARMA uses multi-agent debate for conflict resolution (S9). Neo4j Graph Builder includes entity resolver (S11). The EDC framework adds trained canonicalization (S4).

**Contrary evidence**: AutoSchemaKG claims 92% semantic alignment without manual intervention (S10), but this was on web-scale data where statistical patterns help.

**Implication**: Budget significant effort for entity resolution. For domain-specific corpus (Scaling Up), this will require domain expert involvement.

### Claim 5: Schema-guided extraction significantly outperforms free-form extraction

**Confidence: MEDIUM** (3 sources: S5, S12, S24)

SPIRES (S5) demonstrates that knowledge schemas constrain extraction and improve grounding. LlamaIndex (S12) shows schema-guided mode produces more consistent results than free-form. Fine-tuned models with few-shot examples outperform zero-shot (S24).

**Contrary evidence**: EDC (S4) and AutoSchemaKG (S10) achieve good results without predefined schemas. The best approach may be iterative: start free-form, induce schema, then use schema to guide subsequent passes.

**Implication**: Start with a lightweight seed schema (core Scaling Up concepts), extract, refine schema from results, re-extract with refined schema.

### Claim 6: Competency questions are an effective specification mechanism for LLM-driven ontology construction

**Confidence: MEDIUM** (3 sources: S3, S16, S18)

CQbyCQ (S16) demonstrated that translating competency questions to OWL produces engineer-quality ontologies. The systematic review (S3) identifies CQ generation as a key LLM-assisted task. Keet (S18) acknowledges this as one of the more promising LLM applications.

**Implication**: Formulate 20-30 competency questions about the Scaling Up domain with Eduardo before extraction. These become both specification and evaluation criteria.

### Claim 7: Multi-agent architectures improve extraction quality through cross-verification

**Confidence: MEDIUM** (2 sources: S9, S11)

KARMA (S9) uses 9 agents with cross-verification, achieving 83.1% correctness. The conflict resolution agent reduces contradictory edges by 18.6%. Neo4j Graph Builder (S11) uses separate extraction and resolution stages.

**Contrary evidence**: Single-pipeline approaches (EDC, KGGen) also achieve good results. Multi-agent adds complexity and cost.

**Implication**: Multi-agent is justified for large corpus or high-accuracy requirements. For our initial extraction, a simpler pipeline with manual review may be more pragmatic.

---

## Patterns Identified

### Pattern A: The Iterative Refinement Loop

Nearly all successful pipelines use iterative refinement:
1. Extract (noisy, broad)
2. Validate (automated checks + human review)
3. Refine (re-extract with better schema/prompts)
4. Converge (diminishing returns signal completion)

This matches the NeOn methodology (S3) and is implemented in Strwythura (S13) and OntoGPT (S5).

### Pattern B: Cost-Effective Extraction Tiers

Three tiers of extraction tools, each with different cost/quality tradeoffs:

| Tier | Tool Examples | Cost | Quality | Best For |
|------|-------------|------|---------|----------|
| Lightweight NLP | GLiNER, spaCy, REBEL | Very low | Good for NER | Entity extraction, high-volume |
| LLM prompting | GPT-4, Claude, KGGen | Medium | Good for relations | Relationship inference, taxonomy |
| Fine-tuned models | Mistral-7B fine-tuned | Low (after training) | Highest for domain | Production extraction at scale |

### Pattern C: Representation Format Spectrum

| Format | Complexity | When to Use |
|--------|-----------|-------------|
| JSON/property graph | Low | Prototyping, initial extraction |
| SKOS | Medium | Taxonomies, vocabularies |
| OWL Lite / RDF | High | Formal ontologies with reasoning |
| Full OWL DL | Very High | Complex axioms, automated reasoning |

For our use case (domain knowledge graph for agent), SKOS + property graph is likely the sweet spot. Full OWL is overkill unless we need automated reasoning.

### Pattern D: Human Effort Distribution

Based on evidence across sources, estimated effort distribution for LLM-assisted ontology construction:

- **Schema design / CQ formulation**: 10-15% (human + LLM)
- **Automated extraction**: 5-10% (LLM pipeline)
- **Entity resolution / canonicalization**: 20-25% (LLM + human review)
- **Relationship validation**: 25-30% (human expert, the hardest part)
- **Iteration and refinement**: 15-20% (mixed)
- **Evaluation and testing**: 10-15% (automated + human)

Total human effort reduction vs. manual: estimated 40-60% (conservative estimate from S3, S20).

---

## Gaps and Open Questions

### Gap 1: Small-Corpus Effectiveness
Most benchmarks use large corpora (thousands of documents). Our Scaling Up corpus is likely 10-50 documents (books, transcripts, notes). Effectiveness of these methods on small, focused corpora is underexplored.

### Gap 2: Process/Methodology Ontology Extraction
Most work focuses on factual knowledge (entities, properties). Scaling Up is a business methodology with processes, frameworks, decision trees, and heuristics. Extracting procedural/prescriptive knowledge is less studied than declarative knowledge. AutoSchemaKG (S10) models events alongside entities, which is a step in this direction.

### Gap 3: Domain Expert Collaboration Tooling
While HITL is universally acknowledged as necessary, tooling for efficient domain expert review is underdeveloped. Most tools present raw triples for review, which requires technical literacy.

### Gap 4: Evaluation Without Gold Standard
We don't have a pre-existing Scaling Up ontology to evaluate against. Evaluation will rely on competency questions (can the KG answer domain questions?) and expert review.

---

## Contrary Evidence Summary

| Claim | Contrary Evidence | Assessment |
|-------|------------------|------------|
| LLMs generate drafts only | AutoSchemaKG claims 92% alignment without human input | Scale matters — web-scale data has statistical regularities that small corpora lack |
| Schema-guided > free-form | EDC/AutoSchemaKG work schema-free | Iterative approach resolves this: start free, induce schema, re-extract guided |
| Multi-agent is better | Simpler pipelines (KGGen) also work well | Complexity justified only for large corpus or high-accuracy needs |
| Hybrid > pure LLM | Some benchmarks show GPT-4 competitive alone | For cost-sensitive production, hybrid is more pragmatic |

---

*Synthesis based on 24 sources, 7 triangulated claims, 4 patterns, 4 gaps identified*
