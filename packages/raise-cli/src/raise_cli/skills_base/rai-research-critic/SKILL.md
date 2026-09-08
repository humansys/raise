---
name: rai-research-critic
description: Completeness critic — identifies coverage gaps and triggers re-search if needed. Deep depth only.
allowed-tools:
  - Read
  - Write
  - Bash
  - WebSearch
  - Agent
metadata:
  raise.work_cycle: research
  raise.frequency: per-research
  raise.version: "1.0.0"
  raise.visibility: public
---

# Research Critic

## Purpose

Evaluate research completeness. Identify gaps in coverage: angles not searched, source modalities missing, claims unverified, perspectives absent. If gaps are material, trigger a targeted re-search.

## Steps

### Step 1: Read All Artifacts

- `work/research/{topic}/frame.md` — original question and secondary questions
- `work/research/{topic}/scope.md` — planned angles
- `work/research/{topic}/sources/evidence-catalog.md` — verified claims

### Step 2: Completeness Audit

Check each dimension:

| Dimension | Question |
|-----------|----------|
| **Question coverage** | Are all secondary questions addressed by at least one claim? |
| **Angle coverage** | Did every planned angle produce findings? |
| **Source diversity** | Are there 3+ source types (academic, practitioner, vendor, community)? |
| **Geographic diversity** | For LATAM/regional topics: are there region-specific sources? |
| **Temporal coverage** | Are sources from the last 12 months? Any reliance on stale data? |
| **Contrarian coverage** | Is there at least one strong counter-argument documented? |
| **Refuted gap** | Were any refuted claims the only evidence for a secondary question? |

### Step 3: Gap Assessment

Classify each gap:

- **Material** — missing evidence that could change the recommendation
- **Minor** — nice to have but won't change the conclusion
- **Acceptable** — the gap is acknowledged and the recommendation stands

### Step 4: Re-search (if material gaps)

For each material gap, fork a targeted search agent:

```
Agent({
  subagent_type: "fork",
  prompt: "Targeted re-search for gap: {gap_description}.
    Search specifically for: {what's missing}.
    Return findings in the same format as raw-findings."
})
```

Append new findings to evidence catalog. Max 1 re-search round (prevent infinite loops).

### Step 5: Write Critic Report

Write `work/research/{topic}/critic-report.md`:

```markdown
# Completeness Critic: {topic}

## Coverage Matrix
| Dimension | Status | Notes |
|-----------|--------|-------|
| Question coverage | {complete|gaps} | {details} |
...

## Material Gaps
{list, or "None — coverage is complete"}

## Re-search Actions
{what was re-searched, or "None needed"}

## Verdict
{COMPLETE | COMPLETE_WITH_CAVEATS | INCOMPLETE}
```

### Step 6: Emit phase_result

```yaml
phase_result:
  status: done
  verdict: {COMPLETE|COMPLETE_WITH_CAVEATS|INCOMPLETE}
  material_gaps: {N}
  re_searches: {N}
  artifacts:
    - work/research/{topic}/critic-report.md
```

## Output

| Item | Destination |
|------|-------------|
| Critic report | `work/research/{topic}/critic-report.md` |
| Verdict | phase_result → Synthesize knows coverage quality |
