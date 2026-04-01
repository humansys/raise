## Analysis: RAISE-813

### Root Cause (5 Whys)
1. Why wrong label? Output uses `{phase} {event}` always
2. Why phase=design? `--phase` defaults to `"design"` — nobody ever passes it
3. Why nobody passes it? All real callers (story-start/close, epic-start/close) only use `--event`
4. Why was it defaulted? Original design assumed fine-grained per-phase tracking, but callers only track lifecycle events
5. Why never caught? No test for CLI output, only for telemetry schema

### Evidence
All 6 skill callers use `rai signal emit-work {type} {id} --event {start|complete}` without --phase.

### Fix
Make `--phase` optional (default None). Output shows `{phase} {event}` only when phase is explicit, otherwise just `{event}`. Telemetry records phase as provided (None when omitted).
