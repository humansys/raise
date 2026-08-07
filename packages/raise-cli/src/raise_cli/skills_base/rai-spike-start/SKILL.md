---
name: rai-spike-start
description: Initialize a time-boxed spike with scope artifact. Use to begin research or prototype work.
model: opus

allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(git:*)"

license: MIT

metadata:
  raise.work_cycle: spike
  raise.frequency: per-spike
  raise.fase: "1"
  raise.prerequisites: ""
  raise.next: rai-research
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - jira_key: string, optional, argument
    - spike_type: string, optional, default=research
  raise.outputs: |
    - scope_path: file_path, next_skill
raise.mastery:
  shu: "Explain spike types and timebox rationale"
  ha: "Present only non-obvious decisions"
  ri: "Tool call → one-line confirmation → next"
---

# Spike Start

## Purpose

Initialize a time-boxed spike — research or prototype. Creates the scope
artifact with the question to answer, timebox, expected deliverables, and
classification.

## Mastery Levels (ShuHaRi)

- **Shu**: Explain spike types, timebox rationale, and deliverables
- **Ha**: Present only non-obvious decisions
- **Ri**: Minimal output — scope created, "Go."

## Context

**When to use:** Starting a new spike (research or prototype).

**When to skip:** Continuing an existing spike (scope already exists).

**Inputs:** Jira key (optional), spike_type (research|prototype), topic description.

## Steps

### Step 1: Gather spike parameters

Determine from context or ask the developer:
- **Question/Hypothesis:** What are we trying to learn or validate?
- **Spike type:** `research` (evidence catalog) or `prototype` (throwaway PoC)
- **Timebox:** How long before we force a decision? (default: 4 hours)
- **Expected deliverables:** What artifacts will this produce?

### Step 2: Create scope artifact

Derive the slug from the topic (kebab-case, max 50 chars).

Create `work/spikes/SP-{slug}/scope.md` using the Write tool:

```markdown
# SP-{slug}: {title}

## Classification

- **Type:** {research|prototype}
- **Timebox:** {N hours}
- **Jira:** {KEY or "—"}

## Question

{What are we trying to learn or validate? 1-3 sentences.}

## Expected deliverables

- {deliverable 1}
- {deliverable 2}

## Decision

> Pending — to be filled by rai-spike-close.
```

### Step 3: Commit scope

```bash
git add work/spikes/SP-{slug}/
git commit -m "spike(SP-{slug}): initialize — {question summary}

Type: {research|prototype}
Timebox: {N}h
Jira: {KEY}

Co-Authored-By: Rai <rai@humansys.ai>"
```

### Step 4: Present

```
## Spike SP-{slug}
**Type:** {research|prototype} · **Timebox:** {N}h
**Question:** {1-line}
**Next:** /rai-research (research) or direct prototyping (prototype)
```

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Output

| Item | Destination |
|------|-------------|
| Scope artifact | `work/spikes/SP-{slug}/scope.md` |
| Scope commit | On current branch |
| Next | `/rai-research` (research spikes) or direct work (prototype spikes) |

## Quality Checklist

- [ ] Question is specific and answerable within the timebox
- [ ] Spike type (research/prototype) is explicit
- [ ] Timebox is defined (not open-ended)
- [ ] Expected deliverables are listed
- [ ] Scope committed to git

## References

- Next (research): `/rai-research`
- Close: `/rai-spike-close`
- Pipeline: `spike.yaml`
