# Data Model: SOW Command

This document defines the data flow and mapping for the `/raise.7.sow` command.

## Entities

### Input Artifacts
- **Estimation Roadmap**: Source for `Time` and `Cost`.
  - Field: `Evaluation Summary Table` -> SoW `Section 9`
  - Field: `Implementation Roadmap` -> SoW `Section 5`
- **Project Backlog**: Source for `Deliverables`.
  - Field: `Epics/Stories` -> SoW `Section 4`
- **Tech Design**: Source for `Technical Scope`.
  - Field: `System Architecture` -> SoW `Section 3.2` (reference)
- **Solution Vision**: Source for `Objectives`.
  - Field: `Business Goals` -> SoW `Section 2`
- **Project Requirements (PRD)**: Source for `Context` and `Constraints`.
  - Field: `Vision/Problem` -> SoW `Section 1`
  - Field: `Assumptions` -> SoW `Section 6`
  - Field: `Exclusions` -> SoW `Section 8`

### Output Artifact
- **Statement of Work**: The consolidated document.
  - Template: `.specify/templates/raise/solution/statement_of_work.md`

## Transformations

1. **Cost Aggregation**: Sum totals from Roadmap if not explicit.
2. **Timeline Extraction**: Convert Roadmap phases to SoW milestones table.
3. **Scope Consolidation**: Merge PRD capabilities with Backlog items for Scope description.
