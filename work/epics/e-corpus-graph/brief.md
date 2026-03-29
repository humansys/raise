# Epic E-CORPUS: RaiSE Corpus Generation & Versioned Knowledge Graph

> **Status:** IDEA
> **Jira:** [RAISE-1049](https://humansys.atlassian.net/browse/RAISE-1049)
> **Capability:** C3 (Knowledge Graph) + C6 (Documentation)
> **Created:** 2026-03-28

## Problem Statement

RaiSE genera una cantidad significativa de conocimiento estructurado — governance docs, ADRs, research reports, skill definitions, patterns, module descriptions, API surfaces — pero este conocimiento está disperso entre filesystem, Confluence, y Jira. No existe un proceso estandarizado para:

1. **Generar un corpus completo** de cada versión de RaiSE (el "snapshot" de todo el conocimiento en un punto del tiempo)
2. **Extraer la ontología** de ese corpus de forma determinista y reproducible
3. **Producir un grafo de conocimiento versionado** que se distribuya como artefacto de cada release
4. **Garantizar que cada versión publicada** (PyPI, GitHub) incluya su grafo correspondiente

Hoy `rai graph build` genera un grafo local desde el filesystem, pero:
- No incluye conocimiento de Confluence ni Jira
- No es reproducible entre máquinas (depende de estado local)
- No se versiona ni distribuye con los releases
- La ontología es implícita (hardcoded en extractors), no explícita ni versionada

## Hypothesis

Si generamos un corpus canónico por release y extraemos su ontología de forma determinista, podemos distribuir un grafo de conocimiento como artefacto de primera clase. Esto habilita: agentes que entienden la versión exacta del framework que están usando, búsqueda semántica offline, y trazabilidad total entre artefactos de governance y código.

## Vision

### El Corpus

Un **corpus** es la colección completa y normalizada de todos los artefactos de conocimiento de una versión de RaiSE:

```
dist/corpus/v2.4.0/
├── manifest.yaml          ← índice de todos los artefactos incluidos
├── governance/             ← ADRs, policies, standards (desde filesystem)
├── architecture/           ← module descriptions, API surfaces (desde discover)
├── skills/                 ← skill definitions normalizadas
├── patterns/               ← pattern catalog
├── research/               ← research reports y evidence catalogs
├── confluence/             ← snapshot de páginas clave (desde Confluence API)
├── backlog/                ← estado del backlog en el momento (desde Jira API)
└── metadata.yaml           ← versión, fecha, commit SHA, fuentes incluidas
```

**Principio:** El corpus es un artefacto reproducible. Dado el mismo commit SHA y las mismas credenciales de API, dos ejecuciones producen el mismo corpus.

### La Ontología

La **ontología** es la estructura formal del conocimiento de RaiSE — los tipos de entidades, relaciones, y atributos que existen en el grafo:

```yaml
# ontology/v2.4.0.yaml
version: "2.4.0"
entities:
  Module:
    attributes: [name, description, dependencies, public_api]
    sources: [discover, filesystem]
  Skill:
    attributes: [name, type, category, guardrails, inputs, outputs]
    sources: [filesystem, confluence]
  ADR:
    attributes: [number, title, status, date, context, decision]
    sources: [filesystem, confluence]
  Pattern:
    attributes: [id, description, context, type, from_story]
    sources: [filesystem]
  Epic:
    attributes: [key, title, status, stories, capability]
    sources: [jira, filesystem]
  # ...
relations:
  depends_on: {from: Module, to: Module}
  implements: {from: Module, to: Skill}
  decided_by: {from: Module, to: ADR}
  discovered_in: {from: Pattern, to: Epic}
  # ...
```

**Principio:** La ontología es versionada y explícita. Cambios en la ontología requieren ADR (porque cambian la estructura del conocimiento).

### El Grafo Versionado

El **grafo** es la instanciación de la ontología sobre el corpus — el knowledge graph concreto de una versión:

```
dist/graph/v2.4.0/
├── graph.json              ← grafo completo en formato portable
├── graph.jsonld             ← linked data format (para interoperabilidad)
├── ontology.yaml           ← ontología usada para esta versión
├── stats.yaml              ← métricas: nodos, edges, cobertura, completitud
└── CHANGELOG.md            ← diff vs versión anterior (nodos added/removed/changed)
```

**Distribución:** El grafo se publica como:
- Artefacto dentro del paquete PyPI (`rai/data/graph/`)
- Release asset en GitHub
- Página de Confluence con stats y visualización
- Input para `rai graph query` (reemplaza el build local)

## Pipeline

```
[1. Collect]     →  [2. Normalize]  →  [3. Extract]  →  [4. Build]  →  [5. Validate]  →  [6. Publish]

Filesystem ──┐
Confluence ──┤→ Corpus ──→ Ontology ──→ Graph ──→ Quality Gates ──→ PyPI + GitHub + Confluence
Jira ────────┘   (canonical)  (explicit)   (versioned)  (coverage, consistency)
```

### Etapas

| Etapa | Input | Output | Herramienta |
|-------|-------|--------|-------------|
| **Collect** | Filesystem + APIs | Raw artifacts | `rai corpus collect` |
| **Normalize** | Raw artifacts | Corpus canónico | `rai corpus normalize` |
| **Extract** | Corpus + Ontología | Entity/relation instances | `rai corpus extract` |
| **Build** | Instances | Graph (JSON/JSON-LD) | `rai graph build --from-corpus` |
| **Validate** | Graph + Ontología | Quality report | `rai graph validate` |
| **Publish** | Graph + Stats | PyPI, GitHub, Confluence | `rai release publish` (extended) |

## Success Metrics

1. **Reproducibilidad:** Dos ejecuciones del pipeline desde el mismo commit SHA producen grafos idénticos
2. **Cobertura:** >90% de módulos, skills, y ADRs representados en el grafo
3. **Distribución:** Cada release en PyPI incluye su grafo correspondiente
4. **Diff:** Changelog automático entre versiones del grafo (qué cambió en el conocimiento)
5. **Ontología explícita:** `ontology.yaml` versionado en el repo, cambios requieren ADR

## Appetite

- **Size:** L-XL (8-15 stories)
- **Timeframe:** v3.0.0 (strategic, not urgent)
- **Risk:** Medio — requiere estabilizar la ontología actual antes de formalizarla

## Stories (boceto)

| # | Story | Size | Dependency |
|---|-------|------|------------|
| 1 | Formalizar ontología actual en `ontology.yaml` | M | Ninguna |
| 2 | `rai corpus collect` — recolección desde filesystem | M | S1 |
| 3 | `rai corpus collect` — integración Confluence (snapshot) | M | S2 + Adapter v2 |
| 4 | `rai corpus collect` — integración Jira (backlog snapshot) | S | S2 + Adapter v2 |
| 5 | `rai corpus normalize` — normalización a formato canónico | M | S2 |
| 6 | `rai corpus extract` — extracción de entidades/relaciones | L | S1 + S5 |
| 7 | `rai graph build --from-corpus` — generación del grafo | M | S6 |
| 8 | `rai graph validate` — quality gates (cobertura, consistencia) | M | S7 |
| 9 | Graph diff — changelog entre versiones | S | S7 |
| 10 | Publicación del grafo en PyPI package | M | S7 |
| 11 | Publicación del grafo como GitHub release asset | S | S7 |
| 12 | Integración con `rai release publish` | M | S10 + S11 |
| 13 | Documentación: ontology evolution ADR process | S | S1 |

## Rabbit Holes

- No intentar inferencia semántica ni ML sobre el grafo — este epic es sobre extracción determinista
- No construir un graph database (Neo4j, etc.) — JSON/JSON-LD como formato portable es suficiente para v1
- No incluir conocimiento de repos externos (raise-pro, rai-agent) — solo raise-commons/raise-core primero
- No bloquear por Adapter v2 — las stories de filesystem (S1-S2, S5-S9) pueden avanzar sin adaptadores

## Dependencies

- **Adapter v2 (RAISE-1021/1022/1023):** Necesario para S3 y S4 (Confluence/Jira collection), pero no bloquea el core del pipeline
- **Ontology Refinement (E15):** Trabajo previo en ontología — verificar qué se puede reusar
- **Discovery (E13):** `rai discover scan` ya extrae símbolos — base para la etapa de Extract

## Strategic Context

Este epic transforma el knowledge graph de herramienta interna a **producto distribuible**. Un framework que se distribuye con su propio grafo de conocimiento versionado es un diferenciador significativo: los agentes que usan RaiSE entienden exactamente qué versión están usando y qué ha cambiado entre versiones.

Esto conecta directamente con la visión de **Pluggable Domains**: si el grafo es un artefacto de primera clase, los dominios (cartuchos de conocimiento) son extensiones del grafo con su propia ontología parcial.
