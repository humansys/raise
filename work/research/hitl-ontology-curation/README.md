# Research: HITL Ontology Curation

> Where is the domain expert irreplaceable in the ontology construction pipeline, and what human-in-the-loop patterns maximize quality while minimizing cognitive load?

---

## Context

- **Epic**: E3 — ScaleUp Agent
- **Decision**: How to design Eduardo Luna's ontology curation workflow
- **Stakes**: Too much human involvement = Eduardo won't sustain it. Too little = ontology quality degrades.

## Files

| File | Purpose |
|------|---------|
| `sources/evidence-catalog.md` | 20 sources with type, evidence level, key findings, relevance |
| `synthesis.md` | 7 triangulated claims with confidence levels and contrary evidence |
| `recommendation.md` | Actionable architecture for E3 curation workflow |

## Key Findings

1. **LLMs are competent drafters, unreliable validators.** 65-90% accuracy on extraction, but only 44% recall on validation. Expert review is not optional.

2. **Expert is irreplaceable at 4 points:** structural validation, completeness review, nuance resolution, priority assignment. Everything else can be LLM-driven.

3. **Conversational interfaces work** for non-technical ontology engineering (OntoChat, participatory prompting). No ontology tools needed.

4. **The Pareto frontier exists:** approximately 20% of assertions need deep expert review. With confidence-based routing, estimated 8 hours of Eduardo's time over 2-3 months for the complete Scaling Up ontology.

5. **Session design matters:** 20-30 min max, hard items first, batch approvals last, 10-20 decisions per session.

## Methodology

- **Search strategy**: Academic (arxiv, PMC, ACM, Springer, Frontiers, SWJ), Industry (Pareto.ai, Briq), Tools (OntoGPT, WebProtege, PoolParty)
- **Sources reviewed**: 20 primary and secondary
- **Triangulation**: Major claims require 3+ independent sources
- **Depth**: Standard (15-30 sources target, 20 cataloged)
- **Date**: 2026-03-18
- **Researcher**: Rai (Claude Opus 4.6)

## Reproducibility

Search queries used:
1. `human-in-the-loop ontology construction LLM domain expert curation workflow`
2. `LLM accuracy ontology extraction vs human expert systematic evaluation 2024 2025`
3. `active learning uncertainty sampling ontology curation knowledge graph refinement`
4. `expert fatigue annotation curation optimal batch size session length cognitive load`
5. `conversational ontology building non-technical domain expert interface chatbot knowledge elicitation`
6. `Wikidata curation workflow human review knowledge graph quality control at scale`
7. `Gene Ontology SNOMED curation process human expert review biomedical ontology workflow`
8. `OntoGPT LLM ontology extraction tool accuracy evaluation SPIRES`
9. `minimum viable ontology Pareto principle knowledge graph quality vs effort tradeoff`
10. `WebProtégé collaborative ontology editing usability non-expert user study`
11. `annotation fatigue optimal session length 20 minutes review batch quality degradation research`
12. `PoolParty Ontotext enterprise ontology curation HITL workflow taxonomy management`
13. `conversational ontology building propose and validate workflow`
14. `OntoChat conversational ontology engineering user study results`
15. `DRAGON-AI ontology curation LLM automated term definition generation accuracy`
16. `knowledge graph validation human in the loop LLM integrating 2024 2025`
17. `LLM ontology hallucination errors systematic failures taxonomy extraction`
18. `from human experts to machines LLM ontology knowledge graph construction 2024`
19. `confidence-based routing AI human review when to escalate uncertain predictions`
20. `LLM-supported collaborative ontology design Frontiers 2025`
21. `simple interface domain expert knowledge validation spreadsheet form based`
22. `accelerating knowledge graph ontology engineering large language models survey 2025`

## Gaps Identified

1. No business methodology domain evidence (all biomedical/academic/music)
2. No longitudinal sustainability studies for expert engagement
3. No cost-benefit quantification of expert hours vs. quality
4. No conversational curation tool designed for truly non-technical business experts
5. Active learning for ontology curation is underexplored
