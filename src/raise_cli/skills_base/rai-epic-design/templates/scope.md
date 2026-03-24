# Epic E{N}: {Epic Name} — Scope

> **Status:** IN PROGRESS
> **Release:** REL-{id} ({release name})
> **Created:** YYYY-MM-DD

## Objective

{1-2 sentences: What business/user outcome does this epic deliver?}

**Value:** {Why this matters, what's unlocked after completion}

## Stories ({X} SP estimated)

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S{N}.1 | {Name} | S | Pending | {1-line} |
| S{N}.2 | {Name} | M | Pending | {1-line} |

**Total:** {X} stories, {Y} SP

## Scope

**In scope (MUST):**
- {Non-negotiable 1}
- {Non-negotiable 2}

**In scope (SHOULD):**
- {Nice-to-have 1}

**Out of scope:**
- {Excluded 1} → {where deferred}

## Done Criteria

**Per story:**
- [ ] Code with type annotations
- [ ] Tests passing
- [ ] Quality checks pass (ruff, pyright)

**Epic complete:**
- [ ] All stories complete (S{N}.1–S{N}.X)
- [ ] {Epic-specific criterion 1}
- [ ] Epic retrospective done
- [ ] Merged to `{dev_branch}`

## Dependencies

```
S{N}.1 (foundation)
  ↓
S{N}.2 ──┐
  ↓      │ (parallel)
S{N}.3 ◄─┘
```

**External:** {None / list}

## Architecture

| Decision | ADR | Summary |
|----------|-----|---------|
| {Decision 1} | ADR-{XXX} | {1-line} |

> Problem Brief: {path or "N/A"}

## Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| {Risk 1} | H/M | {strategy} |
| {Risk 2} | M/L | {strategy} |

## Parking Lot

- {Deferred item} → {destination}
