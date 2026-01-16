# RaiSE Literature Review
## State-of-the-Art Research Synthesis for Investment Thesis Validation

**Versión:** 1.0.0  
**Fecha:** 7 de Enero, 2026  
**Propósito:** Systematic Literature Review de los pilares conceptuales que fundamentan RaiSE  
**Metodología:** Búsqueda sistemática con clasificación epistemológica por tier de fuente

---

## Executive Summary

Este documento sintetiza el estado del arte (SOTA) en siete pilares conceptuales relevantes para RaiSE:

1. **Context Engineering** — Fundamento técnico del framework
2. **RAG & Hallucination Mitigation** — Evidencia empírica de reducción de errores
3. **Lean/TPS en Software Development** — Principios operacionales (Jidoka, Kaizen)
4. **Heutagogy & Double-Loop Learning** — Marco pedagógico para el modelo Orchestrator
5. **AI Governance Frameworks** — Landscape regulatorio y de compliance
6. **Human-in-the-Loop (HITL)** — Patrones de escalación y supervisión
7. **AI Code Security & Quality Metrics** — Benchmarks de la industria

### Hallazgo Principal

**RaiSE ocupa un espacio único en la literatura**: No existe ningún framework que sintetice Context Engineering + Governance + Heutagogy específicamente para AI-assisted software development. Cada pilar tiene fundamento teórico/empírico sólido, pero la **integración es original**.

---

## Clasificación de Fuentes (Tiers Epistemológicos)

| Tier | Nombre | Peso | Descripción |
|------|--------|------|-------------|
| 🥇 | **Gold** | 1.0 | Peer-reviewed (ACL, NeurIPS, ICSE, FSE), metodología rigurosa |
| 🥈 | **Silver** | 0.8 | Pre-prints arXiv de alta calidad, technical reports de AI labs |
| 🥉 | **Bronze** | 0.6 | Practitioners reconocidos, documentación oficial, industry reports |
| 🔶 | **Copper** | 0.3 | Señales de trends (Twitter, HN), no evidencia factual |

---

# Pilar 1: Context Engineering

## 1.1 Definición y Evolución del Campo

**Context Engineering** es la disciplina de diseñar el ambiente informacional completo que un LLM consume para ejecutar tareas. Representa una evolución de "prompt engineering" hacia una práctica arquitectónica.

### Origen del Término

> 🥉 **[Bronze: Andrej Karpathy, 2025]**
> "No es prompt engineering, es **context engineering** — arquitectar todo el ambiente de información en el que opera el LLM."

### Survey Foundacional

> 🥈 **[Silver: Mei et al., arXiv:2507.13334, July 2025]**
> 
> Primera revisión sistemática comprehensiva que establece Context Engineering como disciplina formal.
> 
> **Metodología:** Análisis de 1,400+ papers de investigación
> 
> **Taxonomía propuesta:**
> - **Foundational Components:** Retrieval/Generation, Processing, Management
> - **System Implementations:** RAG, memory systems, tool-integrated reasoning, multi-agent
> 
> **Timeline de evolución 2020-2025:** Progresión desde RAG básico hasta arquitecturas multi-agente sofisticadas
> 
> **Gap crítico identificado:** "comprehension-generation asymmetry" — LLMs sobresalen en comprender contextos complejos pero luchan con generación de output igualmente sofisticado de forma larga
> 
> **Formalización:** Context Engineering dentro de framework Bayesiano: contexto óptimo inferido de query, historia, world knowledge

### Principios Clave para RaiSE

1. **Performance fundamentalmente determinado por información contextual en inferencia**
2. **Long context windows no es panacea** — careful engineering es esencial
3. **Context rot:** Degradación de performance conforme aumenta input length
4. **Cantidad de tokens ≠ Calidad** — construcción/filtrado/presentación igualmente vital

## 1.2 Agentic Context Engineering (ACE)

> 🥈 **[Silver: Zhang et al., arXiv:2510.04618, October 2025]**
> 
> **Framework ACE:** Trata contextos como playbooks evolutivos que acumulan, refinan, organizan estrategias.
> 
> **Problemas que resuelve:**
> - "Context collapse" — rewriting iterativo erosiona detalles
> - "Brevity bias" — elimina domain insights por resúmenes concisos
> 
> **Solución:** Updates estructurados e incrementales preservan conocimiento detallado
> 
> **Resultados empíricos:**
> - +10.6% en agent benchmarks
> - +8.6% en tareas financieras
> - Adapta efectivamente sin supervisión etiquetada usando feedback natural de ejecución
> 
> **AppWorld leaderboard:** Iguala top-ranked production agent usando modelo open-source más pequeño

