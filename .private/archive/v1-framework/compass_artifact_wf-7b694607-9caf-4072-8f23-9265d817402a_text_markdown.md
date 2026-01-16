# Ontologías modernas de Agentic AI para el Framework RaiSE

El ecosistema de desarrollo asistido por IA ha convergido en 2025 hacia un conjunto de ontologías dominantes que RaiSE puede adoptar estratégicamente. **MCP de Anthropic emerge como el estándar de facto** para integración de herramientas, mientras que la terminología de **Andrew Ng** (Reflection, Planning, Tool Use, Multi-Agent) ofrece accesibilidad inmediata para fundadores técnicos. La comunidad ha evolucionado de "prompt engineering" a **"context engineering"**, y de "vibe coding" casual hacia **"vibe engineering"** profesional—reflejando la maduración del campo hacia prácticas responsables que RaiSE ya incorpora con sus principios Lean.

---

## Glosario comparativo: mapeo de conceptos RaiSE a estándares existentes

La siguiente tabla mapea los cinco conceptos core de RaiSE a la terminología establecida en los principales frameworks y comunidades. Este análisis revela oportunidades tanto de **adopción directa** como de **diferenciación estratégica**.

| Concepto RaiSE | MCP | LangChain/LangGraph | CrewAI | SDD (spec-kit/Kiro) | Lean AI | Comunidad |
|----------------|-----|---------------------|--------|---------------------|---------|-----------|
| **Constitution** | Prompts (templates server-controlled) | System prompts, Memory (procedural) | Backstory + Goal | Constitution (spec-kit), Steering files (Kiro) | Estandarización de productos de datos | CLAUDE.md, .cursorrules, AGENTS.md |
| **Rule** | Tools annotations, Guardrails | Runnable constraints, Assertions (DSPy) | Constraints, Process rules | Constraints en specs | Principios, Límites de WIP | Guardrails, Custom instructions |
| **Kata** | — | Evaluation metrics (DSPy) | Task patterns | — | Kaizen iterations, PDCA | TDD cycles, Validation loops |
| **DoD Fractal** | Elicitation (user confirmation) | Conditional edges, Checkpoints | Human_input, Approval gates | Validation criteria | Quality gates, Pull boundaries | HITL checkpoints, Approval gates |
| **Spec** | Resources (structured context) | State (TypedDict) | Task description + expected_output | Spec document, PRD | Value stream definition | Spec-first, Contract-first |

### Análisis de alineamiento

**Constitution** tiene el mapping más fuerte—todos los frameworks reconocen la necesidad de un "documento de principios" que guíe al agente. MCP lo llama **Prompts** (templates reutilizables), spec-kit usa exactamente **Constitution** (principios inmutables), y la comunidad ha estandarizado archivos como **CLAUDE.md** y **AGENTS.md**. RaiSE puede mantener "Constitution" como término distintivo o adoptar el emergente estándar de **AGENTS.md**.

**Rule** mapea directamente a **Guardrails** en la comunidad y **Assertions** en DSPy—el concepto está bien establecido pero la terminología varía. La palabra "Rule" es clara y adoptable.

**Kata** no tiene equivalente directo en ningún framework de agentes, representando una oportunidad de diferenciación. DSPy's evaluation loops y el concepto Lean de **Kaizen iterations** son los más cercanos. Kata captura algo que los frameworks no nombran: ejercicios deliberados de mejora continua.

**DoD Fractal** corresponde conceptualmente a los **Approval Gates** de HITL y **Checkpoints** de LangGraph, pero el aspecto "fractal" (validación a múltiples niveles) es único de RaiSE y alineado con Lean. 

**Spec** tiene tracción fuerte con los nuevos tools de Amazon (Kiro) y GitHub (spec-kit), aunque existe tensión entre "spec" como documento temporal vs "spec-as-source" permanente.

---

## Ontología propuesta para RaiSE

Basándose en el análisis de frameworks, papers, y terminología de early adopters, propongo una ontología de tres niveles que preserva los principios Lean mientras usa lenguaje reconocible por la comunidad.

### Nivel 1: Infraestructura (Protocol layer)

Adoptar la ontología **MCP** para la capa de integración:

| Primitivo MCP | Función en RaiSE | Justificación |
|---------------|------------------|---------------|
| **Tools** | Acciones que el agente puede ejecutar | Universal, adoptado por OpenAI, LangChain, CrewAI |
| **Resources** | Contexto estructurado (codebase, docs) | Diferenciador MCP vs function calling |
| **Prompts** | Templates reutilizables ≈ Constitution fragments | Permite composición modular |
| **Sampling** | Cuando el servidor necesita razonamiento LLM | Único de MCP, habilita agentic patterns |

