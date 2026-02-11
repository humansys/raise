---
story_id: "F2.3"
title: "MVC Query Engine"
epic: "E2: Governance Toolkit"
story_points: 2
complexity: "moderate"
status: "design"
created: "2026-01-31"
---

# F2.3: MVC Query Engine

## What & Why

**Problem**: RaiSE needs a query interface to extract Minimum Viable Context (MVC) from the concept graph, enabling AI agents to retrieve only the relevant governance concepts for a given task instead of loading entire files.

**Value**: Enables 97% token savings (validated via spike) by returning only relevant concepts and their immediate dependencies, making AI context queries fast, cheap, and precise. Provides deterministic "why this concept?" explanations through relationship paths.

## Approach

Build a query engine that takes queries (concept IDs or keywords), maps them to graph traversal strategies, and returns formatted Minimum Viable Context (MVC):

**Architecture**: Query → Strategy Selection → Graph Traversal → Format → Return MVC

- **Query models**: `MVCQuery` (query params) + `MVCResult` (concepts + metadata)
- **Query engine**: Orchestrates strategy selection, graph traversal, and result formatting
- **Strategies**: 4 query strategies (concept lookup, keyword search, relationship traversal, related concepts)
- **Formatters**: Multiple output formats (markdown, JSON, context blocks)

**Key insight from spike**: Simple keyword matching + BFS traversal is sufficient for 97% token savings. No need for complex NLP or semantic search in MVP.

**Components affected**:
- CREATE: `src/rai_cli/governance/query/` (new submodule)
  - `models.py` - MVCQuery, MVCResult, QueryStrategy
  - `engine.py` - Query orchestration and execution
  - `strategies.py` - Query strategy implementations (concept, requirement, principle, related)
  - `formatters.py` - Output formatters (markdown, json, context)
- CREATE: `src/rai_cli/cli/commands/context.py` - New CLI command group
- MODIFY: `src/rai_cli/cli/app.py` - Register context commands
- CREATE: `tests/governance/query/` (test suite)

## Examples

### CLI Usage

```bash
# Query by concept ID (returns concept + dependencies)
$ raise context query "req-rf-05"

Querying concept graph for: req-rf-05
Strategy: concept_lookup

📋 Minimum Viable Context (MVC):

## req-rf-05: Golden Context Generation

The system MUST generate CLAUDE.md files containing governance-derived
context to prime AI agents with project-specific rules...

### Governed By:
- §2: Governance as Code
  Standards versioned in Git; what's not in repo doesn't exist...

### Implements:
- Outcome: Context Generation
  Reduce AI hallucination by 80% through governed context...

---
Token estimate: ~350 tokens (vs ~6,796 full file)
Savings: 95%

# Query by requirement pattern
$ raise context query "requirements about validation"

Querying concept graph for: requirements about validation
Strategy: keyword_search + type_filter

📋 Minimum Viable Context (MVC):

Found 3 matching concepts:

## req-rf-03: Validation Gates
...

## req-rf-07: Gate Execution Engine
...

## req-nf-02: Validation Performance
...

---
Token estimate: ~580 tokens
Concepts returned: 3

# Query principles governing a requirement
$ raise context query "what governs RF-05?"

Querying concept graph for: what governs RF-05?
Strategy: relationship_traversal (governed_by)

📋 Minimum Viable Context (MVC):

## Principles governing req-rf-05:

### §2: Governance as Code
Standards versioned in Git...

### §4: Validation Gates
Quality checked at each phase...

---
Path: req-rf-05 --[governed_by]--> principle-governance-as-code
Path: req-rf-05 --[governed_by]--> principle-validation-gates

# Output as JSON (for tool integration)
$ raise context query "req-rf-05" --format json

{
  "query": "req-rf-05",
  "strategy": "concept_lookup",
  "concepts": [
    {
      "id": "req-rf-05",
      "type": "requirement",
      "section": "RF-05: Golden Context Generation",
      "content": "The system MUST...",
      "metadata": {...}
    },
    {
      "id": "principle-governance-as-code",
      "type": "principle",
      ...
    }
  ],
  "metadata": {
    "total_concepts": 2,
    "token_estimate": 350,
    "traversal_depth": 1,
    "paths": [
      ["req-rf-05", "principle-governance-as-code"]
    ]
  }
}

# Save result to file for agent consumption
$ raise context query "req-rf-05" --output context.md
✓ MVC written to context.md
```

