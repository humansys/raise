# RAG and Semantic Compression Strategies for Context Delivery

**Document Status**: RESEARCH SYNTHESIS
**Research Date**: 2026-01-24
**Focus**: RAG architectures for guardrails/rules delivery to AI agents

---

## Executive Summary

RAG (Retrieval-Augmented Generation) provides a scalable alternative to loading all context upfront. By 2026, RAG has evolved into "Agentic RAG" with sophisticated guardrails, multi-index embeddings, and semantic compression techniques achieving 40-60% token reduction.

---

## 1. RAG Architecture for Code Rules/Guardrails

### Traditional RAG Pipeline
```
User Query
  ↓
Query Embedding
  ↓
Vector Database Search (similarity)
  ↓
Retrieve Top-K Relevant Documents
  ↓
Rerank (optional)
  ↓
Inject into LLM Context
  ↓
Generate Response
```

### Agentic RAG (2026 Evolution)
```
Agent Task
  ↓
Orchestrator (routing + policy)
  ↓
Retriever (vector/keyword/hybrid search)
  ↓
Reranker (ML model or business rules)
  ↓
Context Builder (semantic compression)
  ↓
LLM Reasoner
  ↓
Tool Runner (execute actions)
  ↓
Memory (store interactions)
  ↓
Guardrails (input/output validation)
  ↓
Observability (logging/monitoring)
```

**Key Difference**: Agentic RAG allows AI to retrieve MORE information when needed, think step-by-step, and refine responses iteratively.

---

## 2. Vector Databases for Code Rules

### Top Vector Databases (2026)

| Database | Strengths | Best For |
|----------|-----------|----------|
| Pinecone | Managed, scalable, fast | Production RAG systems |
| Weaviate | Hybrid search, GraphQL | Complex queries |
| ChromaDB | Open source, simple | Development/prototyping |
| pgvector | PostgreSQL extension | Existing Postgres stack |
| Qdrant | High performance, Rust | Large-scale deployments |

### Embedding Models for Code (2026)

**Best Performers**:
1. **CodeBERT / GraphCodeBERT**: Specialized for code understanding
2. **OpenAI text-embedding-3-large**: General-purpose, 3,072 dimensions
3. **Cohere embed-v3**: Multilingual, efficient
4. **E5-large-v2**: Open source, strong performance

**Dimensionality Considerations**:
- 128-dim: Fast, lightweight (social feeds, simple retrieval)
- 384-dim: Balanced (typical RAG applications)
- 768-dim: Strong semantic understanding (code/rules)
- 1,024-1,536-dim: Maximum nuance (complex multilingual systems)
- 3,072-dim: OpenAI's max resolution (research/experimental)

**For RaiSE Rules**: 768-dim or 1,024-dim recommended (balance between semantic precision and performance)

---

## 3. Multi-Index Embeddings Pattern (2026 Best Practice)

### Concept
Store MULTIPLE embeddings per rule/guardrail:

```
Rule Document:
├── Global embedding (entire rule)
├── Category embedding (architecture/security/testing)
├── Code pattern embedding (specific code snippet)
├── Anti-pattern embedding (what to avoid)
└── Metadata (tags, priority, scope)
```

**Benefits**:
- Dramatically improved recall for diverse queries
- Better handling of multi-faceted rules
- Enables hybrid search (semantic + metadata filters)

**Example for RaiSE**:
```yaml
rule_id: arch-001
embeddings:
  - global: [0.23, -0.45, 0.67, ...] # 768-dim
  - category: "architecture"
  - file_scope: "src/**/*.ts"
  - priority: "P0"
```

---

## 4. Semantic Compression Techniques

### A. Token Efficiency by Format

**Research Findings (2026)**:

| Format | Token Efficiency | LLM Parsing Accuracy | Use Case |
|--------|------------------|---------------------|----------|
| Markdown | **Best** (34-38% fewer than JSON) | High (GPT-4 favors) | Human-readable docs |
| YAML | Good (10% fewer than JSON) | **Best** (GPT-5, Gemini) | Structured rules |
| JSON | Standard | Good (GPT-3.5 favors) | API responses |
| XML | Worst | Worst (17.7pp worse) | Avoid for LLMs |
| TSV | Excellent (tables) | Good | Tabular data |
| TOON | Experimental (30-60% reduction) | Poor (limited training) | Future potential |

