---
id: governance
titulo: "Governance: Definir Guardrails de Sistema"
work_cycle: setup
frequency: once-per-solution
fase_metodologia: 0

prerequisites:
  greenfield: [solution/vision]
  brownfield: []
template: templates/raise/governance/guardrail.mdc
gate: null
next_kata: setup/rules

adaptable: true
shuhari:
  shu: "Responder todas las preguntas de gobernanza sistemáticamente"
  ha: "Enfocarse en guardrails de alto impacto primero"
  ri: "Crear kata de Governance para dominios específicos (fintech, healthcare)"

multi_session: true
version: 2.0.0
---

# Governance: Definir Guardrails de Sistema

## Propósito

Establecer los guardrails a nivel de **solución/sistema** que definen WHAT se enforce en todo el desarrollo. Los guardrails son la fuente única de verdad que:

1. **Guían generación** — Proveen Golden Context para agentes AI
2. **Validan resultados** — Definen criterios de Governance Gates
3. **Previenen drift** — Aplican consistentemente en todos los proyectos y repos del sistema

## Contexto

**Ubicación en la jerarquía (ADR-010):**

```
SOLUTION LEVEL:
  Business Case → Solution Vision → [setup/governance] ← Este kata
                                           │
                                           │ constrains
                                           ▼
PROJECT LEVEL:
  PRD → Project Vision → Tech Design → Backlog
```

**Cuándo usar:**
- Después de definir Solution Vision (greenfield)
- Al adoptar RaiSE en un sistema existente (brownfield)
- Cuando se quiere formalizar estándares de equipo
- Antes de cualquier proyecto en el sistema

**Modos de ejecución:**

| Modo | Input | Proceso |
|------|-------|---------|
| **Greenfield** | Solution Vision + Principios RaiSE | Derivar guardrails de constraints del sistema |
| **Brownfield** | Codebase existente + Deuda técnica | Extraer patrones, identificar brechas, formalizar |

**Inputs requeridos:**
- Greenfield: `governance/solution/vision.md` (nivel solución)
- Brownfield: Acceso al repositorio
- Ambos: Decisiones del equipo sobre estándares

**Output:**
- `governance/solution/guardrails.md` — Documento de política y guardrails
- `governance/guardrails/*.mdc` — Guardrails individuales (si se separan)

## Pasos

### Paso 1: Determinar Modo de Ejecución

Identificar si es greenfield o brownfield:

- **Greenfield**: No existe código, se parte de Solution Vision (nivel sistema)
- **Brownfield**: Existe código, se extrae y formaliza

**Verificación:** Modo identificado y prerequisites validados.

> **Si no puedes continuar:** Greenfield sin Solution Vision → Ejecutar `solution/vision` primero. Brownfield sin acceso a código → Obtener acceso al repositorio.

### Paso 2: Cargar Contexto Base

**Greenfield:**
- Cargar `governance/solution/vision.md` (Solution Vision - nivel sistema)
- Cargar `governance/solution/business_case.md` si existe (Business Case)
- Cargar principios RaiSE desde constitution
- Identificar restricciones técnicas declaradas en Solution Vision:
  - Stack tecnológico
  - Quality attributes
  - Security level
  - Compliance requirements

**Brownfield:**
- Ejecutar análisis estructural del codebase
- Identificar patrones existentes (arquitectura, testing, etc.)
- Detectar inconsistencias y deuda técnica
- Documentar Solution Vision implícita (reverse engineering)

**Verificación:** Contexto cargado y documentado.

> **Si no puedes continuar:** Solution Vision no encontrada → Ejecutar `solution/vision` primero. Documentos no encontrados → Verificar `governance/solution/` directory.

### Paso 3: Derivar Guardrails de Solution Vision

La Solution Vision define el sistema; la Governance enforcea sus constraints:

| Solution Vision dice... | Governance deriva... |
|------------------------|---------------------|
| "Stack: TypeScript strict" | MUST-CODE-*: TypeScript strict mode |
| "Security level: High" | MUST-SEC-*: JWT, RBAC, encryption |
| "Quality: 99.9% uptime" | MUST-TEST-*: 90% coverage, integration |
| "API: REST, OpenAPI" | MUST-API-*: versionado, documentación |

Recorrer las categorías estándar de guardrails:

| Categoría | Fuente en Solution Vision | Ejemplo Guardrail |
|-----------|--------------------------|-------------------|
| **Arquitectura** | Dirección técnica, patrones | MUST: Clean Architecture |
| **Testing** | Quality attributes | SHOULD: 80% coverage |
| **Seguridad** | Security level, compliance | MUST: JWT + RBAC |
| **API** | Integraciones, contratos | MUST: OpenAPI spec |
| **Código** | Stack tecnológico | SHOULD: ESLint strict |
| **Errores** | Quality attributes | MUST: Error boundaries |
| **Documentación** | Governance philosophy | SHOULD: ADRs para decisiones |

**Verificación:** Todas las categorías evaluadas y trazadas a Solution Vision.

