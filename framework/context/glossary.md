# RaiSE Glossary
## Vocabulario Canónico del Framework

**Versión:** 2.4.0
**Fecha:** 30 de Enero, 2026
**Propósito:** Definiciones canónicas de términos usados en el ecosistema RaiSE.

> **Nota de versión 2.1:** Actualización de niveles de Kata (L0-L3 → Principios/Flujo/Patrón/Técnica), adición de ShuHaRi como lente del Orquestador, y Jidoka inline.

> **Nota de versión 2.2:** Simplificación terminológica - se eliminan nombres de componentes (SAR, CTX) en favor de categorías de comandos (setup/, context/).

> **Nota de versión 2.3:** Simplificación ontológica ADR-008 — modelo de 3 capas (Context/Kata/Skill), eliminación de niveles de kata, introducción de Work Cycles como organización, y Kata Harness como capability de plataforma.

> **Nota de versión 2.4:** Jerarquía de tres niveles ADR-010 — Solution Level (Business Case, Solution Vision, Governance), Project Level (PRD, Project Vision, Tech Design), Codebase Level. "Solution Vision" renombrada a "Project Vision" a nivel proyecto.

---

## Términos Core de RaiSE

### Agent (Agente)
Sistema de IA que ejecuta tareas de desarrollo de software bajo la orquestación de un humano. Ejemplos: GitHub Copilot, Claude Code, Cursor, Windsurf.

> **Principio relacionado:** Los agentes son ejecutores, no decisores autónomos. Ver [00-constitution.md](./00-constitution.md) §1.

### Command Category (Categoría de Comando)
**[NUEVO v2.2]** Agrupación semántica de comandos RaiSE según su propósito. Las 7 categorías son:

| Categoría | Propósito | Frecuencia |
|-----------|-----------|------------|
| `setup/` | Análisis de codebase, extracción de reglas | 1x brownfield |
| `context/` | Entrega de contexto mínimo viable a agentes | On-demand |
| `project/` | Flujo de proyecto (PRD → Backlog) | 1x proyecto |
| `feature/` | Flujo de feature (Design → Implement) | Nx feature |
| `validate/` | Gates de validación bajo demanda | On-demand |
| `improve/` | Mejora continua (katas, retrospectivas) | Continuo |
| `tools/` | Utilidades (export, contratos) | Ad-hoc |

> **Nota de diseño v2.2:** Las categorías reemplazan los nombres de componentes (SAR, CTX) para reducir carga cognitiva. Los comandos SON la implementación, no hay capa de abstracción adicional.

### Context (Capa de Sabiduría) [NUEVO v2.3]
Primera capa del modelo ontológico RaiSE. Todo lo que INFORMA pero no se EJECUTA:
- Constitution (principios, filosofía)
- Patterns (estructuras de referencia, anti-patrones)
- Rules/Guardrails (convenciones, restricciones)
- Golden Data (hechos del proyecto, conocimiento del ecosistema)
- Templates (scaffolds, no procesos)

**Metáfora Niwashi:** La sabiduría del jardinero — cuándo podar, por qué ciertas formas.

> Ver ADR-008 para modelo completo Context/Kata/Skill.

### Constitution (Constitución)
Conjunto de principios inmutables que gobiernan todas las decisiones en un proyecto RaiSE. Es el documento de mayor jerarquía y raramente cambia.

**Equivalentes en la industria:**
- **MCP**: Prompts (templates reutilizables)
- **spec-kit**: Constitution (mismo término)
- **Comunidad**: CLAUDE.md, .cursorrules, AGENTS.md

> **Nota**: RaiSE mantiene "Constitution" por su alineamiento con Constitutional AI (Anthropic, 2022) y spec-kit de GitHub.

### context/ (Categoría de Comandos)
**[NUEVO v2.2]** Comandos que entregan Minimum Viable Context (MVC) a agentes LLM.

**Comandos:**
- `/context/get` — Obtener MVC para una tarea específica
- `/context/check` — Verificar compliance de código contra reglas
- `/context/explain` — Explicar una regla específica

**Características:**
- **Input**: Task + Scope + Confidence threshold
- **Output**: MVC (primary_rules, context_rules, warnings)
- **Método**: Determinista (graph traversal, pattern matching)
- **Frecuencia**: On-demand (cada vez que agente necesita contexto)
- **Principio**: Mismo input = mismo output (100% reproducible)

> **Evolución v2.2:** Reemplaza "CTX Component" como terminología. Los comandos son la implementación directa, no hay componente abstracto separado.

