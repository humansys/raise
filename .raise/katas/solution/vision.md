---
id: solution-vision
titulo: "Solution Vision: Definir el Sistema"
work_cycle: solution
frequency: once-per-solution
fase_metodologia: 0

prerequisites:
  - solution/discovery
template: templates/raise/solution/solution_vision.md
gate: null
next_kata: setup/governance

adaptable: true
shuhari:
  shu: "Completar todas las secciones de la Solution Vision sistemáticamente"
  ha: "Enfocarse en decisiones de alto impacto; diferir detalles"
  ri: "Crear kata especializada para tipos de sistema (platform, product, service)"

multi_session: true
version: 1.0.0
---

# Solution Vision: Definir el Sistema

## Propósito

Definir **QUÉ ES el sistema** que aborda la necesidad de negocio documentada en el Business Case. La Solution Vision responde: **"¿Qué sistema construimos para resolver este problema?"**

Este artefacto es la fuente primaria para derivar Governance (guardrails) y guiar todos los proyectos dentro del sistema.

## Contexto

**Ubicación en la jerarquía (ADR-010):**

```
SOLUTION LEVEL:
  solution/discovery → [solution/vision] → setup/governance
         ↓                    ↓                   ↓
    Business Case       Solution Vision       Governance
    "¿Por qué?"         "¿Qué sistema?"       "¿Qué estándares?"
                              │
                              │ informa múltiples proyectos
                              ▼
PROJECT LEVEL:
  PRD → Project Vision → Tech Design → Backlog
```

**Cuándo usar:**
- Después de aprobar Business Case (greenfield)
- Al formalizar un sistema existente (brownfield)
- Cuando se necesita alinear equipos en la dirección técnica
- Antes de setup/governance

**Modos de ejecución:**

| Modo | Input | Proceso |
|------|-------|---------|
| **Greenfield** | Business Case aprobado | Diseñar sistema desde cero |
| **Brownfield** | Sistema existente | Documentar arquitectura actual |

**Inputs requeridos:**
- `governance/business_case.md` (prerequisito)
- Acceso a Technical Lead / Architect
- Constraints técnicos organizacionales

**Output:**
- `governance/vision.md` — Documento de Solution Vision

## Pasos

### Paso 1: Cargar Business Case

Revisar el Business Case para extraer inputs clave:

- **Problema a resolver**: ¿Qué dolor aliviamos?
- **Usuarios target**: ¿Para quién construimos?
- **Constraints de negocio**: ¿Qué limitaciones existen?
- **Métricas de éxito**: ¿Cómo medimos el éxito?

**Verificación:** Business Case cargado y comprendido.

> **Si no puedes continuar:** Business Case no existe → Ejecutar `solution/discovery` primero. Business Case desactualizado → Actualizar antes de continuar.

### Paso 2: Definir Identidad del Sistema

Establecer qué ES el sistema:

**Nombre y descripción (1-2 oraciones):**
> "[Nombre] es un [tipo de sistema] que permite a [usuarios] [capacidad principal] para [beneficio]."

**Tipo de sistema:**
- Product (B2C, B2B)
- Platform (internal, external)
- Service (API, backend)
- Tool (internal, developer)

**Misión del sistema:**
- ¿Cuál es su razón de existir?
- ¿Qué lo hace único?

**Verificación:** Identidad clara en máximo 3 oraciones.

> **Si no puedes continuar:** Identidad difusa → Volver al Business Case para clarificar propuesta de valor.

### Paso 3: Definir Alcance y Boundaries

Establecer qué INCLUYE y qué NO incluye el sistema:

**In Scope:**
- Capacidades que el sistema DEBE tener
- Usuarios que DEBE servir
- Problemas que DEBE resolver

**Out of Scope:**
- Capacidades explícitamente EXCLUIDAS
- Usuarios que NO servirá
- Problemas que NO resolverá

