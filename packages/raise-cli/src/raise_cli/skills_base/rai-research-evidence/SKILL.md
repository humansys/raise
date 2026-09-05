---
name: rai-research-evidence
description: Merge, deduplicate, and catalog findings with evidence levels. Skipped for quick depth.
allowed-tools:
  - Read
  - Write
metadata:
  raise.work_cycle: research
  raise.frequency: per-research
  raise.version: "1.0.0"
  raise.visibility: public
---

# Research Evidence Catalog

## Purpose

Merge raw findings from all search angles, deduplicate semantically equivalent claims, and produce a structured evidence catalog with calibrated evidence levels.

## Steps

### Step 1: Read Raw Findings

Read `work/research/{topic}/sources/raw-findings.md`.

### Step 2: Extract Claims

From all sources, extract discrete, falsifiable claims. Each claim is one assertion that can be independently verified.

### Step 3: Semantic Dedup

Group claims by semantic similarity. When multiple sources make the same claim:
- Merge into one claim entry
- List all supporting sources (strengthens evidence level)
- Note any contradictions between sources on the same claim

### Step 4: Rate Evidence

Per claim, assign evidence level:

| Level | Criteria |
|-------|----------|
| Very High | Peer-reviewed OR production-proven at scale (>10k users), 3+ independent sources |
| High | Expert practitioners at established companies, 2+ sources, >1k stars if OSS |
| Medium | Community-validated, emerging consensus, 1-2 sources, >100 stars |
| Low | Single source, unvalidated, opinion, vendor-only claim |

### Step 5: Write Evidence Catalog

Write `work/research/{topic}/sources/evidence-catalog.md`:

```markdown
# Evidence Catalog: {topic}

## Summary
- Total sources: {N}
- Unique claims: {N} (after dedup, {N} duplicates removed)
- Evidence distribution: {N} Very High, {N} High, {N} Medium, {N} Low

## Claims

### Claim 1: {statement}
- Evidence level: {level}
- Sources: {list with URLs}
- Contradictions: {any contrary evidence}
- Confidence: {HIGH|MEDIUM|LOW}

### Claim 2: ...
```

### Step 6: Emit phase_result

```yaml
phase_result:
  status: done
  claim_count: {N}
  high_confidence_claims: {N with Very High or High evidence}
  contradictions: {N claims with contrary evidence}
  artifacts:
    - work/research/{topic}/sources/evidence-catalog.md
```

## Output

| Item | Destination |
|------|-------------|
| Evidence catalog | `work/research/{topic}/sources/evidence-catalog.md` |
| Claim metrics | phase_result → Verify phase uses for prioritization |