### Context Engineering
**[NUEVO v2.0]** Disciplina de diseñar el ambiente informacional completo que un LLM consume para ejecutar tareas. Evolución de "prompt engineering" hacia una práctica arquitectónica.

> Acuñado por Andrej Karpathy (2025): "No es prompt engineering, es **context engineering**—arquitectar todo el ambiente de información en el que opera el LLM."

En RaiSE, Context Engineering se manifiesta en:
- **Constitution**: Principios que enmarcan todas las decisiones
- **Specs**: Contexto estructurado del "qué" construir
- **Golden Data**: Información verificada del proyecto/organización
- **Guardrails**: Restricciones operacionales activas

### Corpus
Colección estructurada de documentos que proporciona contexto a agentes de IA. El corpus es "Golden Data"—información verificada y canónica que alimenta las sesiones de trabajo.

### Escalation Gate
**[NUEVO v2.0]** Punto específico en el flujo donde el agente debe escalar al Orquestrador humano para decisión o aprobación. Subtipo de Validation Gate enfocado en HITL (Human-in-the-Loop).

**Criterios típicos de escalación:**
- Confianza del agente < umbral definido
- Decisión de alto impacto (arquitectura, seguridad)
- Ambigüedad en spec o contexto
- Primer uso de un patrón nuevo

> **Métrica de referencia**: 10-15% de escalación es óptimo (85-90% ejecución autónoma). Fuente: Galileo HITL Framework, 2025.

### Golden Data
Información verificada, estructurada y canónica que alimenta el contexto de agentes. A diferencia de datos genéricos, el Golden Data refleja la realidad específica del proyecto/organización.

### Governance as Code
Principio que establece que políticas, reglas y estándares son artefactos versionados en Git, no documentos estáticos. Lo que no está en el repositorio, no existe.

### Guardrail (antes: Rule)
**[RENOMBRADO v2.0]** Directiva operacional que gobierna el comportamiento del agente o la calidad del código. Definida en Markdown (para humanos), distribuida en JSON (para máquinas).

**Diferencia con Constitution:**
- **Constitution**: Principios filosóficos, inmutables, alto nivel
- **Guardrail**: Reglas operacionales, cambiantes, enforceables

**Equivalentes en la industria:**
- **DSPy**: Assertions
- **LangChain**: Runnable constraints
- **Comunidad enterprise**: Guardrails

> **Nota de migración**: El término "Rule" sigue siendo válido como alias. Los archivos `.mdc` mantienen su formato.

### Heutagogía
Teoría del aprendizaje auto-determinado (del griego *heutos* = "uno mismo" + *agogos* = "guiar"). En RaiSE, significa que el Orquestador diseña su propio proceso de aprendizaje a través de cada interacción con agentes de IA. El sistema "enseña a pescar" en lugar de solo "entregar el pescado".

> Ver [05-learning-philosophy.md](./05-learning-philosophy.md) para desarrollo completo.

### Checkpoint Heutagógico
Momento estructurado de reflexión al finalizar features significativas. Incluye cuatro preguntas: (1) ¿Qué aprendiste? (2) ¿Qué cambiarías del proceso? (3) ¿Hay mejoras para el framework? (4) ¿En qué eres más capaz ahora? Las respuestas alimentan el crecimiento del Orquestador y la evolución del corpus.

### Jidoka

**Interfaz Simple (Stage 0-1)**: Parar si algo falla

Principio de detener el trabajo cuando detectas un problema, en lugar de acumular errores.

**Ejemplo**: Cuando ejecutas `/speckit.plan` y el gate de coherencia falla, el workflow para - no continúa generando tareas sobre una base inconsistente.

---

**Detalle Avanzado (Stage 3)**:

Jidoka (自動化) — Automatización con toque humano.

**Ciclo formal**:
1. **Detectar**: Identificar el defecto o anomalía
2. **Parar**: Detener el proceso inmediatamente
3. **Corregir**: Resolver la causa raíz
4. **Continuar**: Reanudar con mejora preventiva

**Contexto histórico**: Originado en telares automáticos de Sakichi Toyoda (1896), aplicado a manufactura por Taiichi Ohno en el Toyota Production System.

**Jidoka Inline [v2.1]:** En las Katas, el ciclo Jidoka está embebido en cada paso:

```markdown
### Paso N: [Acción]
[Instrucciones]
**Verificación:** [Cómo saber si funcionó]
> **Si no puedes continuar:** [Causa → Resolución]
```

