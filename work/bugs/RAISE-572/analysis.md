# RAISE-572 Analysis

## Root Cause (XS — causa evidente)

La instrucción en SKILL.md L80 dice:
> "resolve from `.raise/manifest.yaml` first, then language defaults"

Pero no especifica qué forma usar para el comando resuelto. El AI infiere "verificación por archivo modificado" como comportamiento natural — es lo que haría un dev humano revisando sólo lo que tocó. El resultado: `pyright src/rai_agent/daemon/connection.py` en lugar de `uv run pyright`.

El `pyproject.toml` ya tiene `include = ["src/", "tests/"]`, por lo que el comando global cubre todo. Usar paths específicos bypasea esa configuración y deja `tests/` sin verificar.

**Root cause:** La skill no prohíbe explícitamente paths específicos ni explica por qué el scope global es obligatorio.

## Fix Approach

Agregar una regla explícita en Step 2:
- Usar siempre el comando global del manifest (`type_check_command`, `lint_command`, `test_command`)
- Prohibir paths específicos como argumento al type checker / linter
- Explicar el motivo: el pyproject.toml ya define el scope correcto

Cambiar en dos lugares:
1. `src/raise_cli/skills_base/rai-story-plan/SKILL.md` (source — distribuido via rai init)
2. `.claude/skills/rai-story-plan/SKILL.md` (copia local activa)
