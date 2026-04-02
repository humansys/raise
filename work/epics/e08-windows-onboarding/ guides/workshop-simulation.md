---
id: S8.5
epic: E8
title: Workshop Skillset Simulation — Guía del Instructor
status: complete
---

# Workshop: Personalización de Skill Sets con RaiSE

## Introducción

Este workshop guía al equipo a través del flujo completo de personalización de skill sets en RaiSE. Al finalizar, el equipo tendrá su primer skill set en el repositorio y activo en Claude Code.

**Duración estimada:** 90 minutos
**Audiencia:** Equipo de desarrollo que ya conoce RaiSE y quiere adaptar sus skills al contexto del proyecto
**Prerrequisito conceptual:** Haber leído la guía `skill-sets.md` (S8.3) o tener experiencia previa usando RaiSE

**Lo que logra el equipo al final:**
- Un skill set `mi-equipo` creado con 3 tipos de personalización demostrados
- El skill set activo en `.claude/skills/` del proyecto
- Criterio propio para decidir cuándo y cómo personalizar cada skill

---

## Prerrequisitos Técnicos (Windows)

Verificar antes del workshop:

```
[ ] raise-cli instalado: rai --version → raise-cli version 2.x.x
[ ] uv disponible: uv --version → uv 0.x.x
[ ] Variable de entorno: PYTHONUTF8=1 configurada (o prefijada en cada comando)
[ ] Claude Code instalado y funcionando
```

**Nota sobre PYTHONUTF8=1:** En Windows, algunos comandos `rai` producen errores de encoding sin esta variable. Prefijamos todos los comandos del workshop con `PYTHONUTF8=1 rai` para evitar problemas.

Para configurarla permanentemente en la sesión:

```powershell
$env:PYTHONUTF8 = "1"
```

---

## Etapa 1: Setup del Proyecto de Prueba

> **Nota del instructor:** Esta etapa simula lo que haría el equipo en un proyecto real nuevo. El proyecto de prueba vive fuera del repositorio principal para no contaminar el repo con artefactos del workshop.

### Pasos

**1.1 Crear el directorio del proyecto de prueba:**

```bash
mkdir C:\Users\tu-usuario\Documents\workshop-test
cd C:\Users\tu-usuario\Documents\workshop-test
```

**1.2 Inicializar el proyecto con RaiSE:**

```bash
PYTHONUTF8=1 rai init --name workshop-test
```

Output real obtenido:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Welcome to RaiSE!                                                           │
│                                                                             │
│ I'm Rai — your AI partner for reliable software engineering.                │
│                                                                             │
│ Together, we'll build software that's both fast AND reliable.               │
│   • You bring intuition and judgment                                        │
│   • I bring execution and memory                                            │
│   • Together: reliable software at AI speed                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Project detected: Greenfield (0 code files)
Created: .raise/manifest.yaml  — project metadata
Loaded:  ~/.rai/developer.yaml  — your preferences
Created: .raise/rai/identity/  — Rai's base identity
Created: .raise/rai/memory/  — 55 base patterns
Created: .raise/rai/framework/  — methodology definition
Created: .claude/skills/  — 27 onboarding skills
Created: governance/  — 7 governance templates
```

**1.3 Copiar los skills no-builtins:**

```bash
cp -r path\a\raise-commons\.claude\skills\rai-skillset-manage .claude\skills\
cp -r path\a\raise-commons\.claude\skills\rai-skill-create .claude\skills\
```

> **Nota del instructor — Por qué este paso es necesario:** `rai-skillset-manage` y `rai-skill-create` todavía no forman parte del paquete `raise_cli.skills_base`. Viven en `.claude/skills/` de raise-commons como skills de proyecto. Cuando se inicializa un proyecto nuevo con `rai init`, solo se copian los builtins del paquete — estos dos no están incluidos. Hasta que sean promovidos a builtins, cualquier proyecto que los necesite debe copiarlos manualmente. La guía documenta esto explícitamente para que el instructor y los participantes entiendan el porqué y no lo confundan con un bug.

**1.4 Verificar que los skills están disponibles:**

```bash
PYTHONUTF8=1 rai skill list
```

Output real obtenido (35 skills encontrados, incluyendo):

```
Skills (35 found)

