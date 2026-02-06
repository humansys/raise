# Análisis: Creación de Comandos en .raise-kit

**Fecha**: 2026-01-20
**Autor**: RaiSE Ontology Architect
**Feature de Referencia**: `specs/001-tech-design-command`
**Objetivo**: Documentar el patrón para crear y agregar comandos al espacio `.raise-kit` de forma sistemática y consistente

## Contexto

El feature `001-tech-design-command` creó el comando `/raise.4.tech-design` siguiendo un proceso estructurado documentado en `spec.md`, `plan.md` y `tasks.md`. Este análisis extrae el patrón general para la creación de cualquier comando en `.raise-kit`.

## Evidencia Recopilada

### 1. Comandos Existentes Analizados

| Comando | Ubicación | Propósito |
|---------|-----------|-----------|
| `raise.1.discovery` | `.raise-kit/commands/02-projects/` | Transformar notas de descubrimiento en PRD |
| `raise.2.vision` | `.raise-kit/commands/02-projects/` | Generar Solution Vision desde PRD |
| `raise.4.tech-design` | `.raise-kit/commands/02-projects/` | Generar Tech Design desde Solution Vision |
| `raise.1.analyze.code` | `.raise-kit/commands/01-onboarding/` | Análisis de código brownfield usando SAR |
| `raise.rules.generate` | `.raise-kit/commands/01-onboarding/` | Generación de reglas Cursor |

### 2. Estructura Común Identificada

Todos los comandos comparten la siguiente estructura:

```markdown
---
description: [Descripción breve del comando]
handoffs:
  - label: [Etiqueta del siguiente paso]
    agent: [nombre-comando-siguiente]
    prompt: [Prompt para el siguiente comando]
    send: true
---

## User Input
$ARGUMENTS

## Outline
[Pasos numerados con estructura específica]

## Notas
[Contexto adicional y variantes]

## High-Signaling Guidelines
[Principios de ejecución]

## AI Guidance
[Guía para el agente]
```

### 3. Arquitectura de .raise-kit

**Estructura de directorios**:

```
.raise-kit/
├── commands/
│   ├── 01-onboarding/      # Comandos de preparación inicial
│   └── 02-projects/         # Comandos de flujo de proyecto
├── templates/
│   └── raise/
│       ├── solution/        # Templates de solución (PRD, Vision)
│       ├── tech/            # Templates técnicos (Tech Design)
│       └── rules/           # Templates de reglas
├── gates/
│   └── raise/
│       ├── gate-discovery.md
│       ├── gate-vision.md
│       └── gate-design.md
└── scripts/
    └── transform-commands.sh  # Script de inyección
```

**Flujo de inyección**:

1. **Desarrollo**: Artefactos se crean en `.raise-kit/`
2. **Referencias portables**: Comandos usan rutas `.specify/` (no `.raise-kit/`)
3. **Inyección**: `transform-commands.sh` copia todo a `.specify/` del proyecto target
4. **Ejecución**: Comando encuentra dependencias en `.specify/` del proyecto

### 4. Patrón de Creación Observado (Feature 001)

**Fase 1: Especificación**

1. Crear story branch con `/speckit.specify`
2. Generar `spec.md` con:
   - User Stories (priorizadas P1-P3)
   - Functional Requirements (FR-XXX)
   - Key Entities
   - Success Criteria (SC-XXX)
   - Dependencies y Assumptions

**Fase 2: Diseño**

1. Ejecutar `/speckit.plan` para generar `plan.md`
2. Pasar Constitution Check (8 principios)
3. Mapear steps del kata al outline del comando
4. Documentar decisiones arquitectónicas

**Fase 3: Implementación**

1. Ejecutar `/speckit.tasks` para generar `tasks.md`
2. Completar setup (directorios, copiar templates/gates)
3. Crear archivo del comando en `.raise-kit/commands/`
4. Escribir cada paso siguiendo estructura del kata

**Fase 4: Validación**

1. Verificar referencias usan `.specify/` (no `.raise-kit/`)
2. Comparar estructura con comandos existentes
3. Verificar handoffs en frontmatter YAML
4. Confirmar que template y gate existen

## Patrón Identificado

### Pattern Name: **RaiSE Kit Command Creation**

### Alcance

Este patrón aplica a:

- Creación de nuevos comandos en `.raise-kit/commands/`
- Adición de templates a `.raise-kit/templates/raise/`
- Creación de gates en `.raise-kit/gates/raise/`
- Documentación del proceso de creación

### Estructura del Comando