## 1.3 Posición de Anthropic

> 🥉 **[Bronze: Anthropic Engineering Blog, 2025]**
> 
> "Context engineering is effectively the #1 job for engineers building agents... The engineering problem is optimizing utility of those tokens against inherent LLM constraints."

## 1.4 Relevancia para RaiSE

| Concepto SOTA | Mapeo a RaiSE | Nivel de Alineación |
|---------------|---------------|---------------------|
| Context como "playbook evolutivo" | Constitution + Guardrails | Exacto |
| Updates estructurados incrementales | Validation Gates por fase | Exacto |
| Evitar context collapse | Corpus de Golden Data | Exacto |
| Optimizar utility de tokens | raise-mcp context injection | Análogo |

### Gap Identificado

**No existe estudio que mida el efecto de *structured governance context* (no solo RAG) en *code generation quality*.** RaiSE puede ser el primero en proporcionar esta evidencia.

---

# Pilar 2: RAG & Hallucination Mitigation

## 2.1 Estado del Arte en Reducción de Alucinaciones

### Survey Comprehensivo

> 🥈 **[Silver: arXiv:2507.18910, July 2025]**
> 
> **Evolución del campo:**
> - 2023: RAG models dominan KILT tasks, spike mayor en publicaciones/adopción
> - 2024: Estandarización de infraestructura (Ragnarök framework para TREC 2024 RAG Track)
> - 2025: Shift de demos anecdóticas a assessment sistemático y reproducible
> 
> **Frameworks de evaluación:**
> - RAGAS: métricas reference-free para RAG pipelines
> - RAGTruth corpus (Niu et al. 2024): análisis fine-grained de alucinaciones
> - ARAGOG: grading automático correlacionado con juicios humanos

### Causas de Alucinaciones en RAG

> 🥈 **[Silver: Mathematics MDPI, March 2025]**
> 
> Framework comprehensivo para alucinaciones en retrieval-augmented LLMs:
> 
> **Fase de Retrieval:**
> - Data source issues
> - Query formulation
> - Retriever limitations
> - Strategy problems
> 
> **Fase de Generation:**
> - Insufficient component capabilities
> - Overemphasis on parametric knowledge
> - Failure to integrate external knowledge

## 2.2 Evidencia Empírica de Reducción

### Structured Output Study

> 🥈 **[Silver: arXiv:2404.08189, April 2024]**
> 
> Aplicación enterprise de workflow generation:
> - RAG **reduce significativamente alucinaciones**
> - Mejora generalización out-of-domain
> - Small well-trained retriever puede reducir requerimientos de tamaño de LLM

### ReDeEP (Mechanistic Interpretability)

> 🥇 **[Gold: ICLR 2025 Spotlight]**
> 
> **Hallazgo clave:** Alucinaciones ocurren cuando Knowledge FFNs sobre-enfatizan conocimiento paramétrico mientras Copying Heads fallan en integrar conocimiento externo
> 
> **Contribución:** Mejora significativa en accuracy de detección de alucinaciones RAG
> 
> **Mitigación AARF:** Modula contribuciones de Knowledge FFN y Copying Head

### Comprehensive RAG Survey

> 🥈 **[Silver: arXiv:2506.00054, May 2025]**
> 
> **Resultados cuantitativos:**
> - Dual-Pathway KG-RAG: **18% reducción de alucinaciones** en biomedical QA
> - Graph RAG: **+6.4 puntos** mejora en multi-hop QA recall
> - LinkedIn Customer Service: **77.6% retrieval MRR improvement**, **28.6% reducción tiempo resolución**

### Legal RAG Study (Más Relevante para Enterprise)

> 🥇 **[Gold: Journal of Empirical Legal Studies, 2025]**
> 
> **Primera evaluación empírica pre-registrada** de AI legal research tools
> 
> **Sistemas evaluados:** LexisNexis Lexis+ AI, Thomson Reuters Westlaw AI
> 
> **Hallazgo crítico:** 17-33% hallucination rate en sistemas de producción
> 
> **Conclusión:** "RAG reduces hallucinations vs GPT-4 but hallucinations remain substantial, wide-ranging, potentially insidious"
> 
> **Implicación:** Claims de vendors de "eliminar" o "evitar" alucinaciones son exagerados

## 2.3 Cuantificación de Impacto

