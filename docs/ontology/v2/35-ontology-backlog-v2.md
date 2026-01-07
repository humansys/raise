# RaiSE Ontology Backlog
## Registro de Mejoras Ontológicas desde Conversaciones

**Versión:** 1.0.0  
**Fecha:** 06 de Enero, 2026  
**Última actualización:** 06 de Enero, 2026  
**Propósito:** Capturar refinamientos ontológicos emergentes de conversaciones donde se explica RaiSE.

> **Filosofía:** Cada conversación donde Emilio explica RaiSE es un experimento heutagógico. Las fricciones, metáforas efectivas, y conceptos articulados son señales para refinar el framework.

---

## Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| Total items | 14 |
| P0 (Críticos) | 1 |
| P1 (Importantes) | 5 |
| P2 (Mejoras) | 5 |
| P3 (Nice-to-have) | 3 |
| Transcripts procesados | 2 |

---

## Backlog Activo

### 🔴 P0 - Críticos (Contradicciones/Confusiones)

| ID | Tipo | Concepto | Descripción | Fuente | Documento Afectado | Estado |
|----|------|----------|-------------|--------|-------------------|--------|
| ONT-004 | `COR` | "prácticas" vs "técnica" | Emilio dice "Katas de prácticas" donde corpus dice "Katas de técnica". Verificar si es sinónimo intencional o inconsistencia. | Héctor 2026-01 | 20-glossary-v2.md | 🔲 Verificar |

### 🟡 P1 - Importantes (Refinamientos de alto impacto)

| ID | Tipo | Concepto | Descripción | Fuente | Documento Afectado | Estado |
|----|------|----------|-------------|--------|-------------------|--------|
| ONT-001 | `REF` | "Dueño del contexto" + "Arnés determinista" | Frase definitoria del Orquestador: "Ahora no eres dueño del producto, ahora eres dueño del contexto." Metáfora del arnés determinista sobre motor probabilístico. Reforzado en ambos transcripts. | Héctor + Omar | 20-glossary-v2.md (Orquestador, Context Engineering) | 🔲 Pendiente |
| ONT-006 | `ADD` | "Presupuesto de inferencia" | Concepto clave para explicar por qué se necesita proceso determinista: cada request tiene límite de tokens/tiempo que el proveedor controla. | Omar 2026-01 | 20-glossary-v2.md | 🔲 Pendiente |
| ONT-007 | `REF` | "Human-Centered Framework" | RaiSE explícitamente "centrado en el humano, no en productividad, no en costo". "Tu chamba es mejorar el sistema que produce software." | Omar 2026-01 | 00-constitution-v2.md, 05-learning-philosophy-v2.md | 🔲 Pendiente |
| ONT-011 | `ADD` | "Jumpstart" | Proceso propietario de adopción tecnológica (registrado IMPI 2005). Seminario + análisis FCE + validación técnica. 4-6 semanas. Modelo de servicios profesionales. | Omar 2026-01 | 02-business-model-v2.md | 🔲 Pendiente |
| ONT-013 | `ARQ` | Grafo + AST para SAR | Proceso determinista: Parser → AST → Grafo → Recorrido exhaustivo → Interpretación LLM. No probabilístico. | Omar 2026-01 | 10-system-architecture-v2.md (futuro SAR) | 🔲 Documentar |

### 🟢 P2 - Mejoras (Completan la ontología)

| ID | Tipo | Concepto | Descripción | Fuente | Documento Afectado | Estado |
|----|------|----------|-------------|--------|-------------------|--------|
| ONT-002 | `ARQ` | Transpilación MD→JSON/Cedar | Flujo de reglas: Markdown (human-readable) → Transpilación → JSON/Cedar (machine-executable). Cedar para políticas formales. | Héctor 2026-01 | 10-system-architecture-v2.md | 🔲 Pendiente |
| ONT-003 | `ADD` | LinkML | Framework de modelado ontológico para generar schemas validables. Añadir al tech stack. | Héctor 2026-01 | 15-tech-stack-v2.md | 🔲 Pendiente |
| ONT-012 | `SCP` | Software Architecture Reconstruction | Clarificar que SAR existe como práctica pero está fuera del MVP. Documentar roadmap. | Omar 2026-01 | 30-roadmap-v2.md | 🔲 Pendiente |
| ONT-015 | `REF` | Target market refinado | "Dueños de empresas de software en Latinoamérica", "founders técnicos", "no developers individuales, no enterprises grandes". | Héctor + Omar | 04-stakeholder-map-v2.md | 🔲 Pendiente |
| ONT-016 | `ADD` | "Dogfooding" como línea de negocio | Tercera línea: desarrollo interno usando RaiSE como validación del framework. | Héctor 2026-01 | 02-business-model-v2.md | 🔲 Pendiente |

### ⚪ P3 - Nice-to-have (Metáforas y comunicación)

