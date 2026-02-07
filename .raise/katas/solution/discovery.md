---
id: solution-discovery
titulo: "Solution Discovery: Crear Business Case"
work_cycle: solution
frequency: once-per-solution
fase_metodologia: 0

prerequisites: []
template: templates/raise/solution/business_case.md
gate: null
next_kata: solution/vision

adaptable: true
shuhari:
  shu: "Responder todas las preguntas del Business Case sistemáticamente"
  ha: "Enfocarse en justificación de alto impacto; simplificar para startups"
  ri: "Crear kata especializada para contextos específicos (enterprise, startup, internal)"

multi_session: true
version: 1.0.0
---

# Solution Discovery: Crear Business Case

## Propósito

Documentar la **justificación de negocio** para un sistema/solución. El Business Case responde la pregunta fundamental: **"¿Por qué debe existir este sistema?"**

Este es el primer artefacto en la jerarquía de tres niveles (ADR-010) y sirve como fundamento para todas las decisiones posteriores.

## Contexto

**Ubicación en la jerarquía (ADR-010):**

```
SOLUTION LEVEL:
  [solution/discovery] → solution/vision → setup/governance
         ↓
    Business Case        Solution Vision      Governance
    "¿Por qué?"          "¿Qué sistema?"      "¿Qué estándares?"
```

**Cuándo usar:**
- Al iniciar un nuevo sistema/producto (greenfield)
- Al formalizar un sistema existente que carece de documentación (brownfield)
- Cuando se necesita justificar inversión ante stakeholders
- Antes de definir Solution Vision

**Modos de ejecución:**

| Modo | Input | Proceso |
|------|-------|---------|
| **Greenfield** | Oportunidad de negocio identificada | Documentar desde cero con stakeholders |
| **Brownfield** | Sistema existente sin documentación | Reverse engineering de la justificación |

**Inputs requeridos:**
- Acceso a stakeholders (Product Owner, sponsors, usuarios clave)
- Contexto de mercado/negocio
- Constraints organizacionales conocidos

**Output:**
- `governance/business_case.md` — Documento de Business Case

## Pasos

### Paso 1: Identificar Stakeholders Clave

Mapear quién tiene interés en el sistema:

| Rol | Pregunta que responde |
|-----|----------------------|
| **Sponsor/Executive** | ¿Por qué invertir? ¿Cuál es el ROI? |
| **Product Owner** | ¿Qué problema de usuario resuelve? |
| **Technical Lead** | ¿Es técnicamente viable? |
| **End Users** | ¿Qué dolor alivia? |
| **Operations** | ¿Cómo se mantiene? |

**Verificación:** Lista de stakeholders con su rol y contacto.

> **Si no puedes continuar:** Stakeholders no identificados → Escalar a quien solicitó el sistema. Sin sponsor → El sistema carece de justificación de negocio.

### Paso 2: Documentar la Oportunidad de Negocio

Responder las preguntas fundamentales:

**¿Qué problema existe?**
- Descripción del problema actual
- Quién sufre este problema
- Impacto cuantificable (tiempo perdido, dinero, frustración)

**¿Por qué existe este problema?**
- Causas raíz identificadas
- Por qué no se ha resuelto antes
- Qué ha cambiado que hace viable resolverlo ahora

**¿Qué oportunidad representa?**
- Mercado o audiencia objetivo
- Tamaño de la oportunidad
- Ventana de tiempo

**Verificación:** Sección de oportunidad documentada con datos concretos.

> **Si no puedes continuar:** Problema no claro → Realizar más entrevistas con usuarios. Sin datos de impacto → Estimar orden de magnitud con stakeholders.

### Paso 3: Definir Propuesta de Valor

Articular cómo el sistema resuelve el problema:

**Propuesta de valor (1-2 oraciones):**
> "[Sistema] permite a [usuarios] resolver [problema] mediante [mecanismo], resultando en [beneficio medible]."

**Diferenciadores:**
- ¿Por qué este approach vs alternativas?
- ¿Qué hace único a este sistema?
- ¿Cuál es la ventaja competitiva?

**Verificación:** Propuesta de valor clara y diferenciada.

> **Si no puedes continuar:** Propuesta genérica → Refinar con "¿Por qué nosotros? ¿Por qué ahora?". Sin diferenciadores → Considerar si el sistema debe existir.

### Paso 4: Identificar Stakeholders y Usuarios

Documentar quiénes interactúan con el sistema:

**Usuarios primarios:**
- Quiénes usan el sistema directamente
- Sus características y necesidades
- Frecuencia y contexto de uso

**Usuarios secundarios:**
- Quiénes se benefician indirectamente
- Administradores, soporte, etc.

**Stakeholders de negocio:**
- Quiénes toman decisiones
- Quiénes financian
- Quiénes miden el éxito

**Verificación:** Mapa de stakeholders completo.

> **Si no puedes continuar:** Usuarios no claros → Crear proto-personas. Conflicto entre stakeholders → Documentar y escalar para resolución.

### Paso 5: Documentar Constraints de Negocio

Identificar limitaciones no negociables:

