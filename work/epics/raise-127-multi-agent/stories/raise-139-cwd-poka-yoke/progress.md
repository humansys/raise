# RAISE-139: CWD Poka-yoke — Project-Scoped Session Writes

**Status:** In Progress
**Size:** S (3SP)
**Branch:** epic/raise-127/multi-agent-pt1 (S-sized, skip story branch)
**Fixes:** RAISE-134

## Scope

**In:**
- Guard on `rai session close` — reject writes if CWD project != active session project
- Store project path in session-state.yaml on session start
- Clear error message with both paths on mismatch
- Unit tests for mismatch rejection

**Out:**
- Guard on other commands (session close only for now)
- Cross-project session migration
- Changes to agent namespacing (done in RAISE-138)

**Done Criteria:**
- [ ] `rai session close` rejects writes if CWD != session project
- [ ] Error message: "Session started in /path/a but CWD is /path/b"
- [ ] Project path stored in session-state.yaml
- [ ] Unit test: session close from wrong CWD fails gracefully
- [ ] pyright strict + ruff + bandit clean
- [ ] Retrospective complete
