# RaiSE Ontology Backlog
## Registro de Mejoras Ontológicas desde Conversaciones

**Versión:** 1.1.0  
**Fecha:** 06 de Enero, 2026  
**Última actualización:** 06 de Enero, 2026  
**Propósito:** Capturar refinamientos ontológicos emergentes de conversaciones donde se explica RaiSE.

> **Filosofía:** Cada conversación donde Emilio explica RaiSE es un experimento heutagógico. Las fricciones, metáforas efectivas, y conceptos articulados son señales para refinar el framework.

---

## Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| Total items | 26 |
| P0 (Críticos) | 1 |
| P1 (Importantes) | 11 |
| P2 (Mejoras) | 10 |
| P3 (Nice-to-have) | 4 |
| Transcripts procesados | 3 |

---

## Backlog Activo

### 🔴 P0 - Críticos (Contradicciones/Confusiones)

| ID | Tipo | Concepto | Descripción | Fuente | Documento Afectado | Estado |
|----|------|----------|-------------|--------|-------------------|--------|
| ONT-004 | `COR` | "prácticas" vs "técnica" | Emilio dice "Katas de prácticas" donde corpus dice "Katas de técnica". Verificar si es sinónimo intencional o inconsistencia. | Héctor 2026-01 | 20-glossary-v2.md | 🔲 Verificar |

### 🟡 P1 - Importantes (Refinamientos de alto impacto)

| ID | Tipo | Concepto | Descripción | Fuente | Documento Afectado | Estado |
|----|------|----------|-------------|--------|-------------------|--------|
| ONT-001 | `REF` | "Dueño del contexto" + "Arnés determinista" | Frase definitoria del Orquestador: "Ahora no eres dueño del producto, ahora eres dueño del contexto." Metáfora del arnés determinista sobre motor probabilístico. Reforzado en 3 transcripts. | Héctor + Omar + Fer/Aquiles | 20-glossary-v2.md (Orquestador, Context Engineering) | 🔲 Pendiente |
| ONT-006 | `ADD` | "Presupuesto de inferencia" | Concepto clave para explicar por qué se necesita proceso determinista: cada request tiene límite de tokens/tiempo que el proveedor controla. | Omar 2026-01 | 20-glossary-v2.md | 🔲 Pendiente |
| ONT-007 | `REF` | "Human-Centered Framework" | RaiSE explícitamente "centrado en el humano, no en productividad, no en costo". "Tu chamba es mejorar el sistema que produce software." | Omar 2026-01 | 00-constitution-v2.md, 05-learning-philosophy-v2.md | 🔲 Pendiente |
| ONT-011 | `ADD` | "Jumpstart" | Proceso propietario de adopción tecnológica (registrado IMPI 2005). Seminario + análisis FCE + validación técnica. 4-6 semanas. Modelo de servicios profesionales. | Omar 2026-01 | 02-business-model-v2.md | 🔲 Pendiente |
| ONT-013 | `ARQ` | Grafo + AST para SAR | Proceso determinista: Parser → AST → Grafo → Recorrido exhaustivo → Interpretación LLM. No probabilístico. | Omar 2026-01 | 10-system-architecture-v2.md (futuro SAR) | 🔲 Documentar |
| ONT-017 | `REF` | Diferenciación "Lean, no generación" | "RaiSE no es un framework de generación de código con IA, de esos hay cientos. RaiSE es un framework de Lean Software Development con IA, ahí somos únicos." Frase definitoria para pitch. | Fer/Aquiles 2026-01 | 01-product-vision-v2.md, Landing | 🔲 Pendiente |
| ONT-018 | `ADD` | "Ontología bajo demanda" | Concepto arquitectónico: MCP devuelve grafo estructurado con principios/patrones/prácticas/herramientas bajo demanda. "En el momento en que el agente local necesita algo, le pregunta al MCP." | Fer/Aquiles 2026-01 | 10-system-architecture-v2.md, 20-glossary-v2.md | 🔲 Pendiente |
| ONT-020 | `ARQ` | RAG estructurado vs probabilístico | Principio arquitectónico central: "El RAG que se conoce es probabilístico... para desarrollo confiable, eso no nos sirve... contexto determinista estructurado = mejores resultados." | Fer/Aquiles 2026-01 | 10-system-architecture-v2.md | 🔲 Pendiente |
| ONT-022 | `ARQ` | Transpiración MD→LinkML | Flujo completo: Markdown (humano) → transpiración → LinkML/formatos formales (máquina). "El humano habla Markdown... transpiramos las reglas... las generamos en formatos LinkML." | Fer/Aquiles 2026-01 | 10-system-architecture-v2.md, 15-tech-stack-v2.md | 🔲 Pendiente |
| ONT-023 | `ADD` | Evals (Framework de evaluación) | "Los evals son las pruebas de lo que el desarrollador de RaiSE tiene que mejorar. Las pruebas unitarias quien las tiene que cumplir es el agente, pero nosotros tenemos que darle el contexto." | Fer/Aquiles 2026-01 | 20-glossary-v2.md, 15-tech-stack-v2.md | 🔲 Pendiente |
| ONT-027 | `SCP` | Modo con/sin MCP | Clarificar scope MVP: raise-kit sin MCP = comandos + katas (contexto probabilístico). Con MCP = RAG estructurado + ontología bajo demanda (contexto determinista). | Fer/Aquiles 2026-01 | 10-system-architecture-v2.md, 30-roadmap-v2.md | 🔲 Pendiente |

