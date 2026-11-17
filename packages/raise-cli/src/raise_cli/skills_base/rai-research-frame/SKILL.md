---
name: rai-research-frame
description: Define research question, determine depth route, create work directory.
allowed-tools:
  - Read
  - Write
  - Bash
metadata:
  raise.work_cycle: research
  raise.frequency: per-research
  raise.version: "1.0.0"
  raise.visibility: public
---

# Research Frame

## Purpose

Define the research question with epistemological rigor and determine the depth route that controls which pipeline phases will run.

## Steps

### Step 1: Receive Question

Read the research question from the pipeline input or journal. Identify:
- **Primary question** — the specific, falsifiable question to answer
- **Secondary questions** — supporting questions that inform the primary
- **Decision context** — what decision this research informs (ADR, feature, strategy)
- **Stakeholders** — who will consume the output

### Step 2: Determine Depth

Evaluate based on decision stakes and domain familiarity:

| Signal | → Depth |
|--------|---------|
| Low-stakes, reversible, familiar domain | `quick` |
| ADR, technology evaluation, moderate stakes | `standard` |
| Strategic decision, unfamiliar domain, high stakes | `deep` |

If the user specified depth explicitly, honor it. Otherwise, recommend and note reasoning.

### Step 3: Create Work Directory

```bash
mkdir -p work/research/{topic}
```

### Step 4: Write Frame Document

Write `work/research/{topic}/frame.md`:

```markdown
# Research: {topic}

## Question
{primary question — specific and falsifiable}

## Secondary Questions
{numbered list}

## Decision Context
{what decision this informs}

## Depth: {quick|standard|deep}
Rationale: {why this depth}

## Expected Sources
| Depth | Target Sources | Phases |
|-------|---------------|--------|
| quick | 5-10 | Frame → Search → Synthesize |
| standard | 15-30 | + Scope + Evidence |
| deep | 50-100+ | + Verify + Critic |
```

### Step 5: Emit phase_result

```yaml
phase_result:
  status: done
  route: {quick|standard|deep}
  topic: {topic-slug}
  question: {primary question, one line}
  artifacts:
    - work/research/{topic}/frame.md
```

## Output

| Item | Destination |
|------|-------------|
| Frame document | `work/research/{topic}/frame.md` |
| Route | phase_result → orchestrator routes downstream phases |
