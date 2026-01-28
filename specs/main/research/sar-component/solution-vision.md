# SAR Component - Solution Vision

**Document ID**: VIS-SAR-001
**Version**: 1.0.0
**Date**: 2026-01-28
**Author**: Emilio + Claude Opus 4.5
**Status**: Aprobado
**Related Docs**:
  - [Solution Roadmap](./solution-roadmap.md) - Roadmap tactico y fases
  - RES-SAR-REPR-001 (Semantic Density Research)
  - RES-BMAD-BFLD-001-D2 (Strategic Decision Report)
  - RES-SPECKIT-CRIT-001 (Spec-kit Critiques Research)

---

## Contexto de Negocio

### Declaracion del Problema

Los agentes LLM que asisten en desarrollo de software operan sin contexto suficiente sobre las convenciones, patrones y decisiones arquitectonicas del proyecto brownfield en el que trabajan.

- **Quien se ve afectado?** Orquestadores humanos y agentes LLM trabajando en codebases brownfield
- **Cual es el impacto?** Codigo generado inconsistente, violaciones de convenciones, deuda tecnica acumulada, friction en code review
- **Cuando ocurre?** Cada vez que un agente genera codigo sin conocer las "reglas no escritas" del proyecto
- **Por que es importante?** La confiabilidad del codigo generado por AI depende directamente del contexto que recibe; sin contexto de gobernanza, la calidad es impredecible

### Vision de la Solucion

**SAR (Software Architecture Reconstruction)** es el componente de RaiSE que:

1. **Extrae** patrones y convenciones de codebases brownfield
2. **Representa** esas convenciones como reglas semanticamente densas en un grafo de conocimiento
3. **Entrega** el Minimum-Viable Context (MVC) necesario para que agentes LLM generen codigo conforme

**Propuesta de valor central**: Transformar el conocimiento tribal implicito en un codebase en reglas explicitas, versionadas, y consumibles por agentes.

**Diferenciadores clave**:
- Grafo de relaciones entre reglas para contexto estructurado
- Interfaz CLI para integracion en flujos de agentes (`raise get rules`)
- Formato optimizado para RAG y context window de LLMs
- Modelo Open Core con path a determinismo enterprise

**Resultados objetivo**:
- Agentes generan codigo que pasa code review en primer intento >80% del tiempo
- Reduccion de "friction" en onboarding de nuevos desarrolladores/agentes
- Convenciones documentadas y evolucionables como codigo

---

## Estrategia de Producto: Open Core

### Modelo de Negocio

RaiSE adopta un modelo **Open Core** donde la metodologia y herramientas base son gratuitas, con un producto licenciado que ofrece capacidades enterprise-grade.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RAISE FRAMEWORK                                  │
├───────────────────────────────────┬─────────────────────────────────────┤
│         OPEN CORE (Free)          │        LICENSED (Paid)              │
├───────────────────────────────────┼─────────────────────────────────────┤
│ • Metodologia RaiSE completa      │ • Todo Open Core +                  │
│ • Principios y Governance as Code │ • SAR Determinista (ast-grep based) │
│ • SAR No-Determinista             │ • Pipeline 100% Observable          │
│   (LLM synthesis + harness)       │ • Tooling optimizado por stack      │
│ • Stack-agnostico                 │ • Metricas y dashboards             │
│ • Output: rules + graph           │ • Integracion CI/CD                 │
│ • Single-repo scope               │ • SLA de precision (>95%)           │
│                                   │ • Multi-repo governance             │
│                                   │ • Soporte enterprise                │
└───────────────────────────────────┴─────────────────────────────────────┘
```

### Justificacion Estrategica

**1. Open Core Demuestra Valor Real**

El SAR no-determinista no es un "demo crippled" — es una herramienta funcional que:
- Extrae reglas reales de codebases reales
- Produce outputs en el mismo formato que la version pagada
- Permite adopcion incremental sin vendor lock-in
- Funciona con cualquier stack (React, PydanticAI, PHP, Vite, etc.)

**2. Diferenciacion Clara y Defendible**

| Dimension | Open Core | Licensed |
|-----------|-----------|----------|
| **Precision** | ~70-85% (LLM variance) | >95% (determinista) |
| **Reproducibilidad** | Eventual consistency | Exact reproducibility |
| **Observabilidad** | Outputs finales | Pipeline completo |
| **Soporte de stacks** | Agnostico (LLM infiere) | Optimizado por stack |
| **Escala** | Proyectos individuales | Multi-repo, enterprise |
| **Auditabilidad** | Confidence scores | Evidencia deterministica |

**3. Flywheel de Adopcion**

```
Developer prueba RaiSE (free)
         ↓
