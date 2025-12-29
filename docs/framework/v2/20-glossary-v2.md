# RaiSE Glossary
## Vocabulario Canónico del Framework

**Versión:** 2.1.0  
**Fecha:** 28 de Diciembre, 2025  
**Propósito:** Definiciones canónicas de términos usados en el ecosistema RaiSE.

> **Nota de versión 2.1:** Actualización de niveles de Kata (L0-L3 → Principios/Flujo/Patrón/Técnica), adición de ShuHaRi como lente del Orquestador, y Jidoka inline.

---

## Términos Core de RaiSE

### Agent (Agente)
Sistema de IA que ejecuta tareas de desarrollo de software bajo la orquestación de un humano. Ejemplos: GitHub Copilot, Claude Code, Cursor, Windsurf.

> **Principio relacionado:** Los agentes son ejecutores, no decisores autónomos. Ver [00-constitution.md](./00-constitution.md) §1.

### Constitution (Constitución)
Conjunto de principios inmutables que gobiernan todas las decisiones en un proyecto RaiSE. Es el documento de mayor jerarquía y raramente cambia.

**Equivalentes en la industria:**
- **MCP**: Prompts (templates reutilizables)
- **spec-kit**: Constitution (mismo término)
- **Comunidad**: CLAUDE.md, .cursorrules, AGENTS.md

> **Nota**: RaiSE mantiene "Constitution" por su alineamiento con Constitutional AI (Anthropic, 2022) y spec-kit de GitHub.

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
**[NUEVO v2.0]** Punto específico en el flujo donde el agente debe escalar al Orquestador humano para decisión o aprobación. Subtipo de Validation Gate enfocado en HITL (Human-in-the-Loop).

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

### Jidoka (自働化)
Pilar del Toyota Production System que significa "automatización con toque humano". En RaiSE, se manifiesta como la capacidad de **parar el flujo** cuando se detecta un problema (Validation Gate no pasa), en lugar de acumular defectos. Los cuatro pasos: Detectar → Parar → Corregir → Continuar.

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

### Kata [v2.1: Niveles Semánticos + Jidoka Inline]
Proceso estructurado que hace visible la desviación del estándar, habilitando el ciclo Jidoka. Inspirado en las katas de artes marciales (práctica deliberada).

**Propósito:** La Kata no es documentación pasiva—es un **sensor** que detecta cuándo algo no va bien, permitiendo al Orquestador parar, corregir y continuar.

**Diferenciador estratégico**: Ningún framework de agentes AI usa este término. RaiSE lo mantiene como conexión explícita con Lean y como concepto único en la industria.

**Niveles Semánticos [v2.1]:**

| Nivel | Pregunta Guía | Propósito | Desviación Visible |
|-------|---------------|-----------|-------------------|
| **Principios** | ¿Por qué? ¿Cuándo? | Aplicar Constitution | "No puedo justificar" |
| **Flujo** | ¿Cómo fluye? | Secuencias de valor | "Falta input" |
| **Patrón** | ¿Qué forma? | Estructuras recurrentes | "Output incorrecto" |
| **Técnica** | ¿Cómo hacer? | Instrucciones específicas | "Validación falla" |

**Jidoka Inline:** Cada paso de una Kata incluye verificación y guía de corrección embebida, no en sección separada.

> Ver [kata-shuhari-schema-v2.1.md](./kata-shuhari-schema-v2.1.md) para schema completo.

### ShuHaRi (守破離) [NUEVO v2.1]
Modelo de maestría de las artes marciales japonesas que describe tres fases de aprendizaje. En RaiSE, ShuHaRi es una **lente** que describe cómo el Orquestador se relaciona con las Katas—no una clasificación de las Katas mismas.

| Fase | Kanji | Significado | Cómo usa las Katas |
|------|-------|-------------|-------------------|
| **Shu** | 守 | Proteger/Obedecer | Sigue cada paso exactamente |
| **Ha** | 破 | Romper/Desprender | Adapta pasos al contexto |
| **Ri** | 離 | Trascender/Separar | Crea variantes o nuevas Katas |

**Implicación práctica:** Un mismo archivo de Kata sirve a Orquestadores en cualquier fase. No existen variantes `flujo-shu-04.md` o `flujo-ha-04.md`.

> **Coherencia filosófica:** Kata, ShuHaRi, Jidoka, Kaizen—todos de origen japonés, alineados con Lean/TPS.

### Lean Software Development
Adaptación de los principios del Toyota Production System al desarrollo de software. RaiSE es fundamentalmente un framework Lean que integra IA como acelerador del flujo de valor. Los siete principios Lean (eliminar desperdicio, amplificar aprendizaje, decidir tarde, entregar rápido, empoderar al equipo, construir integridad, ver el todo) guían todas las decisiones de diseño de RaiSE.