**Measured Example**:
- Same data: JSON = 13,869 tokens
- Same data: YAML = 12,333 tokens (11% reduction)
- Same data: Markdown = 11,612 tokens (16% reduction)

**Recommendation for RaiSE**: **YAML for machine layer, Markdown for human layer**

---

### B. Telegraphic Semantic Compression (TSC)

**Concept**: Strip grammatical scaffolding, keep only semantic payload

**Example**:
```
Before (verbose):
"When you are implementing a new API endpoint, you should always validate
input parameters using JSON schema validation to ensure type safety and
prevent injection attacks."

After (TSC):
"API endpoint: validate input params via JSON schema → type safety +
injection prevention"

Token reduction: ~65%
```

**Practical Application**:
- Preprocess rules before embedding
- Store both verbose (for humans) and compressed (for LLM retrieval)
- Compressed version for context injection, verbose for reference

---

### C. Hierarchical Compression

**Concept**: Group tokens into hierarchical units

```
Token → Sentence → Paragraph → Section → Document
```

**For RaiSE Rules**:
```
Rule Collection
├── Category Summary (architecture)
│   ├── Rule Group (API design)
│   │   ├── Rule 1 (REST conventions)
│   │   │   ├── Principle
│   │   │   ├── Examples
│   │   │   └── Anti-patterns
│   │   └── Rule 2 (error handling)
│   └── Rule Group (data access)
└── Category Summary (security)
```

**Retrieval Strategy**:
1. Search at category level first (low token cost)
2. If relevant, drill down to rule group
3. Only load full rule if needed

**Token Savings**: 60-80% by avoiding loading irrelevant rule details

---

### D. Context-Aware Compression (2026 Approaches)

**Semantic-Anchor Compression (SAC)**:
- Identify "anchor" tokens with highest semantic density
- Preserve anchors, compress surrounding context
- 40-60% token reduction with 1-2% accuracy loss

**ChunkKV Compression**:
- Compress key-value cache during inference
- Semantic-preserving compression
- Reduces memory footprint and latency

**Adaptive Compression (AdaComp)**:
- Dynamically adjust compression ratio based on task
- Critical information preserved, redundancy removed
- 20x shorter prompts for black-box LLMs

---

## 5. Hybrid Retrieval Strategies

### A. Vector + Keyword (Hybrid Search)

**Approach**: Combine semantic similarity with exact keyword matching

**Use Case**: Find rules matching BOTH concept ("authentication") AND specific framework ("JWT")

**Implementation**:
```
Query: "JWT authentication best practices"
  ↓
Semantic search: embedding similarity
  → Rules about authentication, security, tokens
  ↓
Keyword filter: "JWT"
  → Only rules mentioning JWT
  ↓
Rerank: BM25 or ML model
  → Top 5 most relevant
```

**Token Efficiency**: 80-90% reduction vs loading all auth rules

---

### B. Metadata Filtering

**Strategy**: Pre-filter by structured metadata before vector search

**RaiSE Example**:
```python
# User editing React component in src/ui/components/
filters = {
    "file_scope": "src/ui/**/*.tsx",
    "category": ["architecture", "react"],
    "priority": ["P0", "P1"]
}

# Only search among ~20 rules instead of 200
relevant_rules = vector_db.search(query_embedding, filters=filters, top_k=5)
```

**Token Savings**: 90%+ by never considering irrelevant rules

---

### C. Progressive Disclosure Pattern

**Inspired by Skills Architecture**:

```
Level 1: Rule Metadata (always in context)
  └─ Rule ID, category, 1-sentence description (~20 tokens per rule)

Level 2: Rule Summary (on relevance match)
  └─ Principle, when to apply (~100 tokens)

Level 3: Rule Details (on explicit need)
  └─ Examples, anti-patterns, rationale (~500 tokens)

Level 4: Supporting Docs (rare)
  └─ Full specification, ADRs (~2,000 tokens)
```

**Token Profile**:
- 200 rules at Level 1: 4,000 tokens baseline
- 5 rules escalated to Level 2: +500 tokens
- 1 rule to Level 3: +500 tokens
- **Total**: 5,000 tokens for 200-rule system

**vs Static Loading**: 200 rules × 500 tokens = 100,000 tokens
**Savings**: 95%

---

## 6. Guardrails and Policy Enforcement