Extrae reglas de su proyecto
         ↓
Ve valor, lo propone en su empresa
         ↓
Empresa necesita: reproducibilidad, CI/CD, SLA
         ↓
Upgrade a Licensed
```

### El Patron "Deterministic Rails, Non-Deterministic Engine"

El Open Core usa un patron hibrido inspirado en BMAD + spec-kit:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPEC-KIT HARNESS                             │
│  (deterministic workflow, templates, gates)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   /raise.sar.analyze  (comando unico)                          │
│         │                                                       │
│         ▼                                                       │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │              BMAD-STYLE LLM AGENT                        │  │
│   │                                                          │  │
│   │  • Structured prompts con secciones esperadas           │  │
│   │  • JSON/YAML schemas para outputs                       │  │
│   │  • Context management (purging, chunking)               │  │
│   │  • Write-as-you-go documentation                        │  │
│   │                                                          │  │
│   │  Pipeline interno:                                       │  │
│   │  DETECT → SCAN → DESCRIBE → GOVERN                      │  │
│   │  (todo LLM-driven, no AST tools)                        │  │
│   │                                                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│   Output estructurado:                                          │
│   • specs/main/sar/project-profile.yaml                        │
│   • specs/main/sar/conventions.md                              │
│   • specs/main/sar/rules/*.yaml                                │
│   • specs/main/sar/graph.yaml                                  │
│                                                                 │
│   Gate de validacion:                                           │
│   • Schema validation (estructura correcta)                    │
│   • Confidence scores presentes                                │
│   • Provenance documentada                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Ventajas del enfoque hibrido:**

| Ventaja | Justificacion |
|---------|---------------|
| **Time-to-market** | No requiere AST parsers custom, LLM analiza directamente |
| **Flexibilidad** | Funciona con cualquier lenguaje/framework sin tooling especifico |
| **Evolucionable** | Fases pueden hacerse mas deterministicas incrementalmente |
| **Dog-fooding** | RaiSE se usa para construir RaiSE |
| **Open core viable** | Metodologia usable sin tooling propietario |

**Riesgos y mitigaciones:**

| Riesgo | Mitigacion |
|--------|------------|
| **Consistencia** | Schemas estrictos + validation gates |
| **Reproducibilidad** | Versionar prompts, documentar confidence levels |
| **Costo de tokens** | Context purging patterns (de BMAD) |
| **Hallucinations** | Cross-validation, confidence-based enforcement |

---

## Contexto Historico

### Origen del SAR Legacy

El SAR que existia en RaiSE (los katas de analisis contra Clean Code y Clean Architecture) **nunca fue una decision de framework**. Fue un artefacto del proyecto C#/Clean Architecture donde se desarrollaron originalmente los katas SAR. Ese lente proyecto-especifico fue erroneamente generalizado como "el enfoque SAR de RaiSE".

**Implicacion critica**: No hay un "SAR existente" que preservar. SAR v2 es el **primer SAR real a nivel de framework**.

### Decision BUILD-FIRST

Basado en el analisis competitivo de BMAD Method y la investigacion de extraccion determinista, se tomo la decision de **BUILD-FIRST**: construir el primer SAR real a nivel de framework desde primeros principios, usando:

- **BMAD como benchmark competitivo** (que superar, no que copiar)
- **Herramientas deterministas como fundamento** (ast-grep, ripgrep)
- **El paradigma "Facts Not Gaps" como filosofia**

**Referencia**: `specs/main/research/bmad-brownfield-analysis/strategic-decision-report.md`

---

## Principio Core: Facts Not Gaps

SAR opera bajo el paradigma **"Facts Not Gaps"**:

| Lo que SAR hace | Lo que SAR NO hace |
|-----------------|-------------------|
| Describe "lo que ES" | Evalua contra estandares externos |
| Mide consistencia interna | Impone Clean Architecture/Code |
| "95% usa camelCase" (hecho) | "Viola principio SOLID" (opinion) |
| Identifica inconsistencias | Prescribe refactorizaciones |
| Extrae convenciones observadas | Asume estilo arquitectonico |

### Las Tres Capas de Verdad

**Layer 1: Hechos Deterministicos** (tools extract, 100% reproducible)
- Conteo de archivos, estructura, imports
- Patrones de naming con frecuencias
- Grafo de dependencias desde ast-grep
- Configuracion y entry points

**Layer 2: Entendimiento Sintetizado** (LLM interpreta datos estructurados)
- "Este codebase usa patron X" (no "viola patron Y")
- "95% de servicios usan camelCase" (hecho observado)
- Score de consistencia interna por dimension
- Arquitectura-as-found (lo que ES)

**Layer 3: Artefactos de Gobernanza** (LLM genera desde Layers 1-2)
- `.cursorrules` desde convenciones >= 80% adoption
- `guardrails.yaml` (constraints machine-readable)
- Grafo de reglas con relaciones
- Inconsistencias como action items (NO violaciones)

**Referencia**: `specs/main/research/bmad-brownfield-analysis/governance-bridge-spec.md`

---

## Arquitectura: Pipeline SAR

### Vista de 4 Fases

> **Nota**: Open Core ejecuta todas las fases via LLM synthesis. Licensed usa herramientas deterministas en Phases 0-1.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SAR PIPELINE                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 0: DETECT                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  → project-profile.yaml                                          │   │
│  │  - Clasificacion de proyecto (backend, web, cli, library...)     │   │
│  │  - Deteccion de estructura (monolith, monorepo, multi-part)      │   │
│  │  - Stack tecnologico desde manifests                              │   │
│  │  - Flags de analisis condicional                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  PHASE 1: SCAN                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  → scan-report.json                                              │   │
│  │  - Grafo de imports/exports                                       │   │
│  │  - Patrones de naming con conteos                                 │   │
│  │  - Patrones de error handling, logging                            │   │
│  │  - Estructuras de clases/funciones                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  PHASE 2: DESCRIBE                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  → architecture-as-found.md, conventions-discovered.md           │   │
│  │  - Descripcion de arquitectura observada                         │   │
│  │  - Convenciones con confidence scores                            │   │
│  │  - Inconsistencias internas                                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  PHASE 3: GOVERN                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  → rules/*.yaml, graph.yaml, .cursorrules                        │   │
│  │  - Reglas unitarias extraidas                                     │   │
│  │  - Grafo de relaciones                                            │   │
│  │  - Artefactos de gobernanza                                       │   │
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

---

## Confidence-Based Enforcement

### Scoring de Confianza

Cada convencion descubierta recibe un **confidence score** basado en su adoption rate:

| Adoption Rate | Confidence | Enforcement | Accion |
|---------------|------------|-------------|--------|
| 100% | **Unanimous** | `hard` | ENFORCE - regla sin excepciones |
| 90-99% | **Strong** | `strong` | ENFORCE con excepciones notadas |
| 80-89% | **Moderate** | `moderate` | ENFORCE con lista de excepciones |
| 60-79% | **Weak** | `advisory` | RECOMMEND - solo advisory |
| < 60% | **Inconsistent** | `none` | DOCUMENT - decision de equipo |

**Regla de oro**: Solo convenciones con >= 80% adoption se convierten en reglas enforceables.

### MVC Filtering por Confidence

```bash
# Solo reglas enforceables (>= 80%)
raise get rules --task "..." --min-confidence 0.80

