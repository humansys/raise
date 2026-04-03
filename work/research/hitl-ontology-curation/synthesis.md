# Synthesis: HITL Ontology Curation

> Triangulated claims, patterns, gaps, and contrary evidence.

---

## Claim 1: LLMs are competent drafters but unreliable validators of ontological knowledge

**Confidence: HIGH** (5+ independent sources)

**Supporting Evidence:**
- LLM-generated definitions are acceptable but statistically significantly below human-curated ones [DRAGON-AI]
- LLM outputs approach novice human modeler quality, not expert quality [SWJ-Systematic-Review]
- 65% agreement with human reviewers on ontology extraction [OntoGPT-SPIRES]
- 90%+ accuracy on well-defined categories but 50-60% on ambiguous ones [Bio-Ontology-LLM-Review]
- 88% precision but 44% recall on KG validation — good at confirming, bad at catching gaps [KG-Validation-LLM-HITL]

**Contrary Evidence:**
- None found. All sources agree LLMs are useful drafters but insufficient alone.

**Implication for E3:** The LLM can draft the Scaling Up ontology (concepts, relationships, definitions) with acceptable quality for REVIEW, but cannot be trusted to self-validate. Eduardo's review is not optional -- it is the quality gate.

---

## Claim 2: The domain expert is irreplaceable at four specific points in the pipeline

**Confidence: HIGH** (4+ independent sources per point)

The literature converges on four irreplaceable expert functions:

### 2a. Structural validation — Are the relationships correct?

LLMs produce "structural hallucinations" where fabricated concepts are elevated to the highest-centrality positions in generated graphs [Structural-Hallucination]. The expert must validate not just individual terms but the ARCHITECTURE of relationships.

**Expert task:** "Is BHAG really a sub-concept of Strategic Goals, or is it its own framework that INTERSECTS with goals?"

### 2b. Completeness review — What's missing?

LLMs achieve 88% precision but only 44% recall [KG-Validation-LLM-HITL]. They confirm what they find but miss what they don't know about. Only the domain expert can identify gaps.

**Expert task:** "This looks right, but you're missing the Cash Conversion Cycle -- that's critical in Scaling Up."

### 2c. Nuance and context — When does this apply?

Accuracy drops dramatically for ambiguous, interpretation-heavy content [Bio-Ontology-LLM-Review, OntoGPT-SPIRES]. Business methodology is almost entirely in this category.

**Expert task:** "The Rockefeller Habits are a precursor to Scaling Up, not a component. They overlap but aren't the same."

### 2d. Priority and salience — What matters most?

LLMs treat all extracted concepts equally. Only the expert knows which concepts are CORE vs. PERIPHERAL for practical coaching application.

**Expert task:** "The One-Page Strategic Plan is the centerpiece. Everything else feeds into it."

---

## Claim 3: Conversational interfaces work for non-technical ontology engineering

**Confidence: HIGH** (3 independent sources)

**Supporting Evidence:**
- OntoChat: Domain experts (N=6) successfully created user stories for ontology engineering through conversation, with no ontology engineering knowledge required [OntoChat-ESWC]
- 62.5% found conversational interaction intuitive; 87.5% found resulting concept clusters meaningful [OntoChat-Participatory]
- Participatory prompting (structured questions) improves elicitation quality over free-form conversation [OntoChat-Participatory]
- Form-based and card-sorting interfaces enable non-technical expert participation [Expert-Validation-Framework, WebProtege-Usability]

**Contrary Evidence:**
- OntoChat was tested with users who had SOME ontology familiarity (50% had ontology engineering experience). Truly naive users not fully tested.
- Small sample sizes (N=6, N=8).

**Implication for E3:** The conversational pattern is validated but needs to be even SIMPLER than OntoChat. Eduardo should never see ontology terminology. He sees Scaling Up concepts and validates them in Scaling Up language.

---

## Claim 4: The "propose-and-validate" pattern is the optimal HITL architecture

**Confidence: HIGH** (convergent evidence from multiple domains)

**Supporting Evidence:**
- DRAGON-AI: LLM proposes definitions, curators review and correct [DRAGON-AI]
- HyWay: LLM augments established methodology, expert validates [HyWay-NeOn-LLM]
- SNOMED: Crowd/AI handles easy verifications, experts focus on hard tasks [SNOMED-Crowd]
- Wikidata: Best quality from balanced bot+human contribution [Wikidata-Quality]
- Systematic review: "LLMs as intelligent assistants where AI-generated drafts provide a foundation that domain experts refine" [SWJ-Systematic-Review]

**Pattern description:**
1. AI generates draft (concepts, relationships, definitions)
2. System assigns confidence scores
3. High-confidence items auto-accepted (or auto-presented for lightweight approval)
4. Medium-confidence items queued for expert review
5. Low-confidence items flagged for expert discussion
6. Expert corrections feed back into the system

