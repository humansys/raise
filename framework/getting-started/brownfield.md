# Brownfield Adoption Guide

> Adopting RaiSE in an existing project

---

## Overview

Brownfield adoption is about **incrementally adding governance** to an existing codebase without disrupting ongoing work. You don't need to stop everything—RaiSE layers on top.

## Phase 1: Analysis (Day 1)

### Step 1: Initialize RaiSE Structure

Create the three-directory structure:

```bash
mkdir -p .raise governance work
```

### Step 2: Run Codebase Analysis

Use the `setup/analyze` kata to understand your current codebase:

```
# With Claude Code or similar
/raise.analyze
```

This produces:
- Architecture overview
- Dependency map
- Code quality assessment
- Technical debt inventory

### Step 3: Document Current State

Create `governance/current-state.md`:
- What exists today
- Known issues
- Key stakeholders

---

## Phase 2: Governance Foundation (Week 1)

### Step 4: Establish Guardrails

Use the `setup/governance` kata to define initial guardrails:

```
/raise.governance
```

This creates `governance/guardrails.md` with:
- Coding standards to enforce
- Review requirements
- Quality thresholds

### Step 5: Map Ecosystem

Use the `setup/ecosystem` kata to document integrations:

```
/raise.ecosystem
```

---

## Phase 3: First Governed Work (Week 2+)

### Step 6: Pick a Small Feature

Choose a low-risk feature for your first fully-governed work:
- New functionality (not refactoring)
- Clear scope
- 1-2 week timeline

### Step 7: Run the Feature Cycle

Execute the story katas:

1. `feature/design` — Technical design
2. `feature/stories` — User stories with acceptance criteria
3. `feature/plan` — Implementation plan
4. `feature/implement` — Guided implementation
5. `feature/review` — Validation against gates

---

## What Success Looks Like

After brownfield adoption:

- ✅ Existing code continues to work
- ✅ New features follow governed workflow
- ✅ Guardrails catch issues early
- ✅ Documentation grows organically
- ✅ Team learns RaiSE incrementally

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Trying to govern everything at once | Start with new features only |
| Skipping analysis phase | Analysis informs realistic guardrails |
| Too strict initial guardrails | Start permissive, tighten with experience |

---

## Next Steps

1. Complete Phase 1 analysis
2. Review [Gates concept](../concepts/gates.md) before setting guardrails
3. Plan your first governed feature

---

*See also: [Greenfield Guide](./greenfield.md) | [Work Cycles](../concepts/work-cycles.md)*
