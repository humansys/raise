---
name: rai-research-synthesize
description: Produce final research report with recommendations, confidence levels, and governance linkage.
allowed-tools:
  - Read
  - Write
  - Bash
metadata:
  raise.work_cycle: research
  raise.frequency: per-research
  raise.version: "1.0.0"
  raise.visibility: public
---

# Research Synthesize

## Purpose

Produce the final research report. Synthesize from whatever artifacts prior phases produced — adapts to depth (quick has only raw findings, deep has verified evidence catalog + critic report).

## Steps

### Step 1: Read Available Artifacts

Read in order of richness (use the most complete available):

1. `work/research/{topic}/critic-report.md` (deep only)
2. `work/research/{topic}/sources/evidence-catalog.md` (standard/deep)
3. `work/research/{topic}/sources/raw-findings.md` (all depths)
4. `work/research/{topic}/frame.md` (always)

### Step 2: Synthesize Findings

Group findings by theme. For each theme:
- State the finding as a claim
- List supporting evidence with confidence level
- Note contradictions or caveats
- State whether the claim survived verification (if verify ran)

### Step 3: Formulate Recommendation

Structure:
- **Recommendation** — clear, actionable statement
- **Confidence** — HIGH / MEDIUM / LOW with rationale
- **Trade-offs** — what you gain and lose
- **Risks** — what could go wrong
- **Contrary evidence** — strongest argument against the recommendation

Rules:
- NEVER present single-source findings as consensus
- If confidence is LOW, say so — don't hedge with vague language
- If evidence contradicts the recommendation, state it explicitly

### Step 4: Governance Linkage

Connect research output to actionable next steps:
- **ADR** — if research informs an architectural decision, note the ADR to create
- **Backlog** — if research reveals actionable work, note items to create
- **Parking lot** — if research opens new questions, capture them

### Step 5: Write Report

Write `work/research/{topic}/{topic}-report.md`:

```markdown
# Research Report: {title}

**Date:** {date}
**Depth:** {quick|standard|deep}
**Question:** {primary question}
**Confidence:** {HIGH|MEDIUM|LOW}

## Executive Summary
{2-3 sentences: recommendation + key evidence + main risk}

## Findings

### {Theme 1}
{finding with evidence, sources, confidence}

### {Theme 2}
...

## Recommendation
{actionable recommendation}

### Trade-offs
{what you gain / what you lose}

### Risks
{what could go wrong}

### Contrary Evidence
{strongest argument against}

## Methodology
- Depth: {quick|standard|deep}
- Sources consulted: {N}
- Claims verified: {N} (if verify ran)
- Coverage: {COMPLETE|COMPLETE_WITH_CAVEATS|INCOMPLETE} (if critic ran)
- Tools: {Tavily, Brave, ddgr, WebSearch}

## Next Steps
- [ ] {ADR / backlog item / parking lot entry}

## Sources
{numbered list of all sources with URLs}
```

Write `work/research/{topic}/README.md` with navigation links to all artifacts.

### Step 6: Emit phase_result

```yaml
phase_result:
  status: done
  confidence: {HIGH|MEDIUM|LOW}
  recommendation: {one-line summary}
  artifacts:
    - work/research/{topic}/{topic}-report.md
    - work/research/{topic}/README.md
```

## Output

| Item | Destination |
|------|-------------|
| Research report | `work/research/{topic}/{topic}-report.md` |
| Navigation | `work/research/{topic}/README.md` |
| Next | ADR, backlog item, or parking lot update |
