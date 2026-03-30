---
title: Your First Story
description: Walk through the complete story lifecycle — from scope to merged code — using RaiSE skills.
---

This guide walks you through the full story lifecycle using RaiSE skills. By the end, you'll have experienced the rhythm that makes AI-assisted engineering reliable and repeatable.

## Before You Start

Make sure you have:
- A [RaiSE project initialized](../getting-started.md/
- An AI assistant with RaiSE skills loaded (Claude Code recommended)
- A small feature to build (something you can finish in one session)

Start a session by invoking the skill in your AI assistant:

```
/rai-session-start
```

This loads your context, memory, patterns, and proposes focused work. You work **through skills** — RaiSE skills orchestrate the CLI commands for you.

## Step 1: Start the Story

Every story begins with `/rai-story-start`. This creates a branch and documents what you're building.

```
/rai-story-start S1.1 Add user greeting
```

Your AI will:
1. Create a story branch (`story/s1.1/add-user-greeting`)
2. Write a scope document with in/out criteria
3. Create the scope commit

The scope document captures what's **in scope**, what's **out of scope**, and what **done** looks like. This prevents scope creep — a feature that was "just a greeting" doesn't become an authentication system.

## Step 2: Design the Specification

Next, `/rai-story-design` creates a lean specification.

```
/rai-story-design S1.1 Add user greeting
```

Your AI will:
1. Assess complexity (simple, moderate, complex)
2. Frame the problem and value
3. Describe the approach
4. Write concrete examples
5. Define acceptance criteria

The design document is optimized for both human review and AI implementation. The examples are the most important part — concrete, runnable examples tell the AI exactly what to build.

For simple features, you can skip design and go directly to planning.

## Step 3: Plan the Implementation

`/rai-story-plan` decomposes the story into atomic tasks.

```
/rai-story-plan S1.1 Add user greeting
```

Your AI will:
1. Break the feature into small, independent tasks
2. Define verification criteria for each task
3. Map dependencies between tasks
4. Set execution order

Each task should be individually committable and verifiable. The plan includes a TDD cycle: write a failing test (RED), make it pass (GREEN), clean up (REFACTOR).

## Step 4: Implement

`/rai-story-implement` executes the plan task by task.

```
/rai-story-implement S1.1 Add user greeting
```

Your AI will:
1. Pick the next task from the plan
2. Write the failing test
3. Implement the minimal code to pass
4. Verify (tests, linting, type checks)
5. Commit
6. Pause for your review (HITL checkpoint)
7. Repeat until all tasks complete

The key rhythm here: **implement → verify → commit → pause**. After each task, your AI stops and shows you what was done. You review, approve, and it moves to the next task.

## Step 5: Review

After implementation, `/rai-story-review` captures learnings.

```
/rai-story-review S1.1 Add user greeting
```

Your AI will:
1. Gather data: actual time vs. estimated, deviations from plan
2. Answer four heutagogical questions:
   - What did you learn?
   - What would you change about the process?
   - Are there improvements for the framework?
   - What are you more capable of now?
3. Identify process improvements
4. Persist valuable patterns to memory

This is where memory compounds. A pattern learned here shows up in future sessions.

## Step 6: Close

Finally, `/rai-story-close` merges and cleans up.

```
/rai-story-close S1.1 Add user greeting
```

Your AI will:
1. Verify all done criteria are met
2. Merge the story branch to the epic (or development) branch
3. Delete the story branch
4. Update tracking

## The Rhythm

After a few stories, the rhythm becomes natural:

```
scope → design → plan → build → reflect → close
```

Each step produces an artifact. Each artifact feeds the next step. The retrospective feeds memory, which feeds future sessions. This is how RaiSE compounds learning — not through magic, but through disciplined repetition.

## Skills vs CLI

In RaiSE, you interact through **skills** (slash commands in your AI assistant), not CLI commands directly:

- **Skills** (`/rai-story-start`, `/rai-session-close`) — what you invoke. They orchestrate the full workflow.
- **CLI** (`rai graph build`, `rai gate check`) — the deterministic backend. Skills call these for you.
- **Some CLI is direct** — setup commands like `rai init`, `rai doctor`, and `rai skill list` are used directly.

You can also run the entire story lifecycle in one command with `/rai-story-run S1.1`, which chains all 8 phases automatically.

## Tips

- **Start small.** Your first story should be XS or S sized. Get the rhythm first, then scale up.
- **Don't skip review.** The retrospective is where learning happens. It's tempting to skip when you're excited to start the next feature — resist that impulse.
- **Trust the gates.** Verification gates exist for a reason. When a gate fails, fix the issue before proceeding.
- **Commit after each task.** Not at the end of the story. Each task gets its own commit. This creates a clean history and makes debugging easier.
