---
description: 'Validate component descriptions using confidence-tier workflow. Auto-validates
  high-confidence, batch-reviews medium by module, flags low for individual human
  review.

  '
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '3'
  raise.frequency: per-project
  raise.gate: ''
  raise.next: ''
  raise.prerequisites: discover-scan
  raise.version: 3.0.0
  raise.visibility: public
  raise.work_cycle: discovery
name: rai-discover-validate
---

# Discovery Validate

> **Deprecated:** Use `/rai-discover` instead, which runs the full pipeline (detect → extract → describe → document → build) in one pass. This skill is kept for backward compatibility.

## Purpose

Validate component descriptions using a confidence-tier workflow that reduces human decisions from O(components) to O(modules + exceptions).

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, review each tier in order
- **Ha**: Trust high-confidence auto-validation; focus on medium/low
- **Ri**: Tune confidence thresholds for domain-specific projects

## Context

**When to use:** After `/rai-discover-scan` has created `work/discovery/analysis.json`.

**When to skip:** All components already validated, or no `analysis.json` exists.

**Inputs:** `work/discovery/analysis.json`, `work/discovery/components-draft.yaml`.

## Steps

### Step 1: Load & Present Overview

```markdown
## Validation Overview
**Components:** {total}
- High confidence (auto-validate): {N} ({%})
- Medium confidence (module batch): {N} ({%})
- Low confidence (individual review): {N} ({%})
**Estimated human decisions:** ~{medium_modules + low_count}
```

<verification>
Analysis loaded with confidence tiers.
</verification>

### Step 2: Auto-Validate High Confidence (≥70)

Use `auto_purpose` and `auto_category` directly. Set `validated: true, validated_by: auto`.

Ask user: "Auto-validate {N} high-confidence components? [Approve all / Review individually]"

<verification>
High-confidence components marked validated.
</verification>

### Step 3: Batch Review Medium Confidence (40-69)

For each module group from `analysis.json`:

| # | Name | Kind | Category | Purpose | Score |
|---|------|------|----------|---------|-------|
| 1 | {name} | {kind} | {auto_category} | {purpose} | {score} |

Ask per module: "Approve batch? [Approve all / Edit specific / Skip module]"

For C#/large projects with single-file modules: group by namespace prefix instead.

<verification>
Module batches processed.
</verification>

### Step 4: Handle Low Confidence (<40)

**Scale gate:** If all components are low AND count >50, offer alternative modes:

| Mode | Best for | Strategy |
|------|----------|----------|
| A: By layer | Clean Architecture / CQRS | Group by top-level namespace, approve per layer |
| B: Key components | Large infra-heavy codebases | User nominates 10-20 key components, bulk-skip rest |
| C: Naming pattern | Consistent suffix patterns | Auto-accept by pattern (`*Handler`, `*Repository`) |

Otherwise, review individually — present file, signature, signals, ask: Approve / Edit / Skip.

<verification>
Low-confidence components reviewed or alternative mode applied.
</verification>

### Step 5: Export & Save

1. Update `components-draft.yaml` with validation states
2. Export validated components to `work/discovery/components-validated.json` (graph node format)
3. Update `work/discovery/context.yaml` status to `complete`

**Graph node format:**
```json
{"id": "comp-scanner-symbol", "type": "component", "content": "purpose",
 "source_file": "path", "metadata": {"name": "...", "kind": "...", "validated_by": "..."}}
```

Present summary: total, auto-validated, batch-reviewed, individual, skipped, decision reduction %.

<verification>
`components-validated.json` created. Context status updated.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Updated draft | `work/discovery/components-draft.yaml` |
| Validated catalog | `work/discovery/components-validated.json` |
| Next | `rai graph build` or `/rai-discover-document` |

## Quality Checklist

- [ ] High-confidence auto-validation approved by user before proceeding
- [ ] Medium batches presented with full context (module, category, purpose)
- [ ] Scale gate checked before attempting O(components) individual review
- [ ] Export uses graph node format (id, type, content, source_file, metadata)
- [ ] NEVER skip the scale gate for all-low scenarios (>50 components)

## References

- Previous: `/rai-discover-scan`
- Next: `rai graph build` or `/rai-discover-document`
- CLI: `rai discover analyze --help`
- Confidence tiers: high ≥70, medium 40-69, low <40
