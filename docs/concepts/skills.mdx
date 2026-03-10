---
title: Skills
description: Process-as-code — repeatable workflows that guide both human and AI through complex engineering tasks.
---

Skills are RaiSE's process-as-code. Each skill is a structured workflow — a `SKILL.md` file — that guides both you and your AI partner through a specific engineering activity. Think of them as runbooks that your AI can follow, not just read.

## What a Skill Looks Like

A skill is a markdown file in `.claude/skills/<name>/SKILL.md` with:

- **Purpose** — what this skill does and when to use it
- **Steps** — ordered sequence with verification gates at each step
- **Mastery levels** — Shu (follow exactly), Ha (adapt), Ri (create your own)
- **Inputs and outputs** — what it needs, what it produces

When you invoke a skill (e.g., `/rai-story-plan`), your AI loads the SKILL.md and follows its steps — checking prerequisites, executing each step, verifying results, and producing documented output.

## The Story Lifecycle

The most important skill chain is the story lifecycle — the sequence that takes a feature from idea to merged code:

```
/rai-story-start    → Create branch and scope commit
      ↓
/rai-story-design   → Design the specification
      ↓
/story-plan     → Decompose into atomic tasks
      ↓
/rai-story-implement → Execute tasks with TDD
      ↓
/rai-story-review   → Retrospective and learnings
      ↓
/rai-story-close    → Verify, merge, cleanup
```

Each step produces an artifact (scope.md, design.md, plan.md, progress.md, retrospective.md) and has verification gates that must pass before proceeding. This isn't bureaucracy — it's how you ensure consistency and traceability across sessions.

## Skill Lifecycles

Skills are organized by the work lifecycle they belong to:

| Lifecycle | Skills | When |
|-----------|--------|------|
| **Session** | `/rai-session-start`, `/rai-session-close` | Every working session |
| **Story** | `/rai-story-start` through `/rai-story-close` | For each feature |
| **Epic** | `/rai-epic-start` through `/rai-epic-close` | For multi-story bodies of work |
| **Discovery** | `/rai-discover-start` through `/rai-discover-document` | When analyzing a codebase |

## Skills vs. CLI

This distinction matters:

- **Skills** guide the *process* — they tell you and your AI what to do, in what order, with what verification
- **CLI** handles the *data* — it reads, writes, builds, and queries deterministically

A skill like `/rai-story-plan` tells the AI to decompose a story into tasks. The CLI command `rai signal emit-work` records the event. The skill orchestrates; the CLI executes.

## Mastery Levels (ShuHaRi)

Every skill supports three mastery levels, borrowed from martial arts:

- **Shu (守)** — Follow the form exactly. For new practitioners or new skill types.
- **Ha (破)** — Adapt the form. Skip optional steps, adjust to context. For experienced practitioners.
- **Ri (離)** — Transcend the form. Create custom patterns. For experts who understand the principles deeply enough to improvise.

Your experience level is tracked in your developer profile and included in the context bundle. At Shu level, skills provide detailed explanations. At Ri level, they show essentials only.

## Verification Gates

Every skill step has a verification criterion — a concrete check that the step was completed correctly. If verification fails, the skill stops (Jidoka principle: stop on defects, don't accumulate errors).

Examples of verification gates:
- "Epic branch exists" before creating a story branch
- "Plan exists" before starting implementation
- "Tests pass" before committing
- "Retrospective complete" before merging

## Managing Skills

```bash
# List all skills
rai skill list

# Validate skill structure
rai skill validate

# Create a new skill from template
rai skill scaffold my-new-skill --lifecycle story

# Check naming conventions
rai skill check-name my-new-skill
```

See the [CLI Reference](cli/README.md) for full details.
