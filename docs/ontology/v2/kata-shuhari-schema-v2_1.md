# RaiSE Kata Schema v2.1
## Práctica Deliberada con Jidoka Integrado

**Versión:** 2.1.0  
**Fecha:** 28 de Diciembre, 2025  
**Estado:** Ratificado  
**Dependencias:** 00-constitution-v2.md, 05-learning-philosophy-v2.md, 11-data-architecture-v2.md

---

## 1. Resumen Ejecutivo

Este documento define la ontología actualizada de Katas en RaiSE v2.1, introduciendo:

1. **Niveles semánticos**: Reemplazo de L0-L3 por nombres con contenido semántico
2. **Jidoka inline**: Ciclo de corrección embebido en cada paso de la Kata
3. **ShuHaRi como lente**: El modelo de maestría describe al Orquestador, no clasifica Katas

---

## 2. Niveles de Kata: Nombres Semánticos

### 2.1 Jerarquía

```
ABSTRACCIÓN                                              CONCRECIÓN
     ↑                                                        ↓
     
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│ PRINCIPIOS │ →  │   FLUJO    │ →  │   PATRÓN   │ →  │  TÉCNICA   │
│            │    │            │    │            │    │            │
│  ¿Por qué? │    │ ¿Cómo      │    │ ¿Qué       │    │ ¿Cómo      │
│  ¿Cuándo?  │    │  fluye?    │    │  forma?    │    │  hacer?    │
└────────────┘    └────────────┘    └────────────┘    └────────────┘
       │                │                 │                 │
       ▼                ▼                 ▼                 ▼
    Guían           Secuencian       Estructuran        Ejecutan
   decisiones        el valor         el output         la acción
```

### 2.2 Definición de Niveles

| Nivel | Pregunta Guía | Propósito | Desviación Visible |
|-------|---------------|-----------|-------------------|
| **Principios** | ¿Por qué? ¿Cuándo aplica? | Enseñar a aplicar los §1-§8 de la Constitution | "No puedo justificar esta decisión" |
| **Flujo** | ¿Cómo fluye el trabajo? | Definir secuencias de valor estandarizadas | "No tengo el input requerido" |
| **Patrón** | ¿Qué estructura usar? | Establecer formas recurrentes y templates | "El output no cumple la estructura" |
| **Técnica** | ¿Cómo ejecutar esto? | Proveer instrucciones específicas de implementación | "La validación técnica falla" |

### 2.3 Conexión con Lean

| Nivel Kata | Concepto Lean | Ejemplo Toyota |
|------------|---------------|----------------|
| **Principios** | Toyota Way Principles | "Respeto por las personas" |
| **Flujo** | Value Stream | Kanban, flujo de una pieza |
| **Patrón** | Standardized Work | Templates de ensamblaje |
| **Técnica** | Work Instructions | Procedimiento de soldadura |

### 2.4 Migración desde L0-L3

| Antes | Después | Alias (backward compat) |
|-------|---------|------------------------|
| `L0` | `principios` | `L0`, `meta` |
| `L1` | `flujo` | `L1`, `proceso` |
| `L2` | `patron` | `L2`, `componente` |
| `L3` | `tecnica` | `L3`, `tecnico` |

---

## 3. Propósito de la Kata: Sensor Jidoka

### 3.1 La Kata como Detector de Desviación

La Kata NO es documentación pasiva. Es un **sensor que hace visible la desviación** del proceso estándar, habilitando el ciclo Jidoka:

```
┌─────────────────────────────────────────────────────────────────┐
│                    KATA COMO SENSOR JIDOKA                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   FORMA ESTÁNDAR          DESVIACIÓN           CORRECCIÓN      │
│   (Kata define)    →      (Visible)      →     (Resolver)      │
│                                                                 │
│   "Paso 3 requiere       "No tengo ese        "Debo ejecutar   │
│    Tech Design"           documento"           kata de Patrón"  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Analogía: El Telar de Toyoda

El telar de Sakichi Toyoda no tenía "niveles de dificultad". Tenía:

1. **Una forma correcta de operar** → La Kata define los pasos
2. **Un mecanismo que paraba al fallar** → Jidoka inline en cada paso
3. **Visibilidad inmediata del problema** → El Orquestador sabe qué corregir

---

## 4. Jidoka Inline: Estructura de Pasos

### 4.1 Anatomía de un Paso

Cada paso de una Kata tiene tres componentes:

```markdown
### Paso N: [Nombre de la Acción]

