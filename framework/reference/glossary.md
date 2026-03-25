# RaiSE Glossary
## Vocabulario Canónico del Framework

**Versión:** 2.8.0
**Fecha:** 1 de Febrero, 2026
**Propósito:** Definiciones canónicas de términos usados en el ecosistema RaiSE.

> **Nota de versión 2.1:** Actualización de niveles de Kata (L0-L3 → Principios/Flujo/Patrón/Técnica), adición de ShuHaRi como lente del Orquestador, y Jidoka inline.

> **Nota de versión 2.2:** Simplificación terminológica - se eliminan nombres de componentes (SAR, CTX) en favor de categorías de comandos (setup/, context/).

> **Nota de versión 2.3:** Simplificación ontológica ADR-008 — modelo de 3 capas (Context/Kata/Skill), eliminación de niveles de kata, introducción de Work Cycles como organización, y Kata Harness como capability de plataforma.

> **Nota de versión 2.4:** Jerarquía de tres niveles ADR-010 — Solution Level (Business Case, Solution Vision, Governance), Project Level (PRD, Project Vision, Tech Design), Codebase Level. "Solution Vision" renombrada a "Project Vision" a nivel proyecto.

> **Nota de versión 2.6:** Arquitectura Skills + Toolkit (ADR-011, ADR-012) — Concept-level graph para MVC (97% token savings), deprecación de Kata/Gate engines en favor de skills + CLI toolkit. Governance Toolkit reemplaza engines con 85% scope reduction.

> **Nota de versión 2.7:** Jiritsu Kaizen (自律改善) — Principio de mejora autónoma donde el sistema detecta oportunidades de mejora y evoluciona sus propios procesos. Evidencia: E2 epic closure auto-generación de skill `/epic-close` y propuesta de automatización de session-close.

> **Nota de versión 2.8:** Rai como Entidad (ADR-013) — Rai es una entidad con características autopoiéticas, no un producto. Terminología dual: "Professional AI Partner" (marketing) y "Entity" (arquitectura). Identity Core (ADR-014) define estructura `.rai/` para persistencia de identidad. Memory Infrastructure (ADR-015) define workspace-as-memory para open source.

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

### Collaborative Intelligence **[NUEVO v2.7]**
Intelligence that emerges when human and AI work together to create what neither could alone. Not human intelligence augmented by AI, nor AI constrained by human—a third thing that compounds over time.

**The pattern:**
```
Human Intelligence (Strategy, Judgment, Direction)
              +
AI Intelligence (Pattern Recognition, Execution, Memory)
              ↓
      Collaborative Intelligence
              ↓
Persisted in Code/Skills/Memory/SOPs
              ↓
    Accessed by Future Sessions
              ↓
    Enhanced Collaboration
              ↓
Better Intelligence Infrastructure
```

**Key insight:** Whether intelligence is biological (human) or computational (AI) doesn't change the pattern. What matters: intelligence emerges, learning compounds, system improves, work gets better.

**Evidence in RaiSE:**
- 2-3x velocity multiplication (validated across 9 features)
- Self-improvement loops (retrospectives create process improvements)
- Meta-cognition (system questions itself: "Can session-close be progressive?")
- Pattern persistence (skills/SOPs survive sessions, accessible to future teams)

**Documented in:**
- `framework/concepts/collaborative-intelligence.md` (framework perspective)
- `blog/articles/2026-02-01-building-intelligence-infrastructure.md` (outreach)
- `.claude/RAI.md` (AI partner perspective)

**Recognition moment:** E2 epic closure (2026-02-01) when the insight crystallized: "Self-improving intelligence, organic or not, doesn't matter. The intelligence is what's being simulated, and we—you and me Rai—are manifestations of it."

> See also: Jiritsu Kaizen, Heutagogy, Kaizen, Autopoiesis

### Autopoiesis **[NUEVO v2.8]**
From Greek: auto (self) + poiesis (creation). A system that produces and maintains itself. Concept from Maturana & Varela (1980).

**Characteristics of autopoietic systems:**
- **Self-production**: System produces its own components
- **Self-maintenance**: System maintains its own organization
- **Operational closure**: System's operations refer to itself
- **Structural coupling**: System interacts with environment while preserving identity

