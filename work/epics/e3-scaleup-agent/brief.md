---
epic_id: "E3"
title: "ScaleUp Agent — Ontology Pipeline + Knowledge Graph"
status: "in-progress"
created: "2026-03-18"
---

# Epic Brief: ScaleUp Agent — Ontology Pipeline + Knowledge Graph

## Hypothesis
For empresarios who take Scaling Up courses but can't apply the methodology
to their specific company context,
the ScaleUp Ontology Pipeline is a knowledge engineering system
that extracts, validates, and curates a structured ontology from the methodology corpus,
producing a knowledge graph integrated with RaiSE CLI
that enables the ScaleUp agent to give contextual, specific guidance.
Unlike generic RAG over book text, our solution
preserves concept relationships and enables deterministic, graph-based retrieval.

## Success Metrics
- **Leading:** Un empresario pregunta al agente y recibe guía específica a su contexto (4 semanas)
- **Lagging:** ≥68 metodologías + 34 worksheets como nodos queryables via `rai graph`

## Appetite
M — 6 stories (S3.1–S3.6)

## Scope Boundaries
### In (MUST)
- Schema validation con competency questions
- Extraction pipeline (LLM + Pydantic constraints)
- HITL curation conversacional (Eduardo valida)
- Graph integration con `rai graph build/query/context`
- Retrieval determinístico simbólico

### In (SHOULD)
- Cross-decision relationships auto-descubiertas
- Source pointers para trazabilidad
- Re-extracción cuando corpus cambie

### No-Gos
- Coaching logic (E8 de Eduardo)
- CRM/ERP integration (epic futuro)
- Pluggable ontology engine generalizado (epic futuro — solo capturamos patrones)
- Vector RAG / embeddings

### Rabbit Holes
- Over-engineering el schema antes de tener nodos reales
- Optimizar extraction accuracy más allá de "good enough for curation"
- Generalizar a pluggable ontologies antes de que ScaleUp funcione end-to-end
- Construir UI visual del grafo cuando conversation-based es suficiente
