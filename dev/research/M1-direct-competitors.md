# M1: Direct Competitors — Pluggable Domain Knowledge for AI Agents

**Research date:** 2026-03-24
**Researcher:** Rai (Claude Opus 4.6)
**Confidence level:** Medium-High (triangulated across 20+ searches, product pages, funding announcements)

---

## Executive Summary

No product on the market today offers exactly what Knowledge Cartridges propose: **self-contained, pluggable domain knowledge modules with typed ontology, corpus sources, domain adapters, validation gates, and HITL curation, using symbolic graph retrieval**. The market is converging from two directions:

1. **Memory-layer platforms** (Mem0, Zep, Letta, Cognee) — focus on agent memory/context persistence, increasingly adding knowledge graph capabilities
2. **Knowledge graph platforms** (Diffbot, Graphlit, metaphacts, WhyHow) — focus on graph construction and retrieval, increasingly targeting AI agent use cases

The gap we occupy is the **intersection**: modular, curated, domain-typed knowledge that plugs into agents as a discrete unit. Most competitors either build general-purpose memory or require bespoke graph construction per deployment.

---

## Competitor Profiles

### 1. Mem0
- **Founded:** 2023 (YC W24)
- **Funding:** $24M Series A (Oct 2025) — led by Basis Set Ventures, Peak XV, GitHub Fund, YC
- **Product:** Universal memory layer for AI apps. Compresses chat history into optimized memory representations. SDK-first (3 lines of code).
- **Domain Knowledge Approach:** **Not pluggable/modular.** Memory is learned from user interactions, not pre-loaded domain knowledge. Pro tier adds a knowledge graph linking entities across conversations, but it's conversation-derived, not domain-curated.
- **Target Market:** Horizontal — any AI app needing personalization/memory. Integrates with CrewAI, LangGraph, Flowise.
- **Pricing:** Free (10K memories/1K retrievals/mo) → $19/mo Standard → $249/mo Pro. Usage-based custom.
- **Traction:** 41K+ GitHub stars, 13M+ PyPI downloads, 186M API calls/quarter (Q3 2025). AWS exclusive memory provider for Agent SDK.
- **Overlap with Knowledge Cartridges:** Both provide persistent knowledge to agents beyond single sessions.
- **Our Differentiation:** We provide *curated domain ontology* with validation gates and HITL workflow. Mem0 learns from conversation — it doesn't ship pre-built domain expertise. No typed schema, no corpus provenance, no validation gates.

### 2. Zep (Graphiti)
- **Founded:** 2023 (Oakland, CA)
- **Funding:** $500K Seed (Apr 2024) — early stage
- **Product:** Context engineering platform. Core engine is Graphiti — open-source temporal knowledge graph. Entities have validity windows (when facts became true/superseded). Hybrid retrieval: semantic + BM25 + graph traversal, no LLM calls at retrieval time.
- **Domain Knowledge Approach:** **Partially configurable.** Supports custom entity types and relationship models (e.g., define "Lead" with company_size, budget_range). Upcoming: enhanced custom schema support. But schemas are per-deployment, not distributable modules.
- **Target Market:** Developers building agents with memory. Voice/video agents (low-latency focus). Enterprise (SOC2 Type II, HIPAA).
- **Pricing:** Freemium. Self-hosted open-source (Graphiti). Managed cloud from $14/mo. Enterprise custom.
- **Traction:** Published research paper (arXiv:2501.13956). DMR benchmark: 94.8% (vs MemGPT 93.4%). P95 latency 300ms. Integrated with FalkorDB for sub-ms multi-hop queries.
- **Overlap with Knowledge Cartridges:** Temporal knowledge graphs with custom schemas are architecturally closest to our approach. Graph-based retrieval (not vector-only).
- **Our Differentiation:** Zep's schemas are defined per deployment, not packaged as distributable cartridges. No HITL curation workflow. No corpus source management. No validation gates. Temporal focus (facts over time) vs. our ontological focus (domain structure).

