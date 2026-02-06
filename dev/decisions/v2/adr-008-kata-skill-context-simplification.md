---
id: "ADR-008"
title: "Simplificación Ontológica: Context/Kata/Skill como Modelo Unificado"
date: "2026-01-29"
status: "Accepted"
supersedes: ["ADR-011 (partial)"]
related_to: ["ADR-007", "VIS-RAISE-002", "glossary-v2.2"]
---

# ADR-008: Simplificación Ontológica - Context/Kata/Skill

## Contexto

### Problema Identificado

RaiSE v2.1 acumuló complejidad ontológica a través de múltiples iteraciones:

1. **4 niveles de Kata** (principios, flujo, patrón, técnica) con fronteras difusas
2. **7 categorías de comandos** (setup, context, project, feature, validate, improve, tools)
3. **Múltiples conceptos superpuestos**: comandos, katas, gates, templates, golden data

Esta complejidad genera:

- **Carga cognitiva alta**: Usuarios deben entender 10+ conceptos antes de ser productivos
- **Fronteras difusas**: ¿Es "brownfield analysis" un patrón o un flujo? ¿Es un comando o una kata?
- **Mezcla de concerns**: Los comandos actuales entrelazan conocimiento cultural con lógica de ejecución
- **Dificultad de adaptación**: Los equipos (Dojos) no tienen un punto claro de personalización

### Análisis de los Niveles de Kata Actuales

| Nivel | Propósito Original | Problema |
|-------|-------------------|----------|
| **principios** | Meta-proceso (POR QUÉ) | No se "ejecutan" - son referencias. Pertenecen a Context. |
| **flujo** | Fases SDLC (CÓMO FLUYE) | Estos SÍ son procesos. Son las verdaderas Katas. |
| **patrón** | Estructuras reutilizables | Frontera difusa con flujo. Algunos son Context, otros Katas. |
| **técnica** | Técnicas específicas | Si es lo suficientemente pequeño, es un Skill. |

### La Metáfora del Niwashi (庭師)

Un Niwashi (jardinero japonés tradicional) posee:

- **Sabiduría** (cuándo podar, por qué ciertas formas): Esto es **Context**
- **Práctica** (ciclo de cuidado estacional, flujo de trabajo): Esto es **Kata**
- **Técnica** (cortes específicos, manejo de herramientas): Esto es **Skill**

El Niwashi transmite sabiduría cultural adaptable a cada jardín. Las Katas son el vehículo de esa transmisión, adaptables por cada Dojo (equipo).

## Decisión

### Eliminar los 4 niveles de Kata. Adoptar modelo de 3 capas: Context / Kata / Skill