| Categoría | Preguntas | Ejemplo |
|-----------|-----------|---------|
| **Compliance** | ¿Qué regulaciones aplican? | GDPR, HIPAA, SOC2 |
| **Presupuesto** | ¿Cuál es el budget? | $X para MVP |
| **Timeline** | ¿Hay fecha límite? | Launch en Q3 |
| **Recursos** | ¿Qué equipo está disponible? | 3 devs, 1 PM |
| **Tecnología** | ¿Hay restricciones de stack? | Debe usar cloud X |
| **Integración** | ¿Con qué sistemas debe integrarse? | ERP existente |

**Verificación:** Constraints documentados con fuente/justificación.

> **Si no puedes continuar:** Constraints contradictorios → Escalar para priorización. Budget no definido → Estimar rangos con sponsor.

### Paso 6: Definir Métricas de Éxito

Establecer cómo se medirá el éxito del sistema:

**Métricas de negocio (lagging):**
- Revenue impact
- Cost reduction
- User acquisition/retention

**Métricas de producto (leading):**
- Adoption rate
- Feature usage
- User satisfaction (NPS, CSAT)

**Métricas técnicas:**
- Performance
- Reliability
- Security incidents

**Formato:**

| Métrica | Baseline | Target | Timeframe |
|---------|----------|--------|-----------|
| [Nombre] | [Actual] | [Meta] | [Cuándo] |

**Verificación:** Al menos 3 métricas con targets específicos.

> **Si no puedes continuar:** Métricas vagas → Aplicar SMART (Specific, Measurable, Achievable, Relevant, Time-bound). Sin baseline → Establecer medición inicial como primera tarea.

### Paso 7: Evaluar Riesgos y Mitigaciones

Identificar qué puede salir mal:

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| [Descripción] | Alta/Media/Baja | Alto/Medio/Bajo | [Acción] |

**Categorías de riesgo:**
- **Mercado**: ¿El problema persiste? ¿Hay competencia?
- **Técnico**: ¿Es factible? ¿Hay dependencias riesgosas?
- **Recursos**: ¿Tenemos el equipo? ¿El presupuesto?
- **Organizacional**: ¿Hay apoyo? ¿Cambios políticos?

**Verificación:** Top 5 riesgos documentados con mitigaciones.

> **Si no puedes continuar:** Riesgos críticos sin mitigación → Escalar antes de continuar. El sistema puede no ser viable.

### Paso 8: Compilar Business Case

Crear `governance/business_case.md` con estructura:

```markdown
# Business Case: [Nombre del Sistema]

## Executive Summary
[1 párrafo: problema, solución, beneficio esperado]

## Oportunidad de Negocio
### Problema
### Causas
### Oportunidad

## Propuesta de Valor
### Propuesta
### Diferenciadores

## Stakeholders y Usuarios
### Usuarios Primarios
### Usuarios Secundarios
### Stakeholders de Negocio

## Constraints
| Categoría | Constraint | Fuente |
|-----------|-----------|--------|

## Métricas de Éxito
| Métrica | Baseline | Target | Timeframe |
|---------|----------|--------|-----------|

## Riesgos y Mitigaciones
| Riesgo | P | I | Mitigación |
|--------|---|---|------------|

## Recomendación
[Go / No-Go / Condicional]

## Aprobaciones
| Rol | Nombre | Fecha | Decisión |
|-----|--------|-------|----------|
```

**Verificación:** Documento completo con todas las secciones.

> **Si no puedes continuar:** Secciones incompletas → Marcar como "TBD" y documentar qué falta para completar.

### Paso 9: Obtener Aprobación

Presentar Business Case a stakeholders para decisión:

- **Go**: Proceder a Solution Vision
- **No-Go**: Documentar razones, archivar
- **Condicional**: Documentar condiciones a cumplir

**Verificación:** Decisión documentada con firmas/aprobaciones.

> **Si no puedes continuar:** Sin decisión → Agendar sesión de decisión con deadline. Stakeholders en desacuerdo → Escalar a sponsor ejecutivo.

## Output

- **Artefacto:** `governance/business_case.md`
- **Ubicación:** `governance/`
- **Gate:** N/A (validación por aprobación de stakeholders)
- **Siguiente kata:** `solution/vision`

## Notas por Modo

### Greenfield

En modo greenfield:

1. **Comenzar** con entrevistas a stakeholders
2. **Iterar** el documento con feedback
3. **Validar** assumptions con datos de mercado
4. **Obtener** aprobación formal antes de continuar

### Brownfield

En modo brownfield (sistema existente sin Business Case):

1. **Entrevistar** a quienes crearon/mantienen el sistema
2. **Reconstruir** la justificación original
3. **Validar** si la justificación sigue vigente
4. **Actualizar** con contexto actual

**Pregunta clave brownfield**: "Si tuviéramos que justificar este sistema hoy, ¿lo haríamos?"

## ShuHaRi

| Nivel | Aplicación |
|-------|------------|
| **Shu** | Completar todas las secciones del template sistemáticamente |
| **Ha** | Adaptar profundidad según contexto (startup vs enterprise) |
| **Ri** | Crear templates especializados (B2B SaaS, internal tools, platform) |

## Referencias

- **ADR-010**: Jerarquía de Artefactos de Tres Niveles
- **Template**: `.raise/templates/raise/solution/business_case.md`
- **Siguiente kata**: `solution/vision`