Session
rai-session-close  4.1.0  Close a working session by reflecting on outcomes...
rai-session-start  5.0.0  Begin a session by loading context bundle...

...

Meta
rai-framework-sync   1.0.0  Sync framework files across locations...
rai-publish          1.0.0  Guide the human through a structured release...
rai-skill-create     3.0.0  Guided skill creation through conversation...
rai-skillset-manage  1.0.0  Guided skill set management through conversation...
```

`rai-skill-create` y `rai-skillset-manage` aparecen en la sección Meta.

---

### Preguntas para el equipo — Etapa 1

| # | Pregunta | Objetivo |
|---|----------|----------|
| 1 | ¿Cuántos skills vienen por defecto con RaiSE? ¿Los conocen todos? | Inventario mental |
| 2 | ¿En qué proyectos de su equipo usarían RaiSE? ¿Greenfield o brownfield? | Contexto de aplicación |

---

## Etapa 2: Descubrimiento

> **Nota del instructor:** Esta etapa es breve pero importante — establece el estado inicial antes de crear el skill set.

**2.1 ¿Qué skill sets existen?**

```bash
PYTHONUTF8=1 rai skill set list
```

Output esperado en proyecto recién iniciado:

```
No skill sets found in .raise/skills/
```

**2.2 ¿Qué skills están disponibles?**

Ya lo vimos en la Etapa 1. El punto clave: **27 skills builtin** más los 2 copiados manualmente.

---

### Preguntas para el equipo — Etapa 2

| # | Pregunta | Objetivo |
|---|----------|----------|
| 1 | ¿Cuál de los 27 skills builtins usarían más frecuentemente en su proyecto? | Identificar los más relevantes |
| 2 | ¿Qué información siempre les falta cuando arrancan una historia? | Detectar gaps a cubrir con personalización |

---

## Etapa 3: Crear el Skill Set Base

> **Nota del instructor:** El comando `rai skill set create` copia todos los builtins como punto de partida. Es la decisión correcta para un primer workshop — los participantes pueden ver qué tienen y decidir qué modificar. La alternativa `--empty` crea una carpeta vacía, útil para equipos avanzados.

```bash
PYTHONUTF8=1 rai skill set create mi-equipo
```

Output real obtenido:

```
✓ Skill set 'mi-equipo' created at
C:\Users\tu-usuario\Documents\workshop-test\.raise\skills\mi-equipo
  27 skills copied from builtins

  Next: customize skills, then deploy with:
  rai init --skill-set mi-equipo
```

**Verificar que es copia limpia:**

```bash
PYTHONUTF8=1 rai skill set diff mi-equipo
```

Output real obtenido:

```
Skill set: mi-equipo

Unchanged (27):
  = rai-debug
  = rai-discover
  = rai-docs-update
  = rai-doctor
  = rai-epic-close
  = rai-epic-design
  = rai-epic-docs
  = rai-epic-plan
  = rai-epic-run
  = rai-epic-start
  = rai-mcp-add
  = rai-mcp-remove
  = rai-mcp-status
  = rai-problem-shape
  = rai-project-create
  = rai-project-onboard
  = rai-research
  = rai-session-close
  = rai-session-start
  = rai-story-close
  = rai-story-design
  = rai-story-implement
  = rai-story-plan
  = rai-story-review
  = rai-story-run
  = rai-story-start
  = rai-welcome

Total: 27 skills (0 added, 0 modified)
```

0 cambios — es una copia exacta de los builtins.

---

### Preguntas para el equipo — Etapa 3

| # | Pregunta | Objetivo |
|---|----------|----------|
| 1 | ¿Qué significa que un skill sea "Modified" vs "Added" en el diff? | Conceptualizar el sistema |
| 2 | ¿Qué comandos de verificación usa su equipo? ¿Difieren de los builtins? | Preparar la personalización |
| 3 | Si renombraran su skill set, ¿qué nombre le darían? | Ownership del artefacto |

---

## Etapa 4a: Overlay Parcial — Modificar un Paso

> **Nota del instructor:** Este es el tipo de personalización más quirúrgico — se modifica solo una sección de un skill, manteniendo el resto intacto. Es ideal para adaptar comandos de verificación, thresholds, o convenciones del equipo sin reescribir toda la lógica.

**Objetivo:** Reemplazar el Step 3 (Verify Task) de `rai-story-implement` con los comandos reales del equipo.

**Abrir el archivo a editar:**

```
.raise\skills\mi-equipo\rai-story-implement\SKILL.md
```

**ANTES (Step 3 original — tabla genérica multi-lenguaje):**

```markdown
### Step 3: Verify Task

