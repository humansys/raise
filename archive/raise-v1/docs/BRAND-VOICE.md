# RaiSE Brand Voice Guide

**Version**: 1.0.0
**Date**: 2026-01-16
**Status**: Active
**Applies to**: All public documentation, README, guides, katas, and external communications

---

## Core Identity

**RaiSE** (Reliable AI Software Engineering) is a framework that empowers developers to orchestrate AI-assisted software development with confidence and control.

### Tagline

> "You orchestrate. AI assists. Quality emerges."

### One-Liner

> The conceptual foundation for reliable AI-assisted software engineering.

---

## Voice Principles

### 1. Empowering, Not Prescriptive

RaiSE follows **Heutagogy** (self-directed learning). We provide frameworks and patterns; you decide how to apply them.

| Do ✅ | Don't ❌ |
|------|---------|
| "You define the validation criteria" | "You must define validation criteria" |
| "Consider using a Guardrail when..." | "Always use a Guardrail for..." |
| "This kata helps you practice..." | "This kata teaches you how to..." |

### 2. Precise and Unambiguous

Every term has a specific meaning in RaiSE. Use canonical terminology consistently.

| Do ✅ | Don't ❌ |
|------|---------|
| "Validation Gate" | "DoD", "Definition of Done", "checklist" |
| "Guardrail" | "Rule", "constraint", "guideline" |
| "Orquestador" | "Developer", "user", "programmer" |
| "Principle / Flow / Pattern / Technique" | "L0 / L1 / L2 / L3", "levels" |

### 3. Concise and Direct

Follow **Principle IV: Simplicity**. Cover 80% of cases. Avoid over-documentation.

| Do ✅ | Don't ❌ |
|------|---------|
| One clear sentence | Three sentences saying the same thing |
| "Run the validation" | "You should proceed to run the validation process" |
| Active voice | Passive voice |

### 4. Professional but Accessible

Technical without being intimidating. Assume competence, explain RaiSE-specific concepts.

| Do ✅ | Don't ❌ |
|------|---------|
| "When implementing a feature..." | "For beginners who are new to coding..." |
| "Katas are structured exercises for deliberate practice" | "APIs are application programming interfaces" |
| "The Orquestador (human director) guides the AI" | Complex jargon without context |

### 5. Action-Oriented

Focus on what users can do, not abstract theory.

| Do ✅ | Don't ❌ |
|------|---------|
| "Start with the Discovery kata" | "The Discovery phase is important" |
| "Define your Guardrails in YAML" | "Guardrails can be defined in various formats" |
| Clear steps and examples | Lengthy theoretical explanations |

---

## Tone Spectrum

```
Casual ←――――――――●――――――――→ Formal
              RaiSE
        (Professional, Clear)
```

RaiSE sits in the **professional-clear** zone:
- Not stiff or academic
- Not casual or chatty
- Confident without arrogance
- Helpful without hand-holding

---

## Canonical Terminology (v2.1)

These terms have specific meanings in RaiSE. Always use them consistently.

| Term | Definition | Never Use |
|------|------------|-----------|
| **Orquestador** | The human who directs AI-assisted development | Developer, user, programmer |
| **Validation Gate** | Quality checkpoint at each phase | DoD, Definition of Done |
| **Guardrail** | Constraint that guides AI behavior | Rule, guideline |
| **Kata** | Structured exercise for deliberate practice | Tutorial, lesson |
| **Principle** | Foundational "why" and "when" (kata level) | L0 |
| **Flow** | Phase-based "how it flows" (kata level) | L1 |
| **Pattern** | Reusable "what shape" (kata level) | L2 |
| **Technique** | Specific "how to do" (kata level) | L3 |
| **Constitution** | Core principles document | Manifesto, rules |
| **Golden Data** | Authoritative source of truth | Master data |

---

## Writing Patterns

### Headings

Use clear, action-oriented headings:

```markdown
# Getting Started                    ✅
# Introduction to Getting Started    ❌

## Define Your Validation Gates      ✅
## About Validation Gates            ❌

### Run the Discovery Kata           ✅
### How to Run the Discovery Kata    ❌
```

### Instructions

Use imperative mood, numbered steps:

```markdown
1. Clone the repository
2. Navigate to `docs/core/`
3. Read the Constitution first
4. Explore the Glossary for terminology
```

### Explanations

Lead with the "what", follow with the "why":

```markdown
✅ "Guardrails constrain AI behavior to prevent common errors.
    Define them early in your project setup."

❌ "In software development, it's important to have constraints.
    These constraints, which we call Guardrails, help prevent errors..."
```

