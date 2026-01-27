# RaiSE Semantic Coherence Analysis
## Análisis de Coherencia de Dominios Semánticos

**Versión:** 0.1.0  
**Estado:** Draft para Revisión  
**Fecha:** 28 de Diciembre, 2025  
**Autor:** RaiSE Ontology Architect  
**Metodologías:** NeOn, METHONTOLOGY, OntoClean, Lakoff & Johnson, ISO 704  
**Propósito:** Analizar la coherencia terminológica de RaiSE, identificar conflictos semánticos, y proponer convenciones de nombrado antes de la formalización ontológica.

---

## Prefacio: Por Qué Este Análisis

### El Riesgo de la Incoherencia Semántica

Un framework que mezcla terminología de múltiples dominios sin coherencia genera:

1. **Carga cognitiva elevada:** El usuario debe "traducir" entre dominios mentalmente
2. **Ambigüedad interpretativa:** ¿"Constitution" es documento legal o principio filosófico?
3. **Dificultad de extensión:** ¿Nuevos conceptos siguen qué patrón?
4. **Barreras de adopción:** Mercado meta puede percibir complejidad innecesaria

### El Objetivo

Establecer un **lenguaje ubicuo** (Evans, DDD) que sea:
- Internamente consistente
- Trazable a sus orígenes
- Accesible al mercado meta
- Extensible de forma predecible

---

# PARTE I: Semantic Domain Mapping

## 1. Inventario Terminológico

### 1.1 Extracción del Corpus

He extraído **87 términos** del corpus RaiSE. Los clasifico por frecuencia y centralidad:

#### Términos Tier 1 (Core - Aparecen en Constitution/Glossary)

| # | Término | Frecuencia | Documento Origen |
|---|---------|------------|------------------|
| 1 | Constitution | Alta | 00-constitution |
| 2 | Orchestrator | Alta | 20-glossary |
| 3 | Agent | Alta | 20-glossary |
| 4 | Spec / Specification | Alta | 20-glossary |
| 5 | DoD / Definition of Done | Alta | 20-glossary |
| 6 | Kata | Alta | 20-glossary |
| 7 | Rule | Alta | 20-glossary |
| 8 | Golden Data | Media | 20-glossary |
| 9 | Governance as Code | Media | 20-glossary |
| 10 | Heutagogy / Heutagogía | Media | 20-glossary |
| 11 | Jidoka | Media | 05-learning-philosophy |
| 12 | Kaizen | Media | 05-learning-philosophy |
| 13 | Just-in-Time Learning | Media | 20-glossary |
| 14 | SDD (Spec-Driven Development) | Media | 20-glossary |

#### Términos Tier 2 (Operativos - Aparecen en Methodology/Architecture)

| # | Término | Frecuencia | Documento Origen |
|---|---------|------------|------------------|
| 15 | Phase (Fase) | Alta | 21-methodology |
| 16 | Flow (Flujo) | Media | 21-methodology |
| 17 | Value Stream | Baja | 21-methodology |
| 18 | PRD | Media | 21-methodology |
| 19 | User Story | Alta | 22-templates-catalog |
| 20 | Technical Design | Media | 22-templates-catalog |
| 21 | Implementation Plan | Media | 21-methodology |
| 22 | Backlog | Media | 22-templates-catalog |
| 23 | Template | Alta | 22-templates-catalog |
| 24 | MCP (Model Context Protocol) | Baja | 10-system-architecture |

#### Términos Tier 3 (Infraestructura/Técnicos)

| # | Término | Frecuencia | Documento Origen |
|---|---------|------------|------------------|
| 25 | raise-kit | Media | 10-system-architecture |
| 26 | raise-config | Media | 10-system-architecture |
| 27 | raise-mcp | Baja | 10-system-architecture |
| 28 | raise-commons | Baja | Repo name |
| 29 | .raise/ | Media | File structure |
| 30 | hydrate | Baja | 23-commands-reference |
| 31 | scaffold | Baja | 31-current-state |

---

## 2. Clasificación por Dominio Semántico

### 2.1 Identificación de Dominios

