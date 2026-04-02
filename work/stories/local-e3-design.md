# LOCAL-E3 Design: Limpiar entorno raise-cli

## Problem & Value

**Problem:** Múltiples instalaciones de raise-cli (conda rota, symlinks rotos, uv dev) causan confusión y estado impredecible.

**Value:** Entorno predecible con un solo gestor (uv). `rai` siempre funciona, siempre sabes qué versión estás ejecutando.

## Approach

Eliminar conda por completo. Usar dos mecanismos nativos de uv:

| Mecanismo | Propósito | Cómo funciona |
|-----------|-----------|---------------|
| `uv tool install raise-cli` | Global estable (2.3.0) | venv aislado en `~/.local/share/uv/tools/`, bin en `~/.local/bin/` |
| `uv run rai` en raise-commons | Dev editable (2.4.0a2) | `.venv` del proyecto, prioridad sobre PATH |

## Components Affected

| Component | Action | Risk |
|-----------|--------|------|
| `~/.local/bin/rai` | Delete symlink → recreate via uv tool | Low |
| `~/miniconda3/` | Delete entirely (~5GB) | Medium |
| `~/.bashrc` lines 124-137 | Remove conda init block | Low |
| `~/.zshrc` lines 2-15 | Remove conda init block | Low |
| `git-filter-repo` | Reinstall via `uv tool install` | Low |

## Decision: Ordering

Install before delete. Verify uv tool works BEFORE removing conda.
Rationale: if PyPI is down or uv tool install fails, conda (broken as it is) doesn't make things worse. But deleting first with no fallback is unnecessary risk.

## Examples

```bash
# After: from anywhere
$ rai --version
raise-cli version 2.3.0

$ which rai
/home/fer/.local/bin/rai

# After: from raise-commons
$ cd ~/Documents/raise-commons
$ uv run rai --version
raise-cli version 2.4.0a2

# git-filter-repo still works
$ git filter-repo --version
git-filter-repo 2.47.0
```

## Acceptance Criteria

### MUST
- AC1: `which rai` → `~/.local/bin/rai` (uv tool managed)
- AC2: `rai --version` → 2.3.0 (PyPI stable)
- AC3: `cd raise-commons && uv run rai --version` → 2.4.0a2 (dev)
- AC4: `~/miniconda3/` does not exist
- AC5: Shell configs clean (no conda blocks)
- AC6: `git filter-repo --version` works

### MUST NOT
- Delete conda before verifying uv tool install succeeds
- Modify raise-commons `.venv`
- Touch project uv config
