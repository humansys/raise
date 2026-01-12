# RaiSE Kata Schema v2.1

## Estructura de Katas para el Modelo Híbrido

**Versión:** 2.1.0
**Fecha:** 12 de Enero, 2026
**Propósito:** Definir el schema canónico para Katas bajo el Modelo Híbrido (ADR-011).

> **Nota v2.1:** Este schema reemplaza el anterior basado en L0-L3. Adopta nombres semánticos (principios/flujo/patron/tecnica) y formaliza la relación Kata → Template → Validation Gate.

---

## Modelo Híbrido: Las Tres Capas

```
┌─────────────────────────────────────────────────────────────┐
│   TEMPLATE              KATA                VALIDATION GATE │
│   ─────────            ─────               ──────────────── │
│   ¿QUÉ produce?        ¿CÓMO hacerlo?      ¿ESTÁ BIEN?      │
│                                                             │
│   Estructura           Proceso             Checklist        │
│   del artefacto        con Jidoka          de criterios     │
└─────────────────────────────────────────────────────────────┘
```

| Componente | Responsabilidad | Ubicación | Personalizable por |
|------------|-----------------|-----------|-------------------|
| **Template** | Estructura del output | `templates/` | Organización/Proyecto |
| **Kata** | Proceso para producirlo | `katas/` | Framework RaiSE |
| **Validation Gate** | Criterios de aceptación | `gates/` | Proyecto/Fase |

---

## Niveles Semánticos de Kata

| Nivel | Pregunta Guía | Propósito | Conexión Lean |
|-------|---------------|-----------|---------------|
| **principios** | ¿Por qué? ¿Cuándo? | Filosofía y meta-proceso | Toyota Way Principles |
| **flujo** | ¿Cómo fluye? | Secuencias de valor por fase | Value Stream Mapping |
| **patron** | ¿Qué forma? | Estructuras reutilizables | Standardized Work |
| **tecnica** | ¿Cómo hacer? | Instrucciones específicas | Work Instructions |

### Migración de Nomenclatura

| Antes (v2.0) | Después (v2.1) | Alias Preservado |
|--------------|----------------|------------------|
| `L0` | `principios` | ✅ L0 sigue válido |
| `L1` | `flujo` | ✅ L1 sigue válido |
| `L2` | `patron` | ✅ L2 sigue válido |
| `L3` | `tecnica` | ✅ L3 sigue válido |

---

## Schema de Kata

### Frontmatter (YAML)

```yaml
---
# === IDENTIFICACIÓN ===
id: flujo-01-discovery                    # Patrón: {nivel}-{numero}-{nombre}
nivel: flujo                              # enum: principios, flujo, patron, tecnica
titulo: "Discovery: Creación del PRD"    # Nombre descriptivo

# === AUDIENCIA (ADR-009) ===
audience: intermediate                    # enum: beginner, intermediate, advanced

# === RELACIONES (ADR-011) ===
template_asociado: templates/solution/project_requirements.md   # Opcional
validation_gate: gates/gate-discovery.md                        # Opcional
prerequisites:                            # Katas previas requeridas
  - principios-01-execution-protocol

# === METADATOS ===
fase_metodologia: 1                       # Fase RaiSE (0-7) que cubre
tags: [discovery, prd, requisitos]
version: 1.0.0
---
```

### Campos Requeridos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador único. Patrón: `{nivel}-{numero}-{nombre-kebab}` |
| `nivel` | enum | `principios`, `flujo`, `patron`, `tecnica` |
| `titulo` | string | Nombre descriptivo de la kata |
| `audience` | enum | `beginner`, `intermediate`, `advanced` (ADR-009) |

### Campos Opcionales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `template_asociado` | path | Ruta al template que esta kata llena |
| `validation_gate` | path | Ruta al gate que valida el output |
| `prerequisites` | array | IDs de katas que deben completarse antes |
| `fase_metodologia` | int | Fase RaiSE (0-7) que esta kata cubre |
| `tags` | array | Etiquetas para búsqueda/filtrado |
| `version` | semver | Versión de la kata |

---

## Estructura del Contenido

### Secciones Obligatorias

```markdown
# {Título de la Kata}

## Propósito

[1-2 párrafos explicando para qué sirve esta kata y cuándo usarla]

## Contexto

[Cuándo aplicar esta kata, prerequisitos, inputs necesarios]

## Pasos

### Paso 1: {Nombre del Paso}

{Instrucciones detalladas del paso}

**Verificación:** {Cómo saber si el paso se completó correctamente}

> **Si no puedes continuar:** {Causa probable} → {Resolución sugerida}

### Paso 2: {Nombre del Paso}

...

## Output

[Descripción del artefacto producido y dónde guardarlo]
```

