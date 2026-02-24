---
name: rai-debug
description: >
  Systematic root cause analysis using lean methods (5 Whys, Ishikawa, Gemba).
  Use when encountering unexpected behavior, errors, or defects to find and
  fix the true root cause rather than symptoms.

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
  raise.visibility: public
---

# Debug

## Purpose

Systematically identify and fix the root cause of defects using lean methods. Stop fixing symptoms — find the true cause.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow the 5 Whys method strictly; document each step
- **Ha**: Combine methods (Ishikawa + 5 Whys); adapt depth to complexity
- **Ri**: Develop domain-specific diagnostic patterns; teach methods

## Context

**When to use:** Unexpected behavior, unclear test failures, integration issues, performance problems.

**When to skip:** Obvious typos, simple syntax errors, well-documented known issues.

**Inputs:** Problem statement, steps to reproduce, error messages/symptoms.

**Method selection:**

| Method | Use when | Time |
|--------|----------|------|
| 5 Whys | Single causal chain | 5-10 min |
| Ishikawa (fishbone) | Multiple possible causes | 15-30 min |
| Gemba | Need to observe actual behavior | Variable |

**Time boxing:** Simple (15 min), Medium (30 min), Complex (60 min). Escalate if exceeded.

## Steps

### Step 1: Define the Problem (Genchi Genbutsu)

Go see the actual problem. Reproduce, capture evidence, write problem statement:

```
WHAT: [specific behavior]
WHEN: [conditions/triggers]
WHERE: [location in code/system]
EXPECTED: [what should happen]
```

<verification>
Problem is specific and reproducible.
</verification>

<if-blocked>
Cannot reproduce → gather more information, check logs.
</if-blocked>

### Step 2: Apply 5 Whys

Ask "Why?" five times, staying on one factual causal chain:

```markdown
**Problem:** [statement]
1. Why? → [first-level cause, with evidence]
2. Why? → [second-level cause]
3. Why? → [third-level cause]
4. Why? → [fourth-level cause]
5. Why? → [root cause]
**Countermeasure:** [fix]
```

Rules: each answer factual (not speculative), stop when you reach something changeable, "human error" is never a root cause.

<verification>
Root cause is actionable and explains all symptoms.
</verification>

<if-blocked>
Chain branches → switch to Ishikawa (Step 3).
</if-blocked>

### Step 3: Ishikawa Diagram (if needed)

For multiple possible causes, explore 6 M's: Method (algorithm, edge case), Machine (resources, platform), Material (input, deps, config), Measurement (errors, logs), Manpower (docs, requirements), Milieu (env, config drift).

Identify top 2-3 causes, investigate systematically:

| Hypothesis | Test | Result | Conclusion |
|------------|------|--------|------------|
| [Cause 1] | [How tested] | [What happened] | Confirmed/Eliminated |

<verification>
Root cause confirmed with evidence.
</verification>

### Step 4: Fix & Prevent

Fix the root cause (not symptoms):
- [ ] Fix addresses confirmed root cause
- [ ] Original problem no longer reproduces
- [ ] Tests pass

Optional prevention: regression test, input validation, documentation, lint rule, process update.

<verification>
Problem resolved. Tests pass.
</verification>

<if-blocked>
Fix incomplete → document partial fix, create follow-up task.
</if-blocked>

## Output

| Item | Destination |
|------|-------------|
| Analysis | `work/debug/{issue-name}/analysis.md` (complex issues only) |
| Fix | Implemented code changes |
| Prevention | Test, validation, or documentation (optional) |

## Quality Checklist

- [ ] Problem statement is specific and reproducible
- [ ] Root cause identified with evidence (not speculation)
- [ ] Fix addresses root cause, not symptoms
- [ ] Time box respected — escalate if exceeded
- [ ] NEVER guess — formulate hypothesis, then test it
- [ ] NEVER say "human error" — ask why the error was possible

## References

- 5 Whys: Taiichi Ohno, Toyota Production System
- Ishikawa: Kaoru Ishikawa, "Guide to Quality Control"
- Gemba: "Go and see" — observe actual work
- Jidoka: stop on defects, fix immediately
