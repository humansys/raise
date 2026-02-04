---
id: "ADR-011"
title: "Concept-Level Graph Architecture for MVC"
date: "2026-01-31"
status: "Accepted"
related_to: ["ADR-004"]
supersedes: []
---

# ADR-011: Concept-Level Graph Architecture for MVC

## Context

### Problem

RaiSE needs a graph-based system to deliver Minimum Viable Context (MVC) to AI agents, reducing token usage while maintaining accuracy. Two architectural approaches were validated:

1. **File-level granularity**: Nodes represent entire files, edges represent file relationships
2. **Concept-level granularity**: Nodes represent semantic concepts within files (requirements, principles, outcomes), edges represent semantic relationships

### Hypothesis

Concept-level granularity would provide significantly greater token savings than file-level while maintaining implementation simplicity.

### Experimental Validation

**Experiment 1: File-Level Graph (2026-01-31)**
- Test case: Validate PRD task
- Manual approach: 5 files, 13,657 tokens
- File-level graph: 3 files, 6,796 tokens
- **Savings: 50% (6,861 tokens)**

**Experiment 2: Concept-Level Sanity Check (2026-01-31)**
- Test case: Validate PRD RF-05 requirement
- File-level: 3 files, 6,796 tokens
- Concept-level: 4 sections, 351 tokens
- **Savings: 95% vs file-level, 97% vs manual**

**Experiment 3: Concept Extraction Spike (2026-01-31)**
- Successfully extracted 23 concepts from governance files:
  - 8 requirements from prd.md
  - 7 outcomes from vision.md
  - 8 principles from constitution.md
- Auto-inferred 11 relationships using keyword matching
- Test query returned 132 tokens (98% savings vs file-level)
- **Complexity: EASY (regex-based extraction)**
- **Implementation estimate: 3-4 SP**

### Key Findings

| Metric | File-Level | Concept-Level | Winner |
|--------|------------|---------------|--------|
| **Token savings** | 50% | 97-98% | Concept ✅ |
| **Implementation complexity** | Medium (5-8 SP) | Easy (3-4 SP) | Concept ✅ |
| **Query precision** | File granularity | Section granularity | Concept ✅ |
| **Maintenance** | Track file changes | Track concept changes | Similar |

**Concept-level is superior on all dimensions.**

## Decision

**Build concept-level graph architecture directly in E2.**

Skip file-level graph as an intermediate step. File-level becomes a **fallback mode** for unparseable documents.

### Architecture

```yaml
# Concept-level graph schema
nodes:
  req-rf-05:
    type: requirement
    file: governance/projects/raise-cli/prd.md
    section: "RF-05: Golden Context Generation"
    lines: [206, 214]
    content: "The system MUST generate CLAUDE.md..."
    metadata:
      requirement_id: "RF-05"
      title: "Golden Context Generation"

  principle-governance-as-code:
    type: principle
    file: framework/reference/constitution.md
    section: "§2. Governance as Code"
    lines: [33, 50]
    content: "Standards versioned in Git..."
    metadata:
      principle_number: "2"
      principle_name: "Governance as Code"

edges:
  - from: req-rf-05
    to: principle-governance-as-code
    type: governed_by
    reason: "Requirement relates to governance artifacts"
```

### Concept Types

| Type | Source Document | Extraction Pattern |
|------|----------------|-------------------|
| `requirement` | PRD | `### RF-\d+: (.+)` |
| `outcome` | Vision | Table rows with outcome descriptions |
| `principle` | Constitution | `### §\d+\. (.+)` |
| `pattern` | Design | TBD (future) |
| `practice` | Katas | TBD (future) |

### Relationship Types

| Type | Meaning | Example |
|------|---------|---------|
| `implements` | Requirement implements outcome | req-rf-05 → outcome-context-generation |
| `governed_by` | Artifact governed by principle | req-rf-05 → principle-governance-as-code |
| `depends_on` | Concept depends on another | outcome-A → principle-B |
| `related_to` | Semantic relationship | principle-A → pattern-B |

### Extraction Strategy

**Phase 1 (E2 MVP):**
- Parse PRD requirements (RF-XX)
- Parse Vision outcomes (table extraction)
- Parse Constitution principles (§N)
- Keyword-based relationship inference

**Phase 2 (E2.5 - Future):**
- Parse Design patterns
- Parse Kata practices
- ML-based relationship inference
- Cross-document semantic linking

### Fallback Behavior

