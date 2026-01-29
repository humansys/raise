---
id: "VIS-RAISE-003"
title: "RaiSE Framework v2.3 - Solution Vision"
version: "2.3.0"
date: "2026-01-29"
status: "Active"
author: "Emilio + Claude Opus 4.5"
supersedes: "VIS-RAISE-002 (v2.2 - 7 command categories)"
related_docs:
  - "[ADR-008: Context/Kata/Skill Simplification](./adrs/adr-008-kata-skill-context-simplification.md)"
  - "[Glossary v2.3](.raise/context/glossary.md)"
  - "[Constitution](.raise/context/constitution.md)"
  - "[Work Cycles](.raise/context/work-cycles.md)"
template: "lean-spec-v1"
---

# RaiSE Framework v2.3 - Solution Vision

## Resumen Ejecutivo

**RaiSE v2.3** (Reliable AI Software Engineering) es un framework de gobernanza para desarrollo AI-assisted. Transforma conocimiento tribal implícito en **gobernanza explícita, versionada, y ejecutable**.

### Evolución desde v2.2

| Aspecto | v2.2 | v2.3 |
|---------|------|------|
| **Ontología** | 7 command categories + SAR/CTX components | **Context/Kata/Skill** (3 capas) |
| **Organización** | Commands by function | **Work Cycles** (project/feature/setup/improve) |
| **Ejecución** | spec-kit harness | **Kata Harness** (platform capability) |
| **Carga cognitiva** | 10+ concepts | **3 concepts** (Context, Kata, Skill) |
| **Terminología** | SAR, CTX, Regla, Command | setup/, context/, Guardrail, Kata/Skill |

### La Metáfora del Niwashi (庭師)

Un Niwashi (jardinero japonés tradicional) posee:

- **Sabiduría** (cuándo podar, por qué ciertas formas): Esto es **Context**
- **Práctica** (ciclo de cuidado estacional, flujo de trabajo): Esto es **Kata**
- **Técnica** (cortes específicos, manejo de herramientas): Esto es **Skill**

El Niwashi transmite sabiduría cultural adaptable a cada jardín. Las Katas son el vehículo de esa transmisión, adaptables por cada Dojo (equipo).

---

## 1. Arquitectura: Modelo de 3 Capas

```mermaid
graph TB
    subgraph RAISE["RAISE FRAMEWORK v2.3"]
        subgraph CONTEXT["CONTEXT (Capa de Sabiduría)"]
            direction LR
            C1["Constitution"]
            C2["Patterns"]
            C3["Guardrails"]
            C4["Golden Data"]
            C5["Templates"]
            C6["Gates"]
        end

        subgraph KATA["KATA (Capa de Práctica)"]
            subgraph PROJECT["katas/project/"]
                P1["discovery.md"]
                P2["vision.md"]
                P3["design.md"]
                P4["backlog.md"]
            end
            subgraph FEATURE["katas/feature/"]
                F1["stories.md"]
                F2["plan.md"]
                F3["implement.md"]
                F4["review.md"]
            end
            subgraph SETUP["katas/setup/"]
                S1["analyze.md"]
                S2["ecosystem.md"]
            end
            subgraph IMPROVE["katas/improve/"]
                I1["retrospective.md"]
                I2["evolve-kata.md"]
            end
        end

        subgraph SKILL["SKILL (Capa de Acción)"]
            direction LR
            SK1["retrieve-mvc"]
            SK2["run-gate"]
            SK3["check-compliance"]
            SK4["explain-rule"]
            SK5["generate-rules"]
            SK6["edit-rule"]
        end
    end

    CONTEXT -->|"Informa"| KATA
    KATA -->|"Invoca"| SKILL

    style CONTEXT fill:#e1f5fe
    style KATA fill:#fff3e0
    style SKILL fill:#e8f5e9
```

### Descripción de Capas