[Instrucciones de qué hacer y cómo hacerlo]

**Verificación:** [Cómo saber si el paso se completó correctamente]

> **Si no puedes continuar:**
> [Causa probable y cómo resolver antes de avanzar]
```

### 4.2 Ejemplo Concreto

```markdown
### Paso 3: Cargar Tech Design al Contexto

Proporciona al agente el Tech Design relevante para esta User Story.
El documento debe incluir arquitectura de componentes y contratos de API.

**Verificación:** El agente confirma que tiene acceso al Tech Design
y puede referenciar sus secciones.

> **Si no puedes continuar:**
> No tienes Tech Design → Ejecuta `patron-01-tech-design.md` primero.
> Tech Design incompleto → Revisa Gate-Design antes de continuar.
```

### 4.3 Beneficios del Jidoka Inline

| Aspecto | Sección Separada (antes) | Jidoka Inline (ahora) |
|---------|--------------------------|----------------------|
| Contexto | Lejos del problema | Junto al paso afectado |
| Flujo de lectura | Interrumpido | Natural |
| Acción correctiva | Buscar en otra sección | Inmediata |
| Ciclo Jidoka | Implícito | **Explícito** |

---

## 5. ShuHaRi: Lente del Orquestador

### 5.1 ShuHaRi No Clasifica Katas

ShuHaRi (守破離) describe **cómo el Orquestador se relaciona con las Katas**, no cómo se clasifican las Katas.

| Concepto | Es... | No es... |
|----------|-------|----------|
| **ShuHaRi** | Lente de interpretación | Dimensión de clasificación |
| **Kata** | Una por concepto | Tres variantes por concepto |
| **Archivos** | `flujo-04.md` | `flujo-shu-04.md`, `flujo-ha-04.md` |

### 5.2 Las Tres Fases

| Fase | Kanji | Cómo usa la Kata | Relación con IA |
|------|-------|------------------|-----------------|
| **Shu** | 守 | Sigue cada paso exactamente | IA como mentor que explica |
| **Ha** | 破 | Adapta pasos al contexto | IA como par que debate |
| **Ri** | 離 | Crea variantes o nuevas katas | IA como herramienta que potencia |

### 5.3 Implicación Práctica

El mismo archivo de Kata sirve a los tres modos:

```markdown
## flujo-04-generacion-plan.md

Un Orquestador Shu: Sigue los 5 pasos exactamente como están escritos.
Un Orquestador Ha:  Omite Paso 2 porque ya tiene el input de otra fuente.
Un Orquestador Ri:  Propone un nuevo paso y contribuye a raise-config.
```

### 5.4 Conexión con Principios

El nivel **Principios** de Kata demanda interpretación activa—no puede seguirse "ciegamente" como una receta. Esto alinea naturalmente con la progresión ShuHaRi:

- En **Shu**, el Orquestador aprende *qué* son los principios
- En **Ha**, cuestiona *cuándo* aplicar cada principio
- En **Ri**, propone *extensiones* o nuevos principios

---

## 6. Schema de Kata v2.1

### 6.1 Atributos de Entidad

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| id | string | ✅ | Ej. `flujo-04` |
| level | enum | ✅ | `principios`, `flujo`, `patron`, `tecnica` |
| title | string | ✅ | Nombre descriptivo |
| purpose | string | ✅ | Para qué sirve esta Kata |
| inputs | array | ✅ | Qué consume (hace visible si falta) |
| outputs | array | ✅ | Qué produce |
| steps | array | ✅ | Pasos con Jidoka inline |
| validation_gate | object | ✅ | Sensor final de la Kata |

### 6.2 Schema de Step

```yaml
step:
  number: int               # Número secuencial
  name: string              # Nombre de la acción
  instructions: string      # Qué hacer y cómo
  verification: string      # Cómo saber si funcionó
  if_blocked:               # Jidoka inline
    cause: string           # Causa probable del bloqueo
    resolution: string      # Cómo resolver
    reference: string       # Kata relacionada (opcional)