He identificado **8 dominios semánticos** en la terminología RaiSE:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DOMINIOS SEMÁNTICOS EN RAISE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   JAPONÉS    │  │  EDUCACIÓN   │  │   POLÍTICO   │  │  SOFTWARE    │    │
│  │    (TPS)     │  │   (Teoría)   │  │  (Gobierno)  │  │ (Ingeniería) │    │
│  │              │  │              │  │              │  │              │    │
│  │ • Jidoka     │  │ • Heutagogía │  │ • Constitut° │  │ • Spec       │    │
│  │ • Kaizen     │  │ • Andragogía │  │ • Governance │  │ • Backlog    │    │
│  │ • Kata       │  │ • Pedagogy   │  │ • Rule       │  │ • Deploy     │    │
│  │ • Hansei     │  │              │  │ • Compliance │  │ • CLI        │    │
│  │ • Muda/Mura  │  │              │  │              │  │ • API        │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   MUSICAL    │  │  BIOLÓGICO   │  │ARQUITECTURA  │  │   MILITAR    │    │
│  │ (Orquesta)   │  │  (Orgánico)  │  │(Construcción)│  │  (Defensa)   │    │
│  │              │  │              │  │              │  │              │    │
│  │ • Orchestrat°│  │ • Golden     │  │ • Framework  │  │ • Strategy   │    │
│  │              │  │ • Corpus     │  │ • Scaffold   │  │ • Defense    │    │
│  │              │  │ • Flow       │  │ • Foundation │  │              │    │
│  │              │  │ • Fractal    │  │ • Layer      │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Matriz de Clasificación Completa

| Término | Dominio Primario | Dominio Secundario | Conflicto Potencial |
|---------|------------------|-------------------|---------------------|
| Constitution | Político | Legal | ⚠️ Puede parecer rígido/burocrático |
| Orchestrator | Musical | — | ✅ Metáfora clara |
| Agent | Software | Espionaje | ⚠️ Connotación de autonomía excesiva |
| Spec | Software | — | ✅ Estándar de industria |
| DoD | Software/Agile | Militar (Dept of Defense) | ⚠️ Acronym collision |
| Kata | Japonés/Marcial | — | ✅ Bien establecido en software |
| Rule | Político/Legal | Juegos | ✅ Neutral |
| Golden Data | Biológico/Mítico | — | ⚠️ "Golden" puede parecer aspiracional |
| Governance | Político | Corporativo | ✅ Apropiado para enterprise |
| Heutagogía | Educación/Griego | — | ⚠️ Desconocido para muchos |
| Jidoka | Japonés | — | ⚠️ Requiere explicación |
| Kaizen | Japonés | — | ✅ Conocido en industria |
| JIT Learning | Japonés/Manufactura | — | ✅ Mapping claro |
| Phase | General | — | ✅ Neutral |
| Flow | Biológico/Físico | Psicología (Csikszentmihalyi) | ⚠️ Polisémico |
| Value Stream | Manufactura | — | ✅ Lean estándar |
| User Story | Software/Agile | — | ✅ Estándar de industria |
| Template | Software | — | ✅ Universal |
| MCP | Técnico/Acrónimo | — | ⚠️ Opaco sin contexto |
| hydrate | Biológico/Químico | — | ⚠️ Metáfora no obvia |
| scaffold | Arquitectura | — | ✅ Conocido en dev |
| Corpus | Biológico/Lingüístico | — | ⚠️ Académico |
| Fractal | Matemático | — | ⚠️ Puede parecer complejo |

### 2.3 Distribución por Dominio

| Dominio | Cantidad | % | Términos Representativos |
|---------|----------|---|-------------------------|
| **Software/Ingeniería** | 28 | 32% | Spec, Backlog, Deploy, CLI |
| **Japonés/TPS** | 12 | 14% | Jidoka, Kaizen, Kata, Hansei |
| **Político/Governance** | 10 | 11% | Constitution, Rule, Governance |
| **Biológico/Orgánico** | 9 | 10% | Flow, Golden, Corpus, hydrate |
| **Arquitectura** | 8 | 9% | Framework, Scaffold, Layer |
| **Educación** | 5 | 6% | Heutagogía, Learning |
| **Musical** | 2 | 2% | Orchestrator |
| **Otros/General** | 13 | 15% | Phase, Template, etc. |

---

## 3. Análisis de Coherencia por Dominio

### 3.1 Dominio Japonés/TPS: ✅ COHERENTE

**Términos:** Jidoka, Kaizen, Kata, Hansei, Muda, Mura, Muri, Heijunka, Andon, Genchi Genbutsu

**Análisis:**
- Todos provienen del mismo corpus (Toyota Production System)
- Mantienen significado original
- Forman sistema coherente internamente
- Bien documentados en Upper Ontology

**Veredicto:** Mantener sin cambios. Dominio bien establecido.

---

### 3.2 Dominio Político/Governance: ⚠️ MIXTO

**Términos:** Constitution, Governance, Rule, Compliance, Policy

**Análisis:**
- "Constitution" tiene connotación de rigidez legal
- "Governance" es apropiado para enterprise
- "Rule" es neutral pero podría confundirse con reglas de negocio

**Tensión Identificada:**
```
POLÍTICO (rígido, legal)     vs.    LEAN (flexible, mejora continua)
Constitution = inmutable?           Kaizen = mejora constante?
```

**Recomendación:** 
- Mantener "Constitution" pero enfatizar que es *foundational*, no *restrictive*
- Considerar "Principles" como alternativa menos cargada

---

