# Recommendation: Research Prompt Template & Kata Updates

> Evidence-based design for RaiSE research workflows
> Date: 2026-01-31
> Confidence: HIGH (based on 20 sources, 75% HIGH-confidence claims)

---

## Executive Summary

**Decision**: Implement structured research prompt template with hierarchical delegation pattern

**Confidence**: HIGH

**Rationale**: Convergent evidence from 7 Very High + 8 High sources demonstrates:
1. Structured prompts improve quality (5 independent sources)
2. Human-AI collaboration essential for epistemological rigor (4 sources)
3. Hierarchical delegation enables specialization (4 sources)
4. Transparency and reproducibility foundational (4 sources)

**Trade-offs**:
- **Accept**: More upfront effort to frame research question properly
- **Gain**: Reproducible, auditable, higher-quality research outputs
- **RaiSE Alignment**: Governance as Code + Observable Workflow principles

**Risks**:
- Tool availability variance (ddgr/perplexity may not be installed)
- Initial learning curve for prompt template usage
- Mitigation: Fallback chain + examples in template

---

## Recommendation 1: Research Prompt Template

### Template Design

Create `.raise/templates/tools/research-prompt.md`:

```markdown
---
research_id: "[TOPIC]-[YYYYMMDD]"
primary_question: "[Specific, falsifiable question]"
decision_context: "[What this informs: ADR, feature, backlog]"
depth: "[quick-scan|standard|deep-dive]"
created: "[YYYY-MM-DD]"
version: "1.0"
---

# Research Prompt: [Topic]

## Role Definition

You are a Research Specialist with expertise in [domain]. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

## Research Question

**Primary**: [Main question to answer]

**Secondary**:
1. [Supporting question 1]
2. [Supporting question 2]
3. [Supporting question 3]

## Decision Context

This research will inform: [Specific decision, ADR, story design, etc.]

**Stakeholder**: [Who needs this information]
**Timeline**: [When decision will be made]
**Impact**: [Consequences of getting this wrong]

## Instructions

### Search Strategy

1. **Academic sources**: Google Scholar, arXiv for [specific terms]
2. **Official documentation**: [Technology/framework] official docs
3. **Production evidence**: GitHub repos (>100 stars), engineering blogs (FAANG, established companies)
4. **Community validation**: Reddit, HN, Discord discussions

**Keywords**: [List specific search terms]

### Evidence Evaluation

For each source, assess:
- **Type**: Primary (research, official docs) / Secondary (practitioner) / Tertiary (synthesis)
- **Evidence Level**: Very High / High / Medium / Low (use RaiSE criteria)
- **Key Finding**: One-line takeaway
- **Relevance**: How it answers the research question

### Triangulation Requirements

- **Minimum sources**: [10 for quick-scan, 15-30 for standard, 50-100+ for deep-dive]
- **Major claims**: Require 3+ independent confirmations
- **Contrary evidence**: Document disagreements and conflicts
- **Confidence calibration**: Explicit uncertainty acknowledgment

## Output Format

Produce the following artifacts:

### 1. Evidence Catalog (`sources/evidence-catalog.md`)

```markdown
**Source**: [Title + Link]
- **Type**: Primary/Secondary/Tertiary
- **Evidence Level**: Very High/High/Medium/Low
- **Key Finding**: [Takeaway]
- **Relevance**: [Connection to question]
```

### 2. Synthesis Document

```markdown
## Major Claims (Triangulated)

