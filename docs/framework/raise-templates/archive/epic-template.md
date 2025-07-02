# {EPIC_NAME} - Epic Specification

## Strategic Alignment
- **Business Goal**: {GOAL_REFERENCE}
- **Architecture Impact**: {COMPONENT_REFERENCE}
- **Success Metrics**: 
  - {METRIC_1}: {TARGET}
  - {METRIC_2}: {TARGET}

## Technical Context
```typescript
// Core interfaces impacted
interface EpicContext {
  systemDependencies: string[];
  architecturalPatterns: string[];
  qualityAttributes: string[];
}
```

## Backlog Relationship Rules
```mermaid
graph TD
    A[Epic] --> B[Feature]
    A --> C[Enabler]
    B --> D["Spike|Bug Fix"]
    C --> E[Architecture Decision]
    
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#dfd,stroke:#333
    style D fill:#fdd,stroke:#333
    style E fill:#ddd,stroke:#333
```

## BDD Acceptance Criteria
```gherkin
Feature: {EPIC_NAME}
  As a {STAKEHOLDER_ROLE}
  I need {EPIC_CAPABILITY}
  So that {BUSINESS_OUTCOME}

  @epic
  Scenario: Core business value delivery
    Given {INITIAL_STATE}
    When {MAIN_ACTION}
    Then {OUTCOME_MEASUREMENT}

  @quality
  Scenario: Quality attribute validation
    Given {SYSTEM_CONDITION}
    When {LOAD_OR_EVENT}
    Then {PERFORMANCE_TARGET}
```

<!-- Template Usage Instructions:
1. Reference architecture-document-template.md for technical details
2. Link to feature-prioritization-template.md
3. Maintain traceability to solution-vision-template.md
4. Validate against core-rules-template.yaml
5. Update during sprint reviews
--> 