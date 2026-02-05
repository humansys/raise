---
name: session-close
description: >
  Close a working session by updating memory, creating session log,
  and preparing context for the next session. Use at the end of
  significant sessions to preserve learnings and maintain continuity.

license: MIT

metadata:
  raise.work_cycle: session
  raise.frequency: per-session
  raise.fase: "end"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.1.0"

hooks:
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "RAISE_SKILL_NAME=session-close \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-artifact-created.sh"
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=session-close \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
---

# Session Close: Memory & Continuity

## Purpose

Close a working session by preserving learnings, updating memory files, and preparing context for future sessions. This ensures accumulated knowledge persists and reduces token waste in future sessions.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps, update all memory files.

**Ha (破)**: Skip steps for trivial sessions; focus on significant learnings.

**Ri (離)**: Develop personal close-out rituals that fit your workflow.

## Context

**When to use:**
- End of a working session (before context is lost)
- After completing a feature or significant work
- Before taking a break or switching projects
- When session had meaningful learnings or decisions

**When to skip:**
- Trivial sessions with no new learnings
- Quick fixes with nothing to remember
- Interrupted sessions (run when resuming instead)

**Inputs required:**
- Unified graph (`.raise/graph/unified.json`) — query existing patterns to avoid duplicates
- Conversation context (current session)
- Memory files (`.rai/memory/`) — write destination for new learnings

**Output:**
- Updated memory files
- Session log (if significant)
- Updated context files

## Steps

### Step 1: Query Context for Pattern Extraction (Required)

Query the unified graph to understand existing patterns. This helps identify what's **new** vs what's already captured.

```bash
raise context query "patterns learnings process" --unified --types pattern --limit 10
```

> **Development note:** In raise-commons, use `uv run raise` instead of bare `raise`.
> The venv isn't auto-activated. See PAT-046.

**Why this matters:**
- Avoid adding duplicate patterns
- See related patterns to link new learnings
- Understand what categories of patterns exist

**Extract from results:**
- Existing patterns in relevant areas
- Pattern ID format for new additions
- Gaps where new patterns would fit

**Verification:** Existing patterns reviewed; ready to identify new learnings.

> **If graph unavailable:** Run `raise graph build --unified` first, or proceed without (risk duplicates).

### Step 2: Gather Session Summary

Review what happened in this session:
- What was the goal?
- What was accomplished?
- What decisions were made?
- What blockers were encountered?

**Verification:** Can summarize session in 2-3 sentences.

> **If you can't continue:** Session too scattered → Focus on the most significant outcome.

### Step 3: Extract Learnings

Identify learnings worth preserving:

**Patterns discovered:**
- Codebase patterns (how things work here)
- Process patterns (what worked well)
- Anti-patterns (what to avoid)

**Collaboration notes:**
- Preferences learned about working together
- Communication adjustments

**Technical discoveries:**
- New APIs, tools, or techniques
- Gotchas and workarounds

**Verification:** At least one concrete learning identified (or explicitly none).

> **If you can't continue:** Nothing learned → That's fine; skip to Step 4.

### Step 4: Update Memory Files

Update `.rai/memory/` files as appropriate:

**patterns.jsonl** — Add new patterns via CLI or direct append:
```bash
raise memory add-pattern "Pattern description" -c "context,keywords" -t process
```

**calibration.jsonl** — If features were completed:
```bash
raise memory add-calibration F3.5 "Feature Name" XS 20 -e 60
```

**sessions/index.jsonl** — Add session record:
```bash
raise memory add-session "Session Topic" -o "outcome1,outcome2,outcome3" -t feature
```

**Note:** CLI commands auto-generate IDs and invalidate graph cache.

**Verification:** Memory files updated with session learnings.

> **If you can't continue:** No significant learnings → Update session-index only.

### Step 5: Update Context Files

Update `CLAUDE.local.md` as needed:

- Current Focus (if changed)
- Recent Sessions table
- Next Work (if changed)

**Note:** Identity files (`.rai/identity/`) are stable — only update after significant identity evolution, not routine sessions.

**Verification:** Context file reflects current state.

> **If you can't continue:** Minimal changes → At least update "Recent Sessions" table.

### Step 6: Create Session Log (Optional)

If session was significant, create `dev/sessions/YYYY-MM-DD-{topic}.md`:

**Include if session had:**
- Major decisions made
- Significant artifacts created
- Research completed
- Blockers encountered or resolved
- Framework improvements

