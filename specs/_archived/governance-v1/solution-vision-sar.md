# SAR Component - Solution Vision

**Document ID**: VIS-SAR-001
**Version**: 1.2.0
**Date**: 2026-01-28
**Author**: Emilio + Claude Opus 4.5
**Status**: Aprobado
**Parent Doc**: [RaiSE Framework Vision](./solution-vision.md) - Visión unificada del framework
**Related Docs**:
  - [Solution Roadmap](./solution-roadmap.md) - Roadmap táctico
  - [CTX Component Vision](./solution-vision-context.md) - Componente de entrega de MVC
  - [Architecture Overview](./architecture-overview.md) - Arquitectura C4

> **Nota**: Este documento detalla el componente **SAR** (Layer 2: Infrastructure).
> Para la visión completa del framework, ver [solution-vision.md](./solution-vision.md).

---

## Contexto de Arquitectura

SAR es uno de dos componentes que trabajan juntos para entregar gobernanza a agentes LLM:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RAISE GOVERNANCE ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────┐                                                │
│  │        SAR          │  CLI: raise sar analyze                        │
│  │   (Extracción)      │  Slash: /raise.sar.analyze                     │
│  ├─────────────────────┤                                                │
│  │ • Analiza codebase  │                                                │
│  │ • Extrae patrones   │                                                │
│  │ • Genera reglas     │                                                │
│  │ • Construye grafo   │                                                │
│  └──────────┬──────────┘                                                │
│             │ genera                                                     │
│             ▼                                                            │
│  ┌─────────────────────┐                                                │
│  │    Data Store       │  .raise/                                       │
│  │   (output de SAR)   │  ├── rules/*.yaml                              │
│  │                     │  ├── graph.yaml                                │
│  │                     │  ├── conventions.md                            │
│  │                     │  └── project-profile.yaml                      │
│  └──────────┬──────────┘                                                │
│             │ consume                                                    │
│             ▼                                                            │
│  ┌─────────────────────┐                                                │
│  │    raise.ctx        │  CLI: raise ctx get                            │
│  │  (Entrega de MVC)   │  Slash: /raise.ctx                             │
│  │                     │  Ver: solution-vision-context.md               │
│  └──────────┬──────────┘                                                │
│             │ entrega                                                    │
│             ▼                                                            │
│  ┌─────────────────────┐                                                │
│  │   Agente LLM        │                                                │
│  └─────────────────────┘                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Este documento** cubre solo el componente **SAR** (extracción).
Para el componente de entrega (**raise.ctx**), ver [solution-vision-context.md](./solution-vision-context.md).

---

## Contexto de Negocio

### Declaracion del Problema

Los equipos de desarrollo tienen conocimiento tribal implicito sobre convenciones, patrones y decisiones arquitectonicas que no esta documentado de forma consumible por agentes LLM.

- **Quien se ve afectado?** Orquestadores y agentes trabajando en codebases brownfield
- **Cual es el impacto?** Agentes sin contexto generan codigo inconsistente
- **Cuando ocurre?** Cada vez que un agente trabaja sin conocer las "reglas no escritas"
- **Por que es importante?** Sin gobernanza explicita, la calidad del codigo AI es impredecible

### Vision de la Solucion

**SAR (Software Architecture Reconstruction)** es el componente de RaiSE que:

1. **Analiza** codebases brownfield para descubrir patrones existentes
2. **Extrae** convenciones con confidence scores basados en adoption rate
3. **Genera** reglas semanticamente densas en formato consumible
4. **Construye** un grafo de relaciones entre reglas

**Propuesta de valor**: Transformar conocimiento tribal implicito en reglas explicitas, versionadas, y estructuradas para consumo por el componente `raise.ctx`.

**Lo que SAR NO hace**:
- NO entrega contexto a agentes (eso es `raise.ctx`)
- NO hace traversal del grafo en runtime (eso es `raise.ctx`)
- NO evalua contra estandares externos (paradigma "Facts Not Gaps")

### CLI

```bash
# Ejecutar analisis SAR completo
raise sar analyze [path]

# Slash command en Claude Code
/raise.sar.analyze
```

---

## Estrategia de Producto: Open Core

### Modelo de Negocio

SAR tiene dos tiers que difieren en el **metodo de extraccion**:

| Aspecto | Open Core (Free) | Licensed (Paid) |
|---------|------------------|-----------------|
| **Metodo** | LLM synthesis | Determinista (ast-grep) |
| **Precision** | ~70-85% | >95% |
| **Reproducibilidad** | Variable | 100% |
| **Stack support** | Agnostico | Optimizado por stack |
| **Output format** | Identico | Identico |

**Clave**: Ambos tiers producen el **mismo formato de output** (rules/*.yaml, graph.yaml). Esto permite upgrade sin friccion.

### Flywheel de Adopcion

```
Developer usa SAR Open Core (free)
         ↓
Extrae reglas de su proyecto
         ↓
Equipo ve valor en gobernanza
         ↓
Empresa necesita precision y reproducibilidad
         ↓
Upgrade a Licensed
```

### El Patron "Deterministic Rails, Non-Deterministic Engine"

El Open Core usa un patron hibrido:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPEC-KIT HARNESS                             │
│  (workflow determinista: templates, gates, validacion)          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   /raise.sar.analyze                                           │
│         │                                                       │
│         ▼                                                       │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │              LLM SYNTHESIS ENGINE                        │  │
│   │                                                          │  │
│   │  Pipeline: DETECT → SCAN → DESCRIBE → GOVERN            │  │
│   │  (todo LLM-driven en Open Core)                         │  │
│   │                                                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│   Output estructurado (validado contra schemas):               │
│   • .raise/project-profile.yaml                                │
│   • .raise/conventions.md                                      │
│   • .raise/rules/*.yaml                                        │
│   • .raise/graph.yaml                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Principio Core: Facts Not Gaps

SAR opera bajo el paradigma **"Facts Not Gaps"**:

| Lo que SAR hace | Lo que SAR NO hace |
|-----------------|-------------------|
| Describe "lo que ES" | Evalua contra estandares externos |
| Mide consistencia interna | Impone Clean Architecture/Code |
| "95% usa camelCase" (hecho) | "Viola principio SOLID" (opinion) |
| Identifica inconsistencias internas | Prescribe refactorizaciones |
| Extrae convenciones observadas | Asume estilo arquitectonico |

### Las Tres Capas de Verdad

**Layer 1: Hechos Deterministicos** (100% reproducible en Licensed)
- Conteo de archivos, estructura, imports
- Patrones de naming con frecuencias
- Grafo de dependencias
- Configuracion y entry points

**Layer 2: Entendimiento Sintetizado** (LLM interpreta Layer 1)
- "Este codebase usa patron X" (no "viola patron Y")
- Score de consistencia interna por dimension
- Arquitectura-as-found (lo que ES)

**Layer 3: Artefactos de Gobernanza** (output final de SAR)
- `rules/*.yaml` - reglas unitarias
- `graph.yaml` - grafo de relaciones
- `conventions.md` - documentacion human-readable
- `.cursorrules` - formato compatible con Cursor

---

## Arquitectura: Pipeline SAR

### Vista de 4 Fases

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SAR PIPELINE                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 0: DETECT                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Output: project-profile.yaml                                    │   │
│  │  - Clasificacion: backend, web, cli, library, monorepo          │   │
│  │  - Estructura: monolith, monorepo, multi-part                    │   │
│  │  - Stack tecnologico desde manifests                              │   │
│  │  - Flags de analisis condicional                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  PHASE 1: SCAN                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Output: scan-report.json (interno, no publicado)                │   │
│  │  - Grafo de imports/exports                                       │   │
│  │  - Patrones de naming con conteos                                 │   │
│  │  - Patrones de error handling, logging                            │   │
│  │  - Estructuras de clases/funciones                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  PHASE 2: DESCRIBE                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Output: conventions.md, architecture-as-found.md                │   │
│  │  - Descripcion de arquitectura observada                         │   │
│  │  - Convenciones con confidence scores                            │   │
│  │  - Inconsistencias internas identificadas                         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  PHASE 3: GOVERN                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Output: rules/*.yaml, graph.yaml, .cursorrules                  │   │
│  │  - Reglas unitarias con confidence scores                        │   │
│  │  - Grafo de relaciones entre reglas                              │   │
│  │  - Artefactos de gobernanza listos para raise.ctx               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Comparacion: Open Core vs Licensed

| Dimension | Open Core | Licensed |
|-----------|-----------|----------|
| **Phase 0-1** | LLM synthesis | Determinista (ast-grep, ripgrep) |
| **Phase 2-3** | LLM synthesis | LLM con input deterministico |
| **Tiempo total** | < 20 min | < 15 min |
| **Reproducibilidad** | Variable | 100% en Phase 0-1 |
| **Output format** | Identico | Identico |

---

## Output: Formato de Datos

SAR produce los siguientes artefactos en `.raise/`:

### 1. project-profile.yaml

```yaml
version: "1.0"
generated_date: "2026-01-28T10:30:00Z"
scan_method: "llm-synthesis"  # o "deterministic"

project:
  name: "example-api"
  type: "backend"
  structure: "monolith"
  primary_language: "typescript"
  framework: "express"

analysis_flags:
  requires_api_scan: true
  requires_data_models: true
```

### 2. rules/*.yaml (Reglas Unitarias)

```yaml
# .raise/rules/naming/ts-repository-suffix.yaml
id: ts-repository-suffix
version: 1.0.0
status: active

category: naming
tags: [naming, infrastructure, typescript]

confidence: 0.95
enforcement: strong
evidence_count: 38
total_applicable: 40

title: Repository classes must end with 'Repository' suffix
intent: Maintain consistent naming for data access layer classes

description: |
  All classes in src/repositories/ that provide data access
  must follow the naming pattern: {Entity}Repository.

languages: [typescript]
pattern:
  type: ast-grep
  query: "class $NAME { $$$ }"
  scope: "src/repositories/**/*.ts"

