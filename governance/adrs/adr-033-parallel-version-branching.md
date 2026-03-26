---
id: ADR-033
title: Release Branch Model for Parallel Version Development
status: accepted
date: 2026-03-24
updated: 2026-03-25
decision_makers: [emilio, gerardo, eduardo]
epic: RAISE-650
supersedes: CLAUDE.md § Branch Model (dev-based)
---

# ADR-033: Release Branch Model

## Contexto

RaiSE enfrenta un escenario de desarrollo paralelo en tres líneas de versión:

| Versión | Naturaleza | Volumen estimado | Urgencia |
| --- | --- | --- | --- |
| **v2.3.x** | Hotfixes sobre la versión publicada | ~2-3 bugs/día | Alta (usuarios en producción) |
| **v2.4.0** | Features incrementales (5 épicas planeadas) | Semanas de trabajo | Media |
| **v3.0.0** | Knowledge Cartridges — cambio arquitectónico mayor | Meses de trabajo | Estratégica |

El modelo anterior (`main` → `dev` → `story/*`) funciona para una sola línea de desarrollo,
pero `dev` y `next` son en realidad release branches disfrazadas — el nombre genérico oculta
la intención y crea ambigüedad al rotar versiones.

Con tres líneas paralelas, necesitamos un modelo que:

1. Corrija bugs en producción (v2.3) sin arrastrar WIP de v2.4
2. Desarrolle features de v2.4 sin bloquear hotfixes
3. Trabaje en la arquitectura v3.0 sin contaminar v2.4
4. Cherry-pick de fixes entre líneas cuando aplique
5. **Nombre = intención** — cada rama dice explícitamente qué versión contiene

## Decisión

Adoptar **release branches explícitas** — cada rama long-lived lleva el nombre de su versión target:

```
main ─────────────────────────────── (estable, tags de release)
  │
  ├── release/2.3.x ──────────────── (hotfixes sobre v2.3, vida limitada)
  │
  ├── release/2.4.0 ──────────────── (features v2.4, desarrollo activo)
  │     └── story/s{N}.{M}/{name}    (stories de v2.4)
  │
  └── release/3.0.0 ──────────────── (v3.0, Knowledge Cartridges)
        └── story/s{N}.{M}/{name}    (stories de v3.0)
```

**Principio:** el nombre de la rama es su versión target. Sin alias genéricos.

### Descripción de cada rama

#### `main` — La rama estable

- Contiene solo código publicado y taggeado
- Cada merge a main produce un tag de versión
- Nunca se trabaja directamente en main
- Protected branch: requiere PR/MR aprobado

#### `release/2.3.x` — Hotfixes de producción

