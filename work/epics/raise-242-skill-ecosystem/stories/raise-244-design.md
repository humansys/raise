# Story Design: RAISE-244 rai-bugfix

> **Epic:** RAISE-242 (Skill Ecosystem)
> **Story:** RAISE-244
> **Size:** S

---

## Complexity Assessment

**Simple/Moderate** — one skill, six internal phases. No novel algorithms. UX matters (workflow design). Fits S — single `rai-skill-create` invocation.

**UX gate:** Yes — the phase structure is the entire design. Each step must be clear and produce a verifiable artifact.
**Risk gate:** Low — rai-skill-create handles creation; this is its E2E validation.

---

## What & Why

**Problem:** RaiSE has no formal bug fix lifecycle. Bugs get fixed ad-hoc — no branch convention, no root cause artifact, no traceability from reproduction to close. Developers reach for `rai-debug` (a utility, not a lifecycle) or invent their own process.

**Value:** `rai-bugfix` makes bug fixes first-class work — same formality as a story, single skill to invoke, six phases with clear outputs.

---

## Approach

A **single skill** (`rai-bugfix`) with six internal steps that mirror the story lifecycle phase-for-phase:

| Step | Phase | Story Counterpart | Output Artifact |
|------|-------|-------------------|-----------------|
| 1 | Start | `rai-story-start` | `bug-{N}-scope.md` + branch |
| 2 | Analyse | `rai-story-design` | `bug-{N}-analysis.md` |
| 3 | Plan | `rai-story-plan` | `bug-{N}-plan.md` |
| 4 | Fix | `rai-story-implement` | code + commits |
| 5 | Review | `rai-story-review` | `bug-{N}-retro.md` |
| 6 | Close | `rai-story-close` | merge + branch deleted |

The developer invokes `/rai-bugfix BUG-ID` and follows the skill through all six steps sequentially. Each step has a `<verification>` gate and clear `<if-blocked>` guidance — same structural conventions as story skills.

**Created via one invocation of `rai-skill-create`** — this IS the E2E validation of RAISE-243.

**Relationship to `rai-debug`:** `rai-debug` is reactive and utility-grade (no git lifecycle). `rai-bugfix` is proactive and lifecycle-grade (tracked work item). Step 2 (Analyse) may delegate to `/rai-debug` for deep RCA when needed — they compose.

---

## Phase Detail

### Step 1 — Start (mirrors `rai-story-start`)
- Read `branches.development` from `.raise/manifest.yaml`
- Create `bug/{dev_branch_slug}/raise-{N}/{bug-slug}` branch
- Reproduce the bug — confirm it's observable
- Write `bug-{N}-scope.md`: WHAT / WHEN / WHERE / EXPECTED + done criteria
- Commit scope

### Step 2 — Analyse (mirrors `rai-story-design`)
- Triage tier (XS/S/M/L) determines method depth
- Gather evidence: logs, stack traces, minimal repro
- Document causal chain — 5 Whys (S) or Ishikawa (M/L)
- State hypothesis; confirm it before moving on
- Write `bug-{N}-analysis.md`; do NOT implement yet
- For deeper RCA: invoke `/rai-debug`

### Step 3 — Plan (mirrors `rai-story-plan`)
- Decompose into atomic tasks (TDD order: test first)
- Include regression test task
- Write `bug-{N}-plan.md`

### Step 4 — Fix (mirrors `rai-story-implement`)
- Execute plan task by task: RED → GREEN → REFACTOR
- Run verification gates per task: `pytest`, `ruff check`, `pyright`
- Commit after each task

### Step 5 — Review (mirrors `rai-story-review`)
- Confirm fix addresses root cause (not symptom)
- Verify regression coverage
- Extract pattern if the bug class is recurring — `rai pattern add`
- Write `bug-{N}-retro.md`

### Step 6 — Close (mirrors `rai-story-close`)
- All gates pass
- Merge to `{dev_branch}` (not `main`)
- Delete bug branch
- Update Jira/tracking

---

## Branch Convention

```
{dev_branch} → bug/raise-{N}/{slug}
```

Merge target: `{dev_branch}`. Matches story branch model.

---

## Examples

```bash
# Single invocation — developer follows all 6 steps
/rai-bugfix RAISE-251

# Name check (run by rai-skill-create internally)
rai skill check-name rai-bugfix
# → valid (domain advisory expected)

# Validate after creation
rai skill validate .claude/skills/rai-bugfix/SKILL.md
# → all checks pass
```

**Step artifact sequence for RAISE-251:**
```
bug-251-scope.md       → after Step 1
bug-251-analysis.md    → after Step 2
bug-251-plan.md        → after Step 3
[commits]              → during Step 4
bug-251-retro.md       → after Step 5
[merge + delete]       → Step 6
```

---

## Acceptance Criteria

**MUST:**
- [ ] `rai-bugfix` SKILL.md exists at `.claude/skills/rai-bugfix/SKILL.md`
- [ ] Passes `rai skill validate` without errors
- [ ] Created via `rai-skill-create` (one invocation)
- [ ] Six internal phases present, each with verification gate
- [ ] Each phase maps explicitly to its story counterpart
- [ ] Step 1 creates `bug/raise-{N}/{slug}` branch from dev

**SHOULD:**
- [ ] Step 2 mentions `/rai-debug` as optional compose for deep RCA
- [ ] ShuHaRi section present (verbosity adapts to developer level)

**MUST NOT:**
- [ ] No CLI code changes — pure orchestration
- [ ] `rai-debug` not deprecated — different purpose, different scope
