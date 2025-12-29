# RaiSE Glossary
## Vocabulario CanÃ³nico del Framework

**VersiÃ³n:** 2.1.0  
**Fecha:** 28 de Diciembre, 2025  
**PropÃ³sito:** Definiciones canÃ³nicas de tÃ©rminos usados en el ecosistema RaiSE.

> **Nota de versiÃ³n 2.1:** ActualizaciÃ³n de niveles de Kata (L0-L3 â†’ Principios/Flujo/PatrÃ³n/TÃ©cnica), adiciÃ³n de ShuHaRi como lente del Orquestador, y Jidoka inline.

---

## TÃ©rminos Core de RaiSE

### Agent (Agente)
Sistema de IA que ejecuta tareas de desarrollo de software bajo la orquestaciÃ³n de un humano. Ejemplos: GitHub Copilot, Claude Code, Cursor, Windsurf.

> **Principio relacionado:** Los agentes son ejecutores, no decisores autÃ³nomos. Ver [00-constitution.md](./00-constitution.md) Â§1.

### Constitution (ConstituciÃ³n)
Conjunto de principios inmutables que gobiernan todas las decisiones en un proyecto RaiSE. Es el documento de mayor jerarquÃ­a y raramente cambia.

**Equivalentes en la industria:**
- **MCP**: Prompts (templates reutilizables)
- **spec-kit**: Constitution (mismo tÃ©rmino)
- **Comunidad**: CLAUDE.md, .cursorrules, AGENTS.md

> **Nota**: RaiSE mantiene "Constitution" por su alineamiento con Constitutional AI (Anthropic, 2022) y spec-kit de GitHub.

### Context Engineering
**[NUEVO v2.0]** Disciplina de diseÃ±ar el ambiente informacional completo que un LLM consume para ejecutar tareas. EvoluciÃ³n de "prompt engineering" hacia una prÃ¡ctica arquitectÃ³nica.

> AcuÃ±ado por Andrej Karpathy (2025): "No es prompt engineering, es **context engineering**â€”arquitectar todo el ambiente de informaciÃ³n en el que opera el LLM."

En RaiSE, Context Engineering se manifiesta en:
- **Constitution**: Principios que enmarcan todas las decisiones
- **Specs**: Contexto estructurado del "quÃ©" construir
- **Golden Data**: InformaciÃ³n verificada del proyecto/organizaciÃ³n
- **Guardrails**: Restricciones operacionales activas

### Corpus
ColecciÃ³n estructurada de documentos que proporciona contexto a agentes de IA. El corpus es "Golden Data"â€”informaciÃ³n verificada y canÃ³nica que alimenta las sesiones de trabajo.

### Escalation Gate
**[NUEVO v2.0]** Punto especÃ­fico en el flujo donde el agente debe escalar al Orquestador humano para decisiÃ³n o aprobaciÃ³n. Subtipo de Validation Gate enfocado en HITL (Human-in-the-Loop).

**Criterios tÃ­picos de escalaciÃ³n:**
- Confianza del agente < umbral definido
- DecisiÃ³n de alto impacto (arquitectura, seguridad)
- AmbigÃ¼edad en spec o contexto
- Primer uso de un patrÃ³n nuevo

> **MÃ©trica de referencia**: 10-15% de escalaciÃ³n es Ã³ptimo (85-90% ejecuciÃ³n autÃ³noma). Fuente: Galileo HITL Framework, 2025.

### Golden Data
InformaciÃ³n verificada, estructurada y canÃ³nica que alimenta el contexto de agentes. A diferencia de datos genÃ©ricos, el Golden Data refleja la realidad especÃ­fica del proyecto/organizaciÃ³n.

### Governance as Code
Principio que establece que polÃ­ticas, reglas y estÃ¡ndares son artefactos versionados en Git, no documentos estÃ¡ticos. Lo que no estÃ¡ en el repositorio, no existe.

### Guardrail (antes: Rule)
**[RENOMBRADO v2.0]** Directiva operacional que gobierna el comportamiento del agente o la calidad del cÃ³digo. Definida en Markdown (para humanos), distribuida en JSON (para mÃ¡quinas).

**Diferencia con Constitution:**
- **Constitution**: Principios filosÃ³ficos, inmutables, alto nivel
- **Guardrail**: Reglas operacionales, cambiantes, enforceables

**Equivalentes en la industria:**
- **DSPy**: Assertions
- **LangChain**: Runnable constraints
- **Comunidad enterprise**: Guardrails

> **Nota de migraciÃ³n**: El tÃ©rmino "Rule" sigue siendo vÃ¡lido como alias. Los archivos `.mdc` mantienen su formato.

