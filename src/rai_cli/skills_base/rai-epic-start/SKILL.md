---
name: rai-epic-start
description: >
  Initialize an epic with branch and scope commit.
  Creates the epic branch from the development branch that story branches will nest under.

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
---

# Start: Epic Initialization

## Branch Configuration

**Read `branches.development` from `.raise/manifest.yaml`** to determine the project's development branch. All references to `{dev_branch}` below use this value. Default: `main`.

## Purpose

Initialize an epic with a dedicated branch from `{dev_branch}` and a scope commit. Feature branches will be created as sub-branches of this epic branch.

## Context

**When to use:**
- Starting a new body of work (3-10 features)
- Beginning a planned epic from the backlog
- Creating isolation for a significant capability

**When to skip:**
- Small fixes or single features (use story branch from `{dev_branch}`)
- Continuation of existing epic (branch already exists)

**Inputs required:**
- Epic number (E{N})
- Epic name/slug
- High-level objective

**Output:**
- Epic branch created from `{dev_branch}`
- Scope commit documenting boundaries
- Telemetry recorded

**Branch model:**
```
main (stable)
  └── {dev_branch} (development)
        └── epic/e{N}/{name}        ← THIS SKILL CREATES
              └── feature/f{N}.{M}/{name}  ← /rai-story-start creates
```

## Steps

### Step 1: Verify on Development Branch

Ensure we're starting from the development branch (`{dev_branch}`):

```bash
git branch --show-current
```

**Decision:**
- On `{dev_branch}` → Continue
- On other branch → `git checkout {dev_branch} && git pull`

**Verification:** On `{dev_branch}` branch, up to date.

> **Poka-yoke:** Epic branches MUST branch from `{dev_branch}`. Starting from wrong branch causes merge pain.

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
- [ ] Merged to `{dev_branch}`
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
rai memory emit-work epic E{N} --event start --phase init
```

**Verification:** Telemetry emitted.

### Step 6: Display Lifecycle

```markdown
## Epic Lifecycle

```
/rai-epic-start  ← YOU ARE HERE
     ↓
/rai-epic-design (scope, features, ADRs)
     ↓
/rai-epic-plan (sequence, milestones)
     ↓
[features via /rai-story-start → ... → /rai-story-close]
     ↓
/rai-epic-close (retrospective, merge to {dev_branch})
```

**Next:** `/rai-epic-design` to formalize scope and features.
```

## Output

- **Branch:** `epic/e{N}/{slug}` created from `{dev_branch}`
- **Commit:** Scope commit with objective and boundaries
- **Telemetry:** Epic start recorded
- **Next:** `/rai-epic-design`

## Summary Template

```markdown
## Epic Started: E{N} {Name}

**Branch:** `epic/e{N}/{slug}`
**Commit:** {hash}
**Base:** `{dev_branch}`

### Quick Scope
**Objective:** {1-line}
**Features:** {count} planned
**Done when:** All features + retrospective + merge

### Next
→ `/rai-epic-design` to formalize scope and features
```

## Notes

### Why Epic Branches Matter

1. **Isolation** — Epic work isolated from other epics
2. **Feature nesting** — Features branch from epic, merge to epic
3. **Clean merge** — Epic merges as unit to `{dev_branch}`
4. **Rollback** — Can abandon entire epic if needed

### Branch Lifecycle

```
{dev_branch} ──┬── epic/e14/rai-distribution
     │         ├── feature/f14.1/base-identity
     │         ├── feature/f14.2/base-patterns
     │         └── (features merge back to epic)
     │
     └── (epic merges to {dev_branch} at /rai-epic-close)
```

## References

- Next: `/rai-epic-design`
- Features: `/rai-story-start` (verifies epic branch exists)
- Close: `/rai-epic-close`
- Branch model: `CLAUDE.md` § Git Practices