### 3. Letta (formerly MemGPT)
- **Founded:** 2024 (Berkeley, CA — UCB Sky Computing Lab spinout)
- **Funding:** $10M Seed (Sep 2024) — led by Felicis. $70M post-money valuation. Angels: Jeff Dean, Clem Delangue.
- **Product:** Platform for stateful agents. LLM-as-Operating-System paradigm — model manages its own memory (core blocks + archival). Memory is first-class, explicit, self-editing.
- **Domain Knowledge Approach:** **Not pluggable in our sense.** Core memory blocks (persona, goals, preferences) are always in prompt. Archival memory retrieved via search. Memory stored in normalized tables (facts, entities, events, preferences, policies). Domain knowledge must be loaded per-agent, not as a distributable module.
- **Target Market:** Developers building stateful agents. Enterprise (self-hostable, data sovereignty). #1 on Terminal-Bench (model-agnostic coding).
- **Pricing:** Open-source self-hosted. Cloud platform (pricing not public).
- **Traction:** 41K+ GitHub stars (letta repo). Letta Code #1 on Terminal-Bench. Active community.
- **Overlap with Knowledge Cartridges:** Both treat knowledge/memory as structured, typed, first-class. Both use explicit schemas (not just vector blobs).
- **Our Differentiation:** Letta's memory is agent-centric (self-editing, learned). Cartridges are domain-centric (curated, distributable, versioned). No HITL curation workflow. No corpus provenance. No validation gates. No concept of a "cartridge" that multiple agents can load.

### 4. Cognee
- **Founded:** 2023
- **Funding:** $7.5M Seed — led by Pebblebed, backed by OpenAI and Facebook AI Research founders.
- **Product:** Open-source knowledge engine / AI memory. Six-stage pipeline: classify → permissions → chunk → extract entities/relationships → summarize → embed+graph. Configurable ontology mapper. 29+ database backends.
- **Domain Knowledge Approach:** **Closest to pluggable ontology.** Has an explicit "ontology mapper" in architecture. Custom data models. Learns from feedback. But ontologies are configured per-deployment, not packaged as distributable modules.
- **Target Market:** Enterprises building vertical AI agents. Regulated sectors (Tier 1 US bank, Bayer, University of Wyoming).
- **Pricing:** Cloud managed + self-hosted. Pricing not public.
- **Traction:** 1M+ pipeline runs/month. 70+ companies in production. Bayer, University of Wyoming, dltHub integrations. GitHub Secure Open Source program graduate.
- **Overlap with Knowledge Cartridges:** Ontology mapper + knowledge graph + configurable schema = architecturally similar foundation. Both use graph retrieval, not just vector.
- **Our Differentiation:** Cognee ontologies are configured in-place, not distributed as self-contained modules. No HITL curation workflow for ontology quality. No concept of "cartridge" packaging with corpus + schema + adapter + validation. We separate domain knowledge from the memory engine.

