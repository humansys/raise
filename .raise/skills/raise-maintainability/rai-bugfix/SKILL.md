---
name: rai-bugfix
description: >
  Guide the developer through a formal 7-phase bug fix lifecycle
  (start → triage → analyse → plan → fix → review → close) with
  classification in 4 dimensions and process improvement extraction.
  Use for tracked bugs that need full accountability from reproduction to close.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: as-needed
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"
  raise.visibility: internal
  raise.skillset: raise-maintainability
---

# Bugfix

## Purpose

Guide the developer through a formal 7-phase bug fix lifecycle — branch, triage, analyse, plan, fix, review, close — producing classified bug data, process improvements, and the same artifacts and traceability as a story.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all 7 phases strictly; produce every named artifact
- **Ha**: Collapse plan into analyse for XS bugs; skip retro for trivial fixes
- **Ri**: Define domain-specific triage patterns; feed systemic findings to graph

## Context

**When to use:** Tracked bug (Jira issue) needs formal resolution: branch, artifact trail, retrospective.

**When to skip:** Trivial fix (typo, obvious one-liner) — commit directly. For RCA without lifecycle overhead, use `/rai-debug`.

**Inputs:** Bug ID (e.g., RAISE-251), problem statement or reproduction steps.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`.

## Steps

### Step 1: Start *(mirrors `rai-story-start`)*

`git checkout {dev_branch} && git checkout -b bug/raise-{N}/{bug-slug}`

Update the tracker immediately — assign to yourself and move to In Progress:

```bash
rai backlog update RAISE-{N} --assignee "{developer-email}" -a jira
rai backlog transition RAISE-{N} in-progress -a jira
```

Use the developer's Jira email from memory or session context. If not known, ask before proceeding.

Reproduce the bug — confirm it is observable. Write `work/bugs/RAISE-{N}/scope.md`:

```
WHAT:      [behavior observed]
WHEN:      [conditions / triggers]
WHERE:     [file:line or component]
EXPECTED:  [correct behavior]
Done when: [specific observable outcome]
```

<verification>
On `bug/raise-{N}/{slug}` branch. Jira issue assigned and In Progress. Bug reproduces. Scope artifact committed.
</verification>

### Step 2: Triage *(classify before investigating)*

Classify the bug in 4 orthogonal dimensions before any analysis:

| Dimension | Scope artifact value | Jira dropdown value |
|-----------|---------------------|---------------------|
| **Bug Type** | Functional, Interface, Data, Logic, Configuration, Regression | *(same)* |
| **Severity** | S0-Critical, S1-High, S2-Medium, S3-Low | Sev-0, Sev-1, Sev-2, Sev-3 |
| **Origin** | Requirements, Design, Code, Integration, Environment | *(same, but Jira has typo: "Enviroment")* |
| **Qualifier** | Missing, Incorrect, Extraneous | *(same)* |

Append to `work/bugs/RAISE-{N}/scope.md`:

```
TRIAGE:
  Bug Type:    [Functional|Interface|Data|Logic|Configuration|Regression]
  Severity:    [S0-Critical|S1-High|S2-Medium|S3-Low]
  Origin:      [Requirements|Design|Code|Integration|Environment]
  Qualifier:   [Missing|Incorrect|Extraneous]
