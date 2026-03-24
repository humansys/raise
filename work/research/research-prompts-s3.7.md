# Research Prompts — Knowledge Infrastructure for Personal AI Agents

> 2 research axes for S3.7 design. Run as Claude Code subagents + Gemini Deep Research.
> Date: 2026-03-19
> Context: E3 ScaleUp Agent — S3.7 CLI Gates design
> Prior research (DO NOT duplicate):
>   - agentic-kg-construction (28 sources) — GraphRAG, multi-agent KG construction
>   - ontology-learning-from-text (24 sources) — extraction pipelines, LLM + deterministic scaffolding
>   - hitl-ontology-curation (20 sources) — expert curation workflows, session design

---

## R1: Personal Knowledge Graphs as Infrastructure for Reliable AI Agents

```
---
research_id: "personal-kg-agents-20260319"
primary_question: "How do personal AI agents build, maintain, and use structured
  knowledge about their user's world to provide reliable, grounded assistance —
  rather than relying solely on conversation history and generic training data?"
decision_context: "Architecture of knowledge infrastructure for rai-agent: a
  personal AI agent that needs to reliably assist across multiple life/work
  domains (business methodology, personal productivity, life management).
  Determines whether we build custom or adopt existing patterns."
depth: "standard"
created: "2026-03-19"
version: "1.0"
template: "research-prompt-v1"
---

# Research: Personal Knowledge Graphs as Infrastructure for Reliable AI Agents

## Role Definition

You are a **Research Specialist** with expertise in **personal AI agents,
knowledge representation, and human-AI interaction**. Your task is to conduct
epistemologically rigorous research following scientific standards.

Your responsibilities:
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality (Very High / High / Medium / Low)
- Triangulate findings: 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

## Research Question

**Primary**: How do personal AI agents build, maintain, and use structured
knowledge about their user's world to provide reliable, grounded assistance?

We are NOT asking about RAG (already researched), ontology extraction from text
(already researched), or multi-agent KG construction (already researched).

We ARE asking: once you HAVE a knowledge graph, how does a personal agent USE it
to be reliable? And how do you represent MULTIPLE domains for ONE person?

**Secondary questions**:

1. **Memory architectures for agents**: What knowledge/memory architectures do
   existing agent frameworks use? (MemGPT/Letta, Zep/Graphiti, LangMem, Cognee,
   mem0, etc.) How do they differ from simple RAG? Specifically:
   - How do they distinguish between episodic memory (what happened), semantic
     memory (what things are), and procedural memory (how to do things)?
   - Which use structured graphs vs. unstructured text stores?
   - What persistence and update mechanisms do they provide?

2. **Multi-domain representation**: How do Personal Knowledge Graph (PKG) systems
   represent knowledge from multiple domains for a single user? For example:
   - A user follows ScaleUp methodology for business (concepts, tools, metrics)
   - The same user uses GTD + Personal Kanban for personal productivity
   - The same user has life goals, health routines, financial targets
   - These domains INTERACT (business overcommitment → personal health impact)
   How do you represent these as connected subgraphs? What cross-domain reasoning
   becomes possible? What schema patterns handle this?

3. **Evidence for reliability improvement**: What evidence exists that structured
   knowledge improves agent reliability vs. unstructured memory?
   - Are there benchmarks comparing grounded vs. ungrounded agent responses?
   - User studies showing accuracy improvement with knowledge infrastructure?
   - Specific failure modes that structured knowledge prevents?
   (e.g., "Agent recommends X, but user's knowledge graph shows X contradicts
   their established process Y")

4. **Knowledge lifecycle**: How do agents handle:
   - Freshness: domains update at different frequencies (daily tasks vs. yearly
     strategic plans)
   - Conflicts: when new information contradicts existing graph state
   - Trust calibration: confidence in knowledge from different sources (book
     vs. personal experience vs. AI-extracted)
   - Forgetting: when knowledge becomes obsolete or irrelevant

5. **Failure modes WITHOUT structured knowledge**: What happens when agents don't
   have structured domain knowledge? Documented patterns:
   - Hallucination of domain-specific advice
   - Generic responses that ignore user's specific context
   - Loss of continuity across sessions
   - Inability to reason about relationships between concepts
   - Overconfidence in areas where the agent has no grounded knowledge

## Search Strategy

1. **Academic sources**
   - Google Scholar: "personal knowledge graph AI agent", "user modeling
     knowledge graph", "agent memory architecture structured"
   - arXiv: "personal AI assistant knowledge representation 2024 2025",
     "agent grounding structured knowledge", "knowledge-enhanced AI agents"
   - ACM DL: "personal knowledge management AI", "knowledge-grounded dialogue"
   - Purpose: Peer-reviewed research, theoretical foundations

2. **Agent frameworks (official docs + architecture)**
   - Letta/MemGPT (>30k stars): memory tier architecture, core memory vs.
     archival memory vs. recall memory
   - Zep/Graphiti (>5k stars): temporal knowledge graphs for agents, entity
     extraction, relationship tracking
   - Cognee (~2k stars): knowledge graph memory, how it builds and queries
   - mem0 (~25k stars): memory layer for AI, structured vs. unstructured
   - LangMem/LangGraph: memory integration patterns
   - CrewAI: agent knowledge configuration, long-term memory
   - AutoGen: agent memory and knowledge sharing
   - Purpose: Real implementations, architecture decisions

3. **Personal AI products (production evidence)**
   - Rewind.ai / Limitless: how they model user knowledge from screen capture
   - Dot (by New Computer): personal AI with structured user modeling
   - Personal.ai: personal AI with memory mesh
   - Omi (formerly Friend): wearable AI with memory
   - Notion AI / Obsidian AI plugins: knowledge base + AI assistant patterns
   - Purpose: What shipped products actually do, not just papers

4. **Community & emerging**
   - Reddit r/LocalLLaMA, r/AIAgents: practitioner experiences with memory
   - HN discussions on personal AI agents and memory
   - Conference talks NeurIPS/AAAI/ACL 2024-2025 on agent knowledge
   - Blog posts from personal AI builders
   - Purpose: Emerging patterns, failure stories, honest assessments

**Keywords** (10):
- "personal knowledge graph AI agent memory"
- "agent memory architecture structured graph"
- "multi-domain user model knowledge representation"
- "knowledge-grounded AI assistant reliability accuracy"
- "MemGPT Letta memory tier architecture"
- "Graphiti Zep temporal knowledge graph agent"
- "personal AI context persistence session continuity"
- "agent hallucination prevention knowledge grounding"
- "Cognee mem0 knowledge graph memory AI"
- "personal knowledge graph PKG user modeling survey 2024 2025"

**Avoid**: Pure RAG research, ontology extraction methods (both already
researched), enterprise knowledge management, customer service chatbots

## Evidence Evaluation Criteria

- **Very High**: Peer-reviewed, production-proven at scale, >10k GitHub stars
- **High**: Expert practitioners at established companies, >1k stars
- **Medium**: Community-validated, emerging consensus, >100 stars
- **Low**: Single source, unvalidated, <100 stars

## Triangulation

- Target: 15-30 sources (standard depth)
- Major claims: 3+ independent confirmations required
- Confidence: HIGH / MEDIUM / LOW with explicit criteria
- Contrary evidence: documented, not hidden

## Output

Three artifacts in work/research/personal-kg-agents/:

1. **evidence-catalog.md**: Per-source assessment with all fields
2. **synthesis.md**: Triangulated claims, patterns, gaps, unknowns
3. **recommendation.md**: What to adopt/build, with confidence and trade-offs

### Specific synthesis questions to address:

1. **Architecture choice**: Should rai-agent use an existing memory framework
   (Letta, Graphiti, mem0) or build on its existing raise-core graph engine?
   What would each path give us / cost us?

2. **Multi-domain schema**: What's the best-evidenced pattern for representing
   multiple life/work domains in a single knowledge graph? Separate subgraphs
   with bridge edges? Unified schema with domain tags? Federated graphs?

3. **Reliability mechanisms**: What specific mechanisms (beyond "use a knowledge
   graph") make agents more reliable? Retrieval-augmented verification?
   Confidence scoring? Contradicting detection?

4. **Minimum viable knowledge infrastructure**: What's the simplest thing that
   provides meaningful reliability improvement? We want to avoid building a
   full knowledge management platform when a focused solution works.
```

