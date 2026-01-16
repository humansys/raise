# RaiSE Research Backlog
## Stage 1: Grounding del Marco Teórico

**Versión:** 1.0.0  
**Fecha:** 7 de Enero, 2026  
**Propósito:** Backlog priorizado de research items para validar científicamente los claims de RaiSE
**Metodología:** Basado en Design Science Research (Hevner et al., 2004) y PRISMA-S

---

## Resumen Ejecutivo

Este backlog identifica **23 claims** del framework RaiSE que requieren grounding científico, organizados en 6 épicas de investigación. Cada item incluye:
- El claim específico de RaiSE
- La pregunta de investigación
- Fuentes iniciales a consultar (por tier)
- Criterio de éxito (qué constituye "grounding suficiente")
- Prioridad (P0-P3)
- Esfuerzo estimado

**Objetivo:** Al completar este backlog, RaiSE tendrá evidencia verificable para cada claim fundamental, permitiendo:
1. Priorización de features basada en evidencia
2. Publicación de benchmark con rigor científico
3. Diferenciación de mercado basada en fundamentos sólidos

---

## Épica 1: Lean Software Development como Fundamento
**Justificación:** RaiSE se presenta como "framework de Lean Software Development". Este claim requiere validación de que los principios TPS/Lean son aplicables y efectivos en desarrollo de software AI-asistido.

### RB-001: Validación del Lean Software Development
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "RaiSE es fundamentalmente un framework de Lean Software Development que integra agentes de IA como aceleradores del flujo de valor" (Methodology §Filosofía) |
| **Pregunta de Investigación** | ¿Existe evidencia empírica de que los principios Lean mejoran resultados en desarrollo de software? ¿Cuáles principios tienen mayor evidencia? |
| **Fuentes Tier 1 (Gold)** | Poppendieck M&T (2003, 2006) - papers originales; Petersen & Wohlin (2011) - systematic review |
| **Fuentes Tier 2 (Silver)** | DORA State of DevOps (2018-2024); Forsgren et al. "Accelerate" (2018) |
| **Fuentes Tier 3 (Bronze)** | Fowler, Humble - blog posts sobre Lean |
| **Criterio de Éxito** | ≥3 estudios empíricos que validen al menos 4 de 7 principios Lean en contexto de software |
| **Prioridad** | P0 - Fundacional |
| **Esfuerzo** | 3 días |
| **Entregable** | Literature Review + Mapeo principios Lean → RaiSE |

### RB-002: Jidoka en Desarrollo de Software
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Cada Validation Gate es un punto Jidoka: el proceso puede—y debe—detenerse si hay anomalías" (Methodology §Jidoka) |
| **Pregunta de Investigación** | ¿Existe evidencia de que "stop the line" (quality gates que bloquean avance) mejora la calidad del software? ¿Cuál es el costo en velocidad? |
| **Fuentes Tier 1 (Gold)** | Ohno, T. (1988) - Toyota Production System; Liker, J. (2004) - The Toyota Way |
| **Fuentes Tier 2 (Silver)** | Poppendieck caps. sobre Jidoka; Estudios de quality gates en CI/CD |
| **Fuentes Tier 3 (Bronze)** | Case studies de Toyota en software (Toyota Connected, Woven Planet) |
| **Criterio de Éxito** | Evidencia de aplicación de Jidoka en software + métricas de impacto |
| **Prioridad** | P0 - Core del approach |
| **Esfuerzo** | 2 días |
| **Entregable** | Ficha bibliográfica Jidoka + Gap Analysis |

### RB-003: Kaizen y Mejora Continua en AI-Assisted Development
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Si un prompt falló o el código requirió muchas iteraciones, los guardrails y katas se refinan. El sistema aprende de sus errores" (Constitution §6) |
| **Pregunta de Investigación** | ¿Existe evidencia de que la reflexión sistemática y mejora incremental de procesos AI mejora resultados en desarrollo? |
| **Fuentes Tier 1 (Gold)** | Estudios de retrospectivas en Agile; Research sobre refinamiento de prompts |
| **Fuentes Tier 2 (Silver)** | Anthropic/OpenAI technical reports sobre iteración de prompts; DSPy documentation |
| **Fuentes Tier 3 (Bronze)** | Posts de Simon Willison sobre refinamiento iterativo |
| **Criterio de Éxito** | Evidencia de que la mejora iterativa de contexto/prompts produce mejores resultados |
| **Prioridad** | P1 |
| **Esfuerzo** | 2 días |
| **Entregable** | Literature Review + Métricas de mejora |