```

### 6.3 Ejemplo de Frontmatter YAML

```yaml
---
id: "flujo-04"
level: flujo
title: "Generación de Plan de Implementación"
version: "2.1.0"

purpose: >
  Transformar una User Story en un plan paso a paso
  que el agente pueda ejecutar determinísticamente.

inputs:
  - name: "User Story con Acceptance Criteria"
    required: true
    source: "Output de flujo-03"
  - name: "Tech Design relevante"
    required: true
    source: "Output de patron-01"

outputs:
  - name: "Implementation Plan"
    format: "markdown"
    location: ".raise/plans/{us-id}.md"

validation_gate:
  id: "gate-plan"
  criteria:
    - "Cada paso es atómico (una sola acción)"
    - "Cada paso tiene criterio de verificación"
    - "Todos los AC están cubiertos por pasos"
    - "Dependencias entre pasos están explícitas"
---
```

---

## 7. Estructura de Archivos

### 7.1 Nomenclatura

```
{nivel}-{secuencia}-{slug}.md
```

**Ejemplos:**
- `principios-01-rol-orquestador.md`
- `flujo-04-generacion-plan.md`
- `patron-01-tech-design.md`
- `tecnica-03-api-rest.md`

### 7.2 Estructura de Directorios

```
raise-config/
└── katas/
    ├── principios/              # ¿Por qué? ¿Cuándo?
    │   ├── 01-rol-orquestador.md
    │   ├── 02-heutagogia.md
    │   └── 03-jidoka.md
    ├── flujo/                   # ¿Cómo fluye?
    │   ├── 01-discovery.md
    │   ├── 02-planning.md
    │   ├── 03-user-story.md
    │   └── 04-generacion-plan.md
    ├── patron/                  # ¿Qué forma?
    │   ├── 01-tech-design.md
    │   ├── 02-analisis-codigo.md
    │   └── 03-guardrail.md
    └── tecnica/                 # ¿Cómo hacer?
        ├── 01-modelado-datos.md
        ├── 02-api-rest.md
        └── 03-testing.md
```

---

## 8. Template de Kata

```markdown
---
id: "{nivel}-{secuencia}"
level: {nivel}
title: "{Título Descriptivo}"
version: "1.0.0"

purpose: >
  {Descripción de para qué sirve esta Kata}

inputs:
  - name: "{Input 1}"
    required: true
    source: "{De dónde viene}"

outputs:
  - name: "{Output 1}"
    format: "{formato}"
    location: "{ubicación}"

validation_gate:
  id: "gate-{nombre}"
  criteria:
    - "{Criterio 1}"
    - "{Criterio 2}"
---

# {Título}

## Propósito

{purpose expandido si es necesario}

## Antes de Comenzar

Verifica que tienes los inputs requeridos:

- [ ] {Input 1} → Si no: {qué hacer}
- [ ] {Input 2} → Si no: {qué hacer}

> **Jidoka:** Si no puedes marcar estos checkboxes, PARA. Resuelve primero.

## Pasos

### Paso 1: {Nombre}

{Instrucciones detalladas de qué hacer}

**Verificación:** {Cómo saber si funcionó}

> **Si no puedes continuar:**
> {Causa} → {Resolución}

### Paso 2: {Nombre}

{Instrucciones detalladas}

**Verificación:** {Criterio de éxito}

> **Si no puedes continuar:**
> {Causa} → {Resolución}

[... más pasos ...]

## Validation Gate

- [ ] {Criterio 1}
- [ ] {Criterio 2}
- [ ] {Criterio 3}

> **Jidoka:** Si algún criterio falla, revisa el paso correspondiente.

---

*Kata: {id} | Nivel: {level} | Gate: {gate-id}*
```

---

## 9. Ejemplo Completo: flujo-04

```markdown
---
id: "flujo-04"
level: flujo
title: "Generación de Plan de Implementación"
version: "2.1.0"

purpose: >
  Transformar una User Story con Acceptance Criteria en un
  Implementation Plan que el agente pueda ejecutar paso a paso.

inputs:
  - name: "User Story con AC"
    required: true
    source: "Output de flujo-03"
  - name: "Tech Design relevante"
    required: true
    source: "Output de patron-01"
  - name: "Guardrails de código"
    required: false
    source: ".raise/memory/guardrails.json"

