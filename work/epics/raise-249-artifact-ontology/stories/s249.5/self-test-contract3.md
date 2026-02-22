# Self-Test: Contract 3 — User Story Artifact

> Validates that the story.md template from Step 5.5 is consumable by story-design v1.2.

## Sample Artifact

Below is a hypothetical story.md for a fictional story "S99.1" — an M-sized story.

---

```markdown
---
story_id: "S99.1"
title: "Add session duration tracking"
epic_ref: "RAISE-99"
size: "M"
status: "draft"
created: "2026-02-21"
---

# Story: Add session duration tracking

## User Story
As a developer using RaiSE,
I want session start and close to record timestamps,
so that I can measure actual session duration for calibration.

## Acceptance Criteria

### Scenario: Session records start timestamp
```gherkin
Given a developer starts a session with rai session start
When the session is created
Then the session record includes an ISO timestamp for start_time
```

### Scenario: Session records end timestamp and calculates duration
```gherkin
Given a session is active with a recorded start_time
When the developer runs rai session close
Then the session record includes an ISO timestamp for end_time
And the duration is calculated as end_time - start_time
And the duration is displayed in human-readable format
```

### Scenario: Duration survives interruption
```gherkin
Given a session was started but not closed
When the developer starts a new session
Then the orphaned session is flagged with estimated duration from last activity
```

## Examples (Specification by Example)

| Input | Action | Expected Output |
|-------|--------|----------------|
| `rai session start` at 14:00 | Start session | `start_time: "2026-02-21T14:00:00"` in session record |
| `rai session close` at 15:30 | Close session | `end_time: "2026-02-21T15:30:00"`, `duration: "1h 30m"` |
| Session started, never closed | New session start | Warning: "Stale session SES-099 (~2h estimated)" |

## Notes
- References epic design.md § Session Tracking Component
- ISO 8601 timestamps for cross-timezone compatibility
- Duration calculation uses wall clock time, not working hours
```

---

## Consumption Verification

### story-design v1.2 Step 2 (What & Why)
- **Consumes:** § User Story → "As a developer... I want timestamps... so that calibration"
- **Result:** Problem = no timestamps, Value = calibration accuracy. ✅ Clear framing.

### story-design v1.2 Step 5 (Acceptance Criteria)
- **Consumes:** § Acceptance Criteria → 3 Gherkin scenarios
- **Result:** Step 5 says "See: story.md § Acceptance Criteria" — references, not duplicates. ✅ No duplication.

### story-plan (Task derivation)
- **Consumes:** § Examples (SbE) → 3 concrete input/output pairs
- **Result:** Each SbE row can become a test case in an SDLD blueprint. ✅ Testable.

### story-plan (Traceability)
- **Consumes:** § Acceptance Criteria scenario titles
- **Result:** Traceability table can map "Session records start timestamp" → Task 1. ✅ Traceable.

## Verdict

Contract 3 artifact is **consumable** by story-design v1.2 and story-plan v1.1. All four consumption points verified:
1. Connextra → What & Why ✅
2. Gherkin → AC reference ✅
3. SbE → Test cases ✅
4. Scenario titles → Traceability ✅
