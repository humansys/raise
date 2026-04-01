# RAISE-566: session-start context loss

**WHAT:**    `rai session start --context` muestra "Work: (no previous session state)" aunque la sesión anterior cerró correctamente.

**WHEN:**    Siempre que se usa `rai session close --state-file ...` (full close). El state file existe pero no se puede leer.

**WHERE:**   `src/raise_cli/cli/commands/session.py`, función `start()`, ~línea 286.

**EXPECTED:** El context bundle incluye `current_work`, `narrative`, `next_session_prompt`, y `pending` de la sesión anterior.

**ROOT CAUSE (ya confirmado en spike):**
`migrate_flat_to_session(project, SES-N)` lee `last_session.id = SES-{N-1}` del flat file y mueve
`personal/session-state.yaml → sessions/SES-{N-1}/state.yaml`.
Después, `load_session_state(project, session_id=SES-N)` busca `sessions/SES-{N}/state.yaml` — no existe → `None`.

**Done when:**
- `rai session start --context` muestra `current_work`, `narrative`, `next_session_prompt` de la sesión anterior
- Quick close (`--summary` flag) también funciona (no regresión)
- Tests del ciclo close→start pasan en verde

TRIAGE:
  Bug Type:    Functional
  Severity:    S1-High
  Origin:      Code
  Qualifier:   Incorrect
