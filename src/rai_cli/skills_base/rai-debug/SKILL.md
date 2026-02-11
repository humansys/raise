---
name: rai-debug
description: >
  Systematic root cause analysis using lean methods (5 Whys, Ishikawa, Gemba).
  Use when encountering unexpected behavior, errors, or defects to find and
  fix the true root cause rather than symptoms.

license: MIT

metadata:
  raise.work_cycle: tools
  raise.frequency: as-needed
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
---

# Debug: Root Cause Analysis

## Purpose

Systematically identify and fix the root cause of defects, errors, or unexpected behavior using lean problem-solving methods. **Stop fixing symptoms - find the true cause.**

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow the 5 Whys method strictly; document each step.

**Ha (破)**: Combine methods (Ishikawa + 5 Whys); adapt depth to problem complexity.

**Ri (離)**: Develop domain-specific diagnostic patterns; teach others the methods.

## Context

**When to use:**
- Unexpected behavior or errors
- Test failures with unclear cause
- Integration issues
- Performance problems
- "It works on my machine" situations

**When NOT to use:**
- Obvious typos or simple syntax errors
- Well-documented known issues
- Feature requests (use `/rai-story-plan` instead)

**Inputs required:**
- Clear problem statement
- Steps to reproduce (if available)
- Error messages or symptoms

**Output:**
- Root cause identified
- Fix implemented or documented
- Prevention measures (optional)

## Methods Overview

| Method | Use When | Depth |
|--------|----------|-------|
| **5 Whys** | Single causal chain | Quick (5-10 min) |
| **Ishikawa** | Multiple possible causes | Medium (15-30 min) |
| **Gemba** | Need to observe actual behavior | Variable |
| **A3** | Complex problems requiring documentation | Deep (30+ min) |

## Steps

### Step 1: Define the Problem (Genchi Genbutsu)

**Go see the actual problem.** Don't rely on descriptions.

1. **Reproduce the issue** - Can you make it happen?
2. **Capture evidence** - Error messages, logs, screenshots
3. **Write problem statement** - One sentence, specific, observable

**Problem Statement Template:**
```
WHAT is happening: [specific behavior]
WHEN it happens: [conditions/triggers]
WHERE it occurs: [location in code/system]
EXPECTED behavior: [what should happen]
```

**Verification:** Problem statement is specific and reproducible.

> **If you can't continue:** Cannot reproduce → Gather more information, check logs.

### Step 2: Apply 5 Whys

Ask "Why?" five times to drill down to root cause.