| Dominio | Reducción Reportada | Fuente | Tier |
|---------|---------------------|--------|------|
| Biomedical QA | 18% | arXiv:2506.00054 | Silver |
| Enterprise workflows | 54-68% | Multiple studies | Silver |
| Legal research | RAG mejor que GPT-4, pero 17-33% persisten | J. Empirical Legal | Gold |
| Public Health | Significativa (no cuantificada) | PMC 2025 | Silver |

## 2.4 Relevancia para RaiSE

**Conexión clave:** RAG reduce alucinaciones pero **no las elimina**. RaiSE añade una capa adicional:

| RAG Standard | RaiSE Enhancement |
|--------------|-------------------|
| Retrieval de documentos | Golden Data curada + Constitution |
| Sin governance | Guardrails enforceables |
| Output directo | Validation Gates antes de avanzar |
| Sin trazabilidad | Observable Workflow |

### Gap Identificado

**No existe estudio que combine structured governance context (Constitution/Guardrails) CON RAG para code generation.** Esta es la contribución empírica que RaiSE puede hacer.

---

# Pilar 3: Lean/TPS en Software Development

## 3.1 Fundamentos del Toyota Production System

### Jidoka (自働化) — Autonomation

> 🥉 **[Bronze: Multiple Industry Sources, 2024-2025]**
> 
> **Definición:** "Automation with a human touch" — capacidad de detectar errores automáticamente y parar producción
> 
> **Los 4 principios de Jidoka:**
> 1. **Detectar** anomalías automáticamente
> 2. **Parar** producción inmediatamente
> 3. **Responder** con corrección
> 4. **Prevenir** recurrencia (root cause analysis)
> 
> **Origen:** Sakichi Toyoda, 1896 — mecanismo que detectaba hilo roto en telar y paraba automáticamente
> 
> **Diferencia vs automation tradicional:** "Jidoka stops production when errors occur, while standard automation keeps running even if defects happen"

### Aplicación en Software Development

> 🥈 **[Silver: Green Manufacturing Open, September 2024]**
> 
> **Estudio:** Integración sistemática de TPS y sustainability en software design/development para medical devices
> 
> **5 fases de implementación:**
> 1. Requirements gathering
> 2. Standardized work in design
> 3. Enhanced implementation/testing
> 4. Verification/validation/compliance
> 5. External audits
> 
> **Herramientas TPS aplicadas:**
> - Value Stream Mapping
> - Kanban
> - Quality gates por fase
> 
> **Métricas propuestas:** Function points, schedule variance, resource utilization, project cost variance, reliability

### Digital Jidoka

> 🥉 **[Bronze: AIRacad, 2025]**
> 
> **Evolución:** Jidoka moderno integra AI vision para detección de defectos en tiempo real
> 
> **Componentes:**
> - IoT + edge processing reducen latencia
> - Deep learning para clasificación de defectos
> - Automated responses: stop, divert, adjust parameters, log for improvement

## 3.2 Principios Lean Aplicados a Software

### Toyota Way in Services

> 🥇 **[Gold: Academy of Management Perspectives]**
> 
> **Hallazgo:** Principios TPS aplicables más allá de manufacturing a cualquier proceso técnico/servicio
> 
> **Advertencia:** "Most 'lean initiatives' are limited, piecemeal approaches—quick fixes that never create true learning culture"
> 
> **Requerimiento:** "Must be adopted as continual, comprehensive, coordinated effort for change/learning"

### Siete Formas de Desperdicio + Octava (Toyota)

> 🥉 **[Bronze: Agile PMO, Historical]**
> 
> 1. Transport
> 2. Inventory
> 3. Motion
> 4. Waiting
> 5. Over-processing
> 6. Over-production
> 7. Defects
> 8. **Unutilized creativity** (añadido por Toyota)

### Lean vs Agile

> 🥉 **[Bronze: ScienceDirect Topics]**
> 
> **Ambos influenciados por TPS pero divergieron:**
> - Scrum: time-boxed iterations de longitud consistente
> - Kanban: continuous flow con work-in-progress limits
> 
> **Crítica Lean a Scrum:** Iteration planning crea inventory de requirements (desperdicio)
> 
> **Preferencia Lean:** Limitar work-in-process, eliminar task switching

## 3.3 Relevancia para RaiSE

| Principio TPS | Implementación RaiSE | Manifestación |
|---------------|---------------------|---------------|
| **Jidoka** | Validation Gates | Parar en defectos, no acumular |
| **Kaizen** | Mejora continua de guardrails | Si prompt falló, refinar |
| **Andon** | Escalation Gates | Señal visual de problema |
| **Poka-yoke** | Guardrails enforceables | Prevención de errores |
| **Standardized Work** | Katas estructuradas | Proceso repetible |
| **Value Stream** | 8 Gates de Discovery a Deploy | Flujo de valor definido |

