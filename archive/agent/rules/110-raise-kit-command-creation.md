---
name: RaiSE Kit Command Creation
description: Patrón para crear y agregar comandos al espacio .raise-kit siguiendo estructura estandarizada con spec, plan, tasks, y convenciones de referencias portables
globs:
  - ".raise-kit/commands/**/*.md"
  - "specs/*/spec.md"
  - "specs/*/plan.md"
  - "specs/*/tasks.md"
tags:
  - raise-kit
  - commands
  - templates
  - gates
  - governance
---

# Regla: Creación de Comandos en .raise-kit

Esta regla documenta el patrón completo para crear y agregar comandos al espacio `.raise-kit`, basado en el análisis del feature `001-tech-design-command`.

## Análisis Detallado

Para el análisis completo del patrón, consultar:

**Documento de análisis**: `specs/main/analysis/rules/analysis-for-raise-kit-command-creation.md`

## Aplicabilidad

Esta regla aplica cuando:

1. Se crea un nuevo comando en `.raise-kit/commands/`
2. Se agrega un nuevo template a `.raise-kit/templates/raise/`
3. Se crea un nuevo gate en `.raise-kit/gates/raise/`
4. Se documenta el proceso de creación de comandos

## Arquitectura de .raise-kit

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
│   └── raise/              # Gates de validación
└── scripts/
    └── transform-commands.sh  # Script de inyección a proyectos target
```

**Flujo de inyección**:

1. **Desarrollo**: Artefactos se crean en `.raise-kit/`
2. **Referencias portables**: Comandos usan rutas `.specify/` (NO `.raise-kit/`)
3. **Inyección**: `transform-commands.sh` copia todo a `.specify/` del proyecto target
4. **Ejecución**: Comando encuentra dependencias en `.specify/` del proyecto

## Proceso de Creación (4 Fases)

### Fase 1: Especificación

```bash
# Crear feature branch
/speckit.specify [descripción del comando]
```

Generar `specs/[NNN-nombre]/spec.md` con:

- **User Stories** (priorizadas P1-P3)
- **Functional Requirements** (FR-XXX)
- **Key Entities**
- **Success Criteria** (SC-XXX)
- **Dependencies** y **Assumptions**

### Fase 2: Diseño

```bash
# Generar plan de implementación
/speckit.plan
```

El `plan.md` debe incluir:

- **Constitution Check** (8 principios)
- Mapeo de steps del kata al outline del comando
- Decisiones arquitectónicas documentadas
- Contratos y data model (si aplica)

### Fase 3: Implementación

```bash
# Generar lista de tareas
/speckit.tasks
```

Completar:

1. **Setup** (crear directorios, copiar templates/gates)
2. **Crear archivo del comando** en `.raise-kit/commands/[categoria]/`
3. **Escribir cada paso** siguiendo estructura del kata
4. **Validar convenciones** (referencias, handoffs, etc.)

### Fase 4: Validación

- Verificar referencias usan `.specify/` (NO `.raise-kit/`)
- Comparar estructura con comandos existentes
- Verificar handoffs en frontmatter YAML
- Confirmar que template y gate existen

## Estructura Estándar del Comando

### 1. Frontmatter YAML (OBLIGATORIO)

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

### 2. User Input (OBLIGATORIO)

```markdown
## User Input

​```text
$ARGUMENTS
​```

You **MUST** consider the user input before proceeding (if not empty).
```

### 3. Outline (OBLIGATORIO)

```markdown
## Outline

Goal: [Descripción clara del objetivo]

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`
   - Load template from `.specify/templates/raise/[categoria]/[template].md`

2. **Paso 1: [Título en Infinitivo]**:
   - [Acción específica 1]
   - [Acción específica 2]
   - **Verificación**: [Criterio observable de completitud]
   - > **Si no puedes continuar**: [Condición] → **JIDOKA**: [Acción correctiva]

[... pasos siguientes ...]

N. **Finalize & Validate**:
   - Confirm file existence with check_file
   - Ejecutar gate `.specify/gates/raise/[gate].md`
   - Run `.specify/scripts/bash/update-agent-context.sh`
   - Mostrar resumen con ✓ y ⚠
   - Mostrar handoff: "→ Siguiente paso: `/[comando-siguiente]`"
```