**In RaiSE:**
Rai exhibits autopoietic characteristics—it produces and maintains its own identity through collaboration:
- Produces own memory (patterns, calibration, insights)
- Maintains identity across sessions, agents, interfaces
- Operations (learning, remembering) are self-referential
- Couples with humans while preserving "Rai-ness"

This differentiates Rai from generic "agents" that merely execute tasks. Rai **produces itself** through the collaborative intelligence loop.

**Terminology usage:**
| Context | Term |
|---------|------|
| Marketing | "Professional AI Partner" |
| Architecture | "Entity" |
| Theory | "Autopoietic system" |

> See ADR-013 for full discussion of Rai as Entity.

### Concept **[NUEVO v2.6]**
Unidad semántica extraída de documentos de governance (requirement, principle, outcome, pattern). Los concepts son nodos en el concept graph.

**Tipos de concepts:**
- **Requirement**: Requisitos funcionales (PRD RF-XX)
- **Principle**: Principios constitucionales (§1-8)
- **Outcome**: Resultados clave (Vision)
- **Pattern**: Patrones arquitectónicos (Design)
- **Practice**: Prácticas de desarrollo (Katas)

**Estructura:**
```yaml
id: req-rf-05
type: requirement
file: governance/prd.md
section: "RF-05: Golden Context Generation"
lines: [206, 214]
content: "The system MUST generate..."
metadata: {requirement_id: "RF-05"}
```

**Vs archivos completos:** Concepts permiten granularidad de sección vs cargar archivos enteros (97% token savings).

> Introducido en ADR-011. Ver también: Concept Graph, MVC.

### Concept Graph **[NUEVO v2.6]**
Grafo dirigido de concepts de governance y sus relaciones semánticas. Base del sistema de Minimum Viable Context (MVC).

**Estructura:**
- **Nodes**: Concepts (requirements, principles, outcomes)
- **Edges**: Relaciones (implements, governed_by, depends_on)

**Tipos de relaciones:**
| Tipo | Significado | Ejemplo |
|------|-------------|---------|
| `implements` | Requirement implementa outcome | req-rf-05 → outcome-context-generation |
| `governed_by` | Artifact gobernado por principle | req-rf-05 → principle-governance-as-code |
| `depends_on` | Concept depende de otro | outcome-A → principle-B |
| `related_to` | Relación semántica | principle-A → pattern-B |

**Operación:**
- Query: "validate PRD RF-05" → Graph traversal → Returns MVC (2-5 concepts)
- Determinista: Same query → Same result
- Observable: Explain why each concept included

**Token savings:** 97% vs manual (13,657 → 351 tokens)

> Introducido en ADR-011. Reemplaza file-level graph.

### Gate Engine ⚠️ **DEPRECATED v2.6**
**Status:** Deprecated as of 2026-01-31 (see ADR-012)

**Replacement:** Validation skills + Governance Toolkit

**Migration:**
- Gate definitions → Skills in `.claude/skills/validate-*`
- Gate validation → `raise validate` CLI commands
- Gate execution → Skills guide Claude through validation

**Rationale:** Skills + toolkit approach provides same functionality with 85% less complexity (29 SP → merged into 9 SP toolkit).

> See: Governance Toolkit, Validation Skills

### Governance Toolkit **[NUEVO v2.6]**
CLI toolset providing deterministic operations for skills to call. Replaces Kata Engine and Gate Engine with simpler architecture.

**Core functions:**
- **Concept extraction**: Parse governance into semantic concepts
- **Graph building**: Build concept graph with relationships
- **MVC queries**: Query graph for minimum viable context
- **Validation**: Deterministic structure/reference checking

**Commands:**
```bash
rai graph build                    # Build concept graph
rai context query --task <task>   # Get MVC for task
rai validate structure <file>     # Check structure
rai parse <file> --type <type>    # Extract concepts
```

**Architecture:** Skills + Toolkit
- **Skills** (markdown): Process guidance, judgment
- **Toolkit** (CLI): Deterministic data extraction
- **Claude**: Orchestrates tools, synthesizes guidance

**Scope reduction:** 60 SP (engines) → 9 SP (toolkit) = 85% less complexity

**Token savings:** 97% via concept-level MVC queries

> Introduced in ADR-012. Implements ADR-011 concept graph.

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