### Python API

```python
from raise_cli.governance.query import MVCQueryEngine, MVCQuery, QueryStrategy
from pathlib import Path

# Load or build graph
engine = MVCQueryEngine.from_cache()  # Uses .raise/cache/graph.json

# Query by concept ID
result = engine.query(
    MVCQuery(
        query="req-rf-05",
        strategy=QueryStrategy.CONCEPT_LOOKUP,
        max_depth=1
    )
)

print(f"Concepts: {len(result.concepts)}")
print(f"Tokens: {result.metadata.token_estimate}")
# Output: Concepts: 2, Tokens: 350

# Format as markdown
markdown = result.to_markdown()
print(markdown)

# Query by keyword with type filter
result = engine.query(
    MVCQuery(
        query="validation",
        strategy=QueryStrategy.KEYWORD_SEARCH,
        filters={"type": "requirement"}
    )
)

# Query relationships
result = engine.query(
    MVCQuery(
        query="req-rf-05",
        strategy=QueryStrategy.RELATIONSHIP_TRAVERSAL,
        filters={"edge_types": ["governed_by", "implements"]}
    )
)

# Save to file
result.to_file(Path("context.md"), format="markdown")
```

### Data Structures

```python
from pydantic import BaseModel, Field
from enum import Enum
from raise_cli.governance.models import Concept

class QueryStrategy(str, Enum):
    """Query strategy for MVC extraction"""

    CONCEPT_LOOKUP = "concept_lookup"          # Direct ID lookup + dependencies
    KEYWORD_SEARCH = "keyword_search"          # Keyword match across concepts
    RELATIONSHIP_TRAVERSAL = "relationship"    # Follow specific edge types
    RELATED_CONCEPTS = "related"               # Semantic similarity

class MVCQuery(BaseModel):
    """MVC query parameters"""

    query: str = Field(..., description="Query string (concept ID or keywords)")
    strategy: QueryStrategy = Field(
        default=QueryStrategy.CONCEPT_LOOKUP,
        description="Query execution strategy"
    )
    max_depth: int = Field(
        default=1,
        ge=0,
        le=5,
        description="Maximum traversal depth"
    )
    filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Query filters (type, edge_types, confidence_threshold)"
    )

    # Examples of filters:
    # {"type": "requirement"}  - Only return requirements
    # {"edge_types": ["governed_by"]}  - Only follow governed_by edges
    # {"confidence_threshold": 0.7}  - Only high-confidence relationships

class MVCResult(BaseModel):
    """MVC query result with concepts and metadata"""

    concepts: list[Concept] = Field(
        default_factory=list,
        description="Concepts included in MVC"
    )
    metadata: MVCMetadata = Field(
        ...,
        description="Result metadata (token count, paths, strategy)"
    )

    def to_markdown(self) -> str:
        """Format as markdown for AI consumption"""
        # Implementation in formatters.py
        pass

    def to_json(self) -> str:
        """Format as JSON"""
        return self.model_dump_json(indent=2)

    def to_file(self, path: Path, format: str = "markdown") -> None:
        """Save to file"""
        if format == "markdown":
            path.write_text(self.to_markdown())
        else:
            path.write_text(self.to_json())

class MVCMetadata(BaseModel):
    """Metadata about MVC result"""

    query: str = Field(..., description="Original query")
    strategy: QueryStrategy = Field(..., description="Strategy used")
    total_concepts: int = Field(..., description="Number of concepts returned")
    token_estimate: int = Field(..., description="Estimated token count")
    traversal_depth: int = Field(..., description="Actual depth traversed")
    paths: list[list[str]] = Field(
        default_factory=list,
        description="Relationship paths from query to results"
    )
    execution_time_ms: float = Field(..., description="Query execution time")
```

## Acceptance Criteria

**MUST:**
- Implement 4 query strategies:
  1. **CONCEPT_LOOKUP**: Direct ID lookup + 1-hop dependencies (governed_by, implements)
  2. **KEYWORD_SEARCH**: Keyword matching with optional type filter
  3. **RELATIONSHIP_TRAVERSAL**: Follow specific edge types from starting concept
  4. **RELATED_CONCEPTS**: Semantic similarity via shared keywords