### Just-In-Time Learning
Adquisición de conocimiento exactamente cuando se necesita, integrado al flujo de trabajo. En RaiSE opera en tres dimensiones: (1) Contexto cargado para el agente, (2) Conocimiento ofrecido al Orquestador, (3) Mejoras aplicadas al framework.

### Kaizen
Filosofía japonesa de mejora continua incremental. En RaiSE, opera en dos niveles: (1) mejora del framework con cada feature implementada, y (2) crecimiento profesional del Orquestador. Si un prompt falló o el código requirió muchas iteraciones, los guardrails y katas se refinan. El sistema aprende de sus errores.

### Kata [v2.3: Work Cycles + Jidoka Inline]
Segunda capa del modelo ontológico RaiSE. Proceso estructurado que hace visible la desviación del estándar, habilitando el ciclo Jidoka. Inspirado en las katas de artes marciales (práctica deliberada).

**Propósito:** La Kata no es documentación pasiva—es un **sensor** que detecta cuándo algo no va bien, permitiendo al Orquestador parar, corregir y continuar.

**Diferenciador estratégico**: Ningún framework de agentes AI usa este término. RaiSE lo mantiene como conexión explícita con Lean y como concepto único en la industria.

**Metáfora Niwashi:** La práctica del jardinero — ciclo de cuidado estacional, flujo de trabajo.

**Organización por Work Cycle [v2.3]:**

| Work Cycle | Frecuencia | Katas |
|------------|------------|-------|
| `project/` | 1x por épica | discovery, vision, design, backlog |
| `feature/` | Nx por feature | plan, implement, review |
| `setup/` | 1x brownfield | analyze, ecosystem |
| `improve/` | Continuo | retrospective, evolve-kata |

**Jidoka Inline:** Cada paso de una Kata incluye verificación y guía de corrección embebida, no en sección separada.

> **Migración v2.3:** Los niveles semánticos (principios/flujo/patrón/técnica) fueron eliminados por ADR-008. Las katas se organizan por Work Cycle, no por nivel de abstracción.

### Kata Harness (Capability) [NUEVO v2.3]
Capability de plataforma RaiSE: motor de ejecución que interpreta definiciones de proceso (Katas) e invoca operaciones atómicas (Skills).

**Alcance:** El Kata Harness ejecuta **TODAS las katas de cualquier Work Cycle**:
- `project/`: discovery, vision, design, backlog
- `feature/`: stories, plan, implement, review
- `setup/`: analyze, ecosystem
- `improve/`: retrospective, evolve-kata

**Responsabilidades:**
- Interpretar Katas y ejecutar sus pasos
- Invocar Skills con inputs/outputs definidos
- Gestionar el ciclo de vida del contexto
- Manejar handoffs entre Katas
- Aplicar verificaciones Jidoka inline

**Nota terminológica:** El término "harness" en AI tiene dos contextos:
- **Agent Harness** (ejecución): Infraestructura que envuelve un LLM para tareas largas. *RaiSE usa este significado.*
- **Evaluation Harness** (testing): Framework de benchmarking para evaluar LLMs (e.g., EleutherAI lm-evaluation-harness).

**Alineamiento industria:** Alineado con LangChain DeepAgents y Anthropic Claude Agent SDK (2024-2026).

**Ubicación:** Configuración en `.raise/harness/config.yaml`. El runtime es externo (instalado separadamente).

> Ver ADR-008 para arquitectura completa.

### ShuHaRi (守破離) [NUEVO v2.1]
Modelo de maestría de las artes marciales japonesas que describe tres fases de aprendizaje. En RaiSE, ShuHaRi es una **lente** que describe cómo el Orquestador se relaciona con las Katas—no una clasificación de las Katas mismas.

| Fase | Kanji | Significado | Cómo usa las Katas |
|------|-------|-------------|-------------------|
| **Shu** | 守 | Proteger/Obedecer | Sigue cada paso exactamente |
| **Ha** | 破 | Romper/Desprender | Adapta pasos al contexto |
| **Ri** | 離 | Trascender/Separar | Crea variantes o nuevas Katas |

**Implicación práctica:** Un mismo archivo de Kata sirve a Orquestadores en cualquier fase. No existen variantes `flujo-shu-04.md` o `flujo-ha-04.md`.

> **Coherencia filosófica:** Kata, ShuHaRi, Jidoka, Kaizen—todos de origen japonés, alineados con Lean/TPS.

