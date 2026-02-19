# RQ2: Semantic Compression & Information Density -- Evidence Catalog

> **Research date:** 2026-02-18
> **Status:** First pass complete
> **Confidence:** High (12+ peer-reviewed sources, multiple triangulated claims)

---

## Key Concepts & Definitions

### Semantic Density
The amount of task-relevant meaning encoded per token in a context window. No single formal definition exists in the literature, but the concept operates at the intersection of:
- **Shannon entropy** (bits per symbol in a message)
- **Kolmogorov complexity** (shortest program that produces a string)
- **Minimum Description Length** (optimal trade-off between model complexity and data fit)

Natural language is highly redundant. Zipf's law shows a small set of frequent tokens accounts for most occurrences, and communicators routinely include redundant words. Most prose operates well below theoretical information density limits.

### Semantic Compression
Reducing token count while preserving task-relevant meaning. Distinct from:
- **Syntactic compression** (lossless text shortening -- abbreviations, whitespace removal)
- **Model compression** (quantization, pruning, distillation of model weights)
- **Lossy text compression** (summarization that may lose details)

Semantic compression specifically targets the gap between natural language's redundancy and the information-theoretic minimum needed to preserve meaning for a given task.

### Context Distillation
Training a model to internalize context information so it no longer needs to be provided explicitly. Originally used in the sense of fine-tuning (Anthropic, 2022), now also applied to methods that compress context into compact learned representations (soft tokens, memory slots).

### Minimum Viable Context (MVC)
The smallest representation of context that preserves all task-relevant information for a given query. Not a formal term in the literature but the operational goal of all prompt compression research. Task-dependent: the MVC for a summarization task differs from that for a QA task over the same document.

---

## Information-Theoretic Foundations

### Language Modeling Is Compression

- **Claim:** Prediction and compression are mathematically equivalent; any language model can function as a lossless compressor, and vice versa.
- **Source:** Deletang, Ruoss, et al., "Language Modeling Is Compression," ICLR 2024 (Google DeepMind)
- **Evidence Level:** Very High (peer-reviewed, ICLR oral, formal proofs)
- **Key Finding:** Chinchilla 70B (trained on text) compresses ImageNet patches to 43.4% of raw size (beating PNG at 58.5%) and LibriSpeech audio to 16.4% (beating FLAC at 30.3%). This demonstrates that language models learn general-purpose compression, not just linguistic patterns. Shannon's source coding theorem directly applies: a model's cross-entropy loss IS its compression rate.
- **URL:** https://arxiv.org/abs/2309.10668

### Kolmogorov Complexity and Transformers

- **Claim:** Transformers learn programs approximating Kolmogorov complexity; their pre-training objective is equivalent to approaching joint Kolmogorov complexity via MDL.
- **Source:** (1) "Bridging Kolmogorov Complexity and Deep Learning: Asymptotically Optimal Description Length Objectives for Transformers" (2025); (2) "Unifying Two Types of Scaling Laws from the Perspective of Conditional Kolmogorov Complexity" (2025)
- **Evidence Level:** High (theoretical, recent preprints with formal proofs)
- **Key Finding:** A minimizer of an asymptotically optimal description length objective achieves optimal compression for any dataset up to an additive constant. Transformers tend to learn the shortest program fitting the training set, consistent with MDL and Solomonoff induction. Pre-training LLMs is a computable approximation of the upper bound of joint Kolmogorov complexity.
- **URL:** https://arxiv.org/abs/2509.22445

### Shannon Entropy and Semantic Information

- **Claim:** Shannon's information theory deliberately excludes semantics; extending it to include meaning requires new frameworks (e.g., Carnap-Bar-Hillel logical information, Floridi's semantic information theory).
- **Source:** (1) Shannon, "A Mathematical Theory of Communication" (1948); (2) "Breaking through the classical Shannon entropy limit: A new frontier through logical semantics" (2025)
- **Evidence Level:** High (foundational theory + recent extensions)
- **Key Finding:** Generative transformers with attention mechanisms reduce *semantic* entropy (uncertainty about meanings, not just tokens). Farquhar et al. (2024, Nature) formalized "semantic entropy" for LLM hallucination detection -- measuring uncertainty over meaning clusters rather than individual token sequences. This is the closest the field has to a formal bridge between Shannon entropy and semantic content in LLMs.
- **URL:** https://www.nature.com/articles/s41586-024-07421-0