**1. Frontmatter YAML** (obligatorio):

```yaml
---
description: [Descripción concisa, 1 línea]
handoffs:
  - label: [Etiqueta visible para el usuario]
    agent: [nombre.del.comando.siguiente]
    prompt: [Texto del prompt para el siguiente comando]
    send: true
---
```

**2. User Input** (obligatorio):

```markdown
## User Input

​```text
$ARGUMENTS
​```

You **MUST** consider the user input before proceeding (if not empty).
```

**3. Outline** (obligatorio):

```markdown
## Outline

Goal: [Descripción clara del objetivo]

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`
   - Load template from `.specify/templates/[ruta]`

2. **Paso 1: [Título]**:
   - [Acciones específicas]
   - **Verificación**: [Criterio de completitud]
   - > **Si no puedes continuar**: [Condición] → [Acción Jidoka]

[... pasos siguientes ...]

N. **Finalize & Validate**:
   - Confirm file existence
   - Ejecutar gate `.specify/gates/raise/[gate].md`
   - Run `.specify/scripts/bash/update-agent-context.sh`
   - Mostrar resumen y handoff
```

**4. Notas** (opcional):

Contexto adicional para diferentes escenarios (brownfield, greenfield, etc.)

**5. High-Signaling Guidelines** (obligatorio):

```markdown
## High-Signaling Guidelines

- **Output**: [Qué archivo se genera]
- **Focus**: [En qué se enfoca el comando]
- **Language**: Instructions English; Content **SPANISH**
- **Jidoka**: [Cuándo parar y pedir ayuda]
```

**6. AI Guidance** (obligatorio):

```markdown
## AI Guidance

When executing this workflow:
1. **Role**: [Rol del agente]
2. **Be proactive**: [Qué proponer por defecto]
3. **Follow Katas**: [Qué kata seguir]
4. **Traceability**: [Cómo vincular decisiones]
5. **Gates**: [Qué validar]
```

### Convenciones Críticas

#### Referencias de Rutas

**❌ INCORRECTO**:

```markdown
- Cargar template desde `.raise-kit/templates/raise/tech/tech_design.md`
- Ejecutar gate `.raise-kit/gates/raise/gate-design.md`
```

**✅ CORRECTO**:

```markdown
- Cargar template desde `.specify/templates/raise/tech/tech_design.md`
- Ejecutar gate `.specify/gates/raise/gate-design.md`
```

**Razón**: Los comandos se ejecutan en proyectos target donde `.raise-kit/` no existe; solo existe `.specify/` después de la inyección.

#### Estructura de Pasos (Steps)

Cada paso debe tener:

1. **Título descriptivo**: `Paso N: [Verbo en infinitivo] [Objeto]`
2. **Acciones**: Lista de acciones específicas y ejecutables
3. **Verificación**: Criterio observable de completitud
4. **Jidoka block**: Condiciones de parada con acciones correctivas

**Ejemplo**:

```markdown
3. **Paso 2: Cargar Vision y Contexto**:
   - Cargar `specs/main/solution_vision.md` como input principal
   - Recopilar documentación técnica adicional
   - **Verificación**: La Solution Vision existe y el contexto está claro
   - > **Si no puedes continuar**: Solution Vision no encontrada → **JIDOKA**: Ejecutar `/raise.2.vision` primero
```

#### Handoffs

Los handoffs conectan comandos en un flujo:

```yaml
handoffs:
  - label: Create Project Backlog    # Visible para el usuario
    agent: raise.5.backlog            # Comando siguiente
    prompt: Create the project backlog from this Tech Design
    send: true                         # Auto-ofrecer al finalizar
```

### Setup Requerido

Para agregar un comando que depende de un template nuevo:

1. **Crear directorio del template** (si no existe):
   ```bash
   mkdir -p .raise-kit/templates/raise/[categoria]/
   ```

2. **Copiar template desde src** (si existe en src):
   ```bash
   cp src/templates/[categoria]/[template].md .raise-kit/templates/raise/[categoria]/
   ```

3. **Verificar gate** (si se requiere):
   ```bash
   ls -la .raise-kit/gates/raise/gate-[nombre].md
   ```

4. **Crear el comando**:
   ```bash
   touch .raise-kit/commands/[categoria]/[nombre-comando].md
   ```

5. **NO modificar `transform-commands.sh`**: El script ya copia recursivamente todo.

## Ejemplos

### Ejemplo 1: Comando Simple (Sin Template Nuevo)

**Caso**: Agregar comando `/raise.6.review` que valida un Tech Design existente.

**Setup**:

```bash
# 1. No requiere nuevo template (usa tech_design.md existente)
# 2. Puede requerir nuevo gate
touch .raise-kit/gates/raise/gate-review.md
# 3. Crear comando
touch .raise-kit/commands/02-projects/raise.6.review.md
```

**Contenido del comando**:

```markdown
---
description: Review and validate existing Tech Design against quality criteria
handoffs:
  - label: Start Implementation
    agent: speckit.6.implement
    prompt: Begin implementation of approved design
    send: true
