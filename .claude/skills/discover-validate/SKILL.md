---
name: discover-validate
description: >
  Present synthesized component descriptions to human for validation.
  Supports approve, edit, and skip actions in batches for efficient review.

license: MIT

metadata:
  raise.work_cycle: discovery
  raise.frequency: per-project
  raise.fase: "3"
  raise.prerequisites: discover-scan
  raise.next: discover-complete
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=discover-validate \"$CLAUDE_PROJECT_DIR\"/.raise/scripts/log-skill-complete.sh"
---

# Discovery Validate: Human Review Loop

## Purpose

Present synthesized component descriptions to the human for validation. The human reviews each component and can approve, edit, or skip. This ensures the component catalog has accurate, human-verified descriptions.

**Key insight:** Humans review, they don't write. Rai synthesizes, humans validate accuracy.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Present all components, process each approve/edit/skip decision.

**Ha (破)**: Auto-skip internal symbols (`_prefix`); focus on public APIs.

**Ri (離)**: Batch approval patterns for consistent codebases; custom filters.

## Context

**When to use:**
- After `/discover-scan` has created draft components
- When re-validating after synthesis updates
- To validate specific categories only

**When to skip:**
- All components already validated
- Draft doesn't exist (run `/discover-scan` first)

**Inputs required:**
- `work/discovery/components-draft.yaml` from `/discover-scan`

**Output:**
- Updated `work/discovery/components-draft.yaml` with `validated: true` on approved items
- Ready for `/discover-complete`

## Steps

### Step 1: Load Draft Components

Read the draft file:

```bash
cat work/discovery/components-draft.yaml
```

**Extract:**
- Total component count
- Already validated count
- Pending validation count

**Verification:** Draft file exists with components.

> **If you can't continue:** No draft file → Run `/discover-scan` first.

### Step 2: Filter for Validation

Identify components needing review:

**Include:**
- `validated: false`
- `internal: false` (public APIs)

**Exclude (auto-skip):**
- `internal: true` (private helpers) — unless user requests
- Already `validated: true`

**Calculate:**
- Total pending: N components
- Batches needed: ceil(N / 10)

**Verification:** Pending list created.

> **If you can't continue:** All components already validated → Show summary and exit.

### Step 3: Present Batch for Review

Present components in batches of 10 (default).

**For each component, display:**

```markdown
### Component {N}/{total}: {name}

**File:** {file}:{line}
**Kind:** {kind}
**Signature:** `{signature}`

**Purpose (Rai):** {purpose}

**Category:** {category}
**Dependencies:** {depends_on list}

---
```

**Then ask using AskUserQuestion:**

```
Review this component description:

Options:
- Approve: Description is accurate
- Edit: I'll provide a correction
- Skip: Exclude from catalog (internal/trivial)
```

### Step 4: Process User Decision

Based on user choice:

**Approve:**
- Set `validated: true`
- Set `validated_at: {timestamp}`
- Set `validated_by: human`
- Move to next component

**Edit:**
- Ask: "Enter corrected purpose:"
- Update `purpose` field with user's text
- Optionally ask for category correction
- Set `validated: true` (edited = validated)
- Set `validated_at: {timestamp}`
- Set `validated_by: human`
- Move to next component

**Skip:**
- Set `skipped: true`
- Set `skip_reason: "human_skip"`
- Move to next component

**Verification:** Decision recorded; draft updated.

### Step 5: Save Progress After Each Batch

After every 10 components (or batch completion):

1. Update `work/discovery/components-draft.yaml` with changes
2. Show batch summary:

```markdown
## Batch {M} Complete

- Approved: {N}
- Edited: {N}
- Skipped: {N}

**Progress:** {validated}/{total} components ({percent}%)

Continue to next batch? [Y/n/done]
```

**User options:**
- `Y` or Enter → Continue to next batch
- `n` or `done` → Save and exit (resume later)

**Verification:** Progress saved; user can resume.

### Step 6: Handle Resume

If user exits early or resumes:

1. Load `components-draft.yaml`
2. Count already-validated components
3. Continue from first unvalidated public component

**Verification:** Resume starts from correct position.

### Step 7: Final Summary

When all components reviewed (or user exits):

```markdown
## Validation Complete

**Total components:** {N}
**Validated:** {N} ({percent}%)
**Skipped:** {N}
**Remaining:** {N}

### Breakdown by Category
- Models: {N} validated
- Services: {N} validated
- Utilities: {N} validated
- ...

### Next Step

Run `/discover-complete` to export validated components for graph integration.
```

**Verification:** Summary displayed; user knows status.

## Output

- **Artifact:** Updated `work/discovery/components-draft.yaml`
- **Telemetry:** `skill_event` via Stop hook
- **Next:** `/discover-complete`

## Validation States

| State | Meaning |
|-------|---------|
| `validated: false` | Pending review |
| `validated: true` | Human approved (possibly edited) |
| `skipped: true` | Human excluded from catalog |

## Edit Flow Detail

When user chooses "Edit":

1. **Ask for purpose correction:**
   ```
   Current purpose: "{current_purpose}"

   Enter corrected purpose (or press Enter to keep):
   ```

2. **Ask for category correction (optional):**
   ```
   Current category: {category}

   Change category? [model/service/utility/handler/parser/builder/schema/command/test/keep]
   ```

3. Apply changes and mark validated.

## Batch Control

**Default batch size:** 10 components

**Rationale:**
- Small enough to complete in one sitting
- Large enough to make progress
- Saves after each batch for safety

**Early exit:** User can type "done" at any batch prompt to save and exit.

## Notes

### Validation Philosophy

The human doesn't need to write descriptions from scratch — that's Rai's job. The human validates:
- Is the purpose accurate?
- Is the category correct?
- Should this be in the catalog at all?

Most components should be quick "Approve" — edits are for corrections, not rewrites.

### Internal Symbols

Symbols starting with `_` are marked `internal: true` by `/discover-scan`. By default, `/discover-validate` skips these.

To validate internal symbols too:
```
/discover-validate --include-internal
```

### Bulk Actions

For codebases with consistent quality:
- "Approve all in this module" (future enhancement)
- "Skip all internal" (default behavior)

### Resume Safety

Progress is saved to YAML after each batch. If interrupted:
- No data loss
- Resume from last unvalidated component
- Can re-run `/discover-validate` anytime

## References

- Previous skill: `/discover-scan`
- Next skill: `/discover-complete`
- Design: `work/features/f13.3/design.md`