---

## Épica 2: Heutagogía y Modelo del Orquestador
**Justificación:** RaiSE hace claims fuertes sobre el desarrollo profesional del humano y el modelo de "Orquestador vs Consumidor". Este es un diferenciador clave que requiere validación.

### RB-004: Fundamentos de Heutagogía
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "El sistema enseña a pescar, no solo entrega el pescado" (Constitution §5); Taxonomía Pedagogía→Andragogía→Heutagogía |
| **Pregunta de Investigación** | ¿Cuál es la evidencia empírica de la efectividad de la heutagogía vs andragogía? ¿Existe aplicación en contextos tecnológicos? |
| **Fuentes Tier 1 (Gold)** | Hase & Kenyon (2000) - paper original; Blaschke (2012) - systematic review en IRRODL |
| **Fuentes Tier 2 (Silver)** | Narayan & Herrington (2014) - heutagogía en educación tecnológica |
| **Fuentes Tier 3 (Bronze)** | Blog posts de practitioners aplicando heutagogía |
| **Criterio de Éxito** | Validación de que heutagogía es teoría establecida + identificación de condiciones de aplicabilidad |
| **Prioridad** | P0 - Pilar filosófico central |
| **Esfuerzo** | 3 días |
| **Entregable** | Literature Review completa + Concept Mapping a RaiSE |

### RB-005: Skill Atrophy en AI-Assisted Development
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Consumidor: Skills se atrofian" vs "Orquestador: Skills evolucionan" (Learning Philosophy §Orquestador vs Consumidor) |
| **Pregunta de Investigación** | ¿Existe evidencia de que el uso de herramientas AI causa atrofia de habilidades en desarrolladores? ¿Bajo qué condiciones? |
| **Fuentes Tier 1 (Gold)** | METR Study 2025 (-19% productividad real); Estudios de cognitive offloading |
| **Fuentes Tier 2 (Silver)** | Barke et al. (2023) - aceptación sin revisión; GitClear 2024 - code churn |
| **Fuentes Tier 3 (Bronze)** | Debates en HackerNews, posts de desarrolladores senior |
| **Criterio de Éxito** | Evidencia de atrofia + identificación de mitigaciones propuestas en literatura |
| **Prioridad** | P0 - Fundamento de la propuesta de valor |
| **Esfuerzo** | 4 días |
| **Entregable** | Gap Analysis + Synthesis de evidencia pro/contra |

### RB-006: ShuHaRi como Modelo de Maestría
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "ShuHaRi es una lente que describe cómo el Orquestador se relaciona con las Katas" (Glossary §ShuHaRi) |
| **Pregunta de Investigación** | ¿Existe validación empírica del modelo ShuHaRi en aprendizaje técnico? ¿Es aplicable fuera de artes marciales? |
| **Fuentes Tier 1 (Gold)** | Cockburn, A. - Agile Software Development (2006); Investigación sobre skill acquisition |
| **Fuentes Tier 2 (Silver)** | Dreyfus model of skill acquisition - como comparación |
| **Fuentes Tier 3 (Bronze)** | Fowler, M. - ShuHaRi (2014); Kent Beck - XP y ShuHaRi |
| **Criterio de Éxito** | Mapeo ShuHaRi ↔ Dreyfus + evidencia de uso en contextos técnicos |
| **Prioridad** | P2 |
| **Esfuerzo** | 1.5 días |
| **Entregable** | Concept Mapping + Reading List |

---

## Épica 3: Context Engineering como Disciplina
**Justificación:** RaiSE posiciona "Context Engineering" como evolución de "Prompt Engineering". Este es un claim diferenciador que requiere validación del término y la práctica.

