# SAR Component - Solution Vision

**Document ID**: VIS-SAR-001
**Title**: SAR (Software Architecture Reconstruction) - Componente RaiSE
**Version**: 0.3.0
**Date**: 2026-01-28
**Author**: Emilio + Claude Opus 4.5
**Status**: Borrador - Estrategia Open Core Definida
**Related Docs**:
  - RES-SAR-REPR-001 (Semantic Density Research)
  - RES-BMAD-BFLD-001-D2 (Strategic Decision Report)
  - RES-BMAD-BFLD-001-D3 (Governance Bridge Spec)
  - RES-SPECKIT-CRIT-001 (Spec-kit Critiques Research)
  - deterministic-extraction-patterns.md

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

1. **Extrae** patrones y convenciones de codebases brownfield de manera determinista
2. **Representa** esas convenciones como reglas semanticamente densas en un grafo de conocimiento
3. **Entrega** el Minimum-Viable Context (MVC) necesario para que agentes LLM generen codigo conforme

**Propuesta de valor central**: Transformar el conocimiento tribal implicito en un codebase en reglas explicitas, versionadas, y consumibles por agentes.

**Diferenciadores clave**:
- Extraccion determinista (no AI-inferred) para gobernanza confiable
- Grafo de relaciones entre reglas para contexto estructurado
- Interfaz CLI para integracion en flujos de agentes (`raise get rules`)
- Formato optimizado para RAG y context window de LLMs

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

### El Patrón "Deterministic Rails, Non-Deterministic Engine"

El Open Core usa un patrón híbrido inspirado en BMAD + spec-kit:

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

### Origen Anecdotico del SAR Legacy

El SAR que existia en RaiSE (los katas de analisis contra Clean Code y Clean Architecture) **nunca fue una decision de framework**. Fue un artefacto del proyecto C#/Clean Architecture donde se desarrollaron originalmente los katas SAR. Ese lente proyecto-especifico fue erroneamente generalizado como "el enfoque SAR de RaiSE".

**Implicacion critica**: No hay un "SAR existente" que preservar. SAR v2 es el **primer SAR real a nivel de framework**.

### Decision BUILD-FIRST

Basado en el analisis competitivo de BMAD Method y la investigacion de extraccion determinista, se tomo la decision de **BUILD-FIRST**: construir el primer SAR real a nivel de framework desde primeros principios, usando:

- **BMAD como benchmark competitivo** (que superar, no que copiar)
- **Herramientas deterministas como fundamento** (ast-grep, ripgrep)
- **El paradigma "Facts Not Gaps" como filosofia**

Esta decision invalida las opciones PORT (no hay nada que portar) y ADOPT (BMAD carece de gobernanza).

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

## Arquitectura: Pipeline SAR v2

> **Nota**: Esta seccion describe el pipeline **Licensed** (determinista). El **Open Core** usa el mismo flujo conceptual pero con LLM synthesis en todas las fases en lugar de herramientas deterministicas.