```
┌──────────────────────────────────────────────────────────────────┐
│  CONTEXT (Capa de Sabiduría)                                     │
│  ═══════════════════════════                                     │
│  Todo lo que INFORMA pero no se EJECUTA:                         │
│  • Constitution (principios, filosofía)                          │
│  • Patterns (estructuras de referencia, anti-patrones)           │
│  • Rules/Guardrails (convenciones, restricciones)                │
│  • Golden Data (hechos del proyecto, conocimiento del ecosistema)│
│  • Templates (scaffolds, no procesos)                            │
│                                                                  │
│  Entregado por: context/ skills (get, check, explain)            │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ Informa
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  KATA (Capa de Práctica) - Organizadas por Work Cycle            │
│  ═════════════════════════════════════════════════════           │
│  Lo que los equipos PRACTICAN y ADAPTAN:                         │
│                                                                  │
│  katas/project/    (Work Cycle: Project - 1x por épica)          │
│    • discovery.md    - Creación del PRD                          │
│    • vision.md       - Solution Vision                           │
│    • design.md       - Technical Design                          │
│    • backlog.md      - Creación de backlog                       │
│                                                                  │
│  katas/story/    (Work Cycle: Feature - Nx por feature)        │
│    • stories.md      - Generación de historias                   │
│    • plan.md         - Planificación de implementación           │
│    • implement.md    - Flujo de codificación                     │
│    • review.md       - Retrospectiva y mejora                    │
│                                                                  │
│  katas/setup/      (Work Cycle: Onboarding - 1x brownfield)      │
│    • analyze.md      - Análisis de codebase                      │
│    • ecosystem.md    - Mapeo de ecosistema                       │
│                                                                  │
│  katas/improve/    (Work Cycle: Continuous)                      │
│    • retrospective.md - Retrospectiva                            │
│    • evolve-kata.md   - Evolución de katas                       │
│                                                                  │
│  Adaptable por: Cada Dojo (personalización del equipo)           │
│  Ejecutado por: Kata Harness                                     │
│  Invocable como: /project/discovery, /feature/implement, etc.    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ Invoca
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  SKILL (Capa de Acción) - Estructura plana                       │
│  ══════════════════════════════════════════                      │
│  Operaciones atómicas con inputs/outputs claros:                 │
│  • retrieve-mvc (obtener contexto para tarea)                    │
│  • run-gate (validar contra criterios)                           │
│  • check-compliance (verificar código contra reglas)             │
│  • generate-rules (extraer patrones del código)                  │
│  • edit-rule (modificar una regla específica)                    │
│                                                                  │
│  Invocable por: Katas, Harness, o directamente                   │
│  Nota: Skills son planos porque son atómicos - el nombre         │
│        lleva todo el significado semántico necesario.            │
└──────────────────────────────────────────────────────────────────┘
```

### Jerarquía de Katas por Work Cycle (No por Nivel de Abstracción)

**Distinción crítica:**

| Concepto | Qué Es | Decisión |
|----------|--------|----------|
| **Kata Levels** (principios/flujo/patrón/técnica) | Jerarquía de abstracción (meta → concreto) | ELIMINAR - fronteras difusas, carga cognitiva |
| **Kata Directories** (project/feature/setup/improve) | Agrupación semántica por contexto de trabajo | MANTENER - indica CUÁNDO usar cada kata |

La jerarquía de directorios no representa niveles de abstracción, sino **ciclos de trabajo**:

| Directorio | Work Cycle | Frecuencia | Pregunta que Responde |
|------------|------------|------------|----------------------|
| `project/` | Proyecto | 1x por épica | "¿Qué hago al iniciar un proyecto?" |
| `feature/` | Feature | Nx por feature | "¿Qué hago para implementar un feature?" |
| `setup/` | Onboarding | 1x brownfield | "¿Qué hago al entrar a un repo existente?" |
| `improve/` | Mejora Continua | Ongoing | "¿Qué hago para mejorar?" |

Esta estructura habilita slash commands semánticos: `/project/discovery`, `/feature/implement`.

### Kata Harness (Capability)

Introducir el **Kata Harness** como capability de plataforma que generaliza la contribución de spec-kit al control de flujo LLM.

**Nota terminológica:** El término "harness" en AI tiene dos contextos distintos:
- **Agent Harness** (ejecución): Infraestructura que envuelve un LLM para gestionar tareas de larga duración, invocación de herramientas, y gestión de contexto. *RaiSE usa este significado.*
- **Evaluation Harness** (testing): Framework de benchmarking para evaluar LLMs (e.g., EleutherAI lm-evaluation-harness).

**Alineamiento industria:** El Kata Harness se alinea con LangChain DeepAgents y Anthropic Claude Agent SDK (2024-2026).

