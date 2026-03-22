# Evidence Catalog: Epistemic Infrastructure for AI Agents

> **Date:** 2026-03-22
> **Researcher:** Emilio + Rai
> **Depth:** Standard (22 sources, 4 research tracks)
> **Story:** RAISE-653 / S650.1

---

## Source Registry

### S01 — Codified Context: Infrastructure for AI Agents in a Complex Codebase
- **Type:** Primary (peer-reviewed, arXiv 2602.20478)
- **Evidence Level:** Very High
- **URL:** https://arxiv.org/html/2602.20478v1
- **Key Finding:** Three-tier knowledge infrastructure (hot memory / specialist agents / cold knowledge base) for LLM coding agents. 283 sessions, 108K-line system built in 70 days. Context infra = 24.2% of codebase. Maintenance: 1-2h/week. Staleness is primary failure mode.
- **Relevance:** DIRECTLY addresses our problem. Closest prior art to RaiSE cartridges but without schema contracts or validation — pure documentation approach.

### S02 — Towards a Science of AI Agent Reliability
- **Type:** Primary (arXiv 2602.16666)
- **Evidence Level:** Very High
- **URL:** https://arxiv.org/html/2602.16666v1
- **Key Finding:** Reliability ≠ capability. Four dimensions: Consistency, Robustness, Predictability, Safety. 12 concrete metrics. "Reliability gains lag noticeably behind capability progress" across 14 models. Architecture-level optimization needed, not just better models.
- **Relevance:** Validates T1 (reliability bounded by factors beyond LLM capability). Provides formal measurement framework we could adopt.

### S03 — SymAgent: Neural-Symbolic Self-Learning Agent Framework
- **Type:** Primary (ACM Web Conference 2025, arXiv 2502.03283)
- **Evidence Level:** Very High
- **URL:** https://arxiv.org/html/2502.03283v1
- **Key Finding:** Agent-Planner extracts symbolic rules from KG; Agent-Executor uses tools to traverse KG + external docs. 7B model outperforms GPT-4 on KG reasoning (+37% Hits@1). KG as dynamic environment, not static repository.
- **Relevance:** Validates T3 (neuro-symbolic approach). Shows structured knowledge + weak LLM > unstructured + strong LLM. Critical evidence for our thesis.

### S04 — Context Engineering for Coding Agents (Martin Fowler / Thoughtworks)
- **Type:** Secondary (expert practitioner)
- **Evidence Level:** High
- **URL:** https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html
- **Key Finding:** Context = system instructions + knowledge + tools, not just prompts. Three loading patterns: LLM-driven, human-triggered, agent-deterministic. "Start minimal" — models are powerful enough that less context often works better.
- **Relevance:** Validates JIT principle. Warns against over-loading context. Convergent with our minimum viable context thesis.

### S05 — Google ADK: Context-Aware Multi-Agent Framework
- **Type:** Primary (Google Developers Blog, production framework)
- **Evidence Level:** Very High
- **URL:** https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/
- **Key Finding:** "Every model call and sub-agent sees the minimum context required." Three layers: Working Context (ephemeral), Session (durable log), Memory (long-term). Artifacts as handles (reference, not inline). Compaction via LLM summarization.
- **Relevance:** Google independently arrived at minimum viable context as architectural principle. Strong validation of T3. Adoptable patterns.

### S06 — Augment Code Context Engine
- **Type:** Secondary (commercial product, marketing + benchmarks)
- **Evidence Level:** Medium-High (benchmark claims, but commercial source)
- **URL:** https://www.augmentcode.com/context-engine
- **Key Finding:** Real-time knowledge graph over 1M+ files. Semantic indexing (not grep). Contextual compression: 4,456 sources → 682 relevant. Understands active vs deprecated code, commit history. +18.2 points on code reuse vs competitors.
- **Relevance:** Most advanced commercial competitor in knowledge infrastructure. Uses KG, not just RAG. BUT: no schema contracts, no domain-specific validation, no pluggable domains. Code-only.

