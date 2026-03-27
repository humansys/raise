# Workshop: Entendiendo los Skill Sets

En este workshop vas a descubrir qué son los skill sets observando el proyecto.
No memorices — explora, corre los comandos, lee los outputs.

Al final vas a poder responder: ¿qué tiene activo este proyecto? ¿cómo lo cambio? ¿cómo creo el mío?

## La skill que gestiona esto

RaiSE tiene una skill llamada `/rai-skillset-manage`. Su propósito: guiarte de forma conversacional a través de crear, inspeccionar y comparar skill sets. Internamente ejecuta los mismos comandos CLI que vas a aprender aquí.

En este workshop usamos los comandos directamente para entender qué hace cada uno. Cuando ya los domines, `/rai-skillset-manage` es el atajo para el día a día.

---

## Paso 1: ¿Qué hay en este proyecto?

```bash
PYTHONUTF8=1 rai skill set list
```

Verás algo así:

```
              Skill Sets
+--------------------------------------------+
| Name         | Skills | Path               |
|--------------+--------+--------------------|
| raise-dev    |      3 | .raise\skills\...  |
| raise-dev-ts |      3 | .raise\skills\...  |
+--------------------------------------------+
```

Hay dos sets. Son **sets de ejemplo** que se crearon para probar el sistema. No son sets de producción de ningún equipo — los veremos como material de estudio.

Ahora la pregunta importante: **¿cuál está activo?**

```bash
python -c "import json; d=json.load(open('.raise/manifests/skills.json')); print('activo:', d.get('skill_set'))"
```

Output:

```
activo: None
```

Ninguno está activo todavía. Enseguida entenderemos qué significa eso.

---

## Paso 2: ¿Qué es un skill?

Un **skill** es un archivo `SKILL.md` que le dice al agente cómo ejecutar una tarea.
El agente lee los skills desde `.claude/skills/`.

Mira uno:

```bash
cat .claude/skills/rai-story-implement/SKILL.md | head -10
```

Verás el encabezado del skill builtin — el que viene con el framework. Este es el que usa el agente cuando corres `/rai-story-implement`.

Los **builtins** vienen empaquetados dentro del CLI (`raise_cli.skills_base`). Cuando corres `rai init`, el CLI los copia a `.claude/skills/`.

---

## Paso 3: ¿Qué es un skill set?

Un **skill set** es una carpeta en `.raise/skills/<nombre>/` que contiene **overlays**.

Un **overlay** es un `SKILL.md` que **reemplaza un paso específico** del builtin. No reescribe el skill completo — solo inyecta contenido específico del proyecto en el paso que le indique.

Mira el overlay de `raise-dev` para `rai-story-implement`:

```bash
cat .raise/skills/raise-dev/rai-story-implement/SKILL.md
```

Output:

```markdown
---
name: rai-story-implement
overlay: raise-dev
replaces: Step 3 (Verify Task)
description: Python-specific verification commands for story implementation.
---

# Overlay: Verify Task (Python)

...
## Verification Commands

\`\`\`bash
uv run pytest --tb=short -x
uv run ruff check
uv run pyright
\`\`\`
```

El frontmatter de este ejemplo tiene campos descriptivos:

| Campo | Qué dice |
|-------|----------|
| `overlay` | A qué skill set pertenece |
| `replaces` | Qué paso del builtin reemplaza (referencia semántica) |
| `description` | Qué hace |

> Estos campos son una **convención** — el código no los valida ni los interpreta.
> Lo único que importa al desplegar es que exista un `SKILL.md` en la carpeta correcta.

El builtin tiene una tabla genérica que detecta el lenguaje del proyecto y elige los comandos. Este archivo la reemplaza con comandos concretos para Python. Más simple, más predecible.

### ¿Solo overlays o también skills completos?

Un skill set puede contener **ambos tipos** en el mismo set:

| Tipo | Qué es | Aparece en `diff` como |
|------|--------|------------------------|
| Overlay parcial | Reemplaza un paso del builtin | `Modified` |
| Reescritura total | Reemplaza el builtin completo | `Modified` (misma mecánica) |
| Skill nuevo | No existe en los builtins | `Added` |

El código no distingue overlay de reescritura total — ambos son simplemente un `SKILL.md` que sobreescribe el builtin. La diferencia es semántica: un overlay reemplaza un paso, una reescritura total reemplaza todo el skill.

---

## Paso 4: Estructura del sistema

```
raise_cli.skills_base/    ← builtins empaquetados con el CLI (paquete Python)
        │
        ▼  rai init
.claude/skills/           ← lo que el agente lee
        │
        ▼  rai init --skill-set mi-set   (overlays encima, overwrite=True)
.claude/skills/           ← builtin + overlay activo
        ▲
        │
.raise/skills/mi-set/     ← overlays del proyecto (en git)
```

**Punto importante:** `.claude/skills/` está trackeado en git.

Verifícalo:

```bash
git ls-files .claude/skills/ | head -5
```

Verás archivos listados — están en el repo. Esto significa que cuando alguien clona el proyecto, ya tiene los skills desplegados. Si el equipo deployó un skill set y lo commitó, el developer nuevo ya trabaja con los overlays desde el primer `git clone`. No necesita correr `rai init --skill-set` para el día a día.

---

## Paso 5: Los comandos

### `rai skill set list`

Lista todos los sets en `.raise/skills/`. No hace nada más — solo lee directorios.

```bash
PYTHONUTF8=1 rai skill set list
```

### `rai skill set diff <nombre>`

