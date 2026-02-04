---
name: feature-start
description: >
  Initialize a feature with verified context, branch, and scope commit.
  Use at the beginning of feature work to ensure proper setup and
  traceability from the start.

license: MIT

metadata:
  raise.work_cycle: feature
  raise.frequency: per-feature
  raise.fase: "3"
  raise.prerequisites: ""
  raise.next: feature-design
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=feature-start \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
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
- When you want traceable feature lifecycle from the start

**When to skip:**
- Quick bug fixes (use direct branch)
- Experiments without epic context
- Continuation of already-started feature

**Inputs required:**
- Feature ID from backlog or epic scope
- Epic scope document (for epic features)
- Clear understanding of feature scope

**Output:**
- Feature branch created and checked out
- Scope commit with in/out criteria
- Telemetry emitted for feature start

## Steps

### Step 1: Verify Epic Context (Conditional)

For epic features, verify the epic scope exists:

```bash
ls dev/epic-{epic_id}-scope.md 2>/dev/null || echo "WARN: No epic context"
```

**Decision:**
- Epic exists → Load and verify feature is listed
- Epic missing + complex feature → Consider creating epic scope first
- Epic missing + simple feature → Continue with standalone note

**Verification:** Epic context loaded OR explicitly standalone.

> **If you can't continue:** Complex feature without epic → Run `/epic-design` first.

### Step 2: Verify Feature in Epic (If Epic Exists)

Confirm the feature is listed in the epic scope:

```bash
grep -q "{feature_id}" dev/epic-{epic_id}-scope.md && echo "Feature found in epic" || echo "WARN: Feature not in epic scope"
```

**Decision:**
- Feature found → Continue with epic context
- Feature not found → Add to epic scope or proceed as standalone

**Verification:** Feature verified in epic OR documented as standalone.

> **If you can't continue:** Should be in epic but isn't → Update epic scope first.

### Step 3: Create Feature Branch

Create a dedicated branch for the feature:

```bash
git checkout -b feature/{epic_id}/{feature_id}
```

**Examples:**
- Epic feature: `git checkout -b feature/e12/f12-2`
- Standalone: `git checkout -b feature/standalone/fx-123`

**Verification:** On new feature branch.

> **If you can't continue:** Branch exists → Check out existing branch or rename.

### Step 4: Define Scope

Document what's in and out of scope, plus done criteria.

**Scope template:**
```markdown
## Feature Scope: {feature_id}

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

### Step 5: Create Scope Commit

Create the initial commit with scope documentation:

```bash
git add -A
git commit -m "feat({feature_id}): initialize feature scope

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

**Verification:** Scope commit created on feature branch.

> **If you can't continue:** Nothing to commit → Create scope as plan.md or design.md first.

### Step 6: Display Lifecycle Stages

Show the feature lifecycle for orientation:

```markdown
## Feature Lifecycle

```
/feature-start ← YOU ARE HERE
      ↓
/feature-design (fase 4) — Optional for simple features
      ↓
/feature-plan (fase 5) — Decompose into tasks
      ↓
/feature-implement (fase 6) — Execute tasks
      ↓
/feature-review (fase 7) — Retrospective & learnings
      ↓
/feature-close (fase 8) — Merge & cleanup
```

**Next step:** `/feature-design` for complex features, `/feature-plan` for simple ones.
```

**Verification:** Lifecycle displayed; next step clear.

### Step 7: Emit Feature Start (Telemetry)

Record the start of the feature lifecycle:

```bash
raise telemetry emit feature {feature_id} --event start --phase design
```

**Example:** `raise telemetry emit feature F12.2 -e start -p design`

**Verification:** Telemetry emitted.

> **If you can't continue:** CLI not available → Skip; telemetry is optional.

## Output

- **Branch:** `feature/{epic_id}/{feature_id}` created and active
- **Commit:** Scope commit with in/out and done criteria
- **Telemetry:** `.rai/telemetry/signals.jsonl` (feature_lifecycle: start)
- **Next:** `/feature-design` or `/feature-plan`

## Feature Start Summary Template

```markdown
## Feature Started: {feature_id}

**Epic:** {epic_id} (or standalone)
**Branch:** `feature/{epic_id}/{feature_id}`
**Scope commit:** {commit_hash}

### Scope Summary
**In:** [brief list]
**Out:** [brief list]
**Done:** [key criteria]

### Next Steps
1. `/feature-design` — If complex (>3 components, architectural decisions)
2. `/feature-plan` — If simple or design complete

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
| Epic feature | `feature/{epic}/{feature}` | Required |
| Standalone | `feature/standalone/{id}` | Skip |
| Experiment | `experiment/{topic}` | Skip |

### Quick Start (Minimal)

For urgency, minimum viable start:
1. Create branch
2. Commit with one-line scope
3. Emit telemetry

Full scope documentation can follow in `/feature-design` or `/feature-plan`.

## References

- Next skill: `/feature-design` or `/feature-plan`
- Complement: `/feature-close`
- Epic context: `dev/epic-{id}-scope.md`
