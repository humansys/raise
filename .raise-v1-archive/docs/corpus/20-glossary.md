# RaiSE Glossary
## Vocabulario Canónico del Framework

**Versión:** 1.0.0  
**Fecha:** 27 de Diciembre, 2025  
**Propósito:** Definiciones canónicas de términos usados en el ecosistema RaiSE.

---

## Términos Core de RaiSE

### Agent (Agente)
Sistema de IA que ejecuta tareas de desarrollo de software bajo la orquestación de un humano. Ejemplos: GitHub Copilot, Claude Code, Cursor, Windsurf.

> **Principio relacionado:** Los agentes son ejecutores, no decisores autónomos. Ver [00-constitution.md](file:///home/emilio/Code/raise-commons/docs/corpus/00-constitution.md) §1.

### Constitution (Constitución)
Conjunto de principios inmutables que gobiernan todas las decisiones en un proyecto RaiSE. Es el documento de mayor jerarquía y raramente cambia.

### Corpus
Colección estructurada de documentos que proporciona contexto a agentes de IA. El corpus es "Golden Data"—información verificada y canónica que alimenta las sesiones de trabajo.

### Definition of Done (DoD)
Criterios que deben cumplirse para considerar una fase completada. En RaiSE, los DoD son **fractales**: cada fase del flujo de valor tiene su propio DoD específico.

### Golden Data
Información verificada, estructurada y canónica que alimenta el contexto de agentes. A diferencia de datos genéricos, el Golden Data refleja la realidad específica del proyecto/organización.

### Governance as Code
Principio que establece que políticas, reglas y estándares son artefactos versionados en Git, no documentos estáticos. Lo que no está en el repositorio, no existe.

### Heutagogía
Teoría del aprendizaje auto-determinado (del griego *heutos* = "uno mismo" + *agogos* = "guiar"). En RaiSE, significa que el Orquestador diseña su propio proceso de aprendizaje a través de cada interacción con agentes de IA. El sistema "enseña a pescar" en lugar de solo "entregar el pescado".

> Ver [05-learning-philosophy.md](file:///home/emilio/Code/raise-commons/docs/corpus/05-learning-philosophy.md) para desarrollo completo.

### Jidoka (自働化)
Pilar del Toyota Production System que significa "automatización con toque humano". En RaiSE, se manifiesta como la capacidad de **parar el flujo** cuando se detecta un problema (DoD no pasa), en lugar de acumular defectos. Los cuatro pasos: Detectar → Parar → Corregir → Prevenir.

### Just-In-Time Learning
Adquisición de conocimiento exactamente cuando se necesita, integrado al flujo de trabajo. En RaiSE opera en tres dimensiones: (1) Contexto cargado para el agente, (2) Conocimiento ofrecido al Orquestador, (3) Mejoras aplicadas al framework.

### Kaizen
Filosofía japonesa de mejora continua incremental. En RaiSE, opera en dos niveles: (1) mejora del framework con cada feature implementada, y (2) crecimiento profesional del Orquestador. Si un prompt falló o el código requirió muchas iteraciones, las reglas y katas se refinan. El sistema aprende de sus errores.

### Lean Software Development
Adaptación de los principios del Toyota Production System al desarrollo de software. RaiSE es fundamentalmente un framework Lean que integra IA como acelerador del flujo de valor. Los siete principios Lean (eliminar desperdicio, amplificar aprendizaje, decidir tarde, entregar rápido, empoderar al equipo, construir integridad, ver el todo) guían todas las decisiones de diseño de RaiSE.

> Ver [05-learning-philosophy.md](file:///home/emilio/Code/raise-commons/docs/corpus/05-learning-philosophy.md) para desarrollo completo.

### Checkpoint Heutagógico
Momento estructurado de reflexión al finalizar features significativas. Incluye cuatro preguntas: (1) ¿Qué aprendiste? (2) ¿Qué cambiarías del proceso? (3) ¿Hay mejoras para el framework? (4) ¿En qué eres más capaz ahora? Las respuestas alimentan el crecimiento del Orquestador y la evolución del corpus.

### Kata
Proceso estructurado y documentado que encapsula un estándar, metodología o patrón. Inspirado en las katas de artes marciales (práctica deliberada). Los katas se organizan en niveles:

| Nivel | Propósito | Ejemplos |
|-------|-----------|----------|
| **L0** | Meta-katas: filosofía y fundamentos | Principios RaiSE |
| **L1** | Katas de proceso: metodología | Generación de planes |
| **L2** | Katas de componentes: patrones | Análisis de código |
| **L3** | Katas técnicos: especialización | Modelado de datos |

### Orquestador (Orchestrator)
Rol evolucionado del desarrollador en RaiSE. El humano define el "Qué" y el "Por qué"; valida el "Cómo" generado por agentes. El orquestador es el director, no un simple consumidor de código.

### Platform Agnosticism
Principio que establece que RaiSE funciona donde funciona Git, sin dependencia de GitHub, GitLab, Bitbucket ni ningún proveedor específico.

### raise-config
Repositorio central que contiene reglas, katas y templates compartidos. Los proyectos individuales sincronizan desde raise-config mediante `raise hydrate`.

### raise-kit
CLI local que permite inicializar proyectos, validar compliance y sincronizar reglas. Interfaz principal del usuario final con RaiSE.

### Rule (Regla)
Directiva que gobierna el comportamiento del agente o la calidad del código. Definida en Markdown (para humanos), distribuida en JSON (para máquinas).

### SDD (Spec-Driven Development)
Paradigma de desarrollo donde las especificaciones—no el código—son el artefacto primario. El código es la expresión ejecutable de specs bien definidas.

### Spec (Specification)
Documento que describe **QUÉ** construir, no **CÓMO**. Es la fuente de verdad que el agente consume para generar implementación.

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
| Constitución | Constitution | |
| Definición de Terminado | Definition of Done (DoD) | |
| Especificación | Specification (Spec) | |
| Funcionalidad | Feature | También: Característica |
| Historia de Usuario | User Story | |
| Hoja de Ruta | Roadmap | |
| Kata | Kata | No se traduce |
| Orquestador | Orchestrator | Rol del desarrollador |
| Regla | Rule | |
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

### Jerarquía de Katas
```
L0 (Meta) > L1 (Proceso) > L2 (Componentes) > L3 (Técnico)
```

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
- `[RaiSE: Fractal-DoD]` - Calidad en cada fase
- `[RaiSE: Heutagogy]` - Enseñar, no reemplazar
- `[RaiSE: Kaizen]` - Mejora continua

---

## Anti-Términos (Qué NO Usamos)

| Evitar | Usar en su lugar | Razón |
|--------|------------------|-------|
| "Vibe coding" | "Desarrollo sin spec" | Describe el anti-patrón sin trivializarlo |
| "AI coder" | "Agente de desarrollo" | El humano sigue siendo el coder |
| "Prompt engineering" | "Diseño de contexto" | RaiSE es más que prompts |
| "Magic" | "Proceso automatizado" | Principio de transparencia |

---

*Este glosario es la fuente de verdad para terminología RaiSE. Actualizar con cada nuevo concepto introducido.*
