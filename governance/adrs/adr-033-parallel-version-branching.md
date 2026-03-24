---
id: ADR-033
title: Parallel Version Branching Model for v2.x / v3.0 Development
status: proposed
date: 2026-03-24
decision_makers: [emilio, gerardo, eduardo]
epic: RAISE-650
---

# ADR-033: Parallel Version Branching Model

## Contexto

RaiSE enfrenta un escenario de desarrollo paralelo en tres líneas de versión:

| Versión | Naturaleza | Volumen estimado | Urgencia |
| --- | --- | --- | --- |
| **v2.3.x** | Hotfixes sobre la versión publicada | ~2-3 bugs/día | Alta (usuarios en producción) |
| **v2.4.0** | Features incrementales (5 épicas planeadas) | Semanas de trabajo | Media |
| **v3.0.0** | Knowledge Cartridges — cambio arquitectónico mayor | Meses de trabajo | Estratégica |

El modelo actual (`main` → `dev` → `story/*`) funciona para una sola línea de desarrollo.
Con tres líneas paralelas, necesitamos un modelo que permita:

1. Corregir bugs en producción (v2.3) sin arrastrar WIP de v2.4
2. Desarrollar features de v2.4 sin bloquear hotfixes
3. Trabajar en la arquitectura v3.0 sin contaminar v2.4
4. Cherry-pick de fixes entre líneas cuando aplique

## Decisión

Adoptar un modelo de **tres ramas long-lived** con release branches para hotfixes:

```
main ─────────────────────────────── (estable, tags de release)
  │
  ├── release/2.3.x ──────────────── (hotfixes sobre v2.3, vida limitada)
  │
  ├── dev ─────────────────────────── (v2.4 features, desarrollo activo)
  │     └── story/s{N}.{M}/{name}    (stories de v2.4)
  │
  └── next ────────────────────────── (v3.0, Knowledge Cartridges)
        └── story/s{N}.{M}/{name}    (stories de v3.0)
```

### Descripción de cada rama

#### `main` — La rama estable

- Contiene solo código publicado y taggeado
- Cada merge a main produce un tag de versión
- Nunca se trabaja directamente en main
- Protected branch: requiere PR/MR aprobado

#### `release/2.3.x` — Hotfixes de producción

- Se crea desde `main` cuando se necesita el primer hotfix post-release
- Solo recibe bugfixes críticos, nunca features
- Vida útil limitada: existe mientras v2.3 esté en producción
- Se elimina cuando v2.4 se publique (los usuarios migran)

**Flujo de hotfix:**
```
1. Branch desde release/2.3.x: hotfix/RAISE-NNN
2. Fix + test + commit
3. Merge a release/2.3.x
4. Tag v2.3.1 (o v2.3.2, etc.)
5. Merge release/2.3.x → main
6. Cherry-pick el fix a dev (si aplica)
7. Cherry-pick el fix a next (si aplica)
```

#### `dev` — Desarrollo v2.4

- Funciona exactamente como hoy: stories branch desde dev, merge back a dev
- Contiene todo el trabajo de las 5 épicas de v2.4
- Cuando v2.4 esté lista: merge `dev` → `main`, tag `v2.4.0`

**Flujo de feature v2.4:**
```
1. git checkout dev && git pull
2. git checkout -b story/s{N}.{M}/{name}
3. Develop + test + commit per task
4. Story close: merge --no-ff to dev
5. Epic close: push dev to origin
```

#### `next` — Desarrollo v3.0 (Knowledge Cartridges)

- Rama long-lived para cambios arquitectónicos mayores
- Se sincroniza periódicamente con `dev` para no divergir demasiado
- Stories de v3.0 branch desde `next`, merge back a `next`
- Cuando v3.0 esté lista: merge `next` → `dev` → `main`, tag `v3.0.0`

**Flujo de feature v3.0:**
```
1. git checkout next && git pull
2. git checkout -b story/s{N}.{M}/{name}
3. Develop + test + commit per task
4. Story close: merge --no-ff to next
5. Epic close: push next to origin
```

### Reglas de sincronización

| Dirección | Cuándo | Método | Quién |
| --- | --- | --- | --- |
| `release/2.3.x` → `main` | Cada hotfix release | Merge + tag | Release manager |
| `release/2.3.x` → `dev` | Después de cada hotfix | Cherry-pick | Developer del fix |
| `release/2.3.x` → `next` | Si el fix aplica a v3.0 | Cherry-pick | Developer del fix |
| `dev` → `next` | Semanal o al cerrar épica | Rebase o merge | Responsable de next |
| `dev` → `main` | Release v2.4 | Merge + tag | Release manager |
| `next` → `dev` | Nunca antes de v3.0 | — | — |
| `next` → `main` | Release v3.0 | Merge via dev + tag | Release manager |

**Regla crítica:** `next` absorbe cambios de `dev`, nunca al revés. Esto protege a v2.4 de
cambios breaking de v3.0.

### Convenciones de naming

| Elemento | Patrón | Ejemplo |
| --- | --- | --- |
| Hotfix branch | `hotfix/RAISE-{NNN}` | `hotfix/RAISE-720` |
| Story v2.4 | `story/s{N}.{M}/{name}` | `story/s12.1/new-feature` |
| Story v3.0 | `story/s{N}.{M}/{name}` | `story/s650.2/cartridge-runtime` |
| Release tag v2.3.x | `v2.3.{patch}` | `v2.3.1` |
| Release tag v2.4 | `v2.4.0` | `v2.4.0` |
| Release tag v3.0 | `v3.0.0` | `v3.0.0` |