Run the verification defined in the plan. Resolve commands using this priority chain:

1. **Check `.raise/manifest.yaml`** for `project.test_command`, ...
2. **Detect language** from `project.project_type` in manifest, or scan file extensions
3. **Map language to default:**

| Language | Test       | Lint                      | Format                         | Type Check    |
|----------|------------|---------------------------|--------------------------------|---------------|
| Python   | `uv run pytest --tb=short` | `uv run ruff check src/ tests/` | `uv run ruff format --check` | `uv run pyright` |
| TypeScript | `npx vitest run` | `npx eslint src/` | ...                        | `npx tsc --noEmit` |
| ...      |            |                           |                                |               |

The manifest always wins when present. The table is a fallback.
```

**DESPUÉS (Step 3 personalizado para mi-equipo):**

```markdown
### Step 3: Verify Task (mi-equipo)

Este equipo trabaja exclusivamente en Python con uv. Ejecutar los tres gates
obligatorios en este orden:

```bash
# 1. Tests con reporte de fallo inmediato
uv run pytest --tb=short -x

# 2. Linting
uv run ruff check src/ tests/

# 3. Type checking
uv run pyright
```

Los tres deben pasar antes de continuar. Si alguno falla: corregir y re-ejecutar
(máximo 3 intentos antes de escalar al humano).
```

**Verificar el cambio:**

```bash
PYTHONUTF8=1 rai skill set diff mi-equipo
```

Output real obtenido:

```
Skill set: mi-equipo

Modified (1):
  ~ rai-story-implement
Unchanged (26):
  = rai-debug
  = rai-discover
  ...

Total: 27 skills (0 added, 1 modified)
```

El diff muestra `Modified (1): rai-story-implement` — exactamente lo esperado.

---

### Preguntas para el equipo — Etapa 4a

| # | Pregunta | Objetivo |
|---|----------|----------|
| 1 | ¿Qué otros pasos de `rai-story-implement` querrían personalizar? | Identificar más overlays potenciales |
| 2 | ¿Cómo diseñarían el review de código en su equipo? ¿Qué checklists tienen hoy? | Preparar Etapa 4b |

---

## Etapa 4b: Reescritura Total — Reemplazar un Skill Completo

> **Nota del instructor:** La reescritura total reemplaza el SKILL.md completo con una versión adaptada al equipo. Es útil cuando el flujo del builtin no se corresponde con cómo trabaja el equipo — por ejemplo, si usan una metodología de planning diferente.

**Objetivo:** Reemplazar `rai-story-plan` con una versión simplificada adaptada al ritmo del equipo.

**Abrir el archivo:**

```
.raise\skills\mi-equipo\rai-story-plan\SKILL.md
```

**Reemplazar TODO el contenido con la versión simplificada del equipo:**

```markdown
---
name: rai-story-plan
overlay: mi-equipo
replaces: full-skill
description: >
  Planificación simplificada para mi-equipo — descomposición directa de tareas
  sin andamiaje TDD. Adaptado al ritmo y convenciones del equipo.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "5"
  raise.prerequisites: story-design
  raise.next: story-implement
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: team
---

# Plan (mi-equipo)

## Purpose

Descomponer la historia en tareas atómicas listas para ejecutar, estimadas y
secuenciadas por riesgo.

## Steps

### 1. Listar tareas

Nombrar cada tarea como un entregable concreto: **verbo + sustantivo**.

Ejemplos correctos:
- "Implementar endpoint POST /usuarios"
- "Agregar validación de email duplicado"
- "Escribir tests de integración para AuthService"

### 2. Estimar

Usar tallas: **XS / S / M / L**

Si una tarea es L, partirla en dos antes de continuar.

### 3. Secuenciar

Ordenar por dependencias y riesgo. Regla: **las tareas más riesgosas van primero**.

### 4. Verificar criterio de listo