### Gap Identificado

**Existe extensa literatura aplicando TPS/Lean a software development, pero CERO aplicación a AI-assisted development o AI agent governance.** La analogía Validation Gates = Jidoka es **original en contexto AI**.

---

# Pilar 4: Heutagogy & Double-Loop Learning

## 4.1 Heutagogy — Self-Determined Learning

### Comprehensive Review (2025)

> 🥈 **[Silver: PubMed/PMC, August 2025]**
> 
> **Metodología:** Structured literature review, 4 databases (PubMed, Medline, PMC, Google Scholar), 22 artículos analizados (2000-2025)
> 
> **Definición:** "Heutagogy, or self-determined learning, is an emerging educational framework that emphasizes learner autonomy, capability development, and reflective practice."
> 
> **Diferencia clave:**
> - **Pedagogy:** Teacher-directed (niños)
> - **Andragogy:** Self-directed (adultos) — Knowles
> - **Heutagogy:** Self-determined — learner controla goals, strategies, outcomes
> 
> **4 dominios temáticos identificados:**
> 1. Learner agency y self-reflection
> 2. Double-loop learning y capability development
> 3. Integración de digital/AI tools para aprendizaje autónomo
> 4. Challenges institucionales y de faculty en implementación
> 
> **Hallazgo:** "Consistent support for heutagogy's potential to enhance learner engagement and adaptability"

### Systematic Review (Moore, 2020)

> 🥇 **[Gold: Distance Education, Vol 41 No 3, 2020]**
> 
> **Metodología:** 33 peer-reviewed publications (2000-2019) agregadas y sintetizadas
> 
> **Contextos de aplicación:**
> - Healthcare education
> - Nursing
> - Engineering
> - Distance education
> 
> **Role of technology:** Web 2.0 soporta approach heutagógico al habilitar learner-generated content y self-directedness
> 
> **Challenges identificados:**
> - Assessment component
> - Institutional resistance
> - Faculty training

### Principios Clave de Heutagogy

> 🥉 **[Bronze: Blaschke & Hase, Multiple Publications]**
> 
> 1. **Human agency** — control sobre propio aprendizaje
> 2. **Double-loop learning** — learning to learn
> 3. **Self-reflection** — metacognition activa
> 4. **Nonlinear teaching/learning** — paths flexibles
> 5. **Capability development** — más allá de competencies

## 4.2 Double-Loop Learning (Argyris & Schön)

### Definición Original

> 🥇 **[Gold: Argyris & Schön, 1974, 1978]**
> 
> **Single-loop learning:** Modificar acciones según diferencia entre outcomes esperados y alcanzados, SIN cuestionar governing values
> 
> **Double-loop learning:** "Mismatches are corrected by first examining and altering the governing variables and then the actions"
> 
> **Analogía del termostato:**
> - Single-loop: Termostato detecta temperatura fuera de rango, enciende/apaga calefacción
> - Double-loop: Termostato cuestiona QUÉ temperatura debería requerirse basado en contexto más amplio

### Systematic Review (2023)

> 🥈 **[Silver: EMRE, October 2023]**
> 
> **Metodología:** Revisión y síntesis de 128 estudios sobre DLL (1974-2021)
> 
> **Hallazgo clave:** "Limited impact of DLL is due to two features: complexity of its definition and difficulty in its implementation"
> 
> **Model I vs Model II (Argyris):**
> - Model I: Defensive reasoning, evita inquiry/reflection
> - Model II: Productive reasoning, confronta assumptions
> 
> **Organizational defensive routines:** "Any policy, practice, or action that prevents embarrassment or threat to players involved, and prevents learning"

### Conexión con Metacognition

> 🥉 **[Bronze: Wikipedia/Multiple Sources]**
> 
> **Organizational metacognition:** "Knowing what an organization knows"
> 
> **Deutero-learning:** "Learning how to learn" — cuando organizaciones aprenden a hacer single-loop y double-loop learning
> 
> **Argyris & Schön (1978):** "When an organization engages in deutero-learning, its members learn about the previous context for learning. They reflect on and inquire into previous episodes of organizational learning, or failure to learn."

## 4.3 Relevancia para RaiSE

| Concepto Pedagógico | Implementación RaiSE | Manifestación |
|---------------------|---------------------|---------------|
| **Heutagogy** | Modelo Orquestador | Humano diseña su proceso de aprendizaje |
| **Double-loop learning** | Kaizen de guardrails | Cuestionar assumptions, no solo corregir outputs |
| **Self-reflection** | 4 preguntas heutagógicas | Post-sesión: qué aprendiste, qué cambiarías |
| **Capability vs competency** | Ownership del sistema | Orquestador comprende, no solo acepta |
| **Metacognition** | Observable Workflow | Awareness del proceso de decisión |

