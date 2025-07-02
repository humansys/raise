---
date: '2024-07-27' # Placeholder Date
description: Defines the core data model for the hybrid Retrieval-Augmented Code Generation (RACG) system, supporting both Knowledge Graph and Vector Embedding strategies.
keywords: ["RAG", "RACG", "Data Model", "Knowledge Graph", "Vector Embedding", "PydanticAI", "LlamaIndex", "Clean Architecture", "Code Generation", "MVP"]
lastUpdated: '2024-07-27' # Placeholder Date
title: RACG Core Data Model Design (MVP)
---

# RACG Core Data Model Design (MVP)

<!-- SECTION:overview -->
## Overview

This document outlines the initial Minimum Viable Product (MVP) design for the core data model underpinning the RaiSE Retrieval-Augmented Code Generation (RACG) system. The primary goal is to create a unified representation of knowledge extracted from source code (**Python, C#, TypeScript/JavaScript**) and associated Markdown documentation.

This model serves as the foundation for:

1.  **Knowledge Graph (KG) Construction:** Representing code structure, dependencies, and links to documentation.
2.  **Vector Embedding Generation:** Creating text chunks suitable for semantic search.
3.  **Hybrid Retrieval:** Enabling multi-stage retrieval strategies combining KG traversal and vector search.

The design prioritizes simplicity (KISS, YAGNI) for the PoC phase, focusing on the `jf-backend-product/cart` context, while leveraging PydanticAI for schema definition and anticipating integration with LlamaIndex for indexing and retrieval. It adheres to Clean Architecture principles by modeling domain concepts clearly.

<!-- NOTE: Standard template sections not directly applicable to this architectural design (e.g., Class Structure, Business Rules, Usage Examples, Error Types) are omitted or briefly addressed below. -->

## Core Data Model Entities & Relationships

The model consists of core entities (nodes) and relationships (edges) designed to capture essential structural and conceptual information.

### Entities (Nodes)

We propose the following primary entity types, defined conceptually using PydanticAI `BaseModel` structures:

1.  **`CodeElement`**: Represents syntactical code constructs identified via AST parsing.
    *   **Rationale:** Captures the fundamental building blocks of the source code. Using `elementType` avoids premature complexity (YAGNI).
    *   **Conceptual Schema:**
        ```python
        from typing import List, Optional, Literal
        from pydantic import BaseModel, Field

        class CodeElement(BaseModel):
            id: str = Field(..., description="Unique identifier for the code element (e.g., UUID or hash)")
            elementType: Literal[
                # Cross-Language
                'Module', 'Class', 'Function', 'Method', 'Interface', 'Enum', 'Variable', 'Constant',
                # C# / .NET Specific (or common)
                'Namespace', 'Struct', 'Record', 'Property', 'Field', 'Delegate', 'Event', 'Attribute',
                # TypeScript / React Specific (or common)
                'Component', 'Hook', 'TypeAlias', 'ArrowFunction'
                # Note: Framework conventions (Controller, Service) captured via metadata/annotations
            ] = Field(..., description="Type of code element across different languages")
            name: str = Field(..., description="Name of the element (e.g., class name, function name)")
            filePath: str = Field(..., description="Relative path to the source file from repo root")
            startLine: int = Field(..., description="Starting line number (1-indexed)")
            endLine: int = Field(..., description="Ending line number (1-indexed)")
            codeSnippet: Optional[str] = Field(None, description="Raw code snippet (optional, potentially large)")
            summary: Optional[str] = Field(None, description="AI-generated or extracted summary of the element's purpose")
            docstring: Optional[str] = Field(None, description="Extracted docstring summary")
            parent_id: Optional[str] = Field(None, description="ID of the parent CodeElement (e.g., class containing a method)")
            # --- Essential Multi-Language Metadata ---
            language: Literal['Python', 'CSharp', 'TypeScript', 'JavaScript', 'Markdown'] = Field(..., description="Source language of the code element")
            framework: Optional[Literal['ASP.NET Core', 'React', 'Next.js', 'FastAPI']] = Field(None, description="Detected framework context, if any")
            accessModifier: Optional[Literal['public', 'private', 'protected', 'internal']] = Field(None, description="Visibility/access modifier")
            annotations: Optional[List[str]] = Field(default_factory=list, description="List of annotations/attributes (e.g., C# Attributes, TS Decorators)")
            # Relationships represented implicitly or via explicit edges
        ```

2.  **`DocumentationSection`**: Represents a logical section within a Markdown documentation file.
    *   **Rationale:** Links structured documentation content (derived from `/.raise/templates/standard.md`) into the knowledge model.
    *   **Conceptual Schema:**
        ```python
        from typing import Optional
        from pydantic import BaseModel, Field

        class DocumentationSection(BaseModel):
            id: str = Field(..., description="Unique identifier for the documentation section")
            filePath: str = Field(..., description="Relative path to the source .md file from repo root")
            sectionTitle: str = Field(..., description="Title of the section (e.g., 'Overview', 'Class Structure')")
            textContent: str = Field(..., description="Full text content of the section")
            startLine: int = Field(..., description="Starting line number in the .md file (1-indexed)")
            endLine: int = Field(..., description="Ending line number in the .md file (1-indexed)")
            relatedCodeElement_id: Optional[str] = Field(None, description="Optional ID of the CodeElement this section primarily documents")
            # Relationships represented implicitly or via explicit edges
        ```

3.  **`Chunk`**: Represents a processed unit of text ready for vector embedding.
    *   **Rationale:** Decouples embeddable text from the structural nodes. Aligns with LlamaIndex `TextNode` concepts. Facilitates semantic search.
    *   **Conceptual Schema:**
        ```python
        from typing import Optional, Dict, Any
        from pydantic import BaseModel, Field

        class Chunk(BaseModel):
            id: str = Field(..., description="Unique identifier for the chunk")
            chunkText: str = Field(..., description="The actual text content of the chunk")
            source_id: str = Field(..., description="ID of the source CodeElement or DocumentationSection")
            sourceType: Literal['CodeElement', 'DocumentationSection'] = Field(..., description="Indicates the type of the source node")
            embeddingVector: Optional[List[float]] = Field(None, description="Dense vector embedding (populated during indexing)")
            metadata: Dict[str, Any] = Field(default_factory=dict, description="Key-value metadata for filtering/context (filePath, startLine, elementType, **language**, etc., inherited from source)")
        ```

### Relationships (Edges)

For the MVP, we focus on essential relationships, representing some implicitly via attributes (KISS):

1.  **Containment (`CodeElement` -> `CodeElement`):** Implicitly handled via the `parent_id` attribute on `CodeElement`. (e.g., Method belongs to Class).
2.  **Chunk Generation (`CodeElement`/`DocumentationSection` -> `Chunk`):** Implicitly handled via `source_id` and `sourceType` attributes on `Chunk`.
3.  **`IMPORTS` (`CodeElement` -> `CodeElement`):** Explicit edge representing module/namespace/file-level imports/using directives. Crucial for dependency analysis. Directional.
4.  **`CALLS` (`CodeElement` -> `CodeElement`):** Explicit edge representing function/method calls. Crucial for understanding execution flow. Directional.
5.  **`EXTENDS` (`CodeElement` -> `CodeElement`):** Explicit edge representing class inheritance. Directional. (C#/TS/Python)
6.  **`IMPLEMENTS` (`CodeElement` -> `CodeElement`):** Explicit edge representing interface implementation. Directional. (C#/TS/Python)
7.  **`DOCUMENTS` (`DocumentationSection` -> `CodeElement`):** Optional explicit edge linking a documentation section directly to the code element it describes. Populated based on heuristics or explicit markers. Directional.

*Deferred Relationships (YAGNI for MVP):* `INHERITS_FROM` (covered by EXTENDS), granular `REFERENCES` within comments/docstrings, framework-specific relationships (e.g., `USES_COMPONENT`, `HAS_ATTRIBUTE` - annotations stored in metadata for now).

### Metadata Strategy

Metadata associated primarily with `Chunk` nodes is critical for retrieval and context augmentation. Key metadata includes:

*   `filePath`: Source file of the original content.
*   `startLine`, `endLine`: Location within the source file.
*   `elementType` (if source is `CodeElement`).
*   `sectionTitle` (if source is `DocumentationSection`).
*   `language`: `Python` or `Markdown`.
*   `projectName`: e.g., `jf-backend-product`.
*   `domainConcept`: (Future) Link to higher-level domain concepts.

## Documentation Alignment (`/.raise/templates/standard.md`)

The `DocumentationSection` entity is directly informed by the structure of Markdown files generated using the standard template:

*   **`filePath`**: The path of the `.md` file being processed.
*   **`sectionTitle`**: Extracted from Markdown headings (`## Section Title`) or potentially specific HTML comments like `<!-- SECTION:overview -->`. Key sections to target:
    *   `Overview` (`## Overview`)
    *   `Class Structure` (`## Class Structure`) - The description around the code block.
    *   `Business Rules` (`## Business Rules`)
    *   Potentially others like `Usage Examples`, `Error Types`, `Integration Points`.
*   **`textContent`**: The Markdown content under the corresponding `sectionTitle` heading until the next heading of the same or higher level.
*   **`startLine`/`endLine`**: Line numbers corresponding to the extracted `textContent`.
*   **`relatedCodeElement_id`**: This requires heuristics or explicit markers within the documentation (e.g., a comment `<!-- DOCS_FOR: path/to/module.py::ClassName -->`) to establish the link reliably. This is likely a post-MVP enhancement unless simple heuristics suffice.

## Technology Integration Strategy

*   **PydanticAI:** Used to define the concrete Python classes for `CodeElement`, `DocumentationSection`, and `Chunk`, providing validation and type safety.
*   **LlamaIndex:**
    *   **Indexing:**
        *   An ingestion pipeline will parse source code (**Python, C#, TypeScript/JavaScript**) using language-specific parsers (e.g., AST parsers, Roslyn, Babel/SWC/TS Compiler API) and Markdown docs.
        *   It will create `CodeElement` and `DocumentationSection` instances based on the defined schemas.
        *   Text from these instances (code snippets, docstrings, documentation text) will be chunked to create `Chunk` instances.
        *   `Chunk` instances (mapped to `TextNode`) will be embedded and stored in a Vector Store (e.g., ChromaDB, PGVector). **Crucially, metadata including `language`, `filePath`, `elementType`, `framework`, and `annotations` must be stored with the chunk/vector.**
        *   `CodeElement`, `DocumentationSection` nodes, and explicit relationships (`IMPORTS`, `CALLS`, `EXTENDS`, `IMPLEMENTS`, `DOCUMENTS`) will be stored in a Graph Store (e.g., NebulaGraph, Neo4j via LlamaIndex wrappers).
    *   **Retrieval:**
        *   Hybrid queries will leverage both the Vector Store (semantic similarity on `Chunk` embeddings, **filterable by metadata**) and the Graph Store (traversal via relationships like `IMPORTS`, `CALLS`, `EXTENDS`, `IMPLEMENTS`).
        *   Retrieved `Chunk` metadata (`source_id`) will be used to fetch the original `CodeElement` or `DocumentationSection` context from the graph or a separate document store if needed.

## Integration Points

This data model serves as the central schema for:

*   Data Ingestion Pipeline (AST Parsing, Doc Parsing)
*   LlamaIndex Indexing Service (Vector Store & Graph Store Population)
*   LlamaIndex Retrieval Service (Hybrid Query Engine)
*   Context Augmentation Logic for the LLM

<!-- SECTION:references -->
## References

*   [Hybrid RAG for Code Generation Architecture](/.raise/corpus/raise/docs/architecture/hybrid-rag-for-code-generation.md)
*   PydanticAI Documentation
*   LlamaIndex Documentation 

<!-- SECTION:future_enhancements -->
## Potential Future Enhancements

The current MVP data model provides a solid foundation. Based on techniques identified in the RAG literature review ([Lit Review](/.raise/corpus/raise/docs/research/lit-review-optimizing-RACG.md)), future iterations could evolve the model to support more advanced capabilities:

1.  **Deeper Context & Static Analysis Integration:**
    *   **Model Changes:** Add properties to `CodeElement` for type inference, CFG data, or version hashes. Introduce `ProjectContext` entities. Add relationships like `HAS_TYPE`, `PART_OF_CFG`, `DEPENDS_ON`, `MODIFIED_IN`.
    *   **Benefit:** Allows retrieval based on deeper code understanding (types, control flow, history) and project-wide context.

2.  **Finer-Grained Chunking & Hierarchy:**
    *   **Model Changes:** Enhance `Chunk` metadata with `granularityLevel` and `hierarchicalContext`. Potentially add `ASTNode` entities and `REPRESENTS_AST` relationships.
    *   **Benefit:** Enables more precise retrieval matching code structure (AST) and supports dynamic granularity strategies.

3.  **Expanded Knowledge Graph Relationships:**
    *   **Model Changes:** Add explicit relationships like `INHERITS_FROM`, `IMPLEMENTS`, `READS/WRITES_VARIABLE`, `REFERENCES_CONCEPT`. Introduce `DomainConcept` entities.
    *   **Benefit:** Facilitates more complex graph traversals for finding conceptually related code, understanding inheritance, or tracking data flow.

4.  **Support for Advanced Augmentation:**
    *   **Model Changes:** Add properties to `Chunk` for quality/relevance scores (`qualityScore`, `retrievalScore`, `relevanceScore`), refactoring status (`isRefactored`, `originalChunk_id`), and richer filtering metadata (`codeComplexity`, `isDeprecated`). Consider `RefactoredChunk` entities.
    *   **Benefit:** Enables sophisticated re-ranking, filtering of retrieved results, and techniques like Retrieve-Refactor-Generate (RRG).

5.  **Enhanced Evaluation Support:**
    *   **Model Changes:** Add properties like `keyPoints` or `groundTruthSource` to core entities. Introduce `RetrievalEvent` or `GenerationLog` entities to capture evaluation data.
    *   **Benefit:** Provides the necessary data hooks for calculating advanced RAG metrics (faithfulness, KPR, context relevance).

6.  **Personalization & Adaptability:**
    *   **Model Changes:** Enhance entities with usage frequency or developer feedback. Add `DeveloperProfile` or `ProjectProfile` entities.
    *   **Benefit:** Allows the RAG system to tailor retrieval and generation to specific projects, teams, or individual developers.

These potential enhancements represent directions for increasing the sophistication and effectiveness of the RACG system, building upon the MVP foundation as requirements evolve. Each enhancement introduces trade-offs in terms of complexity and implementation effort. 