### Skill (Capa de Acción) [NUEVO v2.3]
Tercera capa del modelo ontológico RaiSE. Operación atómica con inputs/outputs claros, definida en YAML.

**Características:**
- **Contrato explícito**: Input/output types definidos en schema
- **Atómico**: Una operación, un propósito
- **Invocable**: Por katas, por el harness, o directamente
- **Determinista**: Comportamiento predecible

**Metáfora Niwashi:** Las herramientas del jardinero — tijeras, rastrillo, pala.

**Skills disponibles:**
| Skill | Propósito |
|-------|-----------|
| `retrieve-mvc` | Obtener Minimum Viable Context para tarea |
| `run-gate` | Ejecutar Validation Gate |
| `check-compliance` | Verificar código contra reglas |
| `explain-rule` | Explicar regla con rationale |

**Ubicación:** `.raise/skills/*.yaml`

> Ver ADR-008 para modelo completo Context/Kata/Skill.

### setup/ (Categoría de Comandos)
**[ACTUALIZADO v2.3]** Comandos que analizan codebases existentes (brownfield) y extraen convenciones como reglas versionadas.

**Comandos:**
- `/setup/init-project` — Inicializar proyecto con constitution
- `/setup/analyze-codebase` — Analizar codebase brownfield
- `/setup/generate-rules` — Generar reglas desde análisis
- `/setup/edit-rule` — Editar regla existente

**Características:**
- **Input**: Codebase brownfield
- **Output**: `rules/*.yaml`, `graph.yaml`, `conventions.md`
- **Método**: LLM synthesis (Open Core) / Determinista (Licensed)
- **Frecuencia**: Batch (cuando codebase cambia significativamente)
- **Principio**: "Facts Not Gaps" — describe lo que ES, no evalúa

**Pipeline conceptual:** DETECT → SCAN → DESCRIBE → GOVERN

> **Evolución v2.2:** Reemplaza "SAR Component" como terminología. Los comandos son la implementación directa, no hay componente abstracto separado.

### Lean Software Development
Adaptación de los principios del Toyota Production System al desarrollo de software. RaiSE es fundamentalmente un framework Lean que integra IA como acelerador del flujo de valor. Los siete principios Lean (eliminar desperdicio, amplificar aprendizaje, decidir tarde, entregar rápido, empoderar al equipo, construir integridad, ver el todo) guían todas las decisiones de diseño de RaiSE.

> Ver [05-learning-philosophy.md](./05-learning-philosophy.md) para desarrollo completo.

### MVC (Minimum Viable Context)
**[NUEVO v2.2]** El contexto mínimo necesario para que un agente LLM ejecute una tarea correctamente, sin información innecesaria que aumente tokens o confunda.

**Estructura del MVC:**
```yaml
query:
  task: "descripción de la tarea"
  scope: "path/pattern"
  min_confidence: 0.80

primary_rules:     # Reglas directamente aplicables (contenido completo)
context_rules:     # Reglas relacionadas (solo resúmenes)
warnings:          # Conflictos, deprecaciones, baja confianza
graph_context:     # Subgrafo de relaciones relevantes
```

**Principios:**
- **Determinista**: Mismo input = mismo output (sin LLM en retrieval)
- **Token-efficient**: Resúmenes para reglas de contexto, completas para primarias
- **Graph-aware**: Traversal de relaciones entre reglas

> **Comando asociado:** `/context/get` entrega el MVC para una tarea específica.

### Observable Workflow
**[NUEVO v2.0]** Flujo de trabajo donde cada decisión del agente es trazable y auditable. Alineado con el framework MELT (Metrics, Events, Logs, Traces) de observabilidad.

**Componentes de observabilidad en RaiSE:**
- **Metrics**: Tokens consumidos, re-prompting rate, hallucination rate
- **Events**: Validation Gates pasados/fallidos, escalaciones
- **Logs**: Razonamiento del agente (cuando disponible)
- **Traces**: Flujo completo spec → plan → código

### Orquestador (Orchestrator)
Rol evolucionado del desarrollador en RaiSE. El humano define el "Qué" y el "Por qué"; valida el "Cómo" generado por agentes. El orquestador es el director, no un simple consumidor de código.

### Platform Agnosticism
Principio que establece que RaiSE funciona donde funciona Git, sin dependencia de GitHub, GitLab, Bitbucket ni ningún proveedor específico.

### raise-config
Repositorio central que contiene guardrails, katas y templates compartidos. Los proyectos individuales sincronizan desde raise-config mediante `raise pull`.

