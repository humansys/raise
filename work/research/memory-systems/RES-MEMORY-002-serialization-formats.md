# RQ4: Serialization Formats for LLM Context — Evidence Catalog

**Research Date:** 2026-02-18
**Status:** Complete (first pass)
**Methodology:** Web search, triangulation across academic papers, practitioner benchmarks, and blog posts with measurements

---

## Key Concepts

**Serialization format:** A scheme for encoding structured data (objects, arrays, key-value pairs, graphs) into a linear sequence of characters that can be parsed back into the original structure. In LLM context, the format must be both machine-parseable and comprehensible to the language model.

**Tokens-per-fact:** A measure of how many BPE tokens are required to represent a single unit of knowledge (e.g., a triple, a key-value pair, a row) in a given format. Lower is more efficient, but comprehension must be preserved.

**Structured natural language:** Knowledge represented in constrained English sentences with consistent patterns (e.g., "Entity X has property Y with value Z") rather than formal serialization syntax. Bridges human readability and machine parsing.

**Semantic density (of a format):** The ratio of meaning-bearing tokens to total tokens. Formats with high syntactic overhead (braces, quotes, commas, repeated keys) have low semantic density. Formats where most tokens carry factual content have high semantic density.

---

## Format Taxonomy

### Formal Structured Formats
- **JSON** — Universal interchange, verbose (braces, quotes, repeated keys)
- **JSON-LD** — JSON with linked data semantics (@context, @id), even more verbose
- **XML** — Tag-based, extremely verbose (80% more tokens than Markdown for same data)
- **RDF/XML** — XML serialization of RDF, worst of both worlds for token efficiency
- **Turtle/N3** — Compact RDF serialization, prefix-based, human-readable
- **N-Triples** — One triple per line, simple but repetitive (full URIs every time)

### Semi-Structured Formats
- **YAML** — Indentation-based, less syntactic overhead than JSON, good LLM comprehension
- **TOML** — Section-based, surprisingly good LLM accuracy
- **CSV/TSV** — Minimal overhead for tabular data, header + rows
- **INI** — Section + key-value, minimal syntax
- **JSONL** — One JSON object per line, no array wrapper

### Natural Language Variants
- **Markdown** — Headers, lists, tables; familiar to LLMs from training data
- **Markdown-KV** — Key: Value pairs in markdown, top performer for tables
- **Structured natural language** — Constrained English sentences with consistent patterns
- **Plain text** — Unstructured prose descriptions

### Custom DSLs for LLM Efficiency
- **TOON** (Token-Oriented Object Notation) — Header-based arrays, indentation-based nesting, 40-75% fewer tokens than JSON
- **TRON** — JSON-compatible with token reduction, ~40% savings
- **Columnar JSON** — Keys declared once, values as arrays (avoids key repetition)

### Symbolic Notations
- **S-expressions** — Lisp-style parenthesized notation, minimal syntax, uniform structure

---

## Token Efficiency Comparison

### Measured Comparisons (Same Data, Different Formats)

**Example fact:** A person record with name, age, city.

| Format | Relative Tokens (JSON = 100%) | Source |
|--------|-------------------------------|--------|
| JSON (pretty) | 100% (baseline) | Multiple sources |
| JSON (compact) | ~85% | TOON benchmarks |
| XML | ~180% | ImprovingAgents |
| YAML | ~81-90% | Multiple sources |
| TOML | ~85% | nathom.dev |
| Markdown | ~84% (15-16% less than JSON) | OpenAI community, ImprovingAgents |
| CSV/TSV | ~44% (56% less than JSON) | GetCrux |
| TOON | ~55-60% (40-45% less than JSON) | TOON benchmarks |
| TRON | ~60% (40% less than JSON) | Piotr Sikora comparison |

