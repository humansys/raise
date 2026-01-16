---
document_id: "[PRI]-[PROJECTCODE]-[SEQ]" # ej: PRI-XYZ-001
title: "{SOLUTION_NAME} - Feature Prioritization Matrix"
project_name: "{SOLUTION_NAME}" # Assuming SOLUTION_NAME is project name
client: "[Nombre del Cliente]"
version: "[Número de Versión]"
date: "[YYYY-MM-DD]"
author: "[Nombres o Roles]"
related_docs:
  - "{RELATED_DOC_ID_1}" # ej: PRD-XYZ-001, VIS-XYZ-001
  - "{RELATED_DOC_ID_2}"
status: "[Draft|In Review|Approved|Final]"
---

# {SOLUTION_NAME} - Feature Prioritization Matrix

## Priority Scoring Framework

### Impact Metrics (1-5 scale)
- **Business Value**: Revenue, cost savings, strategic alignment
- **User Value**: User satisfaction, efficiency gains, pain point resolution
- **Technical Foundation**: Platform capability, scalability enablement
- **Risk Reduction**: Security, compliance, technical debt reduction

### Effort Metrics (1-5 scale)
- **Development Complexity**: Technical difficulty, dependencies
- **Integration Points**: System interactions, data flows
- **Testing Requirements**: Test coverage, validation complexity
- **Operational Impact**: Deployment, monitoring, maintenance

## Feature Evaluation Matrix

| Feature ID | Description | Business Value | User Value | Tech Foundation | Risk Reduction | Total Impact | Development Effort | Dependencia Técnica (Ref: Tech Design) | Impacto Estimado (Ref: Estimation) | Priority Score  |
| ---------- | ----------- | -------------- | ---------- | --------------- | -------------- | ------------ | ------------------ | -------------------------------------- | ------------------------------------ | --------------- |
| {FID-001}  | {DESC}      | {1-5}          | {1-5}      | {1-5}           | {1-5}          | {SUM/4}      | {1-5}              | {REF_TEC?}                             | {REF_EST?}                           | {Impact/Effort} |

## MVP Feature Set

### Phase 1 (Must Have)
| Feature ID | Description | Priority Score | Implementation Order | Dependencies |
| ---------- | ----------- | -------------- | -------------------- | ------------ |
| {FID-001}  | {DESC}      | {SCORE}        | {ORDER}              | {DEPS}       |

### Phase 2 (Should Have)
| Feature ID | Description | Priority Score | Rationale for Deferral |
| ---------- | ----------- | -------------- | ---------------------- |
| {FID-002}  | {DESC}      | {SCORE}        | {REASON}               |

## Implementation Sequence

### Sprint 1
- {FEATURE_1}
  - Core capabilities: {CAPABILITIES}
  - Dependencies: {DEPENDENCIES}
  - Definition of Done: {DOD}

### Sprint 2
- {FEATURE_2}
  - Core capabilities: {CAPABILITIES}
  - Dependencies: {DEPENDENCIES}
  - Definition of Done: {DOD}

## Risk Assessment

### Technical Risks
| Risk     | Impact   | Mitigation Strategy |
| -------- | -------- | ------------------- |
| {RISK_1} | {IMPACT} | {STRATEGY}          |

### Business Risks
| Risk     | Impact   | Mitigation Strategy |
| -------- | -------- | ------------------- |
| {RISK_1} | {IMPACT} | {STRATEGY}          |

## Dependencies

### External Dependencies
- {DEPENDENCY_1}
  - Owner: {OWNER}
  - Timeline: {TIMELINE}
  - Status: {STATUS}

### Internal Dependencies
- {DEPENDENCY_1}
  - Team: {TEAM}
  - Timeline: {TIMELINE}
  - Status: {STATUS}

## Success Metrics

### Feature-Level KPIs
| Feature   | Metric   | Target   | Measurement Method |
| --------- | -------- | -------- | ------------------ |
| {FID-001} | {METRIC} | {TARGET} | {METHOD}           |

<!-- Template Usage Instructions:
1. Score features objectively using the defined metrics
2. Focus on measurable impact and effort
3. Consider dependencies in implementation sequence
4. Document clear success criteria per feature
5. Keep risk assessment focused on MVP scope
6. Update regularly based on new information
--> 