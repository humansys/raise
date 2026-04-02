# Epic E1135: ScaleUp Agent — Knowledge Infrastructure + Ontology Pipeline

> **Status:** IN PROGRESS
> **Jira:** LIFE-90
> **Created:** 2026-03-18
> **Updated:** 2026-03-19 (S3.7/S3.8 scope expansion — knowledge infrastructure)

## Objective

Construir la **infraestructura de conocimiento** que permite al agente personal (rai-agent) comprender dominios de forma confiable — comenzando con la metodología Scaling Up como primer dominio. El pipeline extrae ontologías de corpus, las valida con gates deterministas, y las integra al knowledge graph del agente.

**Value (ScaleUp):** El empresario deja de recibir respuestas genéricas del libro. El agente traversa la ontología, conecta conceptos con el contexto de la empresa, y dice "dado tu score en People=2, enfócate en Core Values antes de Topgrading".

**Value (Knowledge Infrastructure):** El agente puede ingestar CUALQUIER dominio (metodologías de negocio, sistemas de productividad personal, marcos de gestión de vida) con el mismo pipeline determinista. La extracción de ontologías es infraestructura cognitiva del agente, no una feature de ScaleUp. Research (56 sources, 2026-03-19) confirma: structured knowledge mejora reliability 26-49% vs. unstructured memory.

## Stories (8 estimadas)

| ID | Story | Size | Status | Descripción |
|----|-------|:----:|:------:|-------------|
| S3.1 | Schema validation | S | ✅ Done | Validar schema de Eduardo con competency questions + coverage check contra corpus |
| S3.2 | Extraction pipeline | M | ✅ Done | Pipeline automatizado: corpus → nodos YAML candidatos usando LLM + Pydantic schema constraints |
| S3.3 | HITL curation skill | S | ✅ Done | Skill conversacional para que Eduardo valide nodos extraídos (agent proposes → expert validates) |
| S3.4 | Graph integration | M | ✅ Done | Builder que mapea nodos YAML ScaleUp → GraphNode/GraphEdge de RaiSE. Compatible con `rai graph` |
| S3.5 | Retrieval engine | S | ✅ Done | Retrieval determinístico: dado (decisión, etapa, contexto empresa), traversar grafo → nodos relevantes |
| S3.9 | Knowledge pipeline skills | M | ✅ Done | Interactive skills (discover/extract/validate/diff/run) for HITL knowledge pipeline operation |
| S3.6 | End-to-end proof | S | ✅ Done | `rai knowledge query` CLI with pluggable domain retrieval. Tested with Eduardo's real questions. Spawned RAISE-650 (Domain Cartridges) |
| S3.7 | Knowledge CLI gates | S | ✅ Done | CLI genérico `rai-agent knowledge` con gates poka-yoke (validate, reconcile, coverage, chunk, graph). GateResult model + exit codes. 0 deps nuevas — Pydantic + NetworkX |
| S3.8 | Full-cycle from zero | M | ✅ Done | Schema discovery + extraction usando Claude Agent SDK + validation + diff. invoke_structured() wrapper, sanitización, discovery live (11 tipos) |

**Total:** 8 stories

## Scope

**In scope (MUST):**
- Validación del schema ontológico de Eduardo (competency questions + coverage check)
- Pipeline de extracción automatizada: corpus → nodos ontológicos YAML (schema de Eduardo)
- Curación HITL conversacional: agent proposes → Eduardo validates
- Knowledge graph poblado: 68 metodologías + 34 worksheets como nodos YAML
- Integración con `rai graph build/query/context` — nodos ScaleUp son ciudadanos del grafo RaiSE
- Retrieval determinístico simbólico (graph traversal, no vector similarity)
- **CLI gates genéricos** (`rai-agent knowledge`) como poka-yoke deterministas — interfaz domain-agnostic con GateResult model, exit codes, y JSON output
- **Full-cycle extraction from zero** — validar que el pipeline descubre estructura sin schema previo