- Load graph from JSON (`.raise/cache/graph.json`)
- Return MVCResult with concepts, metadata (token estimate, paths)
- Format as markdown (section headers, relationship annotations)
- Format as JSON (structured output for tool integration)
- CLI command `rai context query <query>` with `--format` and `--output` options
- Token estimation: count words in result content * 1.3 (spike-validated heuristic)
- Include relationship paths in metadata (for "why this concept?" explanations)
- >90% test coverage on query module
- All code passes type checking (`pyright --strict`)

**SHOULD:**
- Auto-detect strategy from query pattern:
  - `req-rf-05` → CONCEPT_LOOKUP
  - `"validation"` → KEYWORD_SEARCH
  - `"what governs RF-05?"` → RELATIONSHIP_TRAVERSAL
- Support query result caching (avoid re-traversing for same query)
- Include confidence scores in results (from relationship metadata)
- Warn if query returns 0 concepts
- Suggest alternatives if query fails (fuzzy match concept IDs)

**MUST NOT:**
- Require external NLP libraries (keyword matching is sufficient)
- Load full files into memory (work with graph only)
- Return concepts without relationship context (always include paths)
- Exceed 3% token usage vs manual file loading (per spike validation)

## Query Strategy Details

### 1. CONCEPT_LOOKUP

Direct ID lookup with immediate dependencies.

```python
def query_concept_lookup(
    graph: ConceptGraph,
    query: MVCQuery
) -> MVCResult:
    """
    Lookup concept by ID and include immediate dependencies.

    Example: "req-rf-05" → Returns RF-05 + governed_by + implements
    """
    concept_id = normalize_concept_id(query.query)  # "RF-05" → "req-rf-05"

    if concept_id not in graph.nodes:
        return MVCResult(concepts=[], metadata=...)

    # Start with the concept itself
    concepts = [graph.nodes[concept_id]]
    paths = []

    # Add dependencies based on edge types
    edge_types = query.filters.get("edge_types", ["governed_by", "implements"])

    for edge_type in edge_types:
        edges = graph.get_outgoing_edges(concept_id, edge_type=edge_type)
        for edge in edges:
            target = graph.nodes[edge.target]
            concepts.append(target)
            paths.append([concept_id, edge.target])

    return MVCResult(
        concepts=concepts,
        metadata=MVCMetadata(
            query=query.query,
            strategy=query.strategy,
            total_concepts=len(concepts),
            token_estimate=estimate_tokens(concepts),
            paths=paths,
            ...
        )
    )
```

### 2. KEYWORD_SEARCH

Match keywords in concept section/content, optionally filter by type.

```python
def query_keyword_search(
    graph: ConceptGraph,
    query: MVCQuery
) -> MVCResult:
    """
    Search concepts by keyword with optional type filter.

    Example: "validation" + type=requirement → Returns all requirements mentioning validation
    """
    keywords = extract_keywords(query.query)
    concept_type = query.filters.get("type")  # Optional: "requirement", "principle", etc.

    matches = []
    for concept in graph.nodes.values():
        # Type filter
        if concept_type and concept.type.value != concept_type:
            continue

        # Keyword match (section or content)
        text = (concept.section + " " + concept.content[:500]).lower()
        if any(kw in text for kw in keywords):
            matches.append(concept)

    # Sort by relevance (count of matching keywords)
    matches.sort(
        key=lambda c: sum(
            1 for kw in keywords
            if kw in (c.section + " " + c.content[:500]).lower()
        ),
        reverse=True
    )

    return MVCResult(concepts=matches, metadata=...)
```

### 3. RELATIONSHIP_TRAVERSAL

Follow specific edge types from starting concept.

```python
def query_relationship_traversal(
    graph: ConceptGraph,
    query: MVCQuery
) -> MVCResult:
    """
    Traverse graph following specific relationship types.

    Example: "req-rf-05" + edge_types=["governed_by"] → Returns principles governing RF-05
    """
    from raise_cli.governance.graph.traversal import traverse_bfs

    concept_id = normalize_concept_id(query.query)
    edge_types = query.filters.get("edge_types", ["governed_by", "implements"])

    # Use existing BFS traversal from F2.2
    concepts = traverse_bfs(
        graph,
        start_id=concept_id,
        edge_types=edge_types,
        max_depth=query.max_depth
    )

    # Trace paths
    paths = trace_paths(graph, concept_id, concepts, edge_types)

    return MVCResult(concepts=concepts, metadata=..., paths=paths)
```