> **Si no puedes continuar:** Categoría sin respuesta clara → Marcar como "PENDIENTE: Requiere decisión de equipo" y continuar. El kata soporta progreso incremental.

### Paso 4: Definir Nivel de Cada Guardrail

Para cada guardrail identificado, asignar nivel:

| Nivel | Significado | Durante Generación | Durante Validación |
|-------|-------------|-------------------|-------------------|
| **MUST** | Obligatorio, no negociable | "Debes hacer esto" | Gate bloqueante |
| **SHOULD** | Recomendado, excepciones justificadas | "Deberías hacer esto" | Gate de advertencia |
| **MAY** | Opcional, buena práctica | "Puedes hacer esto" | Sin gate |

**Criterios de decisión:**
- MUST: Impacto en seguridad, compliance, o funcionalidad crítica
- SHOULD: Impacto en calidad, mantenibilidad
- MAY: Preferencias de estilo, optimizaciones opcionales

**Verificación:** Cada guardrail tiene nivel asignado con justificación.

> **Si no puedes continuar:** Desacuerdo sobre nivel → Documentar ambas posiciones y escalar a decisión de equipo.

### Paso 5: Escribir Guardrails en Formato .mdc

Para cada guardrail, crear archivo `.mdc`:

```yaml
# governance/guardrails/{categoria}.mdc
---
id: {LEVEL}-{CATEGORY}-{NUMBER}
level: MUST | SHOULD | MAY
scope: "glob/pattern/**/*.ts"
version: 1.0.0
derived_from: "Solution Vision - {sección}"
---

# {Título del Guardrail}

## Regla

[Descripción clara de QUÉ debe cumplirse]

## Contexto (Golden Context para Agentes)

[Instrucciones para generación de código/artefactos]

## Verificación (Criterios de Gate)

```yaml
check: {tipo}
command: {comando si aplica}
threshold: {valor si aplica}
blocking: true | false  # Derivado del level
on_failure:
  message: "{mensaje de error}"
  recovery: "{acción de recuperación}"
```

## Ejemplos

### Correcto
[Ejemplo de código/artefacto que cumple]

### Incorrecto
[Ejemplo de código/artefacto que NO cumple]
```

**Verificación:** Archivos .mdc creados con todas las secciones.

> **Si no puedes continuar:** Schema incorrecto → Verificar contra template en `.raise/templates/governance/guardrail.mdc`.

### Paso 6: Crear Documento de Política

Crear `governance/solution/guardrails.md`:

```markdown
# Guardrails: [Nombre del Sistema]

## Contexto del Sistema
[Breve descripción del sistema - referencia a Solution Vision]

## Trazabilidad
| Fuente | Artefacto |
|--------|-----------|
| Business Case | `governance/solution/business_case.md` |
| Solution Vision | `governance/solution/vision.md` |

## Principios Rectores
[Principios derivados de Solution Vision que guían estas decisiones]

## Guardrails Activos

| ID | Categoría | Nivel | Descripción | Derivado de |
|----|-----------|-------|-------------|-------------|
| MUST-ARCH-001 | Arquitectura | MUST | Clean Architecture | Solution Vision §Dirección Técnica |
| ... | ... | ... | ... | ... |

## Proceso de Excepción
[Cómo solicitar excepciones via ADR]

## Historial de Cambios
[Registro de evolución]
```

**Verificación:** Documento de política creado y consistente con guardrails.

> **Si no puedes continuar:** Inconsistencia detectada → Revisar guardrails vs documento de política.

### Paso 7: Validar Coherencia

Verificaciones finales:

- [ ] Todos los guardrails tienen las secciones requeridas
- [ ] IDs son únicos y siguen convención `{LEVEL}-{CATEGORY}-{NUMBER}`
- [ ] Levels son consistentes con el impacto declarado
- [ ] Documento de política lista todos los guardrails activos
- [ ] No hay contradicciones entre guardrails
- [ ] Guardrails son trazables a Solution Vision

**Verificación:** Validación de coherencia pasada.

> **Si no puedes continuar:** Contradicción detectada → Resolver antes de continuar. Documentar resolución.

### Paso 8: Marcar Progreso (Multi-Session)

Si la sesión termina antes de completar:

1. Documentar guardrails completados vs pendientes en `governance.md`
2. Listar preguntas pendientes para el equipo
3. Guardar estado para próxima sesión

El kata puede resumirse desde cualquier punto.

**Verificación:** Estado guardado y documentado.

> **Si no puedes continuar:** N/A — Este paso siempre puede completarse.

## Output

- **Artefactos:**
  - `governance/solution/guardrails.md` — Documento de política y guardrails
  - `governance/guardrails/*.mdc` — Guardrails individuales (optional, for complex systems)
- **Ubicación:** `governance/solution/` y `governance/guardrails/`
- **Gate:** N/A (validación integrada en Paso 7)
- **Siguiente kata:** `setup/rules`

## Notas por Modo