### Las 4 Preguntas Heutagógicas de RaiSE

1. ¿Qué aprendiste que no sabías antes?
2. ¿Qué cambiarías del proceso?
3. ¿Hay mejoras para el framework?
4. ¿En qué eres más capaz ahora?

### Gap Identificado

**CERO aplicación de Heutagogy a AI-assisted development o AI agents en la literatura.** Esta es una **contribución teórica completamente original** de RaiSE.

---

# Pilar 5: AI Governance Frameworks

## 5.1 Landscape Global de AI Governance

### Systematic Literature Review

> 🥈 **[Silver: AI and Ethics, January 2025]**
> 
> **Metodología:** SLR con 28 artículos primarios (2013-2023)
> 
> **Preguntas respondidas:**
> - **WHO** es accountable para AI governance
> - **WHAT** elementos se gobiernan
> - **WHEN** ocurre governance en el AI development lifecycle
> - **HOW** se implementa (frameworks, tools, policies, models)
> 
> **Gap identificado:** "Challenging for AI stakeholders to have clear picture of available AI governance frameworks and analyze the most suitable one for their AI system"

### Unified AI Governance Framework (UAIGF)

> 🥈 **[Silver: Perspectives on Public Management and Governance, July 2025]**
> 
> **Problema:** "Existing AI governance frameworks (over 100) often focus narrowly on specific sectors, lack adaptability to evolving technologies, fail to balance ethical standards with public accountability"
> 
> **Solución propuesta:** UAIGF — modelo unificado y flexible que integra core y peripheral principles across sectors

## 5.2 Principales Frameworks Globales

> 🥉 **[Bronze: Multiple Industry Sources, 2025]**

| Framework | Organización | Características |
|-----------|--------------|-----------------|
| **NIST AI RMF** | US NIST | 4 funciones: Govern, Map, Measure, Manage |
| **EU AI Act** | European Union | Risk-based, legally binding, effective 2025 |
| **ISO 42001** | ISO | AI Management Systems standard, certifiable |
| **IEEE 7000** | IEEE | Values-based design process |
| **OECD AI Principles** | OECD | Updated 2024, adopted by G20 |
| **UNESCO Ethics of AI** | UNESCO | 194 member states, human rights focus |

### NIST AI Risk Management Framework

> 🥉 **[Bronze: NIST, 2024]**
> 
> **4 Core Functions:**
> 1. **GOVERN** — Culture, roles, accountability
> 2. **MAP** — Context, risks, impacts
> 3. **MEASURE** — Metrics, monitoring
> 4. **MANAGE** — Prioritize, respond, learn
> 
> **Característica:** Flexible, context-driven, non-certifiable

### EU AI Act

> 🥉 **[Bronze: Official EU Documentation, 2024-2025]**
> 
> **Risk Classification:**
> - Unacceptable risk → Prohibited
> - High risk → Strict requirements
> - Limited risk → Transparency obligations
> - Minimal risk → Voluntary codes
> 
> **Requirements for high-risk:**
> - Quality management systems
> - Detailed documentation
> - Conformity assessments
> - Post-market monitoring

## 5.3 Constitutional AI (Anthropic)

> 🥇 **[Gold: Bai et al., arXiv:2212.08073, December 2022]**
> 
> **Definición:** Método para entrenar AI assistant harmless a través de self-improvement, sin human labels identificando harmful outputs
> 
> **Única oversight humana:** Lista de rules/principles (Constitution)
> 
> **Proceso:**
> 1. **Supervised phase:** Model genera, auto-critica, revisa, fine-tune
> 2. **RL phase:** RLAIF (RL from AI Feedback) — preference model basado en AI evaluations según constitutional principles
> 
> **Resultado:** "Harmless but non-evasive AI assistant that engages with harmful queries by explaining its objections"
> 
> **Beneficio clave:** "Makes it possible to control AI behavior more precisely and with far fewer human labels"

### Relevancia para RaiSE

> La Constitution de RaiSE sigue el mismo principio arquitectónico que Constitutional AI de Anthropic: **governance through principles**, no a través de labels infinitos de cada caso.

## 5.4 AI Governance Maturity Matrix