**Recomendación**: RaiSE debe ser **MCP-native**. MCP tiene **11,000+ servers**, soporte nativo en Claude, VS Code, Cursor, y ahora OpenAI. Es el "LSP de AI"—un estándar que ganó.

### Nivel 2: Orquestación (Workflow layer)

Adoptar los **4 Agentic Patterns de Andrew Ng** como vocabulario de diseño:

| Patrón | Descripción | Aplicación RaiSE |
|--------|-------------|------------------|
| **Reflection** | Agente examina y mejora su output | Code review automático, self-critique antes de commit |
| **Tool Use** | Agente decide qué herramientas invocar | Integración MCP, ejecución de tests, linting |
| **Planning** | Descomposición de tareas complejas | Sprint planning asistido, task breakdown |
| **Multi-Agent** | Agentes especializados colaboran | Crews para diferentes aspectos (code, test, docs) |

**Justificación**: Ng eligió estos términos por accesibilidad deliberada. Mapean directamente a conceptos de desarrollo de software que fundadores técnicos ya conocen. "Reflection" = code review, "Planning" = sprint planning.

### Nivel 3: Calidad y Governance (Quality layer)

Aquí RaiSE puede diferenciarse combinando Lean con terminología emergente:

| Concepto RaiSE | Terminología Propuesta | Origen |
|----------------|------------------------|--------|
| Constitution | **Constitution** o **AGENTS.md** | Mantener (spec-kit valida) o adoptar estándar comunidad |
| Rule | **Guardrail** o **Constraint** | Comunidad enterprise, DSPy |
| Kata | **Kata** (diferenciador) | Lean, sin equivalente en AI |
| DoD Fractal | **Validation Gate** (nivel) + **Completion Criteria** | HITL patterns + Lean |
| Spec | **Spec** (adoptar) | SDD movement, alta tracción |

### Diagrama de ontología propuesta

