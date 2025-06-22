# **Enhancing Code Ingestion Pipelines with Software Architecture Reconstruction for Hybrid Graph RAG Systems**

## **I. Introduction**

Software Architecture Reconstruction (SAR) is the process of extracting architectural elements and their relationships from existing software artifacts, primarily source code, to understand the system's high-level structure. As software systems evolve, their implemented architecture often deviates from the original design or documentation, a phenomenon known as architectural drift or erosion.1 Reconstructing the architecture becomes crucial for system comprehension, maintenance, evolution, and modernization.1

In the context of advanced code analysis systems, particularly those employing Retrieval-Augmented Generation (RAG) techniques on codebases, understanding the high-level architecture is paramount. A RAG system benefits significantly from context beyond individual code snippets. Knowledge of components, their interactions, deployed configurations, and architectural patterns allows the RAG system to provide more accurate, contextually relevant, and insightful responses to queries about the software. Specifically, for hybrid graph RAG approaches that leverage both structured (graph) and unstructured (text/code) data, having well-defined architectural information is essential for building the structured knowledge component.

This report provides a deep analysis of recent techniques (2023-2024) for performing SAR with the specific goal of generating "corpus quality" architectural documents suitable for informing a hybrid graph RAG system. It examines both deterministic and Large Language Model (LLM)-based SAR approaches, explores methods for transforming SAR outputs into structured knowledge representations like Knowledge Graphs (KGs), discusses the integration of this architectural knowledge into hybrid graph RAG frameworks, reviews relevant tools, compares the different SAR methodologies, and proposes strategies for complementing an existing code ingestion pipeline with SAR capabilities.

## **II. Recent Advances in Software Architecture Reconstruction**

The need for SAR persists as software complexity grows and architectures evolve.1 Maintaining an accurate understanding of a system's structure is vital for effective management and maintenance.3 Architectural drift, caused by modifications and design decisions over time, necessitates methods to recover the *as-implemented* architecture.1 Traditional SAR techniques often relied on manual analysis or basic static/dynamic analysis. However, recent advancements focus on improving accuracy, automation, and the types of information leveraged.

Modern approaches increasingly recognize that relying on a single information source is often insufficient. Techniques like SARIF explicitly aim to fuse multiple data types – such as code dependencies, textual information within the code, and repository structure – to achieve a more comprehensive and accurate reconstruction.3 Furthermore, specialized techniques are emerging for specific architectural styles, such as microservices, where understanding inter-service communication and deployment configurations is critical.4 The field is also exploring the potential of AI, particularly LLMs, to aid in understanding semantic aspects of architecture and generating documentation, although this is still an emerging area.5

## **III. Deterministic Software Architecture Reconstruction Techniques (2023-2024)**

Deterministic SAR methods rely on predefined rules, algorithms, and analyses applied to software artifacts to identify architectural elements and relationships. These approaches aim for reproducibility and precision based on the analyzed data. Recent work continues to refine these techniques.

A. Static Analysis:  
Static analysis examines code and related artifacts without executing the system. Recent tools leverage various static sources:

* **Deployment Descriptors:** Tools like Attack Graph Generator and MicroDepGraph parse Docker Compose files to extract components and initial dependencies in microservice systems.4 microMiner analyzes Kubernetes deployment files.4 This provides insights into the intended runtime structure.  
* **Source Code Analysis:** Techniques analyze source code directly to find dependencies, API calls, or specific framework annotations. SARIF incorporates code text analysis.3 MicroDepGraph can detect API calls in Java code.4 Prophet analyzes source code for endpoints and connections, also using folder structure clues.4 Code2DFD detects keywords in source code to build dataflow diagrams.4  
* **Bytecode/Compiled Code Analysis:** Tools like MicroGraal (though facing execution issues in one study) and RAD analyze compiled bytecode (e.g., Java bytecode) to identify endpoints and connections, often targeting specific frameworks like Spring.4 RAD-source offers a source-code alternative to RAD.4  
* **Repository History:** Some approaches analyze version control history (e.g., commit logs) to identify evolutionary coupling between modules, suggesting architectural relationships.2

B. Dynamic Analysis:  
Dynamic analysis observes the system during execution to capture runtime behavior and interactions.

* **Log Analysis:** Analyzing server access logs, application logs (potentially instrumented), or system event logs helps identify runtime dependencies and interaction patterns between components.2  
* **Runtime Monitoring:** Tools like Kieker, integrated with visualization platforms like ExplorViz, instrument applications to collect detailed runtime data (traces, metrics) that can be used to reconstruct dynamic architectural views and analyze performance.7 Other tools like Elastic APM and Dynatrace are also used.7 This is particularly relevant for understanding interactions in distributed systems like microservices.2

C. Hybrid and Multi-Source Approaches:  
Recognizing the limitations of single-source analysis, hybrid approaches combine static, dynamic, and potentially artifact-based information.

* **SARIF:** A prime example from 2023, SARIF fuses dependency information, code text semantics, and folder structure details. It adaptively weights these sources based on relevance and quality, demonstrating significantly higher accuracy (34.5% improvement over the best prior technique in its evaluation) in recovering ground-truth architectures.3  
* **Other Combinations:** Researchers combine static analysis of code with dynamic analysis of logs or runtime monitoring data to get a more complete picture.2 Artifact-driven analysis (using UML, requirements documents) can also be combined with code analysis.7