### 4. RELATED_CONCEPTS

Find semantically related concepts via shared keywords.

```python
def query_related_concepts(
    graph: ConceptGraph,
    query: MVCQuery
) -> MVCResult:
    """
    Find concepts related to query via keyword overlap.

    Example: "context generation" → Returns concepts with shared keywords
    """
    query_keywords = extract_keywords(query.query)

    # Score each concept by keyword overlap
    scored_concepts = []
    for concept in graph.nodes.values():
        concept_keywords = extract_keywords(
            concept.section + " " + concept.content[:500]
        )
        shared = query_keywords & concept_keywords

        if len(shared) >= 2:  # At least 2 shared keywords
            score = len(shared) / len(query_keywords)
            scored_concepts.append((concept, score, shared))

    # Sort by score
    scored_concepts.sort(key=lambda x: x[1], reverse=True)

    # Take top N
    top_n = query.filters.get("limit", 5)
    concepts = [c for c, score, _ in scored_concepts[:top_n]]

    return MVCResult(concepts=concepts, metadata=...)
```

## Output Format Examples

### Markdown Format (Default)

```markdown
# Minimum Viable Context (MVC)

Query: `req-rf-05`
Strategy: concept_lookup
Concepts: 2 | Tokens: ~350 | Depth: 1

---

## req-rf-05: Golden Context Generation
**Type:** Requirement | **File:** governance/projects/raise-cli/prd.md

The system MUST generate CLAUDE.md files containing governance-derived
context to prime AI agents with project-specific rules...

### Governed By:

#### §2: Governance as Code
**Type:** Principle | **File:** framework/reference/constitution.md

Standards versioned in Git; what's not in repo doesn't exist...

### Implements:

#### Outcome: Context Generation
**Type:** Outcome | **File:** governance/solution/vision.md

Reduce AI hallucination by 80% through governed context...

---

**Relationship Paths:**
- `req-rf-05` --[governed_by]--> `principle-governance-as-code`
- `req-rf-05` --[implements]--> `outcome-context-generation`

**Token Savings:** 95% (350 tokens vs ~6,796 full files)
```

### JSON Format

```json
{
  "query": "req-rf-05",
  "strategy": "concept_lookup",
  "concepts": [
    {
      "id": "req-rf-05",
      "type": "requirement",
      "file": "governance/projects/raise-cli/prd.md",
      "section": "RF-05: Golden Context Generation",
      "lines": [206, 214],
      "content": "The system MUST generate CLAUDE.md...",
      "metadata": {
        "requirement_id": "RF-05",
        "title": "Golden Context Generation"
      }
    },
    {
      "id": "principle-governance-as-code",
      "type": "principle",
      "file": "framework/reference/constitution.md",
      "section": "§2. Governance as Code",
      "lines": [33, 50],
      "content": "Standards versioned in Git...",
      "metadata": {
        "principle_number": "2",
        "principle_name": "Governance as Code"
      }
    }
  ],
  "metadata": {
    "total_concepts": 2,
    "token_estimate": 350,
    "traversal_depth": 1,
    "paths": [
      ["req-rf-05", "principle-governance-as-code"],
      ["req-rf-05", "outcome-context-generation"]
    ],
    "execution_time_ms": 12.5
  }
}
```

## Performance Constraints

**Query execution:**
- Direct lookup (<10 concepts): <50ms
- Keyword search (full graph): <200ms
- BFS traversal (depth 3): <100ms

**Token efficiency:**
- Typical MVC result: 200-500 tokens
- vs Manual file loading: 5,000-15,000 tokens
- **Target savings: >90%** (validated via spike)

**Memory:**
- Graph loaded once, reused across queries
- No full file loading required
- Peak memory <100MB for typical governance corpus

## Testing Approach

