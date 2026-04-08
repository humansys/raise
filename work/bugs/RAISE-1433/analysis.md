# RAISE-1433: Analysis

## Root Cause — 5 Whys

**Why** does session close produce hollow records?
→ Because `rai session close --summary "..."` builds a CloseInput with only
  summary + type, everything else defaults to empty.

**Why** are narrative/next_session_prompt empty?
→ Because CloseInput defaults them to "" and the CLI --summary path never
  populates them. Only the --state-file path can.

**Why** doesn't the CLI warn about empty semantic fields?
→ Because there's no validation gate. The code treats any structured close
  (summary!=None) as valid without checking semantic completeness.

**Why** are journal entries lost?
→ Because `process_session_close()` never reads journal entries. They live in
  `personal/sessions/{id}/journal.jsonl` but close doesn't know they exist.
  Then `cleanup_session_dir()` (line 735) deletes the session directory,
  destroying the journal.

**Why** was this not caught earlier?
→ Because the /rai-session-close skill uses --state-file which CAN include
  all fields. The --summary path was a convenience shortcut that nobody
  validated end-to-end.

## Method
5 Whys — single causal chain with 3 independent symptoms.

## Evidence
- `session.py:626-629`: CloseInput from --summary has only 2 of 12 fields
- `close.py:72-73`: narrative="" and next_session_prompt="" as defaults
- `session.py:734-738`: cleanup_session_dir deletes journal before it's read
- `close.py:150-291`: process_session_close never imports or reads journal
- Incident SES-023: KonectaParkAhuehuete 2026-04-07 — confirmed hollow record

## 3 Independent Symptoms

### Symptom 1: Empty narrative + next_session_prompt on --summary close
The --summary path provides no way to pass these fields. They default to "".

### Symptom 2: Journal entries never included in close output
`process_session_close()` has no code path that reads `journal.jsonl`.
The journal is a write-only artifact during the session.

### Symptom 3: Journal destroyed on session cleanup
`cleanup_session_dir()` deletes the per-session directory, which contains
`journal.jsonl`. Even if we wanted to read it later, it's gone.

## Key Finding: Journal is Dead Infrastructure

Deep research revealed the journal (`rai session journal add/show`) is scaffolding
without load-bearing purpose:
- No skill writes to it automatically
- Post-compaction hook injection is broken (CC bugs #12671, #15174)
- Recovery is entirely manual
- Comprehensive infra (schema, CLI, tests) supporting an aspirational design

**Decision: Deprecate journal. Fix the real bug (hollow --summary close).**

## Fix Approaches

### A (simplest): CLI warning on empty semantic fields
Print warning when narrative/next_session_prompt are empty. No data fix.
Trade-off: tells you about the problem but doesn't fix it.

### B (selected): Deprecate journal + warn on hollow close
1. Deprecate journal CLI commands + skill + hook
2. Add CLI warning when --summary close produces hollow record
3. Guide user toward --state-file or /rai-session-close skill
Trade-off: removes dead infra, makes the gap visible.

### C (future): Replace journal with better continuity mechanism
Design a new continuity mechanism that doesn't depend on broken CC hooks.
Deferred — "veremos como implementamos eso despues."

## Recommendation
**B** — deprecate dead infra, warn on hollow close. Future mechanism TBD.
