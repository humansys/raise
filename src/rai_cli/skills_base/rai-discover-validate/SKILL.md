---
name: rai-discover-validate
description: >
  Validate component descriptions using confidence-tier workflow.
  Auto-validates high-confidence, batch-reviews medium by module,
  flags low for individual human review.

license: MIT

metadata:
  raise.work_cycle: discovery
  raise.frequency: per-project
  raise.fase: "3"
  raise.prerequisites: discover-scan
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.1.0"
  raise.visibility: public
---

# Discovery Validate: Confidence-Based Review

## Purpose

Validate component descriptions using a confidence-tier workflow that reduces human decisions from O(components) to O(modules + exceptions). High-confidence components are auto-validated. Medium-confidence components are reviewed as module batches with AI synthesis. Low-confidence components get individual human review.

**Key insight:** The deterministic analyzer (`rai discover analyze`) already did the heavy lifting. This skill only involves the human where it matters.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps, review each tier in order.

**Ha (破)**: Trust high-confidence auto-validation; focus time on medium/low.

**Ri (離)**: Tune confidence thresholds for domain-specific projects.

## Context

**When to use:**
- After `/rai-discover-scan` has created `work/discovery/analysis.json`
- When re-validating after code changes (re-run scan + analyze first)

**When to skip:**
- All components already validated
- No `analysis.json` (run `/rai-discover-scan` first)

**Inputs required:**
- `work/discovery/analysis.json` from `/rai-discover-scan` (via `rai discover analyze`)
- `work/discovery/components-draft.yaml` from `/rai-discover-scan`

**Output:**
- Updated `work/discovery/components-draft.yaml` with `validated: true`
- `work/discovery/components-validated.json` — Final component catalog for graph integration

## Steps

### Step 1: Load Analysis Results

Read the analysis file:

```bash
rai discover analyze --input work/discovery/analysis.json --output summary
```

Or read directly:
```
Read: work/discovery/analysis.json
```

**Extract:**
- Confidence distribution (high/medium/low counts)
- Module groups (for batch processing)
- Components list with confidence tiers

**Present overview to user:**

```markdown
## Validation Overview

**Components:** {total}
- High confidence (auto-validate): {N} ({percent}%)
- Medium confidence (module batch review): {N} ({percent}%)
- Low confidence (individual review): {N} ({percent}%)

**Module groups:** {N} modules
**Estimated human decisions:** ~{medium_modules + low_count}
```

> **⚠ All-low scenario:** If `high == 0 AND medium == 0 AND low > 50`, the
> per-component path would require O(components) decisions. Skip to
> **Step 4 Gate** for alternative modes before attempting individual review.

**Verification:** Analysis loaded with confidence tiers.

> **If you can't continue:** No analysis.json → Run `/rai-discover-scan` first.

### Step 2: Auto-Validate High Confidence

Components with confidence score >= 70 have strong signals (docstring, type annotations, path convention, known base class). Auto-validate them:

For each high-confidence component:
- Use `auto_purpose` (first sentence of docstring) as `purpose`
- Use `auto_category` as `category`
- Set `validated: true`, `validated_by: auto`, `validated_at: {timestamp}`

**Present summary to user:**

```markdown
### Auto-Validated: {N} components

Categories: {breakdown}

These components had strong documentation signals. Review any exceptions below.
```

**Ask user:** "Auto-validate {N} high-confidence components? [Approve all / Review individually]"

**Verification:** High-confidence components marked validated.

### Step 3: Batch Review Medium Confidence (by Module)

Medium-confidence components (40-69) have partial signals — they need AI synthesis for purpose/category but can be reviewed efficiently in module batches.

**For each module group** (from `module_groups` in analysis.json):

1. Read all medium-confidence components in this module
2. If the module has components that already have good `auto_purpose`, present those
3. For components without good purpose, synthesize descriptions using module context