### 🟢 P2 - Mejoras (Completan la ontología)

| ID | Tipo | Concepto | Descripción | Fuente | Documento Afectado | Estado |
|----|------|----------|-------------|--------|-------------------|--------|
| ONT-002 | `ARQ` | Transpiración MD→JSON/Cedar | Flujo de reglas: Markdown (human-readable) → Transpiración → JSON/Cedar (machine-executable). Cedar para políticas formales. | Héctor 2026-01 | 10-system-architecture-v2.md | 🔲 Pendiente |
| ONT-003 | `ADD` | LinkML | Framework de modelado ontológico para generar schemas validables. Añadir al tech stack. | Héctor 2026-01 | 15-tech-stack-v2.md | 🔲 Pendiente |
| ONT-012 | `SCP` | Software Architecture Reconstruction | Clarificar que SAR existe como práctica pero está fuera del MVP. Documentar roadmap. | Omar 2026-01 | 30-roadmap-v2.md | 🔲 Pendiente |
| ONT-015 | `REF` | Target market refinado | "Dueños de empresas de software en Latinoamérica", "founders técnicos", "no developers individuales, no enterprises grandes". | Héctor + Omar | 04-stakeholder-map-v2.md | 🔲 Pendiente |
| ONT-016 | `ADD` | "Dogfooding" como línea de negocio | Tercera línea: desarrollo interno usando RaiSE como validación del framework. | Héctor 2026-01 | 02-business-model-v2.md | 🔲 Pendiente |
| ONT-019 | `ADD` | "Agente local" | Término para agente del IDE (Cursor, AntiGravity, Claude Code, Gemini, etc.). Diferenciación de agente RaiSE o agente MCP. "Agente local le vamos a llamar al agente del IDE." | Fer/Aquiles 2026-01 | 20-glossary-v2.md | 🔲 Pendiente |
| ONT-021 | `ADD` | LinkML (alta densidad semántica) | "Formatos de alta densidad semántica. Como viene el campo origen del campo destino y aparte viene la relación, tiene gran información semántica." Expandir entrada existente (ONT-003). | Fer/Aquiles 2026-01 | 15-tech-stack-v2.md, 20-glossary-v2.md | 🔲 Pendiente |
| ONT-024 | `REF` | Built-in Quality (Calidad incluida) | Referencia explícita a TPS: "La máquina que te construye también te ayuda a hacer la prueba unitaria del trabajo terminado. Es un principio de automatización Lean." | Fer/Aquiles 2026-01 | 05-learning-philosophy-v2.md | 🔲 Pendiente |
| ONT-025 | `ADD` | Rigor epistemológico | Principio de diseño: "Cada paso documentable, verificable, repetible, que está basado en un tren de pensamiento que es explicable." Diferenciador de mercado. | Fer/Aquiles 2026-01 | 00-constitution-v2.md, 20-glossary-v2.md | 🔲 Pendiente |
| ONT-026 | `ARQ` | Framework de evaluación organizacional | Capacidad: configurar tanto generación como evaluación por organización. "Configuras cómo se va a generar, pero al mismo tiempo estás configurando cómo se va a evaluar." | Fer/Aquiles 2026-01 | 10-system-architecture-v2.md (futuro) | 🔲 Pendiente |

