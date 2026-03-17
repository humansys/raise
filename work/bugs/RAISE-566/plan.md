# Plan: RAISE-566

## Tasks

### T1 — Regression test: close→start cycle returns state (RED)
Escribir test que verifica que `start()` con `--context` carga el state escrito por un close anterior.
El test debe fallar antes del fix.

**Verify:** `uv run pytest tests/ -k "test_session_start_loads_prior_state" -x`
**Commit:** `test(RAISE-566): regression test — start loads state from prior close [RED]`

### T2 — Fix: mover load_session_state antes de migrate_flat_to_session (GREEN)
En `start()`:
1. Cargar el flat state ANTES de que migration lo mueva
2. Pasar `prev_state` al `assemble_context_bundle` en lugar de re-cargar

**Verify:** `uv run pytest tests/ -k "test_session_start_loads_prior_state" -x`
**Commit:** `fix(RAISE-566): load session state before migration — prev state no longer lost`

### T3 — Gates completos
`uv run pytest tests/` + `uv run pyright src/raise_cli/` + `uv run ruff check src/raise_cli/`

**Commit:** (incluido en T2 si todo verde en un paso)