**Unit tests** for each strategy:
```python
def test_concept_lookup_strategy():
    """Test direct concept lookup with dependencies"""
    # Given: Graph with req-rf-05 and related concepts
    graph = build_test_graph()
    engine = MVCQueryEngine(graph)

    # When: Query by concept ID
    result = engine.query(MVCQuery(
        query="req-rf-05",
        strategy=QueryStrategy.CONCEPT_LOOKUP
    ))

    # Then: Should return concept + dependencies
    assert len(result.concepts) >= 2  # RF-05 + at least 1 dependency
    assert result.concepts[0].id == "req-rf-05"
    assert result.metadata.token_estimate > 0
    assert len(result.metadata.paths) > 0

def test_keyword_search_strategy():
    """Test keyword search with type filter"""
    # Given: Graph with multiple requirements about validation
    graph = build_test_graph()
    engine = MVCQueryEngine(graph)

    # When: Search for "validation" in requirements
    result = engine.query(MVCQuery(
        query="validation",
        strategy=QueryStrategy.KEYWORD_SEARCH,
        filters={"type": "requirement"}
    ))

    # Then: Should return only matching requirements
    assert all(c.type.value == "requirement" for c in result.concepts)
    assert all("validation" in (c.section + c.content).lower()
               for c in result.concepts)

def test_relationship_traversal_strategy():
    """Test following specific edge types"""
    # Given: Graph with governed_by relationships
    graph = build_test_graph()
    engine = MVCQueryEngine(graph)

    # When: Traverse governed_by edges from requirement
    result = engine.query(MVCQuery(
        query="req-rf-05",
        strategy=QueryStrategy.RELATIONSHIP_TRAVERSAL,
        filters={"edge_types": ["governed_by"]}
    ))

    # Then: Should return principles only
    assert all(c.type.value == "principle" or c.id == "req-rf-05"
               for c in result.concepts)
    assert all(
        any(edge_type in path_str for path_str in str(result.metadata.paths))
        for edge_type in ["governed_by"]
    )
```

**Integration tests** for full workflow:
```python
def test_end_to_end_mvc_query_from_real_graph():
    """Test MVC query against real raise-commons governance"""
    # Given: Real graph built from governance files
    from raise_cli.governance import GovernanceExtractor
    from raise_cli.governance.graph.builder import GraphBuilder

    extractor = GovernanceExtractor()
    concepts = extractor.extract_all()
    builder = GraphBuilder()
    graph = builder.build(concepts)

    engine = MVCQueryEngine(graph)

    # When: Query for RF-05
    result = engine.query(MVCQuery(query="req-rf-05"))

    # Then: Should achieve >90% token savings
    # Manual would load: prd.md + vision.md + constitution.md (~6,796 tokens)
    # MVC should return: <500 tokens
    assert result.metadata.token_estimate < 500
    savings_pct = (1 - result.metadata.token_estimate / 6796) * 100
    assert savings_pct > 90

def test_cli_context_query_command():
    """Test CLI command integration"""
    # When: Run CLI command
    result = runner.invoke(app, ["context", "query", "req-rf-05"])

    # Then: Should succeed with formatted output
    assert result.exit_code == 0
    assert "Minimum Viable Context" in result.stdout
    assert "req-rf-05" in result.stdout
    assert "Token estimate:" in result.stdout
```

**Edge cases:**
- Query for non-existent concept → Empty result with helpful message
- Query with no matches → Suggest fuzzy alternatives
- Malformed query string → Graceful error handling
- Empty graph → Clear error message
- Circular dependencies → BFS handles via visited set

## Dependencies

**Blocked by**:
- F2.1 (Concept Extraction) ✓ COMPLETE
- F2.2 (Graph Builder) ✓ COMPLETE

**Blocks**:
- F2.4 (CLI Commands) - Needs MVC query for context commands
- E4 (Context Generation) - Will consume MVC results

**External dependencies**:
- Standard library only (re, pathlib, typing, collections, time)
- Pydantic (already in project)
- Rich (already in project for CLI formatting)
- No new packages required

**Internal dependencies**:
- `raise_cli.governance.models.Concept`
- `raise_cli.governance.graph.models.ConceptGraph`
- `raise_cli.governance.graph.traversal.traverse_bfs`

## References

- **F2.2 Graph Builder**: `work/stories/f2.2-graph-builder/` (provides graph + traversal)
- **Spike validation**: `dev/experiments/test_mvc.py` (97% token savings proven)
- **Architecture**: `dev/decisions/adr-011-concept-level-graph-architecture.md`
- **Epic scope**: `dev/epic-e2-scope.md`
- **Token estimation heuristic**: word_count * 1.3 (from spike)

---

*Created: 2026-01-31*
*Ready for: `/story-plan`*