**Synthesis of foundations:** An LLM's cross-entropy loss measures its compression rate (Shannon). Its training objective approximates Kolmogorov complexity (shortest description). Therefore, the theoretical limit of context compression for a given LLM is bounded by the model's own perplexity on that content -- tokens the model can predict contribute zero additional information.

---

## Compression Techniques for LLM Context

### Taxonomy (from NAACL 2025 Survey)

Li, Liu, Su & Collier provide the authoritative taxonomy in "Prompt Compression for Large Language Models: A Survey" (NAACL 2025, Selected Oral):

1. **Hard prompt methods** -- operate on natural language tokens
   - Token pruning (remove low-information tokens)
   - Sentence/passage extraction (select relevant segments)
   - Abstractive rewriting (paraphrase for conciseness)
2. **Soft prompt methods** -- compress into learned representations
   - Gist tokens (learned compression of prompts)
   - Memory slots (autoencoder-style compression)
   - KV-cache compression (compress attention states)

**URL:** https://aclanthology.org/2025.naacl-long.368/ | GitHub: https://github.com/ZongqianLi/Prompt-Compression-Survey

---

### Hard Prompt Methods

#### LLMLingua (Microsoft Research, EMNLP 2023)

- **How it works:** Uses a small LM (GPT-2 or LLaMA-7B) to compute token perplexity. Low-perplexity tokens (highly predictable = low information) are removed. Coarse-to-fine: budget controller allocates compression across prompt sections, then token-level iterative compression preserves interdependencies.
- **Compression ratio:** Up to 20x with 1.5% performance loss on reasoning tasks
- **Semantic preservation:** Good at high compression; degrades on code tasks
- **Source:** Jiang et al., "LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models," EMNLP 2023
- **Evidence Level:** Very High (widely replicated, Microsoft Research, open source)
- **URL:** https://arxiv.org/abs/2310.05736

#### LLMLingua-2 (ACL 2024)

- **How it works:** Pivots from perplexity-based removal to token classification. XLM-RoBERTa fine-tuned on GPT-4-generated compression data classifies each token as keep/remove. Task-agnostic.
- **Compression ratio:** Similar to LLMLingua but 3-6x faster inference
- **Semantic preservation:** 95-98% accuracy retention; better generalization across tasks
- **Source:** Pan et al., "LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression," ACL 2024
- **Evidence Level:** Very High (peer-reviewed ACL, builds on proven approach)
- **URL:** https://arxiv.org/abs/2403.12968

#### LongLLMLingua (2024)

- **How it works:** Extends LLMLingua for long-context scenarios. Addresses "lost in the middle" by reranking document segments by relevance before compression.
- **Compression ratio:** ~4x with performance *improvement* of up to 21.4% on NaturalQuestions (GPT-3.5-Turbo)
- **Semantic preservation:** Compression can *improve* performance by removing distracting context
- **Source:** Jiang et al., 2024
- **Evidence Level:** High
- **URL:** https://arxiv.org/abs/2310.06839

#### Selective Context (Li et al., 2023)

- **How it works:** Computes self-information -log P(x_i | instruction) per token; removes low-information tokens.
- **Compression ratio:** Up to 32x with negligible loss in BERTScore, faithfulness, BLEU-4
- **Semantic preservation:** Good at moderate compression; rapid degradation under aggressive compression (drops to 48.67 ES at 8x on code tasks)
- **Source:** Li et al., 2023
- **Evidence Level:** High
- **Caveat:** Performance degrades faster than LLMLingua methods under tight budgets

#### RECOMP (ICLR 2024)

