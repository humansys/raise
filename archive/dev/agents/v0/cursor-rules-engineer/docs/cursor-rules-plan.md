# Cursor Rules Plan for Agentic Rule Extractor Project

## Executive Summary

This document outlines a comprehensive plan for implementing Cursor Rules to support the development of the Agentic Rule Extractor project. By establishing clear AI assistant rules, we aim to ensure consistent, high-quality code generation that aligns with the project's architectural principles, coding standards, and implementation roadmap as described in the technical documentation.

## 1. Analysis of Project Requirements

Based on the agentic rule extractor documentation, this project:

- Implements a pipeline architecture for extracting business rules from legacy code (COBOL/RPG)
- Uses PydanticAI agents with clearly defined interfaces
- Follows KISS, DRY, and YAGNI principles 
- Consists of four core components: Code Processor, LLM-based Rule Extractor, Rule Validator, and Output Generator
- Uses Pydantic models for type safety and data validation
- Has a defined MVP implementation plan with clear sprints and deliverables

## 2. Goals for Cursor Rules Implementation

1. **Maintain Architectural Consistency**: Ensure code generation follows the defined component architecture.
2. **Enforce Data Model Standards**: Guide developers to properly implement and use Pydantic models.
3. **Promote Best Practices**: Implement KISS, DRY, and YAGNI principles in code generation.
4. **Support MVP Timeline**: Align with the sprint plan and prioritize essential functionality.
5. **Enable Error Handling**: Implement the robust error handling patterns defined in the documentation.
6. **Enforce Documentation Standards**: Ensure generated code includes appropriate documentation.

## 3. Proposed Rule Structure

We will organize the Cursor Rules into a hierarchical structure that matches the architecture and implementation needs of the project:

### 3.1 Rule Files Organization

```
.cursor/rules/
├── 000-global.mdc                  # Global rules applicable to all files
├── 100-architecture.mdc            # Overall architectural principles
├── 200-components/                 # Component-specific rules
│   ├── 210-code-processor.mdc      # Code Processor component rules
│   ├── 220-rule-extractor.mdc      # Rule Extractor component rules
│   ├── 230-rule-validator.mdc      # Rule Validator component rules
│   └── 240-output-generator.mdc    # Output Generator component rules
├── 300-models.mdc                  # Pydantic model implementation guidelines
├── 400-error-handling.mdc          # Error handling practices
├── 500-testing.mdc                 # Testing guidelines
└── 600-documentation.mdc           # Documentation standards
```

## 4. Rule Content Planning

### 4.1 Global Rules (000-global.mdc)

**Purpose**: Establish project-wide standards applicable to all files.

**Content**:
- Python version and general coding style (PEP 8)
- Import organization and naming conventions
- Implementation of KISS, DRY, and YAGNI principles
- Docstring requirements (Google or NumPy style)
- Type annotations requirement
- Module structure guidelines

**Example Rule**:
```yaml
name: Global Python Standards
globs: ["**/*.py"]
```
```markdown
# Global Python Standards

## General Coding Style
- Follow PEP 8 for all Python code.
- Use 4 spaces for indentation, no tabs.
- Maximum line length is 100 characters.
- Use snake_case for function and variable names.
- Use CamelCase for class names.

## Import Organization
- Group imports in the following order:
  1. Standard library imports
  2. Third-party library imports
  3. Local application imports
- Sort imports alphabetically within each group.

## Type Annotations
- Use type annotations for all function parameters and return values.
- Use generic types (List, Dict, etc.) from the typing module.

## Docstrings
- Use Google-style docstrings for all modules, classes, and functions.
- Include Args, Returns, and Raises sections as appropriate.
```

### 4.2 Architecture Rules (100-architecture.mdc)

**Purpose**: Define the overall architectural principles to maintain component separation and pipeline flow.

**Content**:
- Component boundaries and responsibilities
- Interface definitions between components
- Pipeline data flow guidelines
- Single Responsibility Principle enforcement

**Example Rule**:
```yaml
name: Architecture Guidelines
globs: ["src/**/*.py"]
```
```markdown
# Architecture Guidelines

## Component Boundaries
- Maintain strict separation between the four main components:
  1. Code Processor
  2. LLM-based Rule Extractor
  3. Rule Validator
  4. Output Generator
- Each component should be in its own module or package.
- Components should communicate only through well-defined interfaces.

## Data Flow
- Follow the pipeline architecture defined in the documentation.
- Use typed data structures for communication between components.
- Avoid circular dependencies between components.

## Single Responsibility Principle
- Each class should have a single responsibility.
- Each function should perform a single logical operation.
- If a function exceeds 30 lines, consider breaking it down into smaller functions.
```