### Guardrail Types in Agentic RAG

**Input Guardrails**:
- Filter dangerous prompts
- Detect prompt injection attempts
- Strip PII/sensitive data

**Retrieval Guardrails**:
- Restrict retrieval based on user permissions
- Apply access control policies
- Enforce data residency requirements

**Output Guardrails**:
- Validate responses for safety/compliance
- Check for hallucinations (grounding verification)
- Ensure adherence to rules retrieved

**Action Guardrails**:
- Guardian agents challenge unsafe actions
- Policy-as-code checks before execution
- Hard limits on resource consumption

**For RaiSE**: Policy-as-code guardrails ensure retrieved rules are actually enforced

---

## 7. RAG Token Efficiency Calculations

### Scenario: RaiSE with 200 Guardrails

#### A. Static Loading (Baseline)
```
200 rules × 500 tokens avg = 100,000 tokens
Context window consumed: 50% (of 200k)
Remaining for work: 100,000 tokens
```

#### B. RAG with Semantic Search (No Optimization)
```
Query embedding: 768 dims (~10 tokens equivalent)
Vector search: 0 tokens (server-side)
Retrieve top 10 rules: 10 × 500 = 5,000 tokens
Context window consumed: 2.5%
Remaining for work: 195,000 tokens
Token savings: 95%
```

#### C. RAG with Progressive Disclosure (Optimized)
```
All 200 rule metadata: 200 × 20 = 4,000 tokens (always loaded)
Query and search: ~10 tokens
Top 10 rule summaries: 10 × 100 = 1,000 tokens
Escalate 2 rules to full: 2 × 500 = 1,000 tokens
Total: 6,010 tokens
Context window consumed: 3%
Remaining for work: 194,000 tokens
Token savings: 94%
```

#### D. RAG with Semantic Compression (Maximum Efficiency)
```
All 200 rule metadata (compressed): 200 × 10 = 2,000 tokens
Query: ~10 tokens
Top 10 rules (TSC compressed): 10 × 200 = 2,000 tokens
Escalate 2 rules (verbose): 2 × 500 = 1,000 tokens
Total: 5,010 tokens
Context window consumed: 2.5%
Token savings: 95%
```

---

## 8. Implementation Considerations for RaiSE

### A. Embedding Strategy

**Recommendation**: Dual embeddings
1. **Semantic embedding**: CodeBERT or text-embedding-3-large (768-dim)
2. **Metadata**: Structured (category, scope, priority)

**Indexing**:
```python
# Per rule
{
    "id": "arch-001",
    "embedding": [0.23, -0.45, ...],  # 768 floats
    "metadata": {
        "category": "architecture",
        "scope": "src/**/*.ts",
        "priority": "P0",
        "tags": ["api", "rest", "validation"]
    },
    "content_tiers": {
        "summary": "API endpoints must validate inputs",
        "principle": "...",
        "examples": "...",
        "full": "..."
    }
}
```

### B. Retrieval Strategy

**Query Processing**:
1. User edits file `src/api/users.ts`
2. Extract context: file path, language, imports
3. Generate query: "API design rules for TypeScript user endpoint"
4. Embed query: 768-dim vector
5. Metadata filter: `scope=src/api/**`, `category=architecture`
6. Vector search: top 5 matches
7. Inject summaries into context
8. If agent needs details, fetch tier 3

**Token Budget**:
- Tier 1 (metadata): 4,000 tokens always
- Tier 2 (summaries): 500-1,000 tokens per query
- Tier 3 (details): 500-1,000 tokens rare
- **Typical session**: 5,000-8,000 tokens for 200-rule system

### C. Reranking

**Post-retrieval optimization**:
1. Vector search returns top 20 candidates
2. Rerank with:
   - Priority (P0 > P1 > P2)
   - Recency (newer rules first)
   - File scope match confidence
   - User feedback (rule effectiveness)
3. Select top 5 for injection

**Benefit**: Higher precision = fewer irrelevant rules = lower token waste

---

## 9. Performance vs Token Efficiency Trade-offs

### Latency Considerations

**Static Loading**:
- ✅ Instant availability (all rules in context)
- ❌ Huge upfront cost (100k tokens)
- ❌ Slower LLM processing (more context to process)