> **C# / large projects:** If modules are single-file (1 component each), grouping by
> file is not useful. Switch to grouping by **namespace prefix** instead:
> extract the common namespace segment (e.g., `BetterNet.Services.Profile.Application`)
> and batch all components sharing that prefix in one review.

**Present the module batch:**

```markdown
### Module: {file_path or namespace} ({N} components)

| # | Name | Kind | Auto-Category | Purpose | Confidence |
|---|------|------|---------------|---------|------------|
| 1 | {name} | {kind} | {auto_category} | {auto_purpose or "needs synthesis"} | {score} |
| 2 | ... | ... | ... | ... | ... |
```

**Ask user per module:** "Approve this module batch? [Approve all / Edit specific / Skip module]"

- **Approve all**: Mark all components in module as validated
- **Edit specific**: User specifies which components to correct
- **Skip module**: Leave for later

**Verification:** Module batch processed.

### Step 4: Gate — Check Scale Before Individual Review

**Before starting individual review, check:**

```
all_low = (high_count == 0 AND medium_count == 0 AND low_count > 50)
```

**If `all_low` is true**, individual review would require O(components) decisions — defeating the purpose of the pipeline. Present the user with these alternatives:

---

#### Mode A: By Architectural Layer *(recommended for Clean Architecture / CQRS)*

Group components by top-level namespace segment (e.g., `Application`, `Domain`, `Infrastructure`, `Api`). Review one layer at a time:

1. Extract layer from each component's namespace (first segment after project root)
2. Present components grouped by layer in a table (same format as Step 3)
3. Ask user: "Approve entire `{Layer}` layer? [Approve all / Review individually / Skip layer]"
4. **Approve all**: mark all components in layer `validated: true, validated_by: human`
5. **Skip layer**: mark all as `skipped: true, skip_reason: "layer_skip"`

---

#### Mode B: Key Components *(recommended when codebase is large and mostly infra)*

User nominates 10–20 key components; all others are bulk-skipped.

1. Ask user: "Name the 10–20 most important components (entry points, core domain, key services)"
2. Validate only those individually (use Step 4 normal flow)
3. Bulk-skip the rest: `skipped: true, skip_reason: "bulk_skip — not nominated"`
4. Note in summary how many were bulk-skipped

---

#### Mode C: Accept by Naming Pattern *(recommended for consistent suffix patterns)*

Auto-accept all components whose name matches a consistent suffix pattern in a namespace.

1. Show a breakdown: "Found 87 `*Handler`, 34 `*Repository`, 12 `*Validator`..."
2. Ask user per pattern: "Auto-accept all `*Handler` components? [Yes / Review first / Skip]"
3. **Yes**: mark all matching as `validated: true, validated_by: auto-pattern`
4. Remaining unmatched components → fall back to Mode A or individual review

---

**If `all_low` is false**, proceed normally with individual review below.

**Ask user which mode to use** if `all_low` is true.

**Verification:** Mode selected or individual review confirmed.

---

### Step 4b: Individual Review Low Confidence

Low-confidence components (< 40) that weren't handled by a bulk mode need individual human attention.

**For each low-confidence component:**

```markdown
### Component: {name}

**File:** {file}:{line}
**Kind:** {kind}
**Signature:** `{signature}`
**Docstring:** {docstring or "None"}
**Auto-Category:** {auto_category}
**Confidence:** {score} (low)

**Signals missing:** {list of false signals}
```

**Ask user:**
- Approve with synthesized purpose
- Edit: provide corrected purpose/category
- Skip: exclude from catalog

**Verification:** Each low-confidence component individually reviewed.

### Step 5: Save Validated Components

Update `work/discovery/components-draft.yaml` with all validation decisions:

1. High-confidence: `validated: true`, `validated_by: auto`
2. Medium-confidence: `validated: true`, `validated_by: human` (batch)
3. Low-confidence: `validated: true`, `validated_by: human` (individual)
4. Skipped: `skipped: true`, `skip_reason: "human_skip"`