### 3.3 Dominio Musical (Orchestrator): ✅ COHERENTE pero AISLADO

**Términos:** Orchestrator

**Análisis:**
- Metáfora poderosa y clara
- Implica: dirección, armonía, múltiples instrumentos
- **Problema:** Es el único término musical

**Tensión Identificada:**
```
Si el humano es "Orchestrator"...
¿Los Agents son "instrumentos"? ¿"músicos"?
¿El código es la "música"?
¿La spec es la "partitura"?
```

**Recomendación:**
- Opción A: Extender metáfora musical (Spec = Score, Agent = Instrument)
- Opción B: Renombrar a término más neutral (Director, Conductor, Lead)
- **Mi preferencia:** Opción B - mantener "Orchestrator" pero no extender la metáfora

---

### 3.4 Dominio Biológico/Orgánico: ⚠️ FRAGMENTADO

**Términos:** Golden Data, Corpus, Flow, hydrate, Fractal

**Análisis:**
- "Golden Data" - metáfora de pureza/valor
- "Corpus" - término académico (lingüística, medicina)
- "Flow" - polisémico (física, psicología, manufactura)
- "hydrate" - química/biología (hidratar)
- "Fractal" - matemático/biológico

**Tensión Identificada:**
```
¿RaiSE es un organismo vivo? ¿Un sistema físico? ¿Una estructura matemática?
```

**Problemas Específicos:**

| Término | Problema | Alternativa |
|---------|----------|-------------|
| "hydrate" | Metáfora oscura (¿qué se hidrata?) | `sync`, `pull`, `refresh` |
| "Corpus" | Académico, poco accesible | `Knowledge Base`, `Documentation Set` |
| "Golden Data" | "Golden" puede parecer aspiracional | `Verified Data`, `Canonical Data` |

---

### 3.5 Dominio Educación: ⚠️ BARRERA DE ENTRADA

**Términos:** Heutagogía, Andragogía, Pedagogía, Learning

**Análisis:**
- "Heutagogía" es término técnico de teoría educativa
- Mercado meta (ingenieros) probablemente no lo conoce
- Requiere explicación cada vez

**Tensión Identificada:**
```
PRECISIÓN ACADÉMICA          vs.    ACCESIBILIDAD
"Heutagogía" es exacto               "Self-directed learning" es claro
```

**Recomendación:**
- Usar "Heutagogy" en documentación técnica/filosófica
- Usar "Self-Directed Learning" o "Growth-Oriented" en comunicación externa
- Crear glosario de "traducción" para diferentes audiencias

---

# PARTE II: Terminological Consistency Analysis

## 4. Análisis de Homonimia

### 4.1 Homónimos Identificados

| Término | Significado en RaiSE | Otro Significado Común | Riesgo |
|---------|---------------------|----------------------|--------|
| **DoD** | Definition of Done | Department of Defense | ⚠️ Medio |
| **Agent** | AI Executor | Secret Agent / Software Agent | ⚠️ Medio |
| **Flow** | Flujo de valor | Estado psicológico (Csikszentmihalyi) | ⚠️ Bajo |
| **Rule** | Directiva de governance | Regla de negocio | ⚠️ Bajo |
| **Spec** | Especificación | Spectacles (UK informal) | ✅ Ninguno |

### 4.2 Resolución de Homonimias

**DoD (Definition of Done):**
- Contexto resuelve la ambigüedad
- Considerar usar "Done Criteria" o "Completion Criteria" en contextos ambiguos
- **Decisión:** Mantener, es estándar Agile

**Agent:**
- Connotación de autonomía puede ser problemática
- En RaiSE, Agent es *ejecutor bajo supervisión*, no autónomo
- **Decisión:** Mantener pero enfatizar "supervised" en definiciones

---

## 5. Análisis de Sinonimia

### 5.1 Sinónimos Identificados

| Concepto | Términos Usados | Problema | Resolución |
|----------|-----------------|----------|------------|
| Principios base | Constitution, Principles, Values | ¿Son lo mismo? | Constitution CONTIENE Principles y Values |
| Documento de requisitos | PRD, Spec, Requirements | Confusión de granularidad | PRD = Proyecto, Spec = Feature |
| Validación | DoD, Validation, Check, Verify | ¿Cuándo usar cuál? | DoD = Criterios, Validate = Ejecutar, Check = Comando |
| Mejora | Kaizen, Improvement, Evolution | Solapamiento | Kaizen = Proceso, Improvement = Resultado |
| Aprendizaje | Heutagogy, Learning, Growth | Niveles diferentes | Heutagogy = Filosofía, Learning = Actividad, Growth = Resultado |

### 5.2 Jerarquía de Resolución