### 5. Interloom
- **Founded:** 2024 (Munich, Germany — Fabian Jakobi, ex-Boxplot/Hyperscience)
- **Funding:** $16.5M Seed (Mar 2026) — led by DN Capital, Bek Ventures, Air Street Capital. Previous $3M seed (Mar 2024).
- **Product:** Enterprise operations platform that captures tacit knowledge and transforms it into permanent memory for AI agents. Builds a "context graph" from operational records (emails, tickets, transcripts, work orders).
- **Domain Knowledge Approach:** **Automated extraction, not pluggable.** Ingests millions of records to learn how problems actually get resolved. Like Google Maps for operational knowledge. Domain-specific by nature (each org's graph is unique).
- **Target Market:** Large European enterprises. Operations/support. Commerzbank, Volkswagen, Zurich Insurance.
- **Pricing:** Enterprise sales (not public).
- **Traction:** Won Zurich Insurance AI competition (vs. 2,000 startups). Commerzbank: reduced documented-vs-actual knowledge gap from 50% to 5%.
- **Overlap with Knowledge Cartridges:** Both aim to make domain knowledge available to agents. Both use graph structures.
- **Our Differentiation:** Interloom extracts tacit knowledge from historical records — it's backward-looking and org-specific. Cartridges are forward-designed, curated domain ontologies that can be shared across organizations. We provide validation gates and HITL curation. They provide automated mining.

### 6. Diffbot
- **Founded:** 2012 (Mountain View, CA)
- **Funding:** $12.5M total (Series A $10M in 2016). Investors: Felicis, Tencent, Bloomberg Beta.
- **Product:** World's largest public web knowledge graph — 10B+ entities, 1T+ structured facts. GraphRAG LLM (fine-tuned Llama 3.3). Web data extraction APIs.
- **Domain Knowledge Approach:** **Massive pre-built graph, not pluggable/modular.** One monolithic knowledge graph of the public web. Users query it, not extend it with custom domains. 50B new facts/month added automatically.
- **Target Market:** Enterprise data consumers (Cisco, DuckDuckGo, Snapchat). Lead gen, recruitment, eCommerce.
- **Pricing:** Free tier → paid plans with extraction credits → Enterprise custom.
- **Traction:** 81% on FreshQA (beats ChatGPT, Gemini). Used by major tech companies.
- **Overlap with Knowledge Cartridges:** Both use knowledge graphs for agent grounding. Both prioritize factual accuracy over vector similarity.
- **Our Differentiation:** Diffbot is a single massive public-web graph. No custom ontology. No domain modularity. No HITL curation. No pluggable architecture. Fundamentally different: they index the web, we package domain expertise.

### 7. Graphlit
- **Founded:** ~2023 (Kirk Marple, CEO)
- **Funding:** Not publicly disclosed (early stage).
- **Product:** "Context Layer for AI agents." Cloud-native platform for content ingestion, knowledge graph construction, and GraphRAG. API-first. Supports multi-modal (PDFs, audio, images, websites).
- **Domain Knowledge Approach:** **Per-deployment graph construction.** Builds knowledge graphs from unstructured data via LLMs. Hybrid storage (vector + graph + object). Real-time sync with Slack, GitHub, Jira. Not modular/distributable.
- **Target Market:** App developers building AI with contextual retrieval. Enterprise teams needing real-time data sync.
- **Pricing:** Free up to 1GB → $49/mo + usage → $999/mo Growth + usage.
- **Traction:** Active GitHub, developer guides, blog content. Positioning as "RAG-as-a-Service."
- **Overlap with Knowledge Cartridges:** Both build knowledge graphs for agent retrieval. Both support GraphRAG over traditional vector RAG.
- **Our Differentiation:** Graphlit builds graphs per-deployment from raw data. No curated ontology. No distributable modules. No HITL curation. No validation gates. They're a platform for graph construction; we're a format for domain knowledge distribution.

### 8. metaphacts (metis)
- **Founded:** 2014 (Heidelberg, Germany)
- **Funding:** Not publicly disclosed. Digital Science portfolio company.
- **Product:** metaphactory (knowledge graph platform) + metis (enterprise AI platform). Semantic knowledge modeling + AI agents grounded in ontology. Pre-built agents for semantic modeling, search, discovery. Agent Registry for custom agents.
- **Domain Knowledge Approach:** **Ontology-first, enterprise-configured.** Semantic model as "trust and context layer." Closest to formal ontology approach. But ontologies are built per-deployment with metaphactory, not distributed as modules.
- **Target Market:** Pharma, life sciences, engineering, manufacturing. Boehringer Ingelheim, museum/university collaborations.
- **Pricing:** Enterprise sales. 4-week free trial. Accelerator Package (platform + consulting).
- **Traction:** 10+ years in knowledge graph market. AWS Marketplace presence. Published in Semantic Web Journal.
- **Overlap with Knowledge Cartridges:** Both use formal ontologies to ground AI agents. Both emphasize explainability and trust. Closest philosophical alignment.
- **Our Differentiation:** metaphacts builds ontologies in-place for large enterprises. Not pluggable, not distributable as modules. Heavy enterprise platform vs. our lightweight cartridge format. No HITL curation workflow for cartridge creation. They're consultancy-heavy; we're developer-first.

### 9. Glean
- **Founded:** 2019 (Palo Alto, CA — Arvind Jain, ex-Google)
- **Funding:** $150M Series F (Jun 2025) at $7.2B valuation. Total funding ~$600M+. Investors: Sequoia, Kleiner Perkins, Lightspeed, General Catalyst.
- **Product:** Enterprise AI work assistant. Connects to 100+ workplace apps (Google Workspace, M365, Slack, Salesforce). Understands organizational knowledge. Glean Agents: horizontal agent environment.
- **Domain Knowledge Approach:** **Connector-based, not pluggable domain modules.** Integrates with existing enterprise data sources via connectors. Knowledge is organizational (not domain-typed). No ontology, no curated domain modules.
- **Target Market:** Enterprise (all verticals). 1,475 employees. $100M+ ARR.
- **Pricing:** Enterprise sales.
- **Traction:** $100M+ ARR. 100M+ agent actions/year. $7.2B valuation.
- **Overlap with Knowledge Cartridges:** Both provide knowledge to AI agents. Both emphasize retrieval quality.
- **Our Differentiation:** Completely different approach. Glean indexes existing enterprise data. No domain ontology, no curated knowledge, no pluggable modules. They're enterprise search + agents; we're domain knowledge packaging.

### 10. Hebbia
- **Founded:** 2020 (New York, NY — George Sivulka, Stanford PhD)
- **Funding:** $161M total. $130M Series B (Apr 2024) led by a16z. ~$700M valuation.
- **Product:** AI platform for knowledge work in finance, legal, consulting. Agent swarm architecture. "Infinite effective context window." Matrix UI (spreadsheet interface for multi-doc analysis).
- **Domain Knowledge Approach:** **Domain-specific by vertical, not pluggable.** Built for finance/legal. Domain knowledge is embedded in the product, not in distributable modules. Acquired FlashDocs for automated content generation.
- **Target Market:** Financial services (33% of top global asset managers), legal, consulting.
- **Pricing:** Enterprise sales.
- **Traction:** $13M ARR (Jun 2024, growing fast). 33% of top asset managers. Processed 1B+ pages. OpenAI partnership.
- **Overlap with Knowledge Cartridges:** Both target domain-specific knowledge for AI. Both care about accuracy and provenance.
- **Our Differentiation:** Hebbia is a vertical SaaS product, not a pluggable knowledge format. Their domain knowledge is embedded in the application, not distributable. No ontology, no cartridge concept. They build the whole agent; we build the knowledge module.

### 11. Mistral Forge
- **Founded:** 2023 (Paris, France — Mistral AI)
- **Funding:** Mistral AI has raised $1B+. Forge announced at NVIDIA GTC 2026.
- **Product:** Enterprise platform for training proprietary AI models on internal knowledge. Pre-training + post-training + reinforcement learning on org-specific data (docs, codebases, operational records).
- **Domain Knowledge Approach:** **Knowledge baked into model weights, not pluggable retrieval.** Trains models on proprietary knowledge rather than using retrieval. Fundamentally different paradigm: fine-tuning vs. retrieval.
- **Target Market:** Large enterprises, government, financial institutions. ASML, ESA, Ericsson.
- **Pricing:** Enterprise sales (not public).
- **Traction:** Early — announced Mar 2026. Partnerships with ASML, ESA, Ericsson, DSO Singapore.
- **Overlap with Knowledge Cartridges:** Both aim to make domain knowledge available to AI systems.
- **Our Differentiation:** Completely different approach. Forge embeds knowledge in model weights (expensive, slow, opaque). Cartridges provide knowledge at retrieval time (cheap, fast, transparent, auditable). We keep knowledge separate from the model. No HITL curation, no validation gates in Forge.

### 12. Tana
- **Founded:** 2020 (Palo Alto + Norway)
- **Funding:** $25M total ($14M Series A led by Tola Capital, Feb 2025). Angels: Lars Rasmussen (Google Maps), Arash Ferdowsi (Dropbox).
- **Product:** AI-native workspace with knowledge graph. "Supertag" system transforms unstructured to structured info. Processes voice memos, Zoom calls into actionable items.
- **Domain Knowledge Approach:** **User-built knowledge graph, not pluggable domain modules.** Users build their own knowledge graph through note-taking and tagging. Supertags create typed structure. But it's personal/team knowledge, not distributable domain expertise.
- **Target Market:** Knowledge workers, teams. 160K+ waitlist (80% of Fortune 500 represented).
- **Pricing:** Not public (beta/waitlist stage).
- **Traction:** 160K+ waitlist. Strong angel backing.
- **Overlap with Knowledge Cartridges:** Both use typed/structured knowledge (Supertags ≈ ontology types). Both combine graph structure with AI.
- **Our Differentiation:** Tana is a workspace product for humans. Cartridges are a knowledge format for agents. Different use case entirely. No validation gates, no domain adapters, no corpus management.

---

## Competitive Matrix

| Capability | Knowledge Cartridges | Mem0 | Zep/Graphiti | Letta | Cognee | Interloom | Diffbot | Graphlit | metaphacts | Glean | Hebbia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Typed ontology/schema** | Yes (core) | No | Partial | Partial | Yes | No | Fixed | No | Yes | No | No |
| **Pluggable/distributable** | Yes (core) | No | No | No | No | No | No | No | No | No | No |
| **Corpus source management** | Yes | No | No | No | Partial | Partial | Auto-web | Yes | No | Connectors | Yes |
| **Domain adapter (query interp.)** | Yes | No | No | No | No | No | No | No | Partial | No | Partial |
| **Validation gates** | Yes | No | No | No | No | No | No | No | No | No | Partial |
| **HITL curation workflow** | Yes | No | No | No | No | No | No | No | Partial | No | No |
| **Symbolic graph retrieval** | Yes | No | Yes | No | Yes | Yes | Yes | Yes | Yes | No | No |
| **Temporal knowledge** | Partial | No | Yes (core) | No | No | Yes | Yes | No | No | No | No |
| **Multi-agent support** | Yes | Yes | Yes | Yes | Yes | No | No | Yes | Yes | Yes | Yes |
| **Open source** | TBD | Yes | Yes (Graphiti) | Yes | Yes | No | No | Partial | No | No | No |
| **Enterprise compliance** | TBD | SOC2/HIPAA | SOC2/HIPAA | Self-host | TBD | Enterprise | Enterprise | TBD | Enterprise | Enterprise | Enterprise |

---

## Key Findings

### 1. No One Is Building "Knowledge Cartridges"
The term and concept of self-contained, distributable, pluggable domain knowledge modules does not exist in the market. Every competitor either:
- Builds knowledge per-deployment from raw data (Cognee, Graphlit, Interloom)
- Learns knowledge from agent interactions (Mem0, Letta)
- Provides a fixed, monolithic knowledge base (Diffbot)
- Embeds knowledge in model weights (Mistral Forge)

**This is our whitespace.**

### 2. The Market Is Converging on Graph-Based Retrieval
Vector-only RAG is increasingly seen as insufficient. Zep, Cognee, Graphlit, metaphacts, and even Mem0 (Pro tier) are adding knowledge graph capabilities. Our use of symbolic graph retrieval aligns with where the market is heading.

### 3. Ontology Is Under-Served
Only Cognee (ontology mapper), metaphacts (semantic models), and Zep (custom entity types) offer any form of typed ontology. None of them package ontologies as distributable units. The ontology-as-module concept is novel.

### 4. HITL Curation Is Nearly Absent
Almost no competitor offers a structured HITL curation workflow for knowledge quality. metaphacts has partial support through their knowledge engineering tools. This is a significant differentiator for regulated industries and high-stakes domains.

### 5. Validation Gates Are Unique
No competitor implements validation gates on domain knowledge. This maps to our "Governance as Code" principle and is unique in the market.

### 6. Closest Competitors by Architecture
- **Cognee** — most similar foundation (ontology mapper + graph + configurable schema)
- **Zep/Graphiti** — most similar retrieval approach (temporal graph, custom schemas, symbolic retrieval)
- **metaphacts/metis** — most similar philosophy (ontology-first, explainable AI)

### 7. Funding Landscape
The AI agent memory/knowledge space is well-funded:
- Glean: $7.2B valuation, $600M+ raised
- Hebbia: $700M valuation, $161M raised
- Mistral: $1B+ raised (Forge is one product)
- Mem0: $24M raised
- Interloom: $19.5M raised
- Tana: $25M raised
- Letta: $10M raised
- Cognee: $7.5M raised

### 8. Potential Positioning
Knowledge Cartridges could position as **"the npm for domain knowledge"** — a packaging and distribution format that any agent framework (Letta, LangGraph, CrewAI) can consume. This would make us complementary to memory layers (Mem0, Zep) rather than competitive.

### 9. Risks
- **Cognee** could add cartridge-like packaging to their ontology mapper
- **Zep** could extend custom schemas into distributable modules
- **Large platforms** (AWS, Google, Microsoft) could add knowledge module support to their agent SDKs
- The market might converge on "fine-tuning + RAG" (Mistral Forge approach) rather than "pluggable knowledge modules"

---

## Sources

- [Mem0 Series A announcement](https://techcrunch.com/2025/10/28/mem0-raises-24m-from-yc-peak-xv-and-basis-set-to-build-the-memory-layer-for-ai-apps/)
- [Zep/Graphiti research paper](https://arxiv.org/abs/2501.13956)
- [Letta (MemGPT) stealth launch](https://techcrunch.com/2024/09/23/letta-one-of-uc-berkeleys-most-anticipated-ai-startups-has-just-come-out-of-stealth/)
- [Cognee $7.5M seed](https://www.cognee.ai/blog/cognee-news/cognee-raises-seven-million-five-hundred-thousand-dollars-seed)
- [Interloom $16.5M seed](https://fortune.com/2026/03/23/interloom-ai-agents-raises-16-million-venture-funding/)
- [Diffbot knowledge graph](https://venturebeat.com/ai/diffbots-ai-model-doesnt-guess-it-knows-thanks-to-a-trillion-fact-knowledge-graph)
- [Glean Series F](https://www.glean.com/blog/glean-series-f-announcement)
- [Hebbia Series B](https://venturebeat.com/ai/hebbia-nets-130m-to-build-the-go-to-ai-platform-for-knowledge-retrieval)
- [Mistral Forge launch](https://techcrunch.com/2026/03/17/mistral-forge-nvidia-gtc-build-your-own-ai-enterprise/)
- [Tana $25M](https://techcrunch.com/2025/02/03/tana-snaps-up-25m-with-its-ai-powered-knowledge-graph-for-work-racking-up-a-160k-waitlist/)
- [metaphacts metis launch](https://metaphacts.com/introducing-metis)
- [Graphlit platform](https://www.graphlit.com/)
- [WhyHow Knowledge Graph Studio](https://github.com/whyhow-ai/knowledge-graph-studio)
- [FalkorDB seed funding](https://tracxn.com/d/companies/falkordb/)
- [6 Agentic Knowledge Base Patterns](https://thenewstack.io/agentic-knowledge-base-patterns/)
- [Vertical AI agents landscape](https://www.geekwire.com/2026/the-rise-of-vertical-ai-agents-and-the-startups-racing-to-build-them/)
- [Mem0 pricing](https://mem0.ai/pricing)
- [Zep pricing](https://www.getzep.com/pricing/)