**Write updated file.**

**Verification:** Draft file updated with validation states.

### Step 6: Export Validated Components

After validation, export the validated components to JSON for graph integration.

**Load** `work/discovery/components-draft.yaml` and filter to `validated: true` components.

**Transform** each validated component to graph node format:

```json
{
  "id": "comp-scanner-symbol",
  "type": "component",
  "content": "purpose description",
  "source_file": "path/to/file.py",
  "created": "ISO timestamp",
  "metadata": {
    "name": "Symbol",
    "kind": "class",
    "line": 44,
    "signature": "class Symbol(BaseModel)",
    "category": "model",
    "depends_on": ["pydantic.BaseModel"],
    "validated_by": "human",
    "validated_at": "ISO timestamp"
  }
}
```

**Field mapping:** `id` → `id`, `purpose` → `content`, `file` → `source_file`, everything else → `metadata.*`

**Write** `work/discovery/components-validated.json`:

```json
{
  "generated_at": "ISO timestamp",
  "source_file": "work/discovery/components-draft.yaml",
  "component_count": 32,
  "components": [ ... ]
}
```

**Update** `work/discovery/context.yaml` status to `complete`.

**Verification:** `work/discovery/components-validated.json` created with validated components.

### Step 7: Final Summary

```markdown
## Validation & Export Complete

**Total components:** {N}
**Auto-validated (high):** {N}
**Batch-reviewed (medium):** {N}
**Individually reviewed (low):** {N}
**Skipped:** {N}

**Human decisions made:** {actual_decisions} (vs {total} components — {reduction}% reduction)

**Exported:** {N} components to `work/discovery/components-validated.json`

### Next Steps

**Graph Integration:**
```bash
rai memory build --input work/discovery/components-validated.json
```

**Architecture Documentation:**
Run `/rai-discover-document` to generate module docs from discovery data.
```

**Verification:** Summary displayed; user knows status.

## Output

- **Artifacts:**
  - Updated `work/discovery/components-draft.yaml`
  - `work/discovery/components-validated.json` — Final component catalog
- **Telemetry:** `skill_event` via Stop hook
- **Next:** `rai memory build` (graph integration) or `/rai-discover-document` (architecture docs)

## Confidence Tiers

| Tier | Score | Action | Human Effort |
|------|-------|--------|-------------|
| High | >= 70 | Auto-validate with auto_purpose/auto_category | Approve batch (1 decision) |
| Medium | 40-69 | AI synthesis + module batch review | Per-module decision |
| Low | < 40 | Individual human review | Per-component decision |

## Validation States

| State | Meaning |
|-------|---------|
| `validated: false` | Pending review |
| `validated: true, validated_by: auto` | Auto-validated (high confidence) |
| `validated: true, validated_by: human` | Human approved (possibly edited) |
| `skipped: true` | Human excluded from catalog |

## Notes

### Why Module Batches?

Components in the same module are semantically related. Reviewing them together:
- Provides context (what else is in this file?)
- Enables pattern-based approval ("all models in this file look correct")
- Reduces context switching
- Enables parallel AI synthesis (each module = one batch)

### Resume Safety

Progress is saved to YAML after each tier. If interrupted:
- High-confidence auto-validation is atomic
- Medium/low progress saved per module/component
- Can re-run `/rai-discover-validate` anytime to continue

### Tuning Thresholds

If too many components are medium/low on a well-documented codebase:
- Consider adjusting thresholds in `analyzer.py` (constants at top)
- Default: high >= 70, medium >= 40, low < 40

## References

- Previous skill: `/rai-discover-scan`
- Next: `rai memory build` (graph integration) or `/rai-discover-document` (architecture docs)
- CLI: `rai discover analyze --help`
- Analyzer: `src/rai_cli/discovery/analyzer.py`