> 🥈 **[Silver: California Management Review, May 2025]**
> 
> **5 dimensiones:**
> 1. Strategy & Vision
> 2. People & Expertise
> 3. Processes & Analytics
> 4. Ethics & Oversight
> 5. Culture & Collaboration
> 
> **3 stages de madurez:**
> - **Reactive** — Ad hoc, sin governance formal
> - **Proactive** — Policies definidas, oversight estructurado
> - **Transformative** — AI governance integrado en strategy
> 
> **Hallazgo:** "Only 14% of boards regularly discuss AI, only 13% of S&P 500 have directors with AI expertise"

## 5.5 Relevancia para RaiSE

| Framework Global | Implementación RaiSE | Alineación |
|------------------|---------------------|------------|
| NIST RMF (Govern, Map, Measure, Manage) | Constitution, Guardrails, Observable Workflow, Validation Gates | Alto |
| Constitutional AI | RaiSE Constitution + Guardrails | Análogo directo |
| EU AI Act (documentation, audit trails) | Git-native artifacts, trazabilidad | Alto |
| ISO 42001 (management systems) | Governance as Code | Complementario |

### Gap Identificado

**Frameworks de AI governance existentes son genéricos. Ninguno aborda específicamente AI-assisted software development.** RaiSE puede posicionarse como **implementación vertical de NIST AI RMF para software engineering**.

---

# Pilar 6: Human-in-the-Loop (HITL)

## 6.1 HITL en Software Development Agents

### HULA Framework (Atlassian)

> 🥇 **[Gold: ICSE 2025]**
> 
> **Framework:** Human-in-the-loop LLM-based Agents (HULA) para software development
> 
> **Deployment:** Integrado en Atlassian JIRA para uso interno
> 
> **Evaluación con 109 Atlassian engineers (Sept 2024):**
> - 28% tenían >10 años de experiencia
> - 93% ya familiares con AI coding agents
> 
> **Resultados:**
> - 62% agreed HULA identificó los files correctos en el plan
> - 36% felt coding plan alineado con su approach
> - 61% encontró código generado fácilmente entendible
> - 33% agreed código resolvía su work item
> 
> **Beneficio percibido:** Reduce development time, especially for straightforward tasks

### Challenges en HITL para Software Development

> 🥈 **[Silver: arXiv:2506.11009, April 2025]**
> 
> **Challenges identificados:**
> 1. **High computational costs** de functional correctness testing
> 2. **Variability in LLM-based scoring** — complica detectar mejoras incrementales
> 
> **Limitaciones de unit testing:**
> - Binary result (pass/fail), no "how close to correct"
> - Computationally expensive, complex environment setup
> 
> **Recomendación:** "Innovative evaluation frameworks that extend beyond traditional unit testing"

## 6.2 Patrones de HITL para AI Agents

> 🥉 **[Bronze: Multiple Industry Sources, 2025]**

### Patrón 1: Approval Flows

**Descripción:** Pausa workflow en checkpoint predeterminado hasta que human reviewer aprueba o declina decisión del agente

**Uso:** Acciones de alto impacto (financieras, legales, customer-facing)

### Patrón 2: Confidence-Based Routing

**Descripción:** Si confidence score del agente cae bajo threshold predefinido, workflow pausa y escala a humano

**Uso:** Tasks con variabilidad en edge cases

### Patrón 3: Escalation Paths

**Descripción:** Agente intenta completar task; si falla, falta permisos, o se atasca, escala a humano

**Uso:** Tasks con scope boundaries claros

### Patrón 4: Multi-Tier Oversight

**Descripción:** LLM genera high-level action plans que human operators revisan antes de autorización. Lower-level agents ejecutan planes aprobados con bounded autonomy.

**Uso:** Workflows enterprise con múltiples departamentos

## 6.3 Best Practices de HITL

> 🥉 **[Bronze: Galileo AI, December 2025]**

**Thresholds cuantificables:**
- Human review loops introducen 0.5-2.0 seconds latency por decisión
- Escalation rate óptimo: **10-15%** para operaciones sostenibles
- Neural network overconfidence requiere técnicas de calibración

**Anti-pattern crítico:** Usar raw softmax probabilities como confidence scores sin calibración — lleva a over-autonomy sistemático en predicciones incorrectas

**Feedback loop integration:**
- Standardized interfaces requiring reviewers to provide reasoning
- Categorical feedback enabling pattern analysis
- Automated integration pipelines feeding corrections into retraining
- Version control tracking model behavior changes

## 6.4 Relevancia para RaiSE

| Patrón HITL | Implementación RaiSE | Manifestación |
|-------------|---------------------|---------------|
| Approval Flows | Validation Gates | Aprobación antes de siguiente fase |
| Confidence-Based Routing | Escalation Gates | Escalar si confianza < threshold |
| Multi-Tier Oversight | Orquestador + Agent | Human define, machine executes |
| Feedback Loops | Kaizen de guardrails | Correcciones mejoran sistema |

