# SOP: Branch Management and Scope Control

> Standard Operating Procedure for preventing scope drift in Git branches
> Version: 1.0
> Date: 2026-01-31
> Status: Active

---

## Purpose

Prevent branch scope drift by establishing clear naming conventions, scope definitions, and daily/weekly check procedures.

**Problem this solves:** Branches starting with clear intent (e.g., `project/raise-cli`) accumulate unrelated work (framework changes, research), making it unclear what the branch is actually for.

**Impact of scope drift:**
- Unclear what's being changed (review difficulty)
- Harder to merge selectively
- Branch names don't match content
- Mixed concerns in commits

---

## Branch Naming Convention

### Format

```
<type>/<scope>/<short-description>
```

**Examples:**
```
feature/raise-cli/cli-skeleton
framework/research-templates
experiment/lean-specs-discovery
bugfix/kata-execution/state-persistence
docs/framework/research-kata
```

### Branch Types

| Type | Purpose | Lifespan | Scope Rule |
|------|---------|----------|------------|
| `feature/` | New functionality implementation | 2-5 days | Single feature with clear DoD |
| `framework/` | Framework-only changes (methodology, templates, katas) | 2-5 days | No project-specific code |
| `experiment/` | **Research, discovery, multi-concern exploratory work** | 1-7 days | **Expect to rename or discard** |
| `bugfix/` | Bug fixes | 1-2 days | Single bug or related set |
| `hotfix/` | Urgent production fixes | <1 day | Critical fix only |
| `docs/` | Documentation only | 1-2 days | No code changes |
| `refactor/` | Code refactoring | 2-5 days | No behavior changes |

**Special:**
- `foundation-YYMM` or `sprint-YYMM`: Multi-concern sprint work (document all concerns upfront)

### Type Selection Decision Tree

```
Is it exploratory or multi-concern?
  └─▶ YES → experiment/
      (You can rename later when scope becomes clear)

Is it framework methodology, templates, or katas?
  └─▶ YES → framework/

Is it a single, well-defined feature?
  └─▶ YES → feature/

Is it fixing a bug?
  └─▶ YES → bugfix/

Is it only documentation?
  └─▶ YES → docs/
```

---

## Scope Definition (Before Branch Creation)

### Required: Scope Document in First Commit

**Create branch with scope documented:**

```bash
# Create branch
git checkout -b experiment/raise-cli-discovery

# First commit: Scope document
git commit --allow-empty -m "feat: Start raise-cli discovery

SCOPE:
- Research raise-cli architecture and tech stack
- Create project katas (PRD, Vision, Design, Backlog)
- Initial spike on CLI framework selection

OUT OF SCOPE:
- Implementation code (later branches)
- Framework template changes (separate concern)

DONE CRITERIA:
- Project katas complete and validated
- Architecture decisions documented (ADR if needed)
- Ready to start feature implementation

EXPECTED DURATION: 3-5 days
"
```

### Scope Template

```markdown
SCOPE:
- [Concern 1: What you're working on]
- [Concern 2: Related work]

OUT OF SCOPE:
- [Thing 1: What you're explicitly NOT doing]
- [Thing 2: What belongs in separate branch]

DONE CRITERIA:
- [ ] [Observable outcome 1]
- [ ] [Observable outcome 2]

EXPECTED DURATION: [X days]
```

---

## Daily Scope Check (Session Start Ritual)

**Every time you start working on a branch:**

### 1. Review Branch Diff

```bash
# Check what's changed from base branch
git diff v2 --name-only

# Or see stats
git diff v2 --stat
```

### 2. Ask Three Questions

1. **Does everything here belong to the same concern?**
   - If NO → Rename or split

2. **Does the content match the branch name?**
   - If NO → Rename branch

3. **Am I working on what I intended?**
   - If NO → Reassess scope or create new branch

### 3. Decision Matrix

| Situation | Action |
|-----------|--------|
| **Everything matches branch name** | ✅ Continue working |
| **Minor drift (1-2 unrelated files)** | Move to parking lot, create separate branch |
| **Major drift (different concern)** | **STOP** → Rename branch or split |
| **Branch >5 days old** | Review: Merge what's ready, create new branch for rest |

---