### HeutagogÃ­a
TeorÃ­a del aprendizaje auto-determinado (del griego *heutos* = "uno mismo" + *agogos* = "guiar"). En RaiSE, significa que el Orquestador diseÃ±a su propio proceso de aprendizaje a travÃ©s de cada interacciÃ³n con agentes de IA. El sistema "enseÃ±a a pescar" en lugar de solo "entregar el pescado".

> Ver [05-learning-philosophy.md](./05-learning-philosophy.md) para desarrollo completo.

### Checkpoint HeutagÃ³gico
Momento estructurado de reflexiÃ³n al finalizar features significativas. Incluye cuatro preguntas: (1) Â¿QuÃ© aprendiste? (2) Â¿QuÃ© cambiarÃ­as del proceso? (3) Â¿Hay mejoras para el framework? (4) Â¿En quÃ© eres mÃ¡s capaz ahora? Las respuestas alimentan el crecimiento del Orquestador y la evoluciÃ³n del corpus.

### Jidoka (è‡ªåƒåŒ–)
Pilar del Toyota Production System que significa "automatizaciÃ³n con toque humano". En RaiSE, se manifiesta como la capacidad de **parar el flujo** cuando se detecta un problema (Validation Gate no pasa), en lugar de acumular defectos. Los cuatro pasos: Detectar â†’ Parar â†’ Corregir â†’ Continuar.

**Jidoka Inline [v2.1]:** En las Katas, el ciclo Jidoka estÃ¡ embebido en cada paso:

```markdown
### Paso N: [AcciÃ³n]
[Instrucciones]
**VerificaciÃ³n:** [CÃ³mo saber si funcionÃ³]
> **Si no puedes continuar:** [Causa â†’ ResoluciÃ³n]
```

### Just-In-Time Learning
AdquisiciÃ³n de conocimiento exactamente cuando se necesita, integrado al flujo de trabajo. En RaiSE opera en tres dimensiones: (1) Contexto cargado para el agente, (2) Conocimiento ofrecido al Orquestador, (3) Mejoras aplicadas al framework.

### Kaizen
FilosofÃ­a japonesa de mejora continua incremental. En RaiSE, opera en dos niveles: (1) mejora del framework con cada feature implementada, y (2) crecimiento profesional del Orquestador. Si un prompt fallÃ³ o el cÃ³digo requiriÃ³ muchas iteraciones, los guardrails y katas se refinan. El sistema aprende de sus errores.

### Kata [v2.1: Niveles SemÃ¡nticos + Jidoka Inline]
Proceso estructurado que hace visible la desviaciÃ³n del estÃ¡ndar, habilitando el ciclo Jidoka. Inspirado en las katas de artes marciales (prÃ¡ctica deliberada).

**PropÃ³sito:** La Kata no es documentaciÃ³n pasivaâ€”es un **sensor** que detecta cuÃ¡ndo algo no va bien, permitiendo al Orquestador parar, corregir y continuar.

**Diferenciador estratÃ©gico**: NingÃºn framework de agentes AI usa este tÃ©rmino. RaiSE lo mantiene como conexiÃ³n explÃ­cita con Lean y como concepto Ãºnico en la industria.

**Niveles SemÃ¡nticos [v2.1]:**

| Nivel | Pregunta GuÃ­a | PropÃ³sito | DesviaciÃ³n Visible |
|-------|---------------|-----------|-------------------|
| **Principios** | Â¿Por quÃ©? Â¿CuÃ¡ndo? | Aplicar Constitution | "No puedo justificar" |
| **Flujo** | Â¿CÃ³mo fluye? | Secuencias de valor | "Falta input" |
| **PatrÃ³n** | Â¿QuÃ© forma? | Estructuras recurrentes | "Output incorrecto" |
| **TÃ©cnica** | Â¿CÃ³mo hacer? | Instrucciones especÃ­ficas | "ValidaciÃ³n falla" |

**Jidoka Inline:** Cada paso de una Kata incluye verificaciÃ³n y guÃ­a de correcciÃ³n embebida, no en secciÃ³n separada.

> Ver [kata-shuhari-schema-v2.1.md](./kata-shuhari-schema-v2.1.md) para schema completo.

### ShuHaRi (å®ˆç ´é›¢) [NUEVO v2.1]
Modelo de maestrÃ­a de las artes marciales japonesas que describe tres fases de aprendizaje. En RaiSE, ShuHaRi es una **lente** que describe cÃ³mo el Orquestador se relaciona con las Katasâ€”no una clasificaciÃ³n de las Katas mismas.