- **How it works:** Two compressors for RAG: (1) extractive -- selects relevant sentences via contrastive learning; (2) abstractive -- encoder-decoder model distilled from GPT-3/4 synthesizes multi-document summaries.
- **Compression ratio:** Extractive: 11% token retention; Abstractive: 5% token retention
- **Semantic preservation:** Extractive loses 2.4 EM on HotpotQA; Abstractive loses 2 EM on NQ, 3.7 on TQA
- **Source:** Xu et al., "RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation," ICLR 2024
- **Evidence Level:** Very High (ICLR, empirical results across multiple benchmarks)
- **URL:** https://openreview.net/forum?id=mlJLVigNHp
- **Key Insight:** Extractive works better for multi-hop reasoning; abstractive works better for factoid QA. Task type determines optimal compression strategy.

#### Semantic Compression for Context Extension (ACL 2024 Findings)

- **How it works:** Inspired by source coding in information theory. Pre-trained model reduces semantic redundancy of long inputs before passing to LLM. No fine-tuning required.
- **Compression ratio:** 6:1 (generalizes to texts 6-8x longer than training)
- **Semantic preservation:** Llama 2 retains >90% accuracy on pass-key retrieval at 60,000+ tokens
- **Source:** "Extending Context Window of Large Language Models via Semantic Compression," ACL 2024 Findings
- **Evidence Level:** High
- **URL:** https://aclanthology.org/2024.findings-acl.306/

---

### Soft Prompt Methods

#### Gist Tokens (Mu et al., NeurIPS 2023)

- **How it works:** Fine-tunes LLM with modified attention masks that force prompt information through a small number of "gist" token positions. Zero-shot: given a new prompt, the model predicts gist tokens without additional training.
- **Compression ratio:** Up to 26x prompt compression
- **Semantic preservation:** Minimal loss in output quality; up to 40% FLOPs reduction, 4.2% wall time speedup
- **Source:** Mu, Li & Goodman, "Learning to Compress Prompts with Gist Tokens," NeurIPS 2023
- **Evidence Level:** Very High (NeurIPS, open source, widely cited)
- **URL:** https://arxiv.org/abs/2304.08467
- **Limitation:** Works for relatively short prompts; less effective for very long contexts

#### ICAE -- In-Context Autoencoder (ICLR 2024)

- **How it works:** Adds a lightweight encoder (<1% additional parameters) to an LLM. Pre-trained with autoencoding + language modeling objectives on massive text, then fine-tuned on instruction data. Compresses context into "memory slots" (dense vectors).
- **Compression ratio:** 4x context compression (based on Llama)
- **Semantic preservation:** Memory slots accurately represent original context; validated on instruction-following tasks
- **Source:** Ge et al., "In-context Autoencoder for Context Compression in a Large Language Model," ICLR 2024
- **Evidence Level:** Very High (ICLR, formal evaluation)
- **URL:** https://arxiv.org/abs/2307.06945

#### AutoCompressors (Chevalier et al., 2023)

- **How it works:** LLM recursively compresses long text into "summary vectors" at fixed intervals. Model is fine-tuned to both produce and consume these compressed representations.
- **Compression ratio:** Variable, depending on summary vector count
- **Semantic preservation:** Moderate; requires training and recursive computation
- **Source:** Chevalier et al., 2023
- **Evidence Level:** High
- **Limitation:** ~7x longer training time than CCM approach

#### Compressed Context Memory -- CCM (ICLR 2024)

- **How it works:** Compresses context key/value pairs for online (streaming) scenarios. Uses conditional adapter with parallelized training. Compresses 64 tokens to size 2 at each step.
- **Compression ratio:** 32x per compression step (64 -> 2 tokens)
- **Semantic preservation:** Validated on multi-task learning, personalization, conversation
- **Source:** Kim et al., "Compressed Context Memory for Online Language Model Interaction," ICLR 2024
- **Evidence Level:** Very High (ICLR, with code release)
- **URL:** https://arxiv.org/abs/2312.03414

#### Nugget / Nugget2D (Qin & Van Durme, 2023-2024)