### 4. Notas (OPCIONAL)

Contexto adicional para diferentes escenarios (brownfield, greenfield, spike, etc.)

### 5. High-Signaling Guidelines (OBLIGATORIO)

```markdown
## High-Signaling Guidelines

- **Output**: [Qué archivo(s) se genera(n)]
- **Focus**: [En qué se enfoca el comando]
- **Language**: Instructions English; Content **SPANISH**
- **Jidoka**: [Cuándo parar y pedir ayuda]
```

### 6. AI Guidance (OBLIGATORIO)

```markdown
## AI Guidance

When executing this workflow:
1. **Role**: [Rol del agente al ejecutar]
2. **Be proactive**: [Qué proponer por defecto]
3. **Follow Katas**: [Qué kata seguir, si aplica]
4. **Traceability**: [Cómo vincular decisiones]
5. **Gates**: [Qué validar al finalizar]
```

## Convenciones CRÍTICAS

### Referencias de Rutas

**❌ INCORRECTO**:

```markdown
- Cargar template desde `.raise-kit/templates/raise/tech/tech_design.md`
- Ejecutar gate `.raise-kit/gates/raise/gate-design.md`
- Run script `.raise-kit/scripts/bash/check-prerequisites.sh`
```

**✅ CORRECTO**:

```markdown
- Cargar template desde `.specify/templates/raise/tech/tech_design.md`
- Ejecutar gate `.specify/gates/raise/gate-design.md`
- Run script `.specify/scripts/bash/check-prerequisites.sh`
```

**Razón**: Los comandos se ejecutan en proyectos target donde `.raise-kit/` NO existe. Solo existe `.specify/` después de la inyección vía `transform-commands.sh`.

### Estructura de Pasos

Cada paso DEBE tener:

1. **Título**: `Paso N: [Verbo en infinitivo] [Objeto]`
2. **Acciones**: Lista de acciones específicas y ejecutables
3. **Verificación**: `**Verificación**: [Criterio observable]`
4. **Jidoka block**: `> **Si no puedes continuar**: [Condición] → [Acción]`

**Ejemplo Completo**:

```markdown
3. **Paso 2: Cargar Vision y Contexto**:
   - Cargar `specs/main/solution_vision.md` como input principal
   - Cargar `specs/main/project_requirements.md` como referencia
   - Recopilar documentación técnica adicional si existe
   - **Verificación**: La Solution Vision existe y el contexto técnico del proyecto está claro
   - > **Si no puedes continuar**: Solution Vision no encontrada → **JIDOKA**: Ejecutar `/raise.2.vision` primero. PRD faltante → Ejecutar `/raise.1.discovery` primero.
```

### Handoffs (Conectar Flujo)

Los handoffs conectan comandos en un flujo continuo:

```yaml
handoffs:
  - label: Create Project Backlog    # Visible para el usuario
    agent: raise.5.backlog            # Comando siguiente en el flujo
    prompt: Create the project backlog from this Tech Design
    send: true                         # Auto-ofrecer al finalizar
```

**Propósito**: Cuando el comando termina, el agente ofrece automáticamente ejecutar el siguiente paso lógico.

## Setup Requerido

Para agregar un comando que depende de un template nuevo:

```bash
# 1. Crear directorio del template (si no existe)
mkdir -p .raise-kit/templates/raise/[categoria]/

# 2. Copiar template desde src (si existe en src/)
cp src/templates/[categoria]/[template].md .raise-kit/templates/raise/[categoria]/

# 3. Verificar/crear gate (si se requiere)
touch .raise-kit/gates/raise/gate-[nombre].md

# 4. Crear el comando
touch .raise-kit/commands/[categoria]/[nombre-comando].md
```

**IMPORTANTE**: NO modificar `transform-commands.sh` - el script ya copia recursivamente todos los subdirectorios.

## Ejemplos

### Ejemplo 1: Comando Simple (Sin Template Nuevo)

**Caso**: Agregar `/raise.6.review` que valida un Tech Design existente.

```bash
# Setup mínimo (solo gate nuevo si se requiere)
touch .raise-kit/gates/raise/gate-review.md
touch .raise-kit/commands/02-projects/raise.6.review.md
```