**Claim 1**: [Statement]
- **Confidence**: HIGH/MEDIUM/LOW
- **Evidence**: [3+ sources]
- **Disagreement**: [Any contrary evidence]
- **Implication**: [What this means for our decision]
```

### 3. Recommendation

```markdown
**Decision**: [What we should do]
**Confidence**: HIGH/MEDIUM/LOW
**Rationale**: [Why, based on evidence]
**Trade-offs**: [What we're accepting]
**Risks**: [What could go wrong]
**Mitigations**: [How to address risks]
```

## Quality Criteria

Your research output will be validated against:

- [ ] Research question is specific and falsifiable
- [ ] Minimum source count met (scaled to depth)
- [ ] Evidence catalog complete with ratings
- [ ] Major claims triangulated (3+ sources)
- [ ] Confidence levels explicitly stated
- [ ] Contrary evidence acknowledged
- [ ] Recommendation is actionable
- [ ] Sources include publication dates (recency matters)
- [ ] Mix of academic, official, and practitioner sources

## Constraints

- **Time**: [Specific timebox if applicable]
- **Focus**: [What to deprioritize]
- **Scope**: [What NOT to research]

## Reproducibility Metadata

Include in final output:
- Tool/model used: [e.g., "perplexity-sonar", "WebSearch", "manual"]
- Search date: [YYYY-MM-DD]
- Prompt version: [From frontmatter]
- Researcher: [Agent or human name]
```

**Confidence**: HIGH
**Implementation**: Create as template file, reference from research kata

---

## Recommendation 2: Research Kata Updates

### Add Step 1.5: Create Research Prompt

**Insert between current Step 1 (Frame) and Step 2 (Survey):**

```markdown
### Step 1.5: Create Research Prompt

Using the research prompt template, document:
- Role definition for research specialist
- Search strategy with specific keywords
- Evidence evaluation criteria
- Output format requirements
- Quality checklist

**Verification:** Research prompt file created in `work/research/{topic}/prompt.md`

> **If you can't continue:** Question not clear enough → Return to Step 1 framing

**Tool Selection:** Choose research delegation approach:

| Tool | When to Use | Availability Check |
|------|-------------|-------------------|
| `ddgr` | Quick scans, no API key needed | `which ddgr` |
| `llm -m perplexity` | Deep research with citations | `llm models list \| grep perplexity` |
| `WebSearch` | Fallback, always available | Built-in |
| Manual + Task agent | Complex multi-query research | Always available |

**Delegation Pattern:**
1. Create research prompt following template
2. If `llm` available: `llm -m perplexity "$(cat prompt.md)"`
3. Else if `ddgr` available: `ddgr [keywords]` + manual synthesis
4. Else: WebSearch + Task agent for synthesis
```

**Confidence**: HIGH
**Implementation**: Update `.raise/katas/tools/research.md`

---

## Recommendation 3: Hierarchical Delegation Pattern

### Architecture

```
┌─────────────────────────────────────┐
│   Orchestrator (Human + Primary AI) │
│   - Frames questions                │
│   - Reviews final output            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Research Specialist (Agent/Tool)  │
│   - Executes search strategy        │
│   - Gathers sources                 │
│   - Rates evidence                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Synthesis Agent (Primary AI)      │
│   - Triangulates findings           │
│   - Identifies patterns             │
│   - Formulates recommendation       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Validation Gate (Human)           │
│   - Reviews against quality criteria│
│   - Approves or requests iteration  │
└─────────────────────────────────────┘
```

### Agent Capability Descriptions

**For LLM routing, define:**

```yaml
research_specialist:
  role: "Search and evidence gathering specialist"
  capabilities:
    - Web search across academic, official, and practitioner sources
    - Evidence level assessment using RaiSE criteria
    - Source citation with metadata (type, date, relevance)
  inputs: Research prompt with question, keywords, depth
  outputs: Evidence catalog with rated sources

synthesis_agent:
  role: "Pattern recognition and recommendation specialist"
  capabilities:
    - Cross-source triangulation (3+ confirmations required)
    - Confidence calibration with explicit uncertainty
    - Actionable recommendation formulation
  inputs: Evidence catalog from research specialist
  outputs: Synthesis document with triangulated claims and recommendation
```

**Confidence**: MEDIUM (only 2 sources on routing descriptions, need validation)
**Implementation**: Document in updated research kata

---

## Recommendation 4: Tool Selection Strategy

### Tiered Approach

```python
# Pseudocode for tool selection logic

def select_research_tool(depth: str, available_tools: list) -> str:
    """
    Select research tool based on depth requirement and availability.

    Preference order:
    1. perplexity (deep research with citations)
    2. ddgr (quick, free, no API key)
    3. WebSearch (reliable fallback)
    4. Manual + Task agent (complex research)
    """

    if depth == "deep-dive" and "perplexity" in available_tools:
        return "llm -m perplexity"

    elif depth == "quick-scan" and "ddgr" in available_tools:
        return "ddgr"

    elif "WebSearch" in available_tools:
        return "WebSearch"

    else:
        return "manual + Task(subagent_type='general-purpose')"
```

### Availability Checks

Add to research kata prerequisites:

```bash
# Check tool availability
echo "Checking research tool availability..."

if command -v ddgr &> /dev/null; then
    echo "✓ ddgr available (quick scans)"
else
    echo "✗ ddgr not installed (optional: brew install ddgr)"
fi

if command -v llm &> /dev/null && llm models list | grep -q perplexity; then
    echo "✓ perplexity available (deep research)"
else
    echo "✗ perplexity not configured (optional: llm install perplexity)"
fi

echo "✓ WebSearch available (built-in fallback)"
```

**Confidence**: HIGH (validated during this research session)
**Implementation**: Add to research kata setup section

---

## Recommendation 5: Evidence Level Refinement for Engineering

### Proposed Engineering-Specific Levels

| Level | Criteria | Examples |
|-------|----------|----------|
| **Very High** | Peer-reviewed, production-proven at scale, >10k stars | Academic papers, official framework docs, foundational OSS (Linux, PostgreSQL) |
| **High** | Expert practitioners at established companies, well-maintained projects >1k stars | Engineering blogs (FAANG, GitLab, Atlassian), popular frameworks (Django, React) |
| **Medium** | Community-validated, emerging consensus, >100 stars | Dev.to articles with engagement, emerging OSS tools, conference talks |
| **Low** | Single source, unvalidated, <100 stars or no corroboration | Personal blogs without peer review, brand new repos, anecdotal claims |

**Rationale**: Aligns with software engineering norms (GitHub stars as proxy for validation)

**Confidence**: MEDIUM (synthesized from general patterns, not explicitly stated in sources)

**Implementation**: Update evidence levels table in research kata

---

## Implementation Plan

### Phase 1: Template Creation (Immediate)

- [ ] Create `.raise/templates/tools/research-prompt.md`
- [ ] Add example research prompt for common scenario (e.g., "evaluate tech stack")
- [ ] Update template README to reference new prompt template

### Phase 2: Kata Updates (Next session)

- [ ] Add Step 1.5 (Create Research Prompt) to research kata
- [ ] Add tool availability checks to prerequisites
- [ ] Update evidence levels for engineering context
- [ ] Add delegation pattern diagram
- [ ] Include agent capability descriptions

### Phase 3: Validation (Before broader use)

- [ ] Test template with real research question (e.g., F1.1 lean spec factors)
- [ ] Validate tool fallback chain (ddgr → perplexity → WebSearch)
- [ ] Confirm prompt template produces quality outputs
- [ ] Iterate based on findings

### Phase 4: Documentation (Post-validation)

- [ ] Add research workflow example to framework docs
- [ ] Document tool installation (ddgr, llm, perplexity setup)
- [ ] Create quick reference card for when to use each depth level

---

## Trade-offs Analysis

### Accept: More Upfront Structure

**Cost**: 15-30 minutes to create research prompt vs immediate ad-hoc search
**Benefit**: Reproducible, auditable research; clear quality criteria
**RaiSE Alignment**: Observable Workflow, Governance as Code

**Verdict**: Accept. Investment pays off in research quality and traceability.

### Accept: Tool Availability Variance

**Cost**: Need fallback logic; can't guarantee perplexity available
**Benefit**: Works in any environment; graceful degradation
**RaiSE Alignment**: Platform Agnosticism

**Verdict**: Accept. Tiered approach handles this.

### Accept: Human Validation Gate

**Cost**: Requires human review of research outputs
**Benefit**: Epistemological rigor maintained; prevents AI hallucination propagation
**RaiSE Alignment**: Humans Define, Machines Execute

**Verdict**: Accept. Non-negotiable for research quality.

---

## Risks & Mitigations

### Risk 1: Template Too Complex for Simple Research

**Likelihood**: Medium
**Impact**: Low (slows down quick scans)

**Mitigation**:
- Provide "lite" version for quick-scan depth
- Include autocomplete snippets for common sections
- Document when to skip optional sections

### Risk 2: Tool Installation Friction

**Likelihood**: High (ddgr, llm not preinstalled)
**Impact**: Medium (degrades to WebSearch fallback)

**Mitigation**:
- Clear installation docs with one-liners
- Fallback chain ensures functionality without tools
- Document WebSearch as reliable baseline

### Risk 3: Prompt Template Becomes Stale

**Likelihood**: Medium (as prompt engineering evolves)
**Impact**: Medium (suboptimal research quality)

**Mitigation**:
- Version template (currently v1.0)
- Schedule quarterly review of prompt engineering research
- Include "last reviewed" date in template frontmatter

### Risk 4: Over-Reliance on AI Research

**Likelihood**: Low (human gate prevents this)
**Impact**: High (if gate bypassed)

**Mitigation**:
- Mandate human validation in kata
- Include quality checklist in template
- Document examples of when AI research is insufficient

---

## Success Metrics

### Leading Indicators (Process)

- Research prompts created using template (target: 100% for standard/deep-dive)
- Tool availability check run before research (target: 100%)
- Evidence catalogs include source ratings (target: 100%)

### Lagging Indicators (Outcome)

- Major claims triangulated with 3+ sources (target: >80%)
- Research outputs referenced in ADRs (traceability)
- Time from research question to actionable recommendation (<8h for standard depth)

### Quality Indicators

- Confidence levels explicitly stated (target: 100%)
- Contrary evidence acknowledged when present (target: 100%)
- Human validation gate completed before using research in decisions (target: 100%)

---

## Next Steps

1. **Immediate**: Create research prompt template file
2. **This session**: Apply template to original question (lean spec factors for F1.1)
3. **Next kata session**: Update research kata with new steps
4. **Before F1.1 implementation**: Validate full workflow end-to-end

---

## Governance Linkage

### ADR Recommendation

Create ADR: "Research Workflow for RaiSE Framework"
- **Decision**: Adopt structured research prompt template with delegation pattern
- **Alternatives considered**: Ad-hoc research, fully manual process, pure AI research
- **Rationale**: Evidence-based (20 sources, HIGH confidence)
- **Status**: Proposed (pending Emilio approval)

### Backlog Impact

- **No impact on F1.1-F7.4 feature timeline** (research workflow is meta-process)
- **Enables**: Better decision quality for future ADRs, tech stack choices
- **Dependencies**: None (independent process improvement)

### Parking Lot Resolution

This research resolves the meta-question raised at session start: "How to properly research before planning features?"

**Status**: Resolved with actionable recommendation

---

## References

Full evidence catalog: `work/research/ai-research-prompts/sources/evidence-catalog.md`
Synthesis document: `work/research/ai-research-prompts/synthesis.md`

**Key sources**:
- [The Prompt Report](https://arxiv.org/abs/2406.06608) - Comprehensive taxonomy
- [Hybrid Framework for AI-Augmented Reviews](https://link.springer.com/article/10.1007/s11301-025-00522-8) - Epistemological principles
- [Evidence Triangulator](https://www.nature.com/articles/s41467-025-62783-x) - Two-step extraction pattern
- [Multi-Agent Patterns ADK](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/) - Delegation architecture

---

**Recommendation Status**: READY FOR REVIEW
**Confidence**: HIGH
**Next Action**: Human validation + decision to proceed with implementation

---

*Research completed: 2026-01-31*
*Total sources: 20 (7 Very High, 8 High, 5 Medium)*
*Research time: ~2 hours*