### raise-kit
CLI local que permite inicializar proyectos, validar compliance y sincronizar guardrails. Interfaz principal del usuario final con RaiSE.

### pull (comando CLI) [NUEVO v2.1]
Comando que sincroniza Golden Data desde el repositorio central (raise-config).

**Uso:** `raise pull [--branch <nombre>] [--guardrails-only]`

**Contexto:** Desarrollo + CI/CD (automatizable)

> **Nota de migración:** Reemplaza `raise hydrate` desde v2.1 (ADR-010). El nombre "pull" alinea con la semántica Git y es más intuitivo.

### kata (comando CLI) [NUEVO v2.1]
Comando que ejecuta una Kata (proceso estructurado con Jidoka inline).

**Uso:** `raise kata <nivel> [--verify]`

**Niveles disponibles:** principios, flujo, patrón, técnica (y alias L0, L1, L2, L3)

> **Nota de migración:** Reemplaza `raise validate` desde v2.1 (ADR-010).

### Specification (Spec)
Documento detallado que describe *qué* construir, incluyendo requisitos funcionales, no-funcionales y criterios de aceptación. Es el contrato entre Orquestador y Agente.

### Validation Gate
**[RENOMBRADO v2.0, antes: DoD Fractal]** Punto de verificación de calidad en el flujo que asegura que ciertos criterios se cumplen antes de avanzar a la siguiente fase.

**Fases típicas con Gates:**
- Gate-Discovery: Requisitos suficientemente claros
- Gate-Design: Arquitectura validada
- Gate-Code: Implementación lista para merge
- Gate-Security: Auditoría de seguridad passed

---

## Ontología Agentic AI

### MCP (Model Context Protocol)
Protocolo estándar de Anthropic para conectar LLMs con recursos externos. RaiSE expone Katas, Guardrails y Constitution como recursos MCP, permitiendo que agentes (Claude, Cursor, etc.) accedan a contexto en tiempo real.

**Primitivos MCP en RaiSE:**
- **Resources**: Constitution, Guardrails, Specs
- **Tools**: validate_gate, check_guardrail, escalate
- **Prompts**: Katas como prompts templates
- **Sampling**: Delegación de razonamiento

### Ng Patterns (Andrew Ng, 2024)
Patrones de desarrollo con LLMs identificados por Andrew Ng. RaiSE integra explícitamente: Short-Context, RAG (Golden Data), Fine-tuning (Katas) y Tool-use (MCP Tools).

| Patrón | Implementación en RaiSE | Ejemplo |
|--------|-------------------------|---------|
| **Short-Context** | Constitution + Specs (máx 2-3 docs activos) | Evitar context overflow |
| **RAG** | Golden Data + Corpus | Agente busca contexto relevante |
| **Fine-tuning** | Katas + Learnings | Refinar comportamiento |
| **Tool-use** | MCP Tools (gate validation, escalate) | Agente usa tools para decisiones |
| **Multi-Agent** | Agentes especializados colaboran | Crews por aspecto (code, test, docs) |

---

## Artefactos del Flujo de Trabajo

### Jerarquía de Tres Niveles (ADR-010) [NUEVO v2.4]

RaiSE organiza artefactos en tres niveles que reflejan la estructura natural de desarrollo:

```
SOLUTION LEVEL (Sistema - perdura)
├── Business Case → Solution Vision → Governance
│
PROJECT LEVEL (Iniciativa - time-bound)
├── PRD → Project Vision → Tech Design → Backlog
│
CODEBASE LEVEL (Reglas - heredadas + locales)
└── Governance (heredado) → Rules (repo-specific)
```

### Business Case [NUEVO v2.4]
Artefacto de nivel **solución** que documenta la justificación de negocio para un sistema. Responde: "¿Por qué debe existir este sistema?"

**Secciones clave:**
- Oportunidad de negocio (problema, causas, mercado)
- Propuesta de valor y diferenciadores
- Stakeholders y usuarios
- Constraints y métricas de éxito
- Riesgos y mitigaciones
- Recomendación (Go/No-Go)

**Ubicación:** `specs/main/business_case.md`
**Kata:** `solution/discovery`

### Solution Vision [ACTUALIZADO v2.4]
Artefacto de nivel **solución** que define QUÉ ES el sistema. Responde: "¿Qué sistema construimos para resolver el Business Case?"

**Cambio v2.4:** Antes aplicaba a nivel proyecto. Ahora es exclusivamente nivel solución y define el sistema completo.