D. Focus on Microservices:  
Given the prevalence of microservices, specific SAR tools target this architectural style. A 2024 comparison highlighted tools analyzing Docker/Kubernetes files, Java/Spring annotations, and source/bytecode to map service dependencies and interactions.4 These tools often represent the architecture as graphs (topology, communication, context maps) or structured files (microTOSCA).4  
E. Evaluation:  
Deterministic approaches are typically evaluated by comparing the reconstructed architecture against a known ground truth (if available) using structural similarity metrics.3 For microservice reengineering, evaluation often involves metrics like coupling, cohesion, modularity, and runtime performance characteristics.7  
**Table 1: Selected Recent Deterministic SAR Techniques/Tools (2023-2024)**

| Technique/Tool | Key Information Sources | Primary Analysis Type | Output Representation | Focus Area | Reference(s) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| SARIF | Dependencies, Code Text, Folder Structure | Static (Fusion) | Architectural Components/Map | General | 3 |
| Kieker \+ ExplorViz | Runtime Traces, Metrics | Dynamic | Dynamic Views, Dashboards | Performance, Dynamic | 8 |
| Attack Graph Gen. | Docker Compose Files | Static | Topology Graph | Microservices | 4 |
| Code2DFD | Source Code Keywords, Docker Files | Static | Dataflow Diagrams (DFDs) | Microservices | 4 |
| MicroDepGraph (MDG) | Docker Compose, Java Source Code (API Calls) | Static | Topology Graph | Microservices | 4 |
| microMiner (MMI) | Kubernetes Deployment Files | Static | microTOSCA YAML File | Microservices | 4 |
| Prophet (PRO) | Source Code (Endpoints, Connections), Folder Structure | Static | Context Map | General (Java focus) | 4 |
| RAD / RAD-source | Java Bytecode / Source Code (Annotations, Endpoints) | Static | Architecture Graph | General (Java focus) | 4 |

Deterministic methods provide a foundation for structural reconstruction, offering precision and reproducibility for specific types of analysis. However, they may struggle to capture the semantic intent or implicit relationships within the architecture.

## **IV. LLM-based Approaches for Software Architecture Reconstruction (2023-2024)**

The advent of powerful Large Language Models (LLMs) trained on vast amounts of code and text has opened new possibilities for software engineering tasks, including aspects of SAR.9 While still an emerging area for full architectural reconstruction 5, LLMs are being explored for tasks that complement traditional SAR.

**A. Capabilities and Applications:**

* **Code Understanding and Summarization:** LLMs excel at processing natural language and code, enabling them to generate summaries of code functionality, explain complex code segments, and potentially identify the purpose of modules or components.9 This is directly relevant for generating descriptive documentation for architectural elements. Models like GPT-4, CodeLLaMA, and specialized code models (CodeT5+, DeepSeek-Coder) are often used.10  
* **Pattern Recognition:** Trained on massive codebases, LLMs can implicitly learn common coding patterns and potentially identify instances of architectural or design patterns within the code, although their reliability for complex patterns needs further validation.9  
* **Documentation Generation:** LLMs can automatically generate documentation snippets, comments, or even higher-level descriptions based on code, which can be invaluable for enriching architectural models.6 Some work explores generating formal specifications from natural language or code.16  
* **Architectural Component Generation (Early Stages):** Research is exploring the potential of LLMs to move beyond code snippets towards generating architectural components, for instance, in serverless contexts, though this is still nascent.17  
* **Requirements to Architecture:** GenAI, including LLMs, is being applied in the early stages of the SDLC, such as assisting in deriving architectural elements from requirements.5 Tools exist for deriving class diagrams from user stories.16

**B. Techniques:**

* **Prompt Engineering:** Crafting effective prompts is crucial for guiding LLMs to perform specific architectural analysis or generation tasks. Zero-shot and few-shot prompting are common.5 Techniques like Chain-of-Thought are also applied.16  
* **Retrieval-Augmented Generation (RAG):** To ground LLM responses and provide context, RAG is frequently used. Code snippets, existing documentation, or outputs from deterministic analyses can be retrieved and fed to the LLM as context for summarization or analysis.5  
* **Fine-tuning:** Adapting pre-trained LLMs to specific coding languages, domains, or architectural tasks by further training on relevant datasets can improve performance.15

C. Challenges and Limitations:  
Despite the potential, using LLMs for SAR faces significant hurdles:

* **Hallucinations and Accuracy:** LLMs can generate plausible but incorrect or nonsensical information (hallucinations).5 Their accuracy for complex architectural reasoning is not yet proven, and rigorous testing of outputs is often missing in studies.5  
* **Reliability and Consistency:** LLM outputs can be non-deterministic, making consistent architectural reconstruction challenging.18 Reliability is a major concern cited in recent reviews.5  
* **Evaluation Difficulties:** Assessing the quality and correctness of LLM-generated architectural insights or documentation is difficult. Standardized benchmarks and evaluation frameworks specific to architectural tasks are lacking.5  
* **Scalability and Cost:** Applying LLMs to analyze entire large-scale codebases can be computationally expensive and may hit context window limitations.12  
* **Interpretability:** The "black box" nature of LLMs makes it hard to understand *why* a particular architectural conclusion was reached, hindering trust and verification.5  
* **Contextual Understanding:** While LLMs understand local code patterns, grasping the global architecture and complex interdependencies of large systems remains a challenge.12 Function-level analysis, common in some LLM applications like vulnerability detection, may lack sufficient context for architectural decisions.20

A 2025 multivocal literature review on GenAI for software architecture found significant interest in using GenAI (predominantly GPT models with RAG) for architectural decision support and reconstruction, particularly for monolithic and microservice architectures. However, it strongly emphasized the challenges around precision, hallucinations, ethical concerns, privacy, the lack of architecture-specific datasets, and the need for sound evaluation frameworks.5 The application of LLMs in architecture is considered to be "in its infancy".5

