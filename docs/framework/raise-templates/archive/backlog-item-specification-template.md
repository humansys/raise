# Backlog Item Specification

## Item Types

### User Story
```markdown
# {FEATURE_NAME} 
**As a** {USER_ROLE}  
**I need** {CAPABILITY}  
**So that** {BUSINESS_VALUE}  

**BDD Scenarios**
```gherkin
Scenario: {SCENARIO_NAME}
  Given {PRECONDITION}
    And {ADDITIONAL_CONTEXT}
  When {ACTION}
  Then {OBSERVABLE_OUTCOME}
    And {ADDITIONAL_RESULT}

Examples:
| parameter | value  |
| --------- | ------ |
| {VAR}     | {TEST} |
```

**Technical Constraints**
- Must implement {ARCHITECTURE_COMPONENT}
- Must follow {CORE_RULE_REFERENCE}

**LLM Guidance**
- Required patterns: {PATTERN_NAMES}
- Avoid: {ANTI_PATTERNS}
- Security: {SECURITY_REQS}
```

### Technical Enabler
```markdown
# {ENABLER_NAME}
**Purpose**: Enable {CAPABILITY} via {TECHNICAL_IMPLEMENTATION}

**BDD Validation**
```gherkin
Scenario: Technical requirement validation
  Given {SYSTEM_STATE}
   When {OPERATION_PERFORMED}
   Then {METRIC} should be {EXPECTED_VALUE}
```

**Implementation Guide**
1. {STEP_1}
   - Requirements: {TECH_REQS}
   - Reference: {ARCH_DOC_REFERENCE}
2. {STEP_2}
   - Quality Gates: {GATES}
   - Validation: {CRITERIA}

**LLM Constraints**
```typescript
const enablerRules = {
  complexityLimit: "Cyclomatic < 8",
  requiredPatterns: ["FACADE", "OBSERVER"],
  forbiddenPatterns: ["GOD_OBJECT"]
};
```

### Research Spike
```markdown
# {SPIKE_NAME}
**Hypothesis**: {RESEARCH_QUESTION}

**BDD Validation**
```gherkin
Scenario: Validate {KEY_ASSUMPTION}
  Given {CURRENT_KNOWLEDGE_STATE}
   When {EXPERIMENT_EXECUTED}
   Then {MEASURABLE_OUTCOME} should be {EXPECTED_RESULT}
  
Examples:
| Parameter  | Test Case 1 | Test Case 2 |
| ---------- | ----------- | ----------- |
| {VARIABLE} | {VALUE_1}   | {VALUE_2}   |
```

**Success Signals**
- Clear recommendation
- Documented tradeoffs
- Architecture impact analysis

**Timebox**: {HOURS}h

**LLM Collaboration**
- Research scope: {SCOPE}
- Code boundaries: {LIMITS}
- Validation: {REQS}
```

### Defect Resolution
```markdown
# {BUG_ID}
**Current Behavior**: {ACTUAL}  
**Expected Behavior**: {EXPECTED}

**BDD Validation**
```gherkin
Scenario: Reproduce defect
  Given {DEFECT_PREREQUISITES}
   When {TRIGGER_ACTION}
   Then {OBSERVE_INCORRECT_BEHAVIOR}

Scenario: Verify fix
  Given {FIXED_SYSTEM_STATE}
   When {TRIGGER_ACTION}
   Then {OBSERVE_CORRECT_BEHAVIOR}
```

**Root Cause**
- {CAUSE}
- Impact: {IMPACT}
- Components: {AFFECTED}

**Fix Strategy**
1. {FIX_STEP_1}
2. {FIX_STEP_2}

**Validation**
- [ ] Unit test
- [ ] Integration test
- [ ] Perf check

**LLM Safety**
- Required checks: {CHECKS}
- Error handling: {PATTERNS}
- Logging: {REQS}
```

<!-- Template Usage Instructions:
1. Reference parent epic
2. Link to architecture docs
3. Follow core rules
4. Maintain KISS principles
5. Validate against quality gates
--> 