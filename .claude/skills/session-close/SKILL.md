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
  raise.version: "1.0.0"

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
- Conversation context (current session)
- Access to memory files (`.rai/memory/`)

**Output:**
- Updated memory files
- Session log (if significant)
- Updated context files

## Steps

### Step 1: Gather Session Summary

Review what happened in this session:
- What was the goal?
- What was accomplished?
- What decisions were made?
- What blockers were encountered?

**Verification:** Can summarize session in 2-3 sentences.

> **If you can't continue:** Session too scattered → Focus on the most significant outcome.

### Step 2: Extract Learnings

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

### Step 3: Update Memory Files

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

### Step 4: Update Context Files

Update as needed:

**CLAUDE.local.md:**
- Current Focus (if changed)
- Recent Sessions table
- Next Feature (if changed)

**RAI.md** (if applicable):
- New contributions to log
- New questions emerged
- Perspective evolved

**Verification:** Context files reflect current state.

> **If you can't continue:** Minimal changes → At least update "Next Feature" if changed.

### Step 5: Create Session Log (Optional)

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

### Step 6: Capture Tangents

Check for any ideas or tangents that came up but weren't pursued:

- Add to `dev/parking-lot.md` if worth revisiting
- Discard if not valuable

**Verification:** Parking lot updated OR no tangents to capture.

### Step 7: Suggest Next Session

Provide a brief handoff for the next session:

```markdown
## Next Session Suggestion

**Continue with:** [Most logical next step]
**Alternative:** [If blocked or priorities change]
**Open questions:** [Anything unresolved]
```

**Verification:** Clear handoff documented.

## Output

- **Patterns:** `.rai/memory/patterns.jsonl` (appended via CLI)
- **Calibration:** `.rai/memory/calibration.jsonl` (if features completed)
- **Session Index:** `.rai/memory/sessions/index.jsonl` (appended via CLI)
- **Context:** `CLAUDE.local.md` (updated manually)
- **Session Log:** `dev/sessions/YYYY-MM-DD-{topic}.md` (if significant)
- **Graph:** `.rai/memory/graph.json` (auto-rebuilt on next query)

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

- Memory files: `.rai/memory/`
- Session logs: `dev/sessions/`
- Parking lot: `dev/parking-lot.md`
- RAI perspective: `.claude/RAI.md`