examples:
  positive:
    - code: "export class UserRepository { ... }"
      source: src/repositories/UserRepository.ts
  negative:
    - code: "export class UserStore { ... }"
      fix: "Rename to UserRepository"

provenance:
  source: sar-extracted
  tool_version: "sar-v1.0"
  timestamp: "2026-01-28T10:30:00Z"
```

### 3. graph.yaml (Grafo de Relaciones)

```yaml
# .raise/graph.yaml
version: "1.0"
generated_date: "2026-01-28"

nodes:
  - id: ts-repository-suffix
    category: naming
    layer: infrastructure
    confidence: 0.95
    enforcement: strong

  - id: ts-no-direct-db-access
    category: architecture
    layer: domain
    confidence: 0.88
    enforcement: moderate

edges:
  - from: ts-no-direct-db-access
    to: ts-repository-suffix
    type: requires
    reason: "Si prohibes acceso directo a DB, necesitas el patron Repository"

  - from: old-dao-pattern
    to: ts-repository-suffix
    type: superseded_by
    reason: "Repository reemplaza DAO en este codebase"
```

### Tipos de Relaciones (Edges)

| Tipo | Semantica | Ejemplo |
|------|-----------|---------|
| `requires` | A necesita B | "no-direct-db" requires "repository-pattern" |
| `conflicts_with` | A y B son mutuamente excluyentes | "singleton" conflicts_with "dependency-injection" |
| `supersedes` | A reemplaza B (deprecated) | "new-auth" supersedes "old-auth" |
| `related_to` | Informacional, sin dependencia | "naming-services" related_to "naming-repos" |

---

## Confidence-Based Enforcement

### Scoring de Confianza

Cada convencion recibe un **confidence score** basado en adoption rate:

| Adoption Rate | Confidence | Enforcement |
|---------------|------------|-------------|
| 100% | Unanimous | `hard` - sin excepciones |
| 90-99% | Strong | `strong` - excepciones notadas |
| 80-89% | Moderate | `moderate` - lista de excepciones |
| 60-79% | Weak | `advisory` - solo recomendacion |
| < 60% | Inconsistent | `none` - documentar, no enforcar |

**Regla de oro**: Solo convenciones >= 80% se convierten en reglas enforceables.

---

## Metricas de Exito

### Metricas de SAR (Extraccion)

| Metrica | Open Core | Licensed |
|---------|-----------|----------|
| Precision de reglas | >70% | >95% |
| Cobertura de convenciones | >60% | >85% |
| Reproducibilidad | Variable | 100% |
| Pipeline total | <20 min | <15 min |
| Human edit rate | <30% | <10% |

### Metricas de Adopcion

| Metrica | Target |
|---------|--------|
| Proyectos con SAR ejecutado | 10+ (Open Core) |
| Reglas extraidas total | 500+ |
| Upgrade rate a Licensed | 10% |

---

## Restricciones y Supuestos

### Restricciones Tecnicas

1. **No-Git Constraint**: SAR debe funcionar sin historial de git
2. **Formato Portable**: Output editable por humanos, parseable por herramientas
3. **Schema Validation**: Todo output debe pasar validacion de schema

### Restricciones de Negocio

1. **Build vs Buy**: Usar ast-grep/ripgrep, no crear parsers custom
2. **KISS/DRY/YAGNI**: MVP minimo
3. **Human-in-the-loop**: Reglas requieren aprobacion humana
4. **Facts Not Gaps**: No evaluar contra estandares externos

### Supuestos

1. Codebase tiene patrones repetidos suficientes para extraer reglas
2. Orquestadores invertiran tiempo inicial en validar reglas
3. Formato YAML+Markdown es suficientemente expresivo

---

## Glosario

| Termino | Definicion |
|---------|------------|
| **SAR** | Software Architecture Reconstruction - extraccion de patrones |
| **Facts Not Gaps** | Describir "lo que ES" sin evaluar contra externos |
| **Regla** | Unidad atomica de gobernanza (YAML+Markdown) |
| **Grafo** | Estructura de relaciones entre reglas |
| **Confidence Score** | Porcentaje de adoption de una convencion |
| **Enforcement Level** | Nivel de aplicacion: hard, strong, moderate, advisory, none |

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-01-28 | Separacion de Solution Vision y Roadmap |
| 1.1.0 | 2026-01-28 | Clarificacion de scope: SAR solo extrae, raise.ctx entrega MVC |

---

*SAR genera los datos. Para la entrega de MVC a agentes, ver [raise.ctx](./solution-vision-context.md).*