### Greenfield

En modo greenfield, el agente:

1. **Carga** Solution Vision como fuente primaria
2. **Deriva** guardrails de los constraints declarados
3. **Propone** guardrails adicionales basados en principios RaiSE
4. **Itera** con el equipo hasta aprobación
5. **Documenta** trazabilidad a Solution Vision

**Derivación típica:**

```
SOLUTION VISION                         GOVERNANCE
═══════════════                         ══════════

§ Dirección Técnica
  "TypeScript strict mode"        →     MUST-CODE-001: strict mode
  "Clean Architecture"            →     MUST-ARCH-001: capas separadas

§ Quality Attributes
  "99.9% availability"            →     MUST-TEST-001: 90% coverage
  "< 200ms response time"         →     SHOULD-PERF-001: benchmarks

§ Security Level
  "SOC2 compliance required"      →     MUST-SEC-001: audit logging
  "PII encryption at rest"        →     MUST-SEC-002: encryption
```

### Brownfield

En modo brownfield, el agente:

1. **Analiza** código existente para extraer patrones
2. **Documenta** Solution Vision implícita (reverse engineering)
3. **Identifica** brechas entre práctica actual y mejores prácticas
4. **Propone** formalización de patrones exitosos
5. **Señala** deuda técnica como guardrails SHOULD/MAY futuros

**Orden sugerido en brownfield:**

```
1. setup/governance (extraer del código)
       ↓
2. solution/vision (documentar lo extraído)
       ↓
3. solution/discovery (documentar Business Case si no existe)
```

## ShuHaRi

| Nivel | Aplicación |
|-------|------------|
| **Shu** | Derivar guardrails sistemáticamente de cada sección de Solution Vision |
| **Ha** | Priorizar constraints de alto impacto; omitir MAY en primera iteración |
| **Ri** | Crear kata especializada para dominio (fintech: compliance, healthcare: HIPAA) |

## Fundamento Teórico: Modelo de Grounding de 3+1 Capas

Este kata implementa la **Capa 3 (Guardrails)** del modelo de grounding validado por investigación multi-disciplinaria:

```
PRINCIPIOS (Capa 1 - Universal, Inmutable)
    │ constrain + evaluate + recovery criteria
    ▼
ARQUITECTURA (Capa 2 - Sistema-específica, Mutable)
    │ ground + contextualize + pattern library
    ▼
GUARDRAILS (Capa 3 - Accionable, Derivada)  ← Este kata
    │ execute + validate + enforce
    ▼
COMPORTAMIENTO DEL AGENTE
    │ feedback loop (Kaizen)
    ▼
[CAPA DE APRENDIZAJE (+1)]
```

### Relación con Jerarquía de Artefactos (ADR-010)

```
SOLUTION LEVEL:
  Business Case → Solution Vision → Governance (este kata)
  "¿Por qué?"     "¿Qué sistema?"    "¿Qué estándares?"
       │               │                    │
       │               │                    │
       └───────────────┴────────────────────┘
                       │
            constrains all projects
                       │
                       ▼
PROJECT LEVEL:
  PRD → Project Vision → Tech Design
```

**Solution Vision define WHAT the system is; Governance defines HOW to enforce its constraints.**

### Por qué las 3 Capas son Necesarias

| Sin esta capa | Consecuencia | Evidencia |
|---------------|--------------|-----------|
| Sin Principios | Agente perpetúa patrones malos | Argyris: "theory-in-use perpetuates problems" |
| Sin Arquitectura | Agente carece de contexto para acción coherente | Harnad: "symbol grounding problem" |
| Sin Guardrails | Agente carece de constraints accionables | LLM studies: 62% vs 84% correctness |

### Función de Cada Capa

| Capa | Pregunta que responde | Implementación RaiSE |
|------|----------------------|----------------------|
| **Principios** | "¿Por qué?" + "¿Qué NO hacer?" | Constitution (sec 1-8) |
| **Arquitectura** | "¿Qué es?" + "¿Cómo hacemos las cosas aquí?" | Solution Vision, Golden Data, ADRs |
| **Guardrails** | "¿Qué hacer?" + "¿Cómo verificar?" | `.raise/governance/guardrails/*.mdc` |

> **Research reference**: `specs/main/research/outputs/layered-grounding-analysis.md`

## Referencias

- **ADR-010**: `framework/decisions/adr-010-three-level-artifact-hierarchy.md`
- **ADR-009**: `framework/decisions/adr-009-continuous-governance-model.md`
- **ADR-011**: `framework/decisions/adr-011-three-directory-model.md`
- **Research**: Layered Grounding Analysis (RES-LAYERED-GROUNDING-001)
- **Template**: `.raise/templates/governance/guardrails.md`
- **Questions Catalog**: `.raise/templates/governance/governance-questions.md`
- **Constitution RaiSE**: `framework/context/constitution.md`
- **Prerequisite kata**: `solution/vision`
- **Siguiente kata**: `setup/rules`