```
CONSTITUTION (Documento supremo)
├── Principles (Afirmaciones innegociables)
├── Values (Preferencias de diseño)
└── Restrictions (Límites absolutos)

VALIDATION (Proceso general)
├── DoD (Criterios por fase)
├── Kata (Proceso estructurado)
└── Check (Comando CLI)

SPECIFICATION (Documento de requisitos)
├── PRD (Nivel proyecto)
├── Feature Spec (Nivel feature)
└── User Story (Nivel historia)
```

---

## 6. Análisis de Polisemia

### 6.1 Términos Polisémicos

| Término | Significado 1 | Significado 2 | En RaiSE |
|---------|--------------|--------------|----------|
| **Framework** | Estructura conceptual | Librería de código | Ambos (conceptual + raise-kit) |
| **Template** | Plantilla de documento | Scaffold de código | Ambos |
| **Flow** | Flujo de trabajo | Flujo de valor | Ambos (usar "Value Flow" para Lean) |
| **Context** | Fase 0 del proceso | Información para Agent | Ambos (clarificar con prefijo) |

### 6.2 Resolución de Polisemia

| Término | Uso 1 | Uso 2 | Convención Propuesta |
|---------|-------|-------|---------------------|
| Framework | RaiSE Framework (conceptual) | raise-kit (código) | Usar "RaiSE" para concepto, "raise-kit" para código |
| Template | Document Template | Code Template | Prefijo: "Doc Template", "Code Template" |
| Flow | Workflow | Value Stream | Usar "Value Flow" para Lean, "Workflow" para proceso |
| Context | Phase 0 | Agent Context | "Discovery Context" vs "Agent Context" |

---

# PARTE III: Metaphor Coherence Analysis

## 7. Identificación de Metáforas Conceptuales

Basado en Lakoff & Johnson (1980), las metáforas conceptuales estructuran cómo entendemos un dominio abstracto en términos de otro más concreto.

### 7.1 Metáforas Activas en RaiSE

| Metáfora | Dominio Fuente | Dominio Target | Términos |
|----------|---------------|----------------|----------|
| **DESARROLLO ES MANUFACTURA** | Fábrica Toyota | Software Dev | Jidoka, JIT, Flow, Muda |
| **EQUIPO ES ORQUESTA** | Música clásica | Colaboración | Orchestrator |
| **CONOCIMIENTO ES ORGANISMO** | Biología | Datos/Info | Golden Data, Corpus, hydrate |
| **PROYECTO ES ESTADO** | Gobierno | Organización | Constitution, Governance, Rule |
| **CALIDAD ES FRACTAL** | Matemáticas | DoD | Fractal DoD |
| **PRÁCTICA ES ARTE MARCIAL** | Dojo | Mejora | Kata |

### 7.2 Análisis de Compatibilidad

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPATIBILIDAD DE METÁFORAS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         MANUFACTURA (TPS)                                    │
│                              ◉ CENTRAL                                       │
│                               │                                              │
│              ┌────────────────┼────────────────┐                            │
│              │                │                │                            │
│              ▼                ▼                ▼                            │
│         ┌────────┐      ┌────────┐      ┌────────┐                         │
│         │ORQUESTA│      │ DOJO   │      │GOBIERNO│                         │
│         │   ◐    │      │   ◐    │      │   ◐    │                         │
│         │COMPATIBLE     │COMPATIBLE     │COMPATIBLE                         │
│         │(dirección)    │(práctica)     │(gobernanza)                       │
│         └────────┘      └────────┘      └────────┘                         │
│                                                                              │
│         ┌────────┐      ┌────────┐                                          │
│         │ORGANISMO      │FRACTAL │                                          │
│         │   ○    │      │   ○    │                                          │
│         │TANGENCIAL     │TANGENCIAL                                          │
│         │(flujo)        │(repetición)                                        │
│         └────────┘      └────────┘                                          │
│                                                                              │
│  Leyenda: ◉ Central  ◐ Compatible  ○ Tangencial  ◇ Conflictivo             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Evaluación de Coherencia

**Metáfora Central: DESARROLLO ES MANUFACTURA (TPS)**
- Más términos (12)
- Fundamento filosófico (Upper Ontology)
- Trazabilidad demostrable
- **Veredicto: ANCLA CORRECTA**

**Metáforas Compatibles:**

| Metáfora | Compatibilidad | Razón |
|----------|---------------|-------|
| ORQUESTA | ✅ Alta | Director dirige producción = Orchestrator dirige agentes |
| DOJO | ✅ Alta | Kata es práctica deliberada = mejora continua |
| GOBIERNO | ✅ Media | Governance = calidad sistémica (pero cuidado con rigidez) |

**Metáforas Tangenciales:**

| Metáfora | Problema | Recomendación |
|----------|----------|---------------|
| ORGANISMO | Términos aislados, no sistema | Reducir o sistematizar |
| FRACTAL | Término técnico, puede alienar | Explicar o simplificar |

---

## 8. Recomendación de Metáfora Dominante