| Capa | Propósito | Contenido | Ubicación |
|------|-----------|-----------|-----------|
| **CONTEXT** | Sabiduría que INFORMA pero no se EJECUTA | Constitution, Patterns, Guardrails, Golden Data, Templates, Gates | `.raise/context/`, `.raise/templates/`, `.raise/gates/` |
| **KATA** | Procesos que los equipos PRACTICAN y ADAPTAN | Katas organizadas por Work Cycle (project/feature/setup/improve) | `.raise/katas/{work_cycle}/` |
| **SKILL** | Operaciones ATÓMICAS con inputs/outputs claros | retrieve-mvc, run-gate, check-compliance, explain-rule, generate-rules, edit-rule | `.raise/skills/` |

**Notas:**
- **Katas** son adaptables por cada Dojo (equipo)
- **Kata Harness** ejecuta TODAS las katas (de cualquier Work Cycle)
- **Skills** son planos porque son atómicos - el nombre lleva todo el significado semántico
- Invocación: `/project/discovery`, `/feature/implement`, `/setup/analyze`, etc.

### Interacción entre Capas

```mermaid
sequenceDiagram
    participant O as Orquestador
    participant KH as Kata Harness
    participant S as Sistema (.raise/)

    O->>KH: /project/discovery (o cualquier kata)
    KH->>S: Lee kata metadata
    KH->>S: Carga Context (constitution, patterns, guardrails)
    S-->>KH: Context cargado

    loop Pasos con Jidoka
        KH->>KH: Ejecuta paso
        KH->>KH: Verificación
        alt Verificación falla
            KH-->>O: STOP - Requiere resolución
        end
    end

    KH->>S: Invoca skill: retrieve-mvc
    S-->>KH: MVC
    KH->>S: Invoca skill: run-gate
    S-->>KH: Gate result

    KH-->>O: Output: Artefacto + Gate result
    KH-->>O: Handoff: Siguiente kata sugerida
```

**Nota**: El Kata Harness ejecuta katas de **cualquier Work Cycle** (project/, feature/, setup/, improve/), no solo feature/.

---

## 2. Problema y Solución

### Declaración del Problema

Los equipos de desarrollo tienen **conocimiento tribal implícito** sobre convenciones y patrones que no está documentado de forma consumible por agentes LLM.

| Aspecto | Descripción |
|---------|-------------|
| **Quién** | Orquestadores y agentes LLM trabajando en codebases brownfield |
| **Impacto** | Agentes sin contexto generan código inconsistente con la arquitectura existente |
| **Cuándo** | Cada vez que un agente trabaja sin conocer las "reglas no escritas" |
| **Por qué importa** | Sin gobernanza explícita, la calidad del código AI-generated es impredecible |

### Visión de la Solución

RaiSE transforma conocimiento tribal implícito en **gobernanza explícita, versionada, y ejecutable**:

1. **Context** almacena la sabiduría (constitution, guardrails, patterns, golden data)
2. **Katas** guían procesos SDLC (discovery → vision → design → implementation)
3. **Skills** ejecutan operaciones atómicas (retrieve-mvc, run-gate, check-compliance)
4. **Kata Harness** orquesta la ejecución con Jidoka (stop-and-fix)

**Resultado**: Código AI-generated que pasa code review en el primer intento.

---

## 3. Work Cycles (Ciclos de Trabajo)

Los Work Cycles reemplazan las 7 categorías de comandos de v2.2, organizando las katas por **contexto operacional**:

### Los Cuatro Ciclos