**Boundaries con otros sistemas:**
- ¿Dónde termina este sistema y empieza otro?
- ¿Qué responsabilidades delega?

**Verificación:** Scope documentado con boundaries claros.

> **Si no puedes continuar:** Scope creep → Aplicar YAGNI, volver a Business Case para priorizar. Boundaries difusos → Mapear sistemas adyacentes.

### Paso 4: Definir Capacidades Core

Listar las capacidades principales del sistema:

| Capacidad | Descripción | Prioridad | Usuarios |
|-----------|-------------|-----------|----------|
| [Nombre] | [Qué permite hacer] | Must/Should/Could | [Quién la usa] |

**Categorías típicas:**
- **Core**: Sin estas, el sistema no tiene sentido
- **Supporting**: Habilitan las core (auth, logging, etc.)
- **Nice-to-have**: Mejoran la experiencia pero no son esenciales

**Verificación:** Capacidades core identificadas y priorizadas.

> **Si no puedes continuar:** Demasiadas capacidades "Must" → Priorizar con MoSCoW, consultar Business Case.

### Paso 5: Definir Dirección Técnica

Establecer las decisiones técnicas fundamentales:

**Stack Tecnológico:**

| Capa | Tecnología | Justificación |
|------|------------|---------------|
| Frontend | [Tech] | [Por qué] |
| Backend | [Tech] | [Por qué] |
| Database | [Tech] | [Por qué] |
| Infrastructure | [Tech] | [Por qué] |

**Patrones Arquitectónicos:**
- Arquitectura general (Monolith, Microservices, Modular Monolith)
- Patrones de diseño (Clean Architecture, Hexagonal, etc.)
- Patrones de comunicación (REST, GraphQL, Events)

**Decisiones Fundamentales:**
Documentar como mini-ADRs o referencias a ADRs completos:

| Decisión | Opciones Consideradas | Elección | Razón |
|----------|----------------------|----------|-------|
| [Qué] | [A, B, C] | [B] | [Por qué B] |

**Verificación:** Stack y patrones definidos con justificación.

> **Si no puedes continuar:** Decisiones técnicas en conflicto → Crear ADR formal para resolver. Sin expertise → Consultar con Technical Lead/Architect.

### Paso 6: Definir Quality Attributes

Establecer requisitos no funcionales:

| Attribute | Requirement | Métrica | Target |
|-----------|-------------|---------|--------|
| **Performance** | Response time | p95 latency | < 200ms |
| **Availability** | Uptime | Monthly | 99.9% |
| **Scalability** | Concurrent users | Peak load | 10,000 |
| **Security** | Data protection | Compliance | SOC2 |
| **Maintainability** | Code quality | Coverage | 80% |

**Security Level:**
- Low: Internal tool, no sensitive data
- Medium: User data, standard auth
- High: PII, financial, compliance required
- Critical: Regulated industry (healthcare, finance)

**Verificación:** Quality attributes con targets específicos.

> **Si no puedes continuar:** Targets no definidos → Usar benchmarks de industria. Conflicto performance vs cost → Documentar tradeoffs, escalar decisión.

### Paso 7: Definir Integraciones

Mapear con qué sistemas se integra:

**Sistemas que consume (upstream):**

| Sistema | Tipo | Datos | Criticidad |
|---------|------|-------|------------|
| [Nombre] | API/DB/Event | [Qué datos] | Core/Supporting |

**Sistemas que expone (downstream):**

| Sistema | Tipo | Datos | SLA |
|---------|------|-------|-----|
| [Nombre] | API/Event | [Qué datos] | [Garantías] |

**Contratos:**
- ¿APIs documentadas con OpenAPI?
- ¿Schemas compartidos?
- ¿Contratos versionados?

**Verificación:** Mapa de integraciones completo.

> **Si no puedes continuar:** Integraciones desconocidas → Ejecutar `setup/ecosystem` en paralelo. APIs no documentadas → Documentar como riesgo.

### Paso 8: Compilar Solution Vision