### 8.1 Propuesta: Sistema de Producción con Maestría

Combinar las metáforas compatibles en un sistema coherente:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                    RAISE = SISTEMA DE PRODUCCIÓN                             │
│                         CON MAESTRÍA                                         │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                      │    │
│  │   MANUFACTURA LEAN           →  Cómo FLUYE el valor                 │    │
│  │   (TPS, Jidoka, JIT)             (Fases, DoD, Flow)                 │    │
│  │                                                                      │    │
│  │   DOJO / MAESTRÍA            →  Cómo se APRENDE                     │    │
│  │   (Kata, Kaizen)                 (Heutagogía, Mejora)               │    │
│  │                                                                      │    │
│  │   ORQUESTACIÓN               →  Cómo se DIRIGE                      │    │
│  │   (Orchestrator)                 (Humano guía AI)                   │    │
│  │                                                                      │    │
│  │   GOBERNANZA                 →  Cómo se GOBIERNA                    │    │
│  │   (Constitution, Rules)          (Principios, Reglas)               │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  EXCLUIR/MINIMIZAR:                                                         │
│  • Metáforas biológicas aisladas (hydrate → sync)                           │
│  • Términos matemáticos complejos (fractal → explicar o evitar)             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Narrativa Unificadora

> **RaiSE es un sistema de producción de software donde:**
> - El **valor fluye** como en una fábrica Toyota (Lean)
> - La **maestría se desarrolla** como en un dojo (Kata)
> - La **armonía se logra** como en una orquesta (Orchestrator)
> - La **coherencia se gobierna** como en una constitución (Governance)

---

# PARTE IV: Naming Convention Proposal

## 9. Principios de Nombrado

Basado en ISO 704 (Terminology Work) e ISO 1087 (Vocabulary of Terminology):

### 9.1 Principios Adoptados

| Principio | Descripción | Aplicación RaiSE |
|-----------|-------------|------------------|
| **Transparencia** | Término debe sugerir significado | "DoD Fractal" > "Multi-level validation" |
| **Consistencia** | Mismo patrón para conceptos similares | Fases: Discovery, Design, Deploy |
| **Derivabilidad** | Términos relacionados deben ser derivables | Kata → KataLevel → L1-Kata |
| **Estabilidad** | Evitar cambios frecuentes | Anclar a términos Lean establecidos |
| **Apropiabilidad** | Apropiado para el dominio | Términos software para audiencia software |

### 9.2 Anti-Principios (Qué Evitar)

| Anti-Principio | Ejemplo | Problema |
|----------------|---------|----------|
| Oscuridad | "hydrate" | No sugiere significado |
| Colisión | "DoD" | Conflicto con siglas conocidas |
| Academicismo excesivo | "Heutagogía" sin explicación | Barrera de entrada |
| Mezcla de idiomas sin patrón | "Kaizen-driven workflow" | Incoherente |

---

## 10. Convenciones Propuestas

### 10.1 Regla 1: Términos Japoneses

**Convención:** Mantener términos japoneses para conceptos TPS cuando:
- Son conocidos en la industria (Kaizen, Kanban)
- No tienen traducción que capture el significado (Jidoka)
- Anclan a la Upper Ontology Lean

**Patrón:** Usar el término japonés, seguido de traducción en primer uso.

```markdown
CORRECTO:
"Jidoka (自働化, autonomation) es el principio de..."

INCORRECTO:
"Jidoka es..."  (sin explicación)
"Autonomation with human touch es..."  (pierde trazabilidad)
```

**Lista de Términos Japoneses Canónicos:**

| Término | Mantener | Alternativa Aceptable |
|---------|----------|----------------------|
| Jidoka | ✅ | — (no hay equivalente) |
| Kaizen | ✅ | Continuous Improvement (menos preciso) |
| Kata | ✅ | Practice Pattern (menos preciso) |
| Hansei | ✅ | Reflection (menos profundo) |
| Muda | ✅ | Waste |
| Mura | ✅ | Unevenness |
| Muri | ✅ | Overburden |
| Heijunka | ⚠️ | Leveling (aceptable) |
| Andon | ⚠️ | Signal Board (aceptable) |
| Genchi Genbutsu | ⚠️ | Go and See (aceptable) |

---

### 10.2 Regla 2: Términos de Gobernanza

**Convención:** Usar términos políticos/de gobernanza cuando implican autoridad y jerarquía.

**Patrón:** Capitalizar para indicar término técnico RaiSE.

| Término | Capitalización | Significado RaiSE |
|---------|---------------|-------------------|
| Constitution | ✅ | Documento de principios inmutables |
| constitution | — | (no usar en minúsculas en contexto RaiSE) |
| Rule | ✅ | Directiva de governance |
| Governance | ✅ | Sistema de gobernanza |

---

