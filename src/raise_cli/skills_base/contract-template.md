# Skill Contract Template (ADR-040)

> Reference for refactoring skills to canonical structure.
> Every SKILL.md follows exactly these 7 sections in this order.

## Targets

| Metric | Target |
|--------|--------|
| Sections | Exactly 7, fixed order |
| Total lines | ≤150 (excluding YAML frontmatter) |
| Discrete rules | ≤15 |
| Substance ratio | ≥80% |
| Examples | 1-2 per skill |
| Negative phrases | ≤3 (reserve for true guardrails in Quality Checklist) |

## Canonical Structure

```markdown
# {Skill Title}

## Purpose
One sentence: what this skill does and what success looks like.

## Mastery Levels (ShuHaRi)
≤5 lines. Behavior deltas SPECIFIC to this skill only.
Universal ShuHaRi definitions are in the preamble — do not repeat them.

## Context
When to use / when to skip. Inputs required. Prerequisites (gates).
Use decision tables for conditional logic, not prose paragraphs.

## Steps
### Step N: {Verb Phrase}
Follow the step format convention from the preamble:
- Action: what to do (affirmative phrasing)
- Verification: how to check success
- If blocked: recovery path

Steps use clean integer numbering (1, 2, 3 — no 0.1, 1.5, 4b).

## Output
What this skill produces. Where artifacts go. State changes. Next skill.

## Quality Checklist
Atomic, verifiable items. This is the last thing the agent reads before
finishing — recency bias means these get highest compliance.
Place critical guardrails here (≤3 negative "NEVER" items if needed).

## References
Links only — no inline content. File paths, ADRs, related skills.
```

## Content Principles

1. **Affirmative over negative** — "Do X when Y" instead of "Don't do X"
2. **Decision tables over prose** — Branching logic as tables, not if-else paragraphs
3. **Examples over rules** — One input/output example replaces 10+ lines of rules
4. **Atomic instructions** — Each rule is one verifiable statement
5. **Templates by reference** — Link to template files, don't inline them