```

Update Jira — set the 4 classification custom fields via MCP. Map Severity to Jira format (`S{N}-Label` → `Sev-{N}`) and Origin Environment → `Enviroment`:

```
mcp__atlassian__jira_update_issue(
  issue_key = "RAISE-{N}",
  additional_fields = '{"customfield_13267": {"value": "{Bug Type}"}, "customfield_12090": {"value": "Sev-{N}"}, "customfield_13269": {"value": "{Origin}"}, "customfield_13270": {"value": "{Qualifier}"}}'
)
```

Then transition:

```bash
rai backlog transition RAISE-{N} triaged -a jira
```

> **Field IDs:** Bug Type = `customfield_13267`, Severity = `customfield_12090`, Origin = `customfield_13269`, Qualifier = `customfield_13270`.

**Triage gate:** All 4 dimensions must be classified before advancing to Analyse. If uncertain about Origin, use your best hypothesis — it can be revised during Analyse.

<verification>
4 dimensions classified. Jira fields set. Issue transitioned to Triaged. Scope artifact updated.
</verification>

### Step 3: Analyse *(mirrors `rai-story-design`)*

| Tier | Criteria | Method |
|------|----------|--------|
| XS | Cause evident | Skip to Step 3 |
| S | Single causal chain | 5 Whys |
| M/L | Multiple possible causes | Ishikawa |

**5 Whys (S):** Trace one factual causal chain — ask "Why?" five times, each answer evidenced. Stop at actionable root cause. Record: `Problem → Why1 → Why2 → Why3 → Why4 → Root cause → Countermeasure`.

**Ishikawa (M/L):** Explore 6 M's: Method, Machine, Material, Measurement, Manpower, Milieu. State each hypothesis, test it, confirm or eliminate:

| Hypothesis | Test | Result | Conclusion |
|------------|------|--------|------------|

Rule for both: "Human error" is never a root cause — ask why the error was possible.

Write `work/bugs/RAISE-{N}/analysis.md`: confirmed root cause + fix approach.

<verification>
Root cause stated with evidence. Fix approach decided — not implemented yet.
</verification>

### Step 4: Plan *(mirrors `rai-story-plan`)*

Write `work/bugs/RAISE-{N}/plan.md`: atomic tasks in TDD order (regression test task first), verification command and commit message per task.

<verification>
Regression test task listed first. Each task independently committable.
</verification>

### Step 5: Fix *(mirrors `rai-story-implement`)*

Execute plan tasks in order. Per task: RED (failing regression test) → GREEN (minimal fix) → REFACTOR. Verify and commit before moving on:

Resolve verification commands using this priority chain:

1. **Check `.raise/manifest.yaml`** for `project.test_command`, `project.lint_command`, `project.type_check_command` — if set, use directly
2. **Detect language** from `project.project_type` in manifest, or scan file extensions
3. **Map language to default** (see `/rai-story-implement` Step 3 for the full table)

The manifest always wins when present. **Run ALL four gates** (test + lint + format + type check) after each task — not just the one mentioned in the plan.

<verification>
All tasks committed. All four gates pass (test, lint, format, types). Bug no longer reproduces.
</verification>

<if-blocked>
3 attempts without fix → document partial state, create follow-up issue.
</if-blocked>

### Step 6: Review *(mirrors `rai-story-review`)*

Verify: fix addresses root cause (not symptom), regression test green, no regressions introduced.

**Heutagogical checkpoint** — answer with specific examples:
1. What did you learn about this system or codebase?
2. What would you change about the fix process?
3. Are there improvements for the framework (skill, guardrail, template)?
4. What are you more capable of now?

**Add patterns** worth preserving (causal insights, recurring failure modes):

```bash
rai pattern add "{causal insight}" --context "{keywords}" --type process --scope project --from RAISE-{N}
```

Types: `process`, `technical`, `architecture`, `codebase`. Use `--scope project` — bug insights are codebase-specific.

**Reinforce behavioral patterns** loaded at session start:

```bash
rai pattern reinforce {pattern_id} --vote {1|0|-1} --from RAISE-{N}
```

| Vote | Meaning |
|:----:|---------|
| `1` | Fix followed the pattern |
| `0` | Pattern not relevant (does NOT count toward scoring) |
| `-1` | Fix contradicted the pattern |

Only evaluate patterns you consciously considered. `0` is correct for most patterns.

**Process improvement extraction** — answer with specifics:

1. What change in process or tooling would prevent this **class** of bug?
2. What classification pattern does this bug represent? (e.g., Type=Functional + Origin=Code + Qualifier=Missing → missing boundary validation)

**Write `work/bugs/RAISE-{N}/retro.md`:**

```markdown
## Retrospective: RAISE-{N}