### Vista de 4 Fases (Licensed - Determinista)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SAR v2 PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 0: DETECT (deterministico, ~1 min)                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  tree + find + manifest parse → project-profile.yaml             │   │
│  │  - Clasificacion de proyecto (backend, web, cli, library...)     │   │
│  │  - Deteccion de estructura (monolith, monorepo, multi-part)      │   │
│  │  - Stack tecnologico desde manifests                              │   │
│  │  - Flags de analisis condicional                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  PHASE 1: SCAN (deterministico, ~2-5 min)                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ast-grep + ripgrep → scan-report.json                           │   │
│  │  - Grafo de imports/exports                                       │   │
│  │  - Patrones de naming con conteos                                 │   │
│  │  - Patrones de error handling, logging                            │   │
│  │  - Estructuras de clases/funciones                                │   │
│  │  - Evidencia deterministica y auditable                           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  PHASE 2: DESCRIBE (LLM synthesis, ~5-10 min)                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  LLM reads: project-profile.yaml + scan-report.json              │   │
│  │  + selected key files (entry points, config, README)              │   │
│  │                                                                   │   │
│  │  Produces:                                                        │   │
│  │  - architecture-as-found.md (lo que la arquitectura ES)          │   │
│  │  - conventions-discovered.md (patrones + confidence scores)       │   │
│  │  - consistency-report.md (inconsistencias internas)               │   │
│  │  - dependency-map.md (grafo de dependencias)                      │   │
│  │  - sar-index.md (navegacion AI-consumable)                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  PHASE 3: GOVERN (LLM + graph, ~2-5 min)                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Extract governance artifacts:                                    │   │
│  │  - .cursorrules (convenciones >= 80% adoption)                   │   │
│  │  - guardrails.yaml (constraints machine-readable)                │   │
│  │  - rules/*.yaml (reglas unitarias)                                │   │
│  │  - graph.yaml (grafo de relaciones)                               │   │
│  │  - inconsistencies.md (action items, NO violations)              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  TOTAL: < 15 min (vs BMAD 30-120 min)                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Ventaja Competitiva vs BMAD

| Dimension | BMAD | SAR v2 | Ganador |
|-----------|------|--------|---------|
| **Velocidad** | 30-120 min | < 15 min | SAR v2 |
| **Reproducibilidad** | No determinista | Determinista (Phases 0-1) | SAR v2 |
| **Output value** | Documentacion | Artefactos de gobernanza | SAR v2 |
| **Auditabilidad** | "LLM said so" | JSON con evidencia | SAR v2 |
| **Escalabilidad** | Degrada en codebases grandes | Tools manejan cualquier tamaño | SAR v2 |
| **Opinionatedness** | Bajo (documenta) | Zero (facts + consistencia) | Empate |

**BMAD gana en**: Platform breadth (18+ IDEs). SAR v2 prioriza Claude Code + extensibilidad via MCP.

---

## Project Classification (Phase 0)

Phase 0 clasifica el proyecto para determinar que analisis son relevantes.

### Tipos de Proyecto Soportados

| Tipo | Descripcion | Ejemplos |
|------|-------------|----------|
| `backend` | APIs, servicios, workers | Express, FastAPI, Go services |
| `web` | Frontend web | React, Vue, Angular |
| `mobile` | Apps moviles | React Native, Flutter |
| `cli` | Herramientas de linea de comando | CLI tools, scripts |
| `library` | Paquetes reutilizables | npm packages, Python libs |
| `monorepo` | Multiples proyectos | Turborepo, Nx, pnpm workspaces |

### Flags de Analisis Condicional

| Flag | Descripcion | Aplica a |
|------|-------------|----------|
| `requires_api_scan` | Escanear rutas API | backend, web |
| `requires_data_models` | Escanear schemas/migrations | backend |
| `requires_ui_components` | Inventariar componentes | web, mobile |
| `requires_state_management` | Analizar state | web, mobile |
| `requires_deployment_config` | Docker, K8s, CI/CD | backend, infra |

### Output: project-profile.yaml

```yaml
version: "1.0"
generated_date: "2026-01-28T10:30:00Z"
scan_method: "deterministic"

project:
  name: "example-api"
  type: "backend"
  structure: "monolith"
  primary_language: "typescript"
  framework: "express"
  runtime: "node-20"

analysis_flags:
  requires_api_scan: true
  requires_data_models: true
  requires_ui_components: false
  requires_state_management: false

metrics:
  files: 234
  loc: 45678
  modules_detected: 12
```

Esto elimina analisis irrelevantes (no escanear UI components en un CLI, no buscar APIs en una library).

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

**Regla de oro**: Solo convenciones con >= 80% adoption se convierten en reglas enforceables. Todo lo demás es documentacion o items de decision de equipo.

### Confidence en el Grafo

```yaml
# graph.yaml
nodes:
  - id: ts-repository-suffix
    category: naming
    layer: infrastructure
    confidence: 0.95
    enforcement: strong
    evidence_count: 38
    total_applicable: 40
    exceptions:
      - src/legacy/auth_handler.ts
    provenance:
      source: sar-extracted
      scan_report_ref: "scan-report.json#patterns.classes.line456"

edges:
  - from: ts-no-direct-db
    to: ts-repository-suffix
    type: requires
    confidence_propagation: min  # el edge hereda el menor confidence
```

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
  This convention was observed in 95% of repository classes.

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
    - code: "export class OrderRepository { ... }"
      source: src/repositories/OrderRepository.ts
  negative:
    - code: "export class UserStore { ... }"
      explanation: "Does not follow naming convention"
      fix: "Rename to UserRepository"

# Exceptions
exceptions:
  - path: src/legacy/auth_handler.ts
    reason: "Legacy module, pre-dates convention"
    type: legacy

# Provenance
provenance:
  source: sar-extracted
  extraction:
    tool_version: "sar-v2.0"
    timestamp: "2026-01-28T10:30:00Z"
    scan_report_ref: "scan-report.json#patterns.classes"
  validation:
    reviewed_by: null
    approved: false
```

### Nivel 2: Grafo de Conocimiento

El grafo conecta reglas con relaciones semanticas que permiten:
- Navegacion contextual
- Resolucion de dependencias
- Deteccion de conflictos
- Traversal para MVC

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

  - id: ts-service-suffix
    category: naming
    layer: application
    confidence: 0.92
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

  - from: ts-repository-suffix
    to: ts-service-suffix
    type: related_to
    reason: "Ambas son convenciones de naming por capa"

  - from: old-dao-pattern
    to: ts-repository-suffix
    type: superseded_by
    reason: "Repository reemplaza DAO en este codebase"
```

### Minimum-Viable Context (MVC)

Cuando un agente solicita reglas, el sistema no devuelve reglas aisladas sino el **contexto minimo necesario** para aplicarlas correctamente.

**Ejemplo de Query**:
```bash
raise get rules --task "implement user authentication service" --scope "src/services/"
```

**MVC Response**:
```yaml
# Minimum-Viable Context para la tarea
task: "implement user authentication service"
scope: "src/services/"
min_confidence: 0.80

primary_rules:
  - id: ts-service-suffix
    confidence: 0.92
    enforcement: strong
    # ... contenido completo de la regla

  - id: ts-async-error-handling
    confidence: 0.87
    enforcement: moderate
    # ... contenido completo de la regla

context_rules:  # Reglas relacionadas necesarias para entender las primarias
  - id: ts-repository-suffix
    relation: "ts-service-suffix uses repositories"
    summary: "Services inject repositories ending with 'Repository'"
    confidence: 0.95

  - id: ts-custom-error-classes
    relation: "ts-async-error-handling requires"
    summary: "Define custom error classes for domain errors"
    confidence: 0.91

warnings:
  - type: deprecated
    message: "Rule ts-old-auth-pattern is deprecated. Use ts-jwt-auth-pattern instead."
  - type: inconsistency
    message: "Error handling pattern has 87% adoption. 4 services deviate."

graph_context:
  nodes: [ts-service-suffix, ts-async-error-handling, ts-repository-suffix, ...]
  edges: [...]  # Subgrafo relevante
```

---

## Alineacion Estrategica

### Metas de Negocio

1. **Calidad de codigo generado por AI**
   - Metrica: % de codigo que pasa code review sin cambios relacionados a convenciones
   - Objetivo: >80% en proyectos con SAR implementado

2. **Reduccion de deuda tecnica por inconsistencia**
   - Metrica: Violaciones de convenciones detectadas en CI
   - Objetivo: Reduccion del 50% en 3 meses

3. **Tiempo de onboarding de agentes/developers**
   - Metrica: Tiempo hasta primer PR aprobado
   - Objetivo: Reduccion del 40%

### Impacto en el Usuario

| Stakeholder | Puntos de Dolor Actuales | Beneficios Esperados |
|-------------|--------------------------|----------------------|
| **Orquestador** | Codigo AI inconsistente, mucho review | Codigo conforme, review enfocado en logica |
| **Agente LLM** | Sin contexto de convenciones | MVC con reglas relevantes por tarea |
| **Tech Lead** | Convenciones no documentadas | Reglas versionadas y evolucionables |
| **Nuevo Dev** | Curva de aprendizaje larga | Documentacion ejecutable del "como hacemos las cosas" |

---

## Alcance por Tier

### Tier 1: Open Core MVP (Lanzamiento Inicial)

El Open Core es el primer entregable, usando el patron "Deterministic Rails, Non-Deterministic Engine".

**1. Comando SAR No-Determinista**
```
.raise-kit/commands/03-sar/
└── raise.sar.analyze.md    # Comando unico que ejecuta pipeline completo
```

Caracteristicas:
- Pipeline completo via LLM synthesis (DETECT → SCAN → DESCRIBE → GOVERN)
- Prompts estructurados con secciones esperadas
- Schemas JSON/YAML para validar outputs
- Gates de validacion (estructura, no contenido)
- Context management patterns (inspirado en BMAD)
- Stack-agnostico (React, PydanticAI, PHP, Vite, Next.js, etc.)

**2. Formato de Regla Unitaria**
- Schema YAML+Markdown validable (JSON Schema)
- Campos: identity, classification, confidence, pattern, examples, provenance
- Compatibilidad con Cursor/Claude/Cline rules
- Mismo formato que version Licensed (portabilidad garantizada)

**3. Formato de Grafo**
- YAML con nodos y edges
- Confidence scores en nodos (LLM-estimated)
- Relaciones: requires, conflicts_with, supersedes, related_to
- Validacion de integridad (no cycles, refs exist)

**4. CLI Skill: `raise get rules`**
- Query por tarea (--task)
- Query por scope (--scope, --file)
- Filter por confidence (--min-confidence)
- Output: MVC en YAML/JSON

**5. Documentacion y Metodologia**
- Guia de uso de SAR no-determinista
- Patrones de prompts para diferentes stacks
- Best practices para validacion humana de reglas

### Tier 2: Licensed (Post-Validacion Open Core)

El producto Licensed agrega capacidades enterprise sobre Open Core.

**1. Pipeline Determinista (Phases 0-1)**
- `phase0-detect.sh` → project-profile.yaml (determinista)
- `phase1-scan.sh` → scan-report.json (ast-grep, ripgrep)
- 100% reproducible, auditable, < 5 min
- Evidencia con file:line references

**2. LLM Synthesis Mejorada (Phases 2-3)**
- LLM recibe datos estructurados de Phase 0-1 (mejor input = mejor output)
- Mayor precision por contexto deterministico
- architecture-as-found.md
- conventions-discovered.md
- .cursorrules generation automatica

**3. Observabilidad Completa**
- Logs de cada fase del pipeline
- Metricas de precision por categoria de regla
- Dashboard de gobernanza
- Drift detection (convenciones que cambian over time)

**4. Integraciones Enterprise**
- CI/CD gates (GitHub Actions, GitLab CI)
- Multi-repo governance (reglas compartidas entre proyectos)
- Team-level rule inheritance
- Audit logs para compliance

**5. Tooling Optimizado por Stack**
- Parsers especificos para stacks comunes
- TypeScript/Node (primera prioridad)
- Python/FastAPI/PydanticAI
- React/Next.js

### Fuera del Alcance (Ambos Tiers)

1. ~~Extraccion completamente automatica sin supervision~~ (siempre human-in-the-loop)
2. ~~Machine learning para inferir reglas~~ (no ML, solo LLM synthesis)
3. ~~Evaluacion contra Clean Code/Architecture~~ (deliberadamente excluido por "Facts Not Gaps")

### Considerado para Futuro (Post-Licensed)

1. Integracion con IDEs (VS Code extension, JetBrains plugin)
2. RAG avanzado (embeddings, retrieval semantico, re-ranking)
3. Autofix suggestions basadas en reglas

---

## Metricas de Exito

### Metricas Open Core

| Metrica | Target | Medicion |
|---------|--------|----------|
| Precision de reglas extraidas | >70% | Reglas son validas y aplicables (human validation) |
| Cobertura de convenciones | >60% | Convenciones principales capturadas |
| Latencia de `raise get rules` | <500ms | Benchmark en codebase mediano |
| Pipeline total | <20 min | En codebase de 500 files |
| Human edit rate | <30% | Reglas usables con minor edits |

### Metricas Licensed

| Metrica | Target | Medicion |
|---------|--------|----------|
| Precision de reglas extraidas | >95% | Reglas validas (deterministic extraction) |
| Recall de convenciones | >85% | Convenciones capturadas vs manual audit |
| Reproducibilidad Phase 0-1 | 100% | Misma entrada = misma salida |
| Pipeline total | <15 min | En codebase de 500 files |
| Evidencia trazable | 100% | Toda regla tiene file:line reference |

### Metricas de Adopcion (Ambos Tiers)

| Metrica | Target (Open Core) | Target (Licensed) |
|---------|-------------------|-------------------|
| Proyectos usando SAR | 10+ | 3+ paying customers |
| Reglas extraidas | 500+ | 100+ per customer |
| GitHub stars | 500+ | N/A |
| Conversiones free→paid | N/A | 10% de usuarios activos |

---

## Restricciones y Supuestos

### Restricciones Tecnicas

1. **No-Git Constraint**: SAR debe funcionar en codebases sin historial de version control
2. **Determinismo**: Phases 0-1 deben ser 100% reproducibles (misma entrada = misma salida)
3. **Token Budget**: MVC debe caber en context window razonable (<4K tokens tipico)
4. **Formato Portable**: Reglas deben ser editables por humanos y parseables por herramientas

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

### Analisis Competitivo

| Documento | Ubicacion |
|-----------|-----------|
| BMAD Competitive Analysis | `specs/main/research/bmad-competitive-analysis/` |
| BMAD Brownfield Reverse Engineering | `specs/main/research/bmad-brownfield-analysis/reverse-engineering-report.md` |
| Strategic Decision (BUILD-FIRST) | `specs/main/research/bmad-brownfield-analysis/strategic-decision-report.md` |
| Spec-kit Critiques & Differentiation | `specs/main/research/speckit-critiques/` |

### Especificaciones Tecnicas

| Documento | Ubicacion |
|-----------|-----------|
| Governance Bridge Spec | `specs/main/research/bmad-brownfield-analysis/governance-bridge-spec.md` |
| Deterministic Extraction Patterns | `specs/main/research/deterministic-rule-extraction/` |
| Solution Vision Rule Extraction | `specs/main/research/deterministic-rule-extraction/solution-vision-rule-extraction-katas.md` |

### Representacion de Reglas

| Documento | Ubicacion |
|-----------|-----------|
| Semantic Density Research | `specs/main/research/sar-component/semantic-density/` |
| Rule Template v2 | `specs/main/research/rule-extraction-alignment/prototypes/templates/rule-template-v2.md` |

### Hallazgos Clave Integrados

**De Semantic Density Research (RES-SAR-REPR-001)**:
- Formato recomendado: YAML para estructura + Markdown para contenido
- Campos universales: id, severity, message, pattern, examples
- Chunk size: 256-512 tokens por regla para RAG optimo
- Metadata para filtering: category, tags, applies_to, languages

**De Strategic Decision Report**:
- BUILD-FIRST decision (no PORT, no ADOPT)
- Pipeline de 4 fases
- < 15 min vs BMAD 30-120 min
- Deterministic foundation + LLM synthesis

**De Governance Bridge Spec**:
- Confidence-based enforcement (>= 80% para enforce)
- Conventions → Rules pipeline
- Inconsistencies como action items (no violations)

**De Deterministic Extraction Patterns**:
- Scoring: S = 0.40F + 0.40C + 0.20L (para no-git)
- Evidence standards: 3+ positive, 2+ negative, 2+ modules
- Tools: ast-grep, ripgrep, bash (no git dependency)
- Target metrics: Precision >=95%, Recall >=80%

**De Spec-kit Critiques Research (RES-SPECKIT-CRIT-001)**:
- Spec-kit crea "deterministic harness" via templates y gates
- Critica: 3.7:1 markdown:code ratio, "documentation theater"
- Fortaleza: estructura de workflow, gates de validacion
- Insight: El harness es el PROCESO, no el CONTENIDO
- Patrón viable: "Deterministic Rails, Non-Deterministic Engine"

---

## Roadmap

### Track A: Open Core (Prioridad Maxima)

**Fase A1: Foundation & Schemas (Semana 1)**

- [ ] Finalizar JSON Schema para regla unitaria
- [ ] Finalizar JSON Schema para graph.yaml
- [ ] Crear templates de output SAR
- [ ] Documentar formato de prompts estructurados

**Fase A2: Comando SAR No-Determinista (Semanas 2-3)**

- [ ] Crear `.raise-kit/commands/03-sar/raise.sar.analyze.md`
- [ ] Implementar pipeline LLM (DETECT → SCAN → DESCRIBE → GOVERN)
- [ ] Crear prompts estructurados por fase
- [ ] Implementar gates de validacion (schema validation)
- [ ] Context management (chunking, purging patterns)
- [ ] Testear con stacks: TypeScript, Python, PHP

**Fase A3: CLI `raise get rules` (Semana 4)**

- [ ] Implementar query por tarea (--task)
- [ ] Implementar query por scope (--scope, --file)
- [ ] Filter por confidence (--min-confidence)
- [ ] Output MVC en YAML/JSON
- [ ] Integracion con agente Claude Code

**Fase A4: Documentacion & Launch (Semana 5)**

- [ ] Guia de uso SAR Open Core
- [ ] Ejemplos para diferentes stacks
- [ ] Best practices para validacion humana
- [ ] README y getting started
- [ ] Publicacion open source

### Track B: Licensed (Post-Validacion Open Core)

**Fase B1: Pipeline Determinista (Semanas 6-8)**

- [ ] Implementar `phase0-detect.sh` (determinista)
- [ ] Implementar `phase1-scan.sh` (ast-grep, ripgrep)
- [ ] JSON Schema para project-profile.yaml
- [ ] JSON Schema para scan-report.json
- [ ] Evidencia con file:line references

**Fase B2: LLM Synthesis Mejorada (Semanas 9-10)**

- [ ] LLM recibe datos estructurados de Phase 0-1
- [ ] architecture-as-found.md generation
- [ ] conventions-discovered.md generation
- [ ] .cursorrules automatico

**Fase B3: Observabilidad & Enterprise (Semanas 11-12)**

- [ ] Dashboard de gobernanza
- [ ] CI/CD integrations (GitHub Actions, GitLab CI)
- [ ] Multi-repo governance
- [ ] Audit logs

**Fase B4: Graph Intelligence (Semanas 13-14)**

- [ ] Algoritmo de MVC traversal optimizado
- [ ] Deteccion de conflictos automatica
- [ ] Confidence propagation en edges
- [ ] Drift detection

### Criterio de Transicion A → B

El Track B inicia cuando Open Core demuestra:
- 10+ proyectos usando SAR activamente
- Precision >70% validada por usuarios
- Al menos 3 empresas expresan interes en version Licensed
- Feedback consolidado sobre limitaciones del enfoque no-determinista

---

## Open Questions para Resolver

1. **Donde vive el rule store?**
   - `.raise/rules/` en el repo del proyecto?
   - Repo separado de gobernanza?
   - Hibrido (base + overrides)?

2. **Como se versionan las reglas?**
   - Semver por regla individual?
   - Version del rule set completo?
   - Git tags?

3. **Como se resuelven conflictos entre reglas?**
   - Prioridad explicita?
   - Scope mas especifico gana?
   - Requiere resolucion humana?

4. **Como se integra con CI/CD?**
   - Gate que bloquea?
   - Warning que reporta?
   - Autofix que corrige?

5. **Como evoluciona el grafo?**
   - Edges manuales solamente?
   - Inferencia automatica de relaciones?
   - Validacion de consistencia?

---

## Glosario (Alineado con RaiSE v2.1)

| Termino | Definicion |
|---------|------------|
| **SAR** | Software Architecture Reconstruction - proceso de extraer arquitectura y patrones de codigo existente |
| **Facts Not Gaps** | Paradigma que describe "lo que ES" sin evaluar contra estandares externos |
| **Regla** | Unidad atomica de gobernanza que especifica un patron o convencion del codebase |
| **Grafo de Conocimiento** | Estructura que conecta reglas con relaciones semanticas |
| **MVC** | Minimum-Viable Context - conjunto minimo de reglas + contexto necesario para una tarea |
| **Confidence Score** | Porcentaje de adoption de una convencion en el codebase |
| **Enforcement Level** | Nivel de aplicacion de una regla: hard, strong, moderate, advisory, none |
| **Inconsistencia** | Donde el codebase contradice sus propios patrones (NO "violacion") |
| **Orquestador** | Humano que dirige agentes LLM (no "developer" - termino canonico RaiSE) |
| **Validation Gate** | Punto de verificacion que una regla o conjunto debe pasar (no "DoD") |
| **Open Core** | Modelo de negocio donde metodologia base es gratuita, con producto licensed enterprise-grade |
| **Deterministic Rails** | Workflow estructurado con templates y gates que orquesta el proceso |
| **Non-Deterministic Engine** | LLM synthesis que produce contenido dentro del harness estructurado |
| **Stack-agnostico** | Capacidad de SAR Open Core de funcionar con cualquier tecnologia sin tooling especifico |

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 0.1.0 | 2026-01-28 | Version inicial |
| 0.2.0 | 2026-01-28 | Integrado: contexto historico, Facts Not Gaps, pipeline 4 fases, confidence-based enforcement, project classification, research base |
| 0.3.0 | 2026-01-28 | Estrategia Open Core: modelo dual (Open Core no-determinista + Licensed determinista), patron "Deterministic Rails, Non-Deterministic Engine", roadmap por tracks, metricas por tier, integracion research spec-kit |

---

**Siguiente Paso**: Iniciar Track A (Open Core) - Fase A1: Finalizar schemas y templates de output SAR.

---

*Documento creado como ancla para alinear research y desarrollo del componente SAR de RaiSE.*
