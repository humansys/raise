# RAISE-1433: rai session close skips journal and next_session_prompt

## WHAT
`rai session close --summary "..."` persists a structurally valid but semantically
hollow session record: empty narrative, empty next_session_prompt, zero journal entries.
The next session starts with no continuity context.

## WHERE
Two independent failure points:

### 1. CLI structured close with --summary only (no --state-file)
`session.py:626-629` — builds CloseInput with only summary + type:
```python
close_input = CloseInput(
    summary=summary or "",
    session_type=session_type or "feature",
)
```
narrative, next_session_prompt, outcomes, patterns all default to empty.

### 2. CloseInput accepts empty semantic fields without validation
`close.py:72-73` — narrative and next_session_prompt default to "":
```python
narrative: str = ""
next_session_prompt: str = ""
```
No validation gate between receiving a summary and a complete session record.

### 3. Journal entries are never included in close
Journal entries (`rai session journal add`) are written to per-session JSONL.
But `process_session_close()` never reads them. They are orphaned when the
session directory is cleaned up at close.

## WHEN
Every `rai session close --summary "..."` without --state-file.
Also when /rai-session-close skill generates a state file but omits fields.

## Reproduces
Yes — every direct CLI close produces hollow records.

## Impact
- Next session starts with no continuity context
- Journal entries accumulated during session are lost
- narrative/next_session_prompt (the most valuable continuity fields) always empty
- Session index has summary but no depth

TRIAGE: Functional / S2-Medium / Design / Missing