Cada tarea debe tener un criterio de "done" observable:
- Tests pasan (`uv run pytest --tb=short -x`)
- Sin errores de lint (`uv run ruff check src/ tests/`)
- Sin errores de tipos (`uv run pyright`)

## Output

Archivo `plan.md` con la lista de tareas en formato tabla:
ID | Tarea | Talla | Criterio de listo.

## References

- Anterior: `/rai-story-design`
- Siguiente: `/rai-story-implement`
```

**Verificar los cambios:**

```bash
PYTHONUTF8=1 rai skill set diff mi-equipo
```

Output real obtenido:

```
Skill set: mi-equipo

Modified (2):
  ~ rai-story-implement
  ~ rai-story-plan
Unchanged (25):
  ...

Total: 27 skills (0 added, 2 modified)
```

Ahora tenemos `Modified (2)` — los dos skills personalizados.

---

### Preguntas para el equipo — Etapa 4b

| # | Pregunta | Objetivo |
|---|----------|----------|
| 1 | ¿Cuándo optarían por una reescritura total vs un overlay parcial? | Criterio de decisión |
| 2 | ¿Qué otro skill del equipo merece una reescritura? ¿El de design? ¿El de review? | Backlog de personalización |

---

## Etapa 4c: Skill Nuevo — Agregar lo que No Existe

> **Nota del instructor:** El tercer tipo es el más poderoso — agregar skills que el framework no tiene. Cada equipo tiene procesos únicos: deploy, onboarding, hotfix, runbook de incidentes. Con `rai skill scaffold` se crea la estructura, se edita el contenido, y se valida antes de deployar.

**Objetivo:** Crear `rai-deploy` — el proceso de deploy del equipo — que no existe en los builtins.

**3.1 Crear la estructura del skill:**

```bash
PYTHONUTF8=1 rai skill scaffold rai-deploy --set mi-equipo
```

Output real obtenido:

```
✓ Created skill at:
C:\Users\tu-usuario\Documents\workshop-test\.raise\skills\mi-equipo\rai-deploy\SKILL.md

Next steps:
  1. Edit the SKILL.md to add description and steps
  2. Run raise skill validate to check structure
  3. Test the skill with Claude Code
```

**3.2 Editar el SKILL.md con el proceso de deploy:**

Abrir `.raise\skills\mi-equipo\rai-deploy\SKILL.md` y reemplazar el contenido scaffoldeado con:

```markdown
---
name: rai-deploy
description: >
  Guía de deploy para mi-equipo. Verifica gates locales y ejecuta el deploy
  al ambiente de staging antes de mergear a main.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: per-story
  raise.fase: "8"
  raise.prerequisites: story-review
  raise.next: ""
  raise.gate: gate-code
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: team
---

# Deploy (mi-equipo)

## Purpose

Verificar gates locales y ejecutar el deploy al ambiente de staging. No se
mergea a main sin smoke test aprobado.

## Steps

### Paso 1: Verificar gates locales

```bash
uv run pytest --tb=short -x
uv run ruff check src/ tests/
uv run pyright
```

Los tres deben pasar. Si alguno falla: corregir antes de continuar.

### Paso 2: Deploy a staging

```bash
git push origin HEAD
# El pipeline de CI/CD se activa automáticamente
```

Verificar en el pipeline que el build pase.

### Paso 3: Smoke test en staging

1. Endpoint de health: `GET /health` → 200 OK
2. Flujo principal del feature deployado: al menos un happy path
3. Sin errores 5xx en logs durante 5 minutos post-deploy

Si el smoke test falla: rollback con `git revert HEAD`.

## Output

| Item | Destino |
|------|---------|
| PR aprobado y mergeado | `main` |
| Deploy confirmado | ambiente staging |

## References

- Anterior: `/rai-story-review`
- Gates: `gates/gate-code.md`
```

**3.3 Validar la estructura del skill:**

```bash
PYTHONUTF8=1 rai skill validate .raise/skills/mi-equipo/rai-deploy/
```

Output real obtenido:

```
Validating: .raise\skills\mi-equipo\rai-deploy\SKILL.md
{CHECK} All checks passed

