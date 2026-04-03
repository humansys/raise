---
epic_id: "E3"
grounded_in: "Gemba of scaleupagent repo, raise-commons graph models, research (128 sources across 5 axes)"
updated: "2026-03-19"
---

# Epic Design: Knowledge Infrastructure + Ontology Pipeline

## Affected Surface (Gemba)

| Module/File | Current State | Changes |
|-------------|---------------|---------|
| `scaleupagent/.scaleup/knowledge/ontology/` | Schema designed (6 node types, 6 rel types), ~10 example nodes | Validated schema, populated with ≥68+34 nodes |
| `scaleupagent/scaling_up_llamaparse.md` | Raw LlamaParse output (9,380 lines) | Input to extraction pipeline (read-only) |
| `scaleupagent/metodologias_parsed/*.md` | 4 workbooks (12,044 lines) | Input to extraction pipeline (read-only) |
| `raise-commons/src/raise_core/graph/models.py` | 18 node types, 11 edge types | New node types for ScaleUp ontology (or metadata-based) |
| `raise-commons/src/raise_core/graph/engine.py` | GraphEngine with NetworkX backend | Builder extension for ScaleUp YAML ingest |

## Target Components

| Component | Responsibility | Key Interface |
|-----------|---------------|---------------|
| Schema Validator | Validate Eduardo's schema with competency questions + corpus coverage | `validate_schema(schema, corpus, questions) → ValidationReport` |
| Extraction Pipeline | Extract ontology nodes from corpus using LLM + Pydantic | `extract_nodes(corpus, schema) → list[OntologyNode]` |
| Curation Skill | Conversational HITL for Eduardo to validate/correct extracted nodes | `/scaleup-curate` slash command |
| Graph Builder | Map ScaleUp YAML nodes → RaiSE GraphNode/GraphEdge | `ScaleUpGraphBuilder.build(knowledge_dir) → list[GraphNode]` |
| Retrieval Engine | Deterministic graph traversal for contextual queries | `retrieve(decision, stage, context) → list[GraphNode]` |

## Key Contracts

### OntologyNode (Pydantic — mirrors Eduardo's YAML schema)

```python
class OntologyNode(BaseModel):
    id: str                          # e.g., "tool-opsp"
    type: Literal["decision", "concept", "tool", "worksheet", "stage", "metric"]
    name: str                        # English name
    name_es: str                     # Spanish name
    decision: Literal["people", "strategy", "execution", "cash", "cross"]
    summary: str                     # 1-3 sentence description
    relationships: list[Relationship]
    source: SourcePointer | None = None
    tags: list[str] = []
    metadata: dict[str, Any] = {}

class Relationship(BaseModel):
    type: Literal["belongs-to", "requires", "feeds-into", "measured-by", "prerequisite-of", "implements"]
    target: str                      # Target node ID

class SourcePointer(BaseModel):
    book_chapter: str | None = None
    book_line: int | None = None
    workbook: str | None = None
```

### Mapping OntologyNode → GraphNode (RaiSE)

```python
# OntologyNode.id      → GraphNode.id (prefixed: "su-{id}")
# OntologyNode.type    → GraphNode.type (new types or "ontology-{type}")
# OntologyNode.summary → GraphNode.content
# OntologyNode YAML    → GraphNode.source_file
# OntologyNode.metadata + name/name_es/decision/tags → GraphNode.metadata

# Relationship.type    → GraphEdge.type (reuse existing: implements, belongs_to, depends_on)
# Relationship.target  → GraphEdge.target (prefixed: "su-{target}")
```

### Extraction Pipeline Flow

```
corpus (markdown files)
  ↓ chunking by chapter/section
chunks[]
  ↓ LLM extraction (schema-constrained, Pydantic output)
raw_nodes[]
  ↓ deduplication + entity resolution
candidate_nodes[]
  ↓ validation (Pydantic schema + relationship consistency)
validated_nodes[]
  ↓ HITL curation (Eduardo validates via conversation)
curated_nodes[]
  ↓ YAML serialization to .scaleup/knowledge/
  ↓ GraphBuilder ingest to rai graph
knowledge_graph
```

## Knowledge Infrastructure (S3.7/S3.8 — added 2026-03-19)

### Vision

La extracción de ontología no es una feature de ScaleUp — es **infraestructura cognitiva del agente**. Para que Rai sea confiable en cualquier dominio, necesita:

1. Leer el corpus del dominio (libro, documentación, políticas)
2. Extraer conocimiento estructurado (entidades, relaciones, jerarquías)
3. Validar determinísticamente (CLI gates como poka-yoke)
4. Usar ese conocimiento para respuestas grounded

### Research Findings (R1 + R2, 56 sources)

**R1 — Personal KGs for Agents:**
- Three-tier memory (working/episodic/archival) es universal en agent frameworks
- Structured knowledge → 26-49% accuracy improvement vs. unstructured
- Multi-domain representation es un **gap abierto** — ningún framework lo aborda
- Recomendación: extender raise-core, no adoptar Letta/Mem0/Graphiti
- Highest-impact additions: temporal validity en edges, provenance/confidence, session context bundles

**R2 — KG Validation Tooling:**
- Pydantic + NetworkX = equivalente a SHACL para property graphs (0 deps nuevas)
- Cada major KG tool (OntoGPT, LlamaIndex, Neo4j Builder) usa el mismo stack
- "Graph testing" = pytest assertions sobre propiedades del grafo (no hay framework dedicado)
- GateResult model genérico + GateConfig inyectable = reutilizable para cualquier dominio

### CLI Gate Architecture

```
rai-agent knowledge <command> [options]

Commands:
  validate   — Schema validation of YAML nodes (Pydantic)
  reconcile  — Cross-reference consistency (NetworkX)
  coverage   — Competency question coverage
  chunk      — Corpus splitting into chapters
  graph      — Build graph + stats report
```

Gate protocol:
```python
class GateResult(BaseModel):
    gate: str                    # "validate", "reconcile", etc.
    passed: bool                 # True if gate passes
    metrics: dict[str, Any]      # Gate-specific metrics
    errors: list[str]            # Blocking errors
    warnings: list[str]          # Non-blocking warnings

# Exit code: 0 if passed, 1 if not
# Output: human-readable default, --json for programmatic
```

### Extraction Flow with Gates (S3.8)

```
Rai (inferencia) → produce YAML candidato
CLI validate     → valida contra schema     ← poka-yoke 1
CLI reconcile    → reconcilia referencias   ← poka-yoke 2
CLI coverage     → checa coverage CQs       ← poka-yoke 3
CLI graph        → construye grafo          ← poka-yoke 4
Eduardo (humano) → curación final           ← poka-yoke 5
```

### Multi-Domain Schema (future — from R1)

```
Upper Ontology (shared): Person, Goal, Activity, Metric, Constraint
Domain Subgraphs:        scaleup.*, gtd.*, health.*, life.*
Cross-Domain Edges:      scaleup.lever --impacts--> health.routine
```

Domain-namespaced node types compatible con raise-core's open type system.

## Migration Path

No migration needed — greenfield knowledge graph. Eduardo's existing ~10 example nodes will be validated against the schema in S3.1 and either kept or regenerated by the pipeline in S3.2.

The ScaleUp graph builder will be additive to `rai graph build` — existing RaiSE nodes (patterns, skills, stories) are unaffected.

The CLI gate infrastructure (S3.7) is domain-agnostic — ScaleUp-specific logic is injected via GateConfig. Future domains reuse the same gates with different schemas.