# Incluir recommendations (>= 60%)
raise get rules --task "..." --min-confidence 0.60

# Todo, incluyendo inconsistencias documentadas
raise get rules --task "..." --include-all
```

---

## Dos Niveles de Representacion

### Nivel 1: Reglas Unitarias

Cada regla es un documento YAML+Markdown auto-contenido que representa una convencion o patron del codebase.

```yaml
# .raise/rules/naming/ts-repository-suffix.yaml
id: ts-repository-suffix
version: 1.0.0
status: active

# Classification
category: naming
severity: medium
priority: P1
tags: [naming, infrastructure, typescript]

# Confidence (from SAR extraction)
confidence: 0.95
enforcement: strong
evidence_count: 38
total_applicable: 40

# Semantic Core
title: Repository classes must end with 'Repository' suffix
intent: Maintain consistent naming for data access layer classes

description: |
  All classes in src/repositories/ that provide data access
  must follow the naming pattern: {Entity}Repository.

# Pattern Specification
languages: [typescript]
pattern:
  type: ast-grep
  query: "class $NAME { $$$ }"
  constraint: "NAME matches /Repository$/"
  scope: "src/repositories/**/*.ts"

# Evidence (Few-shot examples)
examples:
  positive:
    - code: "export class UserRepository { ... }"
      source: src/repositories/UserRepository.ts
  negative:
    - code: "export class UserStore { ... }"
      explanation: "Does not follow naming convention"
      fix: "Rename to UserRepository"