> Ver [05-learning-philosophy.md](./05-learning-philosophy.md) para desarrollo completo.

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
Repositorio central que contiene guardrails, katas y templates compartidos. Los proyectos individuales sincronizan desde raise-config mediante `raise hydrate`.

### raise-kit
CLI local que permite inicializar proyectos, validar compliance y sincronizar guardrails. Interfaz principal del usuario final con RaiSE.

### SDD (Spec-Driven Development)
Paradigma de desarrollo donde las especificaciones—no el código—son el artefacto primario. El código es la expresión ejecutable de specs bien definidas.

**Herramientas SDD en la industria:**
- GitHub spec-kit
- Amazon Kiro
- Tessl

### Spec (Specification)
Documento que describe **QUÉ** construir, no **CÓMO**. Es la fuente de verdad que el agente consume para generar implementación.

**Equivalentes en la industria:**
- **MCP**: Resources (contexto estructurado)
- **CrewAI**: Task description + expected_output
- **LangGraph**: State (TypedDict)

### Validation Gate (antes: DoD Fractal)
**[RENOMBRADO v2.0]** Punto de control de calidad que debe pasarse antes de avanzar a la siguiente fase. Cada fase del flujo de valor tiene su propio Validation Gate con criterios específicos.

**Estructura de Validation Gates en RaiSE:**
```
Gate-Context   →  Stakeholders y restricciones claras
Gate-Discovery →  PRD validado
Gate-Vision    →  Solution Vision aprobada
Gate-Design    →  Tech Design completo
Gate-Backlog   →  HUs priorizadas
Gate-Plan      →  Implementation Plan verificado
Gate-Code      →  Código que pasa todas las validaciones
Gate-Deploy    →  Feature en producción
```

**Equivalentes en la industria:**
- **HITL patterns**: Approval Gates, Checkpoints
- **LangGraph**: Conditional edges, Checkpoints
- **Lean**: Quality Gates, Pull boundaries

> **Nota**: El concepto de "fractalidad" (gates a múltiples niveles de granularidad) se preserva en la documentación narrativa.

---

## Ontología Agentic AI (Interoperabilidad)

### Capa de Protocolo: MCP (Model Context Protocol)

RaiSE adopta MCP como estándar de integración. Mapeo de primitivos:

| Primitivo MCP | Equivalente RaiSE | Función |
|---------------|-------------------|---------|
| **Tools** | Comandos slash, CLI | Acciones que el agente puede ejecutar |
| **Resources** | Specs, Golden Data | Contexto estructurado |
| **Prompts** | Constitution fragments | Templates reutilizables |
| **Sampling** | — | Razonamiento LLM delegado |

### Capa de Orquestación: Andrew Ng Patterns

RaiSE incorpora los 4 patrones agentic de Andrew Ng (2025):

| Patrón | Descripción | Aplicación RaiSE |
|--------|-------------|------------------|
| **Reflection** | Agente examina y mejora su output | Code review automático, self-critique |
| **Tool Use** | Agente decide qué herramientas invocar | Integración MCP, tests, linting |
| **Planning** | Descomposición de tareas complejas | Implementation Plan, task breakdown |
| **Multi-Agent** | Agentes especializados colaboran | Crews por aspecto (code, test, docs) |

---

## Artefactos del Flujo de Trabajo

### PRD (Product Requirements Document)
Artefacto de la fase Discovery que captura requisitos del producto desde la perspectiva de negocio y usuarios.

### Solution Vision
Artefacto de la fase de visión que describe el futuro estado deseado del producto o sistema, incluyendo decisiones de alto nivel.

### Technical Design
Especificación técnica que traduce la Solution Vision en arquitectura, componentes y decisiones de implementación.

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

### Jerarquía de Katas [v2.1]
```
Principios > Flujo > Patrón > Técnica
```

| Nivel | Pregunta | Conexión Lean |
|-------|----------|---------------|
| **Principios** | ¿Por qué? | Toyota Way Principles |
| **Flujo** | ¿Cómo fluye? | Value Stream |
| **Patrón** | ¿Qué forma? | Standardized Work |
| **Técnica** | ¿Cómo hacer? | Work Instructions |

**Migración:** `L0`→`principios`, `L1`→`flujo`, `L2`→`patron`, `L3`→`tecnica` (aliases preservados).

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
| "L0/L1/L2/L3" (aislado) | "principios/flujo/patron/tecnica" | Nombres semánticos con pregunta guía implícita (migración v2.1) |
| "micro-kaizen" | "Jidoka inline" | El ciclo de corrección está embebido en cada paso, no separado |

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

## Changelog

### v2.1.0 (2025-12-28)
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