### 4.3 Component-Specific Rules (200-components/*.mdc)

**Purpose**: Provide specific guidelines for each component's implementation.

#### 4.3.1 Code Processor Rules (210-code-processor.mdc)

**Content**:
- File reading and parsing standards
- Code chunking implementation guidelines
- Handling of different source code formats (COBOL, RPG)

**Example Rule**:
```yaml
name: Code Processor Guidelines
globs: ["src/**/code_processor.py", "src/**/code_processor/**/*.py"]
```
```markdown
# Code Processor Guidelines

## Input Handling
- Support both file path and file content inputs.
- Detect file encoding automatically, with fallback to UTF-8.
- Handle EBCDIC to ASCII conversion when necessary.

## Chunking Strategies
- Implement line-based chunking as the primary strategy.
- Respect logical code blocks when possible (don't split mid-procedure).
- Default chunk size should be 300 lines, but make this configurable.

## Output Format
- Each chunk should include:
  - Source file reference
  - Start and end line numbers
  - Original content
- Use the CodeChunk Pydantic model for output.
```

#### 4.3.2 Rule Extractor Rules (220-rule-extractor.mdc)

**Content**:
- PydanticAI agent configuration
- Prompt engineering guidelines
- Rule identification strategies

**Example Rule**:
```yaml
name: Rule Extractor Guidelines
globs: ["src/**/rule_extractor.py", "src/**/rule_extractor/**/*.py", "src/**/agents/extractor.py"]
```
```markdown
# Rule Extractor Guidelines

## Agent Configuration
- Use the PydanticAI Agent pattern from the documentation.
- Configure with appropriate retry logic for resilience.
- Set temperature to 0.1 for deterministic outputs.

## Prompt Engineering
- Structure prompts with clear system, user, and few-shot example components.
- Include specific instructions for extracting business rules.
- Define rule types and criteria for identification.

## Rule Extraction
- Extract rules based on the defined BusinessRule schema.
- Assign unique IDs to each rule.
- Include source code reference for traceability.
```

#### 4.3.3 Rule Validator Rules (230-rule-validator.mdc)

**Content**:
- Validation strategies and confidence scoring
- Error handling for validation failures
- Integration with knowledge sources

**Example Rule**:
```yaml
name: Rule Validator Guidelines
globs: ["src/**/rule_validator.py", "src/**/rule_validator/**/*.py", "src/**/agents/validator.py"]
```
```markdown
# Rule Validator Guidelines

## Validation Approach
- Implement an LLM-based validation strategy.
- Compare extracted rules against source code for accuracy.
- Assign confidence scores on a scale of 0.0 to 1.0.

## Confidence Scoring
- Rules with confidence < 0.7 should be flagged for human review.
- Document the scoring criteria clearly.
- Store validation notes for any problematic rules.

## Error Handling
- Handle validation failures gracefully with fallback strategies.
- Log detailed information about validation issues.
- Allow for manual override of validation results.
```

#### 4.3.4 Output Generator Rules (240-output-generator.mdc)

**Content**:
- Output format standards (JSON, YAML, Markdown)
- Reporting requirements
- File organization

**Example Rule**:
```yaml
name: Output Generator Guidelines
globs: ["src/**/output_generator.py", "src/**/output_generator/**/*.py", "src/**/output/**/*.py"]
```
```markdown
# Output Generator Guidelines

## Output Formats
- Support JSON, YAML, and Markdown output formats.
- Ensure consistent structure across all output formats.
- Use appropriate file extensions (.json, .yaml, .md).

## Report Structure
- Include summary statistics (total rules, confidence distribution).
- Organize rules by type or source file.
- Include metadata about the extraction process.

## File Organization
- Use consistent naming conventions for output files.
- Store outputs in a designated directory.
- Include timestamps or version information in filenames.
```

### 4.4 Models Rules (300-models.mdc)

**Purpose**: Define standards for implementing and using Pydantic models.

**Content**:
- Model definition and inheritance
- Field validation rules
- Schema evolution guidelines

**Example Rule**:
```yaml
name: Pydantic Model Guidelines
globs: ["src/**/models.py", "src/**/*_model.py", "src/**/models/**/*.py"]
```
```markdown
# Pydantic Model Guidelines

## Model Definition
- Define all data models using Pydantic BaseModel.
- Use appropriate field types and annotations.
- Implement model validation methods as needed.

## Core Models
- Follow the BusinessRule model structure defined in the documentation.
- Implement specific rule type models (DecisionRule, ValidationRule, etc.) using inheritance.
- Use SourceReference as a separate model for code references.

## Field Validation
- Use Pydantic Field for detailed field validation.
- Include field descriptions for documentation.
- Set appropriate default values when needed.

## Schema Evolution
- Maintain backward compatibility when modifying models.
- Use Optional fields for new additions.
- Document any breaking changes.
```