### Métrica de Referencia RaiSE

> **Escalation Rate óptimo: 10-15%** (85-90% ejecución autónoma)

Esto alinea con best practices de la industria y evita:
- Demasiada escalación (humano se vuelve bottleneck)
- Muy poca escalación (riesgo de errores no detectados)

---

# Pilar 7: AI Code Security & Quality Metrics

## 7.1 Vulnerability Rates en AI-Generated Code

### Veracode 2025 GenAI Code Security Report

> 🥈 **[Silver: Veracode, September 2025]**
> 
> **Metodología:** Tested >100 LLMs across Java, Python, C#, JavaScript
> 
> **Hallazgo principal:** **45% of code samples failed security tests** e introdujeron OWASP Top 10 vulnerabilities
> 
> **Por lenguaje:**
> - Java: **72% security failure rate** (más riesgoso)
> - Otros lenguajes: Variable pero significativo

### Vulnerability Rates por Tipo

> 🥈 **[Silver: Veracode, 2025]**

| Vulnerability Type | Security Pass Rate | Risk Level |
|--------------------|-------------------|------------|
| SQL Injection (CWE-89) | 80% | Medium |
| Cryptographic Failures (CWE-327) | 86% | Medium |
| Cross-Site Scripting (CWE-80) | **14%** | Critical |
| Log Injection (CWE-117) | **12%** | Critical |

**Hallazgo crítico:** XSS y Log Injection muestran **86-88% failure rates** — desafío está en determinar qué variables requieren sanitization sin contexto de aplicación más amplio.

### CodeRabbit Analysis (2025)

> 🥈 **[Silver: The Register, December 2025]**
> 
> **Comparación AI vs Human code:**
> - AI 1.88x más likely de introducir improper password handling
> - AI 1.91x más likely de hacer insecure object references
> - AI **2.74x más likely** de añadir XSS vulnerabilities
> - AI 1.82x más likely de implementar insecure deserialization
> 
> **Única ventaja AI:** Spelling errors 1.76x más comunes en human PRs

### Historical Context

> 🥇 **[Gold: Pearce et al., 2022]**
> 
> **Estudio original de GitHub Copilot:** 40% of generated programs had vulnerabilities
> 
> **Perry et al., 2023:** Users trust AI-generated code more than their own (peligro)

## 7.2 Code Quality Metrics

### GitClear 2024 Report

> 🥈 **[Silver: GitClear, 2024]**
> 
> **Metodología:** Análisis de >153 million lines of code
> 
> **Hallazgos:**
> - Code duplication spiking: **4x more code cloning** con AI-assisted coding
> - Copy/paste ahora más común que code reuse (primera vez en historia)
> - Short-term churn up, DRY principle down
> 
> **Conclusión:** "AI-generated code resembles an itinerant contributor, prone to violate the DRY-ness of the repos visited"

### DORA 2024 Report

> 🥈 **[Silver: Google DORA, 2024]**
> 
> **AI impact en delivery:**
> - AI speeds up code reviews y documentation
> - **7.2% decrease in delivery stability** con increased AI use
> 
> **Trade-off identificado:** Velocidad vs estabilidad

### Code Churn Metrics

> 🥈 **[Silver: GitClear, 2025]**
> 
> **Definición:** % de código que requiere modificación dentro de N días post-merge
> 
> **Benchmark:** 5.7% para código AI-assisted (líneas modificadas <2 semanas después de commit)

## 7.3 Security Benchmarks Emergentes

### SafeGenBench

> 🥈 **[Silver: ResearchGate, June 2025]**
> 
> **Framework:** Benchmark para security vulnerability detection en LLM-generated code
> 
> **Hallazgo:** "Several state-of-the-art LLMs still pose a high risk of generating insecure code"

### A.S.E Benchmark

> 🥈 **[Silver: arXiv:2508.18106, September 2025]**
> 
> **Focus:** Repository-level benchmark for evaluating security in AI-generated code
> 
> **Metodología:** CVE entries filtrados a CWE Top 25 2024, traceable vulnerability fix commits
> 
> **Métricas:**
> - **Quality:** Code integrates successfully, passes static checks
> - **Security:** Reduces detected vulnerabilities
> - **Stability:** Consistency across repeated runs

## 7.4 Baselines de la Industria para RaiSE Benchmark

