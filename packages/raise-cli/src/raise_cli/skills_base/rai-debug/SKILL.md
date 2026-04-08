---
name: rai-debug
description: Find root cause using 5 Whys, Ishikawa, Gemba. Use when encountering errors or defects.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Bash

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: as-needed
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: story-plan
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.1.0"
  raise.visibility: public
---

# Debug

## Purpose

Systematically identify and fix the root cause of defects using lean methods. Stop fixing symptoms — find the true cause.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow triage → method → fix strictly; document each step
- **Ha**: Combine methods (Ishikawa + 5 Whys); adapt depth to complexity
- **Ri**: Develop domain-specific diagnostic patterns; feed recurring patterns to graph

## Context

**When to use:** Unexpected behavior, unclear test failures, integration issues, performance problems, bug fix stories.

**When to skip:** Obvious typos, simple syntax errors — go directly to fix.

**Inputs:** Problem statement, steps to reproduce, error messages/symptoms. **Time boxing:** XS (5 min), S (15 min), M (30 min), L (60 min). Escalate if exceeded.

## Steps

### Step 0: Triage — Classify Complexity

Before choosing a method, classify the bug:

| Tier | Criteria | Method | Output |
|------|----------|--------|--------|
| **XS** | Cause evident, fix obvious | Skip to Step 3 | One-liner in scope/commit |
| **S** | Cause obscure, single causal chain | 5 Whys (Step 2) | Summary block |
| **M/L** | Multiple possible causes | Ishikawa (Step 2b) | `analysis.md` |

State the tier explicitly before proceeding.

<verification>
Tier declared. Method selected.
</verification>

### Step 1: Define the Problem (Genchi Genbutsu)

Go see the actual problem. Reproduce it, capture evidence:

```
WHAT:     [specific behavior observed]
WHEN:     [conditions / triggers]
WHERE:    [file:line or component]
EXPECTED: [what should happen instead]
```

<verification>
Problem is specific and reproducible (or minimal fixture built).
</verification>

<if-blocked>
Cannot reproduce → gather logs, add instrumentation, build minimal fixture.
</if-blocked>

### Step 2: Root Cause Analysis (S bugs — 5 Whys)

Ask "Why?" five times, staying on one factual causal chain:

```
Problem: [statement]
1. Why? → [first-level cause, with evidence]
2. Why? → [second-level cause]
3. Why? → [third-level cause]
4. Why? → [fourth-level cause]
5. Why? → [root cause]
Countermeasure: [fix]
```

Rules:
- Each answer must be factual, not speculative
- Stop when you reach something actionable and changeable
- "Human error" is never a root cause — ask why the error was possible

<verification>
Root cause is actionable and explains all symptoms.
</verification>

<if-blocked>
Chain branches → switch to Ishikawa (Step 2b).
</if-blocked>

### Step 2b: Ishikawa Diagram (M/L bugs — multiple causes)

Explore 6 M's: Method, Machine, Material, Measurement, Manpower, Milieu (env/config drift).

Identify top 2-3 hypotheses, investigate systematically:

| Hypothesis | Test | Result | Conclusion |
|------------|------|--------|------------|
| [Cause 1]  | [How tested] | [What happened] | Confirmed/Eliminated |

<verification>
Root cause confirmed with evidence. Competing hypotheses eliminated.
</verification>

### Step 3: Fix & Prevent

Fix the root cause (not symptoms). Write the regression test first (RED), then fix (GREEN).

- [ ] Fix addresses confirmed root cause
- [ ] Regression test written (RED → GREEN)
- [ ] Original problem no longer reproduces
- [ ] All existing tests pass

Prevention (choose what applies):
- Regression test (always for S+)
- Input validation at boundary
- Documentation or ADR update
- `rai pattern add` for recurring systemic issues

<verification>
Problem resolved. Tests pass.
</verification>

<if-blocked>
Fix incomplete → document partial fix, create follow-up task.
</if-blocked>

**Feed `/rai-story-plan`** — after fixing, name the tasks explicitly:
- Fix task, regression test task, prevention task (if any)
- Systemic finding: `rai pattern add "[statement]" --context "[keywords]" --type process`

## Output

| Tier | Artifact | Destination |
|------|----------|-------------|
| XS | One-liner root cause + fix | Scope commit or inline |
| S | Summary block (root cause, fix, prevention) | Story scope doc |
| M/L | Full analysis | `work/debug/{issue-name}/analysis.md` |
| Any | Story plan tasks | Fed to `/rai-story-plan` |

## Quality Checklist

- [ ] Tier declared before any analysis
- [ ] Problem is specific and reproducible
- [ ] Root cause identified with evidence (not speculation)
- [ ] Fix addresses root cause, not symptoms
- [ ] Regression test written (RED before GREEN)
- [ ] Time box respected — escalate if exceeded
- [ ] Story plan tasks named
- [ ] NEVER guess — hypothesis first, then test. NEVER say "human error" — ask why the error was possible

## References

- 5 Whys: Taiichi Ohno, Toyota Production System
- Ishikawa: Kaoru Ishikawa, "Guide to Quality Control"
- Gemba: "Go and see" — Jidoka: stop on defects, fix immediately