### ⚪ P3 - Nice-to-have (Metáforas y comunicación)

| ID | Tipo | Concepto | Descripción | Fuente | Documento Afectado | Estado |
|----|------|----------|-------------|--------|-------------------|--------|
| ONT-005 | `COM` | "Pastorear IAs" | Metáfora efectiva para rol del Orquestador. "Tu chamba: pastorear inteligencias artificiales." | Omar 2026-01 | Landing page, pitch deck | 🔲 Pendiente |
| ONT-008 | `COM` | "Framework que eleva, no reemplaza" | "De programador picapiedra a alguien que agrega valor." | Omar 2026-01 | Landing page | 🔲 Pendiente |
| ONT-009 | `COM` | "El coche te enseña a manejar" | Metáfora heutagógica efectiva. | Omar 2026-01 | Docs onboarding | 🔲 Pendiente |
| ONT-010 | `COM` | "Coches para Verstappens" | "No eliminamos al conductor, mejoramos al conductor a través de ganar carreras." | Omar 2026-01 | Landing page, pitch | 🔲 Pendiente |
| ONT-014 | `COM` | "Videojuego del mapa que se abre" | Para explicar SAR iterativo. Emilio lo usó de nuevo en este transcript. | Omar + Fer/Aquiles 2026-01 | Docs SAR | 🔲 Pendiente |
| ONT-028 | `COM` | "Máquina que hace ménsulas/rings de Toyota" | Metáfora TPS: el mismo proceso produce y valida. "Arriba haces el ring y luego abajo la pasas y te mide si el rin está bien." | Fer/Aquiles 2026-01 | Pitch técnico, landing | 🔲 Pendiente |

---

## Historial de Transcripts Procesados

| Fecha | Interlocutor | Rol/Contexto | Items Generados | Análisis |
|-------|--------------|--------------|-----------------|----------|
| 2026-01-05 | Héctor Cuesta | Dev senior, enterprise, escéptico de AI hype | 4 | Ver sección abajo |
| 2026-01-06 | Omar Zamora | Ex-gobierno, busca oportunidad, no-técnico activo | 10 | Ver sección abajo |
| 2026-01-06 | Fernando Rodriguez + Aquiles Lázaro | Dev lead + PM interno, sincronización MVP | 12 | Ver sección abajo |

---

## Análisis por Transcript

### Transcript: Héctor Cuesta (2026-01-05)

**Contexto:** Conversación entre pares técnicos. Héctor viene de enterprise grande con problemas de adopción de AI. Escéptico pero interesado.

**Temas dominantes:**
- Validación de que el problema (inconsistencia AI) es real y extendido
- Discusión técnica sobre determinismo vs probabilismo
- Estructura de equipos (generalistas vs especialistas)
- Rol de Scrum/metodologías con AI

**Insights clave:**
1. "La variabilidad es enemiga de la eficiencia" — Ken Beck citado, validación Lean
2. Concepto de "Catas inversas" de Héctor — compatible con Katas de Patrón
3. Resistencia organizacional es real: "después del paper de Lima, todo mundo bajó los brazos"
4. Target clarificado: "solo dueños, solo founders técnicos"

**Fricciones:** Ninguna significativa — Héctor entiende el modelo mental.

---

### Transcript: Omar Zamora (2026-01-06)

**Contexto:** Pitch fundacional a alguien que no es developer activo pero tiene background técnico. Omar busca oportunidad laboral y puede ser canal de ventas.

**Temas dominantes:**
- Historia de origen de RaiSE (crisis financiera → necesidad → invención)
- Modelo de negocio completo (servicios administrados + producto)
- Propuesta de valor para dueños de empresas
- Proceso Jumpstart como mecanismo de adopción

**Insights clave:**
1. "Pastorear IAs" — metáfora que resonó inmediatamente
2. "Ningún programador me agarra por los huevos" — motivación personal de independencia
3. "Human-centered, no productivity-centered" — posicionamiento filosófico explícito
4. Modelo híbrido: Open source (1 repo) + Licenciado (multi-repo governance)
5. "Presupuesto de inferencia" — concepto técnico clave para justificar determinismo