**Rules:**
- Each answer must be factual, not speculative
- Stay on one causal chain (don't branch)
- Stop when you reach something you can change
- "Human error" is never a root cause - ask why the error was possible

**Template:**
```markdown
## 5 Whys Analysis

**Problem:** [Problem statement]

1. **Why?** [First-level cause]
   → Because: [Evidence/observation]

2. **Why?** [Second-level cause]
   → Because: [Evidence/observation]

3. **Why?** [Third-level cause]
   → Because: [Evidence/observation]

4. **Why?** [Fourth-level cause]
   → Because: [Evidence/observation]

5. **Why?** [Root cause]
   → Because: [Evidence/observation]

**Root Cause:** [Summary]
**Countermeasure:** [Fix]
```

**Verification:** Root cause is actionable and explains all symptoms.

> **If you can't continue:** Chain branches → Use Ishikawa for multiple causes.

### Step 3: Ishikawa Diagram (If Needed)

For problems with multiple potential causes, use the fishbone diagram.

**Categories (6 M's for software):**

```
                    ┌─── Method (process, algorithm)
                    │
                    ├─── Machine (hardware, infrastructure)
                    │
                    ├─── Material (data, inputs, dependencies)
PROBLEM ◄───────────┤
                    ├─── Measurement (metrics, monitoring)
                    │
                    ├─── Manpower (skills, knowledge gaps)
                    │
                    └─── Milieu (environment, configuration)
```

**For each category, list potential causes:**

```markdown
## Ishikawa Analysis

**Problem:** [Problem statement]

### Method
- [ ] Algorithm logic error
- [ ] Missing edge case handling
- [ ] Incorrect sequence of operations

### Machine
- [ ] Resource constraints (memory, CPU)
- [ ] Platform-specific behavior
- [ ] Network issues

### Material
- [ ] Invalid input data
- [ ] Dependency version mismatch
- [ ] Missing configuration

### Measurement
- [ ] Inadequate error messages
- [ ] Missing logs at failure point
- [ ] Incorrect assertions in tests

### Manpower
- [ ] Documentation gap
- [ ] Unclear requirements
- [ ] Knowledge not shared

### Milieu
- [ ] Environment variable missing
- [ ] Different dev vs prod config
- [ ] File path differences

**Most Likely Causes:** [Top 2-3]
**Investigation Order:** [Priority]
```

**Verification:** At least 3 categories explored; most likely causes identified.

> **If you can't continue:** All causes eliminated → Broaden investigation scope.

### Step 4: Investigate and Verify

Test hypotheses systematically.

1. **Start with most likely cause**
2. **Design minimal test** - How to confirm/refute?
3. **Execute test** - Gather evidence
4. **Document result** - Confirmed or eliminated?

**Investigation Log:**
```markdown
## Investigation Log

| Hypothesis | Test | Result | Conclusion |
|------------|------|--------|------------|
| [Cause 1] | [How tested] | [What happened] | Confirmed/Eliminated |
| [Cause 2] | [How tested] | [What happened] | Confirmed/Eliminated |
```

**Verification:** Root cause confirmed with evidence.

> **If you can't continue:** No hypothesis confirmed → Return to Step 3, add categories.

### Step 5: Implement Fix

Fix the root cause, not symptoms.

**Fix Checklist:**
- [ ] Fix addresses root cause (from Step 2/4)
- [ ] Fix doesn't introduce new issues
- [ ] Original problem no longer reproduces
- [ ] Related edge cases considered

**Verification:** Problem no longer occurs; tests pass.

> **If you can't continue:** Fix incomplete → Document partial fix, create follow-up task.

### Step 6: Prevent Recurrence (Optional)

For significant issues, add prevention measures.

**Prevention Options:**
- **Test:** Add regression test covering this case
- **Validation:** Add input validation or type check
- **Documentation:** Document gotcha or common mistake
- **Tooling:** Add lint rule or pre-commit hook
- **Process:** Update checklist or review criteria

**Verification:** Prevention measure in place.

## Output

- **Artifact:** `work/debug/{issue-name}/analysis.md` (optional, for complex issues)
- **Fix:** Implemented code changes
- **Prevention:** Test, validation, or documentation (optional)

## Quick Reference

### 5 Whys Shortcuts

| Symptom Pattern | Common Root Causes |
|-----------------|-------------------|
| "Works locally, fails in CI" | Environment config, path differences, missing deps |
| "Intermittent failure" | Race condition, external dependency, resource limit |
| "Broke after update" | Dependency change, API breaking change, config drift |
| "Only fails with certain data" | Edge case, encoding issue, type coercion |

### Red Flags (Stop and Think)

- "Let me just try this..." → Stop. Formulate hypothesis first.
- "It's probably X" → Test it. Don't assume.
- "I'll fix it later" → Jidoka. Fix now or document why not.
- "Nobody knows why it works" → Gemba. Understand before changing.

## Notes

### Jidoka Integration

This skill implements Jidoka principle: **Stop and fix quality issues immediately.**

When you detect a defect during any skill:
1. Stop the current work
2. Invoke `/rai-debug` to find root cause
3. Fix the root cause
4. Resume original work

### Time Boxing

| Problem Complexity | Max Investigation Time |
|-------------------|----------------------|
| Simple (single component) | 15 minutes |
| Medium (multiple components) | 30 minutes |
| Complex (system-wide) | 60 minutes |

If exceeding time box, document findings and escalate.

## References

- **5 Whys:** Taiichi Ohno, Toyota Production System
- **Ishikawa Diagram:** Kaoru Ishikawa, "Guide to Quality Control"
- **Gemba:** "Go and see" - observe actual work
- **A3 Thinking:** Toyota problem-solving methodology
- **Jidoka:** Automation with human intelligence - stop on defects
