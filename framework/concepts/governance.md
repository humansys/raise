# Governance

> Why explicit rules matter in AI-assisted development

---

## The Problem

AI coding assistants are powerful but unpredictable. Without explicit guidance:

- Different prompts produce inconsistent results
- Quality varies based on context
- Decisions aren't documented
- Knowledge leaves with team members
- Compliance becomes impossible to verify

## The Solution: Explicit Governance

RaiSE makes governance **explicit** and **versioned**:

```
Traditional Development          RaiSE Development
─────────────────────────        ─────────────────────────
"We usually do X"           →    guardrails.md says "MUST do X"
"Ask Sarah, she knows"      →    decision documented in ADR
"It depends on context"     →    kata provides context-aware guidance
"Trust the senior dev"      →    gate validates against criteria
```

## Governance as Code

In RaiSE, governance artifacts are **code**:

- Stored in Git
- Version controlled
- Reviewable via PRs
- Traceable over time

This means governance:
- Survives team changes
- Can be audited
- Evolves deliberately
- Is the same for humans and AI

## The Three Levels

RaiSE governance operates at three levels:

### 1. Solution Level
Governance for the entire system/product.

```
governance/
├── vision.md          # What we're building
├── guardrails.md      # Rules for all work
└── business_case.md   # Why we're building it
```

### 2. Project Level
Governance for specific initiatives.

```
governance/
├── prd.md             # Requirements
├── design.md          # Technical approach
└── backlog.md         # Planned work
```

### 3. Feature Level
Governance for individual features (in `work/`).

```
work/stories/{name}/
├── spec.md            # What to build
├── plan.md            # How to build it
└── tasks.md           # Step by step
```

## Guardrails

Guardrails are governance rules with explicit severity:

| Level | Meaning | Example |
|-------|---------|---------|
| **MUST** | Gate-blocking, required | "MUST have unit tests" |
| **SHOULD** | Expected, deviation needs justification | "SHOULD use TypeScript" |
| **MAY** | Optional, team discretion | "MAY use feature flags" |

Example guardrail:

```markdown
### GR-001: Test Coverage

**Level:** MUST
**Scope:** All production code

All production code MUST have ≥80% test coverage.
Exceptions require Tech Lead approval documented in PR.
```

## Why This Matters for AI

AI assistants follow instructions literally. Explicit governance means:

1. **Consistent behavior** — Same rules, same results
2. **Verifiable compliance** — Gates can check against guardrails
3. **Teachable context** — AI can read governance docs
4. **Auditable decisions** — Everything in Git history

---

## Key Takeaways

1. **Implicit knowledge fails** — Make governance explicit
2. **Version your rules** — Governance as code in Git
3. **Three levels** — Solution → Project → Feature
4. **Guardrails guide** — MUST/SHOULD/MAY with clear criteria

---

*Next: [Work Cycles](./work-cycles.md) | Reference: [Constitution](../reference/constitution.md)*