| Fase | Kanji | Significado | CÃ³mo usa las Katas |
|------|-------|-------------|-------------------|
| **Shu** | å®ˆ | Proteger/Obedecer | Sigue cada paso exactamente |
| **Ha** | ç ´ | Romper/Desprender | Adapta pasos al contexto |
| **Ri** | é›¢ | Trascender/Separar | Crea variantes o nuevas Katas |

**ImplicaciÃ³n prÃ¡ctica:** Un mismo archivo de Kata sirve a Orquestadores en cualquier fase. No existen variantes `flujo-shu-04.md` o `flujo-ha-04.md`.

> **Coherencia filosÃ³fica:** Kata, ShuHaRi, Jidoka, Kaizenâ€”todos de origen japonÃ©s, alineados con Lean/TPS.

### Lean Software Development
AdaptaciÃ³n de los principios del Toyota Production System al desarrollo de software. RaiSE es fundamentalmente un framework Lean que integra IA como acelerador del flujo de valor. Los siete principios Lean (eliminar desperdicio, amplificar aprendizaje, decidir tarde, entregar rÃ¡pido, empoderar al equipo, construir integridad, ver el todo) guÃ­an todas las decisiones de diseÃ±o de RaiSE.

> Ver [05-learning-philosophy.md](./05-learning-philosophy.md) para desarrollo completo.

### Observable Workflow
**[NUEVO v2.0]** Flujo de trabajo donde cada decisiÃ³n del agente es trazable y auditable. Alineado con el framework MELT (Metrics, Events, Logs, Traces) de observabilidad.

**Componentes de observabilidad en RaiSE:**
- **Metrics**: Tokens consumidos, re-prompting rate, hallucination rate
- **Events**: Validation Gates pasados/fallidos, escalaciones
- **Logs**: Razonamiento del agente (cuando disponible)
- **Traces**: Flujo completo spec â†’ plan â†’ cÃ³digo

### Orquestador (Orchestrator)
Rol evolucionado del desarrollador en RaiSE. El humano define el "QuÃ©" y el "Por quÃ©"; valida el "CÃ³mo" generado por agentes. El orquestador es el director, no un simple consumidor de cÃ³digo.

### Platform Agnosticism
Principio que establece que RaiSE funciona donde funciona Git, sin dependencia de GitHub, GitLab, Bitbucket ni ningÃºn proveedor especÃ­fico.

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

**Uso:** `raise kata <alias|id> [target]`

**Contexto:** Solo desarrollo (interactivo, requiere terminal)

**Aliases:** `spec`, `plan`, `design`, `review`, `story`

> **Nota de migración:** Reemplaza `raise validate` desde v2.1 (ADR-010). Las Katas se *ejecutan* como práctica deliberada, no se "validan" como artefactos pasivos.

### SDD (Spec-Driven Development)
Paradigma de desarrollo donde las especificacionesâ€”no el cÃ³digoâ€”son el artefacto primario. El cÃ³digo es la expresiÃ³n ejecutable de specs bien definidas.

**Herramientas SDD en la industria:**
- GitHub spec-kit
- Amazon Kiro
- Tessl

### Spec (Specification)
Documento que describe **QUÃ‰** construir, no **CÃ“MO**. Es la fuente de verdad que el agente consume para generar implementaciÃ³n.

**Equivalentes en la industria:**
- **MCP**: Resources (contexto estructurado)
- **CrewAI**: Task description + expected_output
- **LangGraph**: State (TypedDict)

### Validation Gate (antes: DoD Fractal)
**[RENOMBRADO v2.0]** Punto de control de calidad que debe pasarse antes de avanzar a la siguiente fase. Cada fase del flujo de valor tiene su propio Validation Gate con criterios especÃ­ficos.

**Estructura de Validation Gates en RaiSE:**
```
Gate-Context   â†’  Stakeholders y restricciones claras
Gate-Discovery â†’  PRD validado
Gate-Vision    â†’  Solution Vision aprobada
Gate-Design    â†’  Tech Design completo
Gate-Backlog   â†’  HUs priorizadas
Gate-Plan      â†’  Implementation Plan verificado
Gate-Code      â†’  CÃ³digo que pasa todas las validaciones
Gate-Deploy    â†’  Feature en producciÃ³n
```

**Equivalentes en la industria:**
- **HITL patterns**: Approval Gates, Checkpoints
- **LangGraph**: Conditional edges, Checkpoints
- **Lean**: Quality Gates, Pull boundaries

> **Nota**: El concepto de "fractalidad" (gates a mÃºltiples niveles de granularidad) se preserva en la documentaciÃ³n narrativa.

---

## OntologÃ­a Agentic AI (Interoperabilidad)