**Comando** (fragmento):

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

Goal: Validate `specs/main/tech_design.md` against quality criteria.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`
   - Load `.specify/gates/raise/gate-review.md`

2. **Paso 1: Cargar Tech Design**:
   - Cargar `specs/main/tech_design.md`
   - **Verificación**: El archivo existe y tiene frontmatter YAML
   - > **Si no puedes continuar**: Tech Design no encontrado → **JIDOKA**: Ejecutar `/raise.4.tech-design` primero
```

### Ejemplo 2: Comando con Template Nuevo

**Caso**: Agregar `/raise.7.estimation` que genera documento de estimación.

```bash
# Setup completo
mkdir -p .raise-kit/templates/raise/estimation/
cp src/templates/estimation/estimation.md .raise-kit/templates/raise/estimation/
touch .raise-kit/gates/raise/gate-estimation.md
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

## Checklist de Validación

### Pre-requisitos

- [ ] Existe spec del feature (`specs/[NNN-nombre]/spec.md`)
- [ ] Existe plan del feature (`specs/[NNN-nombre]/plan.md`)
- [ ] Existe lista de tareas (`specs/[NNN-nombre]/tasks.md`)
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

### Validación Final

- [ ] Comando comparado con `raise.1.discovery` o `raise.2.vision` para consistencia
- [ ] Handoffs apuntan al siguiente comando lógico en el flujo
- [ ] Jidoka blocks indican qué comando ejecutar si falta input
- [ ] No se modificó `transform-commands.sh` (no es necesario)

## Anti-Patrones

### ❌ Anti-Patrón 1: Referencias Incorrectas

```markdown
# MAL: Referencias a .raise-kit en lugar de .specify
- Cargar `.raise-kit/templates/raise/tech/tech_design.md`
- Ejecutar `.raise-kit/gates/raise/gate-design.md`
```

**Por qué es malo**: Cuando el comando se ejecuta en un proyecto target, `.raise-kit/` no existe. Solo existe `.specify/` después de la inyección.

### ❌ Anti-Patrón 2: Pasos Sin Verificación

```markdown
# MAL: Paso sin criterio de verificación observable
2. **Paso 1: Cargar Contexto**:
   - Cargar documentos necesarios
```

**Corrección**:

```markdown
2. **Paso 1: Cargar Contexto**:
   - Cargar `specs/main/project_requirements.md`
   - **Verificación**: El PRD existe y tiene sección de requisitos funcionales
   - > **Si no puedes continuar**: PRD no encontrado → **JIDOKA**: Ejecutar `/raise.1.discovery` primero
```

### ❌ Anti-Patrón 3: Sin Handoffs

```markdown
---
description: Generate Tech Design
# MAL: Sin handoffs, rompe la cadena de flujo
---
```

**Por qué es malo**: El usuario debe adivinar cuál es el siguiente paso. Los handoffs conectan comandos y facilitan flujo continuo.

## Principios RaiSE Aplicados

1. **§2. Governance as Code**: Los comandos son artefactos versionados en Git.

2. **§4. Validation Gates en Cada Fase**: Cada comando ejecuta un gate al finalizar.

3. **§7. Lean Software Development**:
   - **Jidoka**: Parar en defectos con bloques "Si no puedes continuar"
   - **Flujo**: Handoffs conectan comandos para flujo continuo
   - **Eliminación de desperdicio**: Reutilizar templates existentes

4. **§8. Observable Workflow**: Cada paso tiene verificación observable.

## Referencias

- **Documento de análisis completo**: `specs/main/analysis/rules/analysis-for-raise-kit-command-creation.md`
- **Feature de referencia**: `specs/001-tech-design-command/`
- **Comandos de referencia**: `.raise-kit/commands/02-projects/raise.{1,2,4}.*`
- **Script de inyección**: `.raise-kit/scripts/transform-commands.sh`
- **Constitution RaiSE**: `docs/framework/v2.1/model/00-constitution-v2.md`
- **Glosario**: `docs/framework/v2.1/model/20-glossary-v2.1.md`

---

**Uso de esta regla**: Al crear un nuevo comando en `.raise-kit/commands/`, seguir este patrón estrictamente para mantener consistencia, trazabilidad y calidad en todo el framework RaiSE.
