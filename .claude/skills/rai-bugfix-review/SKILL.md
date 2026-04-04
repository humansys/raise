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
    - patterns: list, cli
  raise.aspects: introspection
  raise.introspection:
    phase: bugfix.review
    context_source: all bug artifacts
    affected_modules: []
    max_tier1_queries: 2
    max_jit_queries: 3
    tier1_queries:
      - "evaluation patterns for {affected_modules}"
      - "process patterns from recent bugs"
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

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: Read ALL previous bug learning records (bugfix-start, bugfix-triage, bugfix-analyse, bugfix-plan, bugfix-fix). This provides the aggregate view for the retrospective.
2. **Graph query**: Execute tier1 queries from this skill's metadata using `rai graph query`. If graph is unavailable, note in LEARN record and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Verify Fix Quality

Determine which test command to run using this priority chain:

1. **Check `.raise/manifest.yaml`** for `project.test_command` — if set, use directly
2. **Detect language** from `project.project_type` in manifest, or scan file extensions
3. **Map language to default** (see `/rai-bugfix-fix` Step 1 for the full table)

Verify:
- Fix addresses root cause (not symptom) — compare with `analysis.md`
- Regression test is green
- No regressions introduced

| Condition | Action |
|-----------|--------|
| Tests green | Continue |
| Tests failing | Fix first — review requires green tests |

<verification>
Fix verified against root cause. All gates green.
</verification>

### Step 2: Heutagogical Checkpoint

> **JIT**: Before reflecting, query graph for evaluation patterns in affected modules
> → `aspects/introspection.md § JIT Protocol`

Answer with specific examples:
1. What did you learn about this system or codebase?
2. What would you change about the fix process?
3. Are there improvements for the framework (skill, guardrail, template)?
4. What are you more capable of now?

<verification>
All four questions answered with specifics.
</verification>

### Step 3: Aggregate Learning Records

Read learning records produced during this bug's lifecycle:
- `.raise/rai/learnings/rai-bugfix-start/{work_id}/record.yaml`
- `.raise/rai/learnings/rai-bugfix-triage/{work_id}/record.yaml`
- `.raise/rai/learnings/rai-bugfix-analyse/{work_id}/record.yaml`
- `.raise/rai/learnings/rai-bugfix-plan/{work_id}/record.yaml`
- `.raise/rai/learnings/rai-bugfix-fix/{work_id}/record.yaml`

If any record is missing (silent node or execution gap), note it and continue — missing records are valid signal.

Produce aggregate summary with these metrics:

| Metric | Calculation | What it tells us |
|--------|-------------|-----------------|
| **Acceptance rate** | Patterns voted +1 / total patterns primed | Are PRIME queries returning useful context? |
| **Gap rate** | Total gaps / total JIT queries | Is the graph missing knowledge we need? |
| **Pattern utility** | Patterns +1 / (patterns +1 + patterns -1) | Are stored patterns helping or misleading? |

<verification>
Learning records read (or missing noted). Metrics calculated.
</verification>

### Step 4: Persist Patterns & Reinforce

> **JIT**: Before persisting patterns, query graph for existing patterns to avoid duplicates
> → `aspects/introspection.md § JIT Protocol`

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

<verification>
Patterns persisted. Behavioral patterns evaluated.
</verification>

### Step 5: Write Retrospective

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

### Learning Chain Summary
- Records found: {N}/5
- Acceptance rate: {value}
- Gap rate: {value}
- Pattern utility: {value}
- Notable gaps: {list or "none"}

### Patterns
- Added: {pattern IDs or "none"}
- Reinforced: {pattern IDs and votes, or "none evaluated"}
```

Commit:

```bash
git add work/bugs/RAISE-{N}/retro.md .raise/rai/learnings/
git commit -m "bug(RAISE-{N}): review — retro and patterns

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Retro written. Checkpoint answered. Patterns added/reinforced. Learning chain summarized.
</verification>

### Step 6: Emit Calibration Telemetry

```bash
rai signal emit-calibration RAISE-{N} --size {XS|S|M|L} --estimated {minutes} --actual {minutes}
```

This feeds the velocity tracking system for future estimation accuracy.

<verification>
Calibration event recorded (or skipped if CLI unavailable).
</verification>

## Output

| Item | Destination |
|------|-------------|
| Retrospective | `work/bugs/RAISE-{N}/retro.md` |
| Patterns | `.raise/rai/memory/patterns.jsonl` |
| Calibration | Via `rai signal emit-calibration` |
| Next | `/rai-bugfix-close` |

### LEARN (mandatory — do not skip)

After completing the final step, you MUST produce a learning record. Write to `.raise/rai/learnings/rai-bugfix-review/{work_id}/record.yaml`:

```yaml
skill: rai-bugfix-review
work_id: {work_id}
version: "2.4.0"
timestamp: {ISO 8601 UTC}
primed_patterns: [{list of pattern IDs from PRIME}]
tier1_queries: {count}
tier1_results: {count}
jit_queries: {count}
pattern_votes:
  {PATTERN_ID}: {vote: 1|0|-1, why: "reason"}
gaps:
  - "description of missing knowledge"
artifacts: [{list of files produced}]
commit: {current commit hash or null}
branch: {current branch}
downstream: {}
```

**Rules:** Every cognitive skill execution MUST produce this record. Missing records break the learning chain.

**Commit:** Stage and commit the learning record with the retrospective: `git add .raise/rai/learnings/`. Records that stay on disk without a commit are lost when the worktree is cleaned up.

## Quality Checklist

- [ ] Project language detected before running tests
- [ ] Fix verified against root cause (not symptom)
- [ ] Heutagogical checkpoint answered with specifics
- [ ] Learning records aggregated with metrics
- [ ] Process improvement extracted with prevention + pattern
- [ ] Patterns added with `--scope project` if applicable
- [ ] Behavioral patterns reinforced via `rai pattern reinforce`
- [ ] Calibration telemetry emitted
- [ ] Retro artifact committed
- [ ] NEVER merge without retro — learnings compound
- [ ] NEVER skip pattern reinforce — scoring system depends on it
- [ ] LEARN record written to `.raise/rai/learnings/rai-bugfix-review/{work_id}/record.yaml`

## References

- Previous: `/rai-bugfix-fix`
- Next: `/rai-bugfix-close`
- Pattern scoring: RAISE-170 (temporal decay + Wilson scorer)