### Secciones Opcionales

```markdown
## Pre-condiciones

[Lista de condiciones que deben cumplirse antes de iniciar]

## Notas

[Consejos, advertencias, variaciones por contexto]

## Referencias

[Links a documentos relacionados, ADRs, etc.]
```

---

## Jidoka Inline

Cada paso DEBE incluir verificación y guía de corrección embebida:

```markdown
### Paso N: {Acción}

{Instrucciones del paso}

**Verificación:** {Criterio observable de éxito}

> **Si no puedes continuar:** {Causa} → {Resolución}
```

### Principios de Jidoka Inline

1. **Verificación observable**: El criterio debe ser verificable sin ambigüedad
2. **Causa específica**: Identificar la causa más probable del bloqueo
3. **Resolución accionable**: La resolución debe ser un paso concreto
4. **No acumular errores**: Si falla, parar antes de continuar

### Ejemplos de Jidoka Inline

**Bueno:**
```markdown
**Verificación:** El PRD tiene todas las secciones del template completadas y el Product Owner ha confirmado que refleja su visión.

> **Si no puedes continuar:** PRD incompleto → Revisar secciones vacías del template y agendar sesión de clarificación con Product Owner.
```

**Malo:**
```markdown
**Verificación:** El PRD está listo.

> **Si no puedes continuar:** Algo falló → Revisar.
```

---

## Katas del Flujo Principal

Según ADR-011, las katas del flujo principal mapean a las fases de la metodología:

| Kata ID | Fase | Template Asociado | Validation Gate |
|---------|------|-------------------|-----------------|
| `flujo-01-discovery` | 1 | `project_requirements.md` | `gate-discovery` |
| `flujo-02-solution-vision` | 2 | `solution-vision-template.md` | `gate-vision` |
| `flujo-03-tech-design` | 3 | `tech_design.md` | `gate-design` |
| `flujo-04-implementation-plan` | 5 | — | `gate-plan` |
| `flujo-05-backlog-creation` | 4 | `user_story.md` | `gate-backlog` |
| `flujo-06-development` | 6 | — | `gate-code` |

> **Nota:** `flujo-04` no tiene template porque genera planes ad-hoc. `flujo-06` usa guardrails, no templates.

---

## Katas de Patrón

Patrones reutilizables para contextos específicos:

| Kata ID | Contexto | Propósito |
|---------|----------|-----------|
| `patron-01-code-analysis` | Brownfield | Analizar código existente antes de modificar |
| `patron-02-ecosystem-discovery` | Brownfield | Mapear ecosistema de servicios |

---

## Ejemplo Completo: flujo-01-discovery

