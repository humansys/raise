# Story Scope: RAISE-138 — Per-Session State Isolation

**Epic:** RAISE-127 pt1 (Session Instance Isolation)
**Size:** M (3 SP)
**Depends on:** RAISE-137 ✅ (Session Token Protocol)
**JIRA:** [RAISE-138](https://humansys.atlassian.net/browse/RAISE-138)

## In Scope

- Per-session directories under `.raise/rai/personal/sessions/{SES-NNN}/`
- Per-session `state.yaml` (session state isolated per instance)
- Per-session `signals.jsonl` (telemetry writes isolated per instance)
- Migration from old flat layout (`personal/session-state.yaml`) to per-session dirs
- Session directory creation on `rai session start`
- Session directory cleanup on `rai session close`
- `get_session_dir(session_id)` path helper in config/paths.py
- Shared session ledger (`sessions/index.jsonl`) with fcntl locking for concurrent access

## Out of Scope

- Agent coordination / shared context between sessions (pt2)
- Session directory garbage collection beyond close cleanup (parking lot)
- CWD validation / poka-yoke (RAISE-139)
- Changes to memory writer paths (memory remains shared, not per-session)

## Done Criteria

- [ ] `rai session start` creates `.raise/rai/personal/sessions/SES-NNN/` directory
- [ ] Session state writes go to per-session directory, not shared flat file
- [ ] Telemetry signals write to per-session `signals.jsonl`
- [ ] Two concurrent sessions produce independent state dirs
- [ ] Migration from old flat layout works without data loss
- [ ] `rai session close` cleans up session directory
- [ ] Shared session ledger uses fcntl locking
- [ ] Tests pass (>90% coverage on new code)
- [ ] Pyright, ruff, bandit pass
- [ ] Retrospective complete