### 4.5 Error Handling Rules (400-error-handling.mdc)

**Purpose**: Establish consistent error handling patterns throughout the codebase.

**Content**:
- Error classification and handling strategies
- Logging standards
- Retry mechanism implementation

**Example Rule**:
```yaml
name: Error Handling Guidelines
globs: ["src/**/*.py"]
```
```markdown
# Error Handling Guidelines

## Error Classification
- Classify errors into the following categories:
  - Input Errors: Invalid or malformed input files
  - Processing Errors: Errors during normal processing
  - LLM API Errors: Temporary API failures
  - Critical Errors: Unrecoverable system errors

## Error Handling Strategies
- Use the with_error_handling decorator for functions that may fail.
- Implement appropriate retry mechanisms for transient errors.
- Log detailed error information for debugging.

## Logging
- Use structured logging with appropriate levels.
- Include context information in log messages.
- Configure separate log handlers for different output destinations.
```

### 4.6 Testing Rules (500-testing.mdc)

**Purpose**: Define testing requirements and standards.

**Content**:
- Unit testing requirements
- Integration testing approach
- Test data management

**Example Rule**:
```yaml
name: Testing Guidelines
globs: ["tests/**/*.py"]
```
```markdown
# Testing Guidelines

## Unit Testing
- Write unit tests for all components and major functions.
- Use pytest as the testing framework.
- Aim for >80% code coverage.

## Test Data
- Create representative test data for COBOL and RPG code.
- Store test data in a designated directory.
- Include both simple and complex examples.

## Integration Testing
- Test the complete pipeline with end-to-end tests.
- Verify output formats and content.
- Include edge cases and error scenarios.
```

### 4.7 Documentation Rules (600-documentation.mdc)

**Purpose**: Ensure comprehensive documentation throughout the codebase.

**Content**:
- Code documentation standards
- README and user guide requirements
- API documentation

**Example Rule**:
```yaml
name: Documentation Guidelines
globs: ["**/*.py", "**/*.md"]
```
```markdown
# Documentation Guidelines

## Code Documentation
- Document all modules, classes, and functions with appropriate docstrings.
- Include examples for complex functions.
- Keep documentation up-to-date with code changes.

## Project Documentation
- Maintain a comprehensive README with:
  - Project overview
  - Installation instructions
  - Usage examples
  - Configuration options
- Update documentation when features are added or changed.

## API Documentation
- Generate API documentation using Sphinx.
- Include type information and return values.
- Document exceptions and error cases.
```

## 5. Implementation Plan

### 5.1 Phase 1: Core Rules (Sprint 1)

1. Create the basic directory structure for rules
2. Implement 000-global.mdc with general coding standards
3. Implement 100-architecture.mdc to establish component boundaries
4. Implement 300-models.mdc for Pydantic model standards

### 5.2 Phase 2: Component Rules (Sprint 2)

1. Implement 210-code-processor.mdc
2. Implement 220-rule-extractor.mdc
3. Implement 230-rule-validator.mdc
4. Implement 240-output-generator.mdc

### 5.3 Phase 3: Supporting Rules (Sprint 3)

1. Implement 400-error-handling.mdc
2. Implement 500-testing.mdc
3. Implement 600-documentation.mdc

### 5.4 Phase 4: Refinement and Expansion (Ongoing)

1. Collect feedback from developers on rule effectiveness
2. Refine rules based on implementation experience
3. Add more specific rules as patterns emerge
4. Update rules to accommodate project evolution

## 6. Monitoring and Maintenance

### 6.1 Effectiveness Metrics

- Developer feedback on rule utility
- Consistency of code across the codebase
- Reduction in code review comments related to standards
- Acceleration of development through consistent guidance

### 6.2 Update Process

1. Review rules at the end of each sprint
2. Collect developer feedback on rule clarity and helpfulness
3. Identify areas where additional guidance is needed
4. Update rules using the Cursor Rules Agent workflow

### 6.3 Documentation

- Maintain a changelog for rule updates
- Communicate significant changes to the development team
- Document the rationale for rule decisions

## 7. Conclusion

This plan provides a structured approach to implementing Cursor Rules for the Agentic Rule Extractor project. By aligning rules with the project's architecture, implementation plan, and best practices, we aim to enhance development consistency and quality. The phased implementation approach ensures that rules are introduced in a manageable way, with ongoing refinement based on project needs and developer feedback.

As the project evolves, these rules should be revisited and updated to reflect new insights, challenges, and patterns that emerge during development. 