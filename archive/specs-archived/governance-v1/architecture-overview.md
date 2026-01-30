---
id: "SAD-RAISE-001"
title: "Architecture Overview: RaiSE Framework"
version: "2.0"
date: "2026-01-28"
status: "Draft"
related_docs:
  - "VIS-RAISE-001 (solution-vision.md)"
  - "VIS-SAR-001 (solution-vision-sar.md)"
  - "VIS-CTX-001 (solution-vision-context.md)"
  - "TEC-SAR-001 (tech-design.md)"
template: "lean-spec-v1"
c4_levels: ["context", "container"]
---

# Architecture Overview: RaiSE Framework

## 1. System Context (C4 Level 1)

**Propósito del sistema**:
RaiSE es un framework de gobernanza para desarrollo AI-assisted. Extrae convenciones de codebases brownfield (SAR), las entrega como Minimum-Viable Context a agentes (CTX), y orquesta workflows de desarrollo (Commands), permitiendo que el código AI-generated sea consistente con la arquitectura existente.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          SYSTEM CONTEXT                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐                           ┌─────────────────┐         │
│   │ Orquestador │                           │   Agente LLM    │         │
│   │ (Developer) │                           │ (Claude, GPT)   │         │
│   └──────┬──────┘                           └────────┬────────┘         │
│          │                                           │                   │
│          │ ejecuta SAR                               │ consume MVC       │
│          ▼                                           ▼                   │
│   ┌─────────────────────────────────────────────────────────────┐       │
│   │                  RAISE GOVERNANCE SYSTEM                     │       │
│   │                                                              │       │
│   │   Extrae reglas de convenciones y entrega contexto mínimo   │       │
│   │   viable a agentes para generar código consistente          │       │
│   └─────────────────────────────────────────────────────────────┘       │
│          │                                           ▲                   │
│          │ analiza                                   │ lee reglas        │
│          ▼                                           │                   │
│   ┌─────────────┐                           ┌───────┴───────┐           │
│   │  Codebase   │                           │  LLM Provider │           │
│   │ (brownfield)│                           │  (Anthropic)  │           │
│   └─────────────┘                           └───────────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Actor/Sistema | Tipo | Interacción |
|---------------|------|-------------|
| Orquestador (Developer) | usuario | Ejecuta `raise sar analyze` para extraer reglas del codebase |
| Agente LLM | sistema consumidor | Recibe MVC via `raise ctx get` para generar código consistente |
| Codebase brownfield | dependencia (input) | Fuente de convenciones y patrones a extraer |
| LLM Provider (Anthropic) | dependencia (servicio) | Procesa prompts de SAR para síntesis de reglas |

---