```yaml
# Conceptual: .raise/harness/config.yaml
kata_harness:
  version: "1.0"

  # La kata es el "programa"
  kata_schema:
    - frontmatter (id, titulo, fase, prerequisites, template, gate)
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

### Estructura de Directorios Propuesta

```
.raise/
├── katas/                         # Procesos SDLC por Work Cycle
│   ├── project/                   # Work Cycle: Proyecto (1x por épica)
│   │   ├── discovery.md           # PRD creation
│   │   ├── vision.md              # Solution Vision
│   │   ├── design.md              # Technical Design
│   │   └── backlog.md             # Backlog creation
│   │
│   ├── feature/                   # Work Cycle: Feature (Nx por feature)
│   │   ├── stories.md             # Story generation
│   │   ├── plan.md                # Implementation planning
│   │   ├── implement.md           # Development workflow
│   │   └── review.md              # Review & retrospective
│   │
│   ├── setup/                     # Work Cycle: Onboarding (1x brownfield)
│   │   ├── analyze.md             # Codebase analysis
│   │   └── ecosystem.md           # Ecosystem mapping
│   │
│   └── improve/                   # Work Cycle: Mejora Continua
│       ├── retrospective.md       # Team retrospective
│       └── evolve-kata.md         # Kata evolution
│
├── skills/                        # Operaciones atómicas (plano)
│   ├── retrieve-mvc.yaml
│   ├── run-gate.yaml
│   ├── check-compliance.yaml
│   ├── generate-rules.yaml
│   └── edit-rule.yaml
│
├── harness/                       # Configuración del Kata Harness
│   ├── config.yaml                # Comportamiento del harness
│   └── dojo-overrides/            # Personalizaciones por equipo
│
├── context/                       # Sabiduría (reference material)
│   ├── constitution.md
│   ├── patterns/
│   ├── philosophy/
│   └── golden-data/
│
├── gates/                         # Criterios de validación (data)
│   ├── gate-discovery.md
│   ├── gate-vision.md
│   └── ...
│
└── templates/                     # Scaffolds para artefactos
    ├── project_requirements.md
    ├── solution_vision.md
    └── ...