```python
def get_mvc(task: str) -> MVC:
    """Get minimum viable context for task"""
    try:
        # Try concept-level first
        concepts = query_concept_graph(task)
        return build_mvc_from_concepts(concepts)
    except ConceptNotFound:
        # Fallback to file-level
        files = query_file_graph(task)
        return build_mvc_from_files(files)
```

Graceful degradation ensures the system works even for documents not yet parsed into concepts.

## Consequences

### Positive ✅

1. **Massive token savings**: 97-98% reduction vs manual, 95% vs file-level
2. **Lower implementation cost**: 3-4 SP vs 5-8 SP for file-level
3. **Higher precision**: Returns exactly relevant sections, not entire files
4. **Simpler queries**: Concept relationships are more natural than file relationships
5. **Observability**: Can explain exactly why each concept was included
6. **Scalability**: Token savings increase as governance grows

### Negative ⚠️

1. **Parsing dependency**: Requires markdown parsing for each document type
2. **Schema evolution**: New concept types require parser updates
3. **Relationship maintenance**: Graph edges may become stale if documents change
4. **Initial indexing cost**: Must parse all documents to build graph (one-time)

### Neutral 🔄

1. **File-level still exists**: Maintained as fallback, not wasted work
2. **Graph validation**: Need to detect when documents change and re-parse
3. **Query language**: Same traversal engine works for both levels

## Implementation Plan (E2)

### F2.1: Concept Extraction (3 SP)
- Requirements parser (PRD RF-XX format)
- Outcomes parser (Vision table format)
- Principles parser (Constitution §N format)
- Concept schema (Pydantic models)

### F2.2: Graph Builder (2 SP)
- Relationship inference (keyword matching)
- Graph serialization (JSON/YAML)
- Graph validation (detect broken references)

### F2.3: MVC Query Engine (2 SP)
- Graph traversal (BFS with edge filters)
- Concept aggregation (dedupe, sort by relevance)
- Fallback to file-level (graceful degradation)

### F2.4: CLI Commands (2 SP)
- `raise graph build` - Parse governance into concepts
- `raise context query --task <task>` - Get MVC for task
- `raise graph validate` - Check graph consistency

**Total: ~9 SP** (reduced from original 31 SP for kata/gate engines)

## Alternatives Considered

### Alternative 1: File-Level Graph Only
**Rejected because:**
- Only 50% token savings vs 97% for concept-level
- Higher implementation cost (5-8 SP)
- Less precise (returns entire files)
- Doesn't align with "ontología bajo demanda" vision

### Alternative 2: Build File-Level First, Evolve to Concept
**Rejected because:**
- Concept-level is EASIER to implement (3-4 SP vs 5-8 SP)
- File-level becomes throwaway work
- Delays access to 95% of value
- Violates lean principles (build proven value first)

### Alternative 3: Manual Curation of Concepts
**Rejected because:**
- Doesn't scale (every new requirement = manual graph update)
- Error-prone (humans forget to update relationships)
- Violates "Governance as Code" (extraction should be automated)

## Validation

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Token reduction | >90% | Compare MVC tokens to manual approach |
| Query accuracy | 100% dependencies | No missing required concepts |
| Query speed | <1s | Measure graph traversal time |
| Concept coverage | >80% | % of governance content parsed |

### Monitoring

```python
# Track in production
@observe_mvc_query
def query_mvc(task: str) -> MVC:
    metrics = {
        "task": task,
        "concepts_returned": len(mvc.concepts),
        "tokens_saved": manual_tokens - mvc_tokens,
        "fallback_used": mvc.used_fallback
    }
    log_metrics(metrics)
```

## References

- **Experiment Results**: `dev/experiments/test_mvc.py` (file-level validation)
- **Concept Spike**: `dev/experiments/concept_extraction_spike.py` (proof of feasibility)
- **Ontology Research**: `work/tracking/ontology-backlog.md` (ONT-018, ONT-020, ONT-022)
- **ADR-004**: Separate graph architecture (file-level precursor)
- **Semantic Density Research**: `work/research/sar-component/semantic-density/`

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-31 | Experiment with file-level | Test graph hypothesis |
| 2026-01-31 | Sanity check concept-level | Validate if more savings exist |
| 2026-01-31 | Spike concept extraction | Prove implementation feasibility |
| 2026-01-31 | **Accept concept-level** | 98% savings, easier to build, proven feasible |

---

**Status**: Accepted (2026-01-31)

**Approved by**: Emilio Osorio, Rai

**Next steps**:
1. Update E2 scope document with concept-level features
2. Create graph schema (Pydantic models)
3. Implement parsers for PRD, Vision, Constitution
4. Build MVC query engine
