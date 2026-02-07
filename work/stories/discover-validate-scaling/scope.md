# Story: Scale discover-validate for brownfield projects

> **Branch:** `story/discovery/validate-scaling`
> **Type:** Standalone (improvement to E13 Discovery)
> **Created:** 2026-02-07
> **Origin:** Architecture validation dogfooding surfaced this deficiency

---

## Problem

The current `/discover-validate` skill presents components one-by-one for human review. On raise-cli (16K lines, 374 public components), this requires ~37 batches of 10 — impractical. On a typical brownfield project (50-200K lines), it would require 200-500 batches. The process doesn't scale.

Manual validation at this volume is also *less reliable* than improving signal quality upstream — fatigue causes rubber-stamping after ~50 items.

## Objective

Redesign `/discover-validate` to work at module-level with confidence tiers, reducing human interactions from O(components) to O(modules).

---

## In Scope

- Rewrite `/discover-validate` skill (markdown) with:
  - Module-level presentation and batch approval
  - Confidence tiers (auto-approve / batch / individual review)
  - Auto-categorization by file location convention
  - Drill-down only on exceptions
- Update `/discover-scan` skill (markdown) to produce confidence signals in draft YAML

## Out of Scope

- CLI code changes to `raise discover scan`
- New CLI commands
- Diff-mode for re-scans (future enhancement)
- Changes to `/discover-start` or `/discover-complete`

---

## Done Criteria

- [ ] `/discover-validate` skill rewritten with module-level flow
- [ ] `/discover-scan` skill updated with confidence signal instructions
- [ ] Validated on raise-cli codebase (our own repo as test case)
- [ ] Human interactions reduced from ~37 batches to <20 decisions
- [ ] Story reviewed and merged to v2

---

## Design Notes (from session analysis)

**Current flow:** 374 components × 1 decision = 374 interactions
**Target flow:** 13 modules × 1 decision + ~10 drilldowns = ~23 interactions

**Confidence tiers:**
- **High (auto-approve):** Has docstring + category matches location convention
- **Medium (module batch):** Has docstring, standard category
- **Low (individual review):** No docstring, category mismatch, ambiguous purpose

**Location → category mapping:**
- `cli/commands/*.py` → command
- `governance/parsers/*.py` → parser
- `context/*.py` → builder/service
- `**/models.py` → schema/model

---

*Scope defined: 2026-02-07*
