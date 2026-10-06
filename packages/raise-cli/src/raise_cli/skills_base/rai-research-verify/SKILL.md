---
name: rai-research-verify
description: Adversarial verification of major claims using independent forks. Deep depth only.
allowed-tools:
  - Read
  - Write
  - Bash
  - WebSearch
  - WebFetch
  - Agent
metadata:
  raise.work_cycle: research
  raise.frequency: per-research
  raise.version: "1.0.0"
  raise.visibility: public
---

# Research Verify

## Purpose

Adversarially verify each major claim from the evidence catalog. Independent agents attempt to **refute** each claim. Claims survive only if majority of verifiers fail to refute them.

## Steps

### Step 1: Select Claims to Verify

Read `work/research/{topic}/sources/evidence-catalog.md`. Select claims for verification:
- All claims rated High or Very High confidence (must survive scrutiny)
- All claims with contradictions (need resolution)
- Any claim that drives the final recommendation

Skip Low-evidence claims — they're already flagged as weak.

### Step 2: Adversarial Verification

For each claim, fork 3 independent verifier agents:

```
Agent({
  subagent_type: "fork",
  prompt: "ADVERSARIAL VERIFICATION. Your job is to REFUTE this claim.
    Default to refuted=true if uncertain.

    Claim: '{claim_statement}'
    Supporting sources: {source_urls}

    Search for: counter-evidence, methodological flaws, outdated data,
    vendor bias, survivorship bias, sample size issues.

    Return JSON: {refuted: bool, reason: string, counter_sources: [{url, excerpt}]}"
})
```

### Step 3: Tally Verdicts

Per claim:
- **Survives**: 2+ of 3 verifiers failed to refute (could not find counter-evidence)
- **Weakened**: 1 refutation with valid counter-evidence → downgrade confidence
- **Refuted**: 2+ verifiers refute with evidence → mark as refuted, do not include in synthesis

### Step 4: Update Evidence Catalog

Append verification results to evidence catalog:

```markdown
## Verification Results

| Claim | Verifiers | Refuted | Verdict | New Confidence |
|-------|:---------:|:-------:|---------|:--------------:|
| {claim} | 3 | {0-3} | {survives|weakened|refuted} | {level} |

### Refuted Claims
{list with counter-evidence — these are excluded from synthesis}

### Weakened Claims
{list with reason for downgrade}
```

### Step 5: Emit phase_result

```yaml
phase_result:
  status: done
  claims_verified: {N}
  survived: {N}
  weakened: {N}
  refuted: {N}
  artifacts:
    - work/research/{topic}/sources/evidence-catalog.md
```

## Output

| Item | Destination |
|------|-------------|
| Updated evidence catalog | `work/research/{topic}/sources/evidence-catalog.md` |
| Verification tallies | phase_result → Critic checks coverage |