**Secciones clave:**
- Identidad del sistema (nombre, tipo, misión)
- Alcance y boundaries
- Capacidades core
- Dirección técnica (stack, patrones, decisiones)
- Quality attributes y security level
- Integraciones

**Ubicación:** `specs/main/solution_vision.md`
**Kata:** `solution/vision`
**Deriva:** Governance (guardrails del sistema)

### Project Vision [NUEVO v2.4]
Artefacto de nivel **proyecto** que traduce un PRD en visión técnica de alto nivel. Responde: "¿Cómo abordamos este proyecto específico?"

**Cambio v2.4:** Renombrado desde "Solution Vision" a nivel proyecto para distinguirlo del artefacto de nivel solución.

**Secciones clave:**
- Problem statement técnico
- Visión de alto nivel
- Alineamiento estratégico (goals ↔ mecanismos técnicos)
- MVP scope (Must/Should/Could)
- Métricas de éxito técnicas
- Constraints y assumptions

**Ubicación:** `specs/main/project_vision.md`
**Kata:** `project/vision`

### PRD (Product Requirements Document)
Artefacto de nivel **proyecto** en la fase Discovery que captura requisitos del producto desde la perspectiva de negocio y usuarios.

### Technical Design
Especificación técnica que traduce la Project Vision en arquitectura, componentes y decisiones de implementación.

### Implementation Plan
Plan paso a paso que guía la ejecución determinista de una tarea. Incluye tasks atómicas, dependencias y criterios de verificación.

### User Story (Historia de Usuario)
Descripción desde la perspectiva del usuario de una funcionalidad deseada. Formato: "Como [rol], quiero [acción], para [beneficio]".

---

## Conceptos de Preventa/Proyectos

### Capability (Capacidad)
Habilidad de alto nivel que la organización o sistema debe poseer.

### Feature (Funcionalidad)
Agrupación lógica de requisitos que proporciona valor a un stakeholder.

### Statement of Work (SoW)
Documento contractual que detalla trabajo a realizar, entregables, cronograma y costos.

### Roadmap (Hoja de Ruta)
Plan visual que muestra secuencia y tiempos estimados para entrega de funcionalidades o hitos.

---

## Mapeo Español-Inglés

| Español | Inglés | Notas |
|---------|--------|-------|
| Agente | Agent | |
| Barrera de protección | Guardrail | Antes: Regla |
| Constitución | Constitution | |
| Diseño de contexto | Context Engineering | Nuevo v2.0 |
| Especificación | Specification (Spec) | |
| Funcionalidad | Feature | También: Característica |
| Historia de Usuario | User Story | |
| Hoja de Ruta | Roadmap | |
| Kata | Kata | No se traduce |
| Orquestador | Orchestrator | Rol del desarrollador |
| Puerta de escalación | Escalation Gate | Nuevo v2.0 |
| Puerta de validación | Validation Gate | Antes: DoD Fractal |
| Regla | Rule | Alias de Guardrail |
| Requisito | Requirement | |

---

## Jerarquías de Referencia

### Jerarquía de Trabajo (Agile)
```
Capability > Feature/Epic > User Story > Task
```

### Jerarquía de Artefactos RaiSE
```
Constitution > Vision > Architecture > Domain > Execution
```

### Jerarquía de Governance
```
Constitution (Principios) → Guardrails (Reglas) → Specs (Contratos) → Validation Gates (Checkpoints)
```

### Jerarquía Ontológica [v2.3]
```
Context (Sabiduría) → Kata (Práctica) → Skill (Acción)
```

| Capa | Pregunta | Metáfora Niwashi |
|------|----------|------------------|
| **Context** | ¿Por qué? ¿Qué sé? | Sabiduría del jardinero |
| **Kata** | ¿Cómo fluye? | Práctica del jardinero |
| **Skill** | ¿Cómo hacer? | Herramientas del jardinero |

### Organización de Katas por Work Cycle [v2.3]
```
katas/project/   → 1x por épica (discovery, vision, design, backlog)
katas/feature/   → Nx por feature (plan, implement, review)
katas/setup/     → 1x brownfield (analyze, ecosystem)
katas/improve/   → Continuo (retrospective, evolve-kata)
```

> **Migración v2.3:** Los niveles de abstracción (principios/flujo/patrón/técnica) fueron eliminados. Ver ADR-008.

---

## Formato de Referencia a Principios

Para referenciar un principio RaiSE en documentos:

```
[RaiSE: Nombre-Del-Principio]
```

