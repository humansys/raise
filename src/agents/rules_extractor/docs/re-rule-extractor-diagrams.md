# Rule Extractor Design Diagrams

This document contains the visual diagrams representing different aspects of the Rule Extractor design.

## System Architecture Overview

```mermaid
graph TB
    LC["Legacy Code & Artifacts"]
    PP["Preprocessing & Parsing"]
    LLM["LLM-based Rule Extraction"]
    RC["Rule Classification"]
    SF["Structured Formalization"]
    VS["Validation & Confidence Scoring"]
    OUT["Output to JSON/YAML + Metadata Store"]
    KG["Knowledge Graph & Glossary"]
    MAO["Multi-Agent Orchestrator"]

    LC --> PP
    PP --> LLM
    LLM --> RC
    RC --> SF
    SF --> VS
    VS --> OUT
    
    KG <-.-> LLM
    KG <-.-> RC
    KG <-.-> VS
    
    MAO -.-> PP
    MAO -.-> LLM
    MAO -.-> RC
    MAO -.-> SF
    MAO -.-> VS
```

## Multi-Agent Workflow

```mermaid
graph LR
    CA["Code Extractor Agent"]
    RF["Rule Formatter Agent"]
    VA["Validation/Verifier Agent"]
    MM["Memory Manager/Context Agent"]
    OR["Orchestrator"]
    
    OR --> CA
    OR --> RF
    OR --> VA
    
    CA --> RF
    RF --> VA
    
    MM <-.-> CA
    MM <-.-> RF
    MM <-.-> VA
    
    subgraph "Human Review"
        SME["SME Review"]
    end
    
    VA --> SME
    SME -.-> OR
```

## Rule Extraction Pipeline

```mermaid
flowchart TD
    A["Source Code Input"] --> B["Preprocessing"]
    B --> C["Code Chunk Extraction"]
    C --> D["LLM Analysis"]
    D --> E["Rule Identification"]
    E --> F["Schema Validation"]
    F --> G["Confidence Scoring"]
    G --> H["Output Generation"]
    
    I["Knowledge Graph"] -.-> D
    I -.-> E
    I -.-> G
    
    J["Human SME"] -.-> G
    J -.-> H
```

## Validation and Verification Process

```mermaid
flowchart LR
    A["Extracted Rule"] --> B["LLM Self-Verification"]
    A --> C["Heuristic Checks"]
    A --> D["Knowledge Graph Validation"]
    
    B --> E["Confidence Score"]
    C --> E
    D --> E
    
    E --> F{Score >= 0.8}
    F -->|Yes| G["Accept Rule"]
    F -->|No| H["Flag for Review"]
    
    H --> I["SME Review"]
    I --> J["Update Knowledge Base"]
    J --> K["Refine Extraction Process"]
```

## Implementation Phases

```mermaid
graph LR
    P1["Phase 1: MVP
    Core Extraction
    Weeks 1-4"] --> P2
    
    P2["Phase 2: Scale Up
    Full Coverage
    Weeks 5-8"] --> P3
    
    P3["Phase 3: Review
    Human Validation
    Weeks 9-12"] --> P4
    
    P4["Phase 4: Integration
    Production Ready
    Weeks 13-16"] --> P5
    
    P5["Phase 5: Monitoring
    Continuous Improvement
    Ongoing"]
``` 