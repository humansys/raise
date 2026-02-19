# Evidence Catalog: RES-METACOG-001

## Sources

### S1: AutoMeco — LLMs Have Intrinsic Meta-Cognition (arXiv:2506.08410, Jun 2025)
- **Type**: Primary (preprint)
- **Evidence Level**: High
- **Key Finding**: LLMs have latent meta-cognitive ability measurable via "lenses" (entropy, perplexity, max probability). MIRA strategy improves detection in 61-68% of cases by modeling reasoning as Markov chain. Training-free, <0.03ms latency.
- **Relevance**: Confirms LLMs can self-assess accuracy. But requires internal model state access (logits) — not available via API. Useful as theoretical grounding, not implementable directly.

### S2: Hindsight — Agent Memory with Confidence (arXiv:2512.12818, Dec 2025)
- **Type**: Primary (preprint + open source)
- **Evidence Level**: High
- **Key Finding**: Four memory networks (world, experience, opinion, observation) with epistemic separation. Opinions have confidence scores c∈[0,1]. Reinforcement mechanism: supporting evidence → +c, contradiction → -c (doubled penalty). Abstention as evaluation category.
- **Relevance**: Most directly applicable. Confidence per memory item + abstention = what we want. But requires graph restructuring we don't need.

### S3: SAGE — Self-Evolving Agents with Reflection (arXiv:2409.00872, 2024)
- **Type**: Primary (preprint)
- **Evidence Level**: Medium
- **Key Finding**: Dual memory (STM/LTM) with Ebbinghaus-based retention. Reflection generates self-assessments from output + reward. Threshold-based memory tiering (STM→LTM→discard).
- **Relevance**: Reflection mechanism is relevant — Rai already does reflection in /story-review. Gap detection via checker feedback loop.

### S4: KG Quality Management Survey (Peking University, 2024)
- **Type**: Primary (survey)
- **Evidence Level**: High
- **Key Finding**: Three KG quality dimensions: completeness, accuracy, consistency. Completeness = schema completeness (all required properties) + population completeness (all expected instances). Gap detection via reference dataset comparison.
- **Relevance**: Directly applicable. Our graph has a known schema (19 node types) — we can measure population per type against expectations.

### S5: Competency Questions for Ontology Evaluation (Multiple sources, 2019-2024)
- **Type**: Primary (multiple peer-reviewed)
- **Evidence Level**: Very High
- **Key Finding**: CQs define what a knowledge base should answer. Five types: Scoping, Validating, Foundational, Relationship, Metaproperty. If a CQ can't be answered, that's a gap.
- **Relevance**: We can define CQs for our graph: "What patterns apply to the memory module?" "What decisions constrain the CLI layer?" If unanswerable → gap.

### S6: Metacognition and Uncertainty in LLMs (Steyvers & Peters, 2025)
- **Type**: Primary (peer-reviewed, Sage journals)
- **Evidence Level**: Very High
- **Key Finding**: LLMs and humans both tend to be overconfident. Metacognitive sensitivity (confidence diagnostic of accuracy) is similar between humans and LLMs. Calibration is the key challenge.
- **Relevance**: Warns against trusting LLM self-assessment blindly. Our approach should use structural/deterministic indicators, not LLM introspection alone.

### S7: LLMs Lack Metacognition for Medical Reasoning (Nature Communications, 2024)
- **Type**: Primary (peer-reviewed, Nature)
- **Evidence Level**: Very High
- **Key Finding**: Despite high accuracy on MCQ, models fail to recognize knowledge limitations. Provide confident answers even when correct options are absent. Significant metacognitive deficiencies.
- **Relevance**: Critical warning. LLM-based confidence is unreliable. Structural/deterministic indicators are more trustworthy.

### S8: Uncertainty Quantification Survey (arXiv:2503.15850, 2025)
- **Type**: Primary (survey, KDD 2025)
- **Evidence Level**: High
- **Key Finding**: LLM uncertainty sources: input ambiguity, reasoning divergence, decoding stochasticity. Calibration methods: conformal prediction, verbalized confidence, consistency-based. Agent applications: uncertainty threshold → decide whether to accept answer or keep exploring.
- **Relevance**: Threshold-based approach applicable: if Rai's knowledge coverage for a topic is below threshold, flag it.

### S9: MeCo — Metacognition-Oriented Tool Trigger (arXiv:2502.12961, 2025)
- **Type**: Primary (preprint)
- **Evidence Level**: Medium
- **Key Finding**: LLM self-assesses capability before deciding if external tools needed. Metacognitive trigger: "Do I know enough to answer this, or should I use a tool?"
- **Relevance**: Analog for our case: "Does the graph have enough context for this story, or are there gaps that need filling?"

### S10: Self-Improving Agents Require Metacognitive Learning (arXiv:2506.05109, 2025)
- **Type**: Primary (position paper)
- **Evidence Level**: Medium
- **Key Finding**: Three components: metacognitive knowledge (self-assessment), metacognitive planning (deciding what to learn), metacognitive evaluation (reflecting on learning). Self-improving agents with intrinsic metacognition achieve sustained progress.
- **Relevance**: Maps to our three indicators: coverage (knowledge), confidence (planning), gaps (evaluation).

### S11: KG Completeness Systematic Literature Review (HAL, 2022)
- **Type**: Primary (systematic review)
- **Evidence Level**: High
- **Key Finding**: Seven types of completeness identified. Schema completeness (required properties present) and population completeness (expected instances exist) are most measurable. 56 articles, 9 assessment tools identified.
- **Relevance**: Schema completeness maps directly to our node type expectations. Population completeness maps to "are there enough patterns/sessions/etc."

### S12: RaiSE Graph Structure (Internal, 2026)
- **Type**: Primary (our own system analysis)
- **Evidence Level**: Very High
- **Key Finding**: 19 node types, 11 edge types, 1,244 nodes, 16,884 edges. Validation has 4 checks (edge integrity, cycles, reachability, completeness) with significant gaps. 97.7% of edges are keyword-heuristic `related_to`. Completeness check only covers 3 of 19 types.
- **Relevance**: Baseline for meta-cognition. We know exactly what we have and what we should check.