**Principios disponibles:**
- `[RaiSE: Human-Centric]` - Humanos definen, máquinas ejecutan
- `[RaiSE: Governance-as-Code]` - Políticas versionadas en Git
- `[RaiSE: Platform-Agnostic]` - Sin vendor lock-in
- `[RaiSE: Validation-Gates]` - Calidad en cada fase (antes: Fractal-DoD)
- `[RaiSE: Heutagogy]` - Enseñar, no reemplazar
- `[RaiSE: Kaizen]` - Mejora continua
- `[RaiSE: Context-Engineering]` - Diseño deliberado del ambiente informacional

---

## Anti-Términos (Qué NO Usamos)

| Evitar | Usar en su lugar | Razón |
|--------|------------------|-------|
| "Vibe coding" | "Desarrollo sin spec" o "Vibe engineering" (si profesional) | Simon Willison distingue vibe coding (casual) de vibe engineering (profesional con pruebas) |
| "AI coder" | "Agente de desarrollo" | El humano sigue siendo el coder |
| "Prompt engineering" | "Context Engineering" | RaiSE es arquitectura de contexto, no tweaking de prompts |
| "Magic" | "Proceso automatizado" | Principio de transparencia |
| "DoD Fractal" | "Validation Gate" | Terminología HITL estándar (migración v2.0) |
| "Rule" (aislado) | "Guardrail" | Más específico, connota protección activa |
| "L0/L1/L2/L3" (aislado) | Work Cycle + kata name | Niveles de abstracción eliminados por ADR-008 (migración v2.3) |
| "principios/flujo/patrón/técnica" | Work Cycle (project/feature/setup/improve) | Niveles de abstracción eliminados por ADR-008 (migración v2.3) |
| "micro-kaizen" | "Jidoka inline" | El ciclo de corrección está embebido en cada paso, no separado |
| "Kata Executor Harness" | "Kata Harness" | Simplificación terminológica (migración v2.3) |
| "Command" | "Kata" o "Skill" | Commands mezclaban proceso con ejecución (migración v2.3) |
| "SAR" | "`setup/` commands" | Los comandos SON la implementación, no hay componente abstracto (migración v2.2) |
| "CTX" | "`context/` commands" | Los comandos SON la implementación, no hay componente abstracto (migración v2.2) |
| "SAR Component" | "setup commands" | Reducción de carga cognitiva (migración v2.2) |
| "CTX Component" | "context commands" | Reducción de carga cognitiva (migración v2.2) |

---

## Métricas de Calidad AI (Referencia)

Métricas emergentes para desarrollo asistido por IA:

| Métrica | Descripción | Benchmark |
|---------|-------------|-----------|
| **Hallucination Rate** | % de información fabricada por el agente | <10% target |
| **Re-prompting Rate** | Iteraciones para output aceptable | <3 ideal |
| **Context Adherence** | Alineamiento con spec proporcionada | >85% target |
| **Rework Rate** | Código modificado post-merge | Clave para AI code (DORA 2025) |
| **Escalation Rate** | % de tareas escaladas a humano | 10-15% óptimo |

---

## Work Cycle (Ciclo de Trabajo) [ACTUALIZADO v2.4]

Contexto operacional del Orquestador que agrupa katas aplicables y define la frecuencia de ejecución. Los ciclos son **ortogonales**—el Orquestador transita entre ellos según la naturaleza del trabajo, no en secuencia fija.

**Ciclos definidos [v2.4]:**

| Ciclo | Directorio | Frecuencia | Katas |
|-------|------------|------------|-------|
| **solution** | `katas/solution/` | 1x por sistema | discovery, vision |
| **project** | `katas/project/` | 1x por épica | discovery, vision, design, backlog |
| **feature** | `katas/feature/` | Nx por feature | plan, implement, review |
| **setup** | `katas/setup/` | 1x por sistema | governance, rules, ecosystem |
| **improve** | `katas/improve/` | Continuo | retrospective, evolve-kata |

**Cambio v2.4:** Añadido ciclo `solution/` para artefactos de nivel sistema (Business Case, Solution Vision). El ciclo `setup/` ahora incluye `governance` kata.

**Cambio v2.3:** Los Work Cycles ahora son la estructura organizativa principal de las katas, reemplazando los niveles de abstracción (principios/flujo/patrón/técnica).

**Slash commands:** Los Work Cycles habilitan comandos semánticos como `/solution/discovery`, `/project/vision`, `/feature/implement`.