**Fricciones:**
- Confusión inicial sobre si RaiSE es un modelo de AI
- Pregunta sobre dónde corre el cómputo (inferencia vs framework)

**Metáforas que funcionaron:**
- "Coches para Verstappens" (diferenciador)
- "El coche te enseña a manejar" (heutagogía)
- "Arte marcial / Taekwondo" (no hay atajos)
- "Videojuego del mapa" (SAR iterativo)

---

### Transcript: Fernando Rodriguez + Aquiles Lázaro (2026-01-06)

**Contexto:** Reunión interna de sincronización técnica. Fernando es developer lead trabajando en el fork de spec-kit. Aquiles es project manager en proceso de onboarding a RaiSE.

**Temas dominantes:**
- Diferenciación "Lean, no generación de código"
- Arquitectura MCP + RAG estructurado
- Concepto de "ontología bajo demanda"
- Framework de evaluaciones (evals) como componente del MVP
- Transpiración Markdown → LinkML
- Decisión: ¿incluir evals desde cero?

**Insights clave:**
1. **Frase definitoria nueva:** "RaiSE no es un framework de generación de código, es un framework de Lean Software Development con IA"
2. **Ontología bajo demanda:** El MCP devuelve grafos con principios/patrones/prácticas/herramientas cuando el agente lo necesita
3. **RAG estructurado vs probabilístico:** Diferenciador arquitectónico central
4. **Evals como pruebas del desarrollador RaiSE:** Las unit tests son del agente; los evals son del contexto que diseña el Orquestador
5. **Rigor epistemológico:** Diferenciador de mercado — cada paso documentable, verificable, repetible
6. **Built-in Quality (TPS):** Metáfora del ring de Toyota — la máquina que produce también valida
7. **95% sin alucinaciones:** Target métrico para competitividad

**Fricciones detectadas:**
- Aquiles no entendió diferencia con/sin MCP (necesita documentación simplificada)
- Falta guía unificada Greenfield vs Brownfield
- Concepto MCP abstracto sin ejemplo visual

**Metáforas que funcionaron:**
- "Videojuego del mapa que se abre" (investigación progresiva)
- "Máquina que hace ménsulas y las mide" (built-in quality)
- "Ring de Toyota" (Jidoka aplicado)
- "Escudería vs motores" (separación producto/servicios)

**Decisiones detectadas (para ADR):**
| Decisión | Estado | ADR Sugerido |
|----------|--------|--------------|
| Evals integrados desde MVP | Pendiente consenso | ADR-011: Eval-First Design |
| raise-kit + MCP mismo release | Propuesto | Actualizar ADR-003 |
| AntiGravity como IDE principal | Declarado | Documentar en 15-tech-stack |

---

## Patrones Emergentes (Cross-Transcript)

### Conceptos que se repiten y refuerzan

| Concepto | Héctor | Omar | Fer/Aquiles | Implicación |
|----------|--------|------|-------------|-------------|
| Determinismo vs Probabilismo | ✅ Técnico | ✅ Metafórico | ✅ Arquitectónico | Core differentiator — consolidar documentación |
| Dueño del contexto | ✅ | ✅ | ✅ | Frase canónica para Orquestador — 3/3 transcripts |
| Target: dueños/founders | ✅ | ✅ | — | Confirmar en stakeholder map |
| Lean/TPS como fundamento | ✅ Explícito | ✅ Implícito | ✅ Explícito (Built-in Quality) | Mantener prominencia |
| Heutagogía | ✅ Término | ✅ Metáforas | ✅ Implícito | Documentado, reforzar en pitch |
| MCP como core | — | — | ✅ | Nuevo: central para MVP |
| Evals/Evaluaciones | — | — | ✅ | Nuevo: concepto crítico para diferenciación |

### Fricciones recurrentes (a resolver)

| Fricción | Frecuencia | Solución propuesta |
|----------|------------|-------------------|
| "¿RaiSE es un modelo de AI?" | 1/3 | Añadir clarificación en intro |
| "¿Dónde corre?" | 1/3 | Enfatizar "agnóstico a inferencia" |
| "¿Qué hace el MCP?" | 1/3 (nueva) | Crear documentación simplificada MCP para onboarding |
| Greenfield vs Brownfield | 1/3 (nueva) | Fer tiene guía mental; documentar |

---

## Próximas Acciones