LLMs currently offer more promise for *enriching* architectural models generated by other means (e.g., adding natural language descriptions) rather than performing reliable, end-to-end SAR independently.

## **V. Generating Corpus-Quality Architectural Documents via Knowledge Graphs**

To effectively inform a RAG system, the output of SAR needs to be transformed into a "corpus quality" representation. This implies data that is:

* **Structured:** Organized in a way that captures entities and relationships explicitly.  
* **Accurate:** Faithfully reflects the as-implemented architecture derived from SAR.  
* **Semantically Rich:** Includes not just structural links but also descriptions, types, properties, and potentially links to design rationale or requirements.  
* **Integrated:** Connects high-level architectural concepts (components, services, layers) to lower-level code artifacts (files, classes, functions).  
* **Queryable:** Easily accessible and traversable by the RAG system's retrieval mechanism.

Traditional SAR outputs like raw dependency graphs or component lists often lack the necessary structure and semantic richness. Knowledge Graphs (KGs) emerge as a highly suitable target representation for creating such a corpus.22

A. Knowledge Graphs for Codebases:  
A KG represents information as a network of nodes (entities) and edges (relationships), often with associated properties.23 Applied to a codebase, a KG can model:

* **Entities:** Software components, services, modules, classes, functions, files, deployment units, libraries, data stores, architectural patterns, requirements, vulnerabilities, etc..26  
* **Relationships:** Calls, inherits, implements, depends on, contains, deployed on, communicates with, related to (for requirements/docs), etc..26  
* **Properties:** Source code location, natural language descriptions/summaries, version history, metrics, security annotations, links to documentation.26

KGs provide a flexible schema that can evolve as understanding deepens.24 They allow linking diverse information sources – static analysis results, dynamic analysis data, code metadata, documentation, even LLM-generated summaries – into a unified, queryable structure.24 This explicit representation of relationships is key for navigating complex dependencies and understanding architectural context.26

B. Populating the Codebase KG:  
Transforming raw SAR outputs and other code information into a KG involves several steps:

1. **Ontology/Schema Definition:** Define the types of entities (nodes) and relationships (edges) relevant to the architectural understanding needed for RAG (e.g., Component, Service, Class, calls, dependsOn, hasDescription).23  
2. **Data Extraction:** Use SAR tools (deterministic) to extract structural facts (components, dependencies). Parse code for classes, functions, files. Extract metadata from build files or repositories.26  
3. **Transformation (ETL):** Convert extracted data into KG triples (Subject-Predicate-Object) or node/edge formats suitable for the chosen graph database (e.g., RDF, Property Graph).26 Deterministic mapping rules are suitable for structural data.  
4. **Semantic Enrichment (LLM/NLP):**  
   * Use NLP/LLMs to process comments, documentation, or even code itself to extract semantic information, generate summaries, or identify potential entity types/relationships.27  
   * LLMs can be used within automated ETL pipelines, potentially via structured function calling, to populate KG properties like descriptions.27  
   * **Crucially, LLM-generated additions should be validated or used primarily for descriptive properties rather than core structural relationships, given the reliability concerns.** A hybrid graph construction combining deterministic structure with LLM-generated semantic properties has shown promise.31  
5. **Loading:** Load the transformed data into a graph database (e.g., Neo4j, Stardog, FalkorDB).24

The resulting KG acts as the structured component of the corpus for the RAG system, linking high-level architectural views down to the specific code elements they represent.26

## **VI. Integrating Architectural Information into Hybrid Graph RAG**

A standard RAG system retrieves relevant text chunks (often based on vector similarity) and feeds them to an LLM to generate an answer. However, this can struggle with queries requiring understanding complex relationships or navigating structured information.32 Hybrid Graph RAG addresses this by combining structured knowledge retrieval from a KG with traditional vector-based retrieval.32

A. The Hybrid Architecture:  
The core idea is to leverage both the KG (populated with architectural and code information as described in Section V) and a vector store (containing embeddings of code chunks, documentation, etc.).

1. **Knowledge Graph Store:** Contains the structured representation of the architecture, code elements, and their relationships (e.g., Neo4j).26 Nodes in the KG should link to the corresponding code files/functions or documentation sections.  
2. **Vector Store:** Contains vector embeddings of relevant textual/code content (e.g., function bodies, class definitions, documentation paragraphs). These embeddings allow for semantic similarity searches.33 Vector stores like Chroma, FAISS, Pinecone, or even KG databases with vector capabilities (Neo4j) can be used.33  
3. **Retrieval Orchestrator:** Manages the query process, potentially using frameworks like LangChain.33  
4. **LLM Generator:** Synthesizes the final answer based on the retrieved context from both sources.

B. Retrieval Process:  
When a query arrives (e.g., "Explain the authentication flow for the user service" or "Which components handle payment processing?"):

1. **Query Analysis/Decomposition:** The query may be analyzed to determine if it requires structural/relational information (suited for KG) or semantic content retrieval (suited for vector search), or both. Complex queries might be decomposed into sub-queries.35  
2. **Parallel Retrieval:**  
   * **KG Retrieval:** The orchestrator queries the KG using graph query languages (e.g., Cypher for Neo4j, SPARQL for RDF graphs) to find relevant architectural entities (e.g., 'user service', 'authentication component', 'payment components') and traverse relationships (e.g., 'calls', 'contains').25 This retrieves structured information and pointers to relevant code/docs.  
   * **Vector Retrieval:** The query (or relevant terms extracted from it or the KG results) is embedded and used to search the vector store for semantically similar code chunks or documentation passages.33  
3. **Context Fusion/Ranking:** The results from both retrievers (KG subgraphs/paths/entities and text/code chunks) are collected. They might be ranked, filtered, or combined based on relevance scores or heuristics.33  
4. **Answer Generation:** The fused context is passed to the LLM, which generates a comprehensive answer grounded in both the structural architectural knowledge from the KG and the detailed content from the vector store.32