### RB-007: Origen y Definición de Context Engineering
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Acuñado por Andrej Karpathy (2025): 'No es prompt engineering, es context engineering—arquitectar todo el ambiente de información en el que opera el LLM'" (Glossary §Context Engineering) |
| **Pregunta de Investigación** | ¿Cuál es la fuente original del término? ¿Cómo lo definen diferentes autores? ¿Existe consenso? |
| **Fuentes Tier 1 (Gold)** | Papers sobre RAG, Constitutional AI, structured prompting |
| **Fuentes Tier 2 (Silver)** | Karpathy video/post original (2025); Anthropic documentation sobre MCP |
| **Fuentes Tier 3 (Bronze)** | X/Twitter thread original de Karpathy; blogs de practitioners |
| **Criterio de Éxito** | Fuente primaria verificable + mapeo de definiciones en la industria |
| **Prioridad** | P0 - Término clave del framework |
| **Esfuerzo** | 2 días |
| **Entregable** | Ficha bibliográfica + Genealogía del término |

### RB-008: Structured Context Reduce Alucinaciones
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Contexto estructurado evita alucinaciones" (Learning Philosophy §Lean); Target: <10% hallucination rate |
| **Pregunta de Investigación** | ¿Existe evidencia de que el contexto estructurado (vs prompts ad-hoc) reduce la tasa de alucinaciones en LLMs? |
| **Fuentes Tier 1 (Gold)** | Papers sobre RAG vs base LLM; Constitutional AI (Anthropic, 2022); FActScore paper |
| **Fuentes Tier 2 (Silver)** | Technical reports de Anthropic, OpenAI sobre grounding |
| **Fuentes Tier 3 (Bronze)** | Documentación de LangChain, LlamaIndex sobre retrieval |
| **Criterio de Éxito** | ≥2 estudios cuantitativos que midan reducción de alucinaciones con contexto estructurado |
| **Prioridad** | P0 - Claim central del value proposition |
| **Esfuerzo** | 3 días |
| **Entregable** | Literature Review + Métricas de referencia |

### RB-009: Guardrails como Pattern Enforcement
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Los guardrails enforceables producen código más consistente con estándares definidos" (Benchmark Brief §H3) |
| **Pregunta de Investigación** | ¿Existe evidencia de que constraints/assertions en agentes AI mejoran adherencia a patrones? |
| **Fuentes Tier 1 (Gold)** | DSPy assertions paper; Papers sobre constrained generation |
| **Fuentes Tier 2 (Silver)** | LangChain guardrails documentation; NVIDIA NeMo Guardrails |
| **Fuentes Tier 3 (Bronze)** | GitHub spec-kit, Cursor rules documentation |
| **Criterio de Éxito** | Evidencia de que constraints mejoran adherencia + identificación de tipos de constraints efectivos |
| **Prioridad** | P1 |
| **Esfuerzo** | 2 días |
| **Entregable** | Literature Review + Taxonomía de guardrails |

---

## Épica 4: Calidad del Código AI-Generated
**Justificación:** RaiSE hace claims sobre las tasas de defectos en código AI que justifican la necesidad de governance. Estos claims requieren validación con literatura peer-reviewed.

### RB-010: Hallucination Rate en Código AI
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Hallucination Rate (código AI): 10-15%" (Benchmark Brief §Contexto de Mercado) |
| **Pregunta de Investigación** | ¿Cuál es la tasa real de alucinaciones en código generado por AI? ¿Cómo se mide? |
| **Fuentes Tier 1 (Gold)** | HumanEval papers; SWE-bench papers; Papers sobre code LLM evaluation |
| **Fuentes Tier 2 (Silver)** | Technical reports de GitHub Copilot, Cursor, Anthropic Claude Code |
| **Fuentes Tier 3 (Bronze)** | Blog posts de usuarios con métricas propias |
| **Criterio de Éxito** | ≥3 fuentes con metodología clara que reporten tasas de alucinación |
| **Prioridad** | P0 - Justifica la necesidad de RaiSE |
| **Esfuerzo** | 3 días |
| **Entregable** | Literature Review + Definición operacional de "alucinación en código" |

### RB-011: Vulnerability Rate en Código AI
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Vulnerability Rate (código AI): 40-73%" - NYU, Georgetown CSET, Veracode (Benchmark Brief) |
| **Pregunta de Investigación** | ¿Cuáles son las fuentes primarias de estos datos? ¿Qué metodología usaron? |
| **Fuentes Tier 1 (Gold)** | NYU Tandon - Perry et al. (2022); Georgetown CSET papers; CWE estudios |
| **Fuentes Tier 2 (Silver)** | Veracode State of Software Security; Snyk reports |
| **Fuentes Tier 3 (Bronze)** | Blog posts con análisis de vulnerabilidades |
| **Criterio de Éxito** | Verificar fuentes originales + extraer metodología y limitaciones |
| **Prioridad** | P0 |
| **Esfuerzo** | 2 días |
| **Entregable** | Fichas bibliográficas de cada fuente + Validación de claims |

