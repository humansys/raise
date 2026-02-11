---
name: rai-story-start
description: >
  Initialize a story with verified context, branch, and scope commit.
  Use at the beginning of story work to ensure proper setup and
  traceability from the start.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "3"
  raise.prerequisites: ""
  raise.next: story-design
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.2.0"
---

# Start: Feature Initialization

## Purpose

Initialize a feature with verified context, dedicated branch, and scope commit. This creates a clean starting point with full traceability and ensures the feature is properly situated within its epic.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps, verify epic context, create branch with scope commit.

**Ha (破)**: Skip epic verification for standalone features or experiments.

**Ri (離)**: Create custom initialization patterns for specific workflows.

## Context

**When to use:**
- Starting a new feature from the backlog
- Beginning work on an epic feature
- When you want traceable story lifecycle from the start

**When to skip:**
- Quick bug fixes (use direct branch)
- Experiments without epic context
- Continuation of already-started feature

**Inputs required:**
- Feature ID from backlog or epic scope
- Epic scope document (for epic features)
- Clear understanding of story scope

**Output:**
- Feature branch created and checked out
- Scope commit with in/out criteria
- Telemetry emitted for feature start

## Steps

### Step 1: Verify Epic Branch Exists (Poka-Yoke)

For epic features, verify the epic branch exists:

```bash
git branch --list "epic/e{N}/*" | head -1
```

**Decision:**
- Epic branch exists → Continue (will create feature sub-branch)
- Epic branch missing → **STOP.** Run `/rai-epic-start` first.

> **Poka-yoke:** Feature branches MUST nest under epic branches. Creating a story branch without its epic branch breaks the merge flow.

**Verification:** Epic branch `epic/e{N}/*` exists.

> **If you can't continue:** Run `/rai-epic-start` first to create the epic branch.

### Step 2: Verify Epic Scope Document

Verify the epic scope document exists:

```bash
ls work/epics/e{N}-*/scope.md 2>/dev/null || echo "WARN: No epic scope"
```

**Paths:**
- Epic scope: `work/epics/e{N}-{name}/scope.md`
- Features: `work/epics/e{N}-{name}/stories/`

**Decision:**
- Scope exists → Load and verify feature is listed
- Scope missing → Consider running `/rai-epic-design` after `/rai-epic-start`

**Verification:** Epic scope loaded OR noted for creation.

> **If you can't continue:** Complex feature without epic scope → Run `/rai-epic-design` first.

### Step 3: Verify Feature in Epic (If Epic Exists)

Confirm the feature is listed in the epic scope:

```bash
SCOPE="work/epics/e{N}-{name}/scope.md"
grep -q "{story_id}" "$SCOPE" && echo "Feature found in epic" || echo "WARN: Feature not in epic scope"
```

**Decision:**
- Feature found → Continue with epic context
- Feature not found → Add to epic scope or proceed as standalone

**Verification:** Feature verified in epic OR documented as standalone.

> **If you can't continue:** Should be in epic but isn't → Update epic scope first.

### Step 4: Create Feature Branch

Create a dedicated branch for the feature:

```bash
git checkout -b feature/{epic_id}/{story_id}
```

**Examples:**
- Epic feature: `git checkout -b feature/e12/f12-2`
- Standalone: `git checkout -b feature/standalone/fx-123`

**Skip condition:** For S/XS features already on an epic branch (`epic/{id}/...`), skip branch creation and work directly on the epic branch. State the skip explicitly:

> "F12.5 is S-sized and we're on epic branch. Skipping story branch per skip condition."

**Rationale:** Small stories within an epic don't need per-story branch isolation — the epic branch already isolates from main. Avoids branch proliferation for trivial changes.

**Verification:** On new story branch OR on epic branch with skip stated.

> **If you can't continue:** Branch exists → Check out existing branch or rename.

### Step 5: Define Scope

Document what's in and out of scope, plus done criteria.