### S07 — Handbook on Neurosymbolic AI and Knowledge Graphs (IOS Press)
- **Type:** Primary (academic handbook, 2024)
- **Evidence Level:** Very High
- **URL:** https://ebooks.iospress.nl/volume/handbook-on-neurosymbolic-ai-and-knowledge-graphs
- **Key Finding:** KG-enhanced LLMs reduce hallucinations and enable complex reasoning. LLM-augmented KGs facilitate construction and querying. Sharp rise in publications 2023-2024. Neurosymbolic AI positioned as essential complement for LLM reliability.
- **Relevance:** Establishes academic consensus that neurosymbolic is the path to reliable AI. Validates T1 + T3.

### S08 — Neuro-Symbolic Agent Architectures (Emergent Mind Survey)
- **Type:** Secondary (curated survey)
- **Evidence Level:** High
- **URL:** https://www.emergentmind.com/topics/neuro-symbolic-agent-architectures
- **Key Finding:** Three coupling patterns: Loose (ensemble), Serial (pipeline), Tight (differentiable). For coding agents: Serial Hybrid most applicable (neural perception → symbolic validation). Excels at sample efficiency, interpretability, auditability.
- **Relevance:** Provides taxonomy for our approach. RaiSE cartridges = Serial Coupling (symbolic schema → neural reasoning → symbolic validation at build).

### S09 — RAG vs Knowledge Graph: Hallucination Reduction (Multiple surveys)
- **Type:** Primary (multiple arXiv surveys, 2024-2025)
- **Evidence Level:** High
- **URLs:**
  - https://arxiv.org/html/2510.24476v1
  - https://arxiv.org/html/2506.00054v1
  - https://arxiv.org/html/2509.03626v1
- **Key Finding:** RAG alone reduces hallucination ~60%. Hybrid KG+RAG (GraphRAG) reduces additional ~18% in biomedical QA. Production systems now maintain multiple representations: vector embeddings + knowledge graphs + hierarchical indexes.
- **Relevance:** Validates that KG > pure RAG for reliability. Our approach (structured KG with schemas) is aligned with SOTA direction. But we go further with contracts.

### S10 — Agentic Context Engineering (ACE, OpenReview/arXiv 2510.04618)
- **Type:** Primary (peer-reviewed)
- **Evidence Level:** High
- **URL:** https://arxiv.org/abs/2510.04618
- **Key Finding:** Contexts as "evolving playbooks" — structured, itemized bullets, not monolithic prompts. Modular process: generation, reflection, curation. Self-improving context over time.
- **Relevance:** Validates structured context delivery. Our cartridges could be seen as domain-specific "playbooks" with formal contracts. Complementary, not competing.

### S11 — Infrastructure for AI Agents (Chan et al., arXiv 2501.10114)
- **Type:** Primary (arXiv, comprehensive survey)
- **Evidence Level:** High
- **URL:** https://arxiv.org/pdf/2501.10114
- **Key Finding:** Agent infrastructure = technical systems external to agents mediating their interactions with environments. Agents differ from foundation models: they interact with the world, not just users. Taxonomy of infrastructure layers.
- **Relevance:** Frames our work correctly — we're building agent infrastructure, not agent capability.

### S12 — Nova Spivack: Epistemology and Metacognition in AI
- **Type:** Secondary (expert thought leadership)
- **Evidence Level:** Medium
- **URL:** https://www.novaspivack.com/technology/ai-technology/epistemology-and-metacognition-in-artificial-intelligence-defining-classifying-and-governing-the-limits-of-ai-knowledge
- **Key Finding:** Framework for classifying and governing AI knowledge limits. Epistemic transparency, delegative trust, normative reflexivity as conditions for justified belief in AI systems.
- **Relevance:** Provides epistemological vocabulary for our approach. Cartridge contracts = epistemic transparency.

### S13 — EpisTwin: Neuro-Symbolic Epistemic Verification
- **Type:** Primary (referenced in search results)
- **Evidence Level:** High
- **Key Finding:** Neuro-symbolic architecture with Epistemic Verification Module integrating GraphRAG for topology-aware retrieval. Verification layer between knowledge source and consumer.
- **Relevance:** Closest academic analog to our validation-at-boundary principle (P1). Different domain but same pattern.

### S14 — NeSyC: Neuro-Symbolic Continual Learning Agent
- **Type:** Primary (referenced in survey)
- **Evidence Level:** High
- **Key Finding:** Combines LLM-based hypothesis induction with symbolic validation and continual trajectory monitoring. Updates action rules online via hypothetico-deductive reasoning.
- **Relevance:** Shows symbolic validation as online process (not just build-time). Could inform future evolution of our build-time validation to runtime.

