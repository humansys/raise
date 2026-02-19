# Evidence Catalog: RES-TEMPORAL-001

## Sources

### S1: FadeMem (arXiv:2601.18642, Jan 2025)
- **Type**: Primary (peer-reviewed preprint)
- **Evidence Level**: High
- **Key Finding**: Biologically-inspired dual-layer memory with adaptive exponential decay. Retains 82.1% of critical facts at 55% storage vs Mem0's 78.4% at 100%.
- **Relevance**: Most detailed decay formula found. Directly applicable decay function with importance modulation.
- **Formula**: `v_i(t) = v_i(0) * exp(-λ_i * (t - τ_i)^β_i)` where `λ_i = λ_base * exp(-μ * I_i(t))`

### S2: Zep/Graphiti (arXiv:2501.13956, Jan 2025)
- **Type**: Primary (peer-reviewed preprint)
- **Evidence Level**: High
- **Key Finding**: Bi-temporal model (t_valid/t_invalid) tracks fact validity periods. No explicit decay function — uses LLM-based contradiction detection to invalidate edges. Last-write-wins.
- **Relevance**: Sophisticated temporal tracking but requires LLM calls for conflict resolution. Too heavy for our use case.

### S3: Stanford Generative Agents (Park et al., ACM 2023)
- **Type**: Primary (peer-reviewed, ACM)
- **Evidence Level**: Very High
- **Key Finding**: Memory retrieval = weighted sum of recency + importance + relevance. Recency = exponential decay with factor 0.995 per game hour. Importance = LLM-scored 1-10.
- **Relevance**: Canonical reference. The three-factor model is the most widely adopted. Simple, proven.
- **Formula**: `score = α_recency * recency + α_importance * importance + α_relevance * relevance`

### S4: ACT-R Base-Level Learning (Anderson et al., cognitive science)
- **Type**: Primary (foundational cognitive science)
- **Evidence Level**: Very High
- **Key Finding**: `B_i = ln(Σ t_j^-d)` where d=0.5. Power-law decay, not exponential. Each access adds to activation. Approximation: `B_i = ln(n/(1-d)) - d * ln(L)`.
- **Relevance**: Theoretical foundation. Power-law is more accurate than exponential for human memory, but exponential is simpler to implement and "good enough" for engineering.

### S5: MemoryBank (arXiv:2305.10250, 2023)
- **Type**: Primary (preprint)
- **Evidence Level**: Medium
- **Key Finding**: Ebbinghaus curve `R = e^(-t/S)`. S (strength) initialized at 1, increments on each access, t resets to 0 on access.
- **Relevance**: Simplest implementation found. S as integer counter is elegant for our JSONL pattern model.

### S6: Mem0 (arXiv:2504.19413, Apr 2025)
- **Type**: Primary (preprint)
- **Evidence Level**: High
- **Key Finding**: No explicit decay function. Uses relevance-based retrieval + LLM-powered deduplication/contradiction resolution. "Forgets" by surfacing only most relevant.
- **Relevance**: Validates that explicit forgetting is not the only approach. Relevance-first retrieval is a viable alternative for smaller corpora.

### S7: A-Mem (arXiv:2502.12110, Feb 2025)
- **Type**: Primary (NeurIPS 2025)
- **Evidence Level**: High
- **Key Finding**: No explicit temporal decay. Memory evolves through linking and contextual updates. Cosine similarity for retrieval.
- **Relevance**: Confirms that evolution > forgetting for knowledge that remains valid. Patterns that are still true shouldn't decay.

### S8: OpenClaw Issue #5547 (GitHub, 2025)
- **Type**: Secondary (practitioner implementation)
- **Evidence Level**: Medium
- **Key Finding**: Half-life decay model: `recencyScore = exp(-decayRate * ageInHours)` where `decayRate = ln(2) / halfLifeHours`. Applied as post-processing step. ~60-80 lines of code. Supports pinnedPaths exemption.
- **Relevance**: Most pragmatic implementation found. Post-processing approach matches our architecture perfectly. PinnedPaths = our `foundational` flag.

### S9: Frontiers Psychology (2025) — Cross-Attention Memory Retrieval
- **Type**: Primary (peer-reviewed)
- **Evidence Level**: Medium
- **Key Finding**: LLM-trained cross-attention networks improve retrieval over Stanford's weighted-sum approach. But requires training infrastructure.
- **Relevance**: Confirms Stanford formula as baseline. Improvement requires ML pipeline we don't have.

### S10: Multiple Memory Systems (arXiv:2508.15294, 2025)
- **Type**: Primary (preprint)
- **Evidence Level**: Medium
- **Key Finding**: Dual-layer (short-term/long-term) with different decay rates. Consolidation from STM to LTM based on access patterns.
- **Relevance**: Supports tiered approach but we only have one pattern store (JSONL). Tiering adds complexity we may not need.

### S11: MarkTechPost — Persistent Memory with Decay and Self-Evaluation (Nov 2025)
- **Type**: Tertiary (blog synthesis)
- **Evidence Level**: Low
- **Key Finding**: Recommends combining decay with self-evaluation (agent rates own memory quality). Suggests periodic pruning sweeps.
- **Relevance**: Self-evaluation idea interesting for meta-cognition (RAISE-171), not for this research.

### S12: RES-MEMORY-002 (Internal, Feb 2026)
- **Type**: Primary (our own systematic research)
- **Evidence Level**: High (50+ sources, triangulated)
- **Key Finding**: Gap E identified: "All patterns have equal weight regardless of age or validation — severity Medium, will degrade as pattern count grows."
- **Relevance**: Directly motivates this research. Confirms the problem from our own analysis.