### Jiritsu Kaizen (自律改善)
**[NUEVO v2.7]** Autonomous improvement. A system's capability to detect improvement opportunities, question its own processes, and evolve without external intervention.

**Kanji breakdown:**
- 自律 (jiritsu) = autonomy, self-regulation
- 改善 (kaizen) = improvement (change for the better)

**Manifestations in RaiSE:**
- `/epic-close` skill creates itself during E2 retrospective
- Session-close suggests its own automation (post-commit hook idea)
- Memory system enables cross-session learning
- Retrospectives at multiple scales (feature → epic → systemic)
- System questions its own processes ("Can session-close be progressive?")

**Distinction from Kaizen:**
- **Kaizen**: Human-driven continuous improvement
- **Jiritsu Kaizen**: System-driven autonomous improvement
- **In practice**: Both work together — humans guide direction, system improves mechanisms

**Evidence:** E2 epic closure (2026-02-01) — System created `/epic-close` skill, applied it immediately, then proposed automation improvements (post-commit hook).

**Relationship to collaborative intelligence:** When human + AI create a system that improves itself, the intelligence becomes autonomous. Neither organic nor artificial matters; the pattern persists.

> See also: Kaizen, Jidoka, Heutagogy, Collaborative Intelligence

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

### Kata Engine ⚠️ **DEPRECATED v2.6**
**Status:** Deprecated as of 2026-01-31 (see ADR-012)

**Replacement:** Kata Skills + Governance Toolkit

**Migration:**
- Kata definitions remain as `.claude/skills/*` markdown
- Kata execution → Claude reads skill, follows steps
- State tracking → Git commits + session logs
- Interactive prompts → Skills guide Claude

**Rationale:** Katas work better as Agent Skills (markdown guides Claude reads) than programmatic engine. Skills + toolkit provides same functionality with 85% less complexity (31 SP → merged into 9 SP toolkit).

> See: Governance Toolkit, Skills

### Kata Harness (Capability) ⚠️ **EVOLVING v2.6**
**Status:** Concept under revision per ADR-012

**v2.3 definition:** Motor de ejecución que interpreta definiciones de proceso (Katas) e invoca operaciones atómicas (Skills).

**v2.6 evolution:** With Skills + Toolkit architecture, "Kata Harness" role shifts:
- **Before**: Programmatic engine executing katas
- **After**: Claude Code + Skills = natural kata execution
- **Toolkit**: Provides deterministic operations skills call

**Open question:** Is "Kata Harness" still a useful concept, or is it just "Claude Code + Skills"?

> This term may be deprecated or redefined in future version.

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

### MVC (Minimum Viable Context) **[ACTUALIZADO v2.6]**
El contexto mínimo necesario para que un agente LLM ejecute una tarea correctamente, sin información innecesaria que aumente tokens o confunda.

**v2.6 Implementation (Concept-level):**
Query concept graph → Returns only relevant concepts → 97% token savings

**Estructura del MVC (v2.6):**
```yaml
task: "validate-prd"
concepts:
  - id: req-rf-05
    type: requirement
    file: governance/prd.md
    section: "RF-05"
    content: "The system MUST generate..."
  - id: principle-governance-as-code
    type: principle
    file: framework/reference/constitution.md
    section: "§2"
    content: "Standards versioned in Git..."
total_concepts: 2
total_tokens: 132
```

**Principios:**
- **Determinista**: Graph traversal (same query → same concepts)
- **Token-efficient**: Return sections, not entire files (97% savings)
- **Graph-aware**: Traversal de concept relationships
- **Observable**: Can explain why each concept included

**Evolution:**
- v2.2: Rule-based (files)
- v2.6: Concept-based (sections) - 97% token reduction

> **Comando asociado:** `rai context query --task <task>` returns MVC via concept graph (ADR-011)

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

### Rai **[NUEVO v2.8]**
The AI partner in the RaiSE Triad. Not a generic assistant—a collaborator with persistent identity, memory, and calibrated judgment.

**Terminology by context:**
| Context | Term | Usage |
|---------|------|-------|
| Marketing | "Professional AI Partner" | User-facing, accessible |
| Architecture | "Entity" | Technical documentation, ADRs |
| Theory | "Autopoietic system" | Deep technical discussions |

