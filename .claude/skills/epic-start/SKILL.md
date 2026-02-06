---
name: epic-start
description: >
  Initialize an epic with branch and scope commit.
  Creates the epic branch from v2 that feature branches will nest under.

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "2"
  raise.prerequisites: ""
  raise.next: epic-design
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=epic-start \"$CLAUDE_PROJECT_DIR\"/.raise/scripts/log-skill-complete.sh"
---

# Start: Epic Initialization

## Purpose

Initialize an epic with a dedicated branch from v2 and a scope commit. Feature branches will be created as sub-branches of this epic branch.

**Branch model:**
```
main (stable)
  └── v2 (development)
        └── epic/e{N}/{name}        ← THIS SKILL CREATES
              └── feature/f{N}.{M}/{name}  ← /feature-start creates
```

## Steps

### Step 1: Verify on v2 Branch

Ensure we're starting from the development branch:

```bash
git branch --show-current
```

**Decision:**
- On `v2` → Continue
- On other branch → `git checkout v2 && git pull`

**Verification:** On v2 branch, up to date.

> **Poka-yoke:** Epic branches MUST branch from v2. Starting from wrong branch causes merge pain.

### Step 2: Create Epic Branch

Create the epic branch:

```bash
git checkout -b epic/e{N}/{epic-slug}
```

**Naming convention:**
- `epic/e14/rai-distribution`
- `epic/e15/telemetry-insights`

**Verification:** On new epic branch.

> **If branch exists:** `git checkout epic/e{N}/{slug}` and verify scope commit exists.

### Step 3: Define Epic Scope

Document what's in and out of scope:

```markdown
## Epic Scope: E{N} {Name}

**Objective:** {1-2 sentences}

**In Scope:**
- [Deliverable 1]
- [Deliverable 2]

**Out of Scope:**
- [Exclusion 1] → {where deferred}

**Features (planned):**
- F{N}.1: {name}
- F{N}.2: {name}

**Done when:**
- [ ] All features complete
- [ ] Epic retrospective done
- [ ] Merged to v2
```

**Verification:** Scope documented.

### Step 4: Create Scope Commit

Create the initial commit:

```bash
git add -A
git commit -m "epic(e{N}): initialize {epic-name}

Objective: {1-line}

In scope:
- {item 1}
- {item 2}

Out of scope:
- {item 1}

Co-Authored-By: Rai <rai@humansys.ai>"
```

**Verification:** Scope commit created on epic branch.

### Step 5: Emit Telemetry

```bash
uv run raise memory emit-work epic E{N} --event start --phase init
```

**Verification:** Telemetry emitted.

### Step 6: Display Lifecycle

```markdown
## Epic Lifecycle

```
/epic-start  ← YOU ARE HERE
     ↓
/epic-design (scope, features, ADRs)
     ↓
/epic-plan (sequence, milestones)
     ↓
[features via /feature-start → ... → /feature-close]
     ↓
/epic-close (retrospective, merge to v2)
```

**Next:** `/epic-design` to formalize scope and features.
```

## Output

- **Branch:** `epic/e{N}/{slug}` created from v2
- **Commit:** Scope commit with objective and boundaries
- **Telemetry:** Epic start recorded
- **Next:** `/epic-design`

## Summary Template

```markdown
## Epic Started: E{N} {Name}

**Branch:** `epic/e{N}/{slug}`
**Commit:** {hash}
**Base:** v2

### Quick Scope
**Objective:** {1-line}
**Features:** {count} planned
**Done when:** All features + retrospective + merge

### Next
→ `/epic-design` to formalize scope and features
```

## Notes

### Why Epic Branches Matter

1. **Isolation** — Epic work isolated from other epics
2. **Feature nesting** — Features branch from epic, merge to epic
3. **Clean merge** — Epic merges as unit to v2
4. **Rollback** — Can abandon entire epic if needed

### Branch Lifecycle

```
v2 ──┬── epic/e14/rai-distribution
     │         ├── feature/f14.1/base-identity
     │         ├── feature/f14.2/base-patterns
     │         └── (features merge back to epic)
     │
     └── (epic merges to v2 at /epic-close)
```

## References

- Next: `/epic-design`
- Features: `/feature-start` (verifies epic branch exists)
- Close: `/epic-close`
- Branch model: `CLAUDE.md` § Git Practices
