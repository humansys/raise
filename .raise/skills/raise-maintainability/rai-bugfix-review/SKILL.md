---
name: rai-bugfix-review
description: Retrospective, pattern extraction, and process improvement. Phase 6 of bugfix pipeline.

allowed-tools:
  - Read
  - Write
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '6'
  raise.frequency: per-bug
  raise.gate: ''
  raise.next: bugfix-close
  raise.prerequisites: bugfix-fix
  raise.skillset: raise-maintainability
  raise.version: 2.4.0
  raise.visibility: internal
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - scope_md: file_path, required, from_previous
  raise.outputs: |
    - retro_md: file_path, next_skill
---

# Bugfix Review

## Purpose

Verify the fix addresses root cause, extract process improvements and causal patterns, and produce the retrospective artifact. This is where bugs become organizational learning.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, answer every checkpoint question, add patterns
- **Ha**: Skip checkpoint for trivial fixes; focus patterns on novel insights
- **Ri**: Feed systemic findings to graph; cross-bug pattern analysis

## Context

**When to use:** After `/rai-bugfix-fix` has completed all planned tasks with passing gates.

**When to skip:** Never — even trivial fixes produce learnings. Skipping review is the #1 step-skipping failure mode.

**Inputs:** Bug ID, all prior artifacts (`scope.md`, `analysis.md`, `plan.md`), code commits.

**Expected state:** On bug branch. All tasks committed. All gates pass. Bug no longer reproduces.

## Steps

### Step 1: Verify Fix Quality

Verify:
- Fix addresses root cause (not symptom) — compare with `analysis.md`
- Regression test is green
- No regressions introduced

<verification>
Fix verified against root cause. All gates green.
</verification>

### Step 2: Heutagogical Checkpoint

Answer with specific examples:
1. What did you learn about this system or codebase?
2. What would you change about the fix process?
3. Are there improvements for the framework (skill, guardrail, template)?
4. What are you more capable of now?

### Step 3: Extract Patterns & Process Improvements

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

### Step 4: Write Retrospective

Write `work/bugs/RAISE-{N}/retro.md`:

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

Commit:

```bash
git add work/bugs/RAISE-{N}/retro.md
git commit -m "bug(RAISE-{N}): review — retro and patterns

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Retro written. Checkpoint answered. Patterns added/reinforced.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Retrospective | `work/bugs/RAISE-{N}/retro.md` |
| Patterns | via `rai pattern add` CLI |
| Next | `/rai-bugfix-close` |

## Quality Checklist

- [ ] Fix verified against root cause (not symptom)
- [ ] Heutagogical checkpoint answered with specifics
- [ ] Process improvement extracted with prevention + pattern
- [ ] Patterns added with `--scope project` if applicable
- [ ] Retro artifact committed
- [ ] NEVER merge without retro — learnings compound
- [ ] NEVER skip pattern reinforce — scoring system depends on it

## References

- Previous: `/rai-bugfix-fix`
- Next: `/rai-bugfix-close`