```

**Nota sobre estructura plana de Skills:** Los skills no necesitan jerarquía porque son operaciones atómicas - el nombre del skill (`retrieve-mvc`, `run-gate`) contiene todo el significado semántico necesario. No hay pregunta de "¿cuándo uso este skill vs aquel?" como sí la hay con las katas.

### Migración de Artefactos Actuales

#### Desde Katas Antiguas (niveles L0-L3)

| Ubicación Actual | Tipo Actual | Nueva Ubicación | Nuevo Tipo |
|------------------|-------------|-----------------|------------|
| `katas/principios/meta-kata.md` | Kata L0 | `context/philosophy/meta-kata.md` | Context |
| `katas/principios/execution-protocol.md` | Kata L0 | `harness/executor-config.yaml` | Harness Config |
| `katas/flujo/discovery.md` | Kata L1 | `katas/project/discovery.md` | Kata |
| `katas/flujo/solution-vision.md` | Kata L1 | `katas/project/vision.md` | Kata |
| `katas/flujo/tech-design.md` | Kata L1 | `katas/project/design.md` | Kata |
| `katas/flujo/backlog-creation.md` | Kata L1 | `katas/project/backlog.md` | Kata |
| `katas/flujo/implementation-plan.md` | Kata L1 | `katas/story/plan.md` | Kata |
| `katas/flujo/development.md` | Kata L1 | `katas/story/implement.md` | Kata |
| `katas/patron/code-analysis.md` | Kata L2 | `katas/setup/analyze.md` | Kata |
| `katas/patron/ecosystem-discovery.md` | Kata L2 | `katas/setup/ecosystem.md` | Kata |
| `katas/patron/tech-design-stack.md` | Kata L2 | `context/patterns/tech-design-stack.md` | Context |
| `katas/patron/dependency-validation.md` | Kata L2 | `context/patterns/dependency-validation.md` | Context |

#### Desde Comandos v2 (preservando el trabajo realizado)

| Ubicación Actual | Tipo Actual | Nueva Ubicación | Nuevo Tipo |
|------------------|-------------|-----------------|------------|
| `commands/project/create-prd.md` | Command | `katas/project/discovery.md` | Kata |
| `commands/project/define-vision.md` | Command | `katas/project/vision.md` | Kata |
| `commands/project/design-architecture.md` | Command | `katas/project/design.md` | Kata |
| `commands/project/create-backlog.md` | Command | `katas/project/backlog.md` | Kata |
| `commands/project/map-ecosystem.md` | Command | `katas/setup/ecosystem.md` | Kata |
| `commands/project/estimate-effort.md` | Command | `katas/project/estimate.md` | Kata |
| `commands/feature/generate-stories.md` | Command | `katas/story/stories.md` | Kata |
| `commands/feature/plan-implementation.md` | Command | `katas/story/plan.md` | Kata |
| `commands/feature/implement.md` | Command | `katas/story/implement.md` | Kata |
| `commands/feature/design-feature.md` | Command | `katas/story/design.md` | Kata |
| `commands/setup/analyze-codebase.md` | Command | `katas/setup/analyze.md` | Kata |
| `commands/setup/generate-rules.md` | Command | `skills/generate-rules.yaml` | Skill |
| `commands/setup/edit-rule.md` | Command | `skills/edit-rule.yaml` | Skill |
| `commands/context/get.md` | Command | `skills/retrieve-mvc.yaml` | Skill |
| `commands/context/check.md` | Command | `skills/check-compliance.yaml` | Skill |
| `commands/context/explain.md` | Command | `skills/explain-rule.yaml` | Skill |
| `commands/validate/*.md` | Command | `skills/run-gate.yaml` | Skill (parametrizado) |
| `commands/tools/generate-contract.md` | Command | `skills/generate-contract.yaml` | Skill |

**Nota sobre fusión**: Los comandos v2 tienen buena estructura de pasos y Jidoka inline. Al migrar a katas, se preserva el contenido de proceso y se extrae la lógica de ejecución (AI Guidance, High-Signaling, handoffs) al Harness.

### Schema de Kata (Simplificado)

```yaml
---
# IDENTIFICACIÓN
id: discovery                    # Nombre único de la kata
titulo: "Discovery: Creación del PRD"
work_cycle: project              # project | feature | setup | improve

# CONTEXTO DE TRABAJO
frequency: once-per-epic         # once-per-epic | per-story | once-brownfield | continuous
fase_metodologia: 1              # Fase SDLC (1-7, opcional)

# RELACIONES
prerequisites: []                # Otras katas requeridas (format: work_cycle/kata_id)
template: templates/project_requirements.md
gate: gates/gate-discovery.md
next_kata: project/vision        # Sugerencia de siguiente kata

# ADAPTABILIDAD
adaptable: true                  # Puede ser personalizada por Dojo
shuhari:
  shu: "Seguir todos los pasos exactamente"
  ha: "Combinar pasos 4-5 si las métricas son conocidas"
  ri: "Crear kata de Discovery específica del dominio"

version: 1.0.0
---

# Discovery: Creación del PRD

## Propósito
[1-2 párrafos explicando POR QUÉ existe esta kata]

## Contexto
**Cuándo usar:** [Criterios de aplicabilidad]
**Inputs requeridos:** [Lista]
**Output:** [Descripción del artefacto]

## Pasos

### Paso 1: [Verbo en infinitivo]
[Descripción de qué hacer]

**Verificación:** [Criterio observable de éxito]
> **Si no puedes continuar:** [Causa] → [Resolución]

[... más pasos ...]

## Output
- **Artefacto:** [Nombre]
- **Ubicación:** `specs/main/[nombre].md`
- **Siguiente kata:** [Referencia con format work_cycle/kata_id]

## Referencias
- [Links a documentos relacionados]
```

**Campos clave del schema:**

| Campo | Propósito | Valores |
|-------|-----------|---------|
| `work_cycle` | Directorio padre, indica contexto de trabajo | `project`, `feature`, `setup`, `improve` |
| `frequency` | Cuántas veces se ejecuta típicamente | `once-per-epic`, `per-story`, `once-brownfield`, `continuous` |
| `next_kata` | Sugiere siguiente paso en el flujo | `work_cycle/kata_id` (ej: `project/vision`) |
| `shuhari` | Guía de adaptación por nivel de maestría | Objeto con claves `shu`, `ha`, `ri` |

### Schema de Skill

```yaml
---
id: retrieve-mvc
name: "Retrieve Minimum Viable Context"
type: skill
version: 1.0.0

description: |
  Obtiene reglas y convenciones relevantes para un scope de tarea específico.

# Contrato
input:
  task:
    type: string
    required: true
    description: "Descripción de la tarea a realizar"
  scope:
    type: string
    default: "."
    description: "Path o patrón de archivos"
  min_confidence:
    type: number
    default: 0.80
    description: "Umbral mínimo de confianza"

output:
  type: object
  properties:
    primary_rules:
      type: array
      items: { id: string, name: string, content: string }
    context_rules:
      type: array
      items: { id: string, name: string, summary: string }
    warnings:
      type: array
      items: { type: string, message: string, affected_rules: array }

# Implementación
implementation:
  type: inline  # o "mcp-tool", "bash-script"
  steps:
    - "Escanear .cursor/rules/"
    - "Match globs contra scope"
    - "Clasificar en primary/context"
    - "Detectar conflictos"
    - "Retornar MVC estructurado"
---
```

## Consecuencias

### Positivas

| Aspecto | Beneficio |
|---------|-----------|
| **Carga cognitiva** | 3 conceptos vs 10+ conceptos anteriores |
| **Modelo mental claro** | Context=SABER, Kata=HACER, Skill=USAR |
| **Adaptabilidad Dojo** | Punto claro de personalización (katas/) |
| **Separación de concerns** | Conocimiento cultural separado de lógica de ejecución |
| **Metáfora Niwashi** | Alineación con sabiduría, práctica, técnica |
| **Preserva trabajo v2** | Los comandos actuales informan el diseño de katas |

### Negativas

| Aspecto | Impacto | Mitigación |
|---------|---------|------------|
| **Migración requerida** | Reestructurar archivos existentes | Plan de migración incremental |
| **Documentación existente** | Referencias a niveles L0-L3, SAR, CTX obsoletas | Notas de migración + aliases |
| **Curva de aprendizaje** | Usuarios existentes deben re-aprender | Guía de migración clara |
| **Kata Harness** | Nueva capability a construir | Basado en spec-kit existente |

### Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Over-simplificación | Media | Alto | Mantener extensibilidad para técnicas futuras |
| Pérdida de matices | Baja | Medio | Context absorbe patrones con metadatos apropiados |
| Resistencia al cambio | Baja | Bajo | ADRs anteriores como contexto histórico |

## Alternativas Consideradas

### A1: Mantener 4 niveles pero renombrar
**Rechazado**: El problema no es el nombre, es la complejidad estructural. Renombrar no reduce carga cognitiva.

### A2: Colapsar a 2 niveles (Kata/Skill)
**Rechazado**: Pierde la distinción entre conocimiento de referencia (Context) y procesos ejecutables (Kata).

### A3: Mantener categorías de comandos como están
**Rechazado**: Las categorías operacionales (project/, setup/) no alinean con la ontología de conocimiento abstracto (principios/flujo/patrón/técnica). Sin embargo, las categorías operacionales SÍ son valiosas como estructura de directorios para katas.

### A4: Modelo de 4 capas (Context/Kata/Skill/Gate)
**Considerado pero simplificado**: Gates son data consumida por el skill `run-gate`, no una capa separada.

### A5: Estructura plana de katas (sin directorios)
**Rechazado**: Una estructura `katas/{discovery,vision,design,...}.md` pierde el significado semántico de CUÁNDO usar cada kata. Los directorios por Work Cycle (`project/`, `feature/`, `setup/`, `improve/`) responden la pregunta "¿qué hago cuando estoy en este contexto de trabajo?" y habilitan slash commands claros como `/project/discovery`.

**Distinción crítica**: Eliminamos los niveles de abstracción (principios/flujo/patrón/técnica) pero mantenemos la jerarquía por contexto de trabajo (project/feature/setup/improve). Son dimensiones ortogonales.

## Plan de Implementación

### Fase 1: Definir Schemas (Este ADR)
- [x] Definir schema de Kata con work_cycle
- [x] Definir schema de Skill
- [x] Definir estructura de Context
- [x] Definir jerarquía por Work Cycle (project/feature/setup/improve)
- [x] Revisar y aprobar ADR

### Fase 2: Crear Estructura Base
- [ ] Crear directorios `.raise/katas/{project,feature,setup,improve}/`
- [ ] Crear directorio `.raise/skills/`
- [ ] Crear directorios `.raise/{harness,context}/`
- [ ] Migrar `commands/project/*.md` → `katas/project/*.md`
- [ ] Migrar `commands/feature/*.md` → `katas/story/*.md`
- [ ] Migrar `commands/setup/*.md` → `katas/setup/*.md` + `skills/*.yaml`
- [ ] Migrar `commands/context/*.md` → `skills/*.yaml`
- [ ] Migrar `commands/validate/*.md` → `skills/run-gate.yaml`
- [ ] Migrar `katas/principios/` → `context/philosophy/`

### Fase 3: Implementar Kata Harness
- [ ] Definir `harness/config.yaml`
- [ ] Extraer lógica común de comandos actuales (AI Guidance, High-Signaling, handoffs)
- [ ] Implementar interpretación de katas
- [ ] Implementar invocación de skills

### Fase 4: Validación y Documentación
- [ ] Actualizar glossary v2.3
- [ ] Actualizar vision.md v2.3
- [ ] Crear guía de migración
- [ ] Archivar estructura anterior (commands/, katas antiguas)

## Glosario de Términos (Preview v2.3)

| Término | Definición |
|---------|------------|
| **Context** | Sabiduría que informa pero no se ejecuta: constitution, patterns, rules, golden data. |
| **Kata** | Proceso SDLC que los equipos practican y adaptan. Organizadas por Work Cycle. |
| **Work Cycle** | Contexto operacional que agrupa katas: `project`, `feature`, `setup`, `improve`. |
| **Skill** | Operación atómica con inputs/outputs definidos. Invocable por katas o directamente. |
| **Dojo** | Equipo que adapta las katas base a su contexto específico. |
| **Kata Harness** | Capability de plataforma: motor de ejecución que interpreta katas e invoca skills. Alineado con "Agent Harness" (no "Evaluation Harness"). |
| **Gate** | Criterios de validación (data) consumidos por el skill `run-gate`. |

## Anti-Términos (Deprecated)

| Evitar | Usar en su lugar | Razón |
|--------|------------------|-------|
| Kata Level (L0/L1/L2/L3) | Work Cycle (project/feature/setup/improve) | Niveles de abstracción confusos; Work Cycles son contextuales |
| principios/flujo/patrón/técnica | Context + Kata + Skill | Simplificación ontológica |
| Command | Kata o Skill | Commands mezclaban proceso con ejecución |

## Referencias

- **Investigación**: `specs/main/research/outputs/command-kata-skill-ontology-report.md`
- **Análisis de discrepancias**: `specs/main/research/outputs/kata-command-discrepancy-analysis.md`
- **ADR-007**: Simplificación terminológica (SAR/CTX → setup/context commands)
- **ADR-011**: Hybrid Kata-Template-Gate model (superseded parcialmente)
- **Toyota Kata**: Mike Rother - Improvement Kata / Coaching Kata
- **Cognitive Load Theory**: Sweller, 1988

---

*Aceptado: 2026-01-29*