1. **Inmediato (P0):** Verificar "prácticas" vs "técnica" con Emilio
2. **Esta semana (P1):** 
   - Incorporar "Dueño del contexto" al Glossary
   - Documentar "Ontología bajo demanda" en arquitectura
   - Definir si evals entran en MVP
3. **Este mes (P2):** 
   - Documentar Jumpstart en Business Model
   - Añadir LinkML al tech stack
   - Crear guía Brownfield
4. **Backlog:** Metáforas para materiales de comunicación externa

---

## Changelog

| Fecha | Cambio | Items |
|-------|--------|-------|
| 2026-01-06 | Añadido transcript Fernando+Aquiles | +12 items (ONT-017 a ONT-028) |
| 2026-01-06 | Creación inicial con 2 transcripts | 14 items |

---

## Observaciones Meta (Cross-Transcript)

### Secuencia de Pitch Efectiva

Basado en los 3 transcripts, Emilio sigue una secuencia consistente cuando explica RaiSE:

1. **Problema** → "El cuello de botella no es generar código, es entenderlo"
2. **Solución técnica** → "Proceso determinista, no probabilístico"
3. **Diferenciador** → "Human-centered, no productivity-centered" / "Lean, no generación"
4. **Metáfora** → "Coches para Verstappens" / "El coche te enseña a manejar"
5. **Prueba** → Casos reales (Prosa, Jafra, equipos internos)
6. **Call to action** → "Súbete al coche y aprende"

### Metáforas Consistentes

| Metáfora | Uso | Efectividad | Transcripts |
|----------|-----|-------------|-------------|
| "Coches para Verstappens" | Diferenciador | ⭐⭐⭐ Alta | Omar |
| "El coche te enseña a manejar" | Heutagogía | ⭐⭐⭐ Alta | Omar |
| "Pastorear IAs" | Rol del Orquestador | ⭐⭐⭐ Alta | Omar |
| "Videojuego del mapa" | SAR/investigación iterativa | ⭐⭐ Media | Omar, Fer/Aquiles |
| "Máquina que hace ménsulas/rings" | Built-in Quality | ⭐⭐⭐ Alta | Fer/Aquiles |
| "Arte marcial / Taekwondo" | No hay atajos | ⭐⭐ Media | Omar |

### Insights sobre Audiencia

| Audiencia | Qué funciona | Qué ajustar |
|-----------|--------------|-------------|
| Dev técnico (Héctor) | Hablar de determinismo, Lean, variabilidad | Menos metáforas de carros |
| No-dev con background técnico (Omar) | Metáforas, historia de origen, independencia | Más demos, menos teoría |
| Equipo interno (Fer/Aquiles) | Arquitectura, decisiones técnicas, MCP | Onboarding MCP simplificado |

---

## Decisiones Pendientes para Emilio

### P0: "prácticas" vs "técnica"

**Contexto:** En el transcript de Héctor, Emilio menciona "Katas de prácticas" donde el corpus documenta "Katas de Técnica".

**Pregunta:** ¿Es "prácticas" un sinónimo intencional de "técnica" o una inconsistencia a corregir?

**Opciones:**
- A) Son sinónimos → Documentar ambos como válidos
- B) "Técnica" es canónico → Corregir uso verbal
- C) "Prácticas" es mejor → Migrar corpus a "prácticas"

**Impacto:** Afecta Glossary y documentación de Katas.

### P1: ¿Evals en MVP?

**Contexto:** Este transcript plantea incluir framework de evaluaciones desde el diseño inicial del MVP.

**Pregunta:** ¿Se incluyen evals en el primer release o es v0.3+?

**Opciones:**
- A) Incluir desde cero → Diseño técnico los considera
- B) Post-MVP → Roadmap para v0.3
- C) Híbrido → Infraestructura básica ahora, features después

**Impacto:** Afecta diseño técnico, timeline, y diferenciación de mercado.

### P1: ¿raise-kit + MCP mismo release?

**Contexto:** Emilio propone que raise-kit y raise-mcp sean el mismo proyecto/release.

**Pregunta:** ¿Confirmar unificación o mantener separados?

**Impacto:** Afecta ADR-003, arquitectura de componentes, y experiencia de instalación.

---

*Este backlog se actualiza con cada transcript procesado. Ver `kata-refinamiento-ontologico.md` para el proceso.*