```markdown
---
id: flujo-01-discovery
nivel: flujo
titulo: "Discovery: Creación del PRD"
audience: beginner
template_asociado: templates/solution/project_requirements.md
validation_gate: gates/gate-discovery.md
prerequisites: []
fase_metodologia: 1
tags: [discovery, prd, requisitos, fase-1]
version: 1.0.0
---

# Discovery: Creación del PRD

## Propósito

Transformar las notas de reuniones de discovery y el contexto inicial del proyecto en un PRD (Product Requirements Document) estructurado que sirva como contrato entre stakeholders y el equipo técnico.

## Contexto

**Cuándo usar:** Al iniciar un nuevo proyecto o feature significativo, después de las reuniones iniciales con stakeholders.

**Inputs requeridos:**
- Notas de reuniones de discovery
- Contexto del proyecto (Fase 0)
- Acceso a stakeholders para clarificaciones

**Output:** PRD completado siguiendo `templates/solution/project_requirements.md`

## Pasos

### Paso 1: Cargar Contexto Inicial

Recopilar todas las notas de reuniones, correos y documentos previos que capturen la visión inicial del proyecto.

**Verificación:** Existe un documento o carpeta con todo el contexto inicial consolidado y accesible.

> **Si no puedes continuar:** Contexto disperso o incompleto → Solicitar al Orquestador que consolide las notas de reuniones antes de continuar.

### Paso 2: Instanciar Template PRD

Crear una copia del template `templates/solution/project_requirements.md` con el nombre del proyecto.

**Verificación:** Existe archivo `{proyecto}-prd.md` con todas las secciones del template vacías pero presentes.

> **Si no puedes continuar:** Template no encontrado → Verificar que `templates/solution/project_requirements.md` existe en el repositorio.

### Paso 3: Articular el Problema de Negocio

Completar la sección "Problem Statement" del PRD, respondiendo:
- ¿Quién tiene el problema?
- ¿Cuál es el impacto del problema?
- ¿Por qué es importante resolverlo ahora?

**Verificación:** La sección Problem Statement está completa y un stakeholder no técnico puede entenderla.

> **Si no puedes continuar:** Problema no claro → Agendar sesión de 30 min con Product Owner para clarificar el problema central.

### Paso 4: Definir Metas y Métricas de Éxito

Completar la sección "Goals & Success Metrics" con:
- Metas de negocio cuantificables
- Métricas que indicarán éxito
- Targets específicos

**Verificación:** Cada meta tiene al menos una métrica asociada con target numérico.

> **Si no puedes continuar:** Métricas vagas → Preguntar "¿Cómo sabremos que tuvimos éxito?" hasta obtener números concretos.

### Paso 5: Documentar Alcance (In/Out)

Completar la sección "Scope" especificando explícitamente:
- Lo que SÍ está incluido en este proyecto
- Lo que NO está incluido (y por qué)

**Verificación:** Las listas In-Scope y Out-of-Scope son mutuamente excluyentes y cubren las áreas de ambigüedad común.

> **Si no puedes continuar:** Alcance ambiguo → Listar 3-5 áreas grises y pedir decisión explícita a stakeholders.

### Paso 6: Listar Requisitos Funcionales y No-Funcionales

Completar las secciones de requisitos:
- Funcionales: qué debe hacer el sistema
- No-funcionales: cómo debe comportarse (rendimiento, seguridad, etc.)

**Verificación:** Cada requisito es testeable (se puede escribir un criterio de aceptación para él).

> **Si no puedes continuar:** Requisitos no testeables → Reformular como "El sistema debe [acción observable] cuando [condición]".

### Paso 7: Documentar Supuestos y Riesgos

Completar las secciones finales:
- Supuestos: lo que asumimos verdadero sin verificar
- Riesgos: lo que podría salir mal y cómo mitigarlo

**Verificación:** Hay al menos 3 supuestos y 3 riesgos documentados.

> **Si no puedes continuar:** No se identifican riesgos → Preguntar "¿Qué pasaría si [recurso clave] no está disponible?" para cada dependencia.

### Paso 8: Validar PRD con Stakeholders

Presentar el PRD completo a los stakeholders para aprobación.

**Verificación:** El PRD tiene aprobación explícita (email, comentario, firma) de al menos un stakeholder clave.

> **Si no puedes continuar:** Stakeholder no disponible → Documentar intento de validación y proceder con nota de "pendiente aprobación formal".

## Output

- **Artefacto:** PRD completado
- **Ubicación:** `.raise/specs/{proyecto}-prd.md`
- **Siguiente paso:** Pasar Gate-Discovery, luego ejecutar `flujo-02-solution-vision`

## Referencias

- Template: `templates/solution/project_requirements.md`
- Gate: `gates/gate-discovery.md`
- Metodología: `21-methodology-v2.md` §Fase 1
```

---

## Validación de Kata

Una kata bien formada cumple:

| Criterio | Verificación |
|----------|-------------|
| ID único | Patrón `{nivel}-{numero}-{nombre}` |
| Nivel válido | Uno de: principios, flujo, patron, tecnica |
| Pregunta guía | El contenido responde la pregunta del nivel |
| Jidoka completo | Cada paso tiene **Verificación** y **Si no puedes continuar** |
| Verificación observable | Criterios concretos, no vagos |
| Resolución accionable | Pasos concretos, no "revisar" |
| Template enlazado | Si produce artefacto, referencia template |
| Gate enlazado | Referencia el gate correspondiente |

---

## Changelog

### v2.1.0 (2026-01-12)
- NUEVO: Schema completo para Modelo Híbrido (ADR-011)
- NUEVO: Campos `template_asociado` y `validation_gate`
- NUEVO: Niveles semánticos reemplazan L0-L3
- NUEVO: Ejemplo completo `flujo-01-discovery`
- NUEVO: Criterios de validación de kata

---

*Este schema define la estructura canónica de Katas v2.1. Todas las katas nuevas deben seguir este formato.*