### Summary
- Root cause: {one line}
- Fix approach: {one line}
- Classification: {Bug Type}/{Severity}/{Origin}/{Qualifier}

### Process Improvement
**Prevention:** {specific process/tool change that would prevent this class of bug}
**Pattern:** {Bug Type}={X} + {Origin}={Y} → {systemic insight}

### Heutagogical Checkpoint
1. Learned: ...
2. Process change: ...
3. Framework improvement: ...
4. Capability gained: ...

### Patterns
- Added: {pattern IDs or "none"}
- Reinforced: {pattern IDs and votes, or "none evaluated"}
```

<verification>
Retro written. Checkpoint answered. Patterns added/reinforced. All gates green.
</verification>

### Step 7: Close *(mirrors `rai-story-close`)*

**Never merge locally to `{dev_branch}`.** Push the bug branch and create a merge request.

```bash
# Push bug branch to origin
git push origin bug/raise-{N}/{slug} -u

# Create merge request via glab
glab mr create \
  --source-branch bug/raise-{N}/{slug} \
  --target-branch {dev_branch} \
  --title "fix(RAISE-{N}): {summary}" \
  --description "Root cause: {one line}

Co-Authored-By: Rai <rai@humansys.ai>" \
  --no-editor

# Delete local branch
git branch -D bug/raise-{N}/{slug}
```

If `glab` is not available, provide the GitLab URL from `git push` output for manual MR creation.

Update tracker:

```bash
rai backlog transition RAISE-{N} done -a jira
```

<verification>
MR created in GitLab targeting `{dev_branch}`. Local branch deleted. Jira transitioned to Done.
</verification>

## Output

| Artifact | Step | Purpose |
|----------|------|---------|
| `work/bugs/RAISE-{N}/scope.md` | 1, 2 | Bug definition + done criteria + triage classification |
| `work/bugs/RAISE-{N}/analysis.md` | 3 | Root cause + fix approach |
| `work/bugs/RAISE-{N}/plan.md` | 4 | Atomic tasks + test plan |
| Code + commits | 5 | Fix + regression tests |
| `work/bugs/RAISE-{N}/retro.md` | 6 | Learnings + process improvement + optional pattern |
| Merge request | 7 | GitLab MR: bug branch → `{dev_branch}` |

## Quality Checklist

- [ ] Jira issue assigned and transitioned to In Progress (Step 1)
- [ ] Bug reproduces before any fix (Step 1)
- [ ] Bug classified in 4 dimensions, Jira fields set, transitioned to Triaged (Step 2)
- [ ] Root cause confirmed with evidence (Step 3)
- [ ] Regression test written RED-first (Step 5)
- [ ] All gates pass: test runner, linter, type checker (Step 5)
- [ ] Fix verified against root cause — not symptom (Step 6)
- [ ] Process improvement extracted with prevention + pattern (Step 6)
- [ ] Heutagogical checkpoint answered with specific examples (Step 6)
- [ ] Patterns added with `--scope project` if applicable (Step 6)
- [ ] MR created in GitLab targeting `{dev_branch}` (Step 7)
- [ ] Local branch deleted after MR creation (Step 7)
- [ ] Jira transitioned to Done (Step 7)
- [ ] NEVER merge locally to `{dev_branch}` — always via MR
- [ ] NEVER fix before analysing — symptoms recur without root cause
- [ ] NEVER merge without retro — learnings compound
- [ ] NEVER skip pattern reinforce — scoring system depends on it

## References

- Lifecycle mirrors (Steps 1→7): `/rai-story-start` · *triage* · `/rai-story-design` · `/rai-story-plan` · `/rai-story-implement` · `/rai-story-review` · `/rai-story-close`
- Branch model: `CLAUDE.md` § Branch Model
