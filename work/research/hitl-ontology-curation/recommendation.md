# Recommendation: HITL Ontology Curation for E3 — ScaleUp Agent

> Actionable design for Eduardo Luna's curation workflow.

---

## Executive Summary

The literature converges on a clear pattern: **LLMs draft, experts validate**. For the Scaling Up ontology, we should build a conversational curation workflow where the agent proposes ontology elements and Eduardo validates/corrects through natural conversation -- no graph editors, no ontology tools, no programming.

The optimal expert involvement is approximately **20% of total ontology assertions** requiring deep review, with the remaining 80% either auto-accepted at high confidence or batch-approved with minimal cognitive load. Eduardo's weekly time commitment should be **1-2 sessions of 20-30 minutes each**.

---

## Recommended Architecture: Three-Phase Curation

### Phase 1: LLM Extraction (No expert involvement)

The agent extracts candidate ontology elements from Scaling Up source materials:
- **Concepts**: "BHAG", "One-Page Strategic Plan", "Rockefeller Habits Checklist"
- **Relationships**: "BHAG is-a strategic goal", "Cash Flow feeds-into financial health"
- **Definitions**: Plain-language descriptions of each concept
- **Provenance**: Book chapter, page number, or source reference for each assertion

Each assertion gets a confidence score based on:
- Source clarity (explicit definition in book vs. implied)
- Consistency with other extracted assertions
- Number of supporting source passages

### Phase 2: Confidence-Based Routing

| Confidence Tier | Threshold | Action | Eduardo's Role |
|----------------|-----------|--------|----------------|
| **High** | >85% | Auto-queued for batch approval | Scan and approve in batches of 10-20 |
| **Medium** | 50-85% | Queued for review | Read proposed assertion + source, accept/modify/reject |
| **Low** | <50% | Flagged for discussion | Conversational exploration: "I found this but I'm not sure..." |
| **Structural** | Any | Always reviewed | Any proposed hierarchy or framework-level relationship |

**Key design principle**: Eduardo never sees the confidence score. He sees either:
- A batch of items to quickly approve ("These look right? Yes/No for each")
- Individual items needing his judgment ("What's the relationship between X and Y?")
- Open questions ("I'm not sure about this -- can you help me understand?")

### Phase 3: Conversational Curation Sessions

The interface is a **structured conversation**, not a form or editor.

**Session Flow (20-30 minutes):**

1. **Opening context** (1 min): "Since last session, I've processed Chapter 5. I have 3 items that need your expertise and 12 items for quick approval."

2. **Deep review first** (10-15 min): Present the 2-4 hardest items while Eduardo is fresh.
   - Agent: "I extracted that the 'Rockefeller Habits' are a component of Scaling Up. But in some sources they seem like a predecessor, not a component. Which is more accurate?"
   - Eduardo responds in plain language
   - Agent reformulates as ontology assertion, confirms with Eduardo

3. **Batch approval** (5-10 min): Show 10-15 high-confidence items for quick scan.
   - Agent: "Here are the concepts I extracted from Chapter 5. Anything wrong or missing?"
   - Eduardo scans, flags any issues
   - Unmarked items are approved

4. **Completeness check** (2-5 min): Ask about gaps.
   - Agent: "For the People section, I have: hiring, values alignment, performance management. Am I missing anything critical?"
   - Eduardo adds what's missing

5. **Closing** (1 min): Summary of what was decided, what's queued for next session.

---

## The Four Expert-Only Functions

Based on the research, Eduardo is irreplaceable for exactly four things:

### 1. Structural Validation
**Why:** LLMs produce structural hallucinations -- fabricated concepts placed in central positions. Eduardo validates the ARCHITECTURE, not just individual terms.

**Implementation:** After initial extraction, present Eduardo with a high-level concept map (text-based, not graphical). "Here's how I understand Scaling Up is organized. Is this right?"

### 2. Completeness Review
**Why:** LLMs achieve only 44% recall -- they confirm what they find but miss what they don't know. Eduardo catches gaps.

**Implementation:** Per-module completeness questions. "For the Cash chapter, I have these 7 concepts. What am I missing?"

### 3. Nuance Resolution
**Why:** LLM accuracy drops to 50-60% on ambiguous, interpretation-heavy content. Business methodology IS interpretation-heavy content.

**Implementation:** Present ambiguous items as questions, not assertions. "Is X more like A or more like B?" rather than "X is A -- approve?"

### 4. Priority Assignment
**Why:** LLMs treat all concepts equally. Only Eduardo knows which are CORE to coaching practice vs. PERIPHERAL.