All 1 skill(s) valid
```

> **Nota del instructor — Requisito de headers en inglés:** El validador requiere que las secciones principales del SKILL.md tengan nombres en inglés: `## Purpose`, `## Steps`, `## References`. El contenido dentro de esas secciones puede estar en el idioma que prefiera el equipo. Si el validate falla con "Missing required section: Purpose", revisar que los headers sean exactamente `## Purpose`, `## Steps`, `## References`.

**3.4 Verificar el diff final:**

```bash
PYTHONUTF8=1 rai skill set diff mi-equipo
```

Output real obtenido:

```
Skill set: mi-equipo

Added (1):
  + rai-deploy
Modified (2):
  ~ rai-story-implement
  ~ rai-story-plan
Unchanged (25):
  = rai-debug
  = rai-discover
  = rai-docs-update
  = rai-doctor
  = rai-epic-close
  = rai-epic-design
  = rai-epic-docs
  = rai-epic-plan
  = rai-epic-run
  = rai-epic-start
  = rai-mcp-add
  = rai-mcp-remove
  = rai-mcp-status
  = rai-problem-shape
  = rai-project-create
  = rai-project-onboard
  = rai-research
  = rai-session-close
  = rai-session-start
  = rai-story-close
  = rai-story-design
  = rai-story-review
  = rai-story-run
  = rai-story-start
  = rai-welcome

Total: 28 skills (1 added, 2 modified)
```

El estado final del skill set: `Added (1): rai-deploy`, `Modified (2): rai-story-implement, rai-story-plan`.

---

### Preguntas para el equipo — Etapa 4c

| # | Pregunta | Objetivo |
|---|----------|----------|
| 1 | ¿Qué gates necesita verificar el equipo antes de deployar? ¿Son distintos por proyecto? | Contexto real |
| 2 | Además de deploy, ¿qué otros skills nuevos crearía el equipo? ¿Hotfix? ¿Runbook? | Backlog de skills |
| 3 | ¿Cómo documentarían los criterios de rollback del equipo? | Ownership del proceso |

---

## Etapa 5: Deploy y Verificación

> **Nota del instructor:** `rai init --skill-set mi-equipo` activa el skill set: copia las versiones personalizadas a `.claude/skills/` y registra el set activo en `.raise/manifests/skills.json`. Claude Code lee `.claude/skills/` al iniciar — por eso el deploy es el mecanismo de activación.

**5.1 Activar el skill set:**

```bash
PYTHONUTF8=1 rai init --skill-set mi-equipo
```

Output real obtenido:

```
Project detected: Greenfield (0 code files)
Created: .raise/manifest.yaml  — project metadata
Loaded:  ~/.rai/developer.yaml  — your preferences
Loaded:  .raise/rai/  — Rai base already present
Loaded:  .claude/skills/  — skills already present
Loaded:  governance/  — governance templates already present
```

> **Nota:** La salida no menciona explícitamente el skill set por nombre, pero el registro ocurre internamente. La verificación en el paso siguiente lo confirma.

**5.2 Confirmar que el skill set está activo:**

```bash
python -c "import json; d=json.load(open('.raise/manifests/skills.json')); print('activo:', d.get('skill_set'))"
```

Output real obtenido:

```
activo: mi-equipo
```

**5.3 Confirmar que los skills personalizados están activos:**

```bash
PYTHONUTF8=1 rai skill list
```

Output real (fragmento relevante):

```
Skills (30 found)

Story
rai-story-implement  2.2.0  Execute the implementation plan task by task...
rai-story-plan       1.0.0  Planificación simplificada para mi-equipo — des...

Utility
rai-deploy  1.0.0  Guía de deploy para mi-equipo. Verifica gates l...
```

Evidencia de activación:
- `rai-story-plan` muestra versión `1.0.0` con descripción en español (la versión del equipo, no la builtin)
- `rai-deploy` aparece con la descripción del equipo (no existía en los builtins)
- Total: 30 skills (27 builtins + rai-skill-create + rai-skillset-manage + rai-deploy del equipo)

---

### Preguntas para el equipo — Etapa 5

| # | Pregunta | Objetivo |
|---|----------|----------|
| 1 | ¿Dónde vive el skill set en el repositorio? ¿Cómo lo commitean? | Git workflow |
| 2 | Si un miembro nuevo del equipo clona el repo, ¿qué debe hacer para activar el skill set? | Onboarding |
| 3 | ¿Cómo versionarían los cambios al skill set? ¿Un PR por skill? ¿Batch? | Governance del skill set |

