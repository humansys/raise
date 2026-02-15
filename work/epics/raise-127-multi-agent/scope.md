## Epic Scope: RAISE-127 pt1 — Multi-Agent Isolation

**JIRA:** [RAISE-127](https://humansys.atlassian.net/browse/RAISE-127)
**Objective:** Devs and F&F can use multiple IDEs/agents without session corruption.

This is pt1 of RAISE-127 — the 3 urgent stories that fix session isolation.
Remaining 5 stories (pt2) deferred until after these land.

**In Scope:**
- Agent identity detection (IDE/runtime fingerprinting)
- Namespaced session state (per-agent isolated directories)
- Project-scoped session writes (CWD poka-yoke, fixes RAISE-134)

**Out of Scope:**
- Agent coordination / shared state → RAISE-127 pt2
- Agent-to-agent communication → RAISE-127 pt2
- IDE-specific plugins → RAISE-128
- Hierarchical memory → RAISE-135

**Stories:**
- RAISE-137: Agent Identity — detect IDE/runtime, assign agent ID (S)
- RAISE-138: Namespaced Session State — per-agent isolated directories (M, depends on RAISE-137)
- RAISE-139: Project-scoped session writes — poka-yoke CWD, fixes RAISE-134 (S, depends on RAISE-138)

**Done when:**
- [ ] All 3 stories complete
- [ ] Multiple agents can run concurrently without session corruption
- [ ] RAISE-134 (context leak) is resolved
- [ ] Epic retrospective done
- [ ] Merged to v2