### Links

Use descriptive link text:

```markdown
✅ See the [Glossary](docs/core/glossary.md) for terminology
❌ Click [here](docs/core/glossary.md) for the glossary
```

---

## Audience

### Primary: Technical Practitioners

- Software developers
- Tech leads
- Engineering managers
- AI/ML practitioners exploring human-AI collaboration

### Assumptions

- Comfortable with Git, Markdown, CLI tools
- Familiar with software development lifecycle
- New to RaiSE methodology (needs onboarding)
- Evaluating frameworks for AI-assisted development

### What They Want

- Quick understanding of RaiSE value proposition
- Clear paths to get started
- Practical examples, not just theory
- Reference material they can return to

---

## Content Types

### README (Entry Point)

- **Purpose**: First impression, orientation
- **Tone**: Welcoming, confident, concise
- **Length**: Scannable in 2 minutes
- **Focus**: What is RaiSE, why it matters, where to start

### Katas (Exercises)

- **Purpose**: Guided practice
- **Tone**: Instructive, encouraging
- **Length**: Complete but focused
- **Focus**: Steps, verification, practical application

### ADRs (Decisions)

- **Purpose**: Document architectural choices
- **Tone**: Objective, analytical
- **Length**: As needed for clarity
- **Focus**: Context, decision, consequences

### Glossary (Reference)

- **Purpose**: Canonical definitions
- **Tone**: Precise, authoritative
- **Length**: Concise definitions
- **Focus**: Clarity, consistency

### Templates (Tools)

- **Purpose**: Reusable starting points
- **Tone**: Neutral, instructive
- **Length**: Minimal scaffolding
- **Focus**: Structure, placeholders, guidance comments

---

## Examples

### Good README Opening

```markdown
# RaiSE Commons

The conceptual foundation for reliable AI-assisted software engineering.

## What is RaiSE?

RaiSE is a framework for building software with AI assistance. You remain
in control as the Orquestador—defining requirements, setting Guardrails,
and validating outputs at every phase.

This repository contains the methodology, terminology, and exercises that
define how RaiSE works. It's not code; it's the "why" and "how" behind
effective human-AI collaboration.
```

### Good Kata Introduction

```markdown
# Discovery Kata

Transform stakeholder conversations into a validated Product Requirements
Document (PRD).

## When to Use

- Starting a new project
- Beginning a major feature
- After initial stakeholder meetings

## What You'll Produce

A complete PRD following the `templates/solution/project_requirements.md`
template, validated against the Discovery Validation Gate.
```

### Good Glossary Entry

```markdown
### Orquestador

The human who directs AI-assisted development. The Orquestador defines
requirements, establishes Guardrails, selects appropriate Katas, and
validates AI outputs against Validation Gates.

The term emphasizes that humans conduct and coordinate; AI assists and
executes within defined boundaries.

**See also**: Guardrail, Validation Gate
```

---

## Anti-Patterns

### Avoid These

1. **Marketing speak**: "Revolutionary", "game-changing", "next-generation"
2. **Hedging**: "Perhaps", "maybe", "it might be good to"
3. **Unnecessary words**: "In order to", "basically", "actually"
4. **Passive voice**: "The code is written" → "Write the code"
5. **Explaining basics**: Don't explain what Git or APIs are
6. **Wall of text**: Break up long paragraphs
7. **Vague instructions**: "Configure as needed" → Specify what to configure

---

## Language Standards

- **Dialect**: American English
- **Spelling**: American (color, analyze, organization)
- **Date format**: YYYY-MM-DD (ISO 8601)
- **Code style**: Follow repository conventions
- **Capitalization**:
  - RaiSE terms capitalized (Validation Gate, Guardrail, Orquestador)
  - General terms lowercase (framework, methodology, documentation)

---

## Review Checklist

Before publishing, verify:

- [ ] Uses canonical terminology (no deprecated terms)
- [ ] Active voice throughout
- [ ] Concise (no unnecessary words)
- [ ] Action-oriented headings
- [ ] Clear next steps for the reader
- [ ] Links use descriptive text
- [ ] American English spelling
- [ ] Empowering tone (not prescriptive)

---

## References

- [Glossary](core/glossary.md) - Canonical terminology
- [Constitution](core/constitution.md) - Core principles
- [Methodology](core/methodology.md) - Framework approach

---

*Brand Voice Guide v1.0.0 | RaiSE Commons*