---

## User Input
$ARGUMENTS

## Outline

Goal: Validate `specs/main/tech_design.md` against quality and completeness criteria.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`
   - Load `.specify/gates/raise/gate-review.md`

2. **Paso 1: Cargar Tech Design**:
   - Cargar `specs/main/tech_design.md`
   - **Verificación**: El archivo existe y tiene frontmatter YAML
   - > **Si no puedes continuar**: Tech Design no encontrado → **JIDOKA**: Ejecutar `/raise.4.tech-design` primero

[... más pasos ...]
```

### Ejemplo 2: Comando con Template Nuevo

**Caso**: Agregar comando `/raise.7.estimation` que genera documento de estimación.

**Setup**:

```bash
# 1. Crear directorio para template de estimación
mkdir -p .raise-kit/templates/raise/estimation/

# 2. Copiar template desde src (si existe)
cp src/templates/estimation/estimation.md .raise-kit/templates/raise/estimation/

# 3. Verificar/crear gate
touch .raise-kit/gates/raise/gate-estimation.md

# 4. Crear comando
touch .raise-kit/commands/02-projects/raise.7.estimation.md
```

**Referencias en el comando**:

```markdown
1. **Initialize Environment**:
   - Load template from `.specify/templates/raise/estimation/estimation.md`

[...]

N. **Finalize & Validate**:
   - Ejecutar gate `.specify/gates/raise/gate-estimation.md`
```

### Anti-Ejemplos

**❌ Anti-Ejemplo 1: Referencias Incorrectas**

```markdown
# MAL: Referencias a .raise-kit en lugar de .specify
- Cargar `.raise-kit/templates/raise/tech/tech_design.md`
- Ejecutar `.raise-kit/gates/raise/gate-design.md`
```

**❌ Anti-Ejemplo 2: Pasos Sin Verificación**

```markdown
# MAL: Paso sin criterio de verificación
2. **Paso 1: Cargar Contexto**:
   - Cargar documentos necesarios
```

**✅ CORRECTO**:

```markdown
2. **Paso 1: Cargar Contexto**:
   - Cargar `specs/main/project_requirements.md`
   - **Verificación**: El PRD existe y tiene sección de requisitos funcionales
   - > **Si no puedes continuar**: PRD no encontrado → **JIDOKA**: Ejecutar `/raise.1.discovery` primero
```

**❌ Anti-Ejemplo 3: Sin Handoffs**

```markdown
---
description: Generate Tech Design
# MAL: Sin handoffs, rompe la cadena de flujo
---
```

## Justificación del Patrón

### Principios RaiSE Aplicados

1. **§2. Governance as Code**: Los comandos son artefactos versionados en Git.

2. **§4. Validation Gates en Cada Fase**: Cada comando ejecuta un gate al finalizar.

3. **§7. Lean Software Development**:
   - **Jidoka**: Parar en defectos con bloques "Si no puedes continuar"
   - **Flujo**: Handoffs conectan comandos para flujo continuo
   - **Eliminación de desperdicio**: Reutilizar templates existentes

4. **§8. Observable Workflow**: Cada paso tiene verificación observable.

### Beneficios

1. **Consistencia**: Todos los comandos siguen la misma estructura
2. **Trazabilidad**: De spec → plan → tasks → comando final
3. **Portabilidad**: Referencias `.specify/` funcionan en cualquier proyecto
4. **Mantenibilidad**: Patrón claro para agregar/modificar comandos
5. **Calidad**: Gates validan cada artefacto generado

### Trade-offs

| Ventaja | Costo |
|---------|-------|
| Estructura consistente | Mayor overhead inicial (crear spec, plan, tasks) |
| Reutilización de templates | Necesidad de mantener templates sincronizados |
| Gates de calidad | Tiempo adicional en validación |
| Portabilidad con `.specify/` | Indirección en referencias (no obvio hasta entender arquitectura) |

## Decisiones Arquitectónicas

### Decisión 1: Usar `.specify/` en Referencias

