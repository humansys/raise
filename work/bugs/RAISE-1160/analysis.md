# Analysis: RAISE-1160

## 5 Whys (Size: S — single causal chain)

Problem: Two session records with different IDs written on every close

Why 1: process_session_close() generates its own SES-NNN via append_session()
Why 2: The new session index (S-F-*) was added in the CLI command layer, not the orchestrator
Why 3: append_session() was the original recording mechanism; the new index was additive, not a replacement
Why 4: No refactor removed the legacy write when the new system was introduced
Root cause: **Incomplete migration** — new session index added alongside legacy, never replaced it

## Fix Approach

In `process_session_close()`:
- When `session_id` is provided by caller: use it as `result.session_id`, skip `append_session()`
- Legacy path (no session_id): keep append_session() for backward compat
- session-state.yaml LastSession.id inherits the correct ID transitively

No changes needed in session.py CLI — it already passes session_id and prefers S-F-* for final_session_id.
