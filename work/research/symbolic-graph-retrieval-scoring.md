# R3: Symbolic Graph Retrieval Scoring Without Embeddings

> Research Date: 2026-03-20
> Research Question: State of the art in ranking/scoring graph retrieval results using ONLY graph structure (no embeddings, no vector similarity)

---

## Evidence Catalog

### F1: Personalized PageRank (PPR) for Knowledge Graph Retrieval

**Claim:** Personalized PageRank is the current go-to algorithm for graph-based retrieval scoring. HippoRAG (NeurIPS 2024) uses PPR as its core retrieval mechanism over a knowledge graph, outperforming embedding-based RAG by up to 20% on multi-hop queries while being 6-13x faster than iterative retrieval.

**Sources:**
- [HippoRAG: Neurobiologically Inspired Long-Term Memory for LLMs](https://arxiv.org/abs/2405.14831) — NeurIPS 2024
- [Personalized Page Rank on Knowledge Graphs: Particle Filtering](https://openproceedings.org/2020/conf/edbt/paper_357.pdf) — EDBT 2020
- [Edge-Weighted Personalized PageRank](https://dl.acm.org/doi/10.1145/2783258.2783278) — KDD 2015

**Confidence:** Very High

**Relevance:** Directly applicable. PPR works by seeding activation at query-relevant nodes and diffusing through the graph. For small graphs (hundreds of nodes), computation converges in <50 iterations. NetworkX's `pagerank_numpy` uses LAPACK and is optimal for this scale. Edge weights can encode relationship type importance. The teleportation parameter (alpha, typically 0.85) controls how quickly relevance decays with distance.

**Key detail for our case:** In typed KGs, different edge types are assigned different weights in [0,1], and particle transitions are skewed toward more relevant nodes through more informative edges (EDBT 2020). This maps directly to our need for edge-type weighting.

---

### F2: Spreading Activation (SA) for Typed Graph Retrieval

**Claim:** Spreading activation is a well-established algorithm for associative retrieval over semantic networks. SA-RAG (2024) applies it to KG-based retrieval, using breadth-first propagation with edge-weight rescaling and activation thresholds. The core formula is: `a_j = min(1, a_j + sum(a_i * w_ij))`.

**Sources:**
- [SA-RAG: Leveraging Spreading Activation for Document Retrieval in KG-Based RAG](https://arxiv.org/abs/2512.15922) — 2024
- [Spreading Activation — Grokipedia](https://grokipedia.com/page/Spreading_activation)
- [Spreading Activation — Wikipedia](https://en.wikipedia.org/wiki/Spreading_activation)

**Confidence:** Very High

**Relevance:** Highly applicable. SA naturally supports typed edges via link weights W[i,j]. The algorithm is simple: seed nodes get activation=1, propagate through weighted edges with decay factor D (typically 0.5), fire nodes above threshold F. Terminates in 5-10 iterations. For our small graph, this is trivially fast.

**Key formulas:**
- Update: `A[j] = A[j] + (A[i] * W[i,j] * D)` where D is decay factor
- Bounds: activation clamped to [0.0, 1.0]
- SA-RAG rescaling: `w' = (w - c)/(1 - c)` where c=0.4 prevents over-activation
- SA-RAG thresholds: activation threshold=0.5, document pruning=0.45

---

### F3: Katz Centrality for Path-Based Relevance

**Claim:** Katz centrality computes node importance by summing all paths (not just shortest) with exponential decay by path length. Formula: `C_Katz(i) = sum_k sum_j alpha^k * (A^k)_ji`. Unlike PageRank which splits weight across successors, Katz propagates full (discounted) weight.

**Sources:**
- [Katz Centrality — GeeksforGeeks](https://www.geeksforgeeks.org/katz-centrality-centrality-measure/)
- [Katz Centrality — NetworkX documentation](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.katz_centrality.html)
- [Centrality Measures in Complex Networks Survey](https://arxiv.org/pdf/2011.07190)

**Confidence:** High

**Relevance:** Applicable but less suited than PPR or SA for our case. Katz computes global importance, not query-relative importance. You'd need to modify it to be "personalized Katz" (seed from query nodes), at which point it converges to something similar to PPR. The attenuation factor alpha must be < 1/lambda_max (largest eigenvalue). Default alpha=0.1, which gives heavy exponential decay.

**Key distinction:** Katz counts ALL walks (including revisits), while PPR models a random walker. For small typed graphs, the difference is minimal. PPR is better when you want query-personalized scores; Katz is better for global node importance.

---

### F4: ACT-R Activation Model — Fan Effect and Source Strength

**Claim:** The ACT-R cognitive architecture provides a principled model for retrieval scoring that accounts for source strength and the fan effect. The activation equation is: `Ai = Bi + sum_j(Wj * Sji)` where Bi is base-level activation, Wj is source attention weight (1/n for n sources), and Sji is associative strength attenuated by fan (number of associations from j).

**Sources:**
- [ACT-R Unit 5: Activation and Probability of Recall](http://act-r.psy.cmu.edu/wordpress/wp-content/themes/ACT-R/tutorials/unit5.htm)
- [Anderson 1983: A spreading activation theory of memory](http://www.jimdavies.org/summaries/anderson1983-2.html)

**Confidence:** High

**Relevance:** Highly relevant as a principled basis for composite scoring. The fan effect is directly applicable: a node connected to many other nodes has diluted associative strength per connection. This naturally penalizes highly-connected hub nodes that are structurally central but semantically generic. Retrieval time is exponential in activation: `T = F * e^(-Ai)`, giving a principled mapping from score to "how relevant is this."

**Key insight for our case:** The fan effect provides a principled answer to "should a node connected to 50 things score higher or lower than one connected to 3?" Answer: lower per-connection strength, modeling the intuition that specific connections are more informative than generic ones.

---

### F5: Edge-Type Weighting Strategies

**Claim:** Three main strategies for weighting edges by type in knowledge graphs: (1) Predicate Frequency — weight inversely proportional to predicate count (rare predicates are more informative, analogous to IDF); (2) Semantic Connectivity Score (SCS) — measures latent connections with path-length damping; (3) Hierarchical Similarity — weights based on position in type hierarchy.

**Sources:**
- [Knowledge graph-based weighting strategies for scholarly paper recommendation](https://ceur-ws.org/Vol-2290/kars2018_paper2.pdf) — KARS 2018
- [WiSP: Weighted Shortest Paths for RDF Graphs](https://www.semanticscholar.org/paper/WiSP:-Weighted-Shortest-Paths-for-RDF-Graphs-Tartari-Hogan/4d95700a6c5960e19602456269fc4ece73ffe51e) — VOILA 2018
- [Exploring Weighted Property Approaches for RDF Graph Similarity](https://arxiv.org/html/2404.19052v1) — 2024

**Confidence:** High

**Relevance:** Directly applicable. For our typed edges:
- **Predicate-frequency weighting (IDF analogy):** `w(p) = log(|E| / count(p))` — "requires" edges (rare, specific) get higher weight than "related-to" (common, generic)
- **Manual domain weights:** Assign weights per relationship type based on domain semantics. WiSP found this works well in practice, though it introduces subjectivity.
- **Path specificity:** Specificity of a path is inversely proportional to the sum of log-degrees of intermediate nodes. This penalizes paths through hub nodes.

**Key finding from WiSP:** Hybrid schemes combining path length, node weights, and edge weights outperformed single-signal schemes in user studies.

---

### F6: Node-Type Aware Ranking

**Claim:** Entity type ranking in KGs is a well-studied problem. Hierarchy-based approaches (scoring by position in type ontology) outperform flat approaches. The most effective methods combine: type hierarchy depth/specificity, collection statistics (type frequency), and graph structure (connectivity patterns).

**Sources:**
- [Contextualized ranking of entity types based on knowledge graphs](https://www.sciencedirect.com/science/article/abs/pii/S1570826815001468) — Journal of Web Semantics 2016
- [Predicate-Augmented Personalized PageRank for Entity Typing](https://ieeexplore.ieee.org/document/10189694/) — IEEE 2023

**Confidence:** High

**Relevance:** Directly applicable. For our query "what should I do?" where tool nodes should rank higher than metric nodes:
- Define a query-context-to-type relevance mapping (e.g., action-oriented queries boost "tool", "practice", "skill" types)
- Type specificity matters: a "testing-tool" node is more relevant than a generic "tool" node for a testing query
- Learning-to-rank models combining multiple type signals achieve best results, but a simple weighted lookup by query intent is sufficient for our scale.

---

### F7: Decay Functions for Multi-Hop Scoring

**Claim:** Exponential decay is the standard for graph-based relevance scoring. A decay factor of d=0.5 per hop is the most common default, meaning: hop 1 = 1.0, hop 2 = 0.5, hop 3 = 0.25, hop 4 = 0.125. This models the intuition that closer = more relevant, with diminishing returns. The SA-RAG paper additionally applies a rescaling threshold c=0.4 to prevent over-activation.

**Sources:**
- [Spreading Activation — Grokipedia](https://grokipedia.com/page/Spreading_activation) — "d = 0.5 per step, reducing activation exponentially"
- [SA-RAG paper](https://arxiv.org/abs/2512.15922) — threshold-based with rescaling
- [Katz centrality](https://www.geeksforgeeks.org/katz-centrality-centrality-measure/) — alpha=0.5 gives weights 0.5, 0.25, 0.125...
- [Distance decay models](https://www.spatialanalysisonline.com/HTML/distance_decay_models.htm)

**Confidence:** High

**Relevance:** Directly applicable. For our case:
- **Exponential decay (recommended):** `weight(hop) = alpha^hop` where alpha in [0.3, 0.7]
- **Linear decay is too slow** — gives too much weight to distant nodes in small graphs
- **Per-edge-type decay is the innovation:** "requires" might decay at 0.7/hop (strong relevance persists) while "related-to" decays at 0.3/hop (weak signal fades fast)

---

### F8: Evaluation Methodology for Symbolic KG Retrieval

**Claim:** Competency questions (CQs) are the standard evaluation methodology for KG retrieval quality, borrowing from test-driven development. A CQ defines "what should the KG be able to answer?" and evaluation measures precision/recall of retrieved nodes against gold-standard answers. A neuro-symbolic approach achieved P=0.70/R=0.68 vs a pure graph traversal baseline of P=0.28/R=0.25.

**Sources:**
- [Bench4KE: Benchmarking Automated Competency Question Generation](https://arxiv.org/html/2505.24554v3)
- [Quantifying Relational Exploration in Cultural Heritage KGs](https://www.mdpi.com/2306-5729/10/4/52)
- [Diagnosing and Addressing Pitfalls in KG-RAG](https://openreview.net/pdf?id=Vd5JXiX073)

**Confidence:** High

**Relevance:** Directly applicable as our evaluation methodology:
1. Write competency questions for each domain (e.g., "What tools help with X?", "What are the prerequisites for Y?")
2. For each CQ, manually identify the gold-standard set of relevant nodes
3. Run retrieval, measure Precision@K, Recall@K, F1
4. Compare scoring algorithms against the same CQ set

---

### F9: PageRank Anti-Patterns on Small Graphs

**Claim:** PageRank has known convergence issues on small graphs: (1) dangling nodes (no outlinks) create rank sinks; (2) spider traps (cycles with no exit) accumulate all rank; (3) small graphs may require more iterations to converge; (4) damping factor too high causes oscillation, too low washes out structure.

**Sources:**
- [PageRank — Neo4j Graph Data Science](https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/)
- [Deeper Inside PageRank](https://www.stat.uchicago.edu/~lekheng/meetings/mathofranking/ref/langville.pdf)
- [PageRank — NetworkX docs](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html)

**Confidence:** Very High

**Relevance:** Critical for our implementation. In a small ontology graph (hundreds of nodes):
- Leaf nodes are dangling nodes — must handle or they become rank sinks
- Some relationship types may create natural cycles (A requires B, B feeds-into A)
- With few nodes, the teleportation parameter has outsized effect
- **Spreading activation avoids most of these issues** because it's query-seeded and terminates by threshold, not by convergence of a global distribution

---

## Ranked Algorithm Recommendations

### Tier 1: Best Fit for Small, Rich, Typed Property Graphs

#### 1. Spreading Activation (RECOMMENDED)

**Why:** Purpose-built for associative retrieval in semantic networks. Naturally handles:
- Query-seeded activation (start from matched nodes)
- Edge-type weights (W[i,j] varies by relationship type)
- Exponential decay (built-in decay factor D)
- Type-aware scoring (node type can modulate received activation)
- Deterministic, fast, simple to implement (~50 lines of Python)
- No convergence issues — terminates by iteration count or threshold
- No dangling node / sink problems

**Limitations:** No principled handling of "global importance" — a rarely-referenced but directly-connected node scores the same as a frequently-referenced one. Mitigate with base-level activation (a la ACT-R).

#### 2. Personalized PageRank (STRONG ALTERNATIVE)

**Why:** Most-validated in recent KG retrieval work (HippoRAG, SA-RAG). Edge-weighted PPR supports typed edges. Well-supported in NetworkX, igraph, graph-tool.

**Limitations:** Convergence issues on small graphs (dangling nodes, sinks). Teleportation parameter requires tuning. Computes a global distribution rather than local activation — overkill for small graphs where you could just traverse everything.

#### 3. ACT-R Hybrid (Spreading Activation + Fan Effect)

**Why:** Adds the fan effect to spreading activation — nodes with many associations have diluted per-connection strength. This is the most principled model for "this specific connection is more relevant than that generic one."

**Limitations:** More complex. The base-level activation component (recency/frequency) may not apply to a static ontology.

### Tier 2: Useful Components but Not Primary Algorithm

#### 4. Katz Centrality
Good for precomputing global node importance scores. Not query-aware by default.

#### 5. Weighted Shortest Paths (WiSP)
Good for path-based explanations ("why is this node relevant?"). Not a ranking algorithm per se.

---

## Recommended Composite Scoring Formula

```
score(node) = alpha * structural_score
            + beta  * attribute_score
            + gamma * type_score

where:
  structural_score = spreading_activation(node)  # [0, 1]
  attribute_score  = attribute_match(node, query) # [0, 1]
  type_score       = type_relevance(node.type, query.intent) # [0, 1]

  alpha + beta + gamma = 1.0
  (suggested: alpha=0.5, beta=0.3, gamma=0.2)
```

### Structural Score: Spreading Activation

```python
def spreading_activation(graph, seed_nodes, edge_weights, decay=0.5, threshold=0.1, max_hops=4):
    activation = {n: 0.0 for n in graph.nodes}
    for seed in seed_nodes:
        activation[seed] = 1.0

    queue = list(seed_nodes)
    visited = set()

    for _ in range(max_hops):
        next_queue = []
        for node in queue:
            if node in visited:
                continue
            visited.add(node)
            for neighbor, edge_type in graph.neighbors_with_type(node):
                w = edge_weights.get(edge_type, 0.5)
                delta = activation[node] * w * decay
                activation[neighbor] = min(1.0, activation[neighbor] + delta)
                if activation[neighbor] > threshold:
                    next_queue.append(neighbor)
        queue = next_queue

    return activation
```

### Edge-Type Weighting Strategy

```python
# Option A: Manual domain weights (simple, effective)
EDGE_WEIGHTS = {
    "requires":     0.9,   # Strong semantic: prerequisite
    "feeds_into":   0.8,   # Strong semantic: enables
    "belongs_to":   0.7,   # Structural: containment
    "implements":   0.7,   # Structural: realization
    "measures":     0.6,   # Medium: observation
    "related_to":   0.3,   # Weak: generic association
    "see_also":     0.2,   # Very weak: tangential
}

# Option B: Predicate-frequency weighting (IDF analogy)
def edge_weight_idf(edge_type, edge_counts, total_edges):
    """Rare relationship types get higher weight."""
    return math.log(total_edges / edge_counts[edge_type])

# Option C: Hybrid (recommended)
def edge_weight_hybrid(edge_type, domain_weight, idf_weight, alpha=0.7):
    """Blend domain knowledge with frequency signal."""
    return alpha * domain_weight + (1 - alpha) * idf_weight
```

### Attribute Match Score

```python
def attribute_match(node, query_context):
    """Score how well node attributes match query context.

    Uses keyword overlap + exact-match bonus. No embeddings.
    """
    score = 0.0
    query_terms = set(tokenize(query_context))

    # Name/label match (highest signal)
    node_terms = set(tokenize(node.name))
    name_overlap = len(query_terms & node_terms) / max(len(query_terms), 1)
    score += 0.5 * name_overlap

    # Description/attribute match
    attr_terms = set(tokenize(node.description))
    attr_overlap = len(query_terms & attr_terms) / max(len(query_terms), 1)
    score += 0.3 * attr_overlap

    # Tag/keyword exact match bonus
    if hasattr(node, 'tags'):
        tag_match = len(query_terms & set(node.tags)) / max(len(query_terms), 1)
        score += 0.2 * tag_match

    return min(1.0, score)
```

### Node-Type Relevance

```python
# Map query intents to type boosts
TYPE_RELEVANCE = {
    "action": {"tool": 1.0, "practice": 0.9, "skill": 0.8, "process": 0.7, "metric": 0.3},
    "understand": {"concept": 1.0, "principle": 0.9, "pattern": 0.8, "metric": 0.7, "tool": 0.3},
    "measure": {"metric": 1.0, "indicator": 0.9, "tool": 0.7, "process": 0.5, "concept": 0.3},
    "default": {t: 0.5 for t in ALL_TYPES},  # uniform when no intent detected
}

def type_relevance(node_type, query_intent="default"):
    return TYPE_RELEVANCE.get(query_intent, TYPE_RELEVANCE["default"]).get(node_type, 0.3)
```

---

## Anti-Patterns: What Doesn't Work for Small Symbolic Graphs

### 1. Vanilla PageRank (without personalization)
Global PageRank on a small graph just reflects structural centrality (hub nodes win). It tells you nothing about query relevance. You MUST use Personalized PageRank with query-based seed nodes.

### 2. Embedding-based retrieval on small graphs
With hundreds of nodes, embeddings are overkill and introduce unnecessary complexity. Symbolic matching + graph traversal gives you full coverage and deterministic results. Embeddings shine at 10K+ nodes where exact traversal is infeasible.

### 3. BFS with uniform hop decay
The naive approach (current baseline). Loses all semantic richness because it treats every relationship type equally. A node 2 hops away via "requires" should score much higher than a node 1 hop away via "see_also."

### 4. GNN-based approaches
Graph Neural Networks require training data, embeddings, and are non-deterministic. They are designed for graphs with millions of nodes where hand-crafted features can't capture the patterns. For hundreds of nodes with rich type information, they're unnecessary complexity.

### 5. Unweighted Katz centrality
Like vanilla PageRank, it gives global importance, not query relevance. And for small graphs, the spectral radius constraint on alpha can be finicky.

### 6. Single-signal scoring
Using only graph distance, or only attribute match, or only type relevance. The composite approach consistently outperforms any single signal (WiSP found this, ACT-R models this, and it's common sense: relevance is multi-dimensional).

---

## Evaluation Methodology

### Recommended Approach: Competency Question Testing

1. **Define CQs:** For each domain area, write 10-20 competency questions:
   - "What tools help improve code quality?"
   - "What are the prerequisites for implementing CI/CD?"
   - "What practices relate to team communication?"

2. **Create gold standards:** For each CQ, manually identify 3-10 relevant nodes and rank them by relevance (1=most relevant).

3. **Run retrieval:** Execute each CQ against the scoring algorithm.

4. **Measure:**
   - **Precision@K** (K=3,5,10): Of the top K results, how many are in the gold set?
   - **Recall@K**: Of the gold set, how many appear in top K?
   - **NDCG** (Normalized Discounted Cumulative Gain): Accounts for ranking order
   - **MRR** (Mean Reciprocal Rank): How high does the first relevant result appear?

5. **Compare algorithms:** Run the same CQs with different scoring strategies (BFS baseline, SA, PPR, composite) and compare metrics.

6. **Tune weights:** Use a held-out CQ set to tune alpha/beta/gamma weights in the composite formula.

### Sample Evaluation Matrix

| Algorithm | P@5 | R@5 | NDCG | MRR | Latency |
|-----------|-----|-----|------|-----|---------|
| BFS (baseline) | ? | ? | ? | ? | <1ms |
| Spreading Activation | ? | ? | ? | ? | <5ms |
| PPR | ? | ? | ? | ? | <10ms |
| Composite (SA+attr+type) | ? | ? | ? | ? | <10ms |

---

## Summary of Key Decisions

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| Primary algorithm | Spreading Activation | Simple, fast, query-seeded, naturally supports typed edges |
| Decay function | Exponential (alpha=0.5 per hop) | Standard, well-validated, adjustable per edge type |
| Edge-type weighting | Manual domain weights + IDF hybrid | Domain knowledge is available; IDF catches generic predicates |
| Node-type handling | Query-intent-to-type relevance lookup | Simple, deterministic, covers common query patterns |
| Composite scoring | Weighted linear combination (0.5/0.3/0.2) | Standard approach, tune with CQ evaluation |
| Evaluation | Competency questions with P@K, NDCG, MRR | Established methodology for KG retrieval quality |

---

## Sources Index

1. [HippoRAG — NeurIPS 2024](https://arxiv.org/abs/2405.14831)
2. [SA-RAG: Spreading Activation for KG-RAG](https://arxiv.org/abs/2512.15922)
3. [PPR on Knowledge Graphs — EDBT 2020](https://openproceedings.org/2020/conf/edbt/paper_357.pdf)
4. [Edge-Weighted PPR — KDD 2015](https://dl.acm.org/doi/10.1145/2783258.2783278)
5. [Katz Centrality — GeeksforGeeks](https://www.geeksforgeeks.org/katz-centrality-centrality-measure/)
6. [Katz Centrality — NetworkX](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.katz_centrality.html)
7. [Spreading Activation — Grokipedia](https://grokipedia.com/page/Spreading_activation)
8. [KG-based weighting strategies — KARS 2018](https://ceur-ws.org/Vol-2290/kars2018_paper2.pdf)
9. [WiSP: Weighted Shortest Paths for RDF — VOILA 2018](https://www.semanticscholar.org/paper/WiSP:-Weighted-Shortest-Paths-for-RDF-Graphs-Tartari-Hogan/4d95700a6c5960e19602456269fc4ece73ffe51e)
10. [Weighted Property Approaches for RDF Similarity — 2024](https://arxiv.org/html/2404.19052v1)
11. [Contextualized Entity Type Ranking — JWS 2016](https://www.sciencedirect.com/science/article/abs/pii/S1570826815001468)
12. [ACT-R Unit 5: Activation and Recall](http://act-r.psy.cmu.edu/wordpress/wp-content/themes/ACT-R/tutorials/unit5.htm)
13. [Bench4KE: Competency Question Benchmarking](https://arxiv.org/html/2505.24554v3)
14. [PageRank — Neo4j GDS](https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/)
15. [Centrality Measures Survey](https://arxiv.org/pdf/2011.07190)
16. [Deeper Inside PageRank](https://www.stat.uchicago.edu/~lekheng/meetings/mathofranking/ref/langville.pdf)
17. [TF-IDF Optimization of Associative KG](https://www.mdpi.com/2076-3417/10/13/4590)
18. [Predicate-Augmented PPR for Entity Typing — IEEE 2023](https://ieeexplore.ieee.org/document/10189694/)
19. [Fast PageRank Implementation](https://github.com/asajadi/fast-pagerank)
20. [Distance-Based Propagation for KG Retrieval — EMNLP 2023](https://aclanthology.org/2023.emnlp-main.908.pdf)
