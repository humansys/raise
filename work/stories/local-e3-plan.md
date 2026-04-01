# LOCAL-E3 Plan: Limpiar entorno raise-cli

**Story:** LOCAL-E3 | **Size:** S | **Date:** 2026-04-01
**Design:** `work/stories/local-e3-design.md`

## Task List

### T1: Instalar raise-cli via uv tool (S)

**Objetivo:** Crear la instalación global nueva ANTES de tocar las viejas.

**Pasos:**
1. Remover symlink `~/.local/bin/rai` (apunta a conda roto, bloquea uv tool)
2. `uv tool install raise-cli` — estable desde PyPI

**Verificación:**
- `uv tool list` muestra raise-cli
- `~/.local/bin/rai` existe y es managed by uv (no symlink)
- `rai --version` → 2.3.0

**AC:** AC1, AC2
**Deps:** ninguna

---

### T2: Verificar coexistencia con dev (XS)

**Objetivo:** Confirmar que uv run en raise-commons sigue usando el editable, no el global.

**Pasos:**
1. `cd ~/Documents/raise-commons && uv run rai --version` → 2.4.0a2
2. `rai --version` (fuera del proyecto) → 2.3.0

**Verificación:**
- Versiones distintas confirman aislamiento correcto

**AC:** AC3
**Deps:** T1

---

### T3: Eliminar conda y limpiar shell config (M)

**Objetivo:** Remover conda por completo y limpiar las referencias en shell configs.

**Pasos:**
1. Remover bloque conda init de `~/.bashrc` (líneas 124-137)
2. Remover bloque conda init de `~/.zshrc` (líneas 2-15)
3. `rm -rf ~/miniconda3`
4. Verificar que no queden referencias a conda en PATH

**Verificación:**
- `ls ~/miniconda3` → "No such file or directory"
- `grep conda ~/.bashrc ~/.zshrc` → sin resultados
- `echo $PATH | tr ':' '\n' | grep conda` → vacío (requiere nueva shell)

**AC:** AC4, AC5
**Deps:** T1, T2 (solo borrar después de verificar que todo funciona)

---

### T4: Verificación final end-to-end (XS)

**Objetivo:** Validar todos los AC en una nueva shell.

**Pasos:**
1. Abrir nueva shell (para que PATH se recargue sin conda)
2. `which rai` → `~/.local/bin/rai`
3. `rai --version` → 2.3.0
4. `cd ~/Documents/raise-commons && uv run rai --version` → 2.4.0a2
5. `which conda` → not found
7. `echo $PATH | tr ':' '\n' | grep conda` → vacío

**AC:** AC1-AC5 (todos)
**Deps:** T3

## Execution Order

```
T1 (install new) → T2 (verify coexistence) → T3 (remove conda) → T4 (final check)
```

**Rationale:** Install-first, delete-last. Cada paso tiene gate de verificación antes de avanzar al siguiente. T3 (destructivo) solo se ejecuta después de confirmar T1+T2.

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| PyPI down during T1 | Low | Retry later; conda stays until T1 passes |
| uv tool install conflicts with existing symlink | Medium | Remove symlink first in T1 |
| Shell config has more conda refs than detected | Low | grep to verify after cleanup |
| Some tool depends on conda python | Low | System python 3.12.3 exists at /usr/bin/python3 |

## Duration Tracking

| Task | Estimated | Actual | Status |
|------|-----------|--------|--------|
| T1 | 3 min | — | pending |
| T2 | 1 min | — | pending |
| T3 | 5 min | — | pending |
| T4 | 2 min | — | pending |