### 10.3 Regla 3: Términos de Fases

**Convención:** Fases nombradas con sustantivos que indican el *output*, no la actividad.

| Fase | Nombre Actual | Patrón | Evaluación |
|------|--------------|--------|------------|
| 0 | Context | Output: comprensión del contexto | ✅ |
| 1 | Discovery | Output: requisitos descubiertos | ✅ |
| 2 | Vision | Output: visión de solución | ✅ |
| 3 | Design | Output: diseño técnico | ✅ |
| 4 | Backlog | Output: backlog priorizado | ✅ |
| 5 | Plan | Output: plan de implementación | ✅ |
| 6 | Code | Output: código | ✅ |
| 7 | Deploy | Output: software desplegado | ✅ |

**Veredicto:** Nomenclatura de fases es coherente. Mantener.

---

### 10.4 Regla 4: Términos de Artefactos

**Convención:** Artefactos nombrados por tipo + calificador.

**Patrón:** `{Tipo}-{Calificador}` o `{Tipo} {Calificador}`

| Artefacto | Patrón Actual | Patrón Propuesto | Cambio |
|-----------|--------------|------------------|--------|
| PRD | Acrónimo | PRD (mantener, estándar) | — |
| Solution Vision | Tipo + Calificador | ✅ Correcto | — |
| Tech Design | Tipo + Calificador | Technical Design | Expandir |
| User Story | Tipo + Calificador | ✅ Correcto | — |
| Implementation Plan | Tipo + Calificador | ✅ Correcto | — |
| DoD | Acrónimo | DoD o Done Criteria | Mantener |

---

### 10.5 Regla 5: Términos de Herramientas

**Convención:** Prefijo `raise-` para todas las herramientas del ecosistema.

**Patrón:** `raise-{función}`

| Herramienta | Nombre Actual | Evaluación |
|-------------|--------------|------------|
| raise-kit | ✅ Correcto | CLI principal |
| raise-config | ✅ Correcto | Repositorio de configuración |
| raise-mcp | ✅ Correcto | MCP Server |
| raise-commons | ✅ Correcto | Recursos compartidos |

---

### 10.6 Regla 6: Comandos CLI

**Convención:** Verbos en infinitivo que indican la acción.

**Patrón:** `raise {verbo}` o `raise {verbo} {objeto}`

| Comando | Actual | Evaluación | Alternativa |
|---------|--------|------------|-------------|
| `raise init` | ✅ | Claro | — |
| `raise hydrate` | ⚠️ | Metáfora oscura | `raise sync` o `raise pull` |
| `raise check` | ✅ | Claro | — |
| `raise validate` | ✅ | Claro | — |
| `raise generate` | ✅ | Claro | — |

**Recomendación:** Cambiar `hydrate` → `sync`

```bash
# Actual
raise hydrate

# Propuesto
raise sync          # Sincronizar reglas
raise sync --force  # Forzar sincronización
```

---

### 10.7 Regla 7: Slash Commands

**Convención:** Prefijo `/raise.` seguido de verbo en infinitivo.

**Patrón:** `/raise.{verbo}` o `/raise.{verbo} {contexto}`

| Comando | Actual | Evaluación |
|---------|--------|------------|
| `/raise.constitution` | ⚠️ | ¿Es verbo o sustantivo? |
| `/raise.specify` | ✅ | Verbo claro |
| `/raise.plan` | ✅ | Verbo claro |
| `/raise.tasks` | ⚠️ | Sustantivo plural, debería ser verbo |
| `/raise.implement` | ✅ | Verbo claro |
| `/raise.validate` | ✅ | Verbo claro |
| `/raise.explain` | ✅ | Verbo claro |

**Recomendación:**

| Actual | Propuesto | Razón |
|--------|-----------|-------|
| `/raise.constitution` | `/raise.establish` o `/raise.found` | Verbo |
| `/raise.tasks` | `/raise.decompose` o `/raise.break` | Verbo |

---

## 11. Términos a Renombrar/Revisar

### 11.1 Cambios Recomendados

| Término Actual | Término Propuesto | Razón | Prioridad |
|----------------|-------------------|-------|-----------|
| `hydrate` | `sync` | Metáfora oscura → clara | P0 |
| `Golden Data` | `Verified Data` o `Canonical Data` | "Golden" es aspiracional | P1 |
| `Corpus` | `Knowledge Base` o `Documentation` | Académico → accesible | P2 |
| `/raise.constitution` | `/raise.establish` | Sustantivo → verbo | P1 |
| `/raise.tasks` | `/raise.decompose` | Sustantivo → verbo | P1 |

### 11.2 Términos a Mantener (Confirmados)