C. Benefits for Code/Architecture RAG:  
This hybrid approach offers significant advantages for querying codebases:

* **Contextual Understanding:** Leverages the KG to understand relationships between components, dependencies, and code elements, providing better context than isolated code chunks.32  
* **Accuracy and Reduced Hallucinations:** Grounding responses in the structured, verified facts within the KG can reduce LLM hallucinations and improve factual accuracy.31  
* **Complex Query Handling:** Enables answering questions that require navigating relationships (e.g., "What services are downstream from service X?" or "Show me the code implementing the core logic of component Y").33  
* **Efficiency:** KG queries can sometimes be more direct and efficient for finding specific structural information than broad vector searches.37

Integrating the SAR-derived architectural knowledge into a KG provides the necessary structured foundation for this powerful hybrid graph RAG approach, enabling deeper and more accurate querying of the codebase. Frameworks like HM-RAG propose multi-agent architectures to further refine this process, orchestrating decomposition and specialized retrieval agents.35

## **VII. Recent Tools and Frameworks (2023-2024)**

Implementing the described workflow requires integrating tools from different domains: SAR, LLM platforms, KG databases, and RAG orchestration frameworks. The tooling landscape is currently fragmented, with no single tool covering the entire process from SAR to hybrid graph RAG. However, convergence is occurring, with KG databases adding vector capabilities and RAG frameworks incorporating KG retrievers.

**A. Tool Categories:**