## Weekly Scope Review (Friday or Sprint End)

### Branch Hygiene Checklist

```bash
# List all your branches
git branch

# For each branch:
git checkout <branch>
git diff v2 --name-only
```

**Review:**
- [ ] Branches >5 days old: Merge or justify continuation
- [ ] Branches with mixed scope: Rename or split
- [ ] Stale branches (not touched in >1 week): Delete or document why keeping
- [ ] `experiment/` branches: Rename to proper type if scope is now clear

---

## When to Rename vs Split

### Rename is OK When:

✅ **Early in lifecycle** (<3 days old, no PR yet)
✅ **Scope genuinely evolved** (discovery revealed different concern)
✅ **Branch not yet public** OR team is small and coordinated
✅ **New name MORE accurate** than original
✅ **Using experiment/ type** (expected to rename)

**How to rename:**
```bash
git branch -m old-name new-name
git push origin --delete old-name  # if already pushed
git push -u origin new-name
```

### Split is Better When:

🔀 **Distinct concerns** that can be developed independently
🔀 **Branch >5 days old** with mixed work
🔀 **Open PR/MR** with reviews (finish this, start new for other work)

**How to split:**
```bash
# Finish current branch with what's cohesive
git add [files for current concern]
git commit -m "feat: Complete [current concern]"

# Create new branch for other work
git checkout v2
git checkout -b <new-branch>

# Cherry-pick or implement other concern
git cherry-pick [commits] # if already committed
# or just implement fresh
```

---

## Parking Lot Discipline

**Capture scope creep as it happens:**

### When You Discover New Work

```markdown
# dev/parking-lot.md

## While working on [branch-name]

**Date**: 2026-01-31

**Discovered**:
- Need research prompt template for systematic research
- Feature spec format unclear (prose vs examples?)
- Research kata needs tool selection guidance

**Decision**:
- ✅ Add to this branch: Research prompt template (related to discovery process)
- 🅿️ Parking lot: Pre-commit hooks for scope checking (separate concern)
- 🌿 New branch: framework/research-templates (if substantial)

**Rationale**: Research infrastructure needed for current work (discovery phase)
```

### Parking Lot Entry Format

```markdown
## [Topic/Concern]

**Discovered while**: [Working on X branch]
**Date**: YYYY-MM-DD
**Priority**: High/Medium/Low
**Effort**: Small/Medium/Large
**Action**: New branch / Add to backlog / Document for later
```

---

## Scope Evolution: How to Document

**When scope changes during work, document in commit message:**

```bash
git commit -m "feat: Add research infrastructure

SCOPE EVOLUTION:
Started as: raise-cli project discovery
Evolved to: Foundation sprint (framework + project setup)
Reason: Discovered need for lean spec format research before
        implementing features. Natural evolution during discovery work.

ORIGINAL SCOPE:
- Project katas (PRD, Vision, Design, Backlog)

ACTUAL SCOPE:
- Project katas ✓
- Research infrastructure (prompt template, evidence catalog)
- Lean story spec v2 template
- Feature/design kata

JUSTIFICATION:
Discovery work revealed inadequate research and spec processes.
Rather than delay, addressed foundational issues immediately.
All work cohesive: setting up RaiSE framework + first project.

[Detailed changes...]
"
```

---

## Branch Lifecycle Policy

### Maximum Lifespans

| Branch Type | Max Age | Action on Overage |
|-------------|---------|-------------------|
| `feature/` | 5 days | Merge what's ready, create new for remaining |
| `framework/` | 5 days | Merge or justify (complex changes may need longer) |
| `experiment/` | 7 days | Rename to proper type or merge/discard |
| `bugfix/` | 2 days | Urgent fixes should be fast; reassess if longer |
| `docs/` | 2 days | Documentation shouldn't take long |

**Exception:** Foundation/sprint branches can be longer if scope is documented and cohesive

### Short-Lived Branch Benefits

- **Easier to review** (smaller diffs)
- **Less merge conflicts** (less divergence from base)
- **Clearer intent** (focused scope)
- **Faster feedback** (merge and validate quickly)

---

## Git Workflow (GitHub Flow Adapted)