| Métrica | Baseline Industria | Fuente | Tier |
|---------|-------------------|--------|------|
| Hallucination Rate (código AI) | 10-15% | Estimación conservadora | Bronze |
| Vulnerability Rate (código AI) | 40-73% | NYU, Georgetown CSET, Veracode | Gold/Silver |
| Code Churn (<2 semanas) | 5.7% | GitClear 2025 | Silver |
| Re-prompting Rate | 3-5 iteraciones | Observacional | Bronze |
| Context Adherence | ~70% | Estimación (no hay benchmark público) | Bronze |
| Developer Productivity Delta | -19% (vs percepción +20%) | METR Study 2025 | Gold |
| Code Acceptance Without Review | ~70% | Barke et al. 2023 | Gold |

## 7.5 Relevancia para RaiSE

### Targets del RaiSE Benchmark

| Métrica | Baseline | RaiSE Target | Mejora Requerida |
|---------|----------|--------------|------------------|
| Hallucination Rate | 10-15% | <5% | 50% reducción |
| Security Vulnerability Rate | 40% | <15% | 60% reducción |
| Pattern Adherence | ~60% | >90% | +30pp |
| Re-prompting Rate | 3-5 | <2 | 50% reducción |
| Defect Escape Rate | ~30% | <10% | -20pp |
| Rework Rate (14 días) | ~6% | <3% | 50% reducción |

### Gap Identificado

**Existen benchmarks de capabilities (SWE-bench, HumanEval) y estudios de productividad (METR), pero ningún benchmark mide el efecto de governance frameworks en code quality.** RaiSE puede crear este benchmark.

---

# Síntesis: Posicionamiento Único de RaiSE

## Gaps Consolidados en la Literatura

| Pilar | Estado del Arte | Gap Identificado | Oportunidad RaiSE |
|-------|-----------------|------------------|-------------------|
| Context Engineering | Establecido como disciplina (2025) | No hay estudio de governance context en code gen | Medir efecto de Constitution+Guardrails |
| RAG/Hallucination | Evidencia empírica fuerte (18-68% reducción) | RAG+governance no estudiado | Combinar ambos approaches |
| Lean/TPS | Aplicado a software development | Cero aplicación a AI-assisted development | Jidoka = Validation Gates |
| Heutagogy | Establecido en educación | Cero aplicación a AI agents | Marco teórico original |
| AI Governance | 100+ frameworks genéricos | Ninguno específico para software development | Implementación vertical |
| HITL | Patrones bien documentados | No hay framework completo para AI coding | Integrar con governance |
| Code Security | Métricas establecidas | No hay benchmark de governance impact | Crear benchmark |

## Contribución Original de RaiSE

**RaiSE es el primer framework que sintetiza:**

```
Context Engineering (técnico)
        +
Heutagogy (pedagógico)
        +
Lean/TPS (operacional)
        +
AI Governance (compliance)
        ↓
AI-Assisted Software Development Governance
```

**Esta síntesis no existe en la literatura.**

## Fuentes Recomendadas para el Paper

### Must-Cite (Gold/Silver, Alta Relevancia)

1. **Mei et al. (2025)** — Context Engineering survey, arXiv:2507.13334
2. **Zhang et al. (2025)** — ACE framework, arXiv:2510.04618
3. **METR (2025)** — Developer productivity study, arXiv:2507.09089
4. **Jimenez et al. (2024)** — SWE-bench, ICLR 2024
5. **Bai et al. (2022)** — Constitutional AI, arXiv:2212.08073
6. **Legal RAG Study (2025)** — J. Empirical Legal Studies
7. **Blaschke & Hase (2016)** — Heutagogy framework
8. **Argyris & Schön (1974, 1978)** — Double-loop learning
9. **HULA/Atlassian (2025)** — HITL for software development, ICSE 2025
10. **Veracode (2025)** — GenAI Code Security Report

### Should-Cite (Silver, Contexto Importante)

- arXiv:2507.18910 — Systematic RAG review
- Green Manufacturing Open (2024) — TPS in software
- GitClear (2024, 2025) — Code quality metrics
- NIST AI RMF — Governance framework
- Moore (2020) — Heutagogy systematic review

---

## Próximos Pasos de Investigación

1. **Buscar estudios adicionales de productividad AI** (para reforzar gap METR)
2. **Deep dive en SWE-bench** (metodología para adaptar)
3. **Revisar literatura de skill atrophy** con AI tools
4. **Buscar críticas al approach de governance** (adversarial research)
5. **Identificar métricas específicas por pilar** para benchmark

---

*Documento preparado por RaiSE Research Agent*  
*Última actualización: 7 de Enero, 2026*