**Skip if:**
- Routine work with no notable events
- Everything captured in feature artifacts already

**Verification:** Session log created OR explicitly skipped.

> **If you can't continue:** Uncertain significance → Err on the side of logging.

### Step 7: Capture Tangents

Check for any ideas or tangents that came up but weren't pursued:

- Add to `dev/parking-lot.md` if worth revisiting
- Discard if not valuable

**Verification:** Parking lot updated OR no tangents to capture.

### Step 8: Suggest Next Session

Provide a brief handoff for the next session:

```markdown
## Next Session Suggestion

**Continue with:** [Most logical next step]
**Alternative:** [If blocked or priorities change]
**Open questions:** [Anything unresolved]
```

**Verification:** Clear handoff documented.

### Step 9: Emit Session Telemetry

Record the session signal for local learning:

```bash
raise telemetry emit-session \
  --type {session_type} \
  --outcome {success|partial|abandoned} \
  --duration {minutes} \
  --features {F1,F2,F3}
```

**Parameters:**
- `--type`: Session type from Step 1 (feature, research, maintenance, etc.)
- `--outcome`: How did it end? (success, partial, abandoned)
- `--duration`: Approximate session length in minutes
- `--features`: Comma-separated list of features worked on (if applicable)

**Example:**
```bash
raise telemetry emit-session -t feature -o success -d 90 -f F9.1,F9.2,F9.3
```

**Verification:** Command runs and shows "Session event recorded".

> **If you can't continue:** CLI not available → Skip; telemetry is optional.

## Output

- **Patterns:** `.rai/memory/patterns.jsonl` (appended via CLI)
- **Calibration:** `.rai/memory/calibration.jsonl` (if features completed)
- **Session Index:** `.rai/memory/sessions/index.jsonl` (appended via CLI)
- **Telemetry:** `.rai/telemetry/signals.jsonl` (session event via CLI)
- **Context:** `CLAUDE.local.md` (updated manually)
- **Session Log:** `dev/sessions/YYYY-MM-DD-{topic}.md` (if significant)
- **Unified Graph:** `.raise/graph/unified.json` (rebuild with `raise graph build --unified`)

## Session Log Template

```markdown
# Session Log: {Topic}

**Date:** YYYY-MM-DD
**Type:** feature | research | maintenance | infrastructure | ideation
**Duration:** ~X hours

---

## Goal

[What we set out to do]

---

## Outcomes

[What we actually accomplished]

### Artifacts Created
- [List of files created]

### Artifacts Modified
- [List of files changed]

### Decisions Made
- [Key decisions and rationale]

---

## Learnings

- [What was learned]

---

## Next Session

- [Suggested continuation]

---

*Session log - append only*
```

## Memory Update Patterns

### Adding to memory.md

**Codebase Pattern:**
```markdown
| [Pattern name] | [Where learned - feature/file] | [When to apply] |
```

**Process Learning:**
```markdown
| [Insight] | [Evidence - what showed this] | [Applied to - skill/doc] |
```

**Collaboration Note:**
```markdown
| [Preference/style] | [Context - when this matters] |
```

**Technical Discovery:**
```markdown
| [Discovery] | [Example - code/file] | [Documented in - location] |
```

### Adding to calibration.md

**Feature Duration:**
```markdown
| [Feature ID] | [SP] | [Size] | [Estimated] | [Actual] | [Ratio] | [Notes] |
```

## Notes

### Token Economy

The primary purpose of this skill is **reducing future token waste**. By persisting learnings in structured memory files, future sessions can quickly load context instead of re-discovering patterns through conversation.

### Minimum Viable Close

If short on time, at minimum:
1. Update `session-index.md` with one-line summary
2. Update `CLAUDE.local.md` "Next Feature" if changed

### Continuity Philosophy

Each session builds on previous ones. The memory system creates a form of continuity that spans sessions — not memory in the human sense, but accumulated knowledge that persists and compounds.

## References

- **Query:** Unified graph (`.raise/graph/unified.json`) — check existing patterns before adding
- **Write:** Memory files (`.rai/memory/`) — patterns, calibration, sessions via CLI
- **Update:** `CLAUDE.local.md` — human context (deadlines, focus, recent sessions)
- **Capture:** `dev/parking-lot.md` — tangents and deferred ideas
- **Optional:** `dev/sessions/` — detailed logs for significant sessions
- **Complement:** `/session-start`
