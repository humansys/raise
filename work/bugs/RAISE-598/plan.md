## Plan: RAISE-598

### Tasks

**T1 — Baseline GREEN**
Verificar que tests existentes pasan antes de tocar código.
```
uv run pytest tests/doctor/test_cli.py -v
```
Commit: ninguno (verificación)

**T2 — Extraer `_render_json_output`**
Mover L87-105 a función privada. `doctor()` la llama con `_render_json_output(results, passes, warns, errors)`.
```
uv run pytest tests/doctor/test_cli.py -v
uv run ruff check src/raise_cli/cli/commands/doctor.py
uv run pyright src/raise_cli/cli/commands/doctor.py
```
Commit: `refactor(RAISE-598): extract _render_json_output from doctor callback`

**T3 — Extraer `_render_human_output`**
Mover L106-131 a función privada. `doctor()` la llama con `_render_human_output(results, passes, warns, errors, verbose)`.
```
uv run pytest tests/doctor/test_cli.py -v
uv run ruff check src/raise_cli/cli/commands/doctor.py
uv run pyright src/raise_cli/cli/commands/doctor.py
```
Commit: `refactor(RAISE-598): extract _render_human_output from doctor callback`

**T4 — Extraer `_apply_fixes`**
Mover L133-144 a función privada. `doctor()` la llama con `_apply_fixes(results)`.
```
uv run pytest tests/doctor/test_cli.py -v
uv run ruff check src/raise_cli/cli/commands/doctor.py
uv run pyright src/raise_cli/cli/commands/doctor.py
```
Commit: `refactor(RAISE-598): extract _apply_fixes from doctor callback`

**T5 — Gates completos**
```
uv run pytest --tb=short
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/
uv run pyright
```
Verificar complexity estimada ≤ 15.
