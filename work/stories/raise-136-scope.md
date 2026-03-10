---
story: RAISE-136
title: Graph schema crash on unknown NodeType — graceful degradation
size: XS
branch: story/standalone/raise-136-graph-nodetype-graceful-degradation
base: v2
status: in-progress
---

## In Scope

- Detect unknown `NodeType` values during graph deserialization
- Skip unrecognized nodes with a warning instead of hard crash
- Ensure `rai graph build` and `rai session start` complete successfully even with schema drift

## Out of Scope

- Migrating or upgrading existing graph data
- Adding new NodeType values
- Any changes to graph build logic beyond deserialization error handling

## Done When

- [ ] `rai graph build` does not crash when saved graph contains unknown NodeType
- [ ] `rai session start` does not crash when saved graph contains unknown NodeType
- [ ] Unknown nodes are skipped with a warning message visible to user
- [ ] Unit tests cover the graceful degradation path (RED → GREEN)
- [ ] All existing tests pass
- [ ] Types and lint pass