**In scope (SHOULD):**
- Relaciones cross-decisión descubiertas automáticamente
- Source pointers (chapter + line) en cada nodo para trazabilidad
- Mecanismo de re-extracción cuando el corpus cambie
- **GateConfig inyectable** — el schema (OntologyNode), thresholds, y CQs son configuración, no código hardcodeado

**Out of scope:**
- Coaching logic / prompts de facilitación → E8 de Eduardo
- Conexión con CRM/ERP del empresario → epic futuro
- Plugin system / registry de ontologías → epic futuro (S3.7/S3.8 capturan la interfaz genérica, no el plugin system)
- Interfaz visual del grafo → no necesaria para MVP
- Embeddings / vector RAG → retrieval es simbólico
- Modificación de skills existentes de Eduardo (19 slash commands)
- Multi-domain graph (GTD, life areas, etc.) → epic futuro (S3.7 diseña la interfaz que lo habilita)
- Temporal validity / provenance en GraphEdge → epic futuro (research R1 recomienda, pero fuera de E3)
- SHACL / LinkML / RDF — research confirma Pydantic + NetworkX suficiente para property graphs

## Done Criteria

**Per story:**
- [ ] Tests pasando (TDD)
- [ ] Type checks pass (pyright strict)
- [ ] Quality checks pass (ruff, pyright)
- [ ] Commit por tarea completada

**Epic complete:**
- [ ] Schema ontológico validado con competency questions (≥20 preguntas cubiertas)
- [ ] ≥68 metodologías + 34 worksheets extraídos como nodos YAML
- [ ] Eduardo ha curado al menos 1 decisión completa (People o Strategy) vía conversación
- [ ] `rai graph query "scaling up"` retorna nodos relevantes
- [ ] `rai graph context` funciona con nodos ScaleUp
- [ ] Un empresario recibe guía contextualizada en prueba end-to-end
- [ ] Epic retrospective completa

## Dependencies

```
S3.1 (schema validation)
  ↓
S3.2 (extraction pipeline) ──► S3.3 (HITL curation)
  ↓                                    ↓
S3.4 (graph integration) ◄────────────┘
  ↓
S3.7 (CLI gates) ──► S3.8 (full-cycle from zero)
  ↓                          ↓
S3.5 (retrieval engine) ◄──┘
  ↓
S3.6 (end-to-end proof)
```

**Externas:**
- Corpus: `scaling_up_llamaparse.md` + `metodologias_parsed/` (ya disponible en scaleupagent repo)
- Schema: `.scaleup/knowledge/ontology/` de Eduardo (S6.1 completada)
- Eduardo Luna: ~8h de curación distribuidas en 14-21 sesiones de 20-30min
- `raise-commons`: GraphNode, GraphEdge, GraphBuilder interfaces

## Architecture

| Decisión | ADR | Resumen |
|----------|-----|---------|
| Ontology format | Decided | YAML file-based (Pydantic schema) mapeado a GraphNode/GraphEdge de RaiSE |
| Extraction approach | Decided | Hybrid pipeline (LLM + Pydantic validation), no GraphRAG (overkill para corpus size) |
| Retrieval method | Pending | Simbólico (graph traversal) — consistente con neuro-symbolic memory de RaiSE |
| Knowledge infra | Decided (R1) | Extender raise-core, no adoptar Letta/Mem0/Graphiti — resuelven problema diferente (chat→memory vs. structured artifacts) |
| Validation tooling | Decided (R2) | Pydantic v2 + NetworkX + custom assertions. 0 deps nuevas. SHACL/LinkML descartados para E3 |
| CLI namespace | Decided | `rai-agent knowledge` — genérico, domain-agnostic, ScaleUp es primer dominio |
| Gate protocol | Decided (R2) | GateResult model (passed, metrics, errors, warnings) + exit codes (0=pass, 1=fail) + --json flag |

