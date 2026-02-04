# Meta-Research: AI Research Prompt Structuring for RaiSE

> How to structure research prompts for epistemological rigor in AI-assisted workflows
> Research completed: 2026-01-31
> Confidence: HIGH

---

## 15-Minute Overview

### Research Question

**How should AI research prompts be structured to produce epistemologically rigorous results suitable for engineering decisions?**

### Decision Context

This research informs:
- Design of `.raise/templates/tools/research-prompt.md`
- Updates to `.raise/katas/tools/research.md`
- Tool selection strategy for research delegation

### Key Finding

**Structured research prompts with hierarchical delegation patterns produce higher-quality, reproducible research outputs.**

**Evidence**: 20 sources (7 Very High, 8 High, 5 Medium evidence level)
**Confidence**: HIGH (75% of major claims triangulated from 3+ independent sources)

### Recommendation

**Implement research prompt template with:**
1. **Structured anatomy**: Role + Question + Instructions + Output Format + Quality Criteria
2. **Hierarchical delegation**: Orchestrator → Research Specialist → Synthesis Agent → Human Validation
3. **Tool fallback chain**: ddgr → perplexity → WebSearch (graceful degradation)
4. **Reproducibility metadata**: Version prompt, log tools/models, timestamp outputs

**Trade-off**: More upfront effort (15-30 min to create prompt) for reproducible, auditable research

**Next Action**: Create template file → Validate with real research → Update kata

---

## Navigation

| Document | Purpose | Time |
|----------|---------|------|
| **README.md** (this file) | Quick overview and navigation | 5 min |
| [recommendation.md](./recommendation.md) | Detailed recommendation with implementation plan | 15 min |
| [synthesis.md](./synthesis.md) | Triangulated findings and patterns | 20 min |
| [sources/evidence-catalog.md](./sources/evidence-catalog.md) | All 20 sources with ratings | 30 min |

---

## Major Claims (Triangulated)

| Claim | Sources | Confidence |
|-------|---------|------------|
| Structured prompts improve quality | 5 | HIGH |
| Human-AI collaboration required for rigor | 4 | HIGH |
| Two-step approaches outperform single-pass | 3 | HIGH |
| Hierarchical delegation enables specialization | 4 | HIGH |
| Transparency/reproducibility foundational | 4 | HIGH |
| Triangulation minimizes bias | 4 | HIGH |

**Zero contested claims** - All evidence convergent

---

## Implementation Checklist

### Phase 1: Template Creation ✓ NEXT
- [ ] Create `.raise/templates/tools/research-prompt.md`
- [ ] Add example research prompt
- [ ] Update template README

### Phase 2: Kata Updates
- [ ] Add Step 1.5 (Create Research Prompt)
- [ ] Add tool availability checks
- [ ] Update evidence levels for engineering
- [ ] Add delegation pattern diagram

### Phase 3: Validation
- [ ] Test with real research question
- [ ] Validate tool fallback chain
- [ ] Iterate based on findings

---

## Key Patterns Discovered

### Pattern 1: Prompt Anatomy
```
Role Definition → Task Context → Instructions → Output Format → Quality Criteria
```

### Pattern 2: Delegation Architecture
```
Orchestrator (Human + AI) → Research Specialist → Synthesis Agent → Validation Gate
```

### Pattern 3: Iterative Refinement
```
Frame → Execute → Evaluate → Refine ↩
```

---

## Tool Selection Strategy

| Depth | Tool | Use When |
|-------|------|----------|
| Quick Scan (1-2h) | ddgr | Simple questions, no API needed |
| Standard (4-8h) | perplexity | Citations required, complex questions |
| Deep Dive (2-5d) | perplexity + Manual | Strategic decisions, novel domains |
| Fallback | WebSearch | Always available, reliable baseline |

**Availability**: Check with `which ddgr` and `llm models list | grep perplexity`

---

## Quality Assurance

### Evidence Distribution
- Very High: 35% (academic papers, official docs)
- High: 40% (expert practitioners, maintained OSS)
- Medium: 25% (community-validated resources)

### Triangulation Success
- 6 of 8 major claims: HIGH confidence (3+ sources)
- 2 of 8 major claims: MEDIUM confidence (2 sources)
- 0 contested claims

### Geographic/Temporal Coverage
- Primarily 2024-2025 sources (current best practices)
- Global research community (US, EU, academic + industry)

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Template too complex | Medium | Provide "lite" version for quick scans |
| Tool installation friction | High | Fallback chain + clear install docs |
| Template becomes stale | Medium | Version + quarterly review |
| Over-reliance on AI | Low | Mandate human validation gate |

---

## Governance Linkage

**ADR Status**: Recommendation to create "ADR: Research Workflow for RaiSE"
**Backlog Impact**: None (meta-process improvement)
**Parking Lot**: Resolves meta-research question from session start

---

## Sources Summary

### Academic (Very High Evidence)
1. [The Prompt Report](https://arxiv.org/abs/2406.06608) - Taxonomy of 58 techniques
2. [Systematic Survey of Prompt Engineering](https://arxiv.org/abs/2402.07927) - Five hierarchical strategies
3. [Hybrid Framework for AI-Augmented Reviews](https://link.springer.com/article/10.1007/s11301-025-00522-8) - Epistemological principles
4. [Evidence Triangulator](https://www.nature.com/articles/s41467-025-62783-x) - Two-step extraction (F1=0.86)
5. [Prompt Engineering for Statistical Reasoning](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1658316/full) - Epistemological assessment
6. [LLM Prompts for Requirements Engineering](https://arxiv.org/html/2507.03405v1) - Engineering guidelines
7. [Reliable Software Task Flows](https://www.nature.com/articles/s41598-025-19170-9) - Robust evaluation

### Practitioner (High Evidence)
8. [Prompt Engineering Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) - 49k+ stars
9. [LLM Agents Guide](https://www.promptingguide.ai/research/llm-agents) - Delegation patterns
10. [Multi-Agent Patterns ADK](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/) - Google official
11. [Palantir Best Practices](https://www.palantir.com/docs/foundry/aip/best-practices-prompt-engineering) - Enterprise patterns
12. [Agentic AI Design Patterns](https://research.aimultiple.com/agentic-ai-design-patterns/) - Industry research

### Additional (Medium-High Evidence)
13-20. See [evidence-catalog.md](./sources/evidence-catalog.md) for complete list

---

## Next Steps

1. **Immediate**: Review recommendation with Emilio
2. **If approved**: Create research prompt template
3. **Then**: Apply template to original F1.1 lean spec research question
4. **Finally**: Update research kata with new workflow

---

**Research Status**: COMPLETE
**Recommendation Status**: READY FOR REVIEW
**Total Research Time**: ~2 hours
**Output Artifacts**: 4 files (README, recommendation, synthesis, evidence catalog)

---

*Meta-research demonstrating the very process it proposes to improve*
*Conducted using: WebSearch tool (ddgr unavailable, llm not installed)*
*Exemplifies: Fallback chain working as expected*