### S15 — Data Quality in AI Agents (Galileo, UiPath, industry)
- **Type:** Secondary (industry best practices)
- **Evidence Level:** Medium
- **URLs:**
  - https://galileo.ai/blog/data-quality-in-ai-agents
  - https://www.uipath.com/blog/ai/agent-builder-best-practices
- **Key Finding:** "Data pipeline failures are one of the most prevalent causes of AI agents operating incorrectly in production." Tools should have tight input/output contracts. Governed knowledge index with freshness SLAs reduces hallucinations.
- **Relevance:** Industry consensus that data quality bounds agent reliability. Validates T1 + T2 from practitioner perspective.

### S16 — Context File Fragmentation Problem (Multiple comparisons)
- **Type:** Secondary (developer experience reports)
- **Evidence Level:** Medium
- **URLs:**
  - https://dev.to/pockit_tools/cursor-vs-windsurf-vs-claude-code-in-2026-the-honest-comparison-after-using-all-three-3gof
  - https://zoer.ai/posts/zoer/cursor-windsurf-github-copilot-comparison
- **Key Finding:** Each tool reads different context files (.cursorrules, CLAUDE.md, copilot-instructions.md) but the information is the same. Sync across tools is painful. No tool validates context against codebase state. Context staleness is universal complaint.
- **Relevance:** Directly identifies the problem our schema-validated cartridges solve. Current tools = unvalidated markdown. Our approach = contracts with build-time validation.

### S17 — Windsurf/Cascade "Flow" Paradigm
- **Type:** Secondary (product comparison)
- **Evidence Level:** Medium
- **URL:** https://windsurf.com/compare/windsurf-vs-cursor
- **Key Finding:** Tracks edits, commands, clipboard, terminal output to infer intent. Session-persistent context. Architectural analysis over line-by-line completion.
- **Relevance:** Implicit context gathering (behavioral) vs our explicit structured context (declarative). Different approaches, potentially complementary.

### S18 — QCon London 2026: Context Engineering as Knowledge Engine
- **Type:** Secondary (conference talk announcement)
- **Evidence Level:** Medium
- **URL:** https://qconlondon.com/presentation/mar2026/context-engineering-building-knowledge-engine-ai-agents-need
- **Key Finding:** "Context Engineering: Building the Knowledge Engine AI Agents Need" — dedicated conference track. Industry recognition of context as infrastructure problem.
- **Relevance:** Confirms market timing — this is the moment for this approach.

### S19 — Context Engineering Complete Guide (CodeConductor)
- **Type:** Tertiary (industry guide)
- **Evidence Level:** Medium
- **URL:** https://codeconductor.ai/blog/context-engineering
- **Key Finding:** Context engineering = structuring everything an LLM needs (prompts, memory, tools, data). Distinguished from prompt engineering. "By early 2026 widely recognized as core discipline."
- **Relevance:** Market context — our work is in a rising category.

### S20 — Augment Code: Semantic Coding for Any Agent
- **Type:** Secondary (press coverage)
- **Evidence Level:** Medium
- **URL:** https://siliconangle.com/2026/02/06/augment-code-makes-semantic-coding-capability-available-ai-agent/
- **Key Finding:** Augment making its semantic indexing available as API for other agents. MCP integration. Memories that persist across conversations.
- **Relevance:** Potential adoptable component — their code graph could be a provider in our cartridge system.

### S21 — Gartner Prediction: 40% Agent Adoption by Late 2026
- **Type:** Tertiary (analyst forecast)
- **Evidence Level:** Medium
- **Key Finding:** "40% of enterprise applications will feature task-specific AI agents by late 2026, up from <5% in 2025."
- **Relevance:** Market timing validation.

### S22 — AllegroGraph: Neuro-Symbolic KG for Enterprise Intelligence
- **Type:** Secondary (vendor thought leadership)
- **Evidence Level:** Medium
- **URL:** https://allegrograph.com/why-agentic-ai-needs-neuro-symbolic-knowledge-graphs-for-enterprise-intelligence/
- **Key Finding:** Enterprise agents need neuro-symbolic KGs for grounded reasoning. Vector search alone is insufficient for complex enterprise knowledge.
- **Relevance:** Industry voice confirming neuro-symbolic direction for enterprise agents.

---