## 2. Container Diagram (C4 Level 2)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            CONTAINERS                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────┐                                               │
│  │      CODEBASE        │                                               │
│  │   (brownfield)       │                                               │
│  └──────────┬───────────┘                                               │
│             │ input                                                      │
│             ▼                                                            │
│  ┌──────────────────────┐     ┌─────────────────────────────────────┐  │
│  │      SAR CLI         │     │           SAR PIPELINE              │  │
│  │   `raise sar`        │────▶│  DETECT → SCAN → DESCRIBE → GOVERN  │  │
│  │     [TypeScript]     │     │        [LLM-driven synthesis]       │  │
│  └──────────┬───────────┘     └─────────────────────────────────────┘  │
│             │ genera                                                     │
│             ▼                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        DATA STORE                                 │  │
│  │                         `.raise/`                                 │  │
│  │  ┌─────────────────┬─────────────────┬─────────────────────────┐ │  │
│  │  │ project-profile │  conventions.md │  rules/*.yaml + graph   │ │  │
│  │  │     .yaml       │                 │      .yaml              │ │  │
│  │  └─────────────────┴─────────────────┴─────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│             │ consume                                                    │
│             ▼                                                            │
│  ┌──────────────────────┐     ┌─────────────────────────────────────┐  │
│  │    raise.ctx CLI     │     │          GRAPH ENGINE               │  │
│  │   `raise ctx get`    │────▶│  Query → Filter → Traverse → Format │  │
│  │     [TypeScript]     │     │      [determinista, sin LLM]        │  │
│  └──────────┬───────────┘     └─────────────────────────────────────┘  │
│             │ entrega MVC                                                │
│             ▼                                                            │
│  ┌──────────────────────┐                                               │
│  │     AGENTE LLM       │  Recibe: primary_rules + context_rules       │
│  │  (Claude, GPT, etc)  │         + warnings + graph_context           │
│  └──────────────────────┘                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Container | Responsabilidad | Tecnología | Tipo |
|-----------|-----------------|------------|------|
| SAR CLI | Orquestar pipeline de extracción | TypeScript/Node | CLI |
| SAR Pipeline | 4 fases: DETECT, SCAN, DESCRIBE, GOVERN | LLM prompts estructurados | Pipeline |
| Data Store | Persistir reglas, grafo y convenciones | Filesystem (YAML/MD) | Storage |
| raise.ctx CLI | Query parsing, retrieval, formatting de MVC | TypeScript/Node | CLI |
| Graph Engine | Traversal determinista de relaciones entre reglas | TypeScript | Library |

---

## 2.5 Command Layer (Workflows)

Los componentes SAR y CTX se exponen a través de **comandos ejecutables** organizados en 5 categorías:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMMAND LAYER (Layer 3)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  setup/              context/           project/           feature/         │
│  ┌────────────┐      ┌────────────┐     ┌────────────┐     ┌────────────┐  │
│  │init-project│      │get         │     │create-prd  │     │create-spec │  │
│  │analyze     │      │check       │     │define-visn │     │plan        │  │
│  │gen-rules   │      │explain     │     │design-arch │     │tasks       │  │
│  │edit-rule   │      └────────────┘     │backlog     │     │implement   │  │
│  └────────────┘           │             │estimate    │     └────────────┘  │
│        │                  │             └────────────┘           │          │
│        │ SAR              │ CTX              │                   │          │
│        ▼                  ▼                  ▼                   ▼          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SPEC-KIT HARNESS                                  │   │
│  │         (katas + gates + templates + Jidoka inline)                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Categoría | Comandos | Usa Componente | Frecuencia |
|-----------|----------|----------------|------------|
| **setup/** | init-project, analyze-codebase, generate-rules, edit-rule | SAR | 1x setup |
| **context/** | get, check, explain | CTX | On-demand |
| **project/** | create-prd, define-vision, design-architecture, create-backlog, estimate-effort | - | 1x proyecto |
| **feature/** | create-spec, plan-implementation, generate-tasks, implement | CTX (consume) | Nx feature |
| **tools/** | export-issues | - | Utilidad |

**Tecnología**: Cada comando se implementa con el patrón spec-kit (kata + gate + template).

---

## 3. Decisiones Arquitectónicas Clave

| ID | Decisión | Rationale | ADR |
|----|----------|-----------|-----|
| D1 | **YAML para reglas** (no JSON) | Balance densidad/legibilidad; LLMs comprenden mejor YAML según research | [ADR-003](./adrs/adr-003-yaml-rule-format.md) |
| D2 | **Grafo separado** (no embebido en reglas) | Permite traversal eficiente; reglas son self-contained chunks | [ADR-004](./adrs/adr-004-separate-graph.md) |
| D3 | **raise.ctx siempre determinista** | Reproducibilidad crítica para debugging; mismo input = mismo output | [ADR-002](./adrs/adr-002-deterministic-context-delivery.md) |
| D4 | **4 fases en SAR** (DETECT→SCAN→DESCRIBE→GOVERN) | Separation of concerns; permite gates entre fases | [ADR-001](./adrs/adr-001-sar-pipeline-phases.md) |
| D5 | **Confidence basado en adoption rate** | Objetivo ("95% usa X") vs subjetivo ("es buena práctica") | [ADR-005](./adrs/adr-005-confidence-adoption-rate.md) |
| D6 | **MVC con summaries** para context_rules | Token efficiency; full content solo para primary_rules | [ADR-006](./adrs/adr-006-mvc-summaries.md) |

> **Nota**: Detalle completo de cada decisión en su ADR correspondiente.

### Alternativas Descartadas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Embeddings/RAG semántico para raise.ctx | Introduce no-determinismo; overkill para <500 reglas |
| Reglas en Markdown puro | No parseable para validación automática |
| Un solo componente SAR+delivery | Viola single responsibility; batch vs on-demand son distintos |
| SQLite para data store | Agrega dependencia; YAML files son portables y diff-friendly |

---

## 4. Quality Attributes (NFRs)

| Atributo | Requisito | Cómo se Logra |
|----------|-----------|---------------|
| **Determinismo** | raise.ctx: mismo input = mismo output, 100% | Sin LLM en retrieval; algoritmo de traversal fijo |
| **Token Efficiency** | MVC <4000 tokens por query | Summaries para context_rules; token budget management |
| **Reproducibilidad** | SAR: outputs verificables y versionados | Schemas JSON/YAML estrictos; gates de validación |
| **Portabilidad** | Data store legible sin herramientas especiales | Archivos YAML/MD en filesystem; git-friendly |
| **Latencia** | raise.ctx: <100ms para retrieval | Sin llamadas a LLM; traversal O(n) en grafo sparse |
| **Extensibilidad** | Soportar múltiples stacks sin cambios core | Reglas agnósticas; categorías extensibles |

---

<details>
<summary><h2>Component Diagram: SAR Pipeline (C4 Level 3)</h2></summary>

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          SAR PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────┐ │
│  │   DETECT    │    │    SCAN     │    │  DESCRIBE   │    │  GOVERN  │ │
│  │  (Phase 0)  │───▶│  (Phase 1)  │───▶│  (Phase 2)  │───▶│ (Phase 3)│ │
│  │             │    │             │    │             │    │          │ │
│  │ Classify    │    │ Analyze     │    │ Generate    │    │ Extract  │ │
│  │ project     │    │ structure   │    │ conventions │    │ rules    │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └──────────┘ │
│        │                  │                  │                  │       │
│        ▼                  ▼                  ▼                  ▼       │
│  project-profile    scan-report       conventions.md    rules/*.yaml   │
│      .yaml          .json (interno)                     graph.yaml     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Component | Responsabilidad | Output |
|-----------|-----------------|--------|
| DETECT (Phase 0) | Clasificar proyecto: tipo, estructura, stack | `project-profile.yaml` |
| SCAN (Phase 1) | Analizar imports, naming patterns, estructura | `scan-report.json` (interno) |
| DESCRIBE (Phase 2) | Generar documentación de convenciones | `conventions.md` |
| GOVERN (Phase 3) | Extraer reglas con confidence scores | `rules/*.yaml`, `graph.yaml` |

</details>

<details>
<summary><h2>Component Diagram: raise.ctx Retrieval (C4 Level 3)</h2></summary>

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       raise.ctx RETRIEVAL                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────┐ │
│  │   QUERY     │    │   FILTER    │    │  TRAVERSE   │    │  FORMAT  │ │
│  │   Parser    │───▶│   Engine    │───▶│   Engine    │───▶│  Output  │ │
│  │             │    │             │    │             │    │          │ │
│  │ Parse CLI   │    │ By scope,   │    │ Graph walk  │    │ Build    │ │
│  │ args        │    │ confidence  │    │ for deps    │    │ MVC      │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └──────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Component | Responsabilidad |
|-----------|-----------------|
| Query Parser | Parsear --task, --scope, --min-confidence, --max-tokens |
| Filter Engine | Filtrar reglas por scope match, confidence threshold, status |
| Traverse Engine | Recorrer grafo: requires, related_to, detectar conflicts |
| Format Output | Generar MVC: primary_rules, context_rules, warnings, graph_context |

</details>

<details>
<summary><h2>Cross-Cutting Concerns</h2></summary>

| Concern | Approach |
|---------|----------|
| **Schema Validation** | JSON Schema para rules, graph, MVC; validación en gates |
| **Error Handling** | Jidoka: parar en fase fallida, no propagar errores |
| **Configuration** | `.raise/sar.yaml` para config de SAR; CLI flags para raise.ctx |
| **Versioning** | Semver por regla individual; version en cada archivo YAML |
| **Security** | SAR NO ejecuta código; solo lee archivos. Sanitización pre-LLM |

</details>

---

## Referencias

- [Solution Vision SAR](./solution-vision.md) - Componente de extracción
- [Solution Vision raise.ctx](./solution-vision-context.md) - Componente de entrega
- [Tech Design](./tech-design.md) - Diseño técnico detallado
- [Solution Roadmap](./solution-roadmap.md) - Plan de implementación
- [C4 Model](https://c4model.com/) - Simon Brown

---

*Generado siguiendo kata `create-architecture-overview` v1.0*