| ID | Tipo | Concepto | Descripción | Fuente | Documento Afectado | Estado |
|----|------|----------|-------------|--------|-------------------|--------|
| ONT-005 | `COM` | "Pastorear IAs" | Metáfora efectiva para rol del Orquestador. "Tu chamba: pastorear inteligencias artificiales." | Omar 2026-01 | Landing page, pitch deck | 🔲 Pendiente |
| ONT-008 | `COM` | "Framework que eleva, no reemplaza" | "De programador picapiedra a alguien que agrega valor." | Omar 2026-01 | Landing page | 🔲 Pendiente |
| ONT-009 | `COM` | "El coche te enseña a manejar" | Metáfora heutagógica efectiva. | Omar 2026-01 | Docs onboarding | 🔲 Pendiente |
| ONT-010 | `COM` | "Coches para Verstappens" | "No eliminamos al conductor, mejoramos al conductor a través de ganar carreras." | Omar 2026-01 | Landing page, pitch | 🔲 Pendiente |
| ONT-014 | `COM` | "Videojuego del mapa que se abre" | Para explicar SAR iterativo. | Omar 2026-01 | Docs SAR | 🔲 Pendiente |

---

## Historial de Transcripts Procesados

| Fecha | Interlocutor | Rol/Contexto | Items Generados | Análisis |
|-------|--------------|--------------|-----------------|----------|
| 2026-01-05 | Héctor Cuesta | Dev senior, enterprise, escéptico de AI hype | 4 | Ver sección abajo |
| 2026-01-06 | Omar Zamora | Ex-gobierno, busca oportunidad, no-técnico activo | 10 | Ver sección abajo |

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

## Patrones Emergentes (Cross-Transcript)

### Conceptos que se repiten y refuerzan

| Concepto | Héctor | Omar | Implicación |
|----------|--------|------|-------------|
| Determinismo vs Probabilismo | ✅ Técnico | ✅ Metafórico | Core differentiator — documentar mejor |
| Dueño del contexto | ✅ | ✅ | Frase canónica para Orquestador |
| Target: dueños/founders | ✅ | ✅ | Confirmar en stakeholder map |
| Lean/TPS como fundamento | ✅ Explícito | ✅ Implícito | Mantener prominencia |
| Heutagogía | ✅ Término | ✅ Metáforas | Documentado, reforzar en pitch |

### Fricciones recurrentes (a resolver)

| Fricción | Frecuencia | Solución propuesta |
|----------|------------|-------------------|
| "¿RaiSE es un modelo de AI?" | 1/2 | Añadir clarificación explícita en intro |
| "¿Dónde corre?" | 1/2 | Enfatizar "agnóstico a inferencia" |

---

## Próximas Acciones

1. **Inmediato (P0):** Verificar "prácticas" vs "técnica" con Emilio
2. **Esta semana (P1):** Incorporar "Dueño del contexto" al Glossary
3. **Este mes (P2):** Documentar Jumpstart en Business Model
4. **Backlog:** Metáforas para materiales de comunicación externa

---

## Changelog

| Fecha | Cambio | Items |
|-------|--------|-------|
| 2026-01-06 | Creación inicial con 2 transcripts | 14 items |

---

## Observaciones Meta (Cross-Transcript)

### Secuencia de Pitch Efectiva

Basado en ambos transcripts, Emilio sigue una secuencia consistente cuando explica RaiSE:

1. **Problema** → "El cuello de botella no es generar código, es entenderlo"
2. **Solución técnica** → "Proceso determinista, no probabilístico"
3. **Diferenciador** → "Human-centered, no productivity-centered"
4. **Metáfora** → "Coches para Verstappens" / "El coche te enseña a manejar"
5. **Prueba** → Casos reales (Prosa, Jafra, equipos internos)
6. **Call to action** → "Súbete al coche y aprende"

### Metáforas Consistentes

| Metáfora | Uso | Efectividad |
|----------|-----|-------------|
| "Coches para Verstappens" | Diferenciador | ⭐⭐⭐ Alta |
| "El coche te enseña a manejar" | Heutagogía | ⭐⭐⭐ Alta |
| "Pastorear IAs" | Rol del Orquestador | ⭐⭐⭐ Alta |
| "Arte marcial / Taekwondo" | No hay atajos | ⭐⭐ Media |
| "Videojuego del mapa" | SAR iterativo | ⭐⭐ Media |

### Fricciones Recurrentes a Resolver

| Fricción | Apariciones | Solución Propuesta |
|----------|-------------|-------------------|
| "¿RaiSE es un modelo de AI?" | 1/2 | Añadir clarificación en intro: "RaiSE no es un modelo de IA, es un framework de Context Engineering" |
| "¿Dónde corre?" | 1/2 | Enfatizar: "Agnóstico a inferencia - funciona con cualquier LLM" |

### Insights sobre Audiencia

| Audiencia | Qué funciona | Qué ajustar |
|-----------|--------------|-------------|
| Dev técnico (Héctor) | Hablar de determinismo, Lean, variabilidad | Menos metáforas de carros |
| No-dev con background técnico (Omar) | Metáforas, historia de origen, independencia | Más demos, menos teoría |

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

---

*Este backlog se actualiza con cada transcript procesado. Ver `kata-refinamiento-ontologico.md` para el proceso.*
