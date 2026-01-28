---
id: "TEC-SAR-001"
title: "Tech Design: SAR + raise.ctx Governance Components"
version: "1.0"
date: "2026-01-28"
status: "Draft"
related_docs:
  - "VIS-SAR-001 (solution-vision.md)"
  - "VIS-CTX-001 (solution-vision-context.md)"
  - "ROAD-GOV-001 (solution-roadmap.md)"
template: "lean-spec-v1"
---

# Tech Design: SAR + raise.ctx Governance Components

## 1. Objetivo y Solución

**Problema técnico**:
Los agentes LLM carecen de contexto sobre convenciones y patrones existentes en codebases brownfield, generando código inconsistente con la arquitectura establecida.

**Solución propuesta**:
Dos componentes complementarios: **SAR** extrae reglas y construye un grafo de relaciones (batch), **raise.ctx** entrega Minimum-Viable Context al agente (on-demand, determinista).

**Componentes involucrados**:
- **SAR (Software Architecture Reconstruction)**: Pipeline de extracción LLM-driven
- **raise.ctx**: CLI de entrega de MVC con graph traversal
- **Data Store (.raise/)**: Formato compartido entre componentes

---

## 2. Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RAISE GOVERNANCE SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────┐                                               │
│  │      CODEBASE        │                                               │
│  │   (brownfield)       │                                               │
│  └──────────┬───────────┘                                               │
│             │ input                                                      │
│             ▼                                                            │
│  ┌──────────────────────┐     ┌─────────────────────────────────────┐  │
│  │        SAR           │     │           PIPELINE                   │  │
│  │  raise sar analyze   │     │  DETECT → SCAN → DESCRIBE → GOVERN  │  │
│  │  /raise.sar.analyze  │────▶│  (LLM synthesis en Open Core)       │  │
│  └──────────┬───────────┘     └─────────────────────────────────────┘  │
│             │ genera                                                     │
│             ▼                                                            │
│  ┌──────────────────────┐                                               │
│  │    DATA STORE        │  .raise/                                      │
│  │                      │  ├── project-profile.yaml                     │
│  │   (output SAR,       │  ├── conventions.md                           │
│  │    input raise.ctx)  │  ├── rules/*.yaml                             │
│  │                      │  └── graph.yaml                               │
│  └──────────┬───────────┘                                               │
│             │ consume                                                    │
│             ▼                                                            │
│  ┌──────────────────────┐     ┌─────────────────────────────────────┐  │
│  │     raise.ctx        │     │         RETRIEVAL                    │  │
│  │  raise ctx get       │     │  Query → Filter → Traverse → Format │  │
│  │  /raise.ctx          │────▶│  (determinista, sin LLM)            │  │
│  └──────────┬───────────┘     └─────────────────────────────────────┘  │
│             │ entrega MVC                                                │
│             ▼                                                            │
│  ┌──────────────────────┐                                               │
│  │     AGENTE LLM       │  Recibe: primary_rules + context_rules        │
│  │  (Claude, GPT, etc)  │         + warnings + graph_context            │
│  └──────────────────────┘                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Componente | Responsabilidad | Tipo |
|------------|-----------------|------|
| SAR CLI | Orquestar pipeline de extracción | nuevo |
| SAR Pipeline | 4 fases: DETECT, SCAN, DESCRIBE, GOVERN | nuevo |
| Data Store | Persistencia de reglas y grafo | nuevo (filesystem) |
| raise.ctx CLI | Query parsing, retrieval, formatting | nuevo |
| Graph Engine | Traversal determinista de relaciones | nuevo |

---

## 3. Contratos de Datos

### 3.1 Rule Schema (Lean)

```yaml
# .raise/rules/{category}/{rule-id}.yaml
# Schema: rule-schema-lean.json

id: string                    # Unique, slugified (e.g., "ts-repository-suffix")
version: string               # Semver (e.g., "1.0.0")
status: enum                  # draft | active | deprecated
category: enum                # naming | architecture | security | style | reliability

confidence: number            # 0.0-1.0, basado en adoption rate
enforcement: enum             # hard | strong | moderate | advisory | none

title: string                 # Human-readable, <80 chars
intent: string                # The "why" in ONE sentence

pattern:
  type: enum                  # ast-grep | regex | structural
  query: string               # Detection pattern
  scope: string               # File glob

examples:
  positive:                   # Minimum 1
    - code: string
      source: string          # Optional: file path
  negative:                   # Minimum 1
    - code: string
      fix: string             # How to correct

provenance:
  source: enum                # sar-extracted | manual | hybrid
  tool_version: string
  timestamp: string           # ISO8601
  evidence_count: number
```

### 3.2 Graph Schema

```yaml
# .raise/graph.yaml
# Schema: graph-schema-lean.json

version: string               # Schema version
generated_date: string        # ISO8601

nodes:
  - id: string                # References rule id
    category: string
    confidence: number

edges:
  - from: string              # Source rule id
    to: string                # Target rule id
    type: enum                # requires | conflicts_with | supersedes | related_to
    reason: string            # Why this relationship exists
```

### 3.3 MVC Output Schema (raise.ctx)

```yaml
# Output de `raise ctx get`
# Schema: mvc-schema.json

query:
  task: string
  scope: string
  min_confidence: number

primary_rules:                # Directly applicable rules (full content)
  - id: string
    title: string
    intent: string
    pattern: object
    examples: object

context_rules:                # Related rules (summaries only)
  - id: string
    title: string
    relevance: string         # Why included

warnings:                     # Conflicts, deprecations, low-confidence
  - type: enum                # conflict | deprecated | low_confidence
    rule_id: string
    message: string

graph_context:                # Relevant subgraph
  nodes: [string]             # Rule IDs in context
  edges: [object]             # Relationships between context rules

metadata:
  total_rules_matched: number
  token_estimate: number
  retrieval_time_ms: number
```

### 3.4 CLI Interfaces

```bash
# SAR CLI
raise sar analyze [path]
  --output-dir     .raise/          # Default output location
  --phases         all              # detect,scan,describe,govern
  --config         .raise/sar.yaml  # Optional config

# raise.ctx CLI
raise ctx get
  --task           string           # Task description (required)
  --scope          string           # File pattern or path
  --file           string           # Specific file context
  --min-confidence 0.80             # Minimum confidence threshold
  --max-tokens     4000             # Token budget
  --format         yaml             # yaml | json | markdown
  --include-all    false            # Include low-confidence rules
```

---

## 4. Decisiones y Riesgos

### Decisiones Clave

| Decisión | Rationale |
|----------|-----------|
| **YAML para reglas** (no JSON) | Balance densidad/legibilidad; LLMs comprenden mejor YAML (research) |
| **Grafo separado** (no embebido en reglas) | Permite traversal eficiente; reglas son self-contained chunks |
| **raise.ctx siempre determinista** | Reproducibilidad crítica para debugging; mismo input = mismo output |
| **4 fases en SAR** (DETECT→SCAN→DESCRIBE→GOVERN) | Separation of concerns; permite gates entre fases |
| **Confidence basado en adoption rate** | Objetivo ("95% usa X") vs subjetivo ("es buena práctica") |
| **MVC con summaries** para context_rules | Token efficiency; full content solo para primary_rules |

### Alternativas Descartadas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Embeddings/RAG semántico para raise.ctx | Introduce no-determinismo; overkill para <500 reglas |
| Reglas en Markdown puro | No parseable para validación automática; pierde estructura |
| Un solo componente SAR+delivery | Viola single responsibility; batch vs on-demand son distintos |
| GraphQL para queries | Over-engineering para MVP; CLI args suficientes |
| SQLite para data store | Agrega dependencia; YAML files son portables y diff-friendly |

### Open Questions / Riesgos

- [ ] **Chunking strategy**: ¿Cómo manejar codebases >10K archivos? (propuesta: sampling)
- [ ] **LLM provider abstraction**: ¿Soportar múltiples providers o solo Anthropic?
- [ ] **Conflict resolution**: Cuando dos reglas aplican con guidance contradictorio
- [ ] **Schema evolution**: Cómo migrar reglas cuando schema cambia
- [ ] **Token budget distribution**: Cómo distribuir tokens entre primary vs context rules

---

<details>
<summary><h2>Flujo de Datos (Expandir)</h2></summary>

### SAR Pipeline Flow

```
Codebase Input
     │
     ▼
┌─────────────┐
│   DETECT    │  → project-profile.yaml
│  (Phase 0)  │    - type: backend/web/cli/library
└──────┬──────┘    - structure: monolith/monorepo
       │           - stack: languages, frameworks
       ▼
┌─────────────┐
│    SCAN     │  → scan-report.json (interno)
│  (Phase 1)  │    - import graph
└──────┬──────┘    - naming patterns + counts
       │           - file structure analysis
       ▼
┌─────────────┐
│  DESCRIBE   │  → conventions.md
│  (Phase 2)  │    - architecture-as-found
└──────┬──────┘    - consistency scores
       │
       ▼
┌─────────────┐
│   GOVERN    │  → rules/*.yaml + graph.yaml
│  (Phase 3)  │    - confidence-scored rules
└─────────────┘    - relationship graph
```

### raise.ctx Query Flow

```
Query (task + scope + confidence)
     │
     ▼
┌─────────────┐
│   FILTER    │  Filter rules by:
│             │  - scope match (file patterns)
└──────┬──────┘  - confidence >= threshold
       │         - status = active
       ▼
┌─────────────┐
│  TRAVERSE   │  Graph traversal:
│             │  - requires edges (dependencies)
└──────┬──────┘  - related_to edges (1 level)
       │         - detect conflicts_with, supersedes
       ▼
┌─────────────┐
│   FORMAT    │  Output MVC:
│             │  - primary_rules (full)
└─────────────┘  - context_rules (summary)
                 - warnings
                 - graph_context
```

</details>

<details>
<summary><h2>Algoritmos Clave (Expandir)</h2></summary>

### Graph Traversal Algorithm

**Input**: Set of primary rule IDs, graph, depth limit
**Output**: Extended set with related rules + warnings

```python
def traverse_for_mvc(primary_ids: Set[str], graph: Graph, depth: int = 1) -> MVCContext:
    context_ids = set()
    warnings = []

    for rule_id in primary_ids:
        # 1. Traverse 'requires' edges (mandatory dependencies)
        for edge in graph.edges_from(rule_id, type='requires'):
            context_ids.add(edge.to)

        # 2. Traverse 'related_to' edges (informational, limit depth)
        if depth > 0:
            for edge in graph.edges_from(rule_id, type='related_to'):
                context_ids.add(edge.to)

        # 3. Detect conflicts
        for edge in graph.edges_from(rule_id, type='conflicts_with'):
            if edge.to in primary_ids:
                warnings.append(ConflictWarning(rule_id, edge.to, edge.reason))

        # 4. Detect superseded rules
        for edge in graph.edges_to(rule_id, type='supersedes'):
            if edge.from in primary_ids:
                warnings.append(DeprecationWarning(edge.from, rule_id))

    # Remove primary rules from context (avoid duplication)
    context_ids -= primary_ids

    return MVCContext(
        primary_ids=primary_ids,
        context_ids=context_ids,
        warnings=warnings
    )
```

**Complejidad**: O(|primary| * avg_edges) - lineal para grafos sparse típicos

### Confidence Scoring (SAR)

```python
def calculate_confidence(pattern_matches: int, total_applicable: int) -> tuple[float, str]:
    """
    Returns (confidence_score, enforcement_level)
    Based on adoption rate in codebase.
    """
    if total_applicable == 0:
        return (0.0, 'none')

    rate = pattern_matches / total_applicable

    if rate >= 1.0:
        return (1.0, 'hard')      # 100% - unanimous
    elif rate >= 0.90:
        return (rate, 'strong')   # 90-99%
    elif rate >= 0.80:
        return (rate, 'moderate') # 80-89%
    elif rate >= 0.60:
        return (rate, 'advisory') # 60-79%
    else:
        return (rate, 'none')     # <60% - inconsistent
```

</details>

<details>
<summary><h2>Seguridad (Expandir)</h2></summary>

| Aspecto | Medida |
|---------|--------|
| **Ejecución de código** | SAR NO ejecuta código del codebase analizado; solo lee archivos |
| **Secrets en reglas** | Gate de validación: rechazar reglas que contengan patterns de secrets |
| **LLM prompt injection** | Sanitizar contenido de archivos antes de enviar a LLM |
| **File access** | raise.ctx solo lee de .raise/; no accede a codebase directamente |

</details>

<details>
<summary><h2>Estrategia de Pruebas (Expandir)</h2></summary>

| Tipo | Cobertura | Approach |
|------|-----------|----------|
| **Unit** | Schema validation, graph traversal, confidence calc | pytest con fixtures |
| **Integration** | SAR pipeline end-to-end, raise.ctx query flow | Test codebases sintéticos |
| **Contract** | Rule schema, graph schema, MVC schema | JSON Schema validation |
| **Snapshot** | Determinismo de raise.ctx | Same input → same output |

### Test Codebases

1. **minimal-ts**: 10 archivos TypeScript, patrones claros
2. **inconsistent-py**: Python con convenciones mezcladas (test confidence scoring)
3. **large-mono**: Monorepo simulado 1000+ archivos (test performance)

</details>