- **How it works:** Neural Agglomerative Embeddings -- encodes text into compressed "nugget" representations. Nugget2D extends to decoder-only LMs, modeling history as compressed nuggets trained for reconstruction.
- **Compression ratio:** 20x with 98% BLEU for reconstruction
- **Semantic preservation:** Near-lossless at reported ratios
- **Source:** Qin & Van Durme, 2023; Nugget2D variant, 2024
- **Evidence Level:** High
- **URL:** https://arxiv.org/abs/2310.02409

---

### KV-Cache and Attention-Level Compression

#### LazyLLM (Apple, ICML 2024 Workshop)

- **How it works:** Dynamic token pruning -- selectively computes KV only for tokens important for next-token prediction, in both prefilling and decoding stages.
- **Compression ratio:** Significant FLOP reduction (varies by task)
- **Source:** Fu & Cho et al., Apple ML Research, ICML 2024
- **Evidence Level:** High
- **URL:** https://arxiv.org/abs/2407.14057

---

## Empirical Studies: Compressed vs. Verbose Context

### Lost in the Middle (Liu et al., TACL 2024)

- **Claim:** LLM performance degrades by 15-20 percentage points when relevant information is in the middle of the context vs. beginning or end.
- **Source:** Liu et al., "Lost in the Middle: How Language Models Use Long Contexts," TACL 2024
- **Evidence Level:** Very High (highly cited, replicated)
- **Key Finding:** Accuracy drops from 70-75% to 55-60% based purely on position. Caused by: (1) causal attention bias toward initial tokens, (2) RoPE long-term decay. This means compression that *removes* irrelevant middle content can actually *improve* performance (as shown by LongLLMLingua's +21.4% improvement).
- **URL:** https://arxiv.org/abs/2307.03172

### Context Length Alone Hurts Performance (2025)

- **Claim:** Even with perfect retrieval, longer context degrades LLM performance.
- **Source:** "Context Length Alone Hurts LLM Performance Despite Perfect Retrieval," 2025
- **Evidence Level:** High (preprint, but consistent with "Lost in the Middle")
- **URL:** https://arxiv.org/abs/2510.05381
- **Key Finding:** More context is not always better. There is an optimal context size for any task, beyond which performance decreases. This directly supports the MVC concept.

### Compression Can Improve Accuracy

- **Claim:** Removing noise/irrelevant context via compression can improve downstream task performance, not just reduce cost.
- **Evidence from multiple sources:**
  - LongLLMLingua: +21.4% on NaturalQuestions with 4x fewer tokens
  - RECOMP extractive: competitive with full context at 11% token retention
  - Semantic compression: >90% accuracy maintained at 6:1 ratio
- **Evidence Level:** High (triangulated across 3+ independent studies)
- **Mechanism:** Compression acts as a relevance filter, removing distractors that cause attention dilution.

### Structured vs. Natural Language Representations

- **Claim:** Programming language (Python) representations of knowledge graphs outperform both natural language and JSON for LLM reasoning.
- **Source:** Multiple 2024 studies on KG-LLM integration
- **Evidence Level:** Medium (emerging area, not yet fully standardized benchmarks)
- **Key Insight:** Format matters for information density. Structured representations can encode more task-relevant information per token than prose, but the optimal format depends on the model and task.

---

## Theoretical Limits

### Is There a "Shannon Limit" for Semantic Compression?

**Short answer:** Not yet formalized, but the components exist.

**What theory tells us:**

1. **Lower bound = model perplexity on the content.** From "Language Modeling Is Compression" (ICLR 2024): an LLM's cross-entropy loss on a text IS its compression rate. Tokens the model can predict from context carry zero additional information. Therefore, the theoretical minimum context for a perfect LLM is the incompressible residual -- the content that the model cannot predict from its weights alone.

2. **Kolmogorov complexity sets the absolute floor.** The shortest program producing the context is the theoretical minimum description. LLM pre-training approximates this. But Kolmogorov complexity is uncomputable -- we can only approximate it.

3. **Task-conditional compression can go further.** If you only need information relevant to a specific task, the minimum is the conditional Kolmogorov complexity K(answer | question, model_weights). Much context is irrelevant to any given query, so task-conditional compression ratios can far exceed general compression.

4. **Empirical ceiling: ~20-30x for general tasks.** Across methods:
   - Nugget2D: 20x with 98% BLEU reconstruction
   - LLMLingua: 20x with 1.5% performance loss
   - CCM: 32x per step (but for streaming, not arbitrary context)
   - Gist tokens: 26x for prompts

   Beyond ~20x, performance degrades noticeably for general tasks. Task-specific compression can go higher (RECOMP: 95% reduction for factoid QA).

5. **The information-theoretic gap.** Natural language operates at roughly 1-1.5 bits per character of entropy (Shannon's estimate, confirmed by modern LLMs). English text has ~4.7 bits per character in raw encoding. This suggests natural language is roughly 3-5x redundant at the character level. At the semantic level, redundancy is much higher -- entire paragraphs may restate a single proposition.

### The MVC Inequality

Combining the above, for a given task T and context C processed by model M:

```
K(answer_T) <= |MVC(T,C)| <= |compressed(C)| <= |C|
```

Where:
- K(answer_T) = Kolmogorov complexity of the answer (absolute minimum)
- MVC(T,C) = minimum viable context (task-conditional minimum)
- compressed(C) = best achievable compression of full context
- |C| = original context length

The gap between MVC and compressed(C) is the "task-relevance gap" -- information that is faithfully compressed but irrelevant to the task. This is where the biggest wins are: not just compressing text, but selecting what to compress.

---

## Open Questions

1. **No formal definition of "semantic information" for LLMs.** Semantic entropy (Farquhar et al., 2024) measures uncertainty over meaning clusters, but there is no widely accepted formalism for the *amount* of semantic information in a context. The field lacks a "Shannon for semantics."

2. **Compression-performance curves are under-characterized.** Most papers report a few compression ratios. We lack systematic studies mapping the full degradation curve across compression levels for diverse tasks. What is the shape? Linear? Cliff-edge? Task-dependent?

3. **Optimal format for compressed context is unknown.** Natural language, structured (JSON/YAML), graph representations, code representations -- all encode information differently. No systematic comparison exists for which format achieves highest semantic density for LLM consumption across task types.

4. **Interaction between compression and reasoning depth.** Multi-hop reasoning appears more sensitive to compression than factoid retrieval (RECOMP evidence). The relationship between reasoning complexity and compression tolerance is not well understood.

5. **Soft vs. hard prompt compression trade-offs.** Soft methods (gist tokens, ICAE) achieve higher compression but require model modification. Hard methods (LLMLingua) are model-agnostic. When does each approach dominate? No head-to-head comparison exists under controlled conditions.

6. **Dynamic/adaptive compression.** Document regions vary in information density. Adaptive methods that allocate more tokens to dense regions are theoretically superior but under-explored empirically.

7. **Composability of compressed representations.** Can you combine compressed representations from different sources? How does compression interact with multi-document reasoning?

---

## Synthesis: First Principles of Semantic Compression for LLM Memory

Drawing from the evidence above, the following principles emerge:

### Principle 1: Compression Is the Dual of Prediction
An LLM's ability to compress IS its ability to understand. Tokens the model can predict carry zero information (they are redundant given the model's weights). The incompressible residual is the true information content of the context *for that model*. This means compression quality is model-dependent.

### Principle 2: Task Relevance Dominates Compression Ratio
The biggest compression wins come not from making text shorter, but from removing task-irrelevant content. RECOMP achieves 95% token reduction for factoid QA because most retrieved documents are irrelevant. LongLLMLingua *improves* performance by 21.4% through relevance-based compression. The "task-relevance gap" (between MVC and full context) is typically larger than the "redundancy gap" (between compressed and original text).

### Principle 3: There Is an Optimal Context Size (Not Maximum)
"Lost in the Middle" and "Context Length Alone Hurts" demonstrate that more context degrades performance. The optimal context window is not the maximum available -- it is the MVC for the task. Compression toward MVC improves both cost AND quality.

### Principle 4: Natural Language Is ~3-20x Redundant for LLM Tasks
Depending on the task and content:
- Lexical redundancy: ~3-5x (Shannon's estimate of English entropy vs. raw encoding)
- Semantic redundancy (same proposition stated multiple ways): ~5-10x typical
- Task-relevance redundancy (content irrelevant to query): ~10-20x for retrieval tasks
These stack: a RAG context with 10 retrieved documents may be 100x redundant for a specific question.

### Principle 5: The Hard Ceiling Is ~20-30x for General Compression
Multiple independent methods converge on ~20x as the practical limit for general-purpose context compression without significant quality loss. Task-specific compression can exceed this. The theoretical floor is the model's perplexity on the content, but reaching it requires perfect task-relevance filtering.

### Principle 6: Format Is a Compression Lever
Structured representations (code, graphs, tables) can encode more information per token than prose. Python representations of knowledge outperform JSON and natural language for LLM reasoning (2024 evidence). The optimal format for memory/context is not necessarily natural language.

### Principle 7: Compression Methods Are Complementary
The taxonomy is: (1) prune irrelevant content (task-relevance), (2) remove redundant tokens (lexical compression), (3) encode into dense representations (soft compression). These address different sources of redundancy and can be composed: first filter by relevance, then compress the relevant content.

---

## Sources

### Peer-Reviewed Papers
- [Language Modeling Is Compression -- Deletang et al., ICLR 2024](https://arxiv.org/abs/2309.10668)
- [LLMLingua -- Jiang et al., EMNLP 2023](https://arxiv.org/abs/2310.05736)
- [LLMLingua-2 -- Pan et al., ACL 2024](https://arxiv.org/abs/2403.12968)
- [LongLLMLingua -- Jiang et al., 2024](https://arxiv.org/abs/2310.06839)
- [ICAE: In-Context Autoencoder -- Ge et al., ICLR 2024](https://arxiv.org/abs/2307.06945)
- [Gist Tokens -- Mu, Li & Goodman, NeurIPS 2023](https://arxiv.org/abs/2304.08467)
- [RECOMP -- Xu et al., ICLR 2024](https://openreview.net/forum?id=mlJLVigNHp)
- [CCM: Compressed Context Memory -- Kim et al., ICLR 2024](https://arxiv.org/abs/2312.03414)
- [Nugget2D -- Qin & Van Durme, 2024](https://arxiv.org/abs/2310.02409)
- [Lost in the Middle -- Liu et al., TACL 2024](https://arxiv.org/abs/2307.03172)
- [Semantic Entropy for Hallucination Detection -- Farquhar et al., Nature 2024](https://www.nature.com/articles/s41586-024-07421-0)
- [Semantic Compression for Context Extension -- ACL 2024 Findings](https://aclanthology.org/2024.findings-acl.306/)
- [Prompt Compression Survey -- Li et al., NAACL 2025](https://aclanthology.org/2025.naacl-long.368/)
- [LazyLLM -- Fu et al., ICML 2024 Workshop](https://arxiv.org/abs/2407.14057)
- [Kolmogorov Complexity and Transformers, 2025](https://arxiv.org/abs/2509.22445)

### Surveys and Overviews
- [Context Engineering Survey -- 1400+ papers analyzed, 2025](https://arxiv.org/abs/2507.13334)
- [Prompt Compression Survey GitHub](https://github.com/ZongqianLi/Prompt-Compression-Survey)
- [LLMLingua Project Site](https://llmlingua.com/)
- [Awesome LLM Compression -- Paper Collection](https://github.com/HuangOwen/Awesome-LLM-Compression)

### Preprints and Recent Work
- [Context Length Alone Hurts, 2025](https://arxiv.org/abs/2510.05381)
- [Breaking Through Shannon Entropy Limit via Logical Semantics, 2025](https://arxiv.org/abs/2501.00612)
- [Pretraining Context Compressor -- ACL 2025](https://aclanthology.org/2025.acl-long.1394.pdf)