### Capa de Protocolo: MCP (Model Context Protocol)

RaiSE adopta MCP como estÃ¡ndar de integraciÃ³n. Mapeo de primitivos:

| Primitivo MCP | Equivalente RaiSE | FunciÃ³n |
|---------------|-------------------|---------|
| **Tools** | Comandos slash, CLI | Acciones que el agente puede ejecutar |
| **Resources** | Specs, Golden Data | Contexto estructurado |
| **Prompts** | Constitution fragments | Templates reutilizables |
| **Sampling** | â€” | Razonamiento LLM delegado |

### Capa de OrquestaciÃ³n: Andrew Ng Patterns

RaiSE incorpora los 4 patrones agentic de Andrew Ng (2025):

| PatrÃ³n | DescripciÃ³n | AplicaciÃ³n RaiSE |
|--------|-------------|------------------|
| **Reflection** | Agente examina y mejora su output | Code review automÃ¡tico, self-critique |
| **Tool Use** | Agente decide quÃ© herramientas invocar | IntegraciÃ³n MCP, tests, linting |
| **Planning** | DescomposiciÃ³n de tareas complejas | Implementation Plan, task breakdown |
| **Multi-Agent** | Agentes especializados colaboran | Crews por aspecto (code, test, docs) |

---

## Artefactos del Flujo de Trabajo

### PRD (Product Requirements Document)
Artefacto de la fase Discovery que captura requisitos del producto desde la perspectiva de negocio y usuarios.

### Solution Vision
Artefacto de la fase de visiÃ³n que describe el futuro estado deseado del producto o sistema, incluyendo decisiones de alto nivel.

### Technical Design
EspecificaciÃ³n tÃ©cnica que traduce la Solution Vision en arquitectura, componentes y decisiones de implementaciÃ³n.

### Implementation Plan
Plan paso a paso que guÃ­a la ejecuciÃ³n determinista de una tarea. Incluye tasks atÃ³micas, dependencias y criterios de verificaciÃ³n.

### User Story (Historia de Usuario)
DescripciÃ³n desde la perspectiva del usuario de una funcionalidad deseada. Formato: "Como [rol], quiero [acciÃ³n], para [beneficio]".

---

## Conceptos de Preventa/Proyectos

### Capability (Capacidad)
Habilidad de alto nivel que la organizaciÃ³n o sistema debe poseer.

### Feature (Funcionalidad)
AgrupaciÃ³n lÃ³gica de requisitos que proporciona valor a un stakeholder.

### Statement of Work (SoW)
Documento contractual que detalla trabajo a realizar, entregables, cronograma y costos.

### Roadmap (Hoja de Ruta)
Plan visual que muestra secuencia y tiempos estimados para entrega de funcionalidades o hitos.

---

## Mapeo EspaÃ±ol-InglÃ©s

| EspaÃ±ol | InglÃ©s | Notas |
|---------|--------|-------|
| Agente | Agent | |
| Barrera de protecciÃ³n | Guardrail | Antes: Regla |
| ConstituciÃ³n | Constitution | |
| DiseÃ±o de contexto | Context Engineering | Nuevo v2.0 |
| EspecificaciÃ³n | Specification (Spec) | |
| Funcionalidad | Feature | TambiÃ©n: CaracterÃ­stica |
| Historia de Usuario | User Story | |
| Hoja de Ruta | Roadmap | |
| Kata | Kata | No se traduce |
| Orquestador | Orchestrator | Rol del desarrollador |
| Puerta de escalaciÃ³n | Escalation Gate | Nuevo v2.0 |
| Puerta de validaciÃ³n | Validation Gate | Antes: DoD Fractal |
| Regla | Rule | Alias de Guardrail |
| Requisito | Requirement | |

---

## JerarquÃ­as de Referencia

### JerarquÃ­a de Trabajo (Agile)
```
Capability > Feature/Epic > User Story > Task
```

### JerarquÃ­a de Artefactos RaiSE
```
Constitution > Vision > Architecture > Domain > Execution
```

### JerarquÃ­a de Governance
```
Constitution (Principios) â†’ Guardrails (Reglas) â†’ Specs (Contratos) â†’ Validation Gates (Checkpoints)
```

### JerarquÃ­a de Katas [v2.1]
```
Principios > Flujo > PatrÃ³n > TÃ©cnica
```

| Nivel | Pregunta | ConexiÃ³n Lean |
|-------|----------|---------------|
| **Principios** | Â¿Por quÃ©? | Toyota Way Principles |
| **Flujo** | Â¿CÃ³mo fluye? | Value Stream |
| **PatrÃ³n** | Â¿QuÃ© forma? | Standardized Work |
| **TÃ©cnica** | Â¿CÃ³mo hacer? | Work Instructions |