**Sources:**
- OpenAI Community: "Markdown is 15% more token efficient than JSON" — measured 13,869 tokens (JSON) vs 11,612 tokens (Markdown) for same dataset
- GetCrux experiment: CSV consumed 56.20% fewer tokens than JSON (Claude 3.5 Sonnet)
- TOON benchmarks: 2,744 tokens (TOON) vs 3,081 tokens (JSON compact) across 209 questions on 4 LLMs
- ImprovingAgents: XML required 80% more tokens than Markdown for same nested data

### Why Token Counts Differ

BPE tokenizers are trained on corpora heavily featuring Markdown, making common Markdown patterns likely to tokenize as single tokens. JSON syntax characters (braces, quotes, commas) often fragment into separate tokens. Key repetition in JSON arrays (every object repeats all field names) is the single largest source of waste.

---

## Empirical Studies: Format Impact on LLM Performance

### Study 1: "Let Me Speak Freely?" (Tam et al., 2024)
- **Claim:** Format restrictions (JSON, XML, YAML) degrade LLM reasoning by 10-15% compared to free-form generation
- **Methodology:** Compared structured generation (JSON-mode, constrained decoding, format-restricting instructions) vs free-form on math, symbolic reasoning, and complex analysis tasks
- **Results:** Significant decline in reasoning under format restrictions; stricter constraints = greater degradation
- **Source:** [arXiv 2408.02442](https://arxiv.org/abs/2408.02442)
- **Evidence Level:** High (systematic academic study, multiple tasks and models)
- **Key nuance:** This is about *output* format restrictions, not *input* format. Constraining how the model responds hurts reasoning. But the finding implies the model "spends" capacity on format compliance.

### Study 2: "Does Prompt Formatting Have Any Impact on LLM Performance?" (He et al., 2024)
- **Claim:** Same context in different input formats (plain text, Markdown, JSON, YAML) yields up to 40% performance variation
- **Methodology:** Formatted identical contexts into multiple templates, tested on NL reasoning, code generation, translation using GPT-3.5 and GPT-4
- **Results:** GPT-3.5-turbo: up to 40% variation (favors JSON). GPT-4: more robust but still sensitive (favors Markdown). All p-values < 0.05 except GPT-4 on HumanEval.
- **Source:** [arXiv 2411.10541](https://arxiv.org/abs/2411.10541)
- **Evidence Level:** High (systematic, multiple models and tasks, statistical significance)

### Study 3: "LLMs Are Biased Towards Output Formats!" (Long et al., 2024)
- **Claim:** LLMs exhibit systematic format bias across 15 output formats and 8 generation tasks
- **Methodology:** Evaluated 15 formats in 4 categories (MCQ, wrapping, list, mapping) across multiple LLMs
- **Results:** ChatGPT performance variance among wrapping formats: 235.33 (before mitigation) -> 0.71 (after). Significant format-dependent accuracy swings.
- **Source:** [arXiv 2408.08656](https://arxiv.org/abs/2408.08656)
- **Evidence Level:** High (systematic, 15 formats, 8 tasks)

### Study 4: ImprovingAgents — Nested Data Format Benchmark
- **Claim:** YAML provides best accuracy for nested data; Markdown is most token-efficient
- **Methodology:** 3 LLMs (GPT-5 Nano, Llama 3.2 3B, Gemini 2.5 Flash Lite), 1,000 questions each, data volumes calibrated to stress accuracy into 40-60% range
- **Results:** YAML best accuracy for 2/3 models. XML consistently worst. One format yielded 54% more correct answers than another. GPT-5 Nano: YAML outperformed XML by 17.7 percentage points.
- **Source:** [ImprovingAgents: Nested Data Formats](https://www.improvingagents.com/blog/best-nested-data-format/)
- **Evidence Level:** Medium-High (practitioner benchmark, systematic, 3 models, but not peer-reviewed)

### Study 5: ImprovingAgents — Table Format Benchmark (11 Formats)
- **Claim:** Markdown-KV is the best table format for LLM comprehension; CSV performs poorly
- **Methodology:** 11 formats tested on GPT-4.1 mini with 1,000-row tables, measuring accuracy on data retrieval questions
- **Results:** Markdown-KV: 60.7% accuracy (~16 points ahead of CSV). CSV and JSONL performed poorly. Markdown-KV used 2.7x tokens of CSV but accuracy was far superior. More tokens generally correlate with higher accuracy, but relationship is non-linear.
- **Source:** [ImprovingAgents: Table Formats](https://www.improvingagents.com/blog/best-input-data-format-for-llms)
- **Evidence Level:** Medium-High (practitioner benchmark, systematic, 11 formats)

### Study 6: GetCrux — CSV vs JSON for Tabular Data
- **Claim:** CSV uses 56% fewer tokens than JSON with comparable accuracy for tabular data
- **Methodology:** Claude 3.5 Sonnet, 10,000 test questions on structured table data
- **Results:** CSV: 56.20% fewer tokens than JSON. Accuracy: ~100% in top/bottom sections, lower in middle for both formats.
- **Source:** [GetCrux Blog](https://www.getcrux.ai/blog/experiment-data-formats---json-vs-csv)
- **Evidence Level:** Medium (single model, large test set, practitioner)

### Study 7: TOON Benchmarks
- **Claim:** TOON achieves higher accuracy than JSON while using ~40% fewer tokens
- **Methodology:** 209 data retrieval questions across 4 LLMs with semantic validation
- **Results:** TOON 73.9% accuracy / 2,744 tokens vs JSON compact 70.7% / 3,081 tokens. Efficiency: 26.9 accuracy points per 1,000 tokens (TOON) vs 15.3 (JSON). GPT-5 Nano: TOON 99.4% accuracy with 46% fewer tokens.
- **Source:** [TOON GitHub](https://github.com/toon-format/toon), [InfoQ](https://www.infoq.com/news/2025/11/toon-reduce-llm-cost-tokens/)
- **Evidence Level:** Medium (format creator's benchmarks, but reproducible and multi-model)

### Study 8: nathom.dev — Structured Data Format Comparison
- **Claim:** JSON is most token-efficient among traditional formats; TOML provides best accuracy
- **Methodology:** Averaged token counts across Qwen 3, Llama 3.2, and gpt-oss tokenizers. Measured accuracy with Jaccard index.
- **Results:** Token efficiency ranking: JSON > YAML > TOML > XML. Accuracy ranking (Jaccard): TOML > JSON > YAML > XML.
- **Source:** [nathom.dev](https://nathom.dev/llm-data-formats/)
- **Evidence Level:** Medium (practitioner, multiple tokenizers, reproducible)
- **Contrarian finding:** This study recommends *against* YAML, counter to most other studies.

### Study 9: "Prompt Engineering for Structured Data" (2025)
- **Claim:** Format preferences are model-specific; Claude excels with hierarchical formats, GPT-4o with lightweight formats
- **Methodology:** 6 prompting strategies across 3 LLMs (GPT-4o, Claude, Gemini), multiple datasets
- **Results:** Claude: 85% overall accuracy, best with JSON/YAML. GPT-4o: lowest token usage (<100 tokens for lightweight formats), fastest (4-6 sec). Gemini: balanced but variable.
- **Source:** [Preprints.org 202506.1937](https://www.preprints.org/manuscript/202506.1937/v1)
- **Evidence Level:** Medium-High (systematic cross-model study, published preprint)

### Study 10: "How Well Do LLMs Speak Turtle?" (Frey et al., 2023)
- **Claim:** Modern LLMs can comprehend and generate Turtle RDF at useful quality levels
- **Methodology:** Evaluated GPT-3.5, GPT-4, Claude 1.3, Claude 2.0, GPT4All Vicuna, GPT4All Falcon on RDF creation/comprehension tasks
- **Results:** Claude 2.0: highest F1 mean, fewer unparseable outputs. Smaller open models (Vicuna, Falcon): essentially failed. All models inconsistently wrapped Turtle in markdown or explanations.
- **Source:** [arXiv 2309.17122](https://arxiv.org/abs/2309.17122)
- **Evidence Level:** High (systematic benchmark, LLM-KG-Bench framework, multiple models)

---

## Custom Notations for LLM Context

### TOON (Token-Oriented Object Notation)
- **Purpose:** Specifically designed to minimize tokens for LLM input while maximizing comprehension
- **Key innovations:**
  - `[N]` array length headers give LLMs row count upfront
  - `{field1,field2,...}` field headers — keys declared once, not repeated per row
  - Indentation-based nesting (like YAML) instead of braces
  - Data rows are pure values, no keys or delimiters
- **Token savings:** 40-75% vs JSON depending on data shape
- **Best for:** Tabular/semi-structured data with uniform schemas
- **Weakness:** Complex nested hierarchies, non-uniform objects
- **Source:** [toonformat.dev](https://toonformat.dev/), [TOON spec](https://github.com/toon-format/spec)

### TRON (Token-Reduced Object Notation)
- **Purpose:** Token reduction while maintaining JSON compatibility
- **Token savings:** ~40% vs JSON
- **Advantage:** Easier adoption since it preserves JSON structure
- **Source:** [Piotr Sikora comparison](https://www.piotr-sikora.com/blog/2025-12-05-toon-tron-csv-yaml-json-format-comparison)

### Columnar JSON
- **Purpose:** Eliminate key repetition in arrays of objects
- **Method:** Instead of `[{k:v, k:v}, {k:v, k:v}]`, use `{k:[v,v], k:[v,v]}`
- **Advantage:** Supports nested data (unlike CSV), significant savings for homogeneous arrays
- **Source:** [David Gilbertson, Medium](https://david-gilbertson.medium.com/llm-output-formats-why-json-costs-more-than-tsv-ebaf590bd541)

### Markdown-KV (Key-Value Markdown)
- **Purpose:** Not a new format per se, but a pattern: `**Key:** Value` lines in markdown
- **Performance:** Top performer in ImprovingAgents table benchmark (60.7% accuracy)
- **Why it works:** Familiar from training data, minimal syntax, each fact on its own line, clear key-value delineation
- **Source:** [ImprovingAgents](https://www.improvingagents.com/blog/best-input-data-format-for-llms)

### S-expressions for LLM DSLs
- **Purpose:** Using Lisp-style `(operator arg1 arg2)` notation as a compact action language
- **Advantage:** Uniform structure reduces cognitive/computational load; LLMs focus on semantics
- **Use case:** Function-call representation, not general knowledge serialization
- **Source:** [TechConative: Borrowing Lisp for LLMs](https://techconative.ai/blog/borrowing-Idea-of-lisp-into-llm-systems), [arXiv 2506.10021](https://arxiv.org/abs/2506.10021)

---

## Knowledge Graph Serialization for LLMs

### Format Comparison for KG Data

| Format | Token Efficiency | LLM Comprehension | Notes |
|--------|-----------------|-------------------|-------|
| Turtle/TTL | Good (prefix abbreviation) | Moderate-Good (newer models) | Most compact standard RDF format |
| JSON-LD | Poor (verbose, @context overhead) | Good (JSON is familiar) | Valid JSON = wide tool support |
| N-Triples | Poor (full URIs repeated) | Low-Moderate | Simplest but most repetitive |
| RDF/XML | Very Poor | Low | Worst of both XML and RDF verbosity |
| Plain triples | Good | Good | `Subject - Predicate - Object` as text |

### Key Findings

1. **LLMs understand Turtle at useful levels** — Claude 2.0 and GPT-4 can both parse and generate valid Turtle, though they often wrap it in markdown (Frey et al., 2023).

2. **JSON-LD is familiar but wasteful** — LLMs know JSON well from training data, but the @context, @id, @type overhead adds significant tokens per triple compared to plain triples or Turtle.

3. **Plain text linearization often beats formal serialization** — The "Let Your Graph Do the Talking" paper (arXiv 2402.05862) found that text-based serialization of graph structure is often insufficient for reasoning, suggesting that learned encodings (GraphToken) significantly outperform hand-crafted text serializations.

4. **For LLM *input* (not KG engineering), simple is better** — Representing triples as `Subject | Predicate | Object` or natural language sentences often outperforms formal RDF serializations for LLM comprehension, because the model doesn't need to decode URI syntax.

### Practical Recommendation

For feeding knowledge graph data to LLMs:
- **Avoid** RDF/XML and N-Triples (too verbose, unfamiliar syntax patterns)
- **Consider** Turtle if the LLM needs to understand ontological structure (prefixes help)
- **Prefer** simplified representations: `entity - relation - entity` per line, or Markdown-KV for entity descriptions
- JSON-LD only if you need JSON ecosystem compatibility and accept the token cost

---

## Anti-Patterns

### 1. JSON for Homogeneous Arrays (Key Repetition)
- **Problem:** Every object in a JSON array repeats all field names. For 100 records with 10 fields, that's 1,000 redundant key tokens.
- **Fix:** Use CSV, TOON, columnar JSON, or Markdown tables.
- **Impact:** 40-60% token waste for tabular data.

### 2. XML for Any LLM Input
- **Problem:** XML uses 80% more tokens than Markdown for the same data and consistently underperforms on accuracy.
- **Fix:** Use literally any other format.
- **Evidence:** ImprovingAgents benchmarks; consistent last-place across studies.

### 3. Pretty-Printing with Excessive Whitespace
- **Problem:** Indentation in JSON/XML adds tokens with zero semantic content.
- **Fix:** Compact serialization, or switch to a format where indentation IS the structure (YAML, TOON).
- **Impact:** 10-15% token overhead from whitespace alone.

### 4. Forcing Structured Output for Reasoning Tasks
- **Problem:** Requiring JSON/XML output degrades reasoning performance by 10-15%.
- **Fix:** Let the model reason in free text, then extract structure in a second pass ("NL-to-Format" approach from Tam et al., 2024).
- **Evidence:** "Let Me Speak Freely?" (arXiv 2408.02442).

### 5. Assuming One Format Fits All Models
- **Problem:** GPT-3.5 favors JSON, GPT-4 favors Markdown, Claude excels with hierarchical formats. Format preference is model-specific.
- **Fix:** Test your specific model with your specific data shape.
- **Evidence:** He et al. (2411.10541), Preprints.org 202506.1937.

### 6. Optimizing for Tokens Alone (Ignoring Comprehension)
- **Problem:** CSV is the most token-efficient (~56% savings) but ranked poorly for accuracy in ImprovingAgents table benchmark. More tokens sometimes buy better comprehension.
- **Fix:** Optimize for accuracy-per-token, not just tokens.
- **Evidence:** ImprovingAgents: Markdown-KV used 2.7x more tokens than CSV but had 16 points higher accuracy.

### 7. Using JSONL for Large Tables
- **Problem:** JSONL (one JSON object per line) still repeats keys per record and performed poorly in benchmarks.
- **Fix:** Use Markdown tables, TOON, or CSV with headers.
- **Evidence:** ImprovingAgents table benchmark.

---

## Open Questions

1. **No standard "tokens-per-fact" metric exists.** The field lacks a normalized benchmark where the same set of facts is represented in all formats and token-counted with the same tokenizer. Most comparisons use different data, different tokenizers, and different accuracy tasks.

2. **Training data bias vs. inherent format properties.** Is YAML good because it's inherently clear, or because LLMs saw massive amounts of YAML in training (config files, GitHub repos)? Would a format unseen in training data (e.g., TOON) improve with exposure? The TOON benchmarks suggest LLMs can comprehend novel formats, but the question of ceiling performance remains open.

3. **Knowledge graph linearization remains unsolved.** The "Let Your Graph Do the Talking" paper showed text serialization is fundamentally limited for graph reasoning. Learned encodings (GraphToken) help but require fine-tuning. For general-purpose LLM APIs, we're stuck with text serialization — what's the best one?

4. **Nested vs. flat data.** Most comparisons focus on either tabular or nested data. Real-world knowledge often mixes both (entity descriptions with nested properties). No study has systematically compared formats on mixed-shape data.

5. **Long-context scaling.** Format effects may compound at scale. A 15% savings per fact could mean tens of thousands of tokens in a large context window. Does the accuracy impact also compound, or does it plateau?

6. **Format interaction with retrieval.** RAG systems retrieve chunks — does the serialization format of those chunks affect retrieval accuracy (embedding similarity)? One article (Wetrocloud) claims Markdown produces better embeddings, but empirical evidence is thin.

7. **Structured natural language as a format category** is underexplored. It appears in prompt engineering guides but lacks systematic benchmarking against formal formats. The SR-LLM paper (arXiv 2502.14352) suggests converting structured representations to natural language descriptions improves LLM reasoning, but this hasn't been benchmarked for *input* context efficiency.

8. **TOON comprehension at scale.** TOON shows promise but benchmarks are from the format creators. Independent replication with adversarial testing is needed. The arXiv paper "Are LLMs Ready for TOON?" (2601.12014) raises questions about structural correctness.

---

## Synthesis: First Principles of Format Choice for LLM Context

### The Fundamental Trade-off

**Token efficiency and comprehension accuracy are correlated but not linearly.** More concise formats generally use fewer tokens, but there is a sweet spot where removing syntactic overhead improves both efficiency AND comprehension (the model doesn't need to parse through noise). Below that sweet spot, removing structure hurts the model's ability to locate and reason about facts.

### What Makes a Format Good for LLM Context

1. **Minimal key repetition.** The single largest waste in JSON for arrays. Any format that declares field names once (CSV headers, TOON headers, Markdown table headers, columnar JSON) wins immediately.

2. **Familiar from training data.** LLMs are statistical pattern matchers trained on internet text. Markdown, YAML, JSON, and CSV are heavily represented in training corpora. Novel formats like TOON work but may hit a ceiling on models that haven't seen them.

3. **One fact per visual line.** Formats where each line represents one complete assertion (Markdown-KV, N-Triples, CSV rows) appear to help LLMs locate specific facts. This aligns with how attention mechanisms work: each line becomes a retrieval unit.

4. **Explicit structure metadata.** TOON's `[N]` length headers and `{fields}` declarations help the model understand the shape of data upfront. This is analogous to how humans scan a table: header first, then data.

5. **Low ratio of syntax tokens to content tokens.** Every brace, quote, comma, and closing tag is a token that carries no factual content. The ideal format approaches the Shannon limit: every token carries meaning.

6. **Match format to data shape:**
   - **Tabular/homogeneous:** CSV, TSV, TOON, Markdown tables
   - **Nested/hierarchical:** YAML, TOML, (JSON if model prefers it)
   - **Entity descriptions:** Markdown-KV, structured natural language
   - **Graph/relational:** Turtle (if model supports), simplified triples, adjacency lists
   - **Mixed:** Markdown with embedded tables and KV sections

### Practical Recommendations (Ranked by Evidence Strength)

| Recommendation | Evidence Level | Key Sources |
|----------------|---------------|-------------|
| Don't use XML for LLM input | Very High | Multiple benchmarks, consistent last place |
| YAML > JSON for nested data accuracy | High | ImprovingAgents, He et al., multiple practitioner tests |
| Markdown-KV for entity/record descriptions | High | ImprovingAgents table benchmark (top performer) |
| CSV/TSV for pure tabular data (when accuracy not critical) | High | GetCrux, David Gilbertson, token measurements |
| Format preference is model-specific | High | He et al., Preprints.org 202506.1937 |
| Output format restrictions hurt reasoning | High | Tam et al. (Let Me Speak Freely) |
| TOON for tabular LLM input | Medium | TOON benchmarks (creator-run but multi-model) |
| Markdown for general-purpose context | Medium | Training data familiarity, OpenAI community measurements |
| Separate reasoning from formatting | Medium | "Let Me Speak Freely" mitigation strategies |

### The "Semantic Density" Formula (Conceptual)

```
Format Quality = Comprehension Accuracy / Tokens Used

Where:
- Comprehension Accuracy = how well the LLM can answer questions about the serialized data
- Tokens Used = BPE token count for the serialized data

Maximize: accuracy per token, not minimum tokens alone
```

The ideal format is not the most compressed — it's the one that achieves the highest comprehension per token spent.

---

## Sources Index

### Academic Papers
- [Let Me Speak Freely? (Tam et al., 2024)](https://arxiv.org/abs/2408.02442)
- [Does Prompt Formatting Have Any Impact on LLM Performance? (He et al., 2024)](https://arxiv.org/abs/2411.10541)
- [LLMs Are Biased Towards Output Formats! (Long et al., 2024)](https://arxiv.org/abs/2408.08656)
- [How Well Do LLMs Speak Turtle? (Frey et al., 2023)](https://arxiv.org/abs/2309.17122)
- [Let Your Graph Do the Talking (Perozzi et al., 2024)](https://arxiv.org/abs/2402.05862)
- [SR-LLM: Structured Representation in LLMs (2025)](https://arxiv.org/abs/2502.14352)
- [LLM-KG-Bench 3.0 (2025)](https://arxiv.org/abs/2505.13098)
- [Are LLMs Ready for TOON? (2026)](https://arxiv.org/abs/2601.12014)
- [Prompt Engineering for Structured Data (2025)](https://www.preprints.org/manuscript/202506.1937/v1)
- [LLMs in a Persistent Lisp Metaprogramming Loop (2025)](https://arxiv.org/abs/2506.10021)

### Practitioner Benchmarks & Articles
- [ImprovingAgents: Nested Data Formats](https://www.improvingagents.com/blog/best-nested-data-format/)
- [ImprovingAgents: Table Formats (11 Formats)](https://www.improvingagents.com/blog/best-input-data-format-for-llms)
- [ImprovingAgents: TOON Benchmarks](https://www.improvingagents.com/blog/toon-benchmarks/)
- [GetCrux: CSV vs JSON Experiment](https://www.getcrux.ai/blog/experiment-data-formats---json-vs-csv)
- [nathom.dev: Comparing Structured Data Formats](https://nathom.dev/llm-data-formats/)
- [David Gilbertson: LLM Output Formats (JSON vs TSV)](https://david-gilbertson.medium.com/llm-output-formats-why-json-costs-more-than-tsv-ebaf590bd541)
- [TOON Official Site](https://toonformat.dev/)
- [TOON Spec (GitHub)](https://github.com/toon-format/spec)
- [TOON vs TRON vs JSON vs YAML vs CSV](https://www.piotr-sikora.com/blog/2025-12-05-toon-tron-csv-yaml-json-format-comparison)
- [InfoQ: TOON Announcement](https://www.infoq.com/news/2025/11/toon-reduce-llm-cost-tokens/)
- [OpenAI Community: Markdown Token Efficiency](https://community.openai.com/t/markdown-is-15-more-token-efficient-than-json/841742)
- [Elya Livshitz: YAML vs JSON for LLMs](https://medium.com/better-programming/yaml-vs-json-which-is-more-efficient-for-language-models-5bc11dd0f6df)
- [TechConative: Borrowing Lisp for LLMs](https://techconative.ai/blog/borrowing-Idea-of-lisp-into-llm-systems)
- [Factory.ai: Evaluating Context Compression](https://factory.ai/news/evaluating-compression)

---

*Evidence catalog compiled 2026-02-18. First-pass research; some claims would benefit from independent replication.*
