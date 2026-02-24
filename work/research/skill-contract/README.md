# Research: Skill Contract Design

> RES-SKILL-CONTRACT-001 | 2026-02-23 | E250 Skill Excellence

## 15-Minute Overview

**Question**: What structural patterns maximize AI agent instruction reliability, consistency, and token efficiency?

**Answer**: Fewer rules, better positioned, with examples over rules. The compliance math is brutal: `p(all)≈p(each)^n`. Halving instruction count can quadruple full compliance.

**Key Numbers**:
- Reasoning degrades at ~3,000 tokens (ACL 2024)
- >30% accuracy drop for middle-positioned info (TACL 2024)
- Best frontier models: 68% compliance at 500 instructions (IFScale 2025)
- Examples: 1-2 sweet spot, >5 counterproductive
- Semantically similar noise is worse than random noise

**Proposed Contract**: 7 fixed sections, ≤150 lines, ≤15 discrete rules, ≥80% substance ratio.

## Files

| File | Content |
|------|---------|
| `skill-contract-report.md` | Full findings + recommendation |
| `sources/evidence-catalog.md` | All 23 sources with ratings |

## Decision Linkage

- **Informs**: E250 epic-design → Skill Contract ADR
- **Builds on**: SES-270 structural + content audit of 23 skills
- **Feeds**: Story breakdown for skill refactoring