**Opciones**:

- **(A)** Referencias absolutas a `.raise-kit/`
- **(B)** Referencias relativas
- **(C)** Referencias a `.specify/` ✅

**Elegida**: C - `.specify/`

**Razón**: Los comandos se ejecutan en proyectos target donde `.raise-kit/` no existe. El script `transform-commands.sh` copia todo a `.specify/`, por lo que las referencias deben apuntar ahí.

### Decisión 2: Estructura de Pasos con Verificación + Jidoka

**Opciones**:

- **(A)** Pasos simples sin verificación
- **(B)** Pasos con verificación solamente
- **(C)** Pasos con verificación + Jidoka blocks ✅

**Elegida**: C - Verificación + Jidoka

**Razón**: Implementa principio Lean de "parar en defectos". El agente sabe cuándo detener y qué acción correctiva sugerir, en lugar de continuar con datos faltantes.

### Decisión 3: Frontmatter con Handoffs

**Opciones**:

- **(A)** Sin handoffs (usuario decide siguiente paso)
- **(B)** Handoffs en texto al final
- **(C)** Handoffs en YAML frontmatter ✅

**Elegida**: C - YAML frontmatter

**Razón**: Estructurado y parseable. Permite auto-ofrecer siguiente comando al finalizar, creando flujo continuo.

## Checklist de Creación de Comandos

### Pre-requisitos

- [ ] Existe spec del feature (`spec.md`)
- [ ] Existe plan del feature (`plan.md`)
- [ ] Existe lista de tareas (`tasks.md`)
- [ ] Se identificó el kata a seguir (si aplica)

### Setup

- [ ] Directorio de templates creado si es necesario
- [ ] Template copiado desde `src/` a `.raise-kit/templates/raise/` (si aplica)
- [ ] Gate verificado/creado en `.raise-kit/gates/raise/`
- [ ] Archivo del comando creado en `.raise-kit/commands/[categoria]/`

### Estructura del Comando

- [ ] Frontmatter YAML con `description` y `handoffs`
- [ ] Sección "User Input" con `$ARGUMENTS`
- [ ] Sección "Outline" con Goal y pasos numerados
- [ ] Cada paso tiene: título, acciones, **Verificación**, Jidoka block
- [ ] Paso "Initialize Environment" carga prerequisitos
- [ ] Paso "Finalize & Validate" ejecuta gate y muestra handoff
- [ ] Sección "High-Signaling Guidelines"
- [ ] Sección "AI Guidance"

### Convenciones

- [ ] Todas las referencias usan `.specify/` (NO `.raise-kit/`)
- [ ] Template referenciado como `.specify/templates/raise/[...]`
- [ ] Gate referenciado como `.specify/gates/raise/[...]`
- [ ] Scripts referenciados como `.specify/scripts/bash/[...]`
- [ ] Content en ESPAÑOL, instructions en INGLÉS

### Validación

- [ ] Comando comparado con `raise.1.discovery` o `raise.2.vision` para consistencia
- [ ] Handoffs apuntan al siguiente comando lógico en el flujo
- [ ] Jidoka blocks indican qué comando ejecutar si falta input
- [ ] No se modificó `transform-commands.sh` (no es necesario)

## Métricas de Calidad

### Comandos Analizados

- Total comandos en `.raise-kit/commands/`: 7
- Comandos que siguen patrón completo: 3 (discovery, vision, tech-design)
- Comandos con frontmatter YAML: 7/7 (100%)
- Comandos con Jidoka blocks: 3/7 (43%)

### Cobertura del Patrón

El patrón documentado cubre:

- ✅ Estructura de directorios (100%)
- ✅ Frontmatter YAML (100%)
- ✅ Referencias portables (100%)
- ✅ Pasos con verificación (100%)
- ✅ Jidoka blocks (100% en comandos de flujo)
- ✅ Gates de validación (100%)

## Referencias

- Feature: `specs/001-tech-design-command/`
- Comandos de referencia: `.raise-kit/commands/02-projects/raise.{1,2,4}.*`
- Script de inyección: `.raise-kit/scripts/transform-commands.sh`
- Constitution RaiSE: `docs/framework/v2.1/model/00-constitution-v2.md`
- Glosario: `docs/framework/v2.1/model/20-glossary-v2.1.md`

---

**Conclusión**: Este patrón es el resultado de analizar la creación del comando `raise.4.tech-design` y comandos existentes. Provee una guía sistemática para crear nuevos comandos en `.raise-kit` manteniendo consistencia, trazabilidad y calidad.