# Provenance
provenance:
  source: sar-extracted
  extraction:
    tool_version: "sar-v1.0"
    timestamp: "2026-01-28T10:30:00Z"
```

### Nivel 2: Grafo de Conocimiento

El grafo conecta reglas con relaciones semanticas:

```yaml
# .raise/rules/graph.yaml
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
```

### Minimum-Viable Context (MVC)

Cuando un agente solicita reglas, el sistema devuelve el **contexto minimo necesario**:

```bash
raise get rules --task "implement user authentication service" --scope "src/services/"
```

Response incluye:
- `primary_rules`: Reglas directamente aplicables a la tarea
- `context_rules`: Reglas relacionadas necesarias para entender las primarias
- `warnings`: Deprecations, inconsistencias
- `graph_context`: Subgrafo relevante

---

## Metricas de Exito

### Metricas por Tier

| Metrica | Open Core Target | Licensed Target |
|---------|------------------|-----------------|
| Precision de reglas | >70% | >95% |
| Cobertura de convenciones | >60% | >85% |
| Reproducibilidad | Variable | 100% |
| Pipeline total | <20 min | <15 min |
| Human edit rate | <30% | <10% |

### Metricas de Adopcion

| Metrica | Open Core | Licensed |
|---------|-----------|----------|
| Proyectos activos | 10+ | 3+ paying |
| Reglas extraidas | 500+ total | 100+ per customer |
| Conversiones | N/A | 10% de activos |

---

## Restricciones y Supuestos

### Restricciones Tecnicas

1. **No-Git Constraint**: SAR debe funcionar en codebases sin historial de version control
2. **Token Budget**: MVC debe caber en context window razonable (<4K tokens tipico)
3. **Formato Portable**: Reglas deben ser editables por humanos y parseables por herramientas

### Restricciones de Negocio

1. **Build vs Buy**: Usar herramientas existentes (ast-grep, ripgrep) no crear nuevas
2. **KISS/DRY/YAGNI**: MVP minimo, sin over-engineering
3. **Human-in-the-loop**: Siempre requiere aprobacion humana para reglas governance-grade
4. **Facts Not Gaps**: No evaluar contra estandares externos

### Supuestos

1. El codebase brownfield tiene suficientes patrones repetidos para extraer reglas utiles
2. Los orquestadores estan dispuestos a invertir tiempo inicial en crear reglas
3. Los agentes LLM pueden seguir reglas si se les entregan en contexto
4. El formato YAML+Markdown es suficientemente expresivo para todas las categorias de reglas

---

## Research Base

Este documento se construye sobre el siguiente research:

| Documento | Ubicacion | Hallazgos Clave |
|-----------|-----------|-----------------|
| Semantic Density Research | `sar-component/semantic-density/` | YAML+Markdown, 256-512 tokens/regla |
| BMAD Competitive Analysis | `bmad-competitive-analysis/` | Benchmark competitivo |
| Strategic Decision Report | `bmad-brownfield-analysis/` | BUILD-FIRST decision |
| Governance Bridge Spec | `bmad-brownfield-analysis/` | Confidence-based enforcement |
| Spec-kit Critiques | `speckit-critiques/` | "Deterministic Rails" pattern |
| Deterministic Extraction | `deterministic-rule-extraction/` | Scoring formula, evidence standards |

---

## Glosario

| Termino | Definicion |
|---------|------------|
| **SAR** | Software Architecture Reconstruction - extraer arquitectura y patrones de codigo existente |
| **Facts Not Gaps** | Paradigma que describe "lo que ES" sin evaluar contra estandares externos |
| **Regla** | Unidad atomica de gobernanza que especifica un patron o convencion |
| **Grafo de Conocimiento** | Estructura que conecta reglas con relaciones semanticas |
| **MVC** | Minimum-Viable Context - conjunto minimo de reglas + contexto para una tarea |
| **Confidence Score** | Porcentaje de adoption de una convencion en el codebase |
| **Enforcement Level** | Nivel de aplicacion: hard, strong, moderate, advisory, none |
| **Open Core** | Modelo donde metodologia base es gratuita, con producto licensed enterprise |
| **Deterministic Rails** | Workflow estructurado con templates y gates que orquesta el proceso |
| **Non-Deterministic Engine** | LLM synthesis que produce contenido dentro del harness |

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-01-28 | Separacion de Solution Vision (estrategico) y Solution Roadmap (tactico) |

---

*Este documento define el "que" y "por que" de SAR. Para el "cuando" y "como", ver [Solution Roadmap](./solution-roadmap.md).*