Compara cada overlay del set contra su builtin equivalente usando SHA256.

```bash
PYTHONUTF8=1 rai skill set diff raise-dev
```

Output:

```
Skill set: raise-dev

Added (1):
  + rai-bugfix

Modified (2):
  ~ rai-story-implement
  ~ rai-story-plan

Total: 3 skills (1 added, 2 modified)
```

- **Added**: el overlay agrega un skill que no existe en los builtins
- **Modified**: el overlay reemplaza un skill builtin con contenido distinto
- **Unchanged**: el overlay tiene el mismo contenido que el builtin (sin cambios reales)

### `rai skill set create <nombre>`

Crea un nuevo set copiando todos los builtins como punto de partida.

```bash
PYTHONUTF8=1 rai skill set create mi-set
```

Internamente: copia `raise_cli.skills_base` → `.raise/skills/mi-set/`.

Con `--empty` crea la carpeta vacía, sin copiar nada.

### `rai init --skill-set <nombre>` (activación)

Este es el comando que **despliega** el skill set:

1. Copia los builtins a `.claude/skills/` (igual que `rai init` normal)
2. Copia los overlays del set **encima** de los builtins (`overwrite=True`)
3. Registra en `.raise/manifests/skills.json` → `skill_set: nombre`

El resultado: el agente lee `.claude/skills/rai-story-implement/SKILL.md` y obtiene la versión del overlay, no el builtin.

---

## Paso 6: Ejercicio práctico

Corre esto paso a paso y observa cada output.

```bash
# 1. Ver qué sets existen
PYTHONUTF8=1 rai skill set list

# 2. Ver qué tiene el set raise-dev (set de ejemplo)
PYTHONUTF8=1 rai skill set diff raise-dev

# 3. Ver qué set está activo ahora
python -c "import json; d=json.load(open('.raise/manifests/skills.json')); print('activo:', d.get('skill_set'))"

# 4. Crear tu propio set (copia limpia de los builtins)
PYTHONUTF8=1 rai skill set create mi-set

# 5. Verificar que no tiene cambios respecto a los builtins
PYTHONUTF8=1 rai skill set diff mi-set
# Esperado: todos los skills aparecen como Unchanged, 0 added, 0 modified

# 6. Desplegar tu set
PYTHONUTF8=1 rai init --skill-set mi-set

# 7. Confirmar que está activo
python -c "import json; d=json.load(open('.raise/manifests/skills.json')); print('activo:', d.get('skill_set'))"
# Esperado: activo: mi-set
```

Ahora el agente usa tu set. Como es una copia limpia de los builtins, el comportamiento es idéntico — pero ya tienes el punto de partida para personalizar.

---

## Cuándo usar `rai init --skill-set`

| Situación | Qué hacer |
|-----------|-----------|
| Setup inicial del proyecto | `rai init --skill-set <nombre>` |
| Cambiar de un set a otro | `rai init --skill-set <nombre-nuevo>` |
| Actualizar tras upgrade del CLI | `rai init --skill-set <nombre>` (re-despliega con builtins nuevos) |
| Uso diario en proyecto ya configurado | Nada — `.claude/skills/` ya está en git |
| Correr `rai init` sin `--skill-set` | ⚠ Revierte a builtins, pierde los overlays activos |

---

## Cómo dar contenido a los skills del set

### Modificar un skill existente (overlay o reescritura)

Edita directamente el archivo en tu set:

```
.raise/skills/mi-set/<nombre-skill>/SKILL.md
```

Ese archivo ya existe porque `rai skill set create` copió todos los builtins. Modifica el paso que necesites, guarda, y re-despliega.

### Agregar un skill nuevo (no existe en builtins)

Usa `rai skill scaffold` con `--set` para crear la estructura:

```bash
# Crea una plantilla vacía en tu set
PYTHONUTF8=1 rai skill scaffold mi-skill-nuevo --set mi-set

# O parte del builtin desplegado como base
PYTHONUTF8=1 rai skill scaffold rai-story-implement --set mi-set --from-builtin
```

Esto crea `.raise/skills/mi-set/<nombre>/SKILL.md` con una estructura inicial. El contenido lo escribes tú editando ese archivo.

Antes de deployar, puedes validar la estructura del skill directamente en `.raise/skills/` — no necesita estar desplegado:

```bash
PYTHONUTF8=1 rai skill validate .raise/skills/mi-set/mi-skill-nuevo/
```

Cuando pase la validación, despliega:

```bash
PYTHONUTF8=1 rai init --skill-set mi-set
```

El skill nuevo aparece en `.claude/skills/` y el agente lo puede usar.

### El ciclo completo

```
1. Crear o editar SKILL.md en .raise/skills/<set>/<skill>/
2. rai skill validate .raise/skills/<set>/<skill>/   ← validar antes de deployar
3. rai init --skill-set <set>                        ← despliega a .claude/skills/
4. git add .claude/skills/                           ← comparte con el equipo
5. git commit
```

---

## Cuándo usar `rai init --skill-set`

| Situación | Qué hacer |
|-----------|-----------|
| Setup inicial del proyecto | `rai init --skill-set <nombre>` |
| Cambiar de un set a otro | `rai init --skill-set <nombre-nuevo>` |
| Actualizar tras upgrade del CLI | `rai init --skill-set <nombre>` (re-despliega con builtins nuevos) |
| Uso diario en proyecto ya configurado | Nada — `.claude/skills/` ya está en git |
| Correr `rai init` sin `--skill-set` | ⚠ Revierte a builtins, pierde los overlays activos |