## Claim Validation Matrix

### Thesis 1: Agent reliability is bounded by knowledge source quality, not just LLM capability

| Evidence | Source | Level |
|----------|--------|-------|
| "Reliability gains lag behind capability progress" — formal metrics prove it | S02 | Very High |
| 7B model + structured KG outperforms GPT-4 on KG reasoning | S03 | Very High |
| Data pipeline failures = most prevalent cause of agent failure in production | S15 | Medium |
| Context staleness identified as primary failure mode in 283-session study | S01 | Very High |
| "Architecture-level optimization needed, not just better models" | S02 | Very High |

**Verdict: VALIDATED (Very High confidence, 5 independent sources)**

### Thesis 2: Requires dedicated infrastructure — contracts, validation, traceability

| Evidence | Source | Level |
|----------|--------|-------|
| Three-tier knowledge infrastructure proven at scale (108K lines, 70 days) | S01 | Very High |
| "Tools should have tight input/output contracts" — production best practice | S15 | Medium |
| "Governed knowledge index with freshness SLAs reduces hallucinations" | S15 | Medium |
| Hybrid KG+RAG > RAG alone for reliability (+18% in empirical study) | S09 | High |
| Context file fragmentation = unvalidated markdown across tools | S16 | Medium |
| Google ADK: three-layer architecture with explicit scoping | S05 | Very High |

**Verdict: VALIDATED (High confidence, 6 sources). BUT: no prior art combines contracts + validation + traceability into a unified framework. Closest is S01 (Codified Context) which uses tiered docs but NO schema contracts.**

### Thesis 3: Delivery should be neuro-symbolic and JIT — minimum viable context

| Evidence | Source | Level |
|----------|--------|-------|
| Google ADK: "Every model call sees minimum context required" | S05 | Very High |
| Fowler: "Start minimal — models powerful enough, less often works better" | S04 | High |
| SymAgent: symbolic planning + neural execution outperforms pure neural | S03 | Very High |
| Serial Hybrid Coupling most applicable for coding agents | S08 | High |
| Augment: contextual compression 4,456 → 682 sources | S06 | Medium-High |
| ACE: structured itemized context > monolithic prompts | S10 | High |

**Verdict: VALIDATED (Very High confidence, 6 sources). JIT/minimum viable context is emerging consensus. Neuro-symbolic coupling validated academically and commercially.**

---

## Prior Art Map

### Directly Competing / Adoptable

| System | What it does | What it lacks (vs our vision) |
|--------|-------------|-------------------------------|
| **Codified Context** (S01) | 3-tier docs for coding agents | No schema contracts, no validation, no pluggable domains, manual maintenance |
| **Augment Context Engine** (S06) | Semantic KG over codebase | Code-only (no work items, governance, domain knowledge), closed source, no contracts |
| **Google ADK** (S05) | Min-viable-context multi-agent framework | Generic (not domain-cartridge), no schema validation, no build-time composition |
| **CLAUDE.md / .cursorrules** (S16) | Static context files | No validation, no schema, staleness, fragmented per tool |

### Academically Relevant (Not Directly Competing)

| System | Relevance to RaiSE |
|--------|-------------------|
| **SymAgent** (S03) | Proves structured KG + weak LLM > unstructured + strong LLM |
| **EpisTwin** (S13) | Epistemic verification module — same pattern as our boundary validation |
| **NeSyC** (S14) | Online symbolic validation — future evolution path for build-time validation |
| **Agent Reliability Framework** (S02) | Formal metrics we could adopt for measuring cartridge impact |

### Market Context

| Player | Knowledge Approach | Gap |
|--------|-------------------|-----|
| **Cursor** | .cursorrules + codebase indexing | No structured knowledge, no validation, no domain awareness |
| **Copilot** | copilot-instructions.md + repo context | Weakest architectural reasoning, line-by-line focus |
| **Windsurf** | Behavioral tracking ("Flow") | Implicit context only, no declarative knowledge structure |
| **Devin** | Full agent with web/terminal access | Black box, no structured knowledge infrastructure |
| **Claude Code** | CLAUDE.md + skills + MCP | Most extensible, but no schema contracts or build-time validation |
| **Augment** | Semantic KG + memories | Most advanced KG, but code-only, closed, no domain cartridges |

---

*Next: Synthesis report with contribution map and problem formalization*