* **Deterministic SAR Tools:** Focus on extracting structure from code/artifacts. Examples include academic tools like SARIF 3, monitoring frameworks like Kieker 8, and specialized tools for microservices identified in recent comparisons 4 (e.g., MDG, Code2DFD). Commercial modeling or diagramming tools are also widely used for documentation, though often manually updated.38  
* **LLM Platforms/Models:** Provide the core AI capabilities for semantic analysis and generation. Key models include OpenAI's GPT series, Anthropic's Claude, Meta's LLaMA variants (including CodeLLaMA), Google's Gemini, and code-specific models like CodeT5+, DeepSeek-Coder.10 Platforms like Hugging Face provide access to many models.13  
* **Knowledge Graph Databases:** Store and query the structured architectural information. Leading options include Neo4j (Property Graph, Cypher query language) 25, Stardog (RDF/Property Graph, SPARQL/Cypher) 24, Ontotext GraphDB (RDF, SPARQL) 23, and FalkorDB (Property Graph, Cypher).30 These platforms often provide features for data integration, visualization, and sometimes inference.  
* **KG Construction/ETL Tools:** Tools and libraries aid in extracting information and transforming it into graph formats. This can range from custom scripts using libraries like Roslyn (.NET) 26 or standard NLP/parsing libraries, to more integrated platforms like Ontotext Platform 23 or specialized tools like Strazh (for C\#).26 LLMs themselves are being used within ETL pipelines for extraction.29  
* **Vector Databases:** Store embeddings for semantic search. Options include Chroma, FAISS, Pinecone, Weaviate, Milvus, and increasingly, vector index capabilities within KG databases like Neo4j.33  
* **RAG Orchestration Frameworks:** Libraries like LangChain 33 and LlamaIndex provide components and abstractions to build RAG pipelines, including hybrid retrieval strategies integrating vector stores and graph databases. Microsoft has also introduced GraphRAG as a framework concept.37 Conceptual frameworks like HM-RAG describe advanced multi-agent architectures.35

B. Tool Ecosystem Considerations:  
Building the desired system necessitates integrating tools across these categories. Key considerations for selection include:

* **Interoperability:** APIs, support for standard formats (e.g., JSON, GraphML for SAR output; RDF/SPARQL or Property Graph/Cypher for KGs), and compatibility with orchestration frameworks are crucial.  
* **Convergence:** Platforms that integrate multiple capabilities (e.g., KG \+ Vector Search) might simplify the architecture. Neo4j, for instance, offers both graph storage and vector indexing.33  
* **Scalability:** Ensure chosen tools can handle the size and complexity of the target codebase and the expected query load.  
* **Maturity and Support:** Balance cutting-edge research tools with mature, supported commercial or open-source options.

The following table summarizes some key tools and frameworks relevant to building an architecture-aware graph RAG system, based on recent literature.

**Table 2: Overview of Relevant Tools/Frameworks (2023-2024)**

| Tool/Framework Name | Category | Key Features Relevant to Arch/Code RAG | Maturity/Availability | Reference(s) |
| :---- | :---- | :---- | :---- | :---- |
| SARIF | Deterministic SAR | Fuses dependencies, code text, folder structure; high accuracy demo | Research Prototype | 3 |
| Kieker / ExplorViz | Deterministic SAR (Dyn.) | Runtime monitoring, dynamic view generation, performance analysis | OSS Framework/Tool | 8 |
| MDG, Code2DFD, etc. | Deterministic SAR (Static) | Microservice analysis (deployment files, code); graph/DFD output | Research Prototypes | 4 |
| GPT-4 / CodeLLaMA | LLM / Platform | Code understanding, summarization, generation; used in RAG | Commercial / OSS | 10 |
| LangChain | RAG Orchestration | Framework for building RAG pipelines, supports KGs & Vector DBs | OSS Framework | 33 |
| Neo4j | KG Database (+Vector) | Property Graph storage, Cypher query lang., Vector Index, Vis. | Commercial / OSS | 25 |
| Stardog | KG Database | RDF/Property Graph, SPARQL/Cypher, Virtualization, Inference | Commercial | 24 |
| Ontotext GraphDB | KG Database | RDF/RDF\* storage, SPARQL, Inference, Text Analytics Integration | Commercial / Free | 23 |
| FalkorDB | KG Database | Property Graph, Cypher, focus on performance, Code Graph features | OSS | 30 |
| RDF / SPARQL | KG Standard | W3C standards for graph data representation and querying | Standard | 23 |
| Cypher | KG Standard (de facto) | Declarative query language for Property Graphs (Neo4j, FalkorDB) | Standard (openCypher) | 25 |
| Microsoft GraphRAG | Hybrid RAG Pattern/Framework | Leverages KGs for RAG; framework concept | Vendor Initiative | 37 |
| HM-RAG | Hybrid RAG Pattern | Hierarchical Multi-agent Multimodal RAG framework concept | Research Concept | 35 |
| Strazh | KG Construction | ETL tool to build Codebase KG from C\# using Roslyn | OSS Tool | 26 |

Successfully implementing the target system requires navigating this ecosystem and carefully selecting and integrating tools that meet the specific technical requirements and constraints of the project.

## **VIII. Comparative Analysis: Deterministic vs. LLM-based SAR**

Choosing the right SAR approach, or combination of approaches, requires understanding the relative strengths and weaknesses of deterministic and LLM-based methods, particularly in the context of generating reliable architectural information for RAG.

**A. Strengths:**

* **Deterministic:** Offer high precision for extracting verifiable structural facts like dependencies, component containment, or specific code patterns when correctly configured for the target system.4 Results are generally reproducible and interpretable, as the analysis follows defined rules traceable back to the code or artifacts.1 They are often well-suited for identifying concrete architectural elements defined by specific syntax or structures (e.g., microservices defined in deployment files 4).  
* **LLM-based:** Show potential for understanding semantic nuances, intent, and ambiguity in code or documentation.9 They excel at generating fluent natural language summaries and descriptions, which are valuable for documentation.5 They might identify fuzzier patterns or architectural concepts not easily captured by rigid rules and can be used for rapid prototyping of analysis tasks.9

**B. Weaknesses:**

* **Deterministic:** Can struggle with semantic interpretation – understanding the *why* behind the structure. They may require significant effort to configure and adapt to specific programming languages, frameworks, or project conventions.1 Static analysis misses runtime behavior, while dynamic analysis may suffer from incomplete code coverage or runtime overhead.2 They might fail to capture implicit relationships or the architect's original intent if not explicitly represented.  
* **LLM-based:** Prone to generating incorrect or fabricated information (hallucinations), making their outputs unreliable for critical architectural facts.5 Their reasoning capabilities for complex, multi-step architectural inference are limited.12 The lack of interpretability makes it difficult to verify results or trust conclusions.5 Performance can degrade on out-of-distribution or highly complex code, and evaluating their true comprehension versus pattern matching is challenging.12 Scalability to very large codebases and inference costs are also concerns.12

**C. Accuracy, Reliability, Scalability, and Interpretability:**

* **Accuracy/Reliability:** Deterministic methods generally provide higher reliability for *structural* accuracy. LLM accuracy for architectural tasks is currently questionable and a major cited challenge; rigorous validation is often lacking.5  
* **Scalability:** Static analysis scalability varies; simple parsing can be efficient, but complex inter-procedural analysis can be costly. Dynamic analysis overhead depends on instrumentation level. LLM scalability depends on model size, context window limits, and inference infrastructure.  
* **Interpretability:** Deterministic results are typically traceable. LLM reasoning remains largely opaque.

D. The Case for Synergy:  
The strengths and weaknesses of deterministic and LLM-based approaches are highly complementary. Deterministic methods excel at extracting the reliable, factual structural backbone of the architecture. LLMs excel at generating semantic interpretations and natural language descriptions, albeit with reliability concerns.  
Neither approach alone provides a complete solution for generating high-quality, corpus-ready architectural documents that are both structurally accurate and semantically meaningful. Relying solely on deterministic methods yields structure without rich descriptions. Relying solely on LLMs risks introducing factual inaccuracies and lacks verifiable grounding.

Therefore, a synergistic approach is necessary. Use deterministic methods to establish the ground truth structural framework (components, dependencies). Represent this framework in a KG. Then, use LLMs, guided by RAG principles (retrieving relevant code/docs linked via the KG), to enrich this structure with semantic information like summaries and descriptions. This leverages the precision of deterministic methods and the fluency of LLMs while mitigating the latter's reliability issues by grounding them in retrieved facts. Deterministic checks could potentially also be used to validate LLM outputs. This combined approach, unified by a KG, offers the most promising path towards generating the comprehensive architectural intelligence needed for an effective graph RAG system.

## **IX. Strategies for Enhancing Your Code Ingestion Pipeline**

To integrate SAR and generate the architectural corpus for your hybrid graph RAG system, the existing code ingestion pipeline needs enhancement. This involves adding SAR modules, defining a workflow for processing code and generating the KG/vector corpus, and selecting appropriate tools.

**A. Integration Points:**

* **Post-Ingestion Processing:** The most straightforward approach is to add SAR steps that execute after the initial code fetching is complete.  
* **Parallelism:** Depending on the tools and resources, deterministic SAR, LLM analysis, and vector embedding could potentially run in parallel for different code sections or artifacts.  
* **Triggers:** SAR processes can be triggered on code commits (potentially integrated into CI/CD, mindful of performance impacts 4), scheduled runs, or on-demand analysis.

B. Proposed Enhancement Workflow:  
A robust workflow integrating deterministic and LLM approaches via a KG is recommended:

1. **Code Ingestion:** The existing pipeline fetches or updates the source code and relevant artifacts (e.g., build files, deployment descriptors).  
2. **Deterministic SAR Execution:** Execute selected deterministic SAR tool(s) (e.g., static analyzers for dependencies, structure, microservice configurations).  
   * *Input:* Source code, deployment files, etc.  
   * *Output:* Raw structural data (e.g., JSON, GraphML representing components, files, classes, dependencies).  
3. **KG Structural Population:** Transform the deterministic SAR output into the Knowledge Graph.  
   * *Process:* Map extracted elements (files, classes, components) to KG nodes and relationships (dependencies, containment) according to a predefined ontology. Store links back to source code locations.  
   * *Output:* A KG representing the architectural skeleton, stored in a graph database.  
4. **LLM Semantic Enrichment (RAG-based):** Augment the KG with descriptive information.  
   * *Process:* For key architectural nodes (e.g., components, services) in the KG:  
     * Retrieve associated code snippets using the source links stored in the KG.  
     * Use an LLM, prompted for summarization or description generation, with the retrieved code snippets as context (RAG).  
     * Add the generated summaries/descriptions as properties to the corresponding KG nodes. Validate outputs where possible.  
   * *Output:* Enriched KG with semantic descriptions.  
5. **Vector Embedding Generation:** Create embeddings for semantic search.  
   * *Process:* Generate vector embeddings for relevant code chunks (e.g., function bodies, class definitions identified via the KG) and potentially associated documentation.  
   * *Output:* Embeddings stored in a vector database, with links back to the corresponding KG nodes or source locations.  
6. **Corpus Ready:** The combination of the enriched Knowledge Graph and the linked Vector Database now constitutes the comprehensive, multi-modal corpus ready to be queried by the hybrid graph RAG system.

**C. Tool Selection Considerations:**

* **Language/Framework Fit:** Prioritize deterministic tools with strong support for the project's specific technologies.  
* **Output Interoperability:** Choose SAR tools outputting machine-readable formats (JSON, GraphML) suitable for automated KG transformation.  
* **KG & Vector DB Choice:** Select graph and vector databases based on scalability needs, query language preference (Cypher, SPARQL), integration capabilities (e.g., built-in vector index, LangChain compatibility), and operational considerations.  
* **LLM Selection:** Choose LLMs based on performance for code tasks, cost, availability, and ease of integration (APIs). Consider models specialized for code.12  
* **Orchestration:** Leverage frameworks like LangChain to simplify the integration of different components (SAR outputs, KG, Vector DB, LLM).

D. Phased Implementation Strategy:  
Given the complexity and the varying maturity of the involved technologies, a phased implementation is strongly recommended to manage risk and deliver value incrementally:

1. **Phase 1: Deterministic Foundation & KG:** Implement robust deterministic SAR to extract the core architectural structure. Populate a KG with this structural backbone. This provides immediate, verifiable insights into the architecture.  
2. **Phase 2: Vector Embeddings:** Generate and store vector embeddings for code and documentation, linking them to the KG. This enables basic semantic search capabilities.  
3. **Phase 3: LLM Semantic Enrichment:** Cautiously introduce LLM-based enrichment (via RAG) to add summaries and descriptions to the KG. Focus on validating the quality and accuracy of LLM outputs.  
4. **Phase 4: Hybrid RAG Querying:** Implement the full hybrid graph RAG query engine that leverages both the enriched KG and the vector store.

This phased approach builds upon a reliable foundation, allowing for iterative development and validation, and contains the risks associated with the less predictable LLM components until a solid structural base is established.

## **X. Conclusion and Future Directions**

A. Summary and Recommendations:  
This report has explored recent advancements in Software Architecture Reconstruction (SAR) aimed at generating high-level architectural knowledge suitable for enhancing Retrieval-Augmented Generation (RAG) systems operating on codebases. Key findings indicate that while traditional deterministic SAR methods continue to evolve, particularly through multi-source fusion (e.g., SARIF 3\) and specialization (e.g., for microservices 4), they primarily capture structural information. Large Language Models (LLMs) show significant promise for semantic understanding and documentation generation 5, but currently face substantial challenges regarding reliability, accuracy, and evaluation for core architectural reconstruction tasks.5  
Generating "corpus quality" architectural documents requires integrating both accurate structure and rich semantics. Knowledge Graphs (KGs) provide an effective mechanism to represent this integrated knowledge, linking high-level components to low-level code details.26 The optimal consumption pattern for this integrated knowledge within a RAG system is the hybrid graph RAG architecture, which combines structured KG traversal with semantic vector search.32

The most effective strategy involves a synergistic approach:

1. Employ **deterministic SAR** methods to build a reliable structural backbone of the architecture.  
2. Represent this structure and link it to code artifacts within a **Knowledge Graph**.  
3. Use **LLMs cautiously via RAG**, grounded in code retrieved via the KG, primarily for **semantic enrichment** (e.g., generating summaries) rather than core structural discovery.  
4. Implement a **hybrid graph RAG** system to query the combined KG and vector corpus.  
5. Adopt a **phased implementation** strategy to manage complexity and risk, starting with the deterministic foundation.  
6. Carefully **select and integrate tools** from the fragmented but converging SAR, LLM, KG, and RAG ecosystems.

B. Future Directions:  
Significant research and development are needed to fully realize the potential of AI-driven SAR for RAG systems:

* **Improved LLM Reliability and Evaluation:** Developing techniques to reduce LLM hallucinations, enhance complex reasoning for architectural tasks, and create robust, architecture-specific benchmarks and evaluation methodologies is critical.5  
* **Explainability and Trust:** Methods are needed to make LLM-derived architectural insights more transparent and verifiable.5  
* **Automated KG Construction and Maintenance:** Advancing techniques for automatically and reliably building, validating, and updating codebase KGs as the software evolves, potentially leveraging LLMs more effectively within structured pipelines.30  
* **Tighter Tool Integration:** The emergence of more unified platforms that seamlessly integrate SAR capabilities, KG management, vector search, and LLM orchestration would significantly simplify implementation.  
* **Advanced Graph RAG Strategies:** Exploring more sophisticated hybrid retrieval techniques, adaptive query planning, and multi-agent architectures (like HM-RAG 35) to optimize context retrieval from complex codebase KGs.  
* **Architecture-Specific Datasets:** Creating high-quality, curated datasets specifically designed for training and evaluating SAR models (both deterministic and LLM-based).5

By pursuing these directions, the field can move closer to providing automated, reliable, and deeply insightful architectural understanding, significantly enhancing the capabilities of next-generation code analysis and RAG systems.

#### **Works cited**

1. (PDF) Software Architecture Reconstruction: A Process-Oriented ..., accessed April 19, 2025, [https://www.researchgate.net/publication/44961315\_Software\_Architecture\_Reconstruction\_A\_Process-Oriented\_Taxonomy](https://www.researchgate.net/publication/44961315_Software_Architecture_Reconstruction_A_Process-Oriented_Taxonomy)  
2. Software improvement in the reconstruction of architectures (SIRA) \- ResearchGate, accessed April 19, 2025, [https://www.researchgate.net/figure/Software-improvement-in-the-reconstruction-of-architectures-SIRA\_fig8\_346220232](https://www.researchgate.net/figure/Software-improvement-in-the-reconstruction-of-architectures-SIRA_fig8_346220232)  
3. Software Architecture Recovery with Information Fusion (ESEC/FSE ..., accessed April 19, 2025, [https://2023.esec-fse.org/details/fse-2023-research-papers/44/Software-Architecture-Recovery-with-Information-Fusion](https://2023.esec-fse.org/details/fse-2023-research-papers/44/Software-Architecture-Recovery-with-Information-Fusion)  
4. arxiv.org, accessed April 19, 2025, [https://arxiv.org/pdf/2412.08352](https://arxiv.org/pdf/2412.08352)  
5. Generative AI for Software Architecture. Applications, Trends, Challenges, and Future Directions \- arXiv, accessed April 19, 2025, [https://arxiv.org/html/2503.13310v1](https://arxiv.org/html/2503.13310v1)  
6. Generative AI for Software Architecture. Applications, Trends, Challenges, and Future Directions \- arXiv, accessed April 19, 2025, [https://arxiv.org/pdf/2503.13310](https://arxiv.org/pdf/2503.13310)  
7. (PDF) Microservices-based Software Systems Reengineering: State ..., accessed April 19, 2025, [https://www.researchgate.net/publication/382445929\_Microservices-based\_Software\_Systems\_Reengineering\_State-of-the-Art\_and\_Future\_Directions](https://www.researchgate.net/publication/382445929_Microservices-based_Software_Systems_Reengineering_State-of-the-Art_and_Future_Directions)  
8. The Kieker Observability Framework Version 2 \- arXiv, accessed April 19, 2025, [https://arxiv.org/html/2503.09189v1](https://arxiv.org/html/2503.09189v1)  
9. Large Language Models (LLMs) for Source Code Analysis: applications, models and datasets \- arXiv, accessed April 19, 2025, [https://arxiv.org/html/2503.17502v1](https://arxiv.org/html/2503.17502v1)  
10. Large Language Models for Software Engineering: A Systematic Literature Review \- arXiv, accessed April 19, 2025, [https://arxiv.org/html/2308.10620v6](https://arxiv.org/html/2308.10620v6)  
11. Large Language Models for Code Analysis: Do LLMs Really Do Their Job? \- arXiv, accessed April 19, 2025, [https://arxiv.org/html/2310.12357v2](https://arxiv.org/html/2310.12357v2)  
12. The Code Barrier: What LLMs Actually Understand? \- arXiv, accessed April 19, 2025, [https://arxiv.org/html/2504.10557v1](https://arxiv.org/html/2504.10557v1)  
13. Towards an Understanding of Large Language Models in Software Engineering Tasks, accessed April 19, 2025, [https://arxiv.org/html/2308.11396v2](https://arxiv.org/html/2308.11396v2)  
14. From LLMs to LLM-based Agents for Software Engineering: A Survey of Current, Challenges and Future \- arXiv, accessed April 19, 2025, [https://arxiv.org/html/2408.02479v2](https://arxiv.org/html/2408.02479v2)  
15. A Survey On Large Language Models For Code Generation \- arXiv, accessed April 19, 2025, [https://arxiv.org/html/2503.01245v1](https://arxiv.org/html/2503.01245v1)  
16. iSEngLab/AwesomeLLM4SE: A Survey on Large Language Models for Software Engineering \- GitHub, accessed April 19, 2025, [https://github.com/iSEngLab/AwesomeLLM4SE](https://github.com/iSEngLab/AwesomeLLM4SE)  
17. LLMs for Generation of Architectural Components: An Exploratory Empirical Study in the Serverless World \- arXiv, accessed April 19, 2025, [https://arxiv.org/html/2502.02539v1](https://arxiv.org/html/2502.02539v1)  
18. saltudelft/ml4se: A curated list of papers, theses, datasets, and tools related to the application of Machine Learning for Software Engineering \- GitHub, accessed April 19, 2025, [https://github.com/saltudelft/ml4se](https://github.com/saltudelft/ml4se)  
19. (PDF) Generative AI for Software Architecture. Applications, Trends, Challenges, and Future Directions \- ResearchGate, accessed April 19, 2025, [https://www.researchgate.net/publication/389877715\_Generative\_AI\_for\_Software\_Architecture\_Applications\_Trends\_Challenges\_and\_Future\_Directions](https://www.researchgate.net/publication/389877715_Generative_AI_for_Software_Architecture_Applications_Trends_Challenges_and_Future_Directions)  
20. Top Score on the Wrong Exam: On Benchmarking in Machine Learning for Vulnerability Detection \- arXiv, accessed April 19, 2025, [https://arxiv.org/pdf/2408.12986](https://arxiv.org/pdf/2408.12986)  
21. \[2503.13310\] Generative AI for Software Architecture. Applications, Trends, Challenges, and Future Directions \- arXiv, accessed April 19, 2025, [https://arxiv.org/abs/2503.13310](https://arxiv.org/abs/2503.13310)  
22. Step-by-Step Guide to Building a Knowledge Graph in 2025 \- PageOn.ai, accessed April 19, 2025, [https://www.pageon.ai/blog/knowledge-graph](https://www.pageon.ai/blog/knowledge-graph)  
23. What Is a Knowledge Graph? | Ontotext Fundamentals, accessed April 19, 2025, [https://www.ontotext.com/knowledgehub/fundamentals/what-is-a-knowledge-graph/](https://www.ontotext.com/knowledgehub/fundamentals/what-is-a-knowledge-graph/)  
24. What is a Knowledge Graph | Stardog, accessed April 19, 2025, [https://www.stardog.com/knowledge-graph/](https://www.stardog.com/knowledge-graph/)  
25. Knowledge Graph \- Graph Database & Analytics \- Neo4j, accessed April 19, 2025, [https://neo4j.com/use-cases/knowledge-graph/](https://neo4j.com/use-cases/knowledge-graph/)  
26. Codebase Knowledge Graph: Code Analysis with Graphs \- Neo4j, accessed April 19, 2025, [https://neo4j.com/blog/developer/codebase-knowledge-graph/](https://neo4j.com/blog/developer/codebase-knowledge-graph/)  
27. Building a Knowledge Graph of Your Codebase \- Daytona.io, accessed April 19, 2025, [https://www.daytona.io/dotfiles/building-a-knowledge-graph-of-your-codebase](https://www.daytona.io/dotfiles/building-a-knowledge-graph-of-your-codebase)  
28. Use knowledge graphs to discover open source package vulnerabilities | Red Hat Developer, accessed April 19, 2025, [https://developers.redhat.com/blog/2021/05/10/use-knowledge-graphs-to-discover-open-source-package-vulnerabilities](https://developers.redhat.com/blog/2021/05/10/use-knowledge-graphs-to-discover-open-source-package-vulnerabilities)  
29. Building massive knowledge graphs using automated ETL pipelines \- metaphacts Blog, accessed April 19, 2025, [https://blog.metaphacts.com/building-massive-knowledge-graphs-using-automated-etl-pipelines](https://blog.metaphacts.com/building-massive-knowledge-graphs-using-automated-etl-pipelines)  
30. How to Use Knowledge Graph Tools to Enhance AI Development \- FalkorDB, accessed April 19, 2025, [https://www.falkordb.com/blog/how-to-use-knowledge-graph-tools-for-ai/](https://www.falkordb.com/blog/how-to-use-knowledge-graph-tools-for-ai/)  
31. Using Graphs to Improve the Interpretability of API Documentation for BIM Authoring Software. \- mediaTUM, accessed April 19, 2025, [https://mediatum.ub.tum.de/doc/1769403/d2hslvcoe54id06i0tp71yh22.2025-Wrabel-Du.pdf](https://mediatum.ub.tum.de/doc/1769403/d2hslvcoe54id06i0tp71yh22.2025-Wrabel-Du.pdf)  
32. GraphRAG: Leveraging Graph-Based Efficiency to Minimize Hallucinations in LLM-Driven RAG for Finance Data \- ACL Anthology, accessed April 19, 2025, [https://aclanthology.org/2025.genaik-1.6.pdf](https://aclanthology.org/2025.genaik-1.6.pdf)  
33. RAG Using Knowledge Graph: Mastering Advanced Techniques \- Part 2 \- ProCogia, accessed April 19, 2025, [https://procogia.com/rag-using-knowledge-graph-mastering-advanced-techniques-part-2/](https://procogia.com/rag-using-knowledge-graph-mastering-advanced-techniques-part-2/)  
34. How to Build a JIT Hybrid Graph RAG with Code Tutorial, accessed April 19, 2025, [https://ragaboutit.com/how-to-build-a-jit-hybrid-graph-rag-with-code-tutorial/](https://ragaboutit.com/how-to-build-a-jit-hybrid-graph-rag-with-code-tutorial/)  
35. HM-RAG: Hierarchical Multi-Agent Multimodal Retrieval Augmented Generation \- arXiv, accessed April 19, 2025, [https://arxiv.org/html/2504.12330v1](https://arxiv.org/html/2504.12330v1)  
36. HM-RAG: Hierarchical Multi-Agent Multimodal Retrieval Augmented Generation \- arXiv, accessed April 19, 2025, [https://arxiv.org/pdf/2504.12330](https://arxiv.org/pdf/2504.12330)  
37. Graph RAG \- News from generation RAG, accessed April 19, 2025, [https://ragaboutit.com/category/graph-rag/](https://ragaboutit.com/category/graph-rag/)  
38. State of Software Architecture Report \- 2024 | IcePanel Blog, accessed April 19, 2025, [https://icepanel.io/blog/2024-11-26-State-of-software-architecture-2024](https://icepanel.io/blog/2024-11-26-State-of-software-architecture-2024)