outputs:
  - name: "Implementation Plan"
    format: "markdown"
    location: ".raise/plans/{us-id}.md"

validation_gate:
  id: "gate-plan"
  criteria:
    - "Cada paso es atómico"
    - "Cada paso es verificable"
    - "Todos los AC cubiertos"
    - "Dependencias explícitas"
---

# Generación de Plan de Implementación

## Propósito

Producir un plan que el agente pueda ejecutar determinísticamente,
donde cada paso es atómico, verificable, y trazable a un AC.

## Antes de Comenzar

Verifica que tienes los inputs requeridos:

- [ ] User Story con Acceptance Criteria completos
      → Si no: Ejecuta `flujo-03-user-story.md`
- [ ] Tech Design que cubre la arquitectura necesaria
      → Si no: Ejecuta `patron-01-tech-design.md`

> **Jidoka:** Si no puedes marcar estos checkboxes, PARA. Resuelve primero.

## Pasos

### Paso 1: Cargar Contexto al Agente

Proporciona al agente:
1. User Story completa con todos los AC
2. Secciones relevantes del Tech Design
3. Guardrails de código aplicables (si existen)

**Verificación:** El agente confirma que tiene el contexto y puede
referenciar los AC por número.

> **Si no puedes continuar:**
> Agente no reconoce AC → Verifica formato de User Story (flujo-03).
> Tech Design no carga → Verifica que existe en `.raise/specs/`.

### Paso 2: Solicitar Plan Estructurado

Usa este prompt:

```
Genera un Implementation Plan para esta User Story.
Requisitos:
- Cada paso debe ser atómico (una sola acción)
- Cada paso debe tener criterio de verificación
- Mapea cada AC a los pasos que lo implementan
- Identifica dependencias entre pasos
```

**Verificación:** El agente produce un plan con estructura clara:
pasos numerados, verificaciones, mapeo a AC.

> **Si no puedes continuar:**
> Plan sin estructura → Re-prompt pidiendo formato específico.
> Plan muy vago → Pide desglose de pasos grandes.

### Paso 3: Validar Atomicidad

Para cada paso del plan, pregunta:
- ¿Es una sola acción? (No "Crear y configurar...")
- ¿Puedo verificar si se completó?

**Verificación:** Todos los pasos pasan ambas preguntas.

> **Si no puedes continuar:**
> Pasos compuestos → Pide al agente dividir en sub-pasos.
> Pasos no verificables → Pide criterio de éxito explícito.

### Paso 4: Validar Cobertura de AC

Crea un mapeo:

| AC | Pasos que lo implementan |
|----|--------------------------|
| AC1 | Paso 2, Paso 5 |
| AC2 | Paso 3 |
| ... | ... |

**Verificación:** Cada AC tiene al menos un paso asociado.

> **Si no puedes continuar:**
> AC sin cobertura → Pide al agente añadir pasos para ese AC.
> Mapeo confuso → Pide al agente explicar cómo cada paso contribuye.

### Paso 5: Guardar Plan

Guarda el plan validado en `.raise/plans/{us-id}.md`.

**Verificación:** Archivo existe y contiene el plan completo.

> **Si no puedes continuar:**
> Error de escritura → Verifica permisos en `.raise/plans/`.

## Validation Gate: Plan

- [ ] Cada paso es atómico (una sola acción)
- [ ] Cada paso tiene criterio de verificación explícito
- [ ] Todos los AC de la US tienen pasos asociados
- [ ] Dependencias entre pasos están documentadas

> **Jidoka:** Si algún criterio falla, regresa al paso correspondiente.

---