Crear `governance/vision.md`:

```markdown
# Solution Vision: [Nombre del Sistema]

## Identidad
### Descripción
### Tipo de Sistema
### Misión

## Alcance
### In Scope
### Out of Scope
### Boundaries

## Capacidades Core
| Capacidad | Descripción | Prioridad |
|-----------|-------------|-----------|

## Dirección Técnica
### Stack Tecnológico
| Capa | Tecnología | Justificación |
|------|------------|---------------|

### Patrones Arquitectónicos
### Decisiones Fundamentales (ADRs)

## Quality Attributes
| Attribute | Target | Métrica |
|-----------|--------|---------|

### Security Level
[Low/Medium/High/Critical + justificación]

## Integraciones
### Upstream (consume)
### Downstream (expone)
### Contratos

## Evolución
### Roadmap de Alto Nivel
### Principios de Evolución

## Trazabilidad
| Fuente | Artefacto |
|--------|-----------|
| Business Case | `governance/business_case.md` |

## Aprobaciones
| Rol | Nombre | Fecha |
|-----|--------|-------|
```

**Verificación:** Documento completo con todas las secciones.

> **Si no puedes continuar:** Secciones incompletas → Marcar como "TBD" con owner y fecha target.

### Paso 9: Validar con Stakeholders

Revisar Solution Vision con:

- **Technical Lead/Architect**: ¿Es técnicamente viable?
- **Product Owner**: ¿Cumple con Business Case?
- **Team Lead**: ¿El equipo puede construirlo?

**Verificación:** Feedback incorporado, documento aprobado.

> **Si no puedes continuar:** Desacuerdo técnico → Crear ADR para resolver. Scope cuestionado → Volver a Business Case.

## Output

- **Artefacto:** `governance/vision.md`
- **Ubicación:** `governance/`
- **Gate:** N/A (validación por revisión de stakeholders)
- **Siguiente kata:** `setup/governance`

## Relación con Governance

La Solution Vision es el **input principal** para derivar Governance:

```
SOLUTION VISION                         GOVERNANCE
═══════════════                         ══════════

§ Dirección Técnica
  "TypeScript strict mode"        →     MUST-CODE-001: strict mode
  "Clean Architecture"            →     MUST-ARCH-001: capas separadas

§ Quality Attributes
  "99.9% availability"            →     MUST-TEST-001: 90% coverage
  "Security Level: High"          →     MUST-SEC-001: encryption

§ Integraciones
  "OpenAPI para todas las APIs"   →     MUST-API-001: documentación
```

**Solution Vision define WHAT; Governance enforcea HOW.**

## Notas por Modo

### Greenfield

En modo greenfield:

1. **Partir** del Business Case como constraint principal
2. **Diseñar** con libertad dentro de constraints
3. **Validar** viabilidad técnica temprano
4. **Iterar** con stakeholders antes de commitment

### Brownfield

En modo brownfield (sistema existente):

1. **Documentar** la arquitectura actual (as-is)
2. **Identificar** gaps vs mejores prácticas
3. **Distinguir** entre "cómo es" vs "cómo debería ser"
4. **Planear** evolución hacia target architecture

**Preguntas clave brownfield:**
- "¿Por qué se tomaron estas decisiones originalmente?"
- "¿Siguen siendo válidas hoy?"
- "¿Qué cambiaríamos si empezáramos de cero?"

## ShuHaRi

| Nivel | Aplicación |
|-------|------------|
| **Shu** | Completar todas las secciones del template sistemáticamente |
| **Ha** | Adaptar profundidad según madurez del sistema |
| **Ri** | Crear templates especializados (platform vision, service vision) |

## Referencias

- **ADR-010**: Jerarquía de Artefactos de Tres Niveles
- **Prerequisite**: `solution/discovery` (Business Case)
- **Template**: `.raise/templates/raise/solution/solution_vision.md`
- **Siguiente kata**: `setup/governance`
