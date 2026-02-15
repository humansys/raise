# Research Scope: Bidirectional Sync Patterns

## Primary Question
What are production-proven patterns for bidirectional synchronization between heterogeneous systems with dual-truth ownership?

## Secondary Questions
1. What conflict resolution strategies exist and when should each be used?
2. How do systems handle "dual source of truth" scenarios (local for Rai, external for team)?
3. What are the trade-offs between CRDT, OT, vector clocks, three-way merge, and LWW?
4. What patterns exist for sync across different backend types (JIRA, GitLab, Odoo)?

## Decision Context
Designing sync architecture for RaiSE backlog system:
- **Local**: `governance/backlog.md` + memory graph (source of truth for Rai workflows)
- **External**: JIRA/GitLab/Odoo issues (source of truth for team collaboration)
- **Requirement**: Bidirectional sync keeps both aligned without data loss

## Depth Constraint
Standard research (4-8h) - this is an architectural decision requiring ADR.

## Success Criteria
- Evidence-backed recommendation on conflict resolution strategy
- Pattern catalog for heterogeneous backend sync
- Trade-off matrix for different approaches
- Implementation guidance for RaiSE context