> Ver ADR-008 y ADR-010 para decisiones arquitectónicas.

---

## Changelog

### v2.4.0 (2026-01-30)
- **NUEVO**: Jerarquía de tres niveles: Solution → Project → Codebase (ADR-010)
- **NUEVO**: Entrada `Business Case` — justificación de negocio a nivel solución
- **NUEVO**: Entrada `Solution Vision` — definición del sistema a nivel solución
- **NUEVO**: Entrada `Project Vision` — visión técnica a nivel proyecto (antes: Solution Vision)
- **NUEVO**: Sección `Jerarquía de Tres Niveles` en Artefactos del Flujo de Trabajo
- **NUEVO**: Work Cycle `solution/` con katas discovery y vision
- **ACTUALIZADO**: Work Cycle `setup/` ahora incluye kata governance
- **ACTUALIZADO**: Entrada `Work Cycle` con tabla actualizada de 5 ciclos
- **RENOMBRADO**: "Solution Vision" (nivel proyecto) → "Project Vision"
- **REFERENCIA**: ADR-010 para decisión arquitectónica completa

### v2.3.0 (2026-01-29)
- **NUEVO**: Modelo ontológico de 3 capas: Context/Kata/Skill (ADR-008)
- **NUEVO**: Entrada `Context (Capa de Sabiduría)` — primera capa ontológica
- **NUEVO**: Entrada `Skill (Capa de Acción)` — tercera capa ontológica
- **NUEVO**: Entrada `Kata Harness (Capability)` — motor de ejecución de katas
- **ACTUALIZADO**: Entrada `Kata` — ahora organizada por Work Cycle, no por nivel de abstracción
- **ACTUALIZADO**: Entrada `Work Cycle` — ahora estructura organizativa principal de katas
- **ACTUALIZADO**: Jerarquía de Katas → Jerarquía Ontológica + Organización por Work Cycle
- **DEPRECADO**: Niveles de kata (principios/flujo/patrón/técnica) — usar Work Cycles
- **DEPRECADO**: Término "Command" — usar Kata o Skill según corresponda
- **NOTA TERMINOLÓGICA**: "Harness" = Agent Harness (ejecución), no Evaluation Harness (testing)
- **REFERENCIA**: ADR-008 para decisión arquitectónica completa

### v2.2.0 (2026-01-29)
- **NUEVO**: Entrada `Command Category (Categoría de Comando)` con tabla de 7 categorías
- **NUEVO**: Entrada `context/` (Categoría de Comandos) — reemplaza "CTX Component"
- **NUEVO**: Entrada `setup/` (Categoría de Comandos) — reemplaza "SAR Component"
- **NUEVO**: Entrada `MVC (Minimum Viable Context)` con estructura YAML
- **DEPRECADO**: Términos "SAR" y "CTX" como nombres de componentes
- **AÑADIDO**: Anti-términos SAR, CTX, SAR Component, CTX Component
- **DECISIÓN**: Los comandos SON la implementación, no hay capa de abstracción adicional

### v2.1.0 (2025-12-29)
- **NUEVO**: Entrada `Work Cycle (Ciclo de Trabajo)` con tabla resumen de los 4 ciclos
- **NUEVO**: Entrada `pull` (comando CLI) — ADR-010
- **NUEVO**: Entrada `kata` (comando CLI) — ADR-010
- **ACTUALIZADO**: raise-config usa `raise pull` (antes: hydrate)
- **NUEVO**: Entrada ShuHaRi
- **ACTUALIZADO**: Kata con niveles semánticos (Principios/Flujo/Patrón/Técnica)
- **ACTUALIZADO**: Kata con Jidoka inline
- **ACTUALIZADO**: Jidoka con mención de Jidoka inline
- **ACTUALIZADO**: Jerarquía de Katas
- **AÑADIDO**: Anti-términos L0-L3, micro-kaizen

### v2.0.0 (2025-12-28)
- **Renombrado**: Rule → Guardrail
- **Renombrado**: DoD Fractal → Validation Gate
- **Nuevo**: Context Engineering
- **Nuevo**: Escalation Gate
- **Nuevo**: Observable Workflow
- **Nueva sección**: Ontología Agentic AI (MCP, Ng Patterns)
- **Nueva sección**: Métricas de Calidad AI
- Actualización de mapeo español-inglés
- Actualización de Anti-Términos

---

*Este glosario es la fuente de verdad para terminología RaiSE. Actualizar con cada nuevo concepto introducido.*