- Se crea desde `main` (o tag `v2.3.0`) cuando se necesita el primer hotfix
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
6. Cherry-pick el fix a release/2.4.0 (si aplica)
7. Cherry-pick el fix a release/3.0.0 (si aplica)
```

#### `release/2.4.0` — Features v2.4 (antes `dev`)

- Stories branch desde release/2.4.0, merge back a release/2.4.0
- Contiene todo el trabajo de las épicas de v2.4
- Cuando v2.4 esté lista: merge `release/2.4.0` → `main`, tag `v2.4.0`
- Después del release, se elimina. Si hay v2.5: se crea `release/2.5.0` desde main

**Flujo de feature v2.4:**
```
1. git checkout release/2.4.0 && git pull
2. git checkout -b story/s{N}.{M}/{name}
3. Develop + test + commit per task
4. Story close: merge --no-ff to release/2.4.0
5. Epic close: push release/2.4.0 to origin
```

#### `release/3.0.0` — v3.0 Knowledge Cartridges (antes `next`)

- Rama long-lived para cambios arquitectónicos mayores
- Se sincroniza periódicamente con `release/2.4.0` para no divergir
- Stories de v3.0 branch desde `release/3.0.0`, merge back
- Cuando v3.0 esté lista: merge `release/3.0.0` → `main`, tag `v3.0.0`

**Flujo de feature v3.0:**
```
1. git checkout release/3.0.0 && git pull
2. git checkout -b story/s{N}.{M}/{name}
3. Develop + test + commit per task
4. Story close: merge --no-ff to release/3.0.0
5. Epic close: push release/3.0.0 to origin
```

### Reglas de sincronización

| Dirección | Cuándo | Método | Quién |
| --- | --- | --- | --- |
| `release/2.3.x` → `main` | Cada hotfix release | Merge + tag | Release manager |
| `release/2.3.x` → `release/2.4.0` | Después de cada hotfix | Cherry-pick | Developer del fix |
| `release/2.3.x` → `release/3.0.0` | Si el fix aplica a v3.0 | Cherry-pick | Developer del fix |
| `release/2.4.0` → `release/3.0.0` | Semanal o al cerrar épica | Merge | Responsable de 3.0 |
| `release/2.4.0` → `main` | Release v2.4 | Merge + tag | Release manager |
| `release/3.0.0` → `release/2.4.0` | Nunca | — | — |
| `release/3.0.0` → `main` | Release v3.0 | Merge + tag | Release manager |

**Regla crítica:** `release/3.0.0` absorbe cambios de `release/2.4.0`, nunca al revés.
Esto protege a v2.4 de cambios breaking de v3.0.

### Convenciones de naming

| Elemento | Patrón | Ejemplo |
| --- | --- | --- |
| Release branch (patch) | `release/{major}.{minor}.x` | `release/2.3.x` |
| Release branch (minor/major) | `release/{major}.{minor}.0` | `release/2.4.0`, `release/3.0.0` |
| Hotfix branch | `hotfix/RAISE-{NNN}` | `hotfix/RAISE-720` |
| Story branch | `story/s{N}.{M}/{name}` | `story/s12.1/new-feature` |
| Release tag | `v{major}.{minor}.{patch}` | `v2.3.1`, `v2.4.0`, `v3.0.0` |

El ID de story (`s12.1` vs `s650.2`) indica la épica, y la épica determina la release branch.

## Alternativas consideradas

### A: Solo dos ramas (main + dev)

**Rechazada.** Hotfixes arrastran WIP de v2.4. No se puede publicar v2.3.1 sin features incompletas.

### B: Feature flags en una sola rama

**No aplica.** v3.0 es cambio arquitectónico (mover módulos, cambiar imports). No es togglable.

### C: Fork del repo para v3.0

**Rechazada.** Divergencia extrema, conflictos inmanejables al merge final.

### D: Git flow completo

**Parcialmente adoptada.** Demasiada ceremonia para equipo de 5. Nuestro modelo es una simplificación.

### E: Named integration branches (dev + next) — MODELO ANTERIOR

```
main → dev (v2.4) → next (v3.0)
```

**Rechazada (2026-03-25).** `dev` y `next` son release branches con nombres genéricos. Esto oculta
la intención, crea ambigüedad al rotar versiones (¿dev pasa a ser v2.5?), y causó un MR !39
con conflictos innecesarios porque v2.3.0 se taggeó en main mientras dev ya tenía contenido
de v2.4. Release branches explícitas eliminan la ambigüedad.

## Expectativas de uso

### Para el desarrollador del día a día

**Si estás trabajando en v2.4:**
1. `git checkout release/2.4.0 && git pull`
2. Crea story branch, trabaja, merge back a `release/2.4.0`

**Si estás arreglando un bug de producción:**
1. `git checkout release/2.3.x`
2. Crea branch `hotfix/RAISE-NNN`
3. Fix, test, merge a `release/2.3.x`
4. Cherry-pick a `release/2.4.0` y `release/3.0.0` si aplica

**Si estás trabajando en v3.0 (Knowledge Cartridges):**
1. `git checkout release/3.0.0`
2. Mismo flujo de stories que en release/2.4.0
3. Periódicamente: merge de release/2.4.0 para no divergir

### Para el release manager

**Hotfix release (v2.3.x):**
```bash
git checkout release/2.3.x
git merge hotfix/RAISE-NNN --no-ff
git tag v2.3.1
git checkout main && git merge release/2.3.x
git push origin main release/2.3.x --tags
# Cherry-pick a release/2.4.0 y release/3.0.0 si aplica
```

**Minor release (v2.4.0):**
```bash
git checkout main && git merge release/2.4.0 --no-ff
git tag v2.4.0
git push origin main --tags
git branch -d release/2.4.0  # eliminar rama
# Eliminar release/2.3.x (ya no se mantiene)
# Si hay v2.5: git checkout -b release/2.5.0 main
```

**Major release (v3.0.0):**
```bash
git checkout main && git merge release/3.0.0 --no-ff
# Resolver conflictos, run full test suite
git tag v3.0.0
git push origin main --tags
git branch -d release/3.0.0  # eliminar rama
```

### Frecuencia de sincronización esperada

| Actividad | Frecuencia |
| --- | --- |
| Hotfixes v2.3 | Diario (2-3 bugs/día según estimación) |
| Cherry-pick hotfix → release/2.4.0 | Mismo día del fix |
| Cherry-pick hotfix → release/3.0.0 | Mismo día si aplica |
| Sync release/2.4.0 → release/3.0.0 | Semanal o al cerrar épica |
| Release v2.3.x | Según acumulación (cada 3-5 fixes) |
| Release v2.4 | Al completar épicas planeadas |
| Release v3.0 | Cuando Knowledge Cartridges esté listo |

## Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
| --- | --- | --- | --- |
| `release/3.0.0` diverge de `release/2.4.0` | Alta | Alto | Sync semanal obligatorio. CI debe pasar |
| Conflictos en cherry-pick de hotfixes | Media | Bajo | Hotfixes son pequeños y focalizados |
| Alguien commitea en la rama equivocada | Baja | Medio | CI valida epic → release branch mapping |
| Merge rompe historia compartida | Media | Alto | Preferir merge sobre rebase si otros ya pullearon |
| Se olvida cherry-pick de hotfix | Media | Medio | Checklist en el MR template de hotfix |

## Cuándo se retira este modelo

El modelo de release branches es permanente. Las ramas individuales son temporales:

- Cuando v2.4 se libere → eliminar `release/2.4.0` y `release/2.3.x`
- Cuando v3.0 se libere → eliminar `release/3.0.0`
- Nuevas versiones → crear `release/{version}` desde main
- Si solo hay una línea activa → modelo se reduce a main + release/X.Y.0 + story/*

## Migración desde modelo anterior

1. [ ] Renombrar `dev` → `release/2.4.0` (o crear desde dev y archivar dev)
2. [ ] Crear `release/2.3.x` desde tag `v2.3.0` en `main`
3. [ ] Crear `release/3.0.0` desde `release/2.4.0` cuando se inicie E650
4. [ ] Cerrar MR !39 (dev→main) — su contenido vive en release/2.4.0
5. [ ] Actualizar `.raise/manifest.yaml` con nueva configuración de branches
6. [ ] Actualizar CI/CD para correr en `release/*`
7. [ ] Configurar protección de ramas en GitLab
8. [ ] Comunicar al equipo el nuevo flujo
9. [ ] Actualizar CLAUDE.md § Branch Model

## Referencias

- Modelo anterior: `CLAUDE.md` § Branch Model (dev-based, superseded)
- Política de versioning: TN-002 — Branching & Versioning Strategy
- Git flow original: Vincent Driessen (2010)
- Precedentes: Node.js, Python, Kubernetes usan release branches explícitas
- Contexto: E650 (Knowledge Cartridges) + MR !39 conflicts evidenciaron la necesidad