| Término | Razón para Mantener |
|---------|---------------------|
| Constitution | Captura jerarquía y autoridad correctamente |
| Orchestrator | Metáfora poderosa y diferenciadora |
| Kata | Establecido en industria, trazable a Lean |
| Jidoka | No hay traducción adecuada |
| Kaizen | Conocido universalmente |
| DoD | Estándar Agile, contexto resuelve ambigüedad |
| Spec | Estándar de industria |
| Heutagogy | Preciso (pero explicar siempre en primer uso) |

### 11.3 Términos a Explicar Siempre

Estos términos deben incluir explicación en primer uso:

| Término | Explicación Requerida |
|---------|----------------------|
| Jidoka | "自働化, automatización con toque humano" |
| Heutagogy | "aprendizaje auto-dirigido" |
| Fractal DoD | "Definition of Done aplicada en cada nivel de granularidad" |
| MCP | "Model Context Protocol, protocolo de Anthropic para contexto AI" |

---

## 12. Glosario de Niveles

### 12.1 Propuesta de Glosarios por Audiencia

| Audiencia | Nivel de Detalle | Términos Japoneses | Términos Académicos |
|-----------|-----------------|-------------------|---------------------|
| **Ejecutivo** | Alto nivel | Traducir | Evitar |
| **Tech Lead** | Completo | Mantener con traducción | Explicar |
| **Developer** | Práctico | Mantener con traducción | Opcional |
| **Académico/Ontológico** | Exhaustivo | Mantener | Mantener |

### 12.2 Ejemplo de Adaptación

**Término:** Heutagogy + Jidoka

**Para Ejecutivo:**
> "RaiSE asegura que los desarrolladores crezcan profesionalmente mientras usan AI (no solo producen código), y que los problemas de calidad se detecten inmediatamente en cada fase."

**Para Tech Lead:**
> "RaiSE implementa Heutagogía (aprendizaje auto-dirigido) para el crecimiento del Orquestador, y Jidoka (自働化, calidad integrada) mediante DoD fractales en cada fase."

**Para Developer:**
> "El sistema te desafía para asegurar que entiendas lo que el AI generó (Heutagogy), y cada fase tiene criterios de calidad que deben pasar antes de avanzar (Jidoka)."

---

# PARTE V: Resolución de Conflictos

## 13. Decisiones de Resolución

### 13.1 Conflicto: Rigidez vs. Mejora Continua

**Síntoma:** "Constitution" suena inmutable; "Kaizen" implica cambio constante.

**Resolución:**
```
Constitution = Principios (inmutables)
               + Valores (estables)
               + Restricciones (estables)

Kaizen aplica a: Katas, Rules, Templates, Procesos
Kaizen NO aplica a: Constitution.Principles
```

**Documentar en Constitution:**
> "Los Principios son inmutables. Los Katas, Rules y Templates evolucionan mediante Kaizen."

---

### 13.2 Conflicto: Agent Autónomo vs. Supervisado

**Síntoma:** "Agent" connota autonomía; RaiSE requiere supervisión.

**Resolución:**
- Renombrar: No (término establecido)
- Calificar: Sí

**Convención:** Siempre referir como "Agent" en contexto de "Orchestrator supervises Agent"

**Definición ajustada:**
> "Agent: Sistema de IA que ejecuta tareas **bajo la supervisión** de un Orchestrator."

---

### 13.3 Conflicto: Metáforas Biológicas Huérfanas

**Síntoma:** "hydrate", "Corpus", "Golden" no forman sistema coherente.

**Resolución:**

| Término | Decisión | Nuevo Término |
|---------|----------|---------------|
| hydrate | Renombrar | `sync` |
| Corpus | Renombrar | `Knowledge Base` |
| Golden Data | Simplificar | `Canonical Data` |
| Flow | Mantener | (polisemia aceptable) |

---

## 14. Terminología Final Consolidada

### 14.1 Términos Canónicos RaiSE v1.0

| Categoría | Términos Canónicos |
|-----------|-------------------|
| **Filosofía** | Constitution, Principles, Values, Restrictions |
| **Lean/TPS** | Jidoka, Kaizen, Kata, Hansei, Muda, Mura, Muri |
| **Roles** | Orchestrator, Agent |
| **Aprendizaje** | Heutagogy, Just-in-Time Learning, Growth |
| **Gobernanza** | Rule, Governance as Code, Compliance |
| **Flujo** | Phase, Value Flow, DoD, Checkpoint |
| **Artefactos** | Spec, PRD, Technical Design, User Story, Plan |
| **Datos** | Canonical Data, Knowledge Base |
| **Herramientas** | raise-kit, raise-config, raise-mcp |
| **Comandos** | init, sync, check, validate, generate |

### 14.2 Términos Deprecados

| Término Deprecado | Reemplazo | Razón |
|-------------------|-----------|-------|
| hydrate | sync | Claridad |
| Golden Data | Canonical Data | Precisión |
| Corpus | Knowledge Base | Accesibilidad |
| /raise.constitution | /raise.establish | Consistencia verbal |
| /raise.tasks | /raise.decompose | Consistencia verbal |