### RB-012: Code Churn y Rework Rate
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Code Churn (revisión <2 semanas): 5.7%" - GitClear 2025 (Benchmark Brief) |
| **Pregunta de Investigación** | ¿Qué dice el estudio GitClear completo? ¿Es code churn indicador válido de calidad AI? |
| **Fuentes Tier 1 (Gold)** | GitClear 2024/2025 full reports; DORA 2025 sobre AI coding |
| **Fuentes Tier 2 (Silver)** | Estudios de code review en código AI |
| **Fuentes Tier 3 (Bronze)** | Discusiones en HackerNews sobre GitClear findings |
| **Criterio de Éxito** | Acceso a estudio completo + validación de metodología |
| **Prioridad** | P1 |
| **Esfuerzo** | 1.5 días |
| **Entregable** | Ficha bibliográfica + Crítica metodológica |

### RB-013: Developer Acceptance Without Review
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Code Acceptance Without Review: ~70%" - Barke et al. 2023 (Benchmark Brief) |
| **Pregunta de Investigación** | ¿Cuál es el estudio original? ¿Qué condiciones llevaron a ese porcentaje? |
| **Fuentes Tier 1 (Gold)** | Barke et al. (2023) - paper original; Estudios de code review behavior |
| **Fuentes Tier 2 (Silver)** | Replicaciones del estudio si existen |
| **Fuentes Tier 3 (Bronze)** | Comentarios de investigadores sobre el estudio |
| **Criterio de Éxito** | Acceso a paper original + extracción de condiciones y limitaciones |
| **Prioridad** | P0 - Justifica modelo Orquestador |
| **Esfuerzo** | 1 día |
| **Entregable** | Ficha bibliográfica completa |

---

## Épica 5: Observable Workflow y Métricas
**Justificación:** RaiSE introduce métricas específicas (re-prompting rate, context adherence, escalation rate) que requieren validación de su relevancia y benchmarks de referencia.