> Problem Brief: `work/problem-briefs/scaleup-ontology-pipeline-2026-03-18.md`
> Research: `work/research/` (5 axes, 128 sources)
>   - agentic-kg-construction (28 sources) — pipeline architectures
>   - ontology-learning-from-text (24 sources) — extraction SOTA
>   - hitl-ontology-curation (20 sources) — expert curation workflows
>   - personal-kg-agents (28 sources) — knowledge infra for personal agents
>   - kg-validation-tooling (28 sources) — deterministic validation tools

## Risks

| Riesgo | L/I | Mitigación |
|--------|:---:|------------|
| Schema de Eduardo necesita cambios significativos post-validación | M/M | S3.1 primero, antes de construir pipeline encima |
| LLM extraction quality insuficiente (<60% accuracy) | M/H | Research dice hybrid > pure LLM. Multi-pass con validación Pydantic |
| Eduardo no tiene tiempo para curación (~8h estimadas) | L/M | Sessions cortas (20-30min), max 20 decisiones/sesión, priorizar 1 decisión como proof |
| Mapping YAML ScaleUp → GraphNode pierde semántica | M/M | Diseñar mapping en S3.4 con tests que verifiquen roundtrip |
| Corpus LlamaParse tiene errores de parsing | L/M | S3.1 incluye coverage check que detecta gaps |

## Parking Lot

- Pluggable ontology engine / domain registry → epic futuro (S3.7 captura interfaz genérica)
- Multi-domain graph (GTD + life areas + ScaleUp como subgraphs conectados) → epic futuro (R1 diseña schema)
- Temporal validity (`t_valid`/`t_invalid`) en GraphEdge → epic futuro (R1 recomienda como highest-impact mechanism)
- Provenance + confidence scoring en edges → epic futuro (R1 recomienda)
- Contradiction detection on write → epic futuro (R1 recomienda)
- Cross-domain query ("qué en mi negocio afecta mi salud?") → epic futuro
- LinkML para auto-schema-discovery → evaluar en S3.8 si aplica
- Conexión con CRM/ERP del empresario → epic futuro
- Interfaz visual del grafo → no necesaria para MVP
- Re-extracción automática cuando corpus cambie → post E3
- Multi-language support (EN/ES ya está en schema, pero no es requisito de E3)

---

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-03-18

### Story Sequence

| Orden | Story | Size | Deps | Milestone | Rationale |
|:-----:|-------|:----:|------|-----------|-----------|
| 1 | S3.1 Schema validation | S | Ninguna | M1 | Risk-first: si el schema está mal, todo downstream falla |
| 2 | S3.4 Graph integration | M | S3.1 | M1 | Walking skeleton: probar mapping YAML→GraphNode con ~10 nodos existentes de Eduardo |
| 3 | S3.2 Extraction pipeline | M | S3.1 | M2 | Core value: con schema validado y mapping probado, extraer con confianza |
| 4 | S3.3 HITL curation skill | S | S3.2 | M2 | Dependency-driven: necesita nodos extraídos para curar. Eduardo valida 1 decisión |
| 5 | S3.7 CLI gates for extraction | S | S3.1-S3.4 | M2b | Poka-yoke: wrappers CLI genéricos sobre funciones existentes (validate, reconcile, coverage, chunk, graph) |
| 6 | S3.8 Full-cycle from zero | M | S3.7 | M2b | Epistemológico: schema discovery + extraction + validation sin input previo. Diff vs Eduardo |
| 7 | S3.5 Retrieval engine | S | S3.8 | M3 | Dependency-driven: necesita nodos extraídos y validados en el grafo |
| 8 | S3.6 End-to-end proof | S | S3.5 | M4 | Capstone: empresario pregunta → retrieval → guía contextualizada |

### Milestones