```
┌─────────────────────────────────────────────────────────────────┐
│                    RaiSE LEAN AI FRAMEWORK                      │
├─────────────────────────────────────────────────────────────────┤
│  GOVERNANCE LAYER                                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │
│  │ Constitution│ │ Guardrails  │ │    Specs    │                │
│  │ (AGENTS.md) │ │ (Rules)     │ │ (Contracts) │                │
│  └─────────────┘ └─────────────┘ └─────────────┘                │
├─────────────────────────────────────────────────────────────────┤
│  QUALITY LAYER                                                   │
│  ┌─────────────────────┐ ┌─────────────────────┐                │
│  │   Validation Gates  │ │       Katas         │                │
│  │   (DoD Fractal)     │ │ (Continuous Improve)│                │
│  └─────────────────────┘ └─────────────────────┘                │
├─────────────────────────────────────────────────────────────────┤
│  ORCHESTRATION LAYER (Andrew Ng Patterns)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │Reflection│ │ Tool Use │ │ Planning │ │Multi-Agt │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
├─────────────────────────────────────────────────────────────────┤
│  PROTOCOL LAYER (MCP)                                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │  Tools   │ │Resources │ │ Prompts  │ │ Sampling │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Recomendaciones de naming para términos RaiSE

Cada término actual se evalúa en tres dimensiones: **reconocimiento** (¿la comunidad lo entiende?), **diferenciación** (¿aporta valor único?), y **acción recomendada**.

### Constitution

| Dimensión | Evaluación |
|-----------|------------|
| Reconocimiento | ⚡ Medio-alto. spec-kit de GitHub usa exactamente "Constitution" |
| Diferenciación | ⚡ Medio. CLAUDE.md y AGENTS.md son más conocidos |
| **Recomendación** | **MANTENER o renombrar a "AGENTS.md"** |

La comunidad ha estandarizado archivos de configuración con nombres específicos: `.cursorrules` (Cursor), `CLAUDE.md` (Claude Code), `AGENTS.md` (Cline y otros). Si RaiSE quiere máxima adopción, considerar usar el formato **AGENTS.md** con la estructura de Constitution. Alternativamente, mantener "Constitution" dado que spec-kit lo valida.

### Rule

| Dimensión | Evaluación |
|-----------|------------|
| Reconocimiento | ⚡ Medio. Genérico pero claro |
| Diferenciación | 🔴 Bajo. Muchos términos compiten |
| **Recomendación** | **Renombrar a "Guardrail"** |

"Guardrail" tiene tracción significativa en enterprise AI y comunidades de seguridad. Es más específico que "Rule" y connota protección activa. DSPy usa "Assertions" para el mismo concepto, pero Guardrail es más accesible.

### Kata

| Dimensión | Evaluación |
|-----------|------------|
| Reconocimiento | ⚡ Medio. Conocido en comunidad Lean/XP |
| Diferenciación | ✅ Alto. **Ningún framework de AI usa este término** |
| **Recomendación** | **MANTENER (diferenciador estratégico)** |

Kata representa mejora continua deliberada—un concepto que los frameworks de agentes no nombran. DSPy tiene "Optimizers" pero son automatizados; Kata implica práctica humana + AI. Este término posiciona a RaiSE como Lean-native.

### DoD Fractal

| Dimensión | Evaluación |
|-----------|------------|
| Reconocimiento | 🔴 Bajo. Compuesto, no estándar |
| Diferenciación | ✅ Alto. Concepto valioso, nombre confuso |
| **Recomendación** | **Renombrar a "Validation Gates" + "Completion Criteria"** |

La comunidad HITL usa "Approval Gates" y "Checkpoints". El aspecto "fractal" (validación a múltiples niveles) es valioso pero el nombre confunde. Propuesta: usar **"Validation Gates"** para los puntos de control, con **"Completion Criteria"** para los criterios en cada nivel. El concepto de fractalidad se explica en documentación sin requerir un término compuesto.

### Spec

| Dimensión | Evaluación |
|-----------|------------|
| Reconocimiento | ✅ Alto. SDD movement, Kiro, spec-kit |
| Diferenciación | 🔴 Bajo. Término estándar |
| **Recomendación** | **ADOPTAR (el término ha ganado)** |

Martin Fowler, Amazon (Kiro), GitHub (spec-kit), y Thoughtworks han adoptado "Spec" como el artefacto intermedio entre idea y código. RaiSE debe usar este término exactamente.

### Resumen de renaming

| Término Actual | Recomendación | Justificación |
|----------------|---------------|---------------|
| Constitution | Mantener o → AGENTS.md | spec-kit valida; AGENTS.md es estándar comunidad |
| Rule | → **Guardrail** | Tracción enterprise, más específico |
| Kata | **Mantener** | Diferenciador único, raíz Lean |
| DoD Fractal | → **Validation Gates** | HITL standard, más claro |
| Spec | **Adoptar** | SDD movement ganó |

---

## Frameworks y papers clave para referenciar

Los siguientes recursos representan la base canónica que RaiSE debería citar y alinearse.

### Papers fundamentales

| Paper | Año | Contribución clave | URL |
|-------|-----|-------------------|-----|
| **ReAct: Synergizing Reasoning and Acting** | 2022 | Define el loop Thought-Action-Observation usado por todos los frameworks | arxiv.org/abs/2210.03629 |
| **Chain-of-Thought Prompting** | 2022 | "Let's think step by step"—patrón universal de razonamiento | arxiv.org/abs/2201.11903 |
| **Constitutional AI** (Anthropic) | 2022 | Base teórica para governance de AI, inspiración para "Constitution" | anthropic.com/research |
| **DSPy: Compiling Declarative Language Model Calls** | 2023 | Signatures y optimizers—programación declarativa de LLMs | arxiv.org/abs/2310.03714 |

### Documentación oficial de frameworks

| Recurso | Relevancia para RaiSE |
|---------|----------------------|
| **MCP Specification (2025-06-18)** | Ontología formal de primitivos (Tools, Resources, Prompts, Sampling) | modelcontextprotocol.io/specification |
| **LangGraph Documentation** | State management, nodes/edges, checkpointers | docs.langchain.com/langgraph |
| **CrewAI Documentation** | Multi-agent patterns (Crews, Roles, Tasks) | docs.crewai.com |
| **DSPy Documentation** | Signatures, modules, optimizers para governance | dspy.ai |

### Blog posts canónicos

| Autor | Post | Por qué importa |
|-------|------|-----------------|
| **Andrew Ng** | "Agentic Patterns" (DeepLearning.AI, 2025) | Define los 4 patrones que la industria ha adoptado |
| **Simon Willison** | "Vibe Engineering" (Oct 2025) | Distingue coding casual de profesional; simonwillison.net |
| **Martin Fowler / Thoughtworks** | "Exploring SDD Tools" (2025) | Análisis crítico de Kiro, spec-kit, Tessl; martinfowler.com |
| **Anthropic** | "Claude Code Best Practices" (2025) | Patrones de producción para coding agents; anthropic.com/engineering |
| **Chip Huyen** | "Agents" (Jan 2025) | Taxonomía de AI engineering vs ML engineering; huyenchip.com |

### Recursos Lean + AI

| Recurso | Contribución |
|---------|-------------|
| **DORA 2025 State of AI-Assisted Development** | VSM como "force multiplier", métricas DORA aplicadas a AI |
| **Artefact "Lean AI" Framework** | Los 7 desperdicios traducidos a proyectos AI |
| **Poppendieck "Lean Software Development"** | Base teórica original que RaiSE debe citar |

### Comunidades a monitorear

| Comunidad | Valor |
|-----------|-------|
| **MCP Discord/GitHub** | Estándares emergentes, servers para desarrollo |
| **r/LocalLLaMA** (~588k miembros) | Terminología técnica, self-hosting |
| **Latent Space** (swyx) | "AI Engineer" community, tendencias |
| **Cursor Discord** | Workflows de practitioners |

---

## Waste categories específicas para AI development

La investigación identificó categorías de desperdicio que RaiSE puede incorporar a su modelo Lean:

| Waste Lean | Equivalente AI Development | Métrica |
|------------|----------------------------|---------|
| **Sobreproducción** | Output verboso innecesario, over-engineering de prompts | Tokens por resultado útil |
| **Transporte** | Context switching entre herramientas (devs usan 2-3 simultáneamente) | Cambios de herramienta/hora |
| **Inventario** | Contexto cacheado no utilizado, embeddings redundantes | Cache hit rate |
| **Movimiento** | Re-prompting, iteraciones de prompt | Prompts por resultado aceptable |
| **Espera** | Latencia de API, colas | Time to first token |
| **Defectos** | **Hallucinations** (23% promedio), código incorrecto | Hallucination rate, rework rate |
| **Sobreprocesamiento** | Usar modelos caros para tareas simples | Costo por task completada |

**Hallazgo clave del estudio Qodo 2025**: El **65% de los desarrolladores** reporta que "missing context" causa más problemas que las alucinaciones. Esto valida el enfoque de RaiSE en Specs y Constitution como artefactos de contexto.

---

## Métricas recomendadas para RaiSE

Basándose en DORA 2025 y DX AI Measurement Framework:

### Métricas de velocidad (Lead Time con AI)

| Métrica | Descripción | Benchmark |
|---------|-------------|-----------|
| **Lead Time for Changes** | Commit → producción | AI acelera coding pero puede crear cuellos de botella downstream |
| **Re-prompting Rate** | Iteraciones para output aceptable | <3 ideal |
| **Context Adherence** | Alineamiento con spec proporcionada | >85% target |

### Métricas de calidad

| Métrica | Descripción | Benchmark |
|---------|-------------|-----------|
| **Hallucination Rate** | % de información fabricada | <10% target (mejor modelos: ~3%) |
| **Rework Rate** | Código modificado post-merge | Nuevo en DORA 2025, clave para AI code |
| **Change Failure Rate** | % de deploys que causan fallas | 30% de devs no confían en output AI |

### La paradoja AI (DORA 2025)

A pesar de mejoras en calidad de código (+3.4%) y documentación (+7.5%), equipos con alta adopción de AI experimentan **-7.2% en estabilidad de delivery**. Causa raíz: AI tienta a abandonar principios de small batches. **RaiSE puede posicionarse como el antídoto** con su enfoque en DoD Fractal / Validation Gates.

---

## Conclusiones y recomendaciones estratégicas

**La ontología de RaiSE está bien posicionada** pero puede beneficiarse de ajustes tácticos. MCP ha ganado como estándar de integración—RaiSE debería ser MCP-native. Los 4 patrones de Andrew Ng ofrecen vocabulario accesible para la capa de orquestación. En la capa de calidad, RaiSE tiene diferenciadores únicos.

**Tres acciones inmediatas**:

1. **Adoptar MCP como protocol layer** — Los 11,000+ servers y soporte de todos los IDEs principales hacen de MCP el estándar inevitable. RaiSE Tools, Resources, y Prompts deberían mapearse a primitivos MCP.

2. **Renombrar selectivamente** — "Guardrail" por Rule, "Validation Gates" por DoD Fractal. Mantener "Constitution" y "Kata" como diferenciadores. Adoptar "Spec" del movimiento SDD.

3. **Posicionar Kata como innovación** — Ningún framework de AI tiene un equivalente a Kata. RaiSE puede liderar definiendo "AI Kata" como práctica de mejora continua deliberada para prompts, agents, y workflows.

El ecosistema ha madurado de "vibe coding" hacia "vibe engineering"—de prácticas casuales hacia profesionales. RaiSE, con sus raíces Lean, está naturalmente alineado con esta evolución hacia responsabilidad y calidad sistemática. La oportunidad es posicionarse como el framework que trae disciplina Lean al desarrollo AI-asistido, usando terminología que early adopters ya reconocen.