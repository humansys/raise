## Story Scope: S15.3 Constraint Edges

**Epic:** E15 Ontology Graph Refinement
**Size:** S (3 SP)
**Depends on:** S15.2 (complete)

**In Scope:**
- Create `constrained_by` edges linking guardrails to bounded contexts in graph builder
- Parse guardrail categories and map to bounded context nodes
- Handle edge cases (guardrails without clear BC mapping)
- Tests for new constraint edge generation
- Graph rebuild with constraint edges

**Out of Scope:**
- Query engine changes (S15.4)
- Query helper functions (S15.5)
- Skills integration (S15.6)
- Module-level constraint edges (start with BC-level, extend if needed)

**Done Criteria:**
- [ ] `constrained_by` edges created between guardrail nodes and bounded context nodes
- [ ] Graph rebuilt with ~200 constraint edges (per M2 success criteria)
- [ ] `rai memory query` can traverse constraint edges
- [ ] All tests GREEN (pyright strict + ruff + pytest)
- [ ] Retrospective complete
