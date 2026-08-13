---
name: rai-bug-file
description: File a bug with diagnostic precision — repro, classification, root cause hypothesis, and Jira issue creation. Intake quality gate for the bugfix pipeline.
model: opus

allowed-tools:
  - Read
  - Bash
  - "Bash(git:*)"
  - "Bash(rai:*)"
  - "Bash(grep:*)"
  - "Bash(find:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.frequency: on-demand
  raise.gate: ''
  raise.next: ''
  raise.prerequisites: ''
  raise.skillset: raise-maintainability
  raise.version: 3.1.0
  raise.visibility: public
  raise.work_cycle: utility
  raise.inputs: |
    - observation: string, required, argument (what went wrong, where, how detected)
    - parent_epic: string, optional, argument (Jira epic key to link as parent)
  raise.outputs: |
    - jira_key: string, next_skill (the created issue key)
    - severity: string, informational
    - component: string, informational
---

# Bug File

## Purpose

Capture a bug with diagnostic precision and create a well-structured Jira issue so the bugfix pipeline starts with high-quality information. This is the intake quality gate: the difference between a vague "X is broken" and an actionable report with repro, classification, root cause hypothesis, and affected component.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps; ask for clarification on each dimension
- **Ha**: Infer classification from observation; confirm before filing
- **Ri**: File from observation in a single pass; classify and create atomically

## Context

**When to use:** A bug is detected (dogfooding, code review, production, spike, testing) and needs to be captured as a Jira issue before starting the bugfix pipeline.

**When to skip:** Bug already exists in Jira with sufficient detail. Trivial typo fix that needs no tracking.

**Inputs:** The observation (what went wrong), optionally a parent epic key.

## Steps

### Step 1: Investigate and Reproduce

From the observation, locate the defect in the codebase:

1. **Find the code** — grep/read the relevant files to confirm the defect exists.
2. **Reproduce or confirm** — if the bug is behavioral, reproduce it. If it is structural (wrong code path, missing guard, wrong contract), confirm by reading the code and tracing the failure path.
3. **Identify the component** — which package/module/file is affected.

<verification>
Defect confirmed in code. Component identified. Reproduction path documented (or structural confirmation with file:line references).
</verification>

### Step 2: Classify (4 Dimensions)

Classify the bug using the ODC-inspired taxonomy (same as `rai-bugfix-triage`):

| Dimension | Values |
|-----------|--------|
| **Bug Type** | Functional, Interface, Data, Logic, Configuration, Regression |
| **Severity** | S0-Critical, S1-High, S2-Medium, S3-Low |
| **Origin** | Requirements, Design, Code, Integration, Environment |
| **Qualifier** | Missing, Incorrect, Extraneous |

### Step 3: Formulate Root Cause Hypothesis

Write a 2-3 sentence hypothesis of WHY the bug exists. This is not the full root cause analysis (that is `rai-bugfix-analyse`), but a directional hypothesis to guide the fixer:

- What mechanism failed or is missing?
- Why did the current code not prevent this?
- What is the likely fix direction?

### Step 4: Compose Description

Build the Jira issue description with this structure:

```
{observation — what was detected and how}

**Repro / Confirmation:**
{repro steps OR structural confirmation with file:line}

**Classification:**
- Bug Type: {value}
- Severity: {value}
- Origin: {value}
- Qualifier: {value}

**Root Cause Hypothesis:**
{2-3 sentences}

**Affected Component:** {package/module}
**Affected File(s):** {file:line references}

**Expected Behavior:**
{what should happen instead}

**Done when:** {specific observable outcome that proves the fix}
```

### Step 5: Create Jira Issue

```bash
rai backlog create "{summary}" \
  -p RAISE \
  -t Bug \
  -d "{description}" \
  -l rai-bug
```

If a parent epic was provided:

```bash
rai backlog update {new_key} -F customfield_10014={parent_epic}
```

Set custom fields if configured (same mapping as `rai-bugfix-triage`):

```bash
rai backlog update {new_key} \
  -F customfield_13267={Bug Type} \
  -F customfield_12090={Severity mapped: S0→Sev-0, S1→Sev-1, S2→Sev-2, S3→Sev-3} \
  -F customfield_13269={Origin — note: Environment→Enviroment (Jira typo)} \
  -F customfield_13270={Qualifier}
```

<verification>
Issue created in Jira with all fields populated. `rai backlog get {new_key}` confirms.
</verification>

<if-blocked>
Custom field update fails → log warning and continue. The issue exists; fields can be set later by `rai-bugfix-triage`.
</if-blocked>

## Output

| Item | Destination |
|------|-------------|
| Jira issue | RAISE project, type Bug |
| Classification | Jira custom fields (best-effort) |
| Report | Returned to caller: key, summary, severity, component |

**STOP HERE.** Return the created issue key, summary, severity, and component. Do NOT start the bugfix pipeline — that is a separate decision.

## Quality Checklist

- [ ] Defect confirmed in code (not just reported — verified)
- [ ] All 4 classification dimensions assigned
- [ ] Root cause hypothesis present (not "unknown")
- [ ] Done-when criterion is specific and observable
- [ ] Jira issue created with description following the template
- [ ] Parent epic linked (if provided)
- [ ] No pipeline started — filing only

## References

- Downstream: `/rai-bugfix-start` (consumes the filed issue)
- Classification model: `/rai-bugfix-triage` (same 4 dimensions)
- Backlog CLI: `rai backlog create --help`
