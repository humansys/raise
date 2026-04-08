---
title: The RaiSE Methodology
description: Why AI coding needs methodology, how RaiSE works, and the principles behind reliable AI software engineering.
---

AI coding assistants are powerful. They're also unreliable.

They hallucinate APIs. They forget your conventions between sessions. They optimize for speed over correctness. They don't know when to stop. Left ungoverned, they produce code that *looks* right but subtly isn't — and the longer you work with them, the more technical debt accumulates invisibly.

RaiSE exists because we believe AI-assisted engineering can be **reliable** — but only with discipline.

## The core problem

Most AI coding tools treat the developer as a prompt writer and the AI as a code generator. The workflow looks like this:

```
Developer writes prompt → AI generates code → Developer reviews → Repeat
```

This works for small tasks. It falls apart for real projects because:

- **No memory.** Each session starts fresh. The AI doesn't remember what it learned yesterday.
- **No rules.** The AI follows general best practices, not *your* rules. Your naming conventions, architecture decisions, and quality standards exist only in your head.
- **No process.** There's no structured way to decompose work, verify results, or learn from mistakes. It's just prompt → generate → hope.
- **No accountability.** When things go wrong, there's no traceability. Why was this decision made? Who approved it? What was the original requirement?

RaiSE addresses all four.

## The Triad

RaiSE is built on a collaboration model we call the Triad:

```
    You (Strategy, Judgment, Ownership)
         │
         │ collaborates with
         ▼
      Rai (AI Partner — Execution + Memory)
         │
         │ governed by
         ▼
      RaiSE (Methodology + Toolkit)
```

**You** are the engineer. You define what to build, why it matters, and what quality looks like. You make judgment calls the AI can't make — prioritization, trade-offs, user empathy, business context. You own the outcome.

**Rai** is the AI partner. Not a generic assistant — a collaborator trained in the discipline of RaiSE. Rai executes with accumulated memory, follows your governance rules, and stops when something doesn't look right (rather than generating more code and hoping you'll catch the error).

**RaiSE** is the methodology and toolkit. It provides the structure — skills that define how to work, governance that defines the rules, memory that persists across sessions, and quality gates that catch defects early.

None of the three is sufficient alone. You without Rai is slow. Rai without RaiSE is unreliable. RaiSE without you has no judgment. Together, they produce something none can achieve independently: **AI speed with human reliability**.

## Principles

RaiSE borrows from Lean Manufacturing — specifically from the Toyota Production System. These aren't metaphors; they're direct applications.

### Jidoka: Stop on defects

In Toyota factories, any worker can pull the cord to stop the production line when they spot a defect. The principle: **it's cheaper to stop and fix now than to let a defect propagate.**

In RaiSE, this means:
- Verification gates at every step. If tests fail, you don't proceed.
- Rai stops when it detects incoherence, ambiguity, or drift — rather than generating more output.
- Quality is built in, not inspected after.

### Kaizen: Continuous improvement

Every story ends with a retrospective. Every retrospective produces at least one concrete improvement. Patterns get captured in memory. Memory feeds future sessions.

This isn't just process — it's a **compounding effect**. Session 1 is slow because you're discovering everything. Session 50 is fast because patterns, calibration data, and governance have accumulated. The system gets better the more you use it.

### Poka-yoke: Mistake-proofing

Poka-yoke means designing systems so errors can't happen in the first place. In RaiSE:
- Story branches can't be created without an epic branch (the tooling prevents it).
- Implementation can't start without a plan (the skill checks for it).
- Merging can't happen without a retrospective (the gate requires it).

These aren't bureaucratic checkboxes. They're structural constraints that make the wrong thing hard to do.

### Humans define, machines execute

This is the fundamental separation. You write governance in natural language — Markdown files that express your principles, requirements, and guardrails. The CLI reads these deterministically. The AI interprets them in context. The machinery is transparent and inspectable.

You specify the *what*. RaiSE handles the *how*.

## The four pillars

### 1. Governance

Governance is a layered rule system that flows from abstract to concrete:

```
Principles (§)     →  "Why we do things this way"
     ↓
Requirements (RF)  →  "What we need to build"
     ↓
Guardrails (GR)    →  "What rules to follow"
     ↓
Code               →  "What we actually produce"
```

Each layer is traceable to the one above. When someone asks "why do we have this rule?" you can follow the chain: guardrail → requirement → principle. Nothing exists without justification.

Governance is loaded at session start and enforced throughout. It's not documentation that sits in a folder — it's active context that shapes every decision.

→ **[Read more about Governance](governance.md)**

### 2. Skills

Skills are process-as-code. Each skill is a structured workflow — a Markdown file — that guides both you and Rai through a specific engineering activity. Think of them as runbooks your AI follows, not just reads.

The most important skill chain is the **story lifecycle**:

```
/rai-story-start     → Scope and branch
/rai-story-design    → Lean specification
/rai-story-plan      → Atomic task decomposition
/rai-story-implement → TDD execution with verification gates
/rai-story-review    → Retrospective and pattern capture
/rai-story-close     → Merge and cleanup
```

Each step produces an artifact. Each artifact feeds the next. The whole chain is repeatable, verifiable, and traceable.

Skills also support mastery levels (Shu-Ha-Ri): beginners get detailed guidance, experts get minimal prompts. The same skill adapts to your experience.

→ **[Read more about Skills](skills.md)**

### 3. Memory

Memory is what makes the AI learn. Without it, every session starts from zero. With RaiSE memory, your AI carries forward:

- **Patterns** — learnings from development ("use fixtures for database tests", "commit after each task")
- **Calibration** — how long things actually take versus estimates (velocity tracking)
- **Sessions** — chronological record of what happened and what was accomplished

Memory lives in three scopes: **global** (all projects), **project** (shared via git), and **personal** (your private session history). It compounds over time — session 1 is discovery, session 50 is expertise.

→ **[Read more about Memory](memory.md)**

### 4. Knowledge Graph

The Knowledge Graph connects everything — governance, memory, skills, work tracking, and discovered code components — into a single queryable structure.

Nodes are concepts (patterns, principles, modules, stories). Edges are relationships (governed by, depends on, learned from). When the CLI assembles your session context, it traverses this graph to deliver exactly the right information for your current work.

This is how Rai knows which guardrails apply to which module, which patterns were learned in which story, and what the architectural constraints are for the code you're touching.

→ **[Read more about the Knowledge Graph](knowledge-graph.md)**

## How it all connects

Here's the full picture:

```
Governance files (Markdown)
     │
     ├── Parsed by CLI into Knowledge Graph
     │
     ├── Loaded at session start as governance primes
     │
     └── Enforced by skills via verification gates

Memory (JSONL + YAML)
     │
     ├── Patterns, calibration, sessions
     │
     ├── Merged into Knowledge Graph
     │
     └── Loaded at session start as behavioral primes

Skills (SKILL.md)
     │
     ├── Define the workflow (steps + gates)
     │
     ├── Reference governance (constraints)
     │
     └── Produce artifacts that feed memory

Session start
     │
     ├── CLI traverses the graph
     │
     ├── Assembles ~150 token context bundle
     │
     └── AI partner has full awareness
```

The cycle is: **govern → work → learn → compound**. Governance defines the rules. Skills structure the work. Memory captures what happened. The next session starts smarter than the last.

## What RaiSE is not

- **Not a code generator.** RaiSE doesn't write code for you. It structures how you and your AI partner write code together.
- **Not platform-specific.** It works where Git works. No GitHub, GitLab, or Bitbucket dependency.
- **Not heavyweight.** The governance files are Markdown. The memory is JSONL. The skills are Markdown. Everything is human-readable, diffable, and version-controlled.
- **Not magic.** The compounding effect is real but gradual. Session 1 is slower than vibe coding. Session 50 is faster and more reliable. You're investing in a system, not getting a shortcut.

## Next steps

- **[Getting Started](../getting-started.md)** — Install and run your first session
- **[Your First Story](../guides/first-story.md)** — Experience the full story lifecycle
- **[CLI Reference](../cli/index.md)** — Every command, flag, and option