---

## R2: Knowledge Validation Tooling & Deterministic Quality Gates

```
---
research_id: "kg-validation-tooling-20260319"
primary_question: "What deterministic tools and frameworks exist for validating,
  testing, and measuring quality of knowledge graphs — and which patterns can we
  adopt for CLI-based poka-yoke gates in an LLM-driven extraction pipeline?"
decision_context: "Design of CLI validation gates for S3.7 — determines whether
  we build custom validators or wrap existing standards/tools"
depth: "standard"
created: "2026-03-19"
version: "1.0"
template: "research-prompt-v1"
---

# Research: Knowledge Validation Tooling & Deterministic Quality Gates

## Role Definition

You are a **Research Specialist** with expertise in **knowledge graph quality
assurance, ontology validation, and data quality engineering**. Your task is to
conduct epistemologically rigorous research following scientific standards.

Your responsibilities:
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality (Very High / High / Medium / Low)
- Triangulate findings: 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Focus on PRACTICAL, DETERMINISTIC tools — not ML-based quality prediction

## Research Question

**Primary**: What deterministic tools, standards, and frameworks exist for
validating knowledge graph quality — and which patterns are most applicable
for building CLI-based validation gates (poka-yoke) in an LLM-driven ontology
extraction pipeline?

**Context we already know** (from prior research, do NOT re-research):
- LLMs produce draft ontologies that need validation (ontology-learning research)
- Multi-agent pipelines can include validator agents (agentic-kg research)
- Human curation is needed for ~20% of assertions (hitl-curation research)

**What we DON'T know** (research THIS):
- What TOOLS exist for the deterministic validation steps
- What STANDARDS (SHACL, ShEx, etc.) are practical for non-RDF graphs
- What METRICS should our quality gates report
- What "graph testing" looks like in practice (analogous to unit testing)

**Secondary questions**:

1. **KG validation standards in practice**: SHACL, ShEx, OWL consistency —
   how are they used in real projects? Specifically:
   - Are they usable with property graphs (not RDF)? Or RDF-only?
   - What's the learning curve for a Python developer?
   - Are there lightweight Python libraries that implement them?
   - Can they validate YAML/JSON nodes or do they require RDF conversion?

2. **Property graph validation (non-RDF)**: Our knowledge graph uses Pydantic
   models serialized as YAML files, not RDF triples. What validation options
   exist for this representation?
   - Pydantic itself (schema validation) — is this sufficient?
   - JSON Schema validation for graph structure
   - Graph constraint languages for property graphs (GQL standard?)
   - Custom assertion frameworks

3. **Production KG quality pipelines**: How do real KG projects do quality
   assurance?
   - Wikidata: constraint system, SPARQL checks, bot-driven validation
   - DBpedia: extraction framework quality gates
   - Google Knowledge Graph: quality scoring (from published papers)
   - Enterprise KGs: what metrics do Stardog, Neo4j, TigerGraph recommend?
   - What's the standard set of quality dimensions? (accuracy, completeness,
     consistency, timeliness, uniqueness)

4. **"Graph testing" as discipline**: Is there an equivalent of unit testing
   for knowledge graphs?
   - Assertions about graph structure (e.g., "every tool node must belong
     to exactly one decision area")
   - Coverage checks (e.g., "all 4 decision areas have ≥5 nodes")
   - Consistency checks (e.g., "no orphan nodes", "no phantom references")
   - Regression tests (e.g., "re-extraction should produce ≥95% of previous
     nodes")
   - Any frameworks, libraries, or established patterns?

5. **Ontology extraction tool validation**: What do existing extraction tools
   do for output validation?
   - OntoGPT: what checks does SPIRES run?
   - KGGen: any built-in validation?
   - Neo4j LLM Graph Builder: quality checks?
   - LlamaIndex PropertyGraphIndex: validation options?

6. **Coverage and completeness metrics**: How do you measure whether a KG is
   "complete enough"?
   - Competency Question (CQ) evaluation — how is this automated?
   - Node/edge type distribution analysis
   - Connectivity metrics (orphans, isolated subgraphs, diameter)
   - Coverage against source corpus (are all important concepts captured?)
   - What thresholds are used in practice? (e.g., ≥80% CQ coverage)

## Search Strategy

1. **Standards & specifications**
   - W3C SHACL: spec, implementations, Python libraries (pySHACL)
   - W3C ShEx: spec, tooling, comparison with SHACL
   - Property Graph Schema: GQL (ISO), openCypher constraints
   - JSON Schema: graph structure validation patterns
   - Purpose: What standards bodies recommend, what's actually implemented

2. **Python tools & libraries**
   - pySHACL: GitHub (stars? maintenance?), docs, Python API
   - rdflib: validation capabilities
   - Pydantic v2: custom validators for graph constraints
   - NetworkX: graph analysis for consistency checks (connected components,
     orphan detection, cycle detection)
   - Great Expectations: data quality framework — any graph adapters?
   - Pandera: schema validation for data — graph equivalents?
   - linkml: linked data modeling in YAML — validation built in?
   - Purpose: What we can pip install and use today

3. **Production pipelines (implementation evidence)**
   - Wikidata quality pipeline: property constraints, SPARQL-based checks
   - DBpedia quality: extraction framework validation gates
   - Schema.org validator: how it works, what it checks
   - OntoGPT/SPIRES: output validation implementation
   - Purpose: Proven patterns from large-scale projects

4. **Academic (quality frameworks)**
   - Google Scholar: "knowledge graph quality metrics framework"
   - "ontology evaluation metrics automated"
   - "graph testing assertions methodology"
   - KG quality dimensions: ISO 25012, Zaveri et al. (2016) quality framework
   - Purpose: Comprehensive quality dimension taxonomies

**Keywords** (12):
- "knowledge graph validation tool deterministic Python"
- "SHACL property graph validation non-RDF"
- "pySHACL Python knowledge graph validation"
- "ontology quality metrics framework automated"
- "graph testing unit test assertions structure consistency"
- "knowledge graph quality dimensions completeness accuracy"
- "Wikidata quality control constraint violation bot"
- "ontology competency question coverage evaluation automated"
- "property graph schema validation YAML JSON"
- "knowledge graph reconciliation entity deduplication tool"
- "linkml YAML schema validation linked data"
- "graph data quality pipeline ETL gate checkpoint"

**Avoid**: Full OWL reasoning theory (too academic), enterprise data governance
platforms (Collibra, Informatica — overkill), ML-based quality prediction (we
need deterministic), RDF-specific tooling unless it works with property graphs

## Evidence Evaluation Criteria

- **Very High**: Peer-reviewed, production-proven at scale, >10k GitHub stars
- **High**: Expert practitioners at established companies, >1k stars
- **Medium**: Community-validated, emerging, >100 stars
- **Low**: Single source, unvalidated, <100 stars

## Triangulation

- Target: 15-30 sources (standard depth)
- Major claims: 3+ independent confirmations required
- Confidence: HIGH / MEDIUM / LOW
- Contrary evidence: documented

## Output

Three artifacts in work/research/kg-validation-tooling/:

1. **evidence-catalog.md**: Per-source assessment
2. **synthesis.md**: Triangulated claims, patterns, gaps
3. **recommendation.md**: What to adopt/build, confidence, trade-offs

### Specific synthesis questions to address:

1. **Build vs. adopt matrix**: For each of our 5 proposed gates, is there an
   existing tool we should wrap?

   | Gate | Function | Existing tool? |
   |------|----------|---------------|
   | validate | Schema validation of YAML nodes | Pydantic? SHACL? linkml? |
   | reconcile | Cross-reference consistency | NetworkX? Custom? |
   | coverage | Competency question coverage | Custom? Existing CQ evaluators? |
   | chunk | Corpus splitting | Already built (CorpusChunker) |
   | graph | Build graph + stats | Already built (ScaleUpGraphBuilder) |

2. **Standard compliance**: Should our YAML-based validation use SHACL under
   the hood? Or is Pydantic + custom graph assertions sufficient? What do we
   GAIN from standards compliance vs. what does it COST?

3. **Metrics catalog**: For each gate, what metrics should it report? Propose
   a concrete list based on what production KG pipelines actually track.

4. **Testing patterns**: What does "graph unit testing" look like? Can we
   define it as pytest assertions? Any framework we should model after?

## Constraints

**Time**: 4-6 hours equivalent
**Priority order**: (1) Lightweight validation for YAML/property graphs,
(2) Quality metrics for our gates, (3) Existing tools we can wrap
**Out of scope**: Full OWL reasoning, RDF-only tooling, enterprise governance,
ML-based quality prediction, anything already covered in prior research
```

---

## Execution Plan

| Prompt | Claude Code | Gemini Deep Research | Overlap with prior research? |
|--------|:-----------:|:--------------------:|------------------------------|
| R1: Personal KGs for Agents | ✅ run | ✅ copy prompt to Gemini | No — new axis |
| R2: KG Validation Tooling | ✅ run | ✅ copy prompt to Gemini | No — new axis |

### After both complete:
1. Merge evidence catalogs (Claude + Gemini per axis)
2. Cross-reference: where do they agree? disagree?
3. Synthesize into S3.7 design decisions
4. Resume `/rai-story-design` with evidence-backed choices