*Kata: flujo-04 | Nivel: flujo | Gate: gate-plan*
```

---

## 10. Conexión con Constitution

### 10.1 Alineación con Principios

| Principio Constitucional | Manifestación en Kata v2.1 |
|--------------------------|---------------------------|
| §1 Humanos Definen, Máquinas Ejecutan | Kata define QUÉ; Orquestador valida CÓMO |
| §4 Validation Gates | Cada Kata termina con Gate explícito |
| §5 Heutagogía | Nivel "Principios" demanda interpretación activa |
| §6 Kaizen | Jidoka inline habilita corrección inmediata |
| §8 Observable Workflow | Pasos verificables generan trazas |

### 10.2 Principios como Nivel Superior

El nivel **Principios** conecta directamente con la Constitution:

| Principio Constitution | Kata de Principios |
|------------------------|-------------------|
| §1 Human-Centric | `principios-01-rol-orquestador.md` |
| §5 Heutagogía | `principios-02-aprendizaje-deliberado.md` |
| §6 Kaizen | `principios-03-mejora-continua.md` |

---

## 11. Auditoría Lean

### 11.1 Desperdicio Eliminado

| Muda | Antes | Después |
|------|-------|---------|
| Complejidad | 12 combinaciones (4×3) | 4 niveles |
| Archivos duplicados | Variantes Shu/Ha/Ri | Una Kata por concepto |
| Búsqueda de corrección | Sección separada | Inline en cada paso |
| Nombres sin significado | L0, L1, L2, L3 | Principios, Flujo, Patrón, Técnica |

### 11.2 Aprendizaje Amplificado

| Aspecto | Cómo se amplifica |
|---------|-------------------|
| Jidoka visible | Orquestador ve ciclo Detectar→Parar→Corregir en cada paso |
| Nombres semánticos | Pregunta guía inmediatamente clara |
| ShuHaRi como lente | Orquestador elige su nivel de interpretación |

---

## 12. Migración

### 12.1 Comandos

```bash
# Migrar nombres de archivos
raise migrate katas --to-semantic

# Verificar estructura de pasos
raise lint katas --check-jidoka-inline

# Generar reporte de migración
raise audit katas --migration-status
```

### 12.2 Compatibilidad

Los aliases `L0`, `L1`, `L2`, `L3` se mantienen para backward compatibility:

```yaml
# Ambos son válidos
level: flujo
level: L1      # Alias, se resuelve a "flujo"
```

---

## 13. Changelog

### v2.1.0 (2025-12-28)

**Cambios mayores:**
- `L0` → `principios` (nombre semántico)
- `L1` → `flujo` (nombre semántico)
- `L2` → `patron` (nombre semántico)
- `L3` → `tecnica` (nombre semántico)
- Jidoka inline en cada paso (elimina sección separada)
- ShuHaRi definido como lente, no clasificación

**Cambios menores:**
- Estructura de directorios actualizada
- Template de Kata actualizado
- Ejemplo completo añadido (flujo-04)

**Eliminado:**
- Campo `band` (propuesto en draft anterior)
- Variantes Shu/Ha/Ri de archivos
- Sección "micro-kaizen" separada

---

## 14. ADR-011: Niveles Semánticos de Kata

### Estado
✅ Accepted

### Fecha
2025-12-28

### Contexto
Los niveles L0-L3 eran técnicos y sin contenido semántico. El Orquestador debía memorizar qué significaba cada número.

### Decisión
Renombrar niveles a nombres con significado:
- L0 → **Principios** (¿Por qué? ¿Cuándo?)
- L1 → **Flujo** (¿Cómo fluye?)
- L2 → **Patrón** (¿Qué forma?)
- L3 → **Técnica** (¿Cómo hacer?)

### Razones
1. Coherencia con Lean (Principios → Value Stream → Standardized Work → Work Instructions)
2. Pregunta guía implícita en cada nombre
3. "Principios" demanda interpretación activa (alineado con §5 Heutagogía)
4. Reducción de carga cognitiva

### Consecuencias
- Migración de nombres de archivos
- Actualización de referencias en corpus
- Aliases para backward compatibility

---

## 15. ADR-012: Jidoka Inline

### Estado
✅ Accepted

### Fecha
2025-12-28

### Contexto
La propuesta inicial tenía una sección separada "micro-kaizen" al final de cada Kata. Esto separaba el problema de su resolución.

### Decisión
Embeber el ciclo Jidoka (Si no puedes continuar → Causa → Resolución) directamente en cada paso de la Kata.

### Razones
1. Contexto inmediato: la resolución está junto al problema
2. Flujo de lectura natural: no hay saltos a otra sección
3. Ciclo Jidoka explícito y visible
4. Alineado con filosofía Lean de "parar la línea"

### Consecuencias
- Template de Kata actualizado
- Cada paso requiere sección "Si no puedes continuar"
- Elimina necesidad de sección separada de corrección

---

*Este documento es parte del corpus RaiSE v2.1 y define la ontología canónica de Katas.*
