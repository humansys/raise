# Story Design: RAISE-244 rai-bug-* lifecycle

> **Epic:** RAISE-242 (Skill Ecosystem)
> **Story:** RAISE-244
> **Size:** M ← adjusted from S (see Scope below)

---

## Complexity Assessment

**Moderate** — 6 components (one per lifecycle phase), no novel algorithms, but establishing a new lifecycle domain with consistent cross-skill conventions.

**UX gate:** Yes — this is a workflow skill family. The interaction design of each phase matters.
**Risk gate:** Low — all skills created via `rai-skill-create` (validates the creator).

---

## What & Why

**Problem:** RaiSE has no formal bug fix lifecycle. Bugs tracked in Jira get fixed ad-hoc — no branch convention, no root cause artifact, no traceability from reproduction to close. Developers reach for `rai-debug` (a utility, not a lifecycle) or invent their own process.

**Value:** A formal `rai-bug-*` lifecycle makes bug fixes first-class work items — traceable, reproducible, retrospectable — exactly like stories.

---

## Approach

Establish a **bug lifecycle** that mirrors the story lifecycle phase-for-phase, under a new `bug` domain. Six skills, each corresponding to a story counterpart:

| Phase | Skill | Story Counterpart | Purpose |
|-------|-------|-------------------|---------|
| 1 | `rai-bug-start` | `rai-story-start` | Branch, reproduce, define scope |
| 2 | `rai-bug-analyse` | `rai-story-design` | Root cause evidence, causal chain |
| 3 | `rai-bug-plan` | `rai-story-plan` | Fix tasks + test plan |
| 4 | `rai-bug-fix` | `rai-story-implement` | Implement fix + tests (TDD) |
| 5 | `rai-bug-review` | `rai-story-review` | Quality gates + retrospective |
| 6 | `rai-bug-close` | `rai-story-close` | Merge + cleanup + tracking update |

**All six skills are created via `rai-skill-create`** — this IS the E2E validation of RAISE-243.

**Domain:** `bug` (new lifecycle domain, not a standard one — expected, `rai skill check-name` confirms valid with advisory warning).

**Relationship to `rai-debug`:** `rai-debug` is a utility — reactive, no git lifecycle, used any time something unexpected happens during any work. `rai-bug-*` is a lifecycle — proactive, for tracked defects that become work items. They compose: `rai-bug-analyse` MAY call `rai-debug` internally for RCA depth.

---

## Scope Adjustment

Original RAISE-244 scope was S (one skill). Creating 6 skills makes this **M**. Each individual skill is XS–S, but the total breadth is M. The epic scope still fits — this is explicitly the validation client for `rai-skill-create`.

---

## Lifecycle Detail

### `rai-bug-start`
Mirrors `rai-story-start`. Creates `bug/raise-{N}/{slug}` branch from dev. Produces `bug-{N}-scope.md` with:
- Bug description (WHAT, WHEN, WHERE, EXPECTED)
- Reproduction steps verified
- Done criteria

### `rai-bug-analyse`
Mirrors `rai-story-design`. Root cause analysis artifact `bug-{N}-analysis.md`:
- Evidence gathered (logs, stack traces, minimal repro)
- Causal chain documented (5 Whys or Ishikawa depending on tier)
- Hypothesis stated and confirmed
- Fix approach decided (NOT implemented here)

### `rai-bug-plan`
Mirrors `rai-story-plan`. Task list `bug-{N}-plan.md`:
- Atomic fix tasks (TDD order: test first)
- Regression test tasks
- Commit strategy

### `rai-bug-fix`
Mirrors `rai-story-implement`. Execute plan task by task:
- Red → green → refactor
- Commit after each task
- Verification gates before proceeding

### `rai-bug-review`
Mirrors `rai-story-review`. Retrospective `bug-{N}-retro.md`:
- Root cause confirmed (fix addresses cause, not symptom)
- Regression coverage verified
- Pattern extraction (could this class of bug recur?)
- Emit pattern if applicable

### `rai-bug-close`
Mirrors `rai-story-close`. Merge to parent branch, delete bug branch, update tracking.

---

## Branch Convention

```
{dev} → bug/raise-{N}/{slug}
```

Merge target: `{dev}` (not `main`). Follows same model as story branches.

---

## Examples

```bash
# Name validation
rai skill check-name rai-bug-start
# → valid (domain warning expected — new lifecycle)

# Invocation flow
/rai-bug-start RAISE-251   # branches, defines scope
/rai-bug-analyse            # RCA, causal chain
/rai-bug-plan               # tasks
/rai-bug-fix                # implement
/rai-bug-review             # gates + retro
/rai-bug-close              # merge + cleanup

# Validation after creation
rai skill validate .claude/skills/rai-bug-start/SKILL.md
rai skill validate .claude/skills/rai-bug-analyse/SKILL.md
# ... etc for all 6
```

---

## Acceptance Criteria

**MUST:**
- [ ] All 6 `rai-bug-*` skills exist in `.claude/skills/`
- [ ] All 6 pass `rai skill validate` without errors
- [ ] All 6 created via `rai-skill-create` (one invocation per skill)
- [ ] Each skill references its story counterpart and maps phase clearly
- [ ] `rai-bug-start` creates `bug/raise-{N}/{slug}` branch from dev

**SHOULD:**
- [ ] `rai-bug-analyse` notes when `rai-debug` can be used for deeper RCA
- [ ] Lifecycle documented in a single `rai-bug-*-lifecycle.md` reference

**MUST NOT:**
- [ ] No CLI code changes — skills are pure orchestration
- [ ] `rai-debug` NOT deprecated — it serves a different purpose