**Scope template:**
```markdown
## Feature Scope: {story_id}

**In Scope:**
- [Specific deliverable 1]
- [Specific deliverable 2]

**Out of Scope:**
- [Explicit exclusion 1]
- [Deferred to future: item]

**Done Criteria:**
- [ ] [Observable outcome 1]
- [ ] [Observable outcome 2]
- [ ] Tests pass
- [ ] Retrospective complete
```

**Verification:** Scope documented with clear boundaries.

> **If you can't continue:** Scope unclear → Clarify with stakeholder or timebox discovery.

### Step 6: Create Scope Commit

Create the initial commit with scope documentation:

```bash
git add -A
git commit -m "feat({story_id}): initialize story scope

In scope:
- [item 1]
- [item 2]

Out of scope:
- [item 1]

Done when:
- [criteria 1]
- [criteria 2]

Co-Authored-By: Rai <rai@humansys.ai>"
```

**Verification:** Scope commit created on story branch.

> **If you can't continue:** Nothing to commit → Create scope as plan.md or design.md first.

### Step 7: Display Lifecycle Stages

Show the story lifecycle for orientation:

```markdown
## Feature Lifecycle

```
/rai-story-start ← YOU ARE HERE
      ↓
/rai-story-design (fase 4) — Grounds integration decisions
      ↓
/rai-story-plan (fase 5) — Decompose into tasks
      ↓
/rai-story-implement (fase 6) — Execute tasks
      ↓
/rai-story-review (fase 7) — Retrospective & learnings
      ↓
/rai-story-close (fase 8) — Merge & cleanup
```

**Next step:** `/rai-story-design` — design is not optional (PAT-186). Proceed to `/rai-story-plan` only after design.
```

**Verification:** Lifecycle displayed; next step clear.

### Step 8: Emit Feature Start (Telemetry)

Record the start of the story lifecycle:

```bash
rai memory emit-work story {story_id} --event start --phase design
```

**Example:** `rai memory emit-work story S15.1 -e start -p design`

**Verification:** Telemetry emitted.

> **If you can't continue:** CLI not available → Skip; telemetry is optional.

## Output

- **Branch:** `feature/{epic_id}/{story_id}` created and active (or epic branch for S/XS)
- **Commit:** Scope commit with in/out and done criteria (optional for S/XS on epic branch)
- **Telemetry:** `.raise/rai/personal/telemetry/signals.jsonl` (feature_lifecycle: start)
- **Next:** `/rai-story-design`

## Feature Start Summary Template

```markdown
## Feature Started: {story_id}

**Epic:** {epic_id} (or standalone)
**Branch:** `feature/{epic_id}/{story_id}`
**Scope commit:** {commit_hash}

### Scope Summary
**In:** [brief list]
**Out:** [brief list]
**Done:** [key criteria]

### Next Step
`/rai-story-design` — Design is not optional (PAT-186). Then `/rai-story-plan`.

Ready to proceed.
```

## Notes

### Why Start with Scope Commit

The scope commit serves multiple purposes:
1. **Traceability** — First commit documents intent
2. **Boundary setting** — Prevents scope creep
3. **Done criteria** — Clear completion definition
4. **Git bisect** — Clean starting point for debugging

### Epic vs Standalone Features

| Type | Branch Pattern | Epic Check |
|------|----------------|------------|
| Epic feature (M/L) | `feature/{epic}/{feature}` | Required |
| Epic feature (S/XS) | Stay on `epic/{id}/...` branch | Required |
| Standalone | `feature/standalone/{id}` | Skip |
| Experiment | `experiment/{topic}` | Skip |

### Quick Start (Minimal)

For urgency, minimum viable start:
1. Create branch
2. Commit with one-line scope
3. Emit telemetry

Full scope documentation can follow in `/rai-story-design` or `/rai-story-plan`.

## References

- Next skill: `/rai-story-design` (always — PAT-186)
- Complement: `/rai-story-close`
- Epic context: `work/epics/e{N}-{name}/scope.md`