**RAG Retrieval**:
- ✅ Minimal upfront cost (2-5k tokens)
- ✅ Faster LLM processing (less context)
- ⚠️ Retrieval latency (50-200ms for embedding + search)
- ⚠️ Potential for missing relevant rules

**Recommendation**: Hybrid approach
- Core rules (P0): Static (always in context) - ~5,000 tokens
- Extended rules (P1-P2): RAG (retrieved on demand)
- Reference docs: RAG (rare access)

---

## 10. RAG Tooling Ecosystem (2026)

### Production-Ready Frameworks

**LangChain**:
- Comprehensive RAG toolkit
- Integrations with all major vector DBs
- Agent orchestration built-in
- ✅ Mature, well-documented

**LlamaIndex**:
- Focus on data ingestion and indexing
- Strong query optimization
- Production monitoring tools
- ✅ Enterprise-ready

**Haystack**:
- Open source, modular
- Strong community
- Good for custom pipelines
- ✅ Flexible

### Embedding Services

**OpenAI Embeddings**:
- text-embedding-3-large: $0.13 per 1M tokens
- Fast, reliable, high quality

**Cohere Embeddings**:
- embed-v3: $0.10 per 1M tokens
- Multilingual, efficient

**Open Source**:
- sentence-transformers (free)
- E5-large-v2 (free)
- ✅ No API costs, but need to host

---

## 11. Evaluation Metrics for RAG

### Retrieval Quality

**Recall@K**: % of relevant rules retrieved in top K results
- Target: >90% for top 5

**Precision@K**: % of retrieved rules that are relevant
- Target: >80% for top 5

**MRR (Mean Reciprocal Rank)**: How quickly does first relevant rule appear
- Target: >0.8

### Token Efficiency

**Compression Ratio**: Tokens used / Tokens in static loading
- Target: <10% (90%+ savings)

**Relevance Density**: Relevant rules / Total rules retrieved
- Target: >80%

### Agent Effectiveness

**Task Completion Rate**: % of tasks completed successfully
- Should NOT degrade vs static loading

**Rule Adherence**: % of code that follows retrieved rules
- Target: >90%

---

## 12. Conclusions for RaiSE

### RAG Viability Assessment

✅ **RAG is HIGHLY VIABLE** for RaiSE's use case (100-200 guardrails)

**Expected Performance**:
- Token reduction: 90-95% vs static loading
- Baseline context: 2,000-5,000 tokens (vs 50,000-100,000)
- Retrieval latency: 50-200ms (acceptable)
- Accuracy: 90%+ recall with proper tuning

### Recommended Architecture

**Hybrid Multi-Tier**:
1. **Tier 1 (Hot)**: 20-30 critical rules, static, always loaded (~5,000 tokens)
2. **Tier 2 (Warm)**: Skills + CLI for tool integrations (~100 tokens metadata)
3. **Tier 3 (Cold)**: RAG-retrieved rules, 150-180 rules (~2,000 tokens on demand)

**Total Baseline**: ~7,000 tokens
**vs MCP**: 100,000 tokens
**Savings**: 93%

---

## Sources

1. [Token Efficiency and Compression in LLMs - Medium](https://medium.com/@anicomanesh/token-efficiency-and-compression-techniques-in-large-language-models-navigating-context-length-05a61283412b)
2. [Vector Databases for Generative AI 2026](https://brollyai.com/vector-databases-for-generative-ai-applications/)
3. [Best Embedding Models 2026](https://www.openxcell.com/blog/best-embedding-models/)
4. [Embeddings Explained - Medium](https://medium.com/@QuarkAndCode/embeddings-explained-vector-databases-semantic-search-rag-for-llm-apps-bc5a77ef39e9)
5. [Markdown vs JSON vs YAML Token Efficiency](https://community.openai.com/t/markdown-is-15-more-token-efficient-than-json/841742)
6. [Best Nested Data Format for LLMs](https://www.improvingagents.com/blog/best-nested-data-format/)
7. [TOON vs JSON vs YAML](https://medium.com/@ffkalapurackal/toon-vs-json-vs-yaml-token-efficiency-breakdown-for-llm-5d3e5dc9fb9c)

---

**Confidence Level**: HIGH (8/10)
**Implementation Complexity**: MEDIUM-HIGH
**Expected ROI**: VERY HIGH (90%+ token savings)
**Strategic Fit for RaiSE**: EXCELLENT
