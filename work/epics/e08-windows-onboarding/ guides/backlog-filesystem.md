# Backlog con filesystem adapter

> **Vigencia:** Esta guía cubre el filesystem adapter incluido en `raise-cli`.
> Los bugs documentados aquí serán resueltos en una release futura.

---

## ¿Necesito configurar algo?

No. El filesystem adapter viene registrado automáticamente con `pip install raise-cli`.
No hay que tocar el manifest ni instalar nada extra.

Para verificar que está disponible:

```bash
rai adapter list
```

Deberías ver:

```
rai.adapters.pm (ProjectManagementAdapter)
  filesystem  raise-cli
```

Si en el futuro instalas un adapter de Jira (paquete separado), necesitarás
indicar cuál usar por defecto en `.raise/manifest.yaml`:

```yaml
backlog:
  adapter_default: filesystem
```

Por ahora, con solo `raise-cli` instalado, no hace falta.

---

## Dónde se guardan los items

Cada item es un archivo YAML en `.raise/backlog/items/`:

```
.raise/backlog/items/
├── E1.yaml   ← epic
├── E2.yaml   ← task (story)
└── E3.yaml   ← task (story)
```

Los keys se generan automáticamente de forma secuencial (`E1`, `E2`, `E3`...).
Epics y Tasks comparten la misma secuencia — no hay keys tipo `S1.1` en la
práctica por un bug conocido (ver más abajo).

---

## Flujo básico

### 1. Crear un epic

```bash
rai backlog create "Onboarding del equipo" -p MIPROYECTO -t Epic -l "epic,onboarding"
# Created: E1
```

### 2. Crear una story

Usar `-t Task` (no `-t Story`) — ver bug conocido más abajo.

```bash
rai backlog create "Configurar prerequisites Windows" -p MIPROYECTO -t Task -l "story,s1.1"
# Created: E2
```

### 3. Linkear la story al epic

```bash
rai backlog link E2 E1 child_of
# E2 → child_of → E1: linked
```

### 4. Ver un item

```bash
rai backlog get E1
```

### 5. Buscar items

```bash
rai backlog search ""                        # todos
rai backlog search "onboarding"              # por texto
rai backlog search "status = in_progress"    # por estado
```

### 6. Cambiar estado

```bash
rai backlog transition E2 in_progress
rai backlog transition E2 done
```

Estados disponibles: `pending`, `in_progress`, `done` (o cualquier string).

### 7. Agregar un comentario

```bash
rai backlog comment E2 "Verificado en Windows 11."
# E2: comment added (E2-1)
```

---

## Bugs conocidos (se resolverán en release futura)

### Bug 1: `-t Story` falla aunque se pase `--parent`

**Síntoma:**
```bash
rai backlog create "Mi story" -p PROYECTO -t Story --parent E1
# Error: 'Story creation requires parent_key'
```

**Causa:** El CLI envía `metadata["parent"]` pero el adapter busca
`metadata["parent_key"]` — mismatch de una sola letra en el código fuente.

**Workaround:** Usa `-t Task` en lugar de `-t Story`. Funciona igual,
solo que el key generado es `E{N}` en vez de `S{epic}.{N}`.

---

### Bug 2: `--parent` se ignora silenciosamente con `-t Task`

**Síntoma:**
```bash
rai backlog create "Mi story" -p PROYECTO -t Task --parent E1
# Created: E2
rai backlog get E2
# (sin campo parent)
```

**Causa:** Mismo mismatch de keys — `--parent` no llega al adapter.

**Workaround:** Linkear manualmente después de crear:
```bash
rai backlog link E2 E1 child_of
```

---

## Ejemplo completo — lo que hicimos en esta sesión

```bash
# Epic E8: Windows Team Onboarding Guide
rai backlog create "Windows Team Onboarding Guide" -p RAISE -t Epic -l "epic,onboarding,windows"
# Created: E8

# Story S8.2 (como Task, por el bug de Story type)
rai backlog create "S8.2: Backlog con filesystem adapter" -p RAISE -t Task -l "story,s8.2,onboarding"
# Created: E9

# Linkear al epic
rai backlog link E9 E8 child_of
# E9 → child_of → E8: linked

# Transicionar
rai backlog transition E9 in_progress
# E9: transitioned → in_progress
```

---

*Verificado en: Windows 11 + Python 3.13 + raise-cli 2.3.0 — 2026-03-25*
*Bugs de referencia: pendientes de fix en raise-cli*