**MigraciÃ³n:** `L0`â†’`principios`, `L1`â†’`flujo`, `L2`â†’`patron`, `L3`â†’`tecnica` (aliases preservados).

---

## Formato de Referencia a Principios

Para referenciar un principio RaiSE en documentos:

```
[RaiSE: Nombre-Del-Principio]
```

**Principios disponibles:**
- `[RaiSE: Human-Centric]` - Humanos definen, mÃ¡quinas ejecutan
- `[RaiSE: Governance-as-Code]` - PolÃ­ticas versionadas en Git
- `[RaiSE: Platform-Agnostic]` - Sin vendor lock-in
- `[RaiSE: Validation-Gates]` - Calidad en cada fase (antes: Fractal-DoD)
- `[RaiSE: Heutagogy]` - EnseÃ±ar, no reemplazar
- `[RaiSE: Kaizen]` - Mejora continua
- `[RaiSE: Context-Engineering]` - DiseÃ±o deliberado del ambiente informacional

---

## Anti-TÃ©rminos (QuÃ© NO Usamos)

| Evitar | Usar en su lugar | RazÃ³n |
|--------|------------------|-------|
| "Vibe coding" | "Desarrollo sin spec" o "Vibe engineering" (si profesional) | Simon Willison distingue vibe coding (casual) de vibe engineering (profesional con pruebas) |
| "AI coder" | "Agente de desarrollo" | El humano sigue siendo el coder |
| "Prompt engineering" | "Context Engineering" | RaiSE es arquitectura de contexto, no tweaking de prompts |
| "Magic" | "Proceso automatizado" | Principio de transparencia |
| "DoD Fractal" | "Validation Gate" | TerminologÃ­a HITL estÃ¡ndar (migraciÃ³n v2.0) |
| "Rule" (aislado) | "Guardrail" | MÃ¡s especÃ­fico, connota protecciÃ³n activa |
| "L0/L1/L2/L3" (aislado) | "principios/flujo/patron/tecnica" | Nombres semÃ¡nticos con pregunta guÃ­a implÃ­cita (migraciÃ³n v2.1) |
| "micro-kaizen" | "Jidoka inline" | El ciclo de correcciÃ³n estÃ¡ embebido en cada paso, no separado |

---

## MÃ©tricas de Calidad AI (Referencia)

MÃ©tricas emergentes para desarrollo asistido por IA:

| MÃ©trica | DescripciÃ³n | Benchmark |
|---------|-------------|-----------|
| **Hallucination Rate** | % de informaciÃ³n fabricada por el agente | <10% target |
| **Re-prompting Rate** | Iteraciones para output aceptable | <3 ideal |
| **Context Adherence** | Alineamiento con spec proporcionada | >85% target |
| **Rework Rate** | CÃ³digo modificado post-merge | Clave para AI code (DORA 2025) |
| **Escalation Rate** | % de tareas escaladas a humano | 10-15% Ã³ptimo |

---

## Changelog

### v2.1.0 (2025-12-29)
- **NUEVO**: Entrada `pull` (comando CLI) — ADR-010
- **NUEVO**: Entrada `kata` (comando CLI) — ADR-010
- **ACTUALIZADO**: raise-config usa `raise pull` (antes: hydrate)
- **NUEVO**: Entrada ShuHaRi
- **ACTUALIZADO**: Kata con niveles semÃ¡nticos (Principios/Flujo/PatrÃ³n/TÃ©cnica)
- **ACTUALIZADO**: Kata con Jidoka inline
- **ACTUALIZADO**: Jidoka con menciÃ³n de Jidoka inline
- **ACTUALIZADO**: JerarquÃ­a de Katas
- **AÃ‘ADIDO**: Anti-tÃ©rminos L0-L3, micro-kaizen

### v2.0.0 (2025-12-28)
- **Renombrado**: Rule â†’ Guardrail
- **Renombrado**: DoD Fractal â†’ Validation Gate
- **Nuevo**: Context Engineering
- **Nuevo**: Escalation Gate
- **Nuevo**: Observable Workflow
- **Nueva secciÃ³n**: OntologÃ­a Agentic AI (MCP, Ng Patterns)
- **Nueva secciÃ³n**: MÃ©tricas de Calidad AI
- ActualizaciÃ³n de mapeo espaÃ±ol-inglÃ©s
- ActualizaciÃ³n de Anti-TÃ©rminos

---

*Este glosario es la fuente de verdad para terminologÃ­a RaiSE. Actualizar con cada nuevo concepto introducido.*
