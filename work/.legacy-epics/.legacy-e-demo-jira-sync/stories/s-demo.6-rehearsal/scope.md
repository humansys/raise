# Story Scope: S-DEMO.6 — Demo Rehearsal & Retrospective

**Epic:** E-DEMO (JIRA Sync Enabler)
**Branch:** demo/atlassian-webinar (epic branch, no story branch for XS)
**Size:** XS (1 SP)
**Created:** 2026-02-15
**Deadline:** 2026-02-16 10:00 AM (1 hour before demo)

---

## In Scope

1. **End-to-end workflow rehearsal** (minimum 3 successful runs)
   - JIRA epic creation → pull → local design → push stories → status sync
   - Validate all CLI commands work (`rai backlog pull/push/status`)
   - Verify JIRA project state (epic + stories visible, correctly linked)

2. **Demo script creation** (tailored to Coppel context)
   - Introduction: Governance scalability problem statement (1 min)
   - Workflow demonstration: 6-step process (10 min)
   - Value articulation: Governance without 1:1 coaching (2 min)
   - Q&A preparation: Anticipated objections/questions

3. **JIRA cleanup & fresh sync**
   - Delete test data from rehearsals
   - Create clean epic for demo ("Product Governance Initiative")
   - Verify sync state clean (`.raise/rai/sync/state.json` reset)

4. **Backup plan documentation**
   - Screenshots of successful workflow
   - Recorded screen demo (if live fails)
   - Manual fallback procedure

5. **Epic retrospective**
   - Learnings from 42-hour sprint
   - Framework validation insights
   - Patterns captured
   - Improvements identified

---

## Out of Scope

- Live JIRA webhook integration (V3 scope)
- Rovo AI integration (V3 scope)
- Confluence sync (future epic)
- Automated demo testing (rehearsal is manual)
- Demo slides/deck creation (script only)

---

## Done Criteria

- [ ] Workflow rehearsed 3+ times end-to-end without errors
- [ ] Demo script written (15-min format, Coppel-contextualized)
- [ ] JIRA project cleaned (test data removed)
- [ ] Fresh epic created for demo ("Product Governance Initiative")
- [ ] Sync state reset (clean `.raise/rai/sync/state.json`)
- [ ] Backup plan documented (screenshots + recorded demo)
- [ ] Epic retrospective complete (learnings captured)
- [ ] All tests passing (regression check)
- [ ] Pyright strict clean

---

## Dependencies

- **Requires:** S-DEMO.5 complete (sync engine functional)
- **Blocks:** Demo delivery (2026-02-16 11:00 AM)

---

## Timeline (4 hours budgeted, Monday 06:00-10:00)

| Time | Task | Duration |
|------|------|----------|
| 06:00-07:00 | Rehearsal 1 + debug issues | 1h |
| 07:00-07:45 | Rehearsal 2 + script refinement | 45min |
| 07:45-08:15 | Rehearsal 3 + timing validation | 30min |
| 08:15-09:00 | JIRA cleanup + fresh sync setup | 45min |
| 09:00-09:30 | Backup plan (screenshots/recording) | 30min |
| 09:30-10:00 | Epic retrospective | 30min |
| **10:00** | **DEMO READY** | — |
| 11:00 | **DEMO START** (Coppel) | — |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Live demo fails (network/auth) | Recorded demo + screenshots ready |
| JIRA API rate limit | Dry-run mode for rehearsals |
| Timing overrun | 15-min script enforced, Q&A flexible |
| Missing context | Script includes Coppel problem statement |

---

**Next:** Create rehearsal plan, execute first run.