---

# PARTE VI: Guía de Estilo Terminológico

## 15. Reglas de Escritura

### 15.1 Capitalización

| Tipo | Regla | Ejemplo |
|------|-------|---------|
| Conceptos Core RaiSE | PascalCase | Constitution, Orchestrator, Kata |
| Comandos CLI | lowercase | `raise sync`, `raise check` |
| Slash Commands | lowercase | `/raise.specify`, `/raise.plan` |
| Términos Japoneses | Capitalizar primera letra | Jidoka, Kaizen (no JIDOKA, jidoka) |
| Fases | Capitalizar | Phase 3: Design |
| Acrónimos | Mayúsculas | DoD, PRD, MCP, SDD |

### 15.2 Idioma

| Contexto | Idioma | Razón |
|----------|--------|-------|
| Documentación técnica | Español (con términos en inglés/japonés) | Mercado meta |
| Código y CLI | Inglés | Estándar industria |
| Términos Lean/TPS | Japonés o inglés | Trazabilidad |
| API/MCP | Inglés | Estándar técnico |

### 15.3 Formato de Primera Mención

Cuando se introduce un término por primera vez en un documento:

```markdown
TÉRMINOS JAPONESES:
**Jidoka** (自働化, autonomation) es el principio de...

TÉRMINOS TÉCNICOS:
**Heutagogy** (aprendizaje auto-dirigido) significa que...

ACRÓNIMOS:
**DoD** (Definition of Done) define los criterios que...
```

---

## 16. Checklist de Revisión Terminológica

Para cada nuevo documento o concepto:

- [ ] ¿El término sigue las convenciones de nombrado?
- [ ] ¿Está en el glosario canónico?
- [ ] ¿Se explica en primera mención si es técnico?
- [ ] ¿Es consistente con la metáfora dominante (Manufactura + Maestría)?
- [ ] ¿Tiene trazabilidad a la Upper Ontology Lean?
- [ ] ¿Evita los términos deprecados?

---

# Apéndice A: Tabla de Migración

## Cambios a Implementar en Corpus Existente

| Documento | Cambio Requerido | Prioridad |
|-----------|------------------|-----------|
| 23-commands-reference.md | `hydrate` → `sync` | P0 |
| 20-glossary.md | Agregar "Canonical Data", deprecar "Golden Data" | P1 |
| 20-glossary.md | Agregar términos deprecados con redirect | P1 |
| 10-system-architecture.md | Actualizar nombres de comandos | P1 |
| 22-templates-catalog.md | Revisar uso de "Corpus" | P2 |
| Todos | Verificar capitalización consistente | P2 |

---

# Apéndice B: Diagrama de Dominios Semánticos Final

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DOMINIOS SEMÁNTICOS RAISE v1.0                            │
│                        (Post-Análisis)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────┐                                 │
│                         │   MANUFACTURA   │                                 │
│                         │      (TPS)      │                                 │
│                         │    ◉ CENTRAL    │                                 │
│                         └────────┬────────┘                                 │
│                                  │                                          │
│           ┌──────────────────────┼──────────────────────┐                  │
│           │                      │                      │                  │
│           ▼                      ▼                      ▼                  │
│    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐            │
│    │    DOJO     │       │  ORQUESTA   │       │  GOBIERNO   │            │
│    │  (Maestría) │       │ (Dirección) │       │(Gobernanza) │            │
│    │      ◐      │       │      ◐      │       │      ◐      │            │
│    │  INTEGRADO  │       │  INTEGRADO  │       │  INTEGRADO  │            │
│    └─────────────┘       └─────────────┘       └─────────────┘            │
│                                                                              │
│    ┌─────────────────────────────────────────────────────────────┐         │
│    │                    SOFTWARE/INGENIERÍA                       │         │
│    │                         ◐ BASE                               │         │
│    │    (Términos técnicos estándar de la industria)             │         │
│    └─────────────────────────────────────────────────────────────┘         │
│                                                                              │
│    ┌─────────────────────────────────────────────────────────────┐         │
│    │                    DEPRECADO/EXCLUIDO                        │         │
│    │    • hydrate → sync                                          │         │
│    │    • Golden Data → Canonical Data                            │         │
│    │    • Corpus → Knowledge Base                                 │         │
│    │    • Metáforas biológicas aisladas                          │         │
│    └─────────────────────────────────────────────────────────────┘         │
│                                                                              │
│  Leyenda: ◉ Central  ◐ Integrado  ○ Tangencial  ◇ Excluido                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Historial de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 0.1.0 | 2025-12-28 | Análisis inicial completo |

---

*Este documento establece las convenciones terminológicas canónicas para RaiSE. Toda documentación futura debe adherirse a estas convenciones.*