```
v2 (development branch)
 │
 ├─▶ experiment/discovery-spike (3-5 days)
 │   └─▶ Rename → feature/implement-X (2-3 days)
 │       └─▶ Merge → v2
 │
 ├─▶ framework/research-templates (2-5 days)
 │   └─▶ Merge → v2
 │
 └─▶ foundation-jan2026 (1 sprint, documented scope)
     └─▶ Merge → v2

v2 accumulates all validated work
 │
 └─▶ Merge to main at release (Feb 15)
```

**Rules:**
1. **All branches from v2** (not main)
2. **Short-lived** (days, not weeks)
3. **One concern per branch** (or document multi-concern in experiment/)
4. **Merge/delete quickly** (don't let branches linger)
5. **If scope changes, rename early** (<3 days)

---

## Team Communication (for Multi-Person Teams)

**When creating branch (Slack/Discord):**
```
🌿 New branch: experiment/raise-cli-discovery
Scope: Initial project setup for raise-cli
  - Project katas (PRD, Vision, Design, Backlog)
  - Discovery research
Out of scope: Implementation code
ETA: 3-5 days
```

**When scope evolves:**
```
🔄 Branch scope evolved: experiment/raise-cli-discovery
Original: Just project katas
Actual: Project katas + framework research infrastructure
Decision: Renaming to foundation-jan2026 (cohesive sprint work)
Reason: Discovered foundational process gaps during discovery
```

---

## Common Scope Drift Patterns

### Pattern 1: "While I'm Here" Syndrome

**Symptom:** Fixing unrelated bugs or refactoring while implementing feature

**Prevention:**
- Add to parking lot
- Create bugfix/ branch separately
- Finish feature first

### Pattern 2: Framework Work Creeping into Feature Branch

**Symptom:** `.raise/` changes appearing in `feature/` branch

**Prevention:**
- Ask: "Is this framework-level or feature-specific?"
- If framework: Create `framework/` branch
- Exception: Feature requires new kata/template (document in commit)

### Pattern 3: Research Expanding Beyond Original Question

**Symptom:** Started researching X, now researching Y, Z, and W

**Prevention:**
- Use `experiment/` type (signals exploratory)
- Define research scope upfront (primary + secondary questions)
- Parking lot tangent discoveries
- Time-box research sessions

### Pattern 4: "Just One More Thing"

**Symptom:** Branch ready to merge but keep adding "quick improvements"

**Prevention:**
- Set hard merge deadline
- "Improvement" backlog for post-merge work
- Perfect is enemy of good (merge and iterate)

---

## Automated Guardrails (Optional)

### Pre-Commit Hook: Scope Drift Warning

```bash
# .raise/hooks/pre-commit-scope-check.sh

#!/bin/bash
BRANCH=$(git branch --show-current)
CHANGED_FILES=$(git diff --cached --name-only)

# Warn if framework changes in non-framework branch
if [[ $BRANCH != framework/* ]] && [[ $BRANCH != experiment/* ]] && echo "$CHANGED_FILES" | grep -q "^\.raise/"; then
    echo "⚠️  Warning: Framework changes in non-framework branch"
    echo "Branch: $BRANCH"
    echo "Framework files changed:"
    echo "$CHANGED_FILES" | grep "^\.raise/"
    echo ""
    echo "Consider:"
    echo "  1. Move to framework/ branch"
    echo "  2. Use experiment/ branch type"
    echo "  3. Document justification in commit message"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

**Installation:**
```bash
chmod +x .raise/hooks/pre-commit-scope-check.sh
ln -s ../../.raise/hooks/pre-commit-scope-check.sh .git/hooks/pre-commit
```

---

## Examples of Good vs Bad Branch Usage

### ✅ GOOD: Clear Scope, Proper Type

```
Branch: feature/raise-cli/cli-skeleton
Commits:
  - feat: Add Typer CLI app with --version, --help
  - feat: Add global options (-v, -q, --format)
  - test: Add CLI tests
  - docs: Update README with CLI usage
All commits related to CLI skeleton. Clean. Mergeable.
```

### ✅ GOOD: Experiment that Evolved

```
Branch: experiment/raise-cli-discovery
Commits:
  - docs: Define initial scope (project katas only)
  - feat: Add raise-cli PRD
  - feat: Add raise-cli Vision
  - docs: Scope evolution (added framework research)
  - feat: Add research prompt template
  - feat: Add story spec v2 template
Final action: Renamed to foundation-jan2026 (cohesive sprint)
```

### ❌ BAD: Scope Drift, Wrong Type

```
Branch: feature/cli-skeleton
Commits:
  - feat: Add Typer CLI app
  - feat: Add research prompt template (❌ framework work)
  - fix: Typo in README (❌ unrelated docs)
  - feat: Update research kata (❌ framework work)
  - refactor: Cleanup project structure (❌ refactoring)
  - feat: Add CLI global options (✅ related)
Mixed concerns. Should have been experiment/ or split into multiple branches.
```

### ❌ BAD: Branch Too Old, Scope Unclear

```
Branch: project/miscellaneous (14 days old)
Commits: 47 commits touching 89 files
What's this for? Hard to tell. Hard to review. Hard to merge.
```

---

## Recommended Workflow for RaiSE

### 1. Starting Work

```bash
# Before creating branch: Define scope
# Am I exploring (experiment/) or implementing (feature/)?

# Create branch with scope commit
git checkout v2
git pull origin v2
git checkout -b <type>/<scope>/<description>

git commit --allow-empty -m "Start <work>

SCOPE: [What I'm doing]
OUT OF SCOPE: [What I'm not doing]
DONE: [How I know I'm done]
DURATION: [X days]
"
```

### 2. Daily Check (Session Start)

```bash
# Check diff from base
git diff v2 --name-only

# Ask: Does this match my branch name and scope?
# If no: Rename or split
```

### 3. During Work

```markdown
# Capture drift in parking lot immediately
While working on X:
- Discovered need for Y → New branch or parking lot?
- Found bug Z → bugfix/ branch or parking lot?
```

### 4. Before Commit

```bash
# Review what's staged
git diff --cached --name-only

# Ask: Does this all belong here?
# If mixed: Stage separately, commit separately, or create new branch
```

### 5. Weekly Review (Friday)

```bash
# List branches
git branch

# For each: Check age, check scope, decide: merge/rename/split/delete
```

### 6. Before Merge

```bash
# Final scope check
git diff v2 --stat

# Document any scope evolution in final commit or MR description
```

---

## Checklist: Am I Following Branch SOPs?

**Daily (session start):**
- [ ] Reviewed: `git diff v2 --name-only`
- [ ] Content matches branch name and type
- [ ] Scope hasn't drifted beyond original intent (or documented evolution)

**Before each commit:**
- [ ] Staged files all related to same concern
- [ ] Commit message clear about what and why

**Weekly:**
- [ ] No branches >5 days old (unless justified)
- [ ] All branches have clear purpose
- [ ] Parking lot updated with out-of-scope discoveries

**Before creating PR/MR:**
- [ ] Branch name accurately reflects content
- [ ] Scope evolution documented (if any)
- [ ] All commits cohesive and related

---

## Exceptions and Edge Cases

### Exception 1: Foundation/Sprint Branches

**When:** Setting up new project or framework infrastructure
**Allowed:** Multiple related concerns if documented upfront
**Naming:** `foundation-YYMM` or `sprint-YYMM`
**Requirement:** Document all concerns in first commit

### Exception 2: Emergency Hotfixes

**When:** Production is down, urgent fix needed
**Allowed:** Skip normal process, fix immediately
**Requirement:** Create `hotfix/` branch, merge ASAP, document after

### Exception 3: Research Leading to Implementation

**When:** Research branch discovers need to implement solution
**Allowed:** Implement in same branch if cohesive
**Requirement:** Start with `experiment/`, rename when scope clear, document evolution

---

## References

- **Git Flow**: https://nvie.com/posts/a-successful-git-branching-model/
- **GitHub Flow**: https://docs.github.com/en/get-started/quickstart/github-flow
- **Trunk-Based Development**: https://trunkbaseddevelopment.com/

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-01-31 | Initial SOP based on foundation-jan2026 experience |

---

**Status**: Active
**Review Frequency**: Quarterly or when process issues arise
**Owner**: RaiSE Framework Team
**Next Review**: 2026-04-30