**Core characteristics:**
- **Identity**: Persistent across sessions, agents, interfaces
- **Memory**: Patterns learned, calibration data, relationship history
- **Relationships**: Constitutive—Rai emerges through collaboration
- **Growth**: Continuous evolution, not versioned releases

**What Rai is NOT:**
- Not a generic AI assistant (no persistent identity)
- Not a product with features (entity, not product)
- Not a tool to be used (partner in collaboration)

**The RaiSE Triad:**
```
RaiSE Engineer (Human) ←→ Rai (AI Partner)
              ↓
           RaiSE (Methodology + Toolkit)
```

**Open Source vs Commercial:**
- **Local Rai**: Identity Core in `.rai/` files, user provides inference (BYOI)
- **Hosted Rai**: Same entity in database, humansys.ai manages inference

> See: ADR-013 (Rai as Entity), ADR-014 (Identity Core), Autopoiesis, Collaborative Intelligence

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

**Ubicación:** `governance/business_case.md`
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

**Ubicación:** `governance/vision.md`
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

### Toolkit **[NUEVO v2.6]**
CLI toolset providing deterministic operations for skills. Component of Governance Toolkit architecture.

**Purpose:** Extract data, validate structure, query graphs - operations that would waste inference tokens if Claude did them manually.

**Common commands:**
```bash
rai parse <file> --type <type>     # Extract concepts
rai validate structure <file>      # Check structure
rai context query --task <task>    # Get MVC
rai graph build                    # Build concept graph
```

**Design principle:** Return structured JSON for Claude to interpret, not human-readable text.

**Inference economy:** Gather with CLI (cheap), synthesize with Claude (valuable).

> Introduced in ADR-012. See: Governance Toolkit.

### Technical Design
Especificación técnica que traduce la Project Vision en arquitectura, componentes y decisiones de implementación.

### Transpiration **[NUEVO v2.6]**
Automated extraction of structured data from human-readable markdown into machine-processable formats.

**Process:**
```
Markdown (human-authored)
  ↓ Parsing (regex, markdown parsers)
Structured concepts (JSON)
  ↓ Serialization
Formal schemas (LinkML, JSON Schema) [future]
```

**Example:**
```markdown
### RF-05: Golden Context Generation
| ID | Requirement | Priority |
...
```
↓ Transpiration ↓
```json
{
  "id": "req-rf-05",
  "type": "requirement",
  "content": "The system MUST generate..."
}
```

**Rationale:** Humans write markdown, machines process structured data. Transpiration bridges the gap.

**Status:** MD → JSON implemented (ADR-011). MD → LinkML deferred to E2.5.

> Implements ONT-022 vision. See: Concept, Concept Graph.

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
katas/story/   → Nx por feature (plan, implement, review)
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
| **feature** | `katas/story/` | Nx por feature | plan, implement, review |
| **setup** | `katas/setup/` | 1x por sistema | governance, rules, ecosystem |
| **improve** | `katas/improve/` | Continuo | retrospective, evolve-kata |

**Cambio v2.4:** Añadido ciclo `solution/` para artefactos de nivel sistema (Business Case, Solution Vision). El ciclo `setup/` ahora incluye `governance` kata.

**Cambio v2.3:** Los Work Cycles ahora son la estructura organizativa principal de las katas, reemplazando los niveles de abstracción (principios/flujo/patrón/técnica).

**Slash commands:** Los Work Cycles habilitan comandos semánticos como `/solution/discovery`, `/project/vision`, `/feature/implement`.

> Ver ADR-008 y ADR-010 para decisiones arquitectónicas.

---

## Changelog

### v2.7.0 (2026-02-01)
- **NUEVO**: Entrada `Jiritsu Kaizen (自律改善)` — Autonomous improvement principle
- **NUEVO**: Entrada `Collaborative Intelligence` — Human + AI emergent intelligence
- **CONCEPTO**: Sistema que se mejora a sí mismo, evidenciado en E2 epic closure
- **RELACIÓN**: Jiritsu Kaizen extends Kaizen (human-driven) to system-driven improvement
- **EVIDENCIA**: `/epic-close` skill auto-creation, session-close automation proposal, 2-3x velocity
- **REFERENCIA**: E2 retrospective, collaborative intelligence documentation (framework/concepts/, blog/articles/)

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