**Contrary Evidence:**
- No evidence that fully autonomous ontology construction achieves acceptable quality for domain-critical applications.

---

## Claim 5: Expert review sessions should be short, batched, and front-loaded with hard decisions

**Confidence: MEDIUM** (2 direct sources + general cognitive science)

**Supporting Evidence:**
- Brain optimal for 90 minutes; 20-minute breaks needed [Annotation-Fatigue-Pareto]
- Subjective judgment tasks cause faster burnout than mechanical tasks [Annotation-Fatigue-Pareto]
- Decision quality degrades predictably; batch similar decisions, prioritize complex ones early [Decision-Fatigue-Neuroscience]
- Review effectiveness drops sharply after 90 minutes [Annotation-Fatigue-Pareto]

**Derived Design Constraints:**
- Review sessions: 15-30 minutes (not the full 90 — Eduardo is a busy executive, not a paid annotator)
- Batch similar concept types (all "tools" together, all "frameworks" together)
- Present ambiguous/hard items FIRST when cognitive resources are highest
- Easy approvals (yes/no on clearly correct items) at the END as cooldown
- Target: 10-20 review decisions per session

**Gap:** No direct study on ontology curation session optimization. These are extrapolated from annotation fatigue and cognitive science.

---

## Claim 6: Confidence-based routing reduces expert workload by 60-80%

**Confidence: MEDIUM** (indirect evidence, quantitative extrapolation)

**Supporting Evidence:**
- LLMs achieve 65-90% accuracy on well-defined concepts [multiple sources]
- Confidence routing: >90% auto-accept, 50-89% review, <50% escalate [Confidence-Routing]
- SNOMED: Crowd (analogous to AI) handles easy tasks, experts focus on hard 20% [SNOMED-Crowd]
- 21% disagreement rate in full LLM pipeline [Kommineni-2024]

**Extrapolation:**
If LLMs correctly handle 70-80% of ontology assertions at high confidence, and another 10-15% at medium confidence need only lightweight approval, then the expert deeply reviews only 10-20% of total assertions. This is the Pareto frontier.

**Gap:** No direct measurement of workload reduction in ontology curation specifically. The 60-80% reduction is estimated from accuracy rates across multiple studies.

---

## Claim 7: Evidence provenance is essential for expert trust and efficient review

**Confidence: HIGH** (convergent from multiple established workflows)

**Supporting Evidence:**
- Gene Ontology: Every annotation carries an evidence code (TAS, ISS, etc.) [GO-Curation-MGI]
- Wikidata: Reference Quality Verification pipeline verifies if triples are supported by documented sources [Wikidata-Quality]
- KG Curation Framework: Assessment phase defines quality metrics including provenance [KG-Curation-Framework]
- DRAGON-AI: LLM definitions sourced via RAG from specific documents [DRAGON-AI]

**Implication:** When the system shows Eduardo a proposed concept, it must also show WHERE it came from: "Source: Scaling Up, Chapter 4, p.73" or "Source: Verne Harnish interview, 2019." This enables efficient review (Eduardo can quickly assess "yes, that's right" or "no, that's taken out of context").

---

## Pattern: The Optimal Division of Labor

| Task | Who | Why |
|------|-----|-----|
| Extract candidate concepts from text | LLM | Mechanical, high-volume |
| Draft definitions | LLM | Acceptable quality for review |
| Propose relationships | LLM | Can identify many, misses nuance |
| Assign confidence scores | LLM | Enables routing |
| Validate structural architecture | Expert | Structural hallucination risk |
| Identify missing concepts | Expert | Low LLM recall (44%) |
| Resolve ambiguous relationships | Expert | 50-60% LLM accuracy on ambiguous |
| Prioritize concepts (core vs peripheral) | Expert | Domain salience judgment |
| Approve high-confidence items | Expert (lightweight) | Quick scan, batch approval |
| Final quality sign-off | Expert | Accountability |

---

## Gaps in the Literature

1. **No business methodology domain evidence.** All ontology curation research is in biomedical, music, or academic domains. Scaling Up is a business methodology -- different characteristics (less formal, more relational, more context-dependent).

2. **No longitudinal sustainability studies.** All HITL evaluations are short-term (single sessions or weeks). No evidence on whether expert engagement sustains over months of incremental curation.

3. **No cost-benefit analysis.** No study quantifies expert hours vs. ontology quality improvement to find the inflection point.

4. **No conversational curation tool for truly non-technical experts.** OntoChat is the closest but still assumes some familiarity with ontology concepts. A pure conversational validator for business experts does not exist in the literature.

5. **Active learning for ontology curation is underexplored.** While active learning is well-studied for annotation tasks, its application to ontology curation (learning WHICH items to escalate based on expert correction patterns) has minimal direct evidence.

---

*Synthesis completed: 2026-03-18*
*Methodology: Triangulation across 20 sources, minimum 3 sources per HIGH-confidence claim*
