# Katas

> Guided step-by-step workflows for reliable results

---

## What is a Kata?

A **kata** is a guided workflow that takes you from input to output through verified steps. The term comes from martial arts—a kata is a practiced sequence of movements.

In RaiSE, katas:
- Have clear inputs and outputs
- Break work into verified steps
- Include recovery guidance when stuck
- Produce consistent, quality results

## Anatomy of a Kata

Every kata follows the same structure:

```markdown
# Kata: {Name}

## Purpose
Why this kata exists, what problem it solves.

## Context
When to use this kata, prerequisites, inputs needed.

## Steps

### Step 1: {Action}
What to do in this step.

**Verification:** How to know this step is complete.

> **If you can't continue:** {Problem} → {Solution}

### Step 2: {Action}
...

## Output
What artifact(s) this kata produces.
```

## The Jidoka Pattern

Every step has a **verification** and **recovery path**:

```markdown
### Step 3: Define Success Metrics

Document measurable success criteria with target values.

**Verification:** Each goal has ≥1 metric with a numeric target.

> **If you can't continue:** Metrics unclear → Ask "How will we
> know we succeeded?" until you get numbers.
```

This is **Jidoka** — stop when something is wrong, don't proceed with defects.

## Kata Categories

Katas are organized by work cycle:

| Category | Purpose | Examples |
|----------|---------|----------|
| `setup/` | Onboarding and initialization | analyze, ecosystem, governance |
| `solution/` | Big picture definition | discovery, vision |
| `project/` | Initiative planning | discovery, design, backlog |
| `feature/` | Building features | design, stories, plan, implement |
| `meta/` | Katas about katas | validation, refinement |

## Using Katas

### With AI Assistants

Katas work naturally with AI coding assistants:

```
Human: Run the project/design kata for the auth system

AI: Starting project/design kata...

Step 1: Load Vision and Context
Loading governance/vision.md...
✓ Vision loaded

Step 2: Define System Context (C4 Level 1)
...
```

The kata guides the AI through each step with clear verification.

### As a Human

You can also follow katas manually:

1. Read the kata document
2. Execute each step
3. Verify before proceeding
4. Use recovery guidance when stuck

## ShuHaRi: Adapting Katas

RaiSE uses **ShuHaRi** for progressive mastery:

| Stage | Meaning | How to Use Katas |
|-------|---------|------------------|
| **Shu** (守) | Protect/Obey | Follow exactly as written |
| **Ha** (破) | Break/Detach | Adapt steps to your context |
| **Ri** (離) | Leave/Transcend | Create your own katas |

Start with Shu—follow katas exactly. As you gain experience, adapt them.

## Finding Katas

Katas live in `.raise/katas/`:

```
.raise/katas/
├── setup/
│   ├── analyze.md
│   ├── ecosystem.md
│   └── governance.md
├── solution/
│   ├── discovery.md
│   └── vision.md
├── project/
│   ├── discovery.md
│   ├── vision.md
│   ├── design.md
│   └── backlog.md
└── feature/
    ├── design.md
    ├── plan.md
    └── implement.md
```

---

## Key Takeaways

1. **Guided workflows** — Katas take you step by step
2. **Verified steps** — Each step has clear completion criteria
3. **Recovery paths** — Know what to do when stuck
4. **Progressive mastery** — Start strict, adapt with experience

---

*Next: [Gates](./gates.md) | Reference: [Kata Structure](../reference/)*
