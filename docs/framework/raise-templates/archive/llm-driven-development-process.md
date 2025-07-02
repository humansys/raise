# LLM-Driven Development Process

## Overview

This document outlines our lean-agile development process using LLM-assisted development, structured around our core documentation templates and following KISS, DRY, and YAGNI principles.

## Document Lifecycle

### 1. Solution Vision Phase
**Primary Document**: `solution-vision-template.md`
- **When**: Project initiation
- **Purpose**: Define business context and success criteria
- **Key Activities**:
  1. Problem statement workshop with stakeholders
  2. Solution vision alignment
  3. MVP scope definition
  4. Success criteria establishment
- **Outputs**:
  - Validated solution vision document
  - Initial MVP scope
  - Clear success metrics

### 2. Feature Planning Phase
**Primary Document**: `feature-prioritization-template.md`
- **When**: Sprint planning
- **Purpose**: Prioritize and sequence MVP features
- **Key Activities**:
  1. Feature scoring using impact/effort framework
  2. MVP feature set definition
  3. Risk assessment
  4. Dependencies mapping
- **Outputs**:
  - Prioritized feature backlog
  - Implementation sequence
  - Risk mitigation strategies

### 3. Technical Design Phase
**Primary Documents**: 
- `agent-specification-template.yaml`
- `core-rules-template.yaml`
- **When**: Pre-implementation
- **Purpose**: Define technical boundaries and standards
- **Key Activities**:
  1. Agent capabilities definition
  2. Core rules establishment
  3. Technical constraints documentation
  4. Quality gates definition
- **Outputs**:
  - Technical implementation guidelines
  - Quality standards
  - Development constraints

### 4. Implementation Phase
**Primary Document**: `architecture-document-template.md`
- **When**: During development
- **Purpose**: Guide technical implementation
- **Key Activities**:
  1. Component design
  2. Interface definition
  3. Flow documentation
  4. Security review
- **Outputs**:
  - Detailed technical specifications
  - Implementation patterns
  - Security measures

## Agile Workflow Integration

### Sprint Planning
1. **Vision Alignment** (15 mins)
   - Review solution vision
   - Confirm MVP priorities
   - Update assumptions if needed

2. **Feature Selection** (30 mins)
   - Use prioritization matrix
   - Select sprint features
   - Update implementation sequence

3. **Technical Planning** (30 mins)
   - Review/update core rules
   - Confirm agent capabilities
   - Define sprint architecture goals

### Daily Development
1. **Morning Sync** (15 mins)
   - Review sprint goals
   - Check technical constraints
   - Update documentation as needed

2. **Development Loop**
   - Follow core rules
   - Update architecture docs
   - Track progress against KPIs

3. **End-of-Day Review** (15 mins)
   - Document learnings
   - Update risk assessment
   - Plan next day priorities

### Sprint Review
1. **Success Metrics Review** (30 mins)
   - Compare against vision KPIs
   - Update feature priorities
   - Document learnings

2. **Documentation Update** (30 mins)
   - Refresh architecture docs
   - Update core rules
   - Revise feature priorities

## Document Update Triggers

### Solution Vision
- New business requirements
- Changed market conditions
- Updated success criteria
- Modified constraints

### Feature Prioritization
- New features identified
- Changed priorities
- Updated effort estimates
- New dependencies discovered

### Technical Documents
- New technical constraints
- Updated patterns
- Security requirements
- Performance learnings

## Quality Gates

### Documentation Quality
- All templates completely filled
- Clear, measurable criteria
- Updated dependencies
- Validated assumptions

### Implementation Quality
- Follows core rules
- Meets architecture standards
- Passes security review
- Achieves KPIs

## Continuous Improvement

### Sprint Retrospective
1. **Document Review** (30 mins)
   - Evaluate documentation effectiveness
   - Identify gaps
   - Propose improvements

2. **Process Adjustment** (30 mins)
   - Update templates if needed
   - Refine workflows
   - Enhance quality gates

### Monthly Review
1. **Vision Alignment** (1 hour)
   - Review business goals
   - Update success criteria
   - Adjust MVP scope

2. **Technical Review** (1 hour)
   - Evaluate architecture
   - Update core rules
   - Refine patterns

## Best Practices

### Documentation
1. Keep it lean
   - Focus on essential information
   - Remove outdated content
   - Link related documents

2. Maintain consistency
   - Use standard templates
   - Follow naming conventions
   - Regular updates

3. Ensure accessibility
   - Clear structure
   - Version control
   - Easy navigation

### Process
1. Stay agile
   - Adapt to changes
   - Quick iterations
   - Regular feedback

2. Focus on value
   - Prioritize MVP
   - Measure outcomes
   - Validate assumptions

3. Maintain quality
   - Follow standards
   - Regular reviews
   - Continuous improvement

## Tools Integration

### Version Control
- Store templates in repository
- Track document changes
- Maintain history

### Agile Tools
- Link documents to stories
- Track progress
- Manage dependencies

### LLM Integration
- Use for document generation
- Validate consistency
- Suggest improvements

<!-- Usage Notes:
1. This process is a guideline, not a strict rulebook
2. Adapt based on project needs
3. Focus on delivering value
4. Maintain documentation as code
5. Regular reviews and updates
--> 