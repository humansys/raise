# Research: Ontology Learning from Text with LLMs

> Epic E3 — ScaleUp Agent
> Conducted: 2026-03-18
> Researcher: Rai (Claude Opus 4.6)

---

## Question

What validated pipelines exist for extracting domain ontologies from unstructured corpus (transcripts, books, notes) using LLMs combined with deterministic scaffolding?

## Files

| File | Description |
|------|-------------|
| [sources/evidence-catalog.md](sources/evidence-catalog.md) | 24 sources with type, evidence level, key findings |
| [synthesis.md](synthesis.md) | 7 triangulated claims, 4 patterns, 4 gaps |
| [recommendation.md](recommendation.md) | Actionable pipeline recommendation for E3 |

## Key Findings (TL;DR)

1. **LLMs generate draft ontologies, not finished ones.** Budget 40-60% effort for human curation.
2. **Hybrid pipelines win.** LLM + lightweight NLP + deterministic validation outperforms pure LLM.
3. **Extract-Schema-Canonicalize is the emerging standard** — extract open, induce schema, normalize entities.
4. **Entity resolution is the hardest step** — requires LLM clustering + domain expert review.
5. **Start with competency questions** — they serve as both specification and evaluation criteria.
6. **Use existing tools** — KGGen, LlamaIndex, Neo4j Graph Builder, OntoGPT are all validated.
7. **SKOS + property graph** is the right representation level for our use case (not full OWL).

## Reproducibility

### Search Strategy
- 18 web searches across: academic (arXiv, ACL Anthology, PubMed), production (GitHub, Neo4j, LlamaIndex), community (Medium, blogs)
- Keywords: "ontology learning LLM", "knowledge graph construction", "concept extraction", "taxonomy induction", "entity resolution", "deterministic validation"
- Date range focus: 2024-2025

### Evidence Standards
- 24 sources cataloged: 16 primary, 6 secondary, 2 tertiary
- 7 Very High, 11 High, 6 Medium evidence level
- All major claims triangulated with 3+ independent sources
- Contrary evidence documented explicitly

### Limitations
- Most benchmarks use large corpora; our small-corpus scenario is underexplored
- Process/methodology ontology extraction is less studied than factual knowledge extraction
- No gold-standard Scaling Up ontology exists for evaluation
- Search limited to English-language sources

---

*Research protocol: RaiSE epistemological standards (triangulation, evidence levels, contrary evidence)*