**Implementation:** After extraction, ask Eduardo to tier concepts: "Must-have for any Scaling Up engagement" vs. "Advanced/situational" vs. "Background/reference."

---

## Conversation Design Principles

These principles emerge directly from the research on expert fatigue, conversational ontology engineering, and non-technical expert interfaces:

1. **Never use ontology terminology.** No "classes," "properties," "axioms," "triples." Use Scaling Up language: "concepts," "relationships," "frameworks," "tools."

2. **Always show provenance.** "I found this in Chapter 3, page 47" enables faster review than raw assertions.

3. **Questions, not statements.** "Is this right?" not "I've determined that..." Framing as questions respects Eduardo's authority and invites correction.

4. **Hard first, easy last.** Ambiguous items when fresh, batch approvals as cooldown.

5. **Bounded sessions.** 20-30 minutes max. "We've covered a lot -- let's pick this up next time" is a valid session end.

6. **Incremental, not monolithic.** Don't dump 200 concepts for review. Process one chapter/module at a time.

7. **Correction is teaching.** Every correction Eduardo makes improves future extractions. Make this visible: "Got it -- I'll apply this pattern to similar concepts."

---

## Estimated Expert Time Budget

Based on the Scaling Up corpus (approximately 300-400 key concepts, 500-800 relationships):

| Activity | Items | Time per item | Total time | Sessions |
|----------|-------|---------------|------------|----------|
| Structural validation (framework-level) | 5-8 frameworks | 10-15 min each | 1-2 hours | 3-4 |
| Deep concept review (medium confidence) | 60-80 items | 2-3 min each | 2-4 hours | 5-8 |
| Batch approval (high confidence) | 200-300 items | 10-15 sec each | 1-1.5 hours | 3-4 |
| Completeness review (per module) | 8-10 modules | 5-10 min each | 1-1.5 hours | 2-3 |
| Priority tiering | 300-400 items | 5-10 sec each | 0.5-1 hour | 1-2 |
| **Total** | | | **6-10 hours** | **14-21 sessions** |

At 2 sessions per week of 25 minutes each, this is **7-11 weeks** to curate the complete Scaling Up ontology.

This is the Pareto frontier: approximately **8 hours of Eduardo's time** to produce a domain-expert-validated ontology that would take 40+ hours to build from scratch manually.

---

## Technical Implementation Notes

### What Eduardo sees (conversational interface):
- WhatsApp-style conversation or simple web chat
- Plain text with occasional bullet lists
- No diagrams, no forms, no technical UI

### What the system does behind the scenes:
- Maintains ontology in structured format (YAML/JSON, not OWL)
- Tracks confidence scores and provenance
- Records Eduardo's corrections as training signal
- Implements the routing logic
- Generates session agendas based on pending review queue

### Integration with E3 Agent:
- The curated ontology becomes the agent's knowledge base
- Eduardo's corrections directly improve agent advice quality
- The agent can cite provenance in its responses ("Per Scaling Up Chapter 4...")
- Ongoing curation as Eduardo encounters edge cases in coaching

---

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Eduardo finds sessions tedious, stops engaging | Medium | Keep sessions short (20 min), show impact of his contributions, respect his time |
| LLM extracts plausible-but-wrong concepts from Scaling Up | High | Always show provenance, structured review catches these |
| Ontology becomes stale as Eduardo's practice evolves | Medium | Monthly 15-min "what's changed?" check-ins after initial curation |
| Overloading Eduardo with too many items per session | Low | Hard cap of 20 review items per session, system manages the queue |
| Eduardo's corrections don't generalize to similar concepts | Medium | Explicitly ask: "Should I apply this to similar cases?" when he corrects |

---

## Decision: Recommended Approach

**Build a conversational curation workflow** with these characteristics:

1. **Agent-proposes, expert-validates** architecture
2. **Confidence-based routing** to minimize expert decisions
3. **Conversational interface** -- no technical tools
4. **Short sessions** (20-30 min, 2x/week)
5. **Module-by-module** processing (one Scaling Up chapter at a time)
6. **Provenance always visible** for efficient review
7. **Hard items first** to respect cognitive resources

This balances ontology quality (expert validation at every critical point) with sustainability (approximately 8 hours total expert time over 2-3 months).

---

*Recommendation finalized: 2026-03-18*
*Confidence: HIGH on architecture, MEDIUM on time estimates*
*Next steps: Validate with Eduardo (does this workflow feel right?), prototype the conversation flow*