No hay ambigüedad en las stories porque el ID de story (`s12.1` vs `s650.2`) indica la
épica, y la épica determina si va en `dev` o `next`.

## Alternativas consideradas

### A: Solo dos ramas (main + dev)

```
main ── (stable)
  └── dev (todo: hotfixes + v2.4 + v3.0)
```

**Pros:** Simple, sin overhead de sincronización.
**Contras:** Hotfixes arrastran WIP de v2.4. No se puede publicar v2.3.1 sin incluir
features incompletas. v3.0 breaking changes contaminan v2.4. **Rechazada.**

### B: Feature flags en una sola rama

Todo en `dev`, v3.0 detrás de feature flags.

**Pros:** Una sola rama, no diverge.
**Contras:** v3.0 es un cambio arquitectónico (mover módulos entre paquetes, cambiar
import paths). No es "togglable" con un flag. Los tests de v2.4 fallarían con imports
rotos aunque el flag esté off. **No aplica a nuestro caso.**

### C: Fork del repo para v3.0

Repo separado para v3.0, merge masivo al final.

**Pros:** Aislamiento total.
**Contras:** Divergencia extrema. Los fixes de v2.4 no llegan a v3.0. Al merge final,
los conflictos serían inmanejables. Duplicación de CI/CD. **Rechazada.**

### D: Git flow completo (develop + release + hotfix + feature + main)

**Pros:** Modelo probado, herramientas disponibles.
**Contras:** Demasiada ceremonia para un equipo de 5. No contempla ramas long-lived
de versión mayor. Nuestra propuesta es una simplificación de git-flow adaptada. **Parcialmente adoptada.**

## Expectativas de uso

### Para el desarrollador del día a día

**Si estás trabajando en v2.4** — nada cambia. Sigues usando `dev` exactamente igual.

**Si estás arreglando un bug de producción:**
1. `git checkout release/2.3.x`
2. Crea branch `hotfix/RAISE-NNN`
3. Fix, test, merge a `release/2.3.x`
4. Avisa para el cherry-pick a `dev` y `next`

**Si estás trabajando en v3.0 (Knowledge Cartridges):**
1. `git checkout next`
2. Trabaja igual que en `dev` — mismo flujo de stories
3. Periódicamente: `git rebase dev` o merge para no divergir

### Para el release manager

**Hotfix release (v2.3.x):**
```bash
git checkout release/2.3.x
git merge hotfix/RAISE-NNN --no-ff
git tag v2.3.1
git checkout main && git merge release/2.3.x
git push origin main release/2.3.x --tags
# Cherry-pick a dev y next si aplica
```

**Minor release (v2.4.0):**
```bash
git checkout main && git merge dev --no-ff
git tag v2.4.0
git push origin main --tags
# Eliminar release/2.3.x (ya no se mantiene)
# Rebase next sobre nuevo main
```

**Major release (v3.0.0):**
```bash
git checkout dev && git merge next --no-ff
# Resolver conflictos, run full test suite
git checkout main && git merge dev --no-ff
git tag v3.0.0
git push origin main --tags
# Eliminar next
```

### Frecuencia de sincronización esperada

| Actividad | Frecuencia |
| --- | --- |
| Hotfixes v2.3 | Diario (2-3 bugs/día según estimación) |
| Cherry-pick hotfix → dev | Mismo día del fix |
| Cherry-pick hotfix → next | Mismo día si aplica |
| Sync dev → next (rebase/merge) | Semanal o al cerrar épica en dev |
| Release v2.3.x | Según acumulación (cada 3-5 fixes) |
| Release v2.4 | Al completar épicas planeadas |
| Release v3.0 | Cuando Knowledge Cartridges esté listo |

## Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
| --- | --- | --- | --- |
| `next` diverge demasiado de `dev` | Alta | Alto | Sync semanal obligatorio. CI en next debe pasar |
| Conflictos en cherry-pick de hotfixes | Media | Bajo | Hotfixes son pequeños y focalizados |
| Alguien commitea en la rama equivocada | Baja | Medio | CI valida que stories de E650 van en next, otras en dev |
| `next` rebase rompe historia compartida | Media | Alto | Preferir merge sobre rebase si otros ya pullearon next |
| Se olvida cherry-pick de hotfix | Media | Medio | Checklist en el PR template de hotfix |

## Cuándo se retira este modelo

Este modelo es temporal — existe mientras haya desarrollo paralelo de v2.x y v3.0.

- Cuando v2.4 se libere y v2.3 deje de mantenerse → eliminar `release/2.3.x`
- Cuando v3.0 se libere → eliminar `next`, volver al modelo simple (main + dev + story)
- Si se necesita v3.1 con breaking changes → crear nuevo `next` siguiendo el mismo patrón

## Prerrequisitos para adoptar

1. [ ] Crear rama `next` desde `dev` actual
2. [ ] Crear rama `release/2.3.x` desde tag `v2.3.0` en `main`
3. [ ] Configurar protección de ramas en GitLab (main, dev, next: no push directo)
4. [ ] Actualizar `.raise/manifest.yaml` con la nueva configuración de branches
5. [ ] Actualizar CI/CD para correr en `dev`, `next`, y `release/*`
6. [ ] Comunicar al equipo el nuevo flujo

## Referencias

- Modelo actual: `CLAUDE.md` § Branch Model
- Git flow original: Vincent Driessen (2010)
- Trunk-based development: trunkbaseddevelopment.com
- Contexto: E650 (Knowledge Cartridges) requiere aislamiento de v2.4 work