### RB-014: Framework MELT para AI Agents
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Observable Workflow alineado con framework MELT (Metrics, Events, Logs, Traces)" (Constitution §8) |
| **Pregunta de Investigación** | ¿Cuál es el origen del framework MELT? ¿Existen aplicaciones a AI agents? |
| **Fuentes Tier 1 (Gold)** | Sridharan, C. - Distributed Systems Observability (O'Reilly, 2018) |
| **Fuentes Tier 2 (Silver)** | OpenTelemetry documentation; Splunk MELT documentation |
| **Fuentes Tier 3 (Bronze)** | Blog posts sobre observabilidad de LLM agents |
| **Criterio de Éxito** | Validar origen de MELT + identificar gaps en aplicación a AI |
| **Prioridad** | P2 |
| **Esfuerzo** | 1.5 días |
| **Entregable** | Literature Review + Gap Analysis |

### RB-015: Re-prompting Rate como Métrica
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Re-prompting Rate: Iteraciones para output aceptable. Target: <3 ideal" (Methodology §Métricas) |
| **Pregunta de Investigación** | ¿Existe esta métrica en la literatura? ¿Cuáles son benchmarks de referencia? |
| **Fuentes Tier 1 (Gold)** | Papers sobre human-AI interaction; Estudios de prompt iteration |
| **Fuentes Tier 2 (Silver)** | Anthropic/OpenAI user research (si público) |
| **Fuentes Tier 3 (Bronze)** | Surveys de usuarios de coding assistants |
| **Criterio de Éxito** | Identificar si métrica es novel o existe + establecer benchmark empírico |
| **Prioridad** | P1 |
| **Esfuerzo** | 2 días |
| **Entregable** | Gap Analysis + Propuesta de definición operacional |

### RB-016: Context Adherence como Métrica
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Context Adherence: Alineamiento con spec. Target: >85%" (Methodology §Métricas) |
| **Pregunta de Investigación** | ¿Existe métrica similar en la literatura? ¿Cómo se mide adherencia a contexto? |
| **Fuentes Tier 1 (Gold)** | Papers sobre faithfulness en NLG; FActScore paper |
| **Fuentes Tier 2 (Silver)** | Evaluation frameworks para coding agents (SWE-bench) |
| **Fuentes Tier 3 (Bronze)** | Documentación de herramientas de evaluación |
| **Criterio de Éxito** | Mapear métricas similares en literatura + definir metodología de medición |
| **Prioridad** | P1 |
| **Esfuerzo** | 2 días |
| **Entregable** | Concept Mapping + Propuesta metodológica |

### RB-017: Escalation Rate Óptimo
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "10-15% de escalación es óptimo (85-90% ejecución autónoma). Fuente: Galileo HITL Framework, 2025" (Glossary §Escalation Gate) |
| **Pregunta de Investigación** | ¿Existe el Galileo HITL Framework? ¿Cuál es la evidencia del 10-15% óptimo? |
| **Fuentes Tier 1 (Gold)** | Papers sobre human-in-the-loop ML; Estudios de automation-autonomy tradeoffs |
| **Fuentes Tier 2 (Silver)** | Galileo documentation (verificar existencia) |
| **Fuentes Tier 3 (Bronze)** | Practitioners compartiendo ratios de escalación |
| **Criterio de Éxito** | Verificar fuente original + encontrar evidencia que soporte el rango |
| **Prioridad** | P1 |
| **Esfuerzo** | 1.5 días |
| **Entregable** | Verificación de fuente + Literature Review HITL |

---

## Épica 6: Validation Gates y Quality Assurance
**Justificación:** El sistema de 8 Validation Gates es central a RaiSE. Requiere validación de que quality gates por fase mejoran resultados.

### RB-018: Quality Gates en Desarrollo de Software
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "No existe un solo 'Done'. Cada fase tiene su propia Validation Gate que debe cruzarse antes de avanzar" (Constitution §4) |
| **Pregunta de Investigación** | ¿Existe evidencia de que quality gates por fase reducen defectos vs validación solo al final? |
| **Fuentes Tier 1 (Gold)** | Estudios de defect detection timing; Cost of defect papers (Boehm, etc.) |
| **Fuentes Tier 2 (Silver)** | DORA research sobre shift-left; Estudios de CI/CD gates |
| **Fuentes Tier 3 (Bronze)** | Case studies de implementación de gates |
| **Criterio de Éxito** | Evidencia cuantitativa de reducción de defectos con gates tempranos |
| **Prioridad** | P0 - Core del approach |
| **Esfuerzo** | 2 días |
| **Entregable** | Literature Review + Métricas de referencia |

### RB-019: Spec-Driven Development
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "SDD: Paradigma donde las especificaciones—no el código—son el artefacto primario" (Glossary §SDD) |
| **Pregunta de Investigación** | ¿Existe evidencia de que spec-first produce mejores resultados que code-first? |
| **Fuentes Tier 1 (Gold)** | Papers sobre requirements engineering; Estudios de TDD vs no-TDD |
| **Fuentes Tier 2 (Silver)** | GitHub spec-kit documentation; Amazon Kiro papers |
| **Fuentes Tier 3 (Bronze)** | Posts de practitioners sobre spec-first |
| **Criterio de Éxito** | Evidencia de correlación entre calidad de specs y calidad de código |
| **Prioridad** | P1 |
| **Esfuerzo** | 2 días |
| **Entregable** | Literature Review + Gap Analysis |

### RB-020: Human-in-the-Loop en AI Coding
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Escalation Gates: puntos donde el agente DEBE escalar al Orquestador humano" (Methodology §Escalation Gates) |
| **Pregunta de Investigación** | ¿Existe evidencia de que HITL mejora resultados en AI coding? ¿Cuándo es más valioso? |
| **Fuentes Tier 1 (Gold)** | Papers sobre HITL en ML; Estudios de human-AI collaboration |
| **Fuentes Tier 2 (Silver)** | Technical reports de coding assistants con HITL |
| **Fuentes Tier 3 (Bronze)** | Practitioners compartiendo experiencias |
| **Criterio de Éxito** | Identificar condiciones donde HITL agrega más valor |
| **Prioridad** | P1 |
| **Esfuerzo** | 2 días |
| **Entregable** | Literature Review + Taxonomía de escalación |

---

## Épica Transversal: Competencia y Diferenciación

### RB-021: Landscape de AI Governance Frameworks
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | Diferenciación de "vibe coding" y otros frameworks |
| **Pregunta de Investigación** | ¿Qué otros frameworks de governance para AI coding existen? ¿Cómo se compara RaiSE? |
| **Fuentes Tier 2 (Silver)** | GitHub spec-kit, Amazon Kiro, DSPy, LangChain, CrewAI documentation |
| **Fuentes Tier 3 (Bronze)** | Reviews y comparativas de practitioners |
| **Criterio de Éxito** | Feature matrix comparativa + identificación de gaps únicos de RaiSE |
| **Prioridad** | P1 |
| **Esfuerzo** | 3 días |
| **Entregable** | Competitive Analysis + Positioning Matrix |

### RB-022: EU AI Act y Compliance Requirements
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Observable Workflow como evidencia de compliance" (Constitution §Compromisos con Reguladores) |
| **Pregunta de Investigación** | ¿Qué requiere el EU AI Act para AI coding tools? ¿Cómo satisface RaiSE esos requisitos? |
| **Fuentes Tier 1 (Gold)** | EU AI Act texto oficial; Guidance documents de la Comisión |
| **Fuentes Tier 2 (Silver)** | Análisis legales de aplicación a AI coding |
| **Fuentes Tier 3 (Bronze)** | Interpretaciones de practitioners |
| **Criterio de Éxito** | Mapeo explícito de requisitos EU AI Act → componentes RaiSE |
| **Prioridad** | P2 |
| **Esfuerzo** | 2 días |
| **Entregable** | Compliance Matrix |

### RB-023: Model Context Protocol (MCP)
| Campo | Valor |
|-------|-------|
| **Claim RaiSE** | "Adoptamos MCP como estándar de integración con agentes" (Constitution §3) |
| **Pregunta de Investigación** | ¿Cuál es el estado actual de MCP? ¿Es realmente un estándar emergente? ¿Alternativas? |
| **Fuentes Tier 1 (Gold)** | Anthropic MCP specification oficial |
| **Fuentes Tier 2 (Silver)** | Implementaciones de MCP en la industria |
| **Fuentes Tier 3 (Bronze)** | Discusiones sobre adopción de MCP |
| **Criterio de Éxito** | Validar estado de adopción + identificar riesgos de dependencia |
| **Prioridad** | P2 |
| **Esfuerzo** | 1 día |
| **Entregable** | Technology Assessment |

---

## Priorización y Secuencia Recomendada

### Sprint 1 (Semana 1-2): Fundamentos Críticos
| ID | Item | Esfuerzo | Dependencias |
|----|------|----------|--------------|
| RB-004 | Fundamentos de Heutagogía | 3d | - |
| RB-007 | Origen de Context Engineering | 2d | - |
| RB-008 | Structured Context Reduce Alucinaciones | 3d | RB-007 |
| RB-010 | Hallucination Rate en Código AI | 3d | - |

**Criterio de éxito del sprint:** Validar los 4 claims más fundamentales de RaiSE.

### Sprint 2 (Semana 3-4): Core Mechanics
| ID | Item | Esfuerzo | Dependencias |
|----|------|----------|--------------|
| RB-001 | Validación Lean Software Development | 3d | - |
| RB-002 | Jidoka en Desarrollo de Software | 2d | RB-001 |
| RB-018 | Quality Gates en Desarrollo | 2d | RB-002 |
| RB-005 | Skill Atrophy en AI-Assisted Dev | 4d | RB-004 |

**Criterio de éxito del sprint:** Validar mecánicas core de Jidoka y Validation Gates.

### Sprint 3 (Semana 5-6): Métricas y Evidencia
| ID | Item | Esfuerzo | Dependencias |
|----|------|----------|--------------|
| RB-011 | Vulnerability Rate | 2d | RB-010 |
| RB-012 | Code Churn | 1.5d | - |
| RB-013 | Acceptance Without Review | 1d | RB-005 |
| RB-015 | Re-prompting Rate | 2d | - |
| RB-016 | Context Adherence | 2d | RB-008 |
| RB-017 | Escalation Rate Óptimo | 1.5d | - |

**Criterio de éxito del sprint:** Establecer métricas base para benchmark.

### Sprint 4 (Semana 7-8): Diferenciación y Compliance
| ID | Item | Esfuerzo | Dependencias |
|----|------|----------|--------------|
| RB-009 | Guardrails como Pattern Enforcement | 2d | RB-008 |
| RB-019 | Spec-Driven Development | 2d | - |
| RB-020 | HITL en AI Coding | 2d | RB-017 |
| RB-021 | Landscape de AI Governance | 3d | Todos los anteriores |

**Criterio de éxito del sprint:** Posicionamiento competitivo documentado.

### Backlog (Priorizar según necesidad)
| ID | Item | Esfuerzo |
|----|------|----------|
| RB-003 | Kaizen en AI-Assisted Dev | 2d |
| RB-006 | ShuHaRi como Modelo | 1.5d |
| RB-014 | Framework MELT | 1.5d |
| RB-022 | EU AI Act Compliance | 2d |
| RB-023 | MCP Assessment | 1d |

---

## Herramientas Recomendadas por Fase

### Fase de Búsqueda
| Herramienta | Uso Principal | Tier |
|-------------|---------------|------|
| **Semantic Scholar** | Búsqueda inicial, API para automatización | Free |
| **Elicit** | Síntesis de evidencia, extracción de datos | $12-42/mo |
| **Connected Papers** | Exploración de citation networks | Free (5/mo) |
| **Google Scholar** | Verificación de citas | Free |

### Fase de Síntesis
| Herramienta | Uso Principal | Tier |
|-------------|---------------|------|
| **Zotero** | Reference management | Free |
| **Obsidian** | Knowledge base con backlinks | Free |
| **Scite** | Verificación de citas (support/contrast) | $8-60/mo |

### Fase de Documentación
| Herramienta | Uso Principal | Tier |
|-------------|---------------|------|
| **Markdown** | Formato principal | - |
| **Mermaid** | Diagramas | - |
| **LaTeX** | Publicación si necesario | - |

---

## Formato de Entregables

### Literature Review
```markdown
## [Tema]: Literature Review

### Executive Summary
[3-5 oraciones con hallazgos principales]

### Estado del Arte
[Síntesis organizada temáticamente]

### Fuentes por Tier
#### Gold (Peer-reviewed)
- [Citation]: [Key finding]

#### Silver (Technical Reports)
- [Citation]: [Key finding]

### Gaps Identificados
[Qué falta en la literatura]

### Relevancia para RaiSE
[Mapeo a entidades/principios del framework]

### Nivel de Confianza
[Alto/Medio/Bajo + justificación]
```

### Ficha Bibliográfica
```markdown
## Ficha: [Título]

| Campo | Valor |
|-------|-------|
| **Autores** | |
| **Año** | |
| **Venue** | |
| **Tier** | |
| **URL** | |

### Resumen
[2-3 párrafos]

### Metodología
[Cómo llegaron a sus conclusiones]

### Hallazgos Clave
1. 
2. 

### Limitaciones
[Declaradas + identificadas]

### Relevancia para RaiSE
[Mapeo específico]

### Citas Útiles
> "[Cita]" (p. X)
```

---

## Criterios de Validación del Backlog

### Go (Claim Validado)
- ✓ ≥2 fuentes Tier 1 o ≥3 fuentes Tier 2 que soporten el claim
- ✓ Metodología de las fuentes es reproducible
- ✓ No hay contradicción significativa en la literatura

### Pivot (Claim Requiere Ajuste)
- Evidencia parcial pero no concluyente
- Claim necesita refinamiento basado en literatura
- Acción: Documentar ajuste propuesto en ADR

### No-Go (Claim No Soportado)
- No existe evidencia que soporte el claim
- Evidencia contradice el claim
- Acción: Proponer eliminación o reformulación del claim

---

## Métricas de Progreso

| Métrica | Target Semana 4 | Target Semana 8 |
|---------|-----------------|-----------------|
| Research Items completados | 10/23 (43%) | 18/23 (78%) |
| Claims validados (Go) | ≥6 | ≥15 |
| Claims que requieren pivot | Documentados | Resueltos |
| Literature Reviews entregados | 4 | 8 |
| Fichas bibliográficas | 15 | 30 |

---

## Changelog

### v1.0.0 (2026-01-07)
- Backlog inicial con 23 research items
- 6 épicas de investigación
- 4 sprints planificados
- Formatos de entregables definidos

---

*"La medida del éxito de este backlog no es cuántos papers leemos, sino cuántos claims de RaiSE podemos defender con evidencia verificable."*