| Ciclo | Frecuencia | Pregunta que Responde | Katas |
|-------|------------|----------------------|-------|
| **project/** | 1x por épica | "¿Qué hago al iniciar un proyecto?" | discovery, vision, design, backlog |
| **feature/** | Nx por feature | "¿Qué hago para implementar un feature?" | stories, plan, implement, review |
| **setup/** | 1x brownfield | "¿Qué hago al entrar a un repo existente?" | analyze, ecosystem |
| **improve/** | Continuo | "¿Qué hago para mejorar?" | retrospective, evolve-kata |

### Flujo entre Ciclos

```mermaid
flowchart TD
    SETUP["setup/<br/>(Onboarding)"]
    PROJECT["project/<br/>(Planning)"]
    FEATURE["feature/<br/>(Execution)"]
    IMPROVE["improve/<br/>(Kaizen)"]

    SETUP -->|"habilita"| PROJECT
    PROJECT -->|"genera features"| FEATURE
    FEATURE -->|"alimenta"| IMPROVE
    IMPROVE -->|"refina"| SETUP
    IMPROVE -->|"refina"| PROJECT
    IMPROVE -->|"refina"| FEATURE

    style SETUP fill:#e3f2fd
    style PROJECT fill:#fff8e1
    style FEATURE fill:#e8f5e9
    style IMPROVE fill:#fce4ec
```

**Notas:**
- Los ciclos son **ortogonales**: un Orquestador puede estar en cualquiera según el momento
- El Ciclo de Mejora **retroalimenta** todos los demás ciclos
- Proyectos pequeños pueden saltar de setup/ directo a feature/
- **Kata Harness ejecuta katas de TODOS los ciclos**, no solo de uno específico

---

## 4. Kata Harness (Platform Capability)

El **Kata Harness** es la capability de plataforma que generaliza el control de flujo LLM, basado en la innovación de spec-kit.

**Alcance**: El Kata Harness ejecuta **TODAS las katas** de cualquier Work Cycle:
- `/project/discovery`, `/project/vision`, `/project/design`, `/project/backlog`
- `/feature/stories`, `/feature/plan`, `/feature/implement`, `/feature/review`
- `/setup/analyze`, `/setup/ecosystem`
- `/improve/retrospective`, `/improve/evolve-kata`

### Terminología de Industria

| Término | Contexto | RaiSE |
|---------|----------|-------|
| **Agent Harness** | Ejecución: infraestructura que envuelve un LLM para gestionar tareas | **Kata Harness usa este significado** |
| **Evaluation Harness** | Testing: framework de benchmarking (e.g., EleutherAI) | No aplica |

### Componentes del Kata Harness

```yaml
# Conceptual: .raise/harness/config.yaml
kata_harness:
  version: "1.0"

  # La kata es el "programa"
  kata_schema:
    - frontmatter (id, titulo, work_cycle, prerequisites, template, gate)
    - proposito (por qué existe)
    - contexto (cuándo aplicar)
    - pasos (con Jidoka inline)
    - output (artefacto resultante)

  # El harness es el "runtime"
  execution:
    - input_handling: "$ARGUMENTS"
    - environment_init: "check-prerequisites"
    - progress_tracking: "specs/{feature}/progress.md"
    - jidoka_behavior: "pause-on-verification-fail"
    - handoff_orchestration: "suggest-next-kata"

  # Los skills son las "syscalls"
  skills:
    - retrieve-mvc
    - run-gate
    - check-prerequisites
    - update-agent-context
```

### Jidoka (Stop and Fix)

Cada paso en las katas implementa el patrón Jidoka:

```markdown
### Paso N: [Verbo en infinitivo]

[Descripción de qué hacer]

**Verificación:** [Criterio observable de éxito]

> **Si no puedes continuar:** [Causa] → [Resolución]
```

**Principio**: Parar en defectos inmediatamente, no propagar errores. El Orquestador decide cómo resolver antes de continuar.

---

## 5. Data Store (.raise/)

### Estructura de Directorios

```
.raise/
├── context/                        # Sabiduría (reference material)
│   ├── constitution.md             # Principios fundamentales
│   ├── glossary.md                 # Terminología canónica (v2.3)
│   ├── philosophy.md               # Filosofía de aprendizaje
│   ├── work-cycles.md              # Definición de ciclos de trabajo
│   ├── compliance.md               # Seguridad y compliance
│   └── patterns/                   # Patrones de referencia
│
├── katas/                          # Procesos SDLC por Work Cycle
│   ├── project/                    # Work Cycle: Proyecto
│   │   ├── discovery.md
│   │   ├── vision.md
│   │   ├── design.md
│   │   └── backlog.md
│   │
│   ├── feature/                    # Work Cycle: Feature
│   │   ├── stories.md
│   │   ├── plan.md
│   │   ├── implement.md
│   │   └── review.md
│   │
│   ├── setup/                      # Work Cycle: Onboarding
│   │   ├── analyze.md
│   │   └── ecosystem.md
│   │
│   └── improve/                    # Work Cycle: Mejora Continua
│       ├── retrospective.md
│       └── evolve-kata.md
│
├── skills/                         # Operaciones atómicas (plano)
│   ├── retrieve-mvc.yaml
│   ├── run-gate.yaml
│   ├── check-compliance.yaml
│   ├── explain-rule.yaml
│   ├── generate-rules.yaml
│   └── edit-rule.yaml
│
├── gates/                          # Criterios de validación
│   ├── gate-discovery.md
│   ├── gate-vision.md
│   ├── gate-design.md
│   ├── gate-plan.md
│   └── gate-code.md
│
├── templates/                      # Scaffolds para artefactos
│   ├── project_requirements.md
│   ├── solution_vision.md
│   ├── tech_design.md
│   └── ...
│
├── harness/                        # Configuración del Kata Harness
│   ├── config.yaml                 # Comportamiento del harness
│   └── dojo-overrides/             # Personalizaciones por equipo
│
└── rules/                          # Guardrails extraídos del código
    ├── naming/
    │   └── ts-service-suffix.yaml
    ├── architecture/
    │   └── ts-no-direct-db.yaml
    └── graph.yaml                  # Grafo de relaciones
```

### Principios de Diseño del Data Store

| Principio | Implementación |
|-----------|----------------|
| **Portable** | YAML + Markdown, sin dependencias |
| **Git-friendly** | Diffable, mergeable, versionable |
| **Human-editable** | Formato legible, comentarios permitidos |
| **Machine-parseable** | JSON Schema para validación |
| **Governance as Code** | Todo versionado en Git |

---

## 6. Principios Core

### 6.1 Heutagogía (Aprendizaje Auto-Dirigido)

El Orquestador **dirige su propio proceso** de aprendizaje. El framework facilita proporcionando:
- **Contexto** (constitution, patterns, guardrails)
- **El "por qué"** (intent en cada guardrail, propósito en cada kata)
- **Recursos** (templates, examples, references)

El framework **no enseña ni dicta** el camino.

### 6.2 Jidoka (Parar en Defectos)

Si se detecta incoherencia o violación de principios: **STOP**.

```mermaid
flowchart LR
    D["Detectar"] --> P["Parar"]
    P --> C["Corregir"]
    C --> CO["Continuar"]

    style D fill:#ffcdd2
    style P fill:#ffecb3
    style C fill:#c8e6c9
    style CO fill:#bbdefb
```

No continuar acumulando errores. Cada paso tiene verificación explícita.

### 6.3 Facts Not Gaps

Los guardrails describen **"lo que ES"**, no evalúan contra estándares externos.

| ✅ Lo que RaiSE hace | ❌ Lo que RaiSE NO hace |
|---------------------|------------------------|
| "95% usa camelCase" | "Viola principio SOLID" |
| Mide consistencia interna | Impone Clean Architecture |
| Identifica inconsistencias | Prescribe refactorizaciones |

### 6.4 Governance as Code

Todo lo que no está en Git, no existe oficialmente.
- Guardrails son archivos YAML versionados
- Decisiones arquitectónicas son ADRs
- Katas son documentos Markdown
- La Constitution es un documento versionado

### 6.5 Lean: Simplicidad sobre Completitud

- Preferir documentación concisa que cubra 80% de casos
- Evitar abstracciones prematuras
- YAGNI aplicado a la ontología misma
- 3 conceptos (Context/Kata/Skill) vs 10+ anteriores

---

## 7. Minimum Viable Context (MVC)

El **MVC** es el output del skill `retrieve-mvc`: exactamente las reglas necesarias para una tarea — ni más, ni menos.

### Estructura del MVC

```yaml
version: "1.0"
deterministic: true  # mismo input siempre produce este output

query:
  task: "implement user authentication service"
  scope: "src/services/"
  min_confidence: 0.80

primary_rules:        # Directly applicable (full content)
  - id: ts-service-suffix
    confidence: 0.92
    enforcement: strong
    title: "Service classes must end with 'Service' suffix"
    description: |
      All classes in src/services/ must follow naming pattern: {Name}Service.
    examples:
      positive:
        - code: "export class AuthService { ... }"
      negative:
        - code: "export class AuthHandler { ... }"
          fix: "Rename to AuthService"

context_rules:        # Related rules (summaries only)
  - id: ts-repository-suffix
    confidence: 0.95
    relation: "ts-service-suffix typically uses repositories"
    summary: "Repository classes end with 'Repository' suffix"

warnings:             # Conflicts, deprecations, low-confidence
  - type: low_confidence
    rule_id: ts-jwt-pattern
    confidence: 0.72
    message: "JWT pattern has 72% adoption. Consider but don't enforce."

metadata:
  total_rules_evaluated: 47
  estimated_tokens: 1847
```

### Principios del MVC

| Principio | Implementación |
|-----------|----------------|
| **Determinista** | Mismo input = mismo output (100%) |
| **Token-efficient** | <4K tokens por default |
| **Relevante** | Solo reglas que aplican al scope |
| **Explicable** | Cada regla incluida tiene razón explícita |

---

## 8. Validación: Gates

Los **Gates** son criterios de validación consumidos por el skill `run-gate`.

### Gate por Work Cycle

| Work Cycle | Gate | Propósito |
|------------|------|-----------|
| project/ | gate-discovery | Validar PRD completeness |
| project/ | gate-vision | Validar Solution Vision |
| project/ | gate-design | Validar Technical Design |
| feature/ | gate-plan | Validar Implementation Plan |
| feature/ | gate-code | Validar código vs guardrails |

### Estructura de un Gate

```markdown
---
id: gate-vision
work_cycle: project
titulo: "Gate-Vision: Validación de Solution Vision"
blocking: true
version: 2.0.0
---

# Gate-Vision

## Propósito
[Por qué existe este gate]

## Criterios Obligatorios (Must Pass)
| # | Criterio | Verificación |
|---|----------|--------------|
| 1 | ... | ... |

## Criterios Recomendados (Should Pass)
| # | Criterio | Verificación |
|---|----------|--------------|
| 8 | ... | ... |

## Proceso de Validación
[Pasos para ejecutar el gate]

## Escalation Triggers
[Cuándo escalar]
```

---

## 9. Estrategia de Producto: Open Core

### Modelo de Negocio

```mermaid
graph LR
    subgraph OPEN["OPEN CORE (Free)"]
        O1["Context layer"]
        O2["All katas"]
        O3["All skills"]
        O4["Kata Harness"]
        O5["Templates + Gates"]
    end

    subgraph LICENSED["LICENSED (Paid)"]
        L1["Deterministic extraction"]
        L2["Observability dashboard"]
        L3["CI/CD integrations"]
        L4["Multi-repo governance"]
        L5["Enterprise support"]
    end

    OPEN -.->|"Mismo formato de output"| LICENSED

    style OPEN fill:#e8f5e9
    style LICENSED fill:#fff3e0
```

### Flywheel de Adopción

```mermaid
flowchart TD
    A["Orquestador usa RaiSE Open Core (free)"] --> B["Ejecuta katas, usa skills"]
    B --> C["Equipo ve valor en gobernanza estructurada"]
    C --> D["Empresa necesita precisión + observabilidad"]
    D --> E["Upgrade a Licensed"]
    E -.->|"Más usuarios"| A

    style A fill:#e3f2fd
    style E fill:#fff8e1
```

---

## 10. Métricas de Éxito

### Métricas de Producto

| Métrica | Target | Descripción |
|---------|--------|-------------|
| Code review pass rate | >80% | Código con MVC pasa review |
| Guardrail precision | >85% | Guardrails extraídos son correctos |
| MVC retrieval latency | <200ms | Tiempo de respuesta |
| Kata completion rate | >90% | Katas completadas sin abandono |

### Métricas de Adopción

| Métrica | Target |
|---------|--------|
| Proyectos con setup/ ejecutado | 10+ (Open Core) |
| Guardrails extraídos total | 500+ |
| Upgrade rate a Licensed | 10% |

---

## 11. Terminología Canónica (v2.3)

| Término | Definición |
|---------|------------|
| **Context** | Sabiduría que informa pero no se ejecuta: constitution, patterns, guardrails, golden data. |
| **Kata** | Proceso SDLC que los equipos practican y adaptan. Organizadas por Work Cycle. |
| **Work Cycle** | Contexto operacional que agrupa katas: `project`, `feature`, `setup`, `improve`. |
| **Skill** | Operación atómica con inputs/outputs definidos. Invocable por katas o directamente. |
| **Guardrail** | Convención o restricción extraída del código, con confidence score. |
| **Dojo** | Equipo que adapta las katas base a su contexto específico. |
| **Kata Harness** | Capability de plataforma: motor de ejecución que interpreta katas e invoca skills. |
| **Gate** | Criterios de validación (data) consumidos por el skill `run-gate`. |
| **MVC** | Minimum Viable Context: conjunto mínimo de guardrails para una tarea. |
| **Orquestador** | Humano que dirige al agente LLM usando katas y skills. |

### Terminología Deprecated (v2.2 y anteriores)

| Evitar | Usar en su lugar | Razón |
|--------|------------------|-------|
| SAR | setup/ katas | Componente eliminado |
| CTX | context/ skills | Componente eliminado |
| Regla | Guardrail | Claridad semántica |
| Command | Kata o Skill | Separación de concerns |
| L0/L1/L2/L3 | Work Cycles | Niveles de abstracción eliminados |
| principios/flujo/patrón/técnica | Context/Kata/Skill | Simplificación ontológica |
| spec-kit harness | Kata Harness | Platform capability naming |

---

## 12. Roadmap de Alto Nivel

### Fase 1: Foundation (Current)

- [x] ADR-008: Context/Kata/Skill ontology
- [x] Glossary v2.3
- [x] Constitution migration
- [x] Work Cycles formalization
- [x] Vision v2.3 (este documento)
- [ ] Kata Harness specification

### Fase 2: Implementation

- [ ] Migrate katas to `.raise/katas/{work_cycle}/`
- [ ] Create skill YAML files in `.raise/skills/`
- [ ] Implement Kata Harness runtime
- [ ] Migrate gates to v2.0 format

### Fase 3: Validation

- [ ] Test katas in real projects
- [ ] Validate MVC retrieval performance
- [ ] Collect feedback from Dojos
- [ ] Refine based on usage patterns

### Fase 4: Launch

- [ ] Documentation complete
- [ ] Examples for each Work Cycle
- [ ] Open Core release

---

## 13. Referencias

### ADRs

| ADR | Decisión |
|-----|----------|
| [ADR-007](./adrs/adr-007-terminology-simplification.md) | Simplificación terminológica (SAR/CTX → setup/context) |
| [ADR-008](./adrs/adr-008-kata-skill-context-simplification.md) | Context/Kata/Skill ontology |
| [ADR-001](./adrs/adr-001-sar-pipeline-phases.md) | Pipeline de 4 fases (histórico) |
| [ADR-002](./adrs/adr-002-deterministic-context-delivery.md) | MVC siempre determinista |
| [ADR-003](./adrs/adr-003-yaml-rule-format.md) | YAML para guardrails |
| [ADR-004](./adrs/adr-004-separate-graph.md) | Grafo separado de guardrails |
| [ADR-005](./adrs/adr-005-confidence-adoption-rate.md) | Confidence por adoption rate |
| [ADR-006](./adrs/adr-006-mvc-summaries.md) | MVC con summaries |

### Context Documents

- [Constitution](.raise/context/constitution.md)
- [Glossary v2.3](.raise/context/glossary.md)
- [Work Cycles](.raise/context/work-cycles.md)
- [Philosophy](.raise/context/philosophy.md)
- [Compliance](.raise/context/compliance.md)

### Research

- [Command/Kata/Skill Ontology Research](../main/research/outputs/command-kata-skill-ontology-report.md)
- [Kata-Command Discrepancy Analysis](../main/research/outputs/kata-command-discrepancy-analysis.md)
- [Corpus Audit v2.3](../main/research/outputs/corpus-audit-v2.3.md)

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 2.0.0 | 2026-01-28 | Framework completo con 3 capas, SAR/CTX components |
| 2.2.0 | 2026-01-29 | 7 command categories, Lean Spec, MVC |
| **2.3.0** | **2026-01-29** | **Context/Kata/Skill ontology, Work Cycles, Kata Harness** |

---

*RaiSE Framework v2.3: Gobernanza explícita para desarrollo AI-assisted.*
*Context informa. Kata guía. Skill ejecuta.*