---

## Resumen del Workshop

Al finalizar el workshop, el equipo tiene:

| Artefacto | Path | Estado |
|-----------|------|--------|
| Skill set base | `.raise/skills/mi-equipo/` | 27 builtins copiados |
| Overlay parcial | `.raise/skills/mi-equipo/rai-story-implement/SKILL.md` | Step 3 personalizado |
| Reescritura total | `.raise/skills/mi-equipo/rai-story-plan/SKILL.md` | Versión simplificada del equipo |
| Skill nuevo | `.raise/skills/mi-equipo/rai-deploy/SKILL.md` | Proceso de deploy del equipo |
| Set activo | `.raise/manifests/skills.json` | `"skill_set": "mi-equipo"` |

**Próximo paso recomendado:** Commitear `.raise/skills/mi-equipo/` al repositorio del proyecto para que todos los miembros del equipo puedan activar el mismo skill set.

---

## Notas del Instructor

### Preparación previa al workshop

1. Verificar que `raise-cli` está instalado en la máquina de demostración: `rai --version`
2. Confirmar que `rai-skillset-manage` y `rai-skill-create` están en `.claude/skills/` de raise-commons
3. Tener listos los contenidos de edición (Etapas 4a, 4b, 4c) — copiar-pegar es más eficiente que tipear en vivo
4. Limpiar cualquier `workshop-test` previo: `rmdir /s /q C:\...\workshop-test`

### Preguntas frecuentes

**"¿Por qué copiamos los skills manualmente? ¿No deberían venir solos?"**
Sí, eventualmente. `rai-skillset-manage` y `rai-skill-create` están en camino a ser builtins. Por ahora, el copy manual es un paso transitorio documentado en el design (D1 de S8.5).

**"¿El diff compara contenido o metadata?"**
Solo SHA256 del contenido del SKILL.md. Cualquier cambio en el archivo — un carácter, un comentario — lo marca como Modified.

**"¿Puedo tener múltiples skill sets?"**
Sí. Cada skill set vive en `.raise/skills/<nombre>/`. `rai init --skill-set <nombre>` activa uno por vez. Para cambiar, volver a correr `rai init --skill-set otro-nombre`.

**"¿Qué pasa si borro un skill del skill set?"**
El diff lo mostrará como eliminado. Al deployar con `rai init --skill-set`, ese skill se elimina de `.claude/skills/` y Claude Code ya no lo tendrá disponible.

**"¿Los headers del SKILL.md tienen que estar en inglés?"**
Las secciones principales sí: `## Purpose`, `## Steps`, `## References`. El contenido dentro de cada sección puede estar en cualquier idioma.

### Timing sugerido

| Etapa | Tiempo |
|-------|--------|
| Intro + Prerrequisitos | 5 min |
| Etapa 1: Setup | 10 min |
| Etapa 2: Descubrimiento | 5 min |
| Etapa 3: Skill set base | 10 min |
| Etapa 4a: Overlay parcial | 15 min |
| Etapa 4b: Reescritura total | 15 min |
| Etapa 4c: Skill nuevo | 15 min |
| Etapa 5: Deploy y verificación | 10 min |
| Preguntas finales + cierre | 5 min |

---

## Acceptance Criteria Cubiertos

| AC | Descripción | Cubierto |
|----|-------------|---------|
| MUST 1 | `workshop-simulation.md` cubre setup → descubrimiento → creación → 3 tipos → deploy → verificación | Sí — Etapas 1-5 |
| MUST 2 | Cada comando incluye su output esperado | Sí — outputs reales en cada etapa |
| MUST 3 | El paso de copiar skills no-builtins documenta la razón explícita | Sí — Etapa 1.3, Nota del instructor |
| MUST 4 | Los 3 tipos demostrados: overlay parcial, reescritura total, skill nuevo | Sí — Etapas 4a, 4b, 4c |
| MUST 5 | La guía termina con verificación de `skills.json` | Sí — Etapa 5.2 con output real |
| SHOULD 1 | Sección "Preguntas por etapa" | Sí — tabla al final de cada etapa |
| SHOULD 2 | Notas de instructor diferenciadas | Sí — bloques `> Nota del instructor` + sección final |