| Milestone | Stories | Éxito |
|-----------|---------|-------|
| **M1: Schema + Walking Skeleton** | S3.1, S3.4 | Schema validado con ≥20 competency questions. ~10 nodos de Eduardo visibles en `rai graph query`. Mapping YAML↔GraphNode con roundtrip tests |
| **M2: Extraction + Curation** | +S3.2, S3.3 | ≥68 nodos extraídos del corpus. Eduardo ha curado 1 decisión completa vía conversación. Nodos curados serializados a YAML |
| **M2b: CLI Gates + Full Cycle** | +S3.7, S3.8 | CLI poka-yoke gates funcionales. Full-cycle from zero produce ontología comparable al schema de Eduardo. Diff report como evidencia epistemológica |
| **M3: E2E Integration** (PAT-E-539) | +S3.5 | Retrieval contextual funciona: dado (decisión, stage), retorna nodos correctos. Contratos entre stories verificados con infra real |
| **M4: Epic Complete** | +S3.6 | Un empresario pregunta y recibe guía contextualizada. Done criteria completos. Listo para retrospective |

### Sequencing Rationale

**Key insight:** S3.4 (graph integration) se adelanta antes de S3.2 (extraction) porque los ~10 nodos que Eduardo ya creó en su E6 S6.1 permiten probar el mapping sin esperar extracción completa. Esto da walking skeleton temprano y reduce riesgo de descubrir problemas de mapping tarde.

```
Tiempo →

S3.1 ──► S3.4 ──► S3.2 ──► S3.3 ──► S3.7 ──► S3.8 ──► S3.5 ──► S3.6
 │         │        │        │        │        │        │        │
 M1 ───────┘        M2 ──────┘        M2b ────┘        M3       M4
```

**No hay parallel streams:** trabajo individual, secuencia lineal. Si hubiera dos personas, S3.2 y S3.4 podrían correr en paralelo (distintas code surfaces).

### Progress Tracking

| Story | Size | Status | Actual | Notas |
|-------|:----:|:------:|:------:|-------|
| S3.1 Schema validation | S | ✅ Done | 40min | 34 tests, 23 CQs, 3 checks. Schema structurally valid, needs more nodes |
| S3.4 Graph integration | M | ✅ Done | 60min | 6 subclasses, builder, 57 tests. 9 nodos reales mapeados. M1 complete |
| S3.2 Extraction pipeline | M | ✅ Done | ~90min | instructor + Pydantic structured outputs, 56 tests, reconciler |
| S3.3 HITL curation skill | S | ✅ Done | ~75min | 52 tests, session engine, formatter, /rai-scaleup-curate skill |
| S3.7 CLI gates for extraction | S | ✅ Done | — | Poka-yoke deterministas + interfaz genérica (merged to main) |
| S3.8 Full-cycle from zero | M | ✅ Done | ~90min | invoke_structured, discovery live (11 types), sanitization. Pipeline skills needed. |
| S3.5 Retrieval engine | S | ✅ Done | ~80min | SA + composite scoring, ScaleUp adapter, 58 tests. PAT-E-001 |
| S3.9 Knowledge pipeline skills | M | ✅ Done | ~240min | 5 skills, 447 nodes extracted, LLM resilience patterns |
| S3.6 End-to-end proof | S | ✅ Done | ~50min | CLI query, pluggable retrieval, tested with real ScaleUp questions. Spawned RAISE-650 |

### Sequencing Risks

| Riesgo | L/I | Mitigación |
|--------|:---:|------------|
| Schema validation (S3.1) revela que hay que rediseñar node types | M/M | Scope S3.1 para producir schema corregido, no solo reportar problemas |
| Graph integration (S3.4) requiere cambios en raise-commons | M/H | Preferir metadata-based approach sobre new node types para evitar tocar raise-commons |
| Eduardo no disponible para curación durante M2 | L/M | S3.3 diseñado para async: extraer todo, curar cuando Eduardo tenga tiempo